from rest_framework.views import APIView, Response
from .services import MunicipalityService
from django.db.models import Sum, Count, Max, F, Value, Case, When
from django.db.models import DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear, Coalesce
from transactions.models import Account, Transaction
from comments.models import Comment, Reaction
from publications.models import Publication
from datetime import datetime, timedelta

service = MunicipalityService()

class MunicipalityView( APIView ):
    
    def get(self, request, type = None, value = None):
        # Value is the id of the department, region or specific municipality
        if type is None and value is None:
            # Get all municipalities
            return service.getAllMunicipalities()
        elif value is not None:
            # A filter must be applied
            if type == "department":
                # Get all municipalities of a department
                return service.getMunicipalitiesByDepartmentName(value)
            elif type == "region":
                # Get all municipalities of a region
                return service.getMunicipalitiesByRegion(value)
            elif type == "id":
                # Get a specific municipality
                return service.getMunicipalityById(value)
        else:
            return Response(
                status = 200,
                data = {
                    "status": "error",
                    "error": "Parámetros inválidos"
                }
            )

class DepartmentsView( APIView ):
    
    def get(self, request):
        # Get all departments
        return service.getAllDepartments()
    
class StatisticView( APIView ):
    
    def get(self, request):

        # Get given filtering and grouping params:
        groupFinancialBy = self.request.query_params.get("groupFinancialBy", "day")
        viewFinancialBy = self.request.query_params.get("viewFinancialBy", "money")
        viewReactionsBy = self.request.query_params.get("viewReactionsBy", "lday")

        viewOffersBy = self.request.query_params.get("viewOffersBy", "money")
        viewLastOffersIn = self.request.query_params.get("viewLastOffersIn", "5")
        
        # First check if user is authenticated
        user = request.user
        if user is not None and user.is_authenticated:
            account = Account.objects.get( user=user )
            transactions = Transaction.objects.filter( account=account )

            # Count the number of transactions which mean sales and purchases
            salesAndPurchases = transactions.filter( type__in = ["CS","BP"]  )

            # Get reactions to this user's comments
            comments = Comment.objects.filter( user=user )
            reactions = Reaction.objects.filter( comment__in = comments )

            # Finally, apply filters and return the data

            # Filter for sales and purchases
            if( groupFinancialBy not in ["day", "week", "month", "year"] ):
                groupFinancialBy = "day"
            if( viewFinancialBy not in ["money", "quantity"] ):
                viewFinancialBy = "money"
            
            # Group purchases by given parameter and given statistical measure
            def getTimeFilterInfo():
                if groupFinancialBy == "day":
                    return [{"day": TruncDay("timestamp")}, "day"]
                if groupFinancialBy == "week":
                    return [{"week": TruncWeek("timestamp")}, "week"]
                if groupFinancialBy == "month":
                    return [{"month": TruncMonth("timestamp")}, "month"]
                if groupFinancialBy == "year":
                    return [{"year": TruncYear("timestamp")}, "year"]
                else:
                    return [{"day": TruncDay("timestamp")}, "day"]
            
            # Get groupping info fields
            groupDict, groupField = getTimeFilterInfo()

            salesAndPurchases = salesAndPurchases.annotate(
                **groupDict,
            ).values( groupField ).annotate(
                sales = Sum(
                    Case(
                        When( type="CS", then= "amount" if viewFinancialBy == "money" else 1 ),
                        default=0,
                        output_field=DecimalField()
                    )
                ),
                purchases = Sum(
                    Case(
                        When( type="BP", then= "amount" if viewFinancialBy == "money" else 1 ),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )

            # Filter for reactions
            if( viewReactionsBy not in ["lday", "lweek", "lmonth", "lyear"] ):
                viewReactionsBy = "lday"
            
            # Filter by last day, week, month or year, then group by type and count

            def getTimeDelta( ):
                if viewReactionsBy == "lday":
                    return timedelta(days=1)
                if viewReactionsBy == "lweek":
                    return timedelta(weeks=1)
                if viewReactionsBy == "lmonth":
                    return timedelta(days=30)
                if viewReactionsBy == "lyear":
                    return timedelta(days=365)
                else:
                    return timedelta(days=1)
            
            reactions = reactions.filter(
                createdAt__gte = datetime.now() - getTimeDelta( )
            ).values( "type" ).annotate( total = Coalesce(
                Count("id"), Value(0),
                output_field=DecimalField()
            ))

            # Filter for offers
            if not viewOffersBy in ["money", "quantity"]:
                viewOffersBy = "money"
            if not viewLastOffersIn in ["5", "10", "20"]:
                viewLastOffersIn = "5"
            
            # Filter by last offers within last n publication, then group by publication and count
            sliceLimit = min(user.publications.count(), int(viewLastOffersIn))

            # Get offers made by other users to this user's publications
            publications_ids = list(Publication.objects.filter( user=user ).\
                order_by("-createdAt")[:sliceLimit].values_list("id", flat=True))

            offers = Publication.objects.filter(
                id__in = publications_ids
            ).values(
                "id", "title"
            ).annotate(
                total = Coalesce(
                    Max("offers__amount") if viewOffersBy == "money" else Count("offers__id"),
                    Value(0),
                    output_field=DecimalField()
                )
            ).annotate(
                publicationTitle = F("title")
            ).values(
                "id", "publicationTitle", "total"
            )

            return Response(
                status = 200,
                data = {
                    "status": "success",
                    "data": {
                        "balance" : account.balance,
                        "frozenBalance" : account.frozen,
                        "salesPurchases": salesAndPurchases,
                        "reactions": reactions,
                        "offers": offers
                    }
                }
            )

        return Response(
            status = 200,
            data = {
                "status": "error",
                "error": "Usuario no autenticado"
            }
        )
    
class CurrencyTranslationView( APIView ):

    def get(self, _, copValue):
        if copValue is None:
            return Response(
                status = 200,
                data = {
                    "status": "error",
                    "error": "Moneda no especificada"
                }
            )
        else:
            return Response(
                status = 200,
                data = {
                    "status": "success",
                    "data": {
                        "copValue": copValue,
                        "usdValue":  0 #self.currencyService.convert(copValue)
                    }
                }
            )
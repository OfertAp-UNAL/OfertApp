from rest_framework.views import APIView, Response
from .services import MunicipalityService
from django.core import serializers
from transactions.models import Account, Transaction
from comments.models import Comment, Reaction
from publications.models import Publication, Offer
from .serializers import OfferStatsSerializer, ReactionStatsSerializer, TransactionStatsSerializer

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

class DepartmentsView( APIView ):
    
    def get(self, request):
        # Get all departments
        return service.getAllDepartments()
        
class StatisticView( APIView ):
    
    def get(self, request):
        # Get user's statistics
        
        # First check if user is authenticated
        user = request.user
        if user is not None and user.is_authenticated:
            account = Account.objects.get( user=user )
            transactions = Transaction.objects.filter( account=account )

            # Count the number of transactions which mean sales and purchases
            sales = transactions.filter( type__in = ["CS"]  )
            purchases = transactions.filter( type__in = ["BP"] )

            # Get reactions to this user's comments
            comments = Comment.objects.filter( user=user )
            reactions = Reaction.objects.filter( comment__in = comments )

            # Get offers made by other users to this user's publications
            publications = Publication.objects.filter( user=user )
            offers = Offer.objects.filter( publication__in = publications )

            return Response(
                status = 200,
                data = {
                    "status": "success",
                    "data": {
                        "balance" : account.balance,
                        "frozenBalance" : account.frozen,
                        "sales": TransactionStatsSerializer(sales, many=True).data,
                        "purchases": TransactionStatsSerializer(purchases, many=True).data,
                        "reactions": ReactionStatsSerializer(reactions, many=True).data,
                        "offers": OfferStatsSerializer(offers, many=True).data
                    }
                }
            )

        return Response(
            status = 200,
            data = {
                "status": "error",
                "error": "User not authenticated"
            }
        )
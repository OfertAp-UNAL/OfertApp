from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from publications.serializers import PublicationSerializer, CategorySerializer, OfferSerializer, \
    OfferCreateSerializer, PublicationSupportSerializer, PublicationCreateSerializer

from publications.models import Publication, Category, Offer
from .services import checkOfferService, checkPublicationService

class PublicationView( APIView ):
    def post( self, request ):

        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You must be logged in to perform this action"
            })

        # Get data from request
        endDate = request.data.get("endDate", None)
        priority = request.data.get("priority", None)

        # Get supports for publication
        supportsData = request.FILES.getlist("supportsFiles")

        # Get supports descriptions for supports
        supportsDescriptions = request.data.getlist("supportsDescriptions")

        # Get types array for supports
        supportsTypes = request.data.getlist("supportsTypes")

        # Check additional publication business logic
        errorResponse = checkPublicationService(
            user, priority, endDate,
            supportsData, supportsDescriptions, supportsTypes
            )
        if errorResponse is not None:
            return errorResponse

        # Get data from request
        data = {
            "title" : request.data.get("title"),
            "description" : request.data.get("description"),
            "minOffer" : request.data.get("minOffer"),
            "category" : request.data.get("category"),
            "user" : user.id,
        }

        if priority is not None:
            data["priority"] = priority
        
        if endDate is not None:
            data["endDate"] = endDate

        serializer = PublicationCreateSerializer(data=data)

        if serializer.is_valid():
            
            # Save publication first
            publication = serializer.save()

            # For each support, create a support object
            for i in range(len(supportsData)):
                supportDescription = supportsDescriptions[i]
                supportFile = supportsData[i]
                supportType = supportsTypes[i]

                supportSerializer = PublicationSupportSerializer(data={
                    "publication" : publication.id,
                    "description" : supportDescription,
                    "type" : supportType,
                    "data" : supportFile
                })

                if supportSerializer.is_valid():
                    supportSerializer.save()
                else:
                    return Response(status = 200, data = {
                        "status" : "error",
                        "errors" : supportSerializer.errors
                    })
                
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 400, data = {
            "status" : "error", 
            "errors" : serializer.errors
        })
    
    def get(self, _, publicationId = None):
        if publicationId is not None:
            try:
                publication = Publication.objects.get(pk=publicationId)
                return Response(status = 200, data = {
                    "status" : "success",
                    "data" : PublicationSerializer(publication).data
                })
            except Publication.DoesNotExist:
                return Response(status = 400, data = {
                    "status" : "error",
                    "error" : "Invalid publication id"
                })

        # Get parameters of filtering
        title = self.request.query_params.get("title", None)
        user = self.request.query_params.get("user", None)
        availableOnly = self.request.query_params.get("available", False)
        minPrice = self.request.query_params.get("minPrice", None)
        maxPrice = self.request.query_params.get("maxPrice", None)
        orderby = self.request.query_params.get("orderBy", "id")
        limit = self.request.query_params.get("limit", 100)

        # Check orderby validity
        if orderby not in ["relevance", "price", "offers", "comments"]:
            orderby = "id" # Make id a default

        # Get publications
        publications = Publication.objects.all()

        # Filter by title if provided
        if title is not None:
            publications = publications.filter(title__icontains=title)
        
        # Filter by user if provided
        if user is not None:
            publications = publications.filter(user__id=user)

        # Filter by availability if provided
        if availableOnly:
            publications = publications.filter(available=True)
        
        # Filter by price if provided
        if minPrice is not None:
            try:
                minPrice = float(minPrice)
                publications = publications.filter(minOffer__gte=minPrice)
            except ValueError:
                pass

        if maxPrice is not None:
            try:
                maxPrice = float(maxPrice)
                publications = publications.filter(minOffer__lte=maxPrice)
            except ValueError:
                pass

        # Order by provided filters
        if orderby == "relevance":
            publications = sorted(
                publications,
                key = lambda publication: publication.getPriorityScore(),
                reverse = True
            )
        elif orderby == "price":
            publications = publications.order_by("minOffer")
        elif orderby == "offers":
            publications = publications.annotate(
                offersCount = Count("offers")
            ).order_by("-offersCount")
        elif orderby == "comments":
            publications = publications.annotate(
                commentsCount = Count("comments")
            ).order_by("-commentsCount")
        elif orderby == "date":
            publications = publications.order_by("-createdAt")

        # Limit the number of publications
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                limit = 100

        publications = publications[:limit]

        # Return the publications
        return Response(status = 200, data = {
            "status" : "success",
            "data" : PublicationSerializer(publications, many=True).data
        })

class CategoryView( APIView ):
    def post( self, request ):
        data = {
            "name" : request.data.get("name"),                      
        }       

        serializer = CategorySerializer(data=data)

        if serializer.is_valid():
            
            serializer.save()          

                
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 400, data = {
            "status": "error",
            "errors" : serializer.errors
        })
    
    def get(self, request):
        categories = Category.objects.all()

        return Response(status = 200, data = {
            "status" : "success",
            "data" : CategorySerializer(categories, many=True).data
        })
    
class OfferView( APIView ):
    def post( self, request, publicationId = None ):
        
        user = request.user

        # Check if user is authenticated
        if user is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You must be logged in to make an offer"
            })
        
        # All offers must belong to a publication
        if publicationId is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid publication id"
            })
        
        amount = request.data.get("amount")

        # Check if amount have consistency
        try:
            amount = float(amount)
        except ValueError:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid amount"
            })

        # Check if publication exists
        try:
            publication = Publication.objects.get(id=publicationId)
        except Publication.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid publication id"
            })

        # Check offer
        errorResponse = checkOfferService(user, amount, publication)
        if errorResponse is not None:
            return errorResponse
        
        # Get last offer made by user
        data = {
            "amount" : request.data.get("amount"),
            "publication" : publicationId,
            "user" : user.id
        }

        serializer = OfferCreateSerializer(
            data = data,
        )

        if serializer.is_valid():
            serializer.save()       
            return Response(
                status = 200,
                data = {
                    "status" : "success",
                    "data" : serializer.data
                }
            )
        
        return Response(
            status = 200,
            data = {
                "status" : "error",
                "error" : serializer.errors
            }
        )
    
    def get(self, request, publicationId = None):
        if publicationId is not None:
            try:
                offers = Offer.objects.filter(
                    publication = publicationId
                )
                return Response(
                    status=200,
                    data = {
                        "status" : "success",
                        "data" : OfferSerializer(offers, many=True ).data
                    })
            
            except Exception:
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "Invalid publication Id"
                    })
        
        offers = Offer.objects.all()

        return Response({
            "status" : "success",
            "data" : OfferSerializer(offers, many=True).data
        })
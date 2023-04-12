from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from publications.serializers import PublicationSerializer, CategorySerializer, OfferSerializer
from publications.models import Publication, Category, Offer

class PublicationView( APIView ):
    def post( self, request ):
        data = {
            "title" : request.data.get("title"),
            "description" : request.data.get("description"),
            "minOffer" : request.data.get("minOffer"),
            "endDate" : request.data.get("endDate"),
            "available" : request.data.get("available"),
            "reportable" : request.data.get("reportable"),
            "category" : request.data.get("category"),
            "user" : request.data.get("user"), 
            "piority": request.data.get("priority"),        
        }       

        data["supports"] = request.FILES["supports"]

        serializer = PublicationSerializer(data=data)

        if serializer.is_valid():
            
            serializer.save()
                
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
        print(title, user, availableOnly, minPrice, maxPrice, orderby, limit)

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
        if availableOnly is not None:
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
    def post( self, request ):
        data = {
            "ammount" : request.data.get("ammount"),
            "available" : request.data.get("available"),
            "id" : request.data.get("id"),
            "user" : request.data.get("user"),
            "publication" : request.data.get("publication"),
        }       

        serializer = OfferSerializer(data=data)

        if serializer.is_valid():
            serializer.save()          
            return Response(serializer.data)
        
        return Response(serializer.errors)
    
    def get(self, request):
        offers = Offer.objects.all()

        return Response({
            "status" : "success",
            "data" : OfferSerializer(offers, many=True).data
        })
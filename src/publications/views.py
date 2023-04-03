from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
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

        publications = Publication.objects.all()
        publications = sorted(
            publications,
            key = lambda publication: publication.getPriorityScore(),
            reverse = True
        )

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
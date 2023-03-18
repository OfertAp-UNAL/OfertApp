from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from publications.serializers import PublicationSerializer

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
        }       

        serializer = PublicationSerializer(data=data)

        if serializer.is_valid():
            
            publication = serializer.save()          

                
            return Response(serializer.data)
        
        return Response(serializer.errors)

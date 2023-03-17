from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from auth.serializers import UserSerializer
from auth.token.serializers import CustomTokenPairSerializer

class LoginView( APIView ):
    def post(self, request):
        data = {
            "email" : request.data.get("email"),
            "username" : request.data.get("username"),
            "password" : request.data.get("password")
        }

        user = authenticate(
            request,
            username=data["username"],
            email=data["email"],
            password=data["password"]
        )

        if user is not None:
            refresh = CustomTokenPairSerializer.get_token(user)

            return Response({
                "token" : str(refresh.access_token),
            })

        return Response({
            "error" : "Invalid credentials"
        })

class RegisterView( APIView ):
    def post( self, request ):
        data = {
            "id" : request.data.get("id"),
            "email" : request.data.get("email"),
            "username" : request.data.get("username"),
            "password" : request.data.get("password"),
            "birthdate" : request.data.get("birthdate"),
            "phone" : request.data.get("phone"),
            "address" : request.data.get("address"),
            "townId" : request.data.get("townId"),
            "profilePicture" : request.data.get("profilePicture"),
            "accountType" : request.data.get("paymentAccountType"),
            "accountId" : request.data.get("paymentAccountNumber"),
            "vipState" : False,
            "vipPubCount" : 0,
            "blocked" : False
        }

        # Hash password
        data["password"] = make_password(data["password"])

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            
            user = serializer.save()
            if user:
                refresh = CustomTokenPairSerializer.get_token(user)

                return Response({
                    "token" : str(refresh.access_token),
                })
            return Response(serializer.data)
        
        return Response(serializer.errors)

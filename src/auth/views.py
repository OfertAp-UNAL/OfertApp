from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from auth.serializers import UserSerializer
from auth.token.serializers import CustomTokenPairSerializer
from .token.verifyEmailToken import emailTokenGenerator
from .models import User

from auth.services import AccountCheckService, PermissionsCheckService
accountService = AccountCheckService()
permissionsService = PermissionsCheckService()

class LoginView( APIView ):
    def post(self, request):
        data = {
            "email" : request.data.get("email"),
            "username" : request.data.get("username"),
            "password" : request.data.get("password")
        }

        try:
            user = authenticate(
                request,
                username=data["username"],
                email=data["email"],
                password=data["password"]
            )
        except Exception as e:
            print(e)
            return Response({
                "status" : "error",
                "error" : "Invalid credentials"
            })
        

        if user is not None:

            # Check if the user is blocked
            if user.blocked:
                return Response({
                    "status" : "error",
                    "error" : "Your account has been blocked"
                })
            
            # Persistent user
            login(request, user)
            
            if user.verified:

                refresh = CustomTokenPairSerializer.get_token(user)

                return Response({
                    "status" : "success",
                    "token" : str(refresh.access_token),
                })

            else:
                # Force the user to verify his Email
                accountService.sendVerificationEmail(user)

                return Response({
                    "status" : "error",
                    "error" : "Please verify your account by checking your email"
                })

        return Response({
            "status" : "error",
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
            "accountType" : request.data.get("paymentAccountType"),
            "accountId" : request.data.get("paymentAccountNumber"),
            "firstName" : request.data.get("firstName"),
            "lastName" : request.data.get("lastName"),
            "idenIdType" : request.data.get("idenIdType"),
        }


        # Get profile picture from files array
        data["profilePicture"] = request.FILES["profilePicture"]

        # Hash password
        data["password"] = make_password(data["password"])

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            
            # Verify user's identity
            if not accountService.checkAccount(data):
                return Response({
                    "status" : "error",
                    "error" : "Invalid identity"
                })
            
            user = serializer.save()
            if user:
                # Force the user to verify his Email
                accountService.sendVerificationEmail(user)

                # Give this user a token, but next time he will have to verify his account
                refresh = CustomTokenPairSerializer.get_token(user)

                return Response({
                    "status" : "success",
                    "token" : str(refresh.access_token),
                })
            
            return Response({
                "status" : "error",
                "error" : "Invalid form body"
            })
        
        return Response({
            "status" : "error",
            "errors" : serializer.errors
        })

class UserInfoView( APIView ):
    def get(self, request):
        user = request.user
        if user is not None and user.is_authenticated:
            return Response({
                "status" : "success",
                "data" : UserSerializer(user).data
            })
        
        return Response({
            "status" : "error",
            "error" : "You aren't logged in"
        })
    
    def patch(self, request):
        user = request.user
        
        if user is not None and user.is_authenticated:

            # Get profile picture from files array
            if "profilePicture" in request.FILES:
                request.data["profilePicture"] = request.FILES["profilePicture"]
            
            data = {
                "id" : request.data.get("id"),
                "email" : request.data.get("email"),
                "username" : request.data.get("username"),
                "birthdate" : request.data.get("birthdate"),
                "phone" : request.data.get("phone"),
                "address" : request.data.get("address"),
                "townId" : request.data.get("townId"),
                "accountType" : request.data.get("paymentAccountType"),
                "accountId" : request.data.get("paymentAccountNumber"),
                "firstName" : request.data.get("firstName"),
                "lastName" : request.data.get("lastName"),
                "idenIdType" : request.data.get("idenIdType"),
            }

            if "profilePicture" in request.FILES:
                data["profilePicture"] = request.FILES["profilePicture"]

            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
            )

            if serializer.is_valid():

                serializer.save()
                if user:

                    return Response({
                        "status" : "success",
                        "data" : UserSerializer(user).data
                    })
                
                return Response({
                    "status" : "error",
                    "error" : "Invalid form body"
                })
            
            return Response({
                "status" : "error",
                "errors" : serializer.errors
            })
        
        return Response({
            "status" : "error",
            "error" : "You aren't logged in"
        })

class VerifyView( APIView ):
    def get(self, request, token = None, user64_id = None ):
        if token is None or user64_id is None:
            return Response({
                "status" : "error",
                "error" : "Invalid request, include /token/user64_id/"
            })

        try:
            user_id = urlsafe_base64_decode(user64_id).decode()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "status" : "error",
                "error" : "Invalid token"
            })

        if emailTokenGenerator.check_token(user, token):

            # Verify user by Email
            user.verified = True
            user.save()

            return Response({
                "status" : "success",
                "message" : "Email verified"
            })
        
        return Response({
            "status" : "error",
            "error" : "Invalid token"
        })
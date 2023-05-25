from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from auth.serializers import UserSerializer
from auth.token.serializers import CustomTokenPairSerializer
from util.services import saveFile
from .token.customTokens import emailTokenGenerator, resetPasswordTokenGenerator
from .models import User
from datetime import datetime, timedelta
import dateutil.parser as parser

from auth.services import AccountCheckService, checkUserPermissions
accountService = AccountCheckService()

class LoginView( APIView ):
    def post(self, request):

        # Allows verification with any of both username or email
        data = {
            "user" : request.data.get("user"),
            "password" : request.data.get("password")
        }

        try:
            user = authenticate(
                request,
                email=data["user"],
                user=data["user"],
                password=data["password"]
            )
        except Exception as e:
            print(e)
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid credentials"
            })
        

        if user is not None:

            # Check if the user is blocked
            if user.blocked:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Your account has been blocked"
                })
            
            # Persistent user
            login(request, user)
            
            if user.verified:

                refresh = CustomTokenPairSerializer.get_token(user)

                return Response(status = 200, data = {
                    "status" : "success",
                    "token" : str(refresh.access_token),
                })

            else:
                # Force the user to verify his Email
                #accountService.sendVerificationEmail(user)

                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Please verify your account by checking your email"
                })

        return Response({
            "status" : "error",
            "error" : "Invalid credentials"
        })

class LogoutView( APIView ):
    def get( self, request ):
        if request.user.is_authenticated:
            logout(request)

            return Response(status = 200, data = {
                "status" : "success"
            })
        
        return Response(status = 401, data = {
            "status" : "error",
            "error" : "You are not logged in"
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
        if "profilePicture" in request.FILES:
            data["profilePicture"] = saveFile(
                request.FILES["profilePicture"], "profile_pictures"
            )

        # Hash password
        data["password"] = make_password(data["password"])
        data["verified"] = True

        serializer = UserSerializer(data=data)

        # Check if user is not underage
        if data["birthdate"] is not None:
            if parser.parse( data["birthdate"] ) > datetime.today() - timedelta(days=18*365):
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "You must be at least 18 years old"
                })
            
        if serializer.is_valid():
            
            # Verify user's identity
            if not accountService.checkAccount(data):
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid identity"
                })
            
            user = serializer.save()
            if user:
                # Force the user to verify his Email
                accountService.sendVerificationEmail(user)
                
                # Give this user a token, but next time he will have to verify his account
                refresh = CustomTokenPairSerializer.get_token(user)

                return Response(status = 200, data = {
                    "status" : "success",
                    "token" : str(refresh.access_token),
                })
            
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid form body"
            })
        return Response(status = 200, data = {
            "status" : "error",
            "error" : serializer.errors
        })

class UserInfoView( APIView ):
    def get(self, request):
        user = request.user
        if user is not None and user.is_authenticated:
            permissions = checkUserPermissions(user)
            responseDict = UserSerializer(user).data

            # Permissions are added to the user's data
            responseDict.update(permissions)

            return Response(status = 200, data = {
                "status" : "success",

                # Permissions are added to the user's data
                "data" : responseDict
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "You aren't logged in"
        })
    
    def patch(self, request):
        user = request.user
        
        if user is not None and user.is_authenticated:
            
            data = {
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

            # Get profile picture from files array
            if "profilePicture" in request.FILES:
                data["profilePicture"] = saveFile(
                    request.FILES["profilePicture"], "profile_pictures"
                )

            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
            )

            if serializer.is_valid():

                serializer.save()
                if user:

                    return Response(status = 200, data = {
                        "status" : "success",
                        "data" : UserSerializer(user).data
                    })
                
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid form body"
                })
            
            return Response(status = 200, data = {
                "status" : "error",
                "error" : serializer.errors
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "You aren't logged in"
        })

class VerifyView( APIView ):
    def get(self, _, token = None, user64_id = None ):
        if token is None or user64_id is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid request, include /token/user64_id/"
            })

        try:
            user_id = urlsafe_base64_decode(user64_id).decode()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid token"
            })

        if emailTokenGenerator.check_token(user, token):

            # Verify user by Email
            user.verified = True
            user.save()

            return Response(status = 200, data = {
                "status" : "success",
                "message" : "Email verified"
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid token"
        })

class PasswordResetView( APIView ):
    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        user64_id = request.data.get("user64_id")
        password = request.data.get("password")

        if email is not None:
            # Its a request to send a password reset email
            email = request.data.get("email")
            if email is None:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid request, include /email/"
                })

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Email doesn't exist"
                })

            # Check if user is verified
            if not user.verified:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Email isn't verified"
                })

            # Send password reset email
            accountService.sendPasswordResetEmail(user)

            return Response(status = 200, data = {
                "status" : "success",
                "message" : "Email sent"
            })

        elif token is not None and user64_id is not None and password is not None:
            # Its a request for reseting user's password
            try:
                user_id = urlsafe_base64_decode(user64_id).decode()
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid token"
                })
            
            if resetPasswordTokenGenerator.check_token(user, token):
                user.set_password(password)
                user.save()

                return Response(status = 200, data = {
                    "status" : "success",
                    "message" : "Password changed"
                })

            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Invalid token"
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid request, include /email/ or /token/user64_id/password/"
        })
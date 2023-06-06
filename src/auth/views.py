from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework.response import Response
from auth.serializers import UserSerializer
from auth.token.serializers import CustomTokenPairSerializer
from util.services import saveFile, checkFileExtension
from .token.customTokens import emailTokenGenerator, resetPasswordTokenGenerator
from .models import User
from util.services import notify
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
                "error" : "Credenciales inválidas"
            })
        

        if user is not None:

            # Check if the user is blocked
            if user.blocked:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Estás bloqueado, no puedes iniciar sesión"
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
                    "error" : "Por favor verifica tu correo electrónico"
                })

        return Response({
            "status" : "error",
            "error" : "Credenciales inválidas"
        })

class LogoutView( APIView ):
    def get( self, request ):
        if request.user.is_authenticated:
            logout(request)

            return Response(status = 200, data = {
                "status" : "success"
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "No estás logueado"
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
            profileFile = request.FILES["profilePicture"]

            # Check file metadata
            message, fileType = checkFileExtension( profileFile )

            if message is not None:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : message
                })
            
            if fileType != "IMAGE":
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "El archivo debe ser una imagen"
                })
            
            data["profilePicture"] = "https://cdn.filestackcontent.com/pLDF5BZTP6ASwiobbC8W"
            data["profilePicture"] = saveFile(
                profileFile, "profile_pictures"
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
                    "error" : "Debes ser mayor de edad para registrarte"
                })
            
        if serializer.is_valid():
            
            # Verify user's identity
            if not accountService.checkAccount(data):
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "La información de tu cuenta no coincide con la información de tu identificación"
                })
            
            user = serializer.save()
            if user:
                # Force the user to verify his Email
                accountService.sendVerificationEmail(user)
                
                # Give this user a token, but next time he will have to verify his account
                refresh = CustomTokenPairSerializer.get_token(user)

                # All OK, lets send a kindly message to the user
                notify(
                    user,
                    "Bienvenido a OfertApp!",
                    "Esperamos serte de ayuda en tu busqueda de las mejores ofertas!"
                )

                return Response(status = 200, data = {
                    "status" : "success",
                    "token" : str(refresh.access_token),
                })
            
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Cuerpo de formulario inválido"
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
            "error" : "No estás logueado"
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

            # Iterate over dictionary keys and delete nulls, since this is a PATCH request
            for key in list(data.keys()):
                if data[key] is None:
                    del data[key]

            # Get profile picture from files array
            if "profilePicture" in request.FILES:
                data["profilePicture"] = saveFile(
                    request.FILES["profilePicture"], "profile_pictures"
                )

            serializer = UserSerializer(
                user,
                data=data,
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
                    "error" : "Cuerpo de formulario inválido"
                })
            
            return Response(status = 200, data = {
                "status" : "error",
                "error" : serializer.errors
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "No estás logueado"
        })

class VerifyView( APIView ):
    def get(self, _, token = None, user64_id = None ):
        if token is None or user64_id is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Petición inválida, incluye /token/user64_id/"
            })

        try:
            user_id = urlsafe_base64_decode(user64_id).decode()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Token inválido"
            })

        if emailTokenGenerator.check_token(user, token):

            # Verify user by Email
            user.verified = True
            user.save()

            return Response(status = 200, data = {
                "status" : "success",
                "message" : "Email verificado"
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Token inválido"
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
                    "error" : "Petición inválida, incluye /email/"
                })

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Email no registrado"
                })

            # Check if user is verified
            if not user.verified:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Por favor verifica tu correo electrónico antes de cambiar tu contraseña"
                })

            # Send password reset email
            accountService.sendPasswordResetEmail(user)

            return Response(status = 200, data = {
                "status" : "success",
                "message" : "Email enviado"
            })

        elif token is not None and user64_id is not None and password is not None:
            # Its a request for reseting user's password
            try:
                user_id = urlsafe_base64_decode(user64_id).decode()
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Token inválido"
                })
            
            if resetPasswordTokenGenerator.check_token(user, token):
                user.set_password(password)
                user.save()

                return Response(status = 200, data = {
                    "status" : "success",
                    "message" : "Contraseña cambiada"
                })

            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Token inválido"
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Petición inválida, incluye /email/ o /token/user64_id/password/"
        })
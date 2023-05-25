import requests
import environ
import base64
from django.conf import settings
from .token.customTokens import emailTokenGenerator, resetPasswordTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from .models import User
from dict_hash import sha256
from datetime import datetime
from util.services import notify

# Mastercard imports
import oauth1.authenticationutils as authutils
from oauth1.signer import OAuthSigner

# Read env variables
env = environ.Env()
environ.Env.read_env()

class AccountCheckService():
    def __init__(self ):
        self.nequi_token = None
        self.paypal_token = None
        self.mastercard_keys = None
    
    def checkAccount(self, userData): 
        return True
        # DEPRECATED: Checks will be made temporarily on each transaction
    
        if userData["accountType"] == 'PP':
            return self.checkPaypalAccount(userData)
        elif userData["accountType"] == 'NQ':
            return self.checkNequiAccount(userData)
        elif userData["accountType"] == 'CD':
            return self.checkMastercardAccount(userData)
        else:
            return False
    
    def checkPaypalAccount(self, _):
        api = env.get_value('PAYPAL_API') + '/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {
            'grant_type': 'client_credentials',
        }

        # TODO: Seek for a way of looking into paypal's users verification info
        data = requests.post(api, headers=headers, data=data).json()

        return True

    def genNequiToken(self):
        api = env.get_value('NQ_AUTH_BASE_URL') + '/oauth2/token?grant_type=client_credentials'

        clientId = env('NQ_CLIENT_ID')
        clientSecret = env('NQ_CLIENT_SECRET')

        authorization = base64.b64encode(
            f"{clientId}:{clientSecret}".encode("utf-8")
        ).decode('ascii')
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization' : f"Basic {authorization}"
        }
        
        try:
            authResp = requests.post(
                api, 
                headers=headers
            ).json()
            self.nequi_token = authResp['access_token']
        except Exception as e:
            print(e)
            self.nequi_token = None

    def checkNequiAccount(self, userData):
        
        self.genNequiToken()

        if self.nequi_token is None:
            return False

        # Visit 
        # https://github.com/nequibc/nequi-api-client-nodejs/blob/master/src/deposit_withdrawal/ValidateClient.js
        check_url = env.get_value('NQ_BASE_URL') + '/agents/v2/-services-clientservice-validateclient'

        search_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization' : f"Bearer {self.nequi_token}",
            'x-api-key' : env.get_value('NQ_API_KEY'),
        }
        data = {
            "RequestMessage": {
                "RequestHeader": {
                    "Channel": 'MF-001',
                    "RequestDate": '2020-01-17T20:26:12.654Z',
                    "MessageID": '1234567890',
                    "ClientID": "12345",
                    "Destination": {
                        "ServiceName": 'RechargeService',
                        "ServiceOperation": 'validateClient',
                        "ServiceRegion": 'C001',
                        "ServiceVersion": '1.4.0'
                    }
                },
                "RequestBody": {
                    "any": {
                        "validateClientRQ": {
                            "phoneNumber": userData["accountId"],
                            "value": "10"
                        }
                    }
                }
            }
        }

        try:
            user_data = requests.post(
                check_url,
                headers=search_headers,
                data=data
            ).json()
            print( user_data )
            response_client = user_data['ResponseMessage']['ResponseBody']['any']['validateClientRS']

            # TODO: Use a better algorithm to check names similarity (maybe ADN method)
            if response_client['customerName'] == userData["firstName"] + " " + userData["lastName"]:
                return True
            return False
        except Exception as e:
            print(e)

            return True # Test purposes
        return True

    def checkByMastercard(self, userData):

        # Load key info
        signinig_key = authutils.load_signing_key(
            "./../" + env.get_value('MC_PRIVATE_KEY_PATH'),
            env.get_value('MC_CARD_KEY_PASSWORD')
        )

        # Gen mastercard service path
        service_uri = "/idverify/user-verifications"
        full_url = env.get_value('MC_API_BASE_URL') + service_uri

        # Define payload
        payload = {
            "optedInConsentStatus": True,
            "phoneNumber": int(userData["phone"]),
            "firstName": userData["firstName"],
            "lastName": userData["lastName"],
            "countryCode": "CO",
            "address": userData["address"],
            "city": "Zipaquirá",
            "region": "CU",
            "dob": userData["birthdate"],
            "last4ssn": 1234,
            "nationalId": userData["id"],
            "emailAddress": userData["email"]
        }

        # Create request body
        # Note its relevant to hash the payload before sending it
        request = requests.Request()
        request.method = "POST"
        request.url = full_url
        request.data = sha256(payload)
        
        signer = OAuthSigner(
            env.get_value('MC_CONSUMER_KEY'),
            signinig_key
        )
        request = signer.sign_request(full_url, request)

        # Send request
        s = requests.Session()
        data = s.send( request.prepare() )

        if data.status_code == 200:
            # TODO Check account info
            return True # Test purposes
        else: 
            # An error ocurred
            print( data.json() )
            return True

    def sendVerificationEmail( self, user ):

        # Getting user's id
        user_id = urlsafe_base64_encode(str(user.id).encode('utf-8'))

        # Generate an unique token for the user
        token = emailTokenGenerator.make_token(user)

        subject = '[OfertApp Team] Verifica tu cuenta'
        from_email = settings.EMAIL_HOST_USER
        to = user.email
        text_content = f'''
            <h1 style="color:#00BF63">Bienvenido a OfertApp</h1>
            <p>Para verificar tu cuenta haz click en el siguiente enlace
            <a href="{settings.WEB_URL}{settings.EMAIL_VERIFICATION_URL_ENDPOINT}/{token}/{user_id}/">
                Verificar cuenta!
            </a></p>

            No contestes a este mensaje (y perdon por el spam :D)
        '''

        try:
            # Sometimes emails get ratelimited
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to]
            )
            email.content_subtype = "html"

            email.send()

        except Exception as e:
            print(e)

    def sendPasswordResetEmail( self, user ):

        # Getting user's id
        user_id = urlsafe_base64_encode(str(user.id).encode('utf-8'))

        # Generate an unique token for the user
        token = resetPasswordTokenGenerator.make_token(user)

        subject = '[OfertApp Team] Cambia tu contraseña'
        from_email = settings.EMAIL_HOST_USER
        to = user.email
        text_content = f'''
            <h1 style="color:#00BF63">Hola {user.firstName}</h1>
            <p>Para cambiar tu contraseña haz click en el siguiente enlace
            <a href="{settings.WEB_URL}{settings.EMAIL_PASSWORD_RESET_URL_ENDPOINT}/{token}/{user_id}/">
                Cambiar contraseña!
            </a></p>

            No contestes a este mensaje (y perdon por el spam :D)
        '''

        try:
            # Sometimes emails get ratelimited
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to]
            )
            email.content_subtype = "html"

            email.send()

        except Exception as e:
            print(e)

def checkUserPermissions( user ):
    permissionsDict = {
        'isAdmin' : hasattr(user, 'admin'),
        'isVerified' : user.verified,
        'isBlocked' : user.blocked
    }
    return permissionsDict

def checkMembershipExpiration( ):
    expiredUsers = User.objects.filter(
        vipMemberSince__lte = datetime.now(),
        vipState = True
    )
    print("================================")
    print("Expired users: " + str(len( expiredUsers )))

    if not settings.ENABLE_SCHEDULERS:
        print("Skipping scheduler")
        return

    for user in expiredUsers:
        user.vipState = False
        user.save()

        # Notify the user sighly
        notify(
            user, "Tu membresía ha expirado",
            "Tu membresía ha expirado, puedes renovarla en cualquier momento"
        )

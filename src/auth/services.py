import requests
import environ
import base64
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# Read env variables
env = environ.Env()
environ.Env.read_env()

# TO Complete
class AccountCheckService():
    def __init__(self ):
        self.nequi_token = None
        self.paypal_token = None
    
    def checkAccount(self, userData):
        if userData["accountType"] == 'PP':
            return self.checkPaypalAccount(userData)
        elif userData["accountType"] == 'NQ':
            return self.checkNequiAccount(userData)
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
        return requests.post(api, headers=headers, data=data).json()

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
            response_client = user_data['ResponseMessage']['ResponseBody']['any']['validateClientRS']

            # TODO: Use a better algorithm to check names similarity (maybe ADN method)
            if response_client['customerName'] == userData["firstName"] + " " + userData["lastName"]:
                return True
            return False
        except Exception as e:
            print(e)
            return False

import requests

# TO Complete
class AccountCheckService():
    def __init__(self, user ):
        self.user = user
    
    def checkAccount(self):
        if self.user.accountType == 'paypal':
            return self.checkPaypalAccount()
        elif self.user.accountType == 'stripe':
            return self.checkStripeAccount()
        else:
            return False
    
    def checkPaypalAccount(self):
        api = 'https://api-m.sandbox.paypal.com/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {
            'grant_type': 'client_credentials',
        }
        return requests.post(api, headers=headers, data=data).json()


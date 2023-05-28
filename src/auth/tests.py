from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient,APITestCase,RequestsClient
from .models import User

class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_user(self):
        url = '/api/v1/userinfo/'
        response = self.client.get(url)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_user(self):        
        url = '/api/v1/auth/register/'
        data = {'id': '2128765940',
                'firstName': 'Diego',
                'lastName': 'Rubio',
                'email':'diegorubioprueba12345@gmail.com',
                'username': 'diegrubio',
                'birthdate': '2002-10-20',
                'phone': '3005410888',
                'address': 'Cra 18 No 13 12',
                'townId': '2.45',
                'password': '123456789',
                'paymentAccountType': 'NQ',
                'paymentAccountNumber': '987654321',
                'idenIdType': 'CC',}
        response = self.client.post(url, data=data, format='json')           
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data["status"], "success")
        
class UserLoginTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_post_login(self):
        url = '/api/v1/auth/login/'
        data = {'user': 'edgonzalezdi',
                'password': '12345',
                }
        response = self.client.post(url, data=data, format='json')
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
class UserLogoutTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_logout(self):
        url = '/api/v1/auth/logout/'
        auth_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg1MDMxMTQwLCJpYXQiOjE2ODUwMjkzNDAsImp0aSI6ImNiYjY2MWI1ZWNhZDQ2NWJiN2MyNjA3NWY2NWI3ZDhjIiwidXNlcl9pZCI6MTAwMDgzMzEwNywidXNlcm5hbWUiOiJlZGdvbnphbGV6ZGkiLCJlbWFpbCI6InRlc3RlZGdkMTIzQGdtYWlsLmNvbSIsInZpcFN0YXRlIjpmYWxzZSwidmlwUHViQ291bnQiOjB9.BvqV3RFizz62jarYzy0M-4_49TE7IntAOvZItoG6PwA'
        headers = {'Authorization': f'Token {auth_token}'}
        response = self.client.get(url, headers=headers)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserInfoTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_info(self):
        url = '/api/v1/auth/logout/'
        auth_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg1MjQyOTQ3LCJpYXQiOjE2ODUyNDExNDcsImp0aSI6IjYwMjY1ZjczZWVjNDQ4YjU4NDhiMTI0OTZhMzA4ZGZmIiwidXNlcl9pZCI6MTAwMDgzMzEwNywidXNlcm5hbWUiOiJlZGdvbnphbGV6ZGkiLCJlbWFpbCI6InRlc3RlZGdkMTIzQGdtYWlsLmNvbSIsInZpcFN0YXRlIjpmYWxzZSwidmlwUHViQ291bnQiOjB9.C7ArV6orGRncUN-AA4HwoU8I7E-OAy-q161htccmZDU'
        headers = {'Authorization': f'Token {auth_token}'}
        response = self.client.get(url, headers=headers)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SendResetPasswordTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_post_sendResetPassword(self):
        url = '/api/v1/auth/recover-password/'
        data = {'email': 'prueba@gmail.com',
                }
        response = self.client.post(url, data=data, format='json')
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)    




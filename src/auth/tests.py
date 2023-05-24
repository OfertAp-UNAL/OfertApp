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
        data = {'id': '1000833107',
                'firstName': 'Edgar',
                'lastName': 'Gonzalez',
                'email':'testedgd123@gmail.com',
                'username': 'edgonzalezdi',
                'birthdate': '2002-10-20',
                'phone': '3005410888',
                'address': 'Cra 18 No 13 12',
                'townId': '2.45',
                'password': '123456789',
                'paymentAccountType': 'NQ',
                'paymentAccountNumber': '3124567890',
                'idenIdType': 'CC',}
        response = self.client.post(url, data=data, format='json')           
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data["status"], "success")
        

    


    

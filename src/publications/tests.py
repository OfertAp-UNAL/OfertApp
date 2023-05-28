from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient,APITestCase,RequestsClient
from .models import Category, Publication

class CategoryTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_category(self):
        url = '/api/v1/categories/'
        response = self.client.get(url)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_category(self):        
        url = '/api/v1/categories/'
        data = {'name': 'televisores'}
        response = self.client.post(url, data=data, format='json')           
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data["status"], "success")

class PublicationsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_publications(self):
        url = '/api/v1/publications/'
        response = self.client.get(url)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    


    

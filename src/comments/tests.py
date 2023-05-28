from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient,APITestCase,RequestsClient
from .models import Comment, Reaction

class CommentsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_comments(self):
        suburl = '/api/v1/comments/'
        publiId= '67b8a0eb-1aba-446a-af3a-873ab9bb4afa'
        url = suburl+publiId+'/'
        response = self.client.get(url)
        print(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


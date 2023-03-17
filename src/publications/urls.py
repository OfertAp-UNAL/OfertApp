from django.contrib import admin
from django.urls import path
from .views import PublicationView


urlpatterns = [
    path('publications/', PublicationView.as_view()),
    #path('register/', RegisterView.as_view()),
]

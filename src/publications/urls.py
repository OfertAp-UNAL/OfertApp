from django.contrib import admin
from django.urls import path
from .views import PublicationView, CategoryView


urlpatterns = [
    path('publications/', PublicationView.as_view()),
    path('categories/', CategoryView.as_view()),
]

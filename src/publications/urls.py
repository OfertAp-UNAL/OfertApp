from django.contrib import admin
from django.urls import path
from .views import PublicationView, CategoryView, OfferView


urlpatterns = [
    path('publications/<str:publicationId>/', PublicationView.as_view()),
    path('publications/', PublicationView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('offers/<str:publicationId>/', OfferView.as_view()),
]

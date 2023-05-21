from django.contrib import admin
from django.urls import path
from .views import PublicationView, CategoryView, OfferView, DeliveryView, ConfirmationView


urlpatterns = [
    path('publications/<str:publicationId>/', PublicationView.as_view()),
    path('publications/', PublicationView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('offers/<str:publicationId>/', OfferView.as_view()),
    path('publications/delivery/<str:publicationId>/', DeliveryView.as_view()),
    path('publications/confirm/<str:publicationId>/', ConfirmationView.as_view())
]

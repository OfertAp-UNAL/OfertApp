"""OfertApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import LoginView, RegisterView, VerifyView, UserInfoView
from .token.views import CustomTokenObtainPairView, CustomTokenRefreshView
from django.conf import settings

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/register/', RegisterView.as_view()),

    # Path for verifying emails, users (or frontend must call this endpoint)
    path(f'auth/{settings.EMAIL_VERIFICATION_URL_ENDPOINT}/<str:token>/<str:user64_id>/', 
        VerifyView.as_view(), name='verify_email'),
    
    # Tokens refresh must be done by logging in again

    # Get and update userinfo
    path('userinfo/', UserInfoView.as_view(), name='user_info')
]

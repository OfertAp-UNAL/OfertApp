from django.contrib import admin
from django.urls import path
from .views import MercadoPagoRechargeView, MercadoPagoWithdrawalView


urlpatterns = [
    path('payments/', MercadoPagoRechargeView.as_view()),
    path('withdrawals/', MercadoPagoWithdrawalView.as_view()),
]

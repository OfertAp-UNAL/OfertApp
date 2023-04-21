from rest_framework.serializers import ModelSerializer

from publications.serializers import OfferSerializer
from auth.serializers import AdminSerializer
from .models import Transaction, Payment, Account

class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'user', 'balance', 'frozen')
    
class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id', 'type', 'timestamp', 'amount', 'receipt', 'flow')
        
class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'type', 'description', 'timestamp', 
            'prevBalance', 'postBalance', 'prevFrozen', 
            'postFrozen', 'flow', 'offer', 'payment', 'admin')

    offer = OfferSerializer()
    payment = PaymentSerializer()
    admin = AdminSerializer()
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer

class TransactionView( APIView ):
    def get( self, request ):
        user = request.user
        if user is not None and user.is_authenticated:
            account = user.account
            transactions = Transaction.objects.filter( account=account ).order_by( '-timestamp' )
            return Response( 
                status = 200,
                data = {
                    "status": "success",
                    "data" : TransactionSerializer( transactions, many=True ).data 
                }
            )
        return Response( 
            status = 200,
            data = {
                "status": "error",
                "error": "User not authenticated"
            }
        )

class PaymentView( APIView ):
    def post(self, request ):
        # This is a callback sent by PayPal when a payment is made
        pass
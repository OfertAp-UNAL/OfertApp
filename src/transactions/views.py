from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer

class TransactionView( APIView ):
    def get( self, request ):
        user = request.user
        if user is not None and user.is_authenticated:
            transactions = Transaction.objects.filter( user=user )
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
                "message": "User not authenticated"
            }
        )
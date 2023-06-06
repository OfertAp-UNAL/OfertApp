from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Transaction
from .serializers import TransactionSerializer
from .services import buyMembership
from datetime import datetime

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
                "error": "Debes iniciar sesión para realizar esta acción"
            }
        )

class MemmbershipView( APIView ):
    def post(self, request ):
        # Getting request user
        user = request.user

        if user is None or not user.is_authenticated:
            return Response(
                status = 200,
                data = {
                    "status": "error",
                    "error": "Debes iniciar sesión para realizar esta acción"
                }
            )
        
        memberShipCost = settings.MEMBERSHIP_COST
        # Check if user has enough balance}
        account = user.account
        if account.balance < memberShipCost:
            return Response(
                status = 200,
                data = {
                    "status": "error",
                    "error": "No tienes suficiente saldo para comprar la membresía"
                }
            )
        
        # Perform transaction
        buyMembership( user )

        # Update user membership
        user.vipState = True
        user.vipPubCount = settings.MEMBERSHIP_PUBLICATIONS
        user.vipMemberSince = datetime.now()
        user.save()

        return Response(
            status = 200,
            data = {
                "status": "success",
                "data": "Membership bought successfully"
            }
        )
        
class PaymentView( APIView ):
    def post(self, request ):
        # This is a callback sent by PayPal when a payment is made
        pass
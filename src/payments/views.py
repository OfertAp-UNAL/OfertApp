from rest_framework.views import APIView
from rest_framework.response import Response
from .services import checkPayment, registerPayment, checkWithdrawal, registerWithdrawal
import mercadopago
import decimal
from django.conf import settings

# Instantiate SDK
sdk = mercadopago.SDK( settings.MP_ACCESS_TOKEN )

class MercadoPagoRechargeView( APIView ):

    def post(self, request ):
        request_values = request.data

        # Get data from Mercado pago
        payment_data = {
            "transaction_amount": float(request_values["transaction_amount"]),
            "token": request_values["token"],
            "installments": int(request_values["installments"]),
            "payment_method_id": request_values["payment_method_id"],
            "issuer_id": request_values["issuer_id"],
            "payer": {
                "email": request_values["payer"]["email"],
                "identification": {
                    "type": request_values["payer"]["identification"]["type"], 
                    "number": request_values["payer"]["identification"]["number"]
                }
            }
        }

        error = checkPayment( request.user, payment_data )

        if error is not None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : error
            })

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        # Check if payment was successful
        if payment["status"] != "approved":
            return Response(status = 200, data = {
                "status" : "error",
                "error" : payment["status_detail"] if "status_detail" in payment else payment["message"]
            })
        else:
            # Save payment as transaction
            registerPayment( request.user, payment_data )
            
            return Response(status = 200, data = {
                "status" : "success",
                "data" : payment
            })

class MercadoPagoWithdrawalView( APIView ):

    def post(self, request ):
        amount = decimal.Decimal(request.data["amount"])

        error = checkWithdrawal( request.user, amount )

        if error is not None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : error
            })
        
        # Create a withdrawal operation
        registerWithdrawal( request.user, amount )

        return Response(status = 200, data = {
            "status" : "success",
            "data" : {
                "amount" : amount
            }
        })
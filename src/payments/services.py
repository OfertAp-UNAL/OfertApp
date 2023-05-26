from transactions.services import rechargeBalance, withdrawBalance
from django.conf import settings

# Check payment data from Mercado Pago
def checkPayment( user, paymentData ):

    # First Check if user is logged In
    if not user.is_authenticated:
        return "User is not authenticated"
    
    # Check transaction amount info
    if paymentData["transaction_amount"] < settings.MINIMUM_OFFER_AMOUNT:
        return "Invalid transaction amount"
    
    payer_data = paymentData["payer"]

    # Check payer email
    if user.email != payer_data["email"]:
        return "Invalid payer email"
    
    # Check payer identification
    if user.id != int( payer_data["identification"]["number"] ):
        return "Invalid payer identification"
    
    return None

# Register payment as transaction
def registerPayment( user, paymentData ):

    # Register transaction and payment for this user
    # also update account balance
    rechargeBalance( user, paymentData )

# Withdrawal logic
def checkWithdrawal( user, amount ):

    # First check if user is logged in
    if not user.is_authenticated:
        return "User is not authenticated"
    
    # Check if user has enough balance
    if user.account.balance < amount:
        return "User has not enough balance"
    
    # At least the minimum offer amount is required to make a withdrawal
    if amount < settings.MINIMUM_OFFER_AMOUNT:
        return "Invalid withdrawal amount, must be greater than " + str(settings.MINIMUM_OFFER_AMOUNT)

    return None

# Register withdrawal as transaction
def registerWithdrawal( user, amount ):

    # This case would require a little bit more of effort with
    # Mercado Pago API

    # TODO: Implement Mercado Pago withdrawal
    
    # Register withdrawal as transaction
    withdrawBalance( user, amount )

from .models import Transaction, Payment
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import decimal

def placeBid(
        offer, description
    ):
    # Alter account and create a transaction when user places a Bid
    user = offer.user

    account = user.account # Reference the user who places the bid

    # Register transaction
    transaction = Transaction.objects.create(
        offer = offer,
        description = description,
        type = Transaction.TransactionTypeChoices.BID_PLACED,
        amount = offer.amount,
        prevBalance = account.balance,
        postBalance = account.balance - offer.amount,
        prevFrozen = account.frozen,
        postFrozen = account.frozen + offer.amount,
        flow = Transaction.TransactionFlowChoices.INFREEZE,
        account = account
    )

    transaction.save()

    # Alter account
    account.balance -= offer.amount
    account.frozen += offer.amount
    account.save()

def revokeBid(
        offer, description
    ):
    # Create a transaction when user places a Bid
    user = offer.user
    
    account = user.account # Reference the user who places the bid
    
    transaction = Transaction.objects.create(
        offer = offer,
        description = description,
        type = Transaction.TransactionTypeChoices.BID_REVOKED,
        amount = offer.amount,
        prevBalance = account.balance,
        postBalance = account.balance + offer.amount,
        prevFrozen = account.frozen,
        postFrozen = account.frozen - offer.amount,
        flow = Transaction.TransactionFlowChoices.OUTFREEZE,
        account = account
    )

    transaction.save()

    # Alter account
    account.balance += offer.amount
    account.frozen -= offer.amount
    account.save()

def acceptBid(
        offer, description
    ):
    # Alter account and create a transaction when user accepts a Bid
    user = offer.user
    
    account = user.account # Reference the user who places the bid
    
    # Alter account
    account.frozen -= offer.amount
    account.save()
    
    transaction = Transaction.objects.create(
        offer = offer,
        description = description,
        type = Transaction.TransactionTypeChoices.BID_ACCEPTED,
        amount = offer.amount,
        prevBalance = account.balance,
        postBalance = account.balance,
        prevFrozen = account.frozen,
        postFrozen = account.frozen - offer.amount,
        flow = Transaction.TransactionFlowChoices.OUTFREEZE,
        account = account
    )

    transaction.save()

    # Notify user via email
    # Getting user's id
    publicationId = offer.publication.id

    # Get seller and ask him for providing shipping information
    seller = offer.publication.user

    subject = '[OfertApp Team] Adjunta información de envío de producto'
    from_email = settings.EMAIL_HOST_USER
    to = seller.email
    text_content = f'''
        <h1 style="color:#00BF63">Adjunta información de envío de producto</h1>
        <p>Tan pronto como envíes tu producto, por favor adjunta la información de envío en el siguiente enlace
        <a href="{settings.WEB_URL}delivery/{publicationId}/">
            Agregar información de envío
        </a></p>

        No contestes a este mensaje (y perdon por el spam :D)
    '''

    try:
        # Sometimes emails get ratelimited
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to]
        )
        email.content_subtype = "html"

        email.send()

    except Exception as e:
        print(e)

    # Get buyer and ask him for confirming the reception of the product
    buyer = offer.user

    subject = '[OfertApp Team] Confirma la recepción de tu producto'
    from_email = settings.EMAIL_HOST_USER
    to = buyer.email
    text_content = f'''
        <h1 style="color:#00BF63">Confirma la recepción de tu producto</h1>
        <p>Una vez hayas recibido tu producto, por favor confirma la recepción en el siguiente enlace
        <a href="{settings.WEB_URL}confirm/{publicationId}/">
            Confirmar recepción
        </a></p>
        
        No contestes a este mensaje (y perdon por el spam :D)
    '''

    try:
        # Sometimes emails get ratelimited
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to]
        )
        email.content_subtype = "html"

        email.send()

    except Exception as e:
        print(e)

def rechargeBalance(
    user, transactionData
):
    # Get amount
    amount = decimal.Decimal( transactionData["transaction_amount"] )

    # Register transaction and payment for this user
    account = user.account

    # Create a Payment transaction
    payment = Payment.objects.create(
        type = Payment.PaymentTypeChoices.CREDIT_CARD,
        amount = amount,
        flow = Payment.PaymentFlowChoices.INFLOW
    )

    # Create a Transaction
    transaction = Transaction.objects.create(
        type = Transaction.TransactionTypeChoices.ACCOUNT_RECHARGE,
        description = "Account recharge",
        amount = amount,
        prevBalance = account.balance,
        postBalance = account.balance + amount,
        prevFrozen = account.frozen,
        postFrozen = account.frozen,
        flow = Transaction.TransactionFlowChoices.INFLOW,
        account = account,

        # This transaction will be related to a payment object
        payment = payment
    )

    # Alter account
    account.balance += amount
    account.save()

    # Save transaction
    transaction.save()

def withdrawBalance(
    user, amount
):
    # Register transaction and payment for this user
    account = user.account

    # Create a Payment transaction
    payment = Payment.objects.create(
        type = Payment.PaymentTypeChoices.CREDIT_CARD,
        amount = amount,
        flow = Payment.PaymentFlowChoices.INFLOW
    )

    # Create a Transaction
    transaction = Transaction.objects.create(
        type = Transaction.TransactionTypeChoices.ACCOUNT_WITHDRAWAL,
        description = "Account withdrawal",
        amount = amount,
        prevBalance = account.balance,
        postBalance = account.balance - amount,
        prevFrozen = account.frozen,
        postFrozen = account.frozen,
        flow = Transaction.TransactionFlowChoices.OUTFLOW,
        account = account,

        # This transaction will be related to a payment object
        payment = payment
    )

    # Alter account
    account.balance -= amount
    account.save()

    # Save transaction
    transaction.save()

def transferToUser(
    targetUser, description, amount, admin
):
    # Register transaction and payment for this user
    account = targetUser.account

    # Create a Transaction
    transaction = Transaction.objects.create(
        type = Transaction.TransactionTypeChoices.ADMIN_ADJUSTMENT,
        description = description,
        amount = amount,
        prevBalance = account.balance,
        postBalance = account.balance + amount,
        prevFrozen = account.frozen,
        postFrozen = account.frozen,
        flow = Transaction.TransactionFlowChoices.INFLOW,
        account = account,
        admin = admin
    )

    # Alter account
    account.balance += amount
    account.save()

    # Save transaction
    transaction.save()

def buyMembership(
    user
):
    # Calculate membresy cost
    amount = decimal.Decimal( settings.MEMBERSHIP_COST )
    
    # Register transaction and payment for this user
    account = user.account

    # Create a Transaction
    transaction = Transaction.objects.create(
        type = Transaction.TransactionTypeChoices.OTHER,
        description = "Renovaste tu membresía!",
        amount = amount,
        prevBalance = account.balance - amount,
        postBalance = account.balance,
        prevFrozen = account.frozen,
        postFrozen = account.frozen,
        flow = Transaction.TransactionFlowChoices.INFLOW,
        account = account
    )

    # Alter account
    account.balance -= amount
    account.save()

    # Save transaction
    transaction.save()
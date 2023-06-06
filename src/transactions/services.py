from .models import Transaction, Payment
from django.conf import settings
from publications.models import Offer
from util.services import sendEmail, notify
import decimal

def placeBid(
        offer
    ):

    # Alter account and create a transaction when user places a Bid
    user = offer.user

    account = user.account # Reference the user who places the bid

    publication = offer.publication
    description = f"""Pusiste una oferta sobre la publicación
                {publication.title} de {publication.user.username}
                por ${str(offer.amount)}."
                """
    
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
    
    publication = offer.publication
    description = f"""{user.username} puso una oferta mayor en la publicación
                    {publication.title} de {publication.user.username}
                    por ${str(offer.amount)}.
                    """
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

def finishBid(
        publication
    ):
    # First, lets get the highest offer
    publicationOffers = Offer.objects.filter(
        publication = publication
    ).order_by("-amount")

    # If there are no offers, we can just notify the owner
    if not publicationOffers or len(publicationOffers) == 0:
        # Notify the owner
        notify( 
            publication.user, 
            "Tu publicación %s ha expirado sin ofertas" % publication.title,
            "Mala suerte... Intenta publicarla de nuevo :)"
        )
        return
    
    # This publication had offers, so we can perform the
    # transaction
    highestOffer = publicationOffers[0]

    # Get seller and ask him for providing shipping information
    seller = publication.user

    # Notify users via email, this is a relevant operation
    sendEmail(
        seller, "Adjunta información de envío de producto",
        "Adjunta información de envío de producto",
        f'''
        <p>Tan pronto como envíes tu producto, por favor adjunta la información de envío en el siguiente enlace
        <a href="{settings.WEB_URL}delivery/{publication.id}/">
            Agregar información de envío
        </a></p>
        '''
    )

    # Get buyer and ask him for confirming the reception of the product
    buyer = highestOffer.user

    # Notify users via email, this is a relevant operation
    sendEmail(
        buyer, "Confirma la recepción de tu producto",
        "Confirma la recepción de tu producto",
        f'''
        <p>Una vez hayas recibido tu producto, por favor confirma la recepción en el siguiente enlace
        <a href="{settings.WEB_URL}confirm/{publication.id}/">
            Confirmar recepción
        </a></p>
        '''
    )

    # Alter publication
    publication.available = False
    publication.save()

def acceptBidOffer(
    publication
):
    # First, lets get the highest offer
    publicationOffers = Offer.objects.filter(
        publication = publication
    ).order_by("-amount")

    # If there are no offers, we can just notify the owner
    if not publicationOffers or len(publicationOffers) == 0:
        return
    
    # This publication had offers, so we can perform the
    # transaction
    highestOffer = publicationOffers[0]

    # User are asked to confirm the reception of the product
    # Alter account and create a transaction when user accepts a Bid
    user = highestOffer.user
    
    account = user.account # Reference the user who places the bid

    description = """
        Tu oferta ha sido la ganadora de la subasta:
        %s de %s
        """ % (publication.title, publication.user.username)
    
    # Register transaction for the user who placed the offer
    transaction = Transaction.objects.create(
        offer = highestOffer,
        description = description,
        type = Transaction.TransactionTypeChoices.BID_ACCEPTED,
        amount = highestOffer.amount,
        prevBalance = account.balance,
        postBalance = account.balance,
        prevFrozen = account.frozen,
        postFrozen = account.frozen - highestOffer.amount,
        flow = Transaction.TransactionFlowChoices.OUTFREEZE,
        account = account
    )

    # Alter account, unfreeze money previously frozen for this offer
    account.frozen -= highestOffer.amount
    account.save()

    transaction.save()

    # Now lets give the money to the seller (and take our fee)
    seller = publication.user

    # Register transaction for the user who placed the offer
    # User will see the money transfered to his account
    transactionTotal = Transaction.objects.create(
        offer = highestOffer,
        description = description,
        type = Transaction.TransactionTypeChoices.AUCTION_SALE,
        amount = highestOffer.amount,
        prevBalance = seller.account.balance,
        postBalance = seller.account.balance + highestOffer.amount,
        prevFrozen = seller.account.frozen,
        postFrozen = seller.account.frozen,
        flow = Transaction.TransactionFlowChoices.INFLOW,
        account = seller.account
    )

    # Charge our fee

    percentage = decimal.Decimal( settings.FEE_PERCENT )
    feeAmount = highestOffer.amount * percentage

    transactionFee = Transaction.objects.create(
        offer = highestOffer,
        description = description,
        type = Transaction.TransactionTypeChoices.AUCTION_SALE,
        amount = highestOffer.amount,
        prevBalance = seller.account.balance,
        postBalance = seller.account.balance - feeAmount,
        prevFrozen = seller.account.frozen,
        postFrozen = seller.account.frozen,
        flow = Transaction.TransactionFlowChoices.INFLOW,
        account = seller.account
    )

    # Alter account, add money to the seller
    seller.account.balance += highestOffer.amount - feeAmount
    seller.account.save()

    # Register transactions for this user
    transactionTotal.save()
    transactionFee.save()
    
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
        description = "Recargaste tu cuenta!",
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
        description = "Retiraste de tu cuenta!",
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
        flow = Transaction.TransactionFlowChoices.OUTFLOW,
        account = account
    )

    # Alter account
    account.balance -= amount
    account.save()

    # Save transaction
    transaction.save()

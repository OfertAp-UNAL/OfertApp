from .models import Transaction, Payment
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

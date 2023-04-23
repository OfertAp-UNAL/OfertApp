from .models import Transaction

def placeBid(
        offer, description
    ):
    # Alter account and create a transaction when user places a Bid
    user = offer.user

    account = user.account # Reference the user who places the bid

    # Alter account
    account.balance -= offer.amount
    account.frozen += offer.amount
    account.save()

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

    print("ola")

    transaction.save()

def revokeBid(
        offer, description
    ):
    # Create a transaction when user places a Bid
    user = offer.user
    
    account = user.account # Reference the user who places the bid
    
    # Alter account
    account.balance += offer.amount
    account.frozen -= offer.amount
    account.save()
    
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
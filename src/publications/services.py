from rest_framework.response import Response
from .models import Offer
from publications.models import Publication
from django.conf import settings
from auth.services import checkUserPermissions
from transactions.services import finishBid

import datetime

def checkOfferService(user, amount, publication):

    # Getting user permissions
    userPermissions = checkUserPermissions(user)

    # If user is an admin, he is not supossed to make offers
    if userPermissions['isAdmin']:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Admins can't make offers"
        })

    # Check if amount is valid
    if amount < 0:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid amount"
        })

    # Check if publication is available
    if not publication.available:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "This publication is not available"
        })
    
    # Check if amount is greater than minimum offer
    if amount < publication.minOffer:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "The amount must be greater than the minimum offer"
        })

    # Check if user is not blocked
    if user.blocked:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "You are blocked"
        })
    
    # Check if user is not the owner of the publication
    if user.id == publication.user.id:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "You can't make an offer to your own publication"
        })
    
    # Check if user has enough money
    if user.account.balance < amount:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "You don't have enough money"
        })
    
    # Check if this offer is the highest offer
    try:
        publicationOffers = Offer.objects.filter(publication = publication).order_by("-amount")
    except Offer.DoesNotExist:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid publication id"
        })

    if publicationOffers and publicationOffers[0].amount > amount:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "This offer does not have the highest amount"
        })
    
    # Return None if not issue found

def checkPublicationService(
        user, prioritary, endDate, minOffer,
        supportsData, supportsDescriptions
    ):
    # Getting user permissions
    userPermissions = checkUserPermissions(user)

    # If user is an admin, he is not supossed to make offers
    if userPermissions['isAdmin']:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Admins can't make publications"
        })
    
    # Check if user is able to make a prioritary publication
    if prioritary:
        if not user.vipState:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You can't powerup a publication if you are not a VIP member"
            })
        if user.vipPubCount <= 0:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You don't have more prioritary publications slots"
            })
    
    # Only VIP users will be able to set a publication's enddate
    if endDate is not None and not user.vipState:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You can't set a publication end date if you are not a VIP member"
            })
    
    # Check if support data is valid

    # First all arrays should have the same size
    if len(supportsData) != len(supportsDescriptions):
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid supports data, all arrays should have the same size"
        })

    # Also, at least one support is required
    if len(supportsData) == 0:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "At least one support is required"
        })

    # Check if enddate is in future
    if endDate is not None and endDate <= datetime.datetime.now() + datetime.timedelta(hours = 12):
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid end date, must be at least half day apart"
        })

    # Check if minimum offer is valid
    if minOffer <= settings.MINIMUM_OFFER_AMOUNT:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Invalid minimum offer, must be greater than " + 
            str(settings.MINIMUM_OFFER_AMOUNT)
        })

def checkPublicationExpiration():
    # Getting all pending publications
    pendingPublications = Publication.objects.filter(
        available = True, endDate__lte = datetime.datetime.now()
    )
    print("================================")
    print("Pending pubs: " + str(len( pendingPublications )))

    if not settings.ENABLE_SCHEDULERS:
        print("Skipping scheduler")
        return
    
    # Iterate through each one and process
    for publication in pendingPublications:
        
        # End bid (Note actual transactions aren't performed yet)
        finishBid(publication)
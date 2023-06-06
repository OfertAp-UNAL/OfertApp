from rest_framework.response import Response
from .models import Offer
from publications.models import Publication
from django.conf import settings
from auth.services import checkUserPermissions
from transactions.services import finishBid
from util.services import stringToDatetime

import datetime

def checkOfferService(user, amount, publication):

    # Getting user permissions
    userPermissions = checkUserPermissions(user)

    # If user is an admin, he is not supossed to make offers
    if userPermissions['isAdmin']:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Los admins no pueden realizar ofertas"
        })

    # Check if amount is valid
    if amount < 0:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Monto inválido"
        })

    # Check if publication is available
    if not publication.available:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Ésta publicación no está disponible"
        })
    
    # Check if amount is greater than minimum offer
    if amount < publication.minOffer:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "El monto debe ser mayor a la oferta mínima"
        })

    # Check if user is not blocked
    if user.blocked:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Estás bloqueado, no puedes realizar ofertas"
        })
    
    # Check if user is not the owner of the publication
    if user.id == publication.user.id:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "No puedes realizar ofertas en tus propias publicaciones"
        })
    
    # Check if user has enough money
    if user.account.balance < amount:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "No tienes suficiente dinero para realizar esta oferta"
        })
    
    # Check if this offer is the highest offer
    try:
        publicationOffers = Offer.objects.filter(publication = publication).order_by("-amount")
    except Offer.DoesNotExist:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "ID de publicación inválido"
        })

    if publicationOffers and publicationOffers[0].amount > amount:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Ya existe una oferta mayor a la tuya"
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
            "error" : "Los admins no pueden realizar publicaciones"
        })
    
    # Check if user is able to make a prioritary publication
    if prioritary:
        if not user.vipState:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes realizar una publicación prioritaria si no eres VIP"
            })
        if user.vipPubCount <= 0:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes realizar una publicación prioritaria si no tienes publicaciones prioritarias disponibles"
            })
    
    # Only VIP users will be able to set a publication's enddate
    if endDate is not None and not user.vipState:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes establecer una fecha de finalización si no eres VIP"
            })
    
    # Check if support data is valid

    # First all arrays should have the same size
    if len(supportsData) != len(supportsDescriptions):
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Los datos de los soportes no son válidos"
        })

    # Also, at least one support is required
    if len(supportsData) == 0:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Se requiere al menos un soporte"
        })

    # Check if enddate is in future
    if endDate is not None and stringToDatetime(endDate) <= datetime.datetime.now() + datetime.timedelta(hours = 12):
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "La fecha de finalización debe ser al menos 12 horas en el futuro"
        })

    # Check if minimum offer is valid
    if minOffer <= settings.MINIMUM_OFFER_AMOUNT:
        return Response(status = 200, data = {
            "status" : "error",
            "error" : "Monto de oferta mónimo inválido, debe ser mayor a " + 
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
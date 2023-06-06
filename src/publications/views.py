from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from publications.serializers import PublicationSerializer, CategorySerializer, OfferSerializer, \
    OfferCreateSerializer, PublicationSupportSerializer, PublicationCreateSerializer
from transactions.services import placeBid, revokeBid
from util.services import saveFile, checkFileExtension
from publications.models import Publication, Category, Offer
from .services import checkOfferService, checkPublicationService
from transactions.services import acceptBidOffer
import decimal

class PublicationView( APIView ):
    def post( self, request ):

        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes estar logueado para ejecutar ésta acción"
            })

        # Get data from request
        endDate = request.data.get("endDate", None)
        priority = request.data.get("priority", None)

        # Get supports for publication
        supportsData = request.FILES.getlist("supportsFiles")

        # Get supports descriptions for supports
        supportsDescriptions = request.data.getlist("supportsDescriptions")

        # Get minimum offer
        minOffer = request.data.get("minOffer", 0)

        try:
            minOffer = decimal.Decimal(minOffer)
        except ValueError:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Oferta mínima inválida"
            })

        # Check additional publication business logic
        errorResponse = checkPublicationService(
            user, priority, endDate, minOffer,
            supportsData, supportsDescriptions
            )
        if errorResponse is not None:
            return errorResponse

        # Get data from request
        data = {
            "title" : request.data.get("title"),
            "description" : request.data.get("description"),
            "minOffer" : minOffer,
            "category" : request.data.get("category"),
            "user" : user.id,
        }

        if priority is not None:
            data["priority"] = priority
        
        if endDate is not None:
            data["endDate"] = endDate

        serializer = PublicationCreateSerializer(data=data)

        if serializer.is_valid():
            
            # Save publication first
            publication = serializer.save()

            # For each support, create a support object
            for i in range(len(supportsData)):
                supportDescription = supportsDescriptions[i]
                supportFile = supportsData[i]
                
                message, fileType = checkFileExtension(supportFile)

                if message is not None:
                    return Response(status = 200, data = {
                        "status" : "error",
                        "error" : message
                    })

                # Save support file in external storage
                supportFile = saveFile(supportFile, "publication_supports")

                supportSerializer = PublicationSupportSerializer(data={
                    "publication" : publication.id,
                    "description" : supportDescription,
                    "type" : fileType,
                    "data" : supportFile
                })

                if supportSerializer.is_valid():
                    supportSerializer.save()
                else:
                    return Response(status = 200, data = {
                        "status" : "error",
                        "error" : supportSerializer.errors
                    })
                
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status" : "error", 
            "error" : serializer.errors
        })
    
    def get(self, request, publicationId = None):
        
        if publicationId is not None:
            try:
                publication = Publication.objects.get(pk=publicationId)
                data = PublicationSerializer(publication, context = {
                        "request" : request
                    }).data
                
                return Response(status = 200, data = {
                    "status" : "success",
                    "data" : data
                })
            except Exception:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de publicación inválido"
                })

        # Get parameters of filtering
        title = self.request.query_params.get("title", None)
        user = self.request.query_params.get("user", None)
        availableOnly = self.request.query_params.get("available", False)
        minPrice = self.request.query_params.get("minPrice", None)
        maxPrice = self.request.query_params.get("maxPrice", None)
        orderby = self.request.query_params.get("orderBy", "id")
        limit = self.request.query_params.get("limit", 100)

        # Check orderby validity
        if orderby not in ["relevance", "price", "offers", "comments"]:
            orderby = "id" # Make id a default

        # Get publications
        publications = Publication.objects.all()

        # Filter by title if provided
        if title is not None:
            publications = publications.filter(title__icontains=title)
        
        # Filter by user if provided
        if user is not None:
            publications = publications.filter(user__id=user)

        # Filter by availability if provided
        if availableOnly:
            publications = publications.filter(available=True)
        
        # Filter by price if provided
        if minPrice is not None:
            try:
                minPrice = float(minPrice)
                publications = publications.filter(minOffer__gte=minPrice)
            except ValueError:
                pass

        if maxPrice is not None:
            try:
                maxPrice = float(maxPrice)
                publications = publications.filter(minOffer__lte=maxPrice)
            except ValueError:
                pass

        # Order by provided filters
        if orderby == "relevance":
            publications = sorted(
                publications,
                key = lambda publication: publication.getPriorityScore(),
                reverse = True
            )
        elif orderby == "price":
            publications = publications.order_by("minOffer")
        elif orderby == "offers":
            publications = publications.annotate(
                offersCount = Count("offers")
            ).order_by("-offersCount")
        elif orderby == "comments":
            publications = publications.annotate(
                commentsCount = Count("comments")
            ).order_by("-commentsCount")
        elif orderby == "date":
            publications = publications.order_by("-createdAt")

        # Limit the number of publications
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                limit = 100

        publications = publications[:limit]

        # Return the publications
        return Response(status = 200, data = {
            "status" : "success",
            "data" : PublicationSerializer(publications, many=True).data
        })

class CategoryView( APIView ):
    def post( self, request ):
        data = {
            "name" : request.data.get("name"),                      
        }       

        serializer = CategorySerializer(data=data)

        if serializer.is_valid():
            
            serializer.save()          

                
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status": "error",
            "error" : serializer.errors
        })
    
    def get(self, request):
        categories = Category.objects.all()

        return Response(status = 200, data = {
            "status" : "success",
            "data" : CategorySerializer(categories, many=True).data
        })
    
class OfferView( APIView ):
    def post( self, request, publicationId = None ):
        
        user = request.user

        # Check if user is authenticated
        if user is None or not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes estar logueado para realizar ésta acción"
            })
        
        # All offers must belong to a publication
        if publicationId is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de publicación inválido"
            })
        
        amount = request.data.get("amount")

        # Check if amount have consistency
        try:
            amount = float(amount)
        except ValueError:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Monto inválido"
            })

        # Check if publication exists
        try:
            publication = Publication.objects.get(id=publicationId)
        except Publication.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de publicación inválido"
            })

        # Check offer
        errorResponse = checkOfferService(user, amount, publication)
        if errorResponse is not None:
            return errorResponse
        
        # Get last offer made by user
        data = {
            "amount" : request.data.get("amount"),
            "publication" : publicationId,
            "user" : user.id
        }

        serializer = OfferCreateSerializer(
            data = data,
        )

        if serializer.is_valid():

            # All checks were passed
            offer = serializer.save()

            # Freeze money for this offer
            placeBid( offer )

            # Disable previous higher offer, if any
            availableOffers = Offer.objects.filter(
                publication = publication,
                available = True
            ).exclude(
                # Exclude myself, ofc
                id = offer.id
            )

            # Disable offers that are not higher than this one anymore
            for availableOffer in availableOffers:
                availableOffer.available = False
                availableOffer.save()

                # Unfreeze money for this offer
                revokeBid(availableOffer)
        
            # Create a transaction: Freeze needed money for this offer

            return Response(
                status = 200,
                data = {
                    "status" : "success",
                    "data" : serializer.data
                }
            )
        
        return Response(
            status = 200,
            data = {
                "status" : "error",
                "error" : serializer.errors
            }
        )
    
    def get(self, request, publicationId = None):
        if publicationId is not None:
            try:
                offers = Offer.objects.filter(
                    publication = publicationId
                )
                return Response(
                    status=200,
                    data = {
                        "status" : "success",
                        "data" : OfferSerializer(offers, many=True ).data
                    })
            
            except Exception:
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "ID de publicación inválido"
                    })
        
        offers = Offer.objects.all()

        return Response({
            "status" : "success",
            "data" : OfferSerializer(offers, many=True).data
        })

class DeliveryView( APIView ):
    def post( self, request, publicationId ):

        data = {
            "deliveryId" : request.data.get("deliveryId"),
            "deliveryType" : request.data.get("deliveryType"),
        }

        user = request.user
        if user is None or not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes estar logueado para realizar ésta acción"
            })

        # Check if user is the owner of the publication
        try:
            publication = Publication.objects.get(id=publicationId)
        except Publication.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de publicación inválido"
            })
        
        if publication.user.id != user.id:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes modificar la entrega de una publicación que no es tuya"
            })
        
        # Check if publication has an offer
        try:
            offer = Offer.objects.filter(publication=publicationId)
        except Offer.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Esta publicación no tiene ofertas"
            })
        
        if not offer or len(offer) == 0:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "This publication has no offers"
            })
    
        # Check if publication has a delivery
        if publication.deliveryType is not None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Esta publicación ya tiene una entrega"
            })
        
        # Update publication info
        serializer = PublicationSerializer(
            publication,
            data = data,
            partial = True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : serializer.errors
        })

class ConfirmationView( APIView ):
    def post(self, request, publicationId):
        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes estar logueado para ejecutar ésta acción"
            })
        
        # Check if publication exists
        try:
            publication = Publication.objects.get(id=publicationId)
        except Publication.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de publicación inválido"
            })
        
        # Check if user is the winner of the publication
        try:
            offers = Offer.objects.filter(publication=publicationId).order_by("-amount")
        except Offer.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Esta publicación no tiene ofertas"
            })
        
        if len(offers) == 0:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Esta publicación no tiene ofertas"
            })
        
        if user.id != offers[0].user.id:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes confirmar una publicación que no es tuya"
            })
        
        # Check if publication has a delivery
        if publication.deliveryType is None:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Esta publicación no tiene una entrega"
            })
        
        # Now mark publication as confirmed
        publication.confirmed = True
        publication.save()

        # Finally, end the transaction
        acceptBidOffer(publication)

        return Response(status = 200, data = {
            "status" : "success",
            "data" : PublicationSerializer(publication).data
        })
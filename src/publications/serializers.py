import rest_framework.serializers as serializers
from publications.models import Publication, Category, Offer, PublicationSupport
from auth.serializers import UserSerializer
from comments.serializers import PublicationCommentSerializer

class OfferSerializer(serializers.ModelSerializer):

    # User author is a relevant part of offers information
    user = UserSerializer()

    class Meta:
        model = Offer
        fields = (
            'amount', 'available', 'id', 'user', 'createdAt', 'publication')
        ordering = 'amount'

class OfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'amount', 'available', 'id', 'publication', 'createdAt', 'user'    
        )
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name', 'id')
        
class PublicationSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationSupport
        fields = (
            'id', 'type', 'data', 'description', 'publication')

class PublicationCreateSerializer(serializers.ModelSerializer):
    endDate = serializers.DateTimeField(required=False)
    priority = serializers.BooleanField(required=False)

    class Meta:
        model = Publication
        fields = (
            'title', 'description', 'minOffer', 'endDate', 'category',
            'user', 'priority', 'user', 'id')
        
class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            'title', 'description', 'minOffer', 'endDate', 'available', 'reportable', 'category',
            'user', 'id', 'priority', 'user', 'comments', 'offers', 'supports', 'deliveryType', 'deliveryId',
            'createdAt', 'confirmed', 'currentPrice'
            )
    
    user = UserSerializer()
    category = CategorySerializer()

    # Nested serializers
    comments = serializers.SerializerMethodField(
        'getComments'
    )
    offers = serializers.SerializerMethodField(
        'getOffers'
    )
    currentPrice = serializers.SerializerMethodField(
        'getCurrentPrice'
    )

    # Here the order doesn't care at all
    supports = PublicationSupportSerializer(many=True)

    def getComments(self, publication):
        comments = publication.comments.all().order_by('-createdAt')
        return PublicationCommentSerializer(comments, context = self.context, many=True).data

    def getOffers(self, publication):
        offers = publication.offers.all().order_by('-amount')
        return OfferSerializer(offers, many=True).data

    def getCurrentPrice(self, publication):
        offers = publication.offers.all().order_by('-amount')
        if len(offers) > 0:
            return offers[0].amount
        else:
            return publication.minOffer
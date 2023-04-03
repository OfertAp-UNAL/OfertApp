import rest_framework.serializers as serializers
from publications.models import Publication, Category, Offer, PublicationSupport
from auth.serializers import UserSerializer
from comments.serializers import PublicationCommentSerializer

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'ammount', 'available', 'id', 'user', 'publication')
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name', 'id')
        
class PublicationSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationSupport
        fields = (
            'id', 'type', 'data', 'description')

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            'title', 'description', 'minOffer', 'endDate', 'available', 'reportable', 'category',
            'user', 'id', 'priority', 'user', 'comments', 'offers', 'supports')
    user = UserSerializer()
    comments = PublicationCommentSerializer(many = True)
    offers = OfferSerializer(many = True)
    category = CategorySerializer()
    supports = PublicationSupportSerializer(many = True)


        

    
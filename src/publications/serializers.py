import rest_framework.serializers as serializers
from publications.models import Publication, Category, Offer

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            'title', 'description', 'minOffer', 'endDate', 'available', 'reportable', 'category',
            'user', 'id', 'priority')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name', 'id')
        
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'ammount', 'available', 'id', 'user', 'publication')
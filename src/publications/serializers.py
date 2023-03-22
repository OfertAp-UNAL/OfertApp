import rest_framework.serializers as serializers
from publications.models import Publication, Category

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            'title', 'description', 'minOffer', 'endDate', 'available', 'reportable', 'category',
            'user', 'id')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name', 'id')
import rest_framework.serializers as serializers
from publications.models import Publication, Category, Offer, PublicationSupport
from reports.models import Report, ReportSupport
from auth.serializers import UserSerializer
from publications.serializers import PublicationSerializer

class ReportCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            'id', 'type', 'body', 'user', 'publication', 'createdAt')
    
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            'id', 'user', 'type','body','open', 'visible', 'user','publication', 'createdAt')
    
    user = UserSerializer()
    publication = PublicationSerializer()

class ReportSupportCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSupport
        fields = (
            'id', 'type', 'body', 'data', 'user', 'report', 'createdAt')
    
class ReportSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSupport
        fields = (
            'id', 'user', 'type', 'body', 'data', 'visible', 'report', 'createdAt')
    
    user = UserSerializer()
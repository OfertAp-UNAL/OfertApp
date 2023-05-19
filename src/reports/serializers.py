import rest_framework.serializers as serializers
from publications.models import Publication, Category, Offer, PublicationSupport
from reports.models import Report, ReportSupport
from auth.serializers import UserSerializer
from publications.serializers import PublicationSerializer

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            'id', 'user', 'type','body','open', 'visible', 'user','publication')
    
    user = UserSerializer()
    publication = PublicationSerializer()

class ReportSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSupport
        fields = (
            'id', 'user', 'type', 'body', 'data', 'visible', 'report')
    
    user = UserSerializer()
    report = ReportSerializer()
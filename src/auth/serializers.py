import rest_framework.serializers as serializers
from auth.models import User, Admin

class UserSerializer(serializers.ModelSerializer):

    # Add useful fields for getting user info
    commentsCount = serializers.SerializerMethodField(
        method_name="countComments"
    )

    publicationsCount = serializers.SerializerMethodField(
        method_name="countPublications"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount',
            'firstName', 'lastName', 'idenIdType', 'createdAt', 'verified', 'reputation',
            'commentsCount', 'publicationsCount'
        )
    
    def countComments(self, user):
        return user.comments.count()

    def countPublications(self, user):
        return user.publications.count()

class AdminSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    class Meta:
        model = Admin
        fields = '__all__'

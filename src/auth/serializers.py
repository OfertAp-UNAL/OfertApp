import rest_framework.serializers as serializers
from auth.models import User, Admin

class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount',
            'firstName', 'lastName', 'idenIdType', 'createdAt', 'verified'
        )

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount',
            'firstName', 'lastName', 'idenIdType', 'createdAt', 'verified', 'hiredDate'
            )

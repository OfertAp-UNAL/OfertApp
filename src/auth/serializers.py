import rest_framework.serializers as serializers
from auth.models import User, Admin

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount'
            )

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount',
            'hiredDate'
            )

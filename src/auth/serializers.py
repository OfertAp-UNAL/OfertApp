import rest_framework.serializers as serializers
from auth.services import AccountCheckService
from auth.models import User, Admin

class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accountService = AccountCheckService()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount'
            )
    
    def validate(self, attrs):
        validation_data = super().validate(attrs)

        # TODO: Check if account is valid by billing info
        #if not self.accountService.checkAccount(validation_data):
        #    raise serializers.ValidationError('Invalid account')
        return validation_data

    

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = (
            'id', 'email', 'username', 'birthdate', 'phone', 'address', 'townId', 'password',
            'profilePicture', 'blocked', 'accountType', 'accountId', 'vipState', 'vipPubCount',
            'hiredDate'
            )

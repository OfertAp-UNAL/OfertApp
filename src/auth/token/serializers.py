from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenPairSerializer( TokenObtainPairSerializer ):
    @classmethod
    def get_token(cls, user):
        print("pasa")
        token = super().get_token(user)
    
        token["username"] = user.username
        token["email"] = user.email
        return token

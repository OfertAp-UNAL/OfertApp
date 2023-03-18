from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data['access'] = response.data.pop('access_token')
        response.data['refresh'] = response.data.pop('refresh_token')
        return response
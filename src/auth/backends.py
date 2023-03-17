from django.contrib.auth.backends import ModelBackend
from auth.models import User, Admin
from django.contrib.auth.hashers import make_password, check_password

class CustomBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        userIdField = 'email' if kwargs.get('email') else 'username'
        userId = kwargs.get(userIdField)
        password = kwargs.get('password')
        try:
            user = User.objects.get(
                **{userIdField: userId}
            )
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
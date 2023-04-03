from django.contrib.auth.backends import ModelBackend
from auth.models import User, Admin
from django.contrib.auth.hashers import make_password, check_password

class CustomBackend(ModelBackend):

    def authenticate(self, _, **kwargs):
        # Actually this is not his/her email always
        userID = kwargs.get("user")
        password = kwargs.get('password')

        # Try to get user by email
        try:
            user = User.objects.get(
                email=userID
            )
            # Check if the password is correct
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            # Could not find user by email
            pass

        # Try to retrieve user by username
        try:
            user = User.objects.get(
                username=userID
            )
            # Check if the password is correct
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            # Could not find user by email
            return None

        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.id) + str(timestamp) +
            str(user.verified)
        )
class ResetPasswordGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.id) + str(timestamp) +
            str(user.verified)
        )
emailTokenGenerator = TokenGenerator()
resetPasswordTokenGenerator = ResetPasswordGenerator()
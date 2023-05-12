from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

class SettingsView( APIView ):
    def get(self, request):
        if request.user is not None and request.user.is_authenticated:
            return Response(
                status = 200,
                data = {
                    "status": "success",
                    "data": {
                        "PPClientID" : settings.PP_CLIENT_ID
                    }
                }
            )
        return Response(
            status = 200,
            data = {
                "status": "error",
                "error": "User not authenticated"
            }
        )



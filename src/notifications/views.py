from .serializers import NotificationSerializer
from .models import Notification
from rest_framework.views import APIView, Response

class NotificationView( APIView ):

    def get( self, request ):

        # Check if user is logged in
        if not request.user.is_authenticated:
            return Response(
                status=200,
                data={
                    "status": "error",
                    "error": "Debes iniciar sesión para realizar esta acción"
                }
            )

        notifications = Notification.objects.filter( user = request.user )
        serializer = NotificationSerializer( notifications, many = True )
        return Response( 
            status = 200,
            data = {
                "status" : "success",
                "data" : serializer.data 
            }
        )

    def post( self, request ):
        # THis endpoint will update all notifications and mark them as read
        if not request.user.is_authenticated:
            return Response(
                status=200,
                data={
                    "status": "error",
                    "error": "Debes iniciar sesión para realizar esta acción"
                }
            )

        notifications = Notification.objects.filter( user = request.user )
        notifications.update( isRead = True )
        return Response( status = 200, data = { "status": "success" } )
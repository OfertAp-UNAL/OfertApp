from rest_framework.views import APIView
from rest_framework.response import Response
from publications.models import Publication, Offer
from comments.models import Comment
from reports.models import Report
from reports.serializers import ReportSerializer
from transactions.models import Transaction
from auth.models import User, Admin
from auth.services import checkUserPermissions

# Globally check user permissions
def checkPermissions(request):
    if not request.user.is_authenticated:
        return Response(
            status=200,
            data = {
                "status" : "error",
                "error" : "User not authenticated"
            }
        )
    permissions = checkUserPermissions(request.user)
    if permissions["isAdmin"] == False:
        return Response(
            status=200,
            data = {
                "status" : "error",
                "error" : "User is not admin"
            }
        )
    return None

class PublicationView(APIView):
    def delete(self, request, publicationId):
        
        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response

        try:
            publication = Publication.objects.get(id=publicationId)
            publication.delete()
            return Response(
                status=200,
                data = {
                    "status" : "success",
                    "data" : "Publication deleted"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Publication not found"
                }
            )

class CommentView(APIView):
    def delete(self, request, commentId):

        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response
        
        try:
            comment = Comment.objects.get(id=commentId)
            comment.delete()
            return Response(
                status=200,
                data = {
                    "status" : "success",
                    "data" : "Comment deleted"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Comment not found"
                }
            )

class UserView(APIView):
    def post(self, request, userId ):

        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response
        
        # Here we will block users
        data = {
            "block" : request.data["block"]
        }
        try:
            user = User.objects.get(id=userId)
            user.block = data["block"]
            user.save()
            return Response(
                status=200,
                data = {
                    "status" : "success",
                    "data" : "User blocked"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "User not found"
                }
            )


    def delete(self, request, userId):

        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response
        
        try:
            user = User.objects.get(id=userId)
            user.delete()
            return Response(
                status=200,
                data = {
                    "status" : "success",
                    "data" : "User deleted"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "User not found"
                }
            )

class ReportView( APIView ):
    def get( self, request ):

        # Get all reports in the whole system
        reports = Report.objects.all().order_by("-date")
        serializer = ReportSerializer(reports, many=True)
        return Response(
            status=200,
            data = {
                "status" : "success",
                "data" : serializer.data
            }
        )

    def post(self, request, reportId ):

        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response
        
        # Change reports status
        data = {
            "open" : request.data["open"]
        }

        try:
            report = Report.objects.get(id=reportId)
            report.open = data["open"]
            report.save()
            return Response(
                status=200,
                data = {
                    "status" : "success",
                    "data" : "Report status changed"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Report not found"
                }
            )





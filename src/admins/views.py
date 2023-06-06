from rest_framework.views import APIView
from rest_framework.response import Response
from publications.models import Publication, Offer
from comments.models import Comment
from reports.models import Report
from reports.serializers import ReportSerializer
from transactions.services import transferToUser
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
                "error" : "El usuario no tiene permisos de administrador"
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
                    "data" : "Publicación eliminada"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Publicación no encontrada"
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
                    "data" : "Comentario eliminado"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Comentario no encontrado"
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
                    "data" : "Usuario eliminado"
                }
            )
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Usuario no encontrado"
                }
            )

class ReportView( APIView ):

    def post(self, request, reportId ):

        # Should not allow this admin to act
        response = checkPermissions(request)
        if response != None:
            return response
        
        # Change reports status
        data = {
            "open" : request.data.get("open"),
            "visible" : request.data.get("visible"),
            "blockState" : request.data.get("blockState"),
            "transactionState" : request.data.get("transactionState"),
            "amount" : request.data.get("amount")
        }


        # General checks, always prefer not to make suspicious actions
        try:
            data["blockState"] = int(data["blockState"])
        except Exception:
            data["blockState"] = 1

        try:
            data["transactionState"] = int(data["transactionState"])
        except Exception:
            data["transactionState"] = 1
        
        try:
            data["amount"] = int(data["amount"])
        except Exception:
            data["amount"] = 0

        try:
            report = Report.objects.get(id=reportId)
            report.open = data["open"]
            report.visible = data["visible"]
            report.save() # First save global configs for this report
        except Exception:
            return Response(
                status=200,
                data = {
                    "status" : "error",
                    "error" : "Reporte no encontrado"
                }
            )

        # Now lets check if further process are neccesary
        blockedState = data["blockState"]

        if blockedState == 2:
            # Block the user who reports
            try:
                user = User.objects.get(id=report.user.id)
                user.blocked = True
                user.save()
            except Exception:
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "Usuario no encontrado"
                    }
                )
        elif blockedState == 3:
            # Block the user who is reported
            try:
                user = User.objects.get(id=report.publication.user.id)
                user.blocked = True
                user.save()
            except Exception:
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "Usuario no encontrado"
                    }
                )
         
         # Other cases do not require any further action

        # Now check actions needed for transactions
        transactionState = data["transactionState"]
        amount = data["amount"]
        
        if transactionState == 2:
            # Perform a transaction to the user who reports
            try:
                # Getting the user who reports
                user = User.objects.get(id=report.user.id)

                # Get myself as Admin
                admin = Admin.objects.get(user_id=request.user.id)

                transferToUser(
                    targetUser = user,
                    description = """
                        Transacción debido a reporte No. 
                        """ + str(report.id) + """
                    """,
                    amount = amount,
                    admin = admin
                )
            except Exception:
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "Usuario no encontrado"
                    }
                )
        elif transactionState == 3:
            # Perform a transaction to the user who is getting reported
            try:
                # Getting the user who is getting reported
                user = User.objects.get(id=report.publication.user.id)

                # Get myself as Admin
                admin = Admin.objects.get(user_id=request.user.id)

                transferToUser(
                    targetUser = user,
                    description = """
                        Transacción debido a reporte No. 
                        """ + str(report.id) + """
                    """,
                    amount = amount,
                    admin = admin
                )
            except Exception as e:
                print( e )
                return Response(
                    status=200,
                    data = {
                        "status" : "error",
                        "error" : "Usuario no encontrado"
                    }
                )

        # Other cases do not require any further action
        return Response(
            status=200,
            data = {
                "status" : "success",
                "data" : "Reporte actualizado"
            }
        )
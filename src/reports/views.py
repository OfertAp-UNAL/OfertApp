from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from reports.serializers import ReportSerializer, ReportSupportSerializer, ReportCreationSerializer, ReportSupportCreationSerializer
from reports.models import Report, ReportSupport
from publications.models import Publication
from auth.services import checkUserPermissions
from util.services import saveFile, checkFileExtension

class ReportView( APIView):
    def post( self,request,publicationId = None ):
        
        if publicationId is not None:
            try:
                publication = Publication.objects.get(pk=publicationId)
                
            except Publication.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de publicación inválido"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de publicación inválido"
                })

        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })

        # Getting user permissions
        userPermissions = checkUserPermissions(user)

        # If user is an admin, he is not supossed to make offers
        if userPermissions['isAdmin']:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Los administradores no pueden reportar publicaciones"
            })

        # Check if user isn't placing reports for himself
        if publication.user.id == user.id:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes reportar tus propias publicaciones"
            })
    
        # Get data from request
        data = {
            "type" : request.data.get("type"),
            "body" : request.data.get("body"),
            "user" : user.id,  
            "publication" : publicationId          
        }

        serializer = ReportCreationSerializer(data=data)

        if serializer.is_valid():
            
            serializer.save()   
                
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status": "error",
            "error" : serializer.errors
        })
    
    def get(self, request):

        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })

        # Getting user permissions
        userPermissions = checkUserPermissions(user)

        # If user is an admin, he is not supossed to make offers
        if userPermissions['isAdmin']:
            reports = Report.objects.all()
            return Response(status = 200, data = {
                "status" : "success",
                "data" : ReportSerializer(reports, many=True).data
            })

        reportsData = Report.objects.filter(
            Q(user=user) | Q(publication__user=user)
        )

        # Lets order reports
        reportsData = reportsData.order_by('-createdAt')

        return Response(status = 200, data = {
            "status" : "success",
            "data" : ReportSerializer(reportsData, many=True).data
        })

class ReportSupportView( APIView):
    def post( self,request, reportId = None ):
        if reportId is not None:
            try:
                report = Report.objects.get(pk=reportId)
                
            except Report.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de reporte inválido"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de reporte inválido"
                })
        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })

        # Getting user permissions
        userPermissions = checkUserPermissions(user)

        # Check if user is supossed to see this report
        canAddSupport = report.user.id == user.id 
        canAddSupport = canAddSupport or report.publication.user.id == user.id
        canAddSupport = canAddSupport and not userPermissions['isAdmin']

        if not canAddSupport:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "No puedes agregar soporte a este reporte"
            })
        
        body = request.data.get("body", None)

        # Getting file
        reportFile = request.FILES.get("data", None)

        if reportFile is not None:

            # Check file extension
            message, fileType = checkFileExtension( reportFile )

            if message is not None:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : message
                })
            
            # Save file
            fileData = saveFile(reportFile, "report_supports")

            if fileData is None:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Error al guardar el archivo"
                })

        # Get data from request
        data = {
            "type" : fileType if fileType is not None else "IMAGE", 
            "data" : fileData, 
            "user" : user.id,
            "report" : reportId      
        }

        if body is not None:
            data["body"] = body

        serializer = ReportSupportCreationSerializer(data=data)

        if serializer.is_valid():
            
            serializer.save()   

            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status": "error",
            "error" : serializer.errors
        })

    def get(self, request, reportId = None):
        if reportId is not None:
            try:
                report = Report.objects.get(pk=reportId)
                
            except Report.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de reporte inválido"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de reporte inválido"
                })
        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })

        # Getting user permissions
        userPermissions = checkUserPermissions(user)
        
        # Check if user is supossed to see this report
        canSeeReport = report.user.id == user.id 
        canSeeReport = canSeeReport or report.publication.user.id == user.id
        canSeeReport = canSeeReport or userPermissions['isAdmin']

        if not canSeeReport:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })
        
        reportSupport = ReportSupport.objects.filter(
            report=report
        )

        # Lets order reports
        reportSupport = reportSupport.order_by('-createdAt')

        # Lets join report data
        responseData = {}
        responseData["supports"] = ReportSupportSerializer(reportSupport, many=True).data
        responseData["report"] = ReportSerializer(report).data

        return Response(status = 200, data = {
            "status" : "success",
            "data" : responseData
        })
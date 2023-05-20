from rest_framework.views import APIView
from rest_framework.response import Response
from reports.serializers import ReportSerializer, ReportSupportSerializer, ReportCreationSerializer, ReportSupportCreationSerializer
from reports.models import Report, ReportSupport
from publications.models import Publication

class ReportView( APIView):
    def post( self,request,publicationId = None ):
        
        if publicationId is not None:
            try:
                Publication.objects.get(pk=publicationId)
                
            except Publication.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid publication id"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid publication id"
                })

        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You must be logged in to perform this action"
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
                "error" : "You must be logged in to perform this action"
            })
        report = Report.objects.filter(user=user)
        report.union(
            # Also get reports made to publications of the user
            Report.objects.filter(publication__user=user)
        )

        # Lets order reports
        report = report.order_by('-createdAt')

        return Response(status = 200, data = {
            "status" : "success",
            "data" : ReportSerializer(report, many=True).data
        })

class ReportSupportView( APIView):
    def post( self,request, reportId = None ):
        if reportId is not None:
            try:
                Report.objects.get(pk=reportId)
                
            except Report.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid report id"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid report id"
                })
        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You must be logged in to perform this action"
            })
        body = request.data.get("body", None)
        # Get data from request
        data = {
            "type" : request.data.get("type"), 
            "data" : request.data.get("data"), 
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
                    "error" : "Invalid report id"
                })        
        else:
            return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "Invalid report id"
                })
        # Get user from request
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "You must be logged in to perform this action"
            })
        
        reportSupport = ReportSupport.objects.filter(report=report)

        return Response(status = 200, data = {
            "status" : "success",
            "data" : ReportSupportSerializer(reportSupport, many=True).data
        })
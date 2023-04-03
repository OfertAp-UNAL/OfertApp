from rest_framework.views import APIView
from .services import MunicipalityService

service = MunicipalityService()

class MunicipalityView( APIView ):
    
    def get(self, request, type = None, value = None):
        # Value is the id of the department, region or specific municipality
        if type is None and value is None:
            # Get all municipalities
            return service.getAllMunicipalities()
        elif value is not None:
            # A filter must be applied
            if type == "department":
                # Get all municipalities of a department
                return service.getMunicipalitiesByDepartmentName(value)
            elif type == "region":
                # Get all municipalities of a region
                return service.getMunicipalitiesByRegion(value)
            elif type == "id":
                # Get a specific municipality
                return service.getMunicipalityById(value)

class DepartmentsView( APIView ):
    
    def get(self, request):
        # Get all departments
        return service.getAllDepartments()
        
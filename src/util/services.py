import requests
from django.conf import settings
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from notifications.models import Notification

class MunicipalityService():
    def __init__(self):
        self.url = settings.MUNICIPALITY_SERVICE_URL
    
    def buildRequest(self, paramsArray = None):
        request = requests.Request(
            'GET',
            self.url,
            params=paramsArray if paramsArray is not None else {}
        )
        
        return request

    def friendlyResponse(self, request, many = False, isMunicipality = True):
        try:
            # Send request
            session = requests.Session()
            response = session.send(request.prepare())

            if( response.status_code != 200 ):
                return Response( 
                    status = 200,
                    data = {
                        "status" : "error",
                        "error" :  response.status_code
                    })
        except requests.exceptions.RequestException as e:
            return Response( 
                    status = 200,
                    data = {
                        "status" : "error",
                        "error" :  e.strerror
                    })
        
        json = response.json()
        response = {
            "status" : "success"
        }

        # Rename fields of municipality object
        def refactorObject(json):
            if isMunicipality:
                # It is a municipality
                return {
                    "id" : json["c_digo_dane_del_municipio"],
                    "name" : json["municipio"],
                    "department" : json["departamento"],
                    "idDepartment" : json["c_digo_dane_del_departamento"],
                    "region" : json["region"]
                }
            else:
                # It is a departmanet
                return {
                    "id" : json["c_digo_dane_del_departamento"],
                    "name" : json["departamento"]
                }

        if many:
            # Build array of municipalities or departments
            response["data"] = []
            for object in json:
                response["data"].append(
                    refactorObject(object)
                )
        else:
            # Build a single municipality or department
            response["data"] = refactorObject(json)

        return Response( 
            status = 200,
            data = response 
        )
    
    def getAllDepartments(self):
        request = self.buildRequest(
            # Goverment API allows the use of SoQL queries through request's params
            {
                "$select" : "c_digo_dane_del_departamento,departamento",
                "$group" : "c_digo_dane_del_departamento,departamento"
            }
        )
        
        # there are department objects
        return self.friendlyResponse(request, many = True, isMunicipality = False)
    
    def getAllMunicipalities(self):
        request = self.buildRequest()
        return self.friendlyResponse(request, many = True)
    
    def getMunicipalitiesByDepartmentId(self,departmentId):
        request = self.buildRequest({
            "c_digo_dane_del_departamento" : departmentId
        })
        return self.friendlyResponse(request, many = True)

    def getMunicipalitiesByDepartmentName(self,departmentName):
        request = self.buildRequest({
            "departamento" : departmentName
        })
        return self.friendlyResponse(request, many = True)

    def getMunicipalitiesByRegion(self, region):
        request = self.buildRequest({
            "region": region
        })
        return self.friendlyResponse(request, many = True)

    def getMunicipalityById(self, id):
        request = self.buildRequest({
            "c_digo_dane_del_municipio": id
        })
        return self.friendlyResponse(request, many = False)

class CurrencyTranslationService():

    def __init__(self):
        self.url = settings.CURRENCY_URL
        self.init()
    
    def init(self, target = "COP" ):
        request = requests.Request(
            'GET', self.url, 
            params = {
                "apikey" : settings.CURRENCY_API_KEY,
                "currencies" : "USD",
                "base_currency" : target
            }
        )

        try:
            response = requests.Session().send(request.prepare())

            if( response.status_code != 200 ):
                self.copReference = 0
                return
            
            json = response.json()
            self.copReference = json["data"]["USD"]["value"]
        except requests.exceptions.RequestException as e:
            self.copReference = 0
    
    def convert(self, value):
        # Value comes in COP units
        return self.copReference * value

def sendEmail( 
        to, subject, subtitle, body 
    ):

    subject = f'[OfertApp Team] {subject}'
    from_email = settings.EMAIL_HOST_USER
    to = to.email
    text_content = f'''
        <h1 style="color:#00BF63">{subtitle}</h1>
        {body}

        No contestes a este mensaje (y perdon por el spam :D)
    '''

    try:
        # Sometimes emails get ratelimited
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to]
        )
        email.content_subtype = "html"

        email.send()

    except Exception as e:
        print(e)

def notify(
    user, title, description
):
    # Notify an user
    Notification.objects.create(
        user = user,
        title = title,
        description = description
    )

def getFileType( file ):
    print( file )
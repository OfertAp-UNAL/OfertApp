from django.urls import path
from .views import MunicipalityView, DepartmentsView, StatisticView, CurrencyTranslationView

urlpatterns = [
    path( "municipalities/", MunicipalityView.as_view() ),
    path( "municipalities/<str:type>/<str:value>/", MunicipalityView.as_view() ),
    path( "departments/", DepartmentsView.as_view() ),
    
    # Statistical info of user's actions in the app
    path( "statistics/", StatisticView.as_view() ),
    path( "conversion/<int:copValue>/", CurrencyTranslationView.as_view() ),
    path( "filetest/", CurrencyTranslationView.as_view() )
]
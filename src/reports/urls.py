from django.contrib import admin
from django.urls import path
from .views import ReportView, ReportSupportView

urlpatterns = [
    path('reports/', ReportView.as_view()),
    path('reports/<str:publicationId>/', ReportView.as_view()),
    path('reportsSupports/<str:reportId>/', ReportSupportView.as_view()),
  ]
from django.contrib import admin
from django.urls import path
from .views import ReportView, CommentView, PublicationView
from django.conf import settings

urlpatterns = [
    path('admin/publications/<str:publicationId>/', PublicationView.as_view() ),
    path('admin/comments/<str:commentId>/', CommentView.as_view()),
    path('admin/reports/<str:reportId>/', ReportView.as_view()),
]

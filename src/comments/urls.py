from django.contrib import admin
from django.urls import path
from .views import CommentView, ReactionView


urlpatterns = [
    path('comments/<str:publicationId>/<str:commentId>/', CommentView.as_view()),
    path('comments/<str:publicationId>/', CommentView.as_view()),
    path('reactions/<str:commentId>/', ReactionView.as_view()),
]

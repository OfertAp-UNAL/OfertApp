from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Comment
from .serializers import CommentSerializer, ReactionSerializer
from publications.models import Publication

class CommentView( APIView ):

    def get(self, _, publicationId, commentId = None):

        try:
            publication = Publication.objects.get(pk=publicationId)
        except Publication.DoesNotExist:
            return Response({
                "status" : "error",
                "error" : "Invalid publication id"
            })
        
        if commentId is not None:
            try:
                comment = publication.comments.get(pk=commentId)

                return Response({
                    "status" : "success",
                    "data" : CommentSerializer(comment).data
                })
            except Comment.DoesNotExist:
                return Response({
                    "status" : "error",
                    "error" : "Invalid comment id"
                })
        
        # List all comments in publication
        comments = publication.comments.all()
        return Response({
            "status" : "success",
            "data" : CommentSerializer(comments, many=True).data
        })
        
    def post(self, request, publicationId, commentId = None ):

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response({
                "status" : "error",
                "error" : "You must be logged in to perform this action"
            })
        
        data = {
            "publication" : publicationId,
            "user" : request.user.id,
            "text" : request.data.get("text"),
            "title" : request.data.get("title"),
            "parent" : commentId
        }

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response({
            "status" : "error",
            "errors" : serializer.errors
        })

class ReactionView( APIView ):

    def get( self, _, commentId ):
            
        try:
            comment = Comment.objects.get(pk=commentId)
        except Comment.DoesNotExist:
            return Response({
                "status" : "error",
                "error" : "Invalid comment id"
            })
        
        return Response({
            "status" : "success",
            "data" : ReactionSerializer(comment.reactions.all(), many=True).data
        })

    def post( self, request, commentId ):
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response({
                "status" : "error",
                "error" : "You must be logged in to perform this action"
            })
        
        try:
            comment = Comment.objects.get(pk=commentId)
        except Comment.DoesNotExist:
            return Response({
                "status" : "error",
                "error" : "Invalid comment id"
            })
        
        data = {
            "comment" : comment.id,
            "user" : request.user.id,
            "type" : request.data.get("type")
        }

        serializer = ReactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response({
            "status" : "error",
            "errors" : serializer.errors
        })
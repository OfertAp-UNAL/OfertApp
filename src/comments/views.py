from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Comment
from .serializers import PublicationCommentSerializer, CommentSerializer, ReactionCreateSerializer, ReactionSerializer
from publications.models import Publication

class CommentView( APIView ):

    def get(self, request, publicationId, commentId = None):

        try:
            publication = Publication.objects.get(pk=publicationId)
        except Publication.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de publicación inválido"
            })
        
        if commentId is not None:
            try:
                comment = publication.comments.get(pk=commentId)

                return Response(status = 200, data = {
                    "status" : "success",
                    "data" : PublicationCommentSerializer(comment, context = {
                        "request" : request
                    }).data
                })
            except Comment.DoesNotExist:
                return Response(status = 200, data = {
                    "status" : "error",
                    "error" : "ID de comentario inválido"
                })
        
        # List all comments in publication
        comments = publication.comments.all()
        return Response(status = 200, data = {
            "status" : "success",
            "data" : PublicationCommentSerializer(comments, context = {
                        "request" : request
                    }, many=True).data
        })
        
    def post(self, request, publicationId, commentId = None ):

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
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
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : serializer.errors
        })

class ReactionView( APIView ):

    def get( self, request, commentId ):
            
        try:
            comment = Comment.objects.get(pk=commentId)
        except Comment.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de comentario inválido"
            })
        
        return Response(status = 200, data = {
            "status" : "success",
            "data" : ReactionSerializer(comment.reactions.all(), context = {
                        "request" : request
                    }, many=True).data
        })

    def post( self, request, commentId ):
        
        # Get current user
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "Debes iniciar sesión para realizar esta acción"
            })
        
        try:
            comment = Comment.objects.get(pk=commentId)
        except Comment.DoesNotExist:
            return Response(status = 200, data = {
                "status" : "error",
                "error" : "ID de comentario inválido"
            })
        
        # Get reaction data
        data = {
            "comment" : comment.id,
            "user" : user.id,
            "type" : request.data.get("type")
        }

        # Check if user already reacted to comment
        commentReactions = comment.reactions.filter(user=request.user)
        if commentReactions.count() > 0:
            # Reaction must be updated (or deleted)
            reaction = commentReactions.first()

            # If reaction type is the same, delete it
            if data["type"] == reaction.type:
                reaction.delete()
                return Response(status = 200, data = {
                    "status" : "success",
                    "data" : "Reaction deleted"
                })
            
            # If reaction is different, update it
            serializer = ReactionCreateSerializer(reaction, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(status = 200, data = {
                    "status" : "success",
                    "data" : serializer.data
                })
        
        # Otherwise, this is a new reaction
        
        # Serialize reaction
        serializer = ReactionCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status = 200, data = {
                "status" : "success",
                "data" : serializer.data
            })
        
        return Response(status = 200, data = {
            "status" : "error",
            "error" : serializer.errors
        })
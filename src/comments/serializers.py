import rest_framework.serializers as serializers
from comments.models import Comment, Reaction
from auth.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ReactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    isLoggedUser = serializers.SerializerMethodField(
        method_name="isLoggedUserReaction"
    )
    class Meta:
        model = Reaction
        fields = '__all__'
    
    def isLoggedUserReaction(self, reaction):
        return reaction.user == self.context['request'].user

class PublicationCommentSerializer(serializers.ModelSerializer):

    # Can't serialize replies here, because it could cause a circular import 
    # However we can include it in the fields list and reuse its object when displaying comments
    user = UserSerializer()

    # Serialize parent
    parent = CommentSerializer()

    # Reactions count
    reactionsCount = serializers.SerializerMethodField(
        method_name="countReactions"
    )
    def countReactions(self, comment):
        toReturn = {
            "LIKE" : comment.reactions.filter(type="LIKE").count(),
            "DISLIKE" : comment.reactions.filter(type="DISLIKE").count(),
            "WARNING" : comment.reactions.filter(type="WARNING").count()
        }
        # Get user from context
        user = None
        request = self.context.get('request', None)
        if request is not None:
            user = request.user

        # Check if user is authenticated
        if user and user.is_authenticated:
            # Add a field to recognize if user has reacted to this comment, 
            # and what type of reaction did he use
            userReaction = comment.reactions.filter(user=user)
            if userReaction and userReaction.count() > 0:
                toReturn["userReaction"] = userReaction.first().type
            
        return toReturn

    class Meta:
        model = Comment
        fields = [
            'id', 'text', 'title', 'createdAt', 'user',
            'replies', 'reactionsCount', 'parent',
        ]
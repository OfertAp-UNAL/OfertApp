import rest_framework.serializers as serializers
from comments.models import Comment, Reaction
from auth.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'

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
        return {
            "LIKE" : comment.reactions.filter(type="LIKE").count(),
            "DISLIKE" : comment.reactions.filter(type="DISLIKE").count(),
            "WARNING" : comment.reactions.filter(type="WARNING").count()
        }

    class Meta:
        model = Comment
        fields = [
            'id', 'text', 'title', 'createdAt', 'user',
            'replies', 'reactions_count', 'parent'
        ]
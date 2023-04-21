from rest_framework.serializers import ModelSerializer
from publications.models import Offer
from comments.models import Reaction
from transactions.models import Transaction

class OfferStatsSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = ("id", "amount", "createdAt")

class ReactionStatsSerializer(ModelSerializer):
    class Meta:
        model = Reaction
        fields = ("id", "type", "createdAt")

class TransactionStatsSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "type", "timestamp")
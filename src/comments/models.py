from django.db import models
from auth.models import User
from publications.models import Publication

import uuid

class Comment( models.Model ):

    class Meta:
        db_table = "COMMENT"

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        null=False, 
        unique=True,
        db_column="comId"
    )
    text = models.CharField(
        max_length=256, 
        null=False,
        db_column="comText"
    )
    title = models.CharField(
        max_length=45, 
        null=True,
        db_column="comTitle"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, 
        null=False,
        db_column="comCreatedAt"
    )

    # Foreign Keys
    user = models.ForeignKey(
        User, related_name="comments",
        on_delete= models.CASCADE,
        db_column="usrId"
    )

    publication = models.ForeignKey(
        Publication, related_name="comments",
        on_delete= models.CASCADE,
        db_column="pubId"
    )

    parent = models.ForeignKey(
        "self", related_name="replies",
        on_delete= models.CASCADE, null=True,
        db_column="parentComId"
    )

class Reaction( models.Model ):
    class Meta:
        db_table = "REACTION"
    
    class TypeChoices(models.TextChoices):
        LIKE = 'LIKE'
        DISLIKE = 'DISLIKE'
        WARNING = 'WARNING'
    
    id = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        null=False, 
        unique=True,
        db_column="reacId"
    )
    type = models.CharField(
        max_length=45, 
        null=False, 
        choices=TypeChoices.choices,
        db_column="reacType"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, 
        null=False,
        db_column="reacCreatedAt"
    )

    user = models.ForeignKey(
        User, related_name="reactions",
        on_delete= models.CASCADE,
        db_column="usrId"
    )

    comment = models.ForeignKey(
        Comment, related_name="reactions",
        on_delete= models.CASCADE,
        db_column="comId"
    )
    
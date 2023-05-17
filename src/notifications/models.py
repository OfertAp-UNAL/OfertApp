from django.db import models
from auth.models import User
import uuid

class Notification( models.Model ):
    class Meta:
        db_table = 'NOTIFICATION'
    
    id = models.UUIDField( 
        primary_key = True, 
        default = uuid.uuid4, 
        editable = False,
        db_column='notId'
        )
    user = models.ForeignKey( 
        User, 
        on_delete = models.CASCADE,
        db_column='userId'
        )
    title = models.CharField( 
        max_length = 100, 
        null = True,
        db_column='notTitle'
        )
    description = models.CharField( 
        max_length = 255,
        null = True,
        db_column='notDescription'
        )
    isRead = models.BooleanField( 
        default = False,
        db_column='notIsRead'
        )
    createdAt = models.DateTimeField(
        auto_now_add = True,
        db_column='notCreatedAt'
        )

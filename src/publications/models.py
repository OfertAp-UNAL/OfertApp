from django.db import models
from auth.models import User
import uuid
import numpy as np
import datetime

class Category(models.Model):
    class Meta:
        db_table = "CATEGORY"
    
    id = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        null=False, unique=True,
        db_column="catId"
    )
    name = models.CharField(
        max_length=50, 
        null=False,
        db_column="catName"
    )

class Publication(models.Model):

    class Meta:
        db_table = "PUBLICATION"

    class DeliveryTypeChoices(models.TextChoices):
        SERVIENTREGA = 'SV'
        PROSEGUR = 'PS'
    
    def getPriorityScore(self):
        # Calculation of user's priority score
        # a = publication boosted, parameters: a_weight
        # b = userScore, parameters: b_weight
        # c = offers count, parameters: c_beta, c_epsilon, c_weight
        # s = comments count, parameters: d_beta, d_epsilon, d_weight
        
        # a parameters
        a_weight = 0.5
        a = int( self.priority )
        
        # b parameters
        b_weight = 0.3
        b = self.user.reputation

        # c parameters
        c_beta = 3; c_epsilon = 20; c_weight = 0.1
        c = 1 / (
            1 + np.exp( 
                ( self.offers.count() - c_epsilon ) / c_beta
            )
        )
        
        # d parameters
        d_beta = 3; d_epsilon = 10; d_weight = 0.1
        d = 1 / (
            1 + np.exp( 
                ( self.comments.count() - d_epsilon ) / d_beta
            )
        )

        # Calculate a percentage which representes publication priority
        return a * a_weight + b * b_weight + c * c_weight + d * d_weight

    id = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        null=False, unique=True,
        db_column="pubId"
    )
    title = models.CharField(
        max_length=50, 
        null=False,
        db_column="pubTitle"
    )
    description = models.CharField(
        max_length=256,
        null=False,
        db_column="pubDescription"
    )
    minOffer = models.DecimalField(
        max_digits=13,decimal_places=0,
        null=False,
        db_column="pubMinOffer"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, null=False,
        db_column="pubCreatedAt"
    )
    endDate = models.DateTimeField(
        null=False,
        db_column="pubEndDate",
        default=datetime.datetime.today() + datetime.timedelta(days=1)
    )
    available = models.BooleanField(
        default=True, null=False,
        db_column="pubAvailable"
    )
    reportable = models.BooleanField(
        default=True, null=False,
        db_column="pubReportable"
    )
    category = models.ForeignKey(
        Category, related_name="publications",
        on_delete= models.CASCADE,
        db_column="catId"
    )
    user = models.ForeignKey(
        User, related_name= "publications",
        on_delete= models.CASCADE,
        db_column="usrId"
    )
    priority = models.BooleanField(
        default=False, null=False,
        db_column="pubPriority"
    )
    deliveryType = models.CharField(
        max_length=2,
        null=True,
        choices=DeliveryTypeChoices.choices,
        db_column="pubDeliveryType"
    )
    deliveryId = models.CharField(
        max_length=45,
        null=True,
        db_column="pubDeliveryId"
    )

    # Buyer confirmed he got the product
    confirmed = models.BooleanField(
        default=False, null=False,
        db_column="pubConfirmed"
    )
    
class Offer(models.Model):
    class Meta:
        db_table = "OFFER"
    
    id = models.UUIDField(
        default=uuid.uuid4, 
        primary_key=True, 
        null=False, unique=True,
        db_column="offId"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, 
        null=False,
        db_column="offCreatedAt",
    )
    amount = models.DecimalField(
        max_digits=13, decimal_places=0,
        null=False,
        db_column="offAmount"
    )
    available = models.BooleanField(
        default=True, null=False,
        db_column="offAvailable"
    ) 
    user = models.ForeignKey(
        User, related_name= "offers",
        on_delete= models.CASCADE,
        db_column="usrId"
    )       
    publication = models.ForeignKey(
        Publication, related_name="offers",
        on_delete= models.CASCADE,
        db_column="pubId"
    )

class PublicationSupport(models.Model):
    class Meta:
        db_table = "PUBLICATIONSUPPORT"
    
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False, unique=True)
    class TypeChoices(models.TextChoices):
        IMAGE = 'IMAGE'
        VIDEO = 'VIDEO'

    type = models.CharField(
        max_length=45, 
        null=False, 
        choices=TypeChoices.choices,
        db_column="sopType"
    ) 
    data = models.URLField(
        max_length=200, null=False,
        db_column="sopData"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, 
        null=False,
        db_column="sopCreatedAt"
    )
    description = models.CharField(
        max_length=255, 
        null=False,
        db_column="sopDescription"
    )

    publication = models.ForeignKey(
        Publication, related_name="supports",
        on_delete= models.CASCADE,
        db_column="pubId"
    )
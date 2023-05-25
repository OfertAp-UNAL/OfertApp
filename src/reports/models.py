from django.db import models
from publications.models import Publication
from auth.models import User
import uuid

class Report(models.Model):

    class Meta:
        db_table = "REPORT"

    class ReportTypeChoices(models.TextChoices):
        DeliveryFraud = 'DF'
        SuspectFraud = 'SF'
        DontLike = 'DL'
        MisleadingAdvertisement = 'MA'
        QualityFraud = 'QF'

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        null=False, unique=True,
        db_column="repId"
    )
    type = models.CharField(
        max_length=50,
        null=False,
        db_column="repTitle",
        choices=ReportTypeChoices.choices
    )
    body = models.TextField(
        max_length=255,
        null=False,
        db_column="repBody"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True,
        null=False,
        db_column="repCreatedAt"
    )
    open = models.BooleanField(
        default=True,
        null=False,
        db_column="repOpen"
    )
    visible = models.BooleanField(
        default=True,
        null=False,
        db_column="repVisible"
    )
    user = models.ForeignKey(
        User,
        related_name="reports",
        on_delete=models.CASCADE,
        db_column="usrId"
    )
    publication = models.ForeignKey(
        Publication,
        related_name="reports",
        on_delete=models.CASCADE,
        db_column="pubId"
    )

class ReportSupport(models.Model):

    class Meta:
        db_table = "REPORTSUPPORT"

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        null=False, unique=True,
        db_column="repSopId"
    )
    user = models.ForeignKey(
        User,
        related_name="reportsSupport",
        on_delete=models.CASCADE,
        db_column="usrId"
    )

    class TypeChoices(models.TextChoices):
        IMAGE = 'IMAGE'
        VIDEO = 'VIDEO'
        
    type = models.CharField(
        max_length=45, 
        null=False, 
        choices=TypeChoices.choices,
        db_column="repSopType"
    )
    body = models.TextField(
        max_length=255, null=True,
        db_column="repSopBody"
    )
    data = models.URLField(
        max_length=200, null=False,
        db_column="repSopData"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True,
        null=False,
        db_column="repSopCreatedAt"
    )
    visible = models.BooleanField(
        default=True,
        null=False,
        db_column="repSopVisible"
    )
    report = models.ForeignKey(
        Report,
        related_name="reports_support",
        on_delete=models.CASCADE,
        db_column="repId"
    )
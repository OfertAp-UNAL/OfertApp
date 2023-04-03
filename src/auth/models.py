from django.db import models
from django.contrib.auth.models import AbstractUser
import numpy as np

class User (AbstractUser):

    class Meta:
        db_table = "USER"
        unique_together = ('accountType', 'accountId')
    
    class IdentificationType (models.TextChoices):
        CC = ('CC',"Cédula de ciudadanía")
        EX = ('CE',"Cédula de extranjería")
        TI = ('TI',"Tarjeta de identidad")
        PAS = ('PP',"Pasaporte")
        NIT = ('NIT',"Número de identificación tributaria")
    
    class AccountType (models.TextChoices):
        PAYPAL = ('PP',"PayPal")
        EFECTY = ('EF',"Efecty")
        NEQUI = ('NQ',"Nequi")
        CREDIT_CARD = ('CD',"Credit Card")
    
    id = models.IntegerField(
        primary_key=True, null=False, unique=True,
        db_column="usrId"
    )
    firstName = models.CharField(
        max_length=45, null=False,
        db_column="usrFirstName"
    )
    lastName = models.CharField(
        max_length=45, null=False,
        db_column="usrLastName"
    )
    username = models.CharField(
        max_length=45, unique=True, null=False,
        db_column="usrUsername"
    )
    email = models.EmailField(
        max_length=45, unique=True, null=False,
        db_column="usrEmail"
    )
    password = models.CharField(
        max_length=256, null=False,
        db_column="usrPassword"
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, null=False,
        db_column="usrCreatedAt"
    )
    birthdate = models.DateField(
        auto_now=False, auto_now_add=False, null=False,
        db_column="usrBirthdate"
    )

    idenIdType = models.CharField(
        max_length=3, choices=IdentificationType.choices,
        default=IdentificationType.CC, null=False,
        db_column="usrIdType"
    )
    
    phone = models.CharField(
        max_length=20, null=False,
        db_column="usrPhone"
    )
    address = models.CharField(
        max_length=100, null=False,
        db_column="usrAddress"
    )
    townId = models.DecimalField(
        max_digits=9, decimal_places=4,
        null=False,
        db_column="usrTownId"
    )
    profilePicture = models.ImageField(
        upload_to='profile_pictures', blank=False, null=False,
        db_column="usrProfilePicture",
        default="defaultProfile.png"
    )
    blocked = models.BooleanField(
        default=False, null=False,
        db_column="usrBlocked"
    )
    verified = models.BooleanField(
        default=False, null=False,
        db_column="usrVerified"
    )

    accountType = models.CharField(
        max_length=2, choices=AccountType.choices, 
        default=AccountType.PAYPAL, null=False,
        db_column="usrAccountType"
    )

    accountId = models.CharField(
        max_length=45, null=False,
        db_column="usrAccountId"
    )
    vipState = models.BooleanField(
        default=False, null=False,
        db_column="usrVipState"
    )
    vipPubCount = models.IntegerField(
        default=0, null=False,
        db_column="usrVipPubCount"
    )
    reputation = models.FloatField(
        default=1.0, null=False,
        db_column="usrReputation",
    )

    def updateReputation( self ):
        reports_count = np.sum( [
            publication.reports.count() for publication in self.publications.all()
        ])
        
        if reports_count > 0:
            # Reputation score, using a sigmoid function
            self.reputation = (-1) * (1 / (1 + np.exp( (reports_count - 7) / 3))) + 1
        else:
            self.reputation = 1.0

        self.save()

class Admin( models.Model ):

    class Meta:
        db_table = "ADMIN"
    
    hiredDate = models.DateField(
        auto_now=False, auto_now_add=False, null=False,
        db_column="admHiredDate"
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column="admUsrId", related_name="admin"
    )

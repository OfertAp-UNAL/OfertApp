from django.db import models
from django.contrib.auth.models import AbstractUser

class User (AbstractUser):

    class Meta:
        db_table = "USER"
    
    id = models.IntegerField(primary_key=True, null=False, unique=True)
    username = models.CharField(max_length=50, unique=True, null=False)
    email = models.EmailField(max_length=50, unique=True, null=False)
    password = models.CharField(max_length=256, null=False)
    createdAt = models.DateTimeField(auto_now_add=True, null=False)
    birthdate = models.DateField(
        auto_now=False, auto_now_add=False, null=False
    )
    phone = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=50, null=False)
    townId = models.FloatField( null=False )
    profilePicture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    blocked = models.BooleanField(default=False, null=False)

    class AccountType (models.TextChoices):
        PAYPAL = ('PP',"PayPal")
        EFECTY = ('EF',"Efecty")
        CREDIT_CARD = ('CD',"Credit Card")
    
    accountType = models.CharField(
        max_length=2, choices=AccountType.choices, 
        default=AccountType.PAYPAL,
        null=False
    )

    accountId = models.CharField(max_length=50, null=False)

    vipState = models.BooleanField(default=False, null=False)
    vipPubCount = models.IntegerField(default=0, null=False)

class Admin( User ):

    class Meta:
        db_table = "ADMIN"
    
    hiredDate = models.DateField()

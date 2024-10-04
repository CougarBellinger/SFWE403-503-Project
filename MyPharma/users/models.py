from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.manage import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):
    PharmacyManager = '1'
    PharmacyTechnician = '2'
    Pharmicist = '3'
    Cashier = '4'
    GeneralUser = '5'


    user_type_choices = (
        (PharmacyManager, "PharmacyManager"),
        (PharmacyTechnician, "PharmacyTechnician"),
        (Pharmicist, "Pharmacist"),
        (Cashier, "Cashier"),
        (GeneralUser, "GeneralUser")
    )

    user_type = models.CharField(
        max_length=10,
        choices=user_type_choices,
        blank=False,
        null=False,
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    # Add the unsuccessful login count field
    unsuccessful_login_count = models.IntegerField(default=0)

    # Fields for password reset
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    # Fields for social login integration
    social_provider = models.CharField(max_length=30, blank=True, null=True)
    social_uid = models.CharField(max_length=255, blank=True, null=True)
    social_access_token = models.CharField(max_length=255, blank=True, null=True)

    # Set username to not none
    username = models.CharField(max_length=255, blank=False, null=False)
    
    # Add any additional fields you need
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',]

    objects = CustomUserManager()

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(Group, related_name='users_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='users_permissions')

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
    
    
class PharmacyManager(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class PharmacyTechnician(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class Pharmacist(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class Cashier(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class GeneralUser(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
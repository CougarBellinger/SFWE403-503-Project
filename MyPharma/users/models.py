from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db import connection
from django.core.management import call_command

from users.manage import CustomUserManager
from datetime import datetime, timedelta

from django.conf import settings
import uuid


# Values for activity log
LOGIN, LOGOUT, MED_REMOVED, FILLED = "User Login", "User Logout", "Medication Removed", "Prescription Filled"

ACTION_TYPES = [
    (LOGIN, LOGIN),
    (LOGOUT, LOGOUT),
    (MED_REMOVED, MED_REMOVED),
    (FILLED, FILLED)
]


# Create your models here.
class CustomUser(AbstractUser):
    PharmacyManager = '1'
    PharmacyTechnician = '2'
    Pharmacist = '3'
    Cashier = '4'
    #Patient = '5'
    GeneralUser = '6'
    

    user_type_choices = (
        (PharmacyManager, "PharmacyManager"),
        (PharmacyTechnician, "PharmacyTechnician"),
        (Pharmacist, "Pharmacist"),
        (Cashier, "Cashier"),
        #(Patient, "Patient"),
        (GeneralUser, "GeneralUser")
    )

    user_type = models.CharField(
        max_length=10,
        choices=user_type_choices,
        blank=False,
        null=False,
    )

    # Credentials
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Set username to not none
    username = models.CharField(max_length=255, blank=False, null=False)
    
    # User privilages
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
    
    # Add any additional fields you need
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',]

    objects = CustomUserManager()

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(Group, related_name='users_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='users_permissions')

    #track first login
    is_first_login = models.BooleanField(default=True)

    #track user states
    is_active = models.BooleanField(default=True)

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

# class Patient(models.Model):
#     id = models.AutoField(primary_key=True)
#     admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class GeneralUser(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    default_birthdate = datetime(2006, 10, 17)
    date_of_birth = models.DateField(default=default_birthdate)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Medications(models.Model):
    name = models.CharField(max_length= 100)
    expiration_date = models.DateField() # must follow format YYYY - MM - DD
    tablet_count = models.IntegerField(default= 0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # For future use


    # true when tablet_count < 50
    is_orderable = models.BooleanField(default=False)

    # true when tablet_count < 120
    is_low = models.BooleanField(default=False)

    # true when (current date - expiration date) <= 0
    is_expired = models.BooleanField(default=False)

    # true when (current date - expiration date) < 30
    is_expiring_soon = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.tablet_count} tablets left)'

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f'Order {self.order_number} by {self.user.email}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.quantity} of {self.medication.name}'

class GenericItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medications, null=True, blank=True, on_delete=models.CASCADE)
    generic_item = models.ForeignKey(GenericItem, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.medication or self.generic_item} - {self.quantity}'



class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescriber_name = models.CharField(max_length=100)
    date_prescribed = models.DateField(auto_now_add=True)
    is_filled = models.BooleanField(default=False)

    def __str__(self):
        return f"Prescription for {self.patient} by {self.prescriber_name} on {self.date_prescribed}"

class PrescriptionMedication(models.Model):
    prescription = models.ForeignKey(Prescription, related_name='medications', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    num_tablets = models.IntegerField()

    def __str__(self):
        return f"{self.num_tablets} tablets of {self.medication} for {self.prescription.patient}"

class Activity(models.Model):
    # User performing the action
    actor =  models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    actor_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    #TODO: Medication assignment breaks the activity log
    # Keys to relevant models
        # medication = models.ForeignKey(Medications, on_delete=models.CASCADE, null=True)
        # patient    = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)

    # Action type and time performed
    action_type = models.CharField(choices=ACTION_TYPES, max_length=20)
    action_time = models.DateTimeField(auto_now_add=True)

    # Field for objectID
    object_id = models.PositiveIntegerField(blank=True, null=True)

    # Remarks for action and relevant data
    remarks = models.TextField(blank=True, null=True)
    data = models.JSONField(default=dict)


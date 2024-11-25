import json
from datetime import datetime

from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver
from django.core import serializers

from .models import Activity, Medications, Prescription, Patient, Order
from .models import LOGIN, LOGOUT, MED_REMOVED, FILLED, PURCHASED 

def log_medications_deleted(instance_id, user):
    print(f"log_medications_deleted triggered")
    print(f"{user.get_user_type_display()}")
    instance = Medications.objects.get(pk=instance_id)
    
    activity = Activity.objects.create(
        actor = user,
        actor_type = user.get_user_type_display(),
        action_type = MED_REMOVED,
        object_id = instance_id,
        remarks = (f"{user.username} removed {instance.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        data = {
            "med_name" : instance.name,
            "med_expDate" : instance.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
            "med_isExpired" : instance.is_expired,
        }
    )

    print("activity instantiated before save")

    activity.save()

    print(f"Activity #{activity.pk}: {activity.remarks}\n")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"log_user_login triggered")
    
    login = Activity.objects.create(
        actor = user,
        actor_type = user.get_user_type_display(),
        action_type = LOGIN,
        remarks = (f"{user.username} logged in on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    )

    print("activity instantiated before save")

    login.save()

    print(f"Activity #{login.pk}: {login.remarks}\n")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f"log_user_logout triggered")
    
    logout = Activity.objects.create(
        actor = user,
        actor_type = user.get_user_type_display(),
        action_type = LOGOUT,
        remarks = (f"{user.username} logged out on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    )

    print("activity instantiated before save")

    logout.save()

    print(f"Activity #{logout.pk}: {logout.remarks}\n")

def log_prescription_filled(instance_id, user):
    print(f"log_prescription_filled triggered")
    instance = Prescription.objects.get(pk=instance_id)
    medication = instance.medication

    prescription = Activity.objects.create(
        actor = user,
        actor_type = user.get_user_type_display(),
        action_type = FILLED,
        object_id = instance_id,
        remarks = (f"{user.username} filled prescription #{instance_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        data = {
            "prescriber_name" : instance.prescriber_name,
            "prescription_number" : instance.pk,
            "patient" : str(instance.patient),
            "date_prescribed" : str(instance.date_prescribed),
            "quantity" : instance.num_tablets,
            "medication" : medication.name
        }
    )

    print("activity instantiated before save")

    prescription.save()

    print(f"Activity #{prescription.pk}: {prescription.remarks}\n")

def log_order_purchased(instance_id, user):
    print(f"log_order_purchased triggered")
    instance = Order.objects.get(pk=instance_id)
    items = instance.items.all()
    total = "{:.2f}".format(instance.get_total_price())

    order = Activity.objects.create(
        actor = user,
        actor_type = user.get_user_type_display(),
        action_type = PURCHASED,
        object_id = instance_id,
        remarks = (f"{user.username} fufilled order #{instance_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        data = serializers.serialize("json", items)
    )

    print("activity instantiated before save")

    order.save()

    print(f"Activity #{order.pk}: {order.remarks}\n")

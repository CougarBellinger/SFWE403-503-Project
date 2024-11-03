from datetime import datetime

from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver

from .models import Activity, Medications
from .models import LOGIN, LOGOUT, MED_REMOVED 

def log_medications_deleted(instance_id, user):
    print(f"log_medications_deleted triggered")
    instance = Medications.objects.get(pk=instance_id)
    
    activity = Activity.objects.create(
        actor = user,
        action_type = MED_REMOVED,
        object_id = instance.pk,
        remarks = (f"{user.username} deleted {instance.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        data = {
            "med_name" : instance.name,
            "med_expDate" : instance.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
            "med_isExpired" : instance.is_expired,
        }
    )

    print("activity instantiated before save")

    activity.save()

    print(f"Activity #{activity.pk}: {activity.remarks}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"log_user_login triggered")
    
    login = Activity.objects.create(
        actor = user,
        action_type = LOGIN,
        remarks = (f"{user.username} logged in on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    )

    print("activity instantiated before save")

    login.save()

    print(f"Activity #{login.pk}: {login.remarks}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f"log_user_logout triggered")
    
    logout = Activity.objects.create(
        actor = user,
        action_type = LOGIN,
        remarks = (f"{user.username} logged out on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    )

    print("activity instantiated before save")

    logout.save()

    print(f"Activity #{logout.pk}: {logout.remarks}")
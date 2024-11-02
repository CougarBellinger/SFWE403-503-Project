from datetime import datetime

from .models import Activity
from .models import MED_REMOVED, FILLED

# @receiver(post_delete, sender=Medications)
def log_medications_deleted(sender, instance, user):
    print(f"log_medications_deleted triggered")
    
    activity = Activity.objects.create(
        actor = user,
        medication = instance,
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
    
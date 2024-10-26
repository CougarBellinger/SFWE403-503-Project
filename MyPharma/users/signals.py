from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from .models import Activity, Medications, Patient 
from .models import REMOVED, FILLED

@receiver(pre_delete, sender=Medications)
def log_medications_deleted(sender, instance, **kwargs):
    user = kwargs('user', None)

    #TODO: Finish populating creating
    Activity.objects.create(
        actor = user,
        medication = instance,
        action_type = REMOVED,
        object_id = instance.pk,
        remarks = f"{user.username} deleted {instance.name} on "
    )
from django.apps import AppConfig
from django.db.models.signals import post_delete

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # def ready(self):
    #     import users.signals
    #     from users.models import Medications

    #     post_delete.connect(users.signals.log_medications_deleted, sender=Medications)

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.dispatch import receiver
from django.db import connection
from django.core.management import call_command

from datetime import datetime, timedelta


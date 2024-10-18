from django import forms
from users.models import *
from .models import *

class OrderMedicationForm(forms.ModelForm):
    class Meta:
        model = Medications
        field = ['tablet_count', 'expiration_date']
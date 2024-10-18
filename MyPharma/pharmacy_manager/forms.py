from django import forms
from users.models import *
from .models import *

class OrderMedicationForm(forms.ModelForm):
    class Meta:
        model = Medications
        fields = ['tablet_count', 'expiration_date']
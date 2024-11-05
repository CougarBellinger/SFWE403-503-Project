from django import forms
from users.models import *
from .models import *

class OrderMedicationForm(forms.ModelForm):
    class Meta:
        model = Medications
        fields = ['tablet_count', 'expiration_date']

class Signature(forms.Form):
    CHOICES = [('P','Physical'),('E','Electronic')]
    like=forms.CharField(label='choice', widget=forms.RadioSelect(choices=CHOICES))
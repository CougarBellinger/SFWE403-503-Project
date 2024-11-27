from django import forms
from users.models import *
from .models import *

class OrderMedicationForm(forms.ModelForm):
    class Meta:
        model = Medications
        fields = ['tablet_count', 'expiration_date']

class SignatureForm(forms.Form):
    signature_type = forms.ChoiceField(
        choices=[('physical', 'Physical'), ('digital', 'Digital')],
        widget=forms.RadioSelect,
        required=True
    )
    DigitalSignature = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        signature_type = cleaned_data.get('signature_type')
        digital_signature = cleaned_data.get('DigitalSignature')

        if signature_type == 'digital' and not digital_signature:
            self.add_error('DigitalSignature', 'A valid digital signature is required')

        return cleaned_data

class FinancialStatsReportsForm(forms.Form):
    timeframe_choices = [('Last 7 days', 'Last 7 days'), ('Last 30 days', 'Last 30 days'), ('Last 12 months', 'Last 12 months')]
    timeframe = forms.ChoiceField(choices=timeframe_choices, widget= forms.Select(), label='Time frame')
    
class InventoryReportsForm(forms.Form):
    timeframe_choices = [('Last 7 days', 'Last 7 days'), ('Last 30 days', 'Last 30 days'), ('Last 12 months', 'Last 12 months')]
    timeframe = forms.ChoiceField(choices=timeframe_choices, widget= forms.Select(), label='Time frame')
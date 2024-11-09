from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import CustomUser, Patient, Medications
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'username', 'user_type','password1','password2')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [ 'username','first_name', 'last_name', 'email', 'user_type']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class PatientCreationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone_number', 'address', 'gender', 'emergency_contact_name', 'emergency_contact_phone', 'medical_history']

class FirstPasswordChangeForm(SetPasswordForm):
     class Meta:
        model = CustomUser
        fields = [ 'new_password1', 'new_password2']   

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']

class PaymentForm(forms.Form):
    payment_method_choices = [('Credit/Debit', 'Credit/Debit'), ('Cash', 'Cash')]
    payment_method = forms.ChoiceField(choices=payment_method_choices, widget= forms.Select())

class CardInfoForm(forms.Form):
    name_on_card = forms.CharField(required=False, min_length=1, max_length=100)
    card_number = forms.CharField(required=False, min_length=16, max_length=16)
    expiration_date = forms.DateField(required=False, input_formats=['%m%y'])
    csv_number = forms.CharField(required=False, min_length=3, max_length=3)

class CashForm(forms.Form):
    cash_given = forms.DecimalField(label='Cash Given', max_digits=10, decimal_places=2)

class ManualPrescriptionForm(forms.Form):
    # drop down menus
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), label='Select Patient')
    medication = forms.ModelChoiceField(queryset=Medications.objects.all(), label='Select Medication')

    # typed out fields
    num_tablets = forms.IntegerField(label='Number of Tablets', min_value=1, max_value=500)
    prescriber_name = forms.CharField(label='Name of Prescriber', min_length=1, max_length=100)

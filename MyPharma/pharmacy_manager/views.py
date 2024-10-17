from io import TextIOWrapper
from datetime import datetime
import csv

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from users.forms import *
from users.models import *
from users.decorators import *

@login_required
def manager_home(request):
    # List of low stock medications
    low_medications = Medications.objects.filter(tablet_count__lt=120)  # filter DB for tablet_count < 120

    # List of expiring and expiring soon medications
    current_date = datetime.today().date()

    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)

    context = {
        'expired_medications': expired_medications,
        'expiring_soon_medications': expiring_soon_medications,
        'low_medications': low_medications,
    }  # Passes dynamic data to template

    if request.method == 'POST':
        if 'sell_medication' in request.POST:
            medication_id = request.POST.get('medication_id')
            amount_to_sell = request.POST.get('amount_to_sell')

            try:
                # Fetch the medication by ID
                medication = Medications.objects.get(id=medication_id)

                # Convert amount_to_sell to integer
                amount_to_sell = int(amount_to_sell)

                # Check if there is enough stock to sell
                if medication.tablet_count >= amount_to_sell:
                    # Decrease the tablet count
                    medication.tablet_count -= amount_to_sell
                    medication.save()
                    messages.success(request, f"Successfully sold {amount_to_sell} of {medication.name}.")
                else:
                    messages.error(request, f"Not enough stock to sell {amount_to_sell} of {medication.name}. Current stock: {medication.tablet_count}")

            except Medications.DoesNotExist:
                messages.error(request, f"Medication with ID {medication_id} does not exist.")
            except ValueError:
                messages.error(request, f"Please enter a valid amount to sell.")
            except Exception as e:
                messages.error(request, f"An error occurred while selling medication: {e}")

        # Handle CSV Upload Form
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                name = row.get('Name')
                amount = row.get('Amount')
                exp_date_str = row.get('ExpDate')

                if not name or not exp_date_str:
                    messages.error(request, f"Error: Missing required field(s) in row: {row}")
                    continue

                try:
                    amount = int(amount)
                    expiration_date = datetime.strptime(exp_date_str, '%m/%d/%Y').date()

                    # Calculate boolean fields
                    is_low = amount < 120
                    is_orderable = amount < 50
                    is_expired = current_date > expiration_date
                    is_expiring_soon = expiration_date <= current_date + timedelta(days=30)

                    # Create the Medications object
                    Medications.objects.create(
                        name=name,
                        expiration_date=expiration_date,
                        tablet_count=amount,
                        is_low=is_low,
                        is_expired=is_expired,
                        is_expiring_soon=is_expiring_soon,
                        is_orderable=is_orderable
                    )

                    messages.success(request, f"Medication added: {name} with Expiration Date: {expiration_date}.")
                    
                except ValueError as ve:
                    messages.error(request, f"Error processing row {row}: {ve}")
                except Exception as e:
                    messages.error(request, f"Error processing row {row}: {e}")
            return redirect('manager_home')

    return render(request, 'manager_home.html', context)

    
@login_required
def order_page(request):
    return render(request, 'order_page.html')

def manager_low_medications():
    # list of low stock medications
    low_medications = Medications.objects.filter(tablet_count__lt= 120) # filter DB for tablet_count < 120
    context = {'low_medications': low_medications} # passes dynamic data to template  

def manager_expiring_medications():
    #list of expired and expiring soon medications
    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)
    context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications} # passes dynamic data to template  



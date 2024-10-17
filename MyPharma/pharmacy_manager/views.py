from io import TextIOWrapper
from datetime import datetime
import csv

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import OrderBy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from users.forms import *
from users.models import *
from users.decorators import *

@login_required
def manager_home(request):
    # list of low stock medications
    low_medications = Medications.objects.filter(tablet_count__lt= 120) # filter DB for tablet_count < 120
    
    
    #list of expiring and expiring soon medications
    #current_date = datetime.date.today()

   # if (current_date - expiration_date)

    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)

    context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications, 'low_medications': low_medications, } # passes dynamic data to template

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Check for missing fields
                name = row.get('Name')
                amount = row.get('Amount')
                exp_date = row.get('ExpDate')

                if not name or not amount or not exp_date:
                    messages.error(request, f"Error: Missing required field(s) in row: {row}")
                    continue

                try:
                    expiration_date = datetime.strptime(exp_date, '%m/%d/%Y').date()
                    
                    # Create Medications entry
                    Medications.objects.create(
                        name=name,
                        expiration_date=expiration_date,
                        tablet_count=int(amount)  # Convert amount to integer
                    )
                except ValueError as ve:
                    messages.error(request, f"Error processing row {row}: {ve}")
                except Exception as e:
                    messages.error(request, f"Error processing row {row}: {e}")
                    continue

            messages.success(request, "Medications successfully uploaded.")
            return redirect('manager_home')
    else:
        form = CSVUploadForm()

    return render(request, 'manager_home.html', {'form': form})


# list of low stock (< 120) medications
def low_medications_management(request):
    low_medications = Medications.objects.filter(is_low= True) # filter DB for tablet_count < 120
    context = {'low_medications': low_medications} # passes dynamic data to template  
    return render(request, 'low_medications_list.html', {'low_medications': low_medications})

# list of orderable (< 50) medications
def orderable_medications_management(request):
    orderable_medications = Medications.objects.filter(is_orderable= True) # filter DB for tablet_count < 50
    context = {'orderable_medications': orderable_medications} # passes dynamic data to template  
    return render(request, 'orderable_medications_list.html', {'orderable_medications': orderable_medications})

# list of expired and expiring soon medications
def expiring_medications_management(request):
    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)
    context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications} # passes dynamic data to template  
    return render(request, 'expiring_medications_list.html', {'expired_medications': expired_medications}, {'expiring_soon_medications': expiring_soon_medications})

def all_medications_view(request):
    all_medications = Medications.objects.all()
    ordered_medications = all_medications.order_by('tablet_count')
    context = {'ordered_medications':ordered_medications} 
    return render(request, 'all_medications_list.html', context)



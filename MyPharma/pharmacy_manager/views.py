from io import TextIOWrapper
from datetime import datetime
from django.utils import timezone
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import OrderBy, Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from users.forms import *
from users.models import *
from users.decorators import *
from users.signals import log_medications_deleted

from .forms import *

@login_required
def sell_medication_view(request):
    if request.method == 'POST':
        medication_id = request.POST.get('medication_id')
        amount_to_sell = request.POST.get('amount_to_sell')

        # Check if medication_id is a valid integer
        if not medication_id.isdigit():
            messages.error(request, "Error: Medication ID must be a positive integer.")
            return redirect('sell_medication')

        medication_id = int(medication_id)

        try:
            # Fetch the medication by ID
            medication = Medications.objects.get(id=medication_id)

            # Validate amount_to_sell
            if not amount_to_sell.isdigit() or int(amount_to_sell) <= 0:
                messages.error(request, "Error: Amount to sell must be a positive integer.")
                return redirect('sell_medication')

            amount_to_sell = int(amount_to_sell)

            # Check stock availability
            if medication.tablet_count >= amount_to_sell:
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

        return redirect('sell_medication')

    # For GET requests, fetch necessary context data
    low_medications = Medications.objects.filter(tablet_count__lt=120)
    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)

    context = {
        'low_medications': low_medications,
        'expired_medications': expired_medications,
        'expiring_soon_medications': expiring_soon_medications,
    }

    return render(request, 'sell_medication.html', context)

@login_required
def add_medication_view(request):
    current_date = datetime.today().date()

    if request.method == 'POST':
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

            return redirect('add_medication')

    return render(request, 'add_medication.html')

@login_required
def manager_home(request):
    # Fetch general information for display
    low_medications = Medications.objects.filter(tablet_count__lt=120)
    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)

    context = {
        'low_medications': low_medications,
        'expired_medications': expired_medications,
        'expiring_soon_medications': expiring_soon_medications,
    }

    return render(request, 'manager_home.html', context)


# list of low stock (< 120) medications
def low_medications_management(request):
    meds = Medications.objects.all()

    for m in meds:
        if m.tablet_count <= 120:
            m.is_low = True
        else:
            m.is_low = False
        
        if m.tablet_count < 50:
            m.is_orderable = True
        else:
            m.is_orderable = False
        
        m.save()

    low_medications = Medications.objects.filter(Q(is_low= True) | Q(is_orderable=True)) # filter DB for tablet_count < 120
    low_medications = low_medications.order_by('tablet_count')
    context = {'low_medications': low_medications} # passes dynamic data to template  
    return render(request, 'low_medications_list.html', {'low_medications': low_medications})

# list of orderable (< 50) medications
def orderable_medications_management(request):
    orderable_medications = Medications.objects.filter(is_orderable= True) # filter DB for tablet_count < 50
    context = {'orderable_medications': orderable_medications} # passes dynamic data to template  
    return render(request, 'orderable_medications_list.html', context)

# list of expired and expiring soon medications
def expiring_medications_management(request):
    meds = Medications.objects.all()

    for m in meds:
        if m.expiration_date <= timezone.now().date():
            m.is_expired = True
        else:
            m.is_expired = False
        
        if m.expiration_date < timezone.now().date() + timedelta(days= 30):
            m.is_expiring_soon = True
        else:
            m.is_expiring_soon = False

        m.save()
           
    expiring_medications = Medications.objects.filter(Q(is_expiring_soon=True) | Q(is_expired=True)) #filter items that are expiring soon or expired
    expiring_medications = expiring_medications.order_by('expiration_date') #sort items by expiration date
    context = {'expiring_medications': expiring_medications} # passes dynamic data to template  
    return render(request, 'expiring_medications_list.html', context)

def all_medications_view(request):
    ordered_medications = Medications.objects.all().order_by('-tablet_count')
    context = {'ordered_medications':ordered_medications} 
    return render(request, 'all_medications_view.html', {'ordered_medications' : ordered_medications})

def remove_medications(request, pk):
    medication = get_object_or_404(Medications, pk=pk)  # Get the medication object by its primary key (pk)
    medication.save()
    if request.method == 'POST':
        user = request.user

        log_medications_deleted(instance_id=medication.pk, user=user)
        
        medication.delete()  # Delete the medication from the database
        return redirect('expiring_medications_management')  # Redirect to expired medication management after deletion

    return render(request, 'remove_medications.html', {'medication': medication})

def order_medications(request, pk):
    medication = get_object_or_404(Medications, pk=pk)  # Get the medication object by its primary key (pk)
    if request.method == 'POST':
        form = OrderMedicationForm(request.POST, instance=medication)
        if form.is_valid():
            medication.save()
            return redirect('low_medications_management')
    else:
        form = OrderMedicationForm(instance=medication)

    return render(request, 'order_medications.html', {'form': form})

def activity_log(request):
    activity_items = Activity.objects.all().order_by('-action_time')
    user = request.user
    return render(request, 'activity_log_view.html', {"activity_items" : activity_items, "user" : user})

def activity_details(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    activity.save()
    if request.method == 'POST':
        return redirect('activity_log')  # Redirect to expired medication management after deletion

    return render(request, 'activity_details.html', {'activity': activity})

def sign_prescriptions(request):
    if request.method == 'POST':
        form = SignatureForm(request.POST)
        if form.is_valid():
            # Process form data if it's valid (e.g., save it or process further)
            # After success, redirect to manager_home
            messages.success(request, "Prescription signed successfully!")
            return redirect('signature_confirmation')
        else:
            # If form is not valid, return with error messages displayed
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignatureForm()

    return render(request, 'sign_prescriptions.html', {'form': form})

def inventory_reports(request):
    if request.method == 'POST':
        form = InventoryReportsForm(request.POST)

        if form.is_valid():
            timeframe = form.cleaned_data['timeframe']

            if timeframe == 'Last 7 days':
                return redirect('inventory_reports_week') 

            if timeframe == 'Last 30 days':
                return redirect('inventory_reports_month')
                    
            if timeframe == 'Last 12 months':
                return redirect('inventory_reports_year')

    else:
        form = InventoryReportsForm()

    return render(request, 'inv_report_timeframe.html', {'form': form})

def inventory_reports_week(request):
    timeframe = 'Last 7 days'
    total_meds_removed = Activity.objects.filter(action_type= 'Medication Removed', action_time__gte=(timezone.now().date() - timedelta(days=7))).count()
    # total_meds_added = Activity.objects.filter(action_type= 'Medication Added', action_time__gte=(timezone.now().date() - timedelta(days=7))).count()
    # total_meds_sold = Activity.objects.filter(action_type= 'Medication Sold', action_time__gte=(timezone.now().date() - timedelta(days=7))).count()
    
    return render(request, 'inventory_reports_week.html', {'total_meds_removed': total_meds_removed, 'timeframe': timeframe}) # need to add total_meds_added and total_meds_sold

#def inventory_reports_month(request):
    # timeframe = 'Last 30 days'
    # total_meds_removed = Activity.objects.filter(action_type= 'Medication Removed', action_time__gte=(timezone.now().date() - timedelta(days=30))).count()
    # total_meds_added = Activity.objects.filter(action_type= 'Medication Added', action_time__gte=(timezone.now().date() - timedelta(days=30))).count()
    # total_meds_sold = Activity.objects.filter(action_type= 'Medication Sold', action_time__gte=(timezone.now().date() - timedelta(days=30))).count()

    #return render(request, 'inventory_reports_month.html', {'total_meds_removed': total_meds_removed, 'timeframe': timeframe}) # need to add total_meds_added and total_meds_sold

#def inventory_reports_year(request):
    # timeframe = 'Last 12 months'
    # total_meds_removed = Activity.objects.filter(action_type= 'Medication Removed', action_time__gte=(timezone.now().date() - timedelta(days=365))).count()
    # total_meds_added = Activity.objects.filter(action_type= 'Medication Added', action_time__gte=(timezone.now().date() - timedelta(days=365))).count()
    # total_meds_sold = Activity.objects.filter(action_type= 'Medication Sold', action_time__gte=(timezone.now().date() - timedelta(days=365))).count()

    #return render(request, 'inventory_reports_month.html', {'total_meds_removed': total_meds_removed, 'timeframe': timeframe}) # need to add total_meds_added and total_meds_sold
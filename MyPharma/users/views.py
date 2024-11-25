# General imports
from io import TextIOWrapper
from datetime import datetime
import csv
import logging
from django.shortcuts import render, get_object_or_404


# Django imports
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.db.models import OrderBy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm

# Decorator imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .forms import UserCreationForm, UserRegistrationForm, ChangePasswordForm
from users.decorators import pharmacy_manager_required
from django.http import Http404


# App imports
from pharmacy_manager.views import *
from .models import Medications, Order, OrderItem
from .forms import *
from .models import *
from .signals import log_prescription_filled

logger = logging.getLogger(__name__)

@login_required
def home_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    if user.user_type == CustomUser.PharmacyManager:
        return redirect('manager_home') #Goes to manager home view in pharmacy_manager app
    else:
        return redirect('/users/customer_home')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Attempt to authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                # User's account is locked
                messages.error(request, 'Your account is locked. Please contact an admin for assistance.')
                return render(request, 'users/login.html', {'form': form})
            
            # Successful login
            user.unsuccessful_login_count = 0  # Reset the count on successful login
            user.save()  # Save the user object
            login(request, user)

            if user.is_first_login:
                return redirect('first_password_view')

            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect based on user type
            if user.user_type == CustomUser.Cashier:
                return redirect('cashier_home')
            elif user.user_type == CustomUser.PharmacyManager:
                return redirect('manager_home')
            elif user.user_type == CustomUser.PharmacyTechnician:
                return redirect('technician_home')
            elif user.user_type == CustomUser.Pharmacist:
                return redirect('pharmacist_home')
            else:
                return redirect('home_view')
        else:
            # Failed login attempt
            try:
                user = CustomUser.objects.get(email=email)  # Get the user object by email
                user.unsuccessful_login_count += 1  # Increment the count

                if user.unsuccessful_login_count >= 3:
                    user.is_active = False  # Lock the account after 3 failed attempts
                    messages.error(request, 'Your account has been locked due to multiple unsuccessful login attempts. Please contact an admin.')
                else:
                    messages.error(request, 'Invalid username or password. Please try again.')

                user.save()  # Save the updated user object
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid username or password.')

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login_view')

@login_required
def contact_view(request):
    return render(request, 'contact.html')

@login_required
def first_password_view(request):
    user = request.user
   
    print(f"password line #77: {str(user)}")
    if request.method == 'POST':
        form = FirstPasswordChangeForm(user, request.POST)
        print(f"password line #80: {str(user)}")

        if form.is_valid():  # checks to see if current password is correct, new password and confirming it is correct
            form.user.is_first_login = False
            print(f"password line #84: {str(user)}")
            form.save()  # hashes new password and saves it to the database
            print(f"password line #86: {str(user)}")
            update_session_auth_hash(request, user)  # keeps the user logged in after changing the password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home_view')  
        
    return render(request, 'users/first_login.html')

@pharmacy_manager_required
def User_registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'] 
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username= form.cleaned_data['username']
            
            # Check if user exists by email
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'User with this email id already exists. Please proceed to login!')
                return render(request, 'users/login.html')
            
            # Determine user type 
            user_type = form.cleaned_data['user_type']
            
            #check if it already exists
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'User with this username already exists. Please use a different username')
                return render(request, 'register.html')
            
            # Create new user with hashed password
            user = CustomUser(username=username, email=email, first_name=first_name, last_name=last_name, user_type=user_type)
            user.set_password(password)  # Hash password
            user.save()

           
            #log the user creation and redirect to register page
            messages.success(request, 'Registration successful.')
            return redirect('home_view')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def recover_account_view(request):
    if request.method == 'POST':
        # Check if the logged-in user is a Pharmacy Manager
        if request.user.user_type != '1':
            messages.error(request, 'You do not have permission to reset passwords.')
            return redirect('home_view')  # Redirect to a safe page

        email = request.POST.get('email')  # Get the email from the form

        if not email:  # Validate the inputs
            messages.error(request, 'The user d')
            return render(request, 'recover.html')  # Re-render the form

        try:
            # Retrieve the user using the email
            user = CustomUser.objects.get(email=email)

            # If user is found, reset the password
            #user.password = make_password(new_password)  # Hash the new password
            user.reset_token = None  # Clear the reset token
            user.reset_token_expiry = None  # Clear the expiry
            user.unsuccessful_login_count = 0  # Resets login count
            user.is_active = True  # Ensure the account is active
            user.save()
            messages.success(request, 'Your Account has been activated successfully!')
            return redirect('login_view')

        except CustomUser.DoesNotExist:
            # Handle the case where the user does not exist
            messages.error(request, 'No account found with that email address.')

    # Render the recovery form for GET requests
    return render(request, 'users/recover.html')


def create_user(request):
    if request.user.user_type != CustomUser.PharmacyManager:
        messages.error(request, 'You do not have permission to create new users.')
        return redirect('home_view')  # Redirect to a safe page

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Set the password
            user.save()
            messages.success(request, 'User created successfully. Please set your password.')
            return redirect('user_list')  # Redirect to a user list or another page
    else:
        form = UserRegistrationForm()
    return render(request, 'create_user.html', {'form': form})

@login_required
def manager_home(request):
    messages.success("whathhathathahthat")
    # list of low stock medications
    low_medications = Medications.objects.filter(tablet_count__lt= 120) # filter DB for tablet_count < 120
    
    
    #list of expiring and expiring soon medications
    current_date = datetime.today().date()  

    #if (current_date - expiration_date)

    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)

    context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications, 'low_medications': low_medications, } # passes dynamic data to template
    if request.method == 'POST': 
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                name = row.get('Name')
                exp_date_str = row.get('ExpDate')

                # Skip the 'Amount' field from the CSV; we hardcode it to 999
                if not name or not exp_date_str:
                    messages.error(request, f"Error: Missing required field(s) in row: {row}")
                    continue

                try:
                    amount = 999  # Force amount to always be 999
                    expiration_date = datetime.strptime(exp_date_str, '%m/%d/%Y').date()

                    # Calculate boolean fields
                    is_low = amount < 120
                    is_orderable = amount < 50
                    is_expired = current_date > expiration_date
                    is_expiring_soon = expiration_date <= current_date + timedelta(days=30)

                    # Create the Medications object with the hardcoded amount
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

            messages.success(request, "All medications successfully uploaded with tablet count set to 999.")
            return redirect('manager_home')

    return render(request, 'manager_home.html', context)

@login_required
def customer_home(request):
    return render(request, 'users/customer_home.html')

@login_required
def cashier_home(request):
    return render(request, 'users/cashier_home.html')

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('home_view')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form})

@login_required
def user_list(request):
    users = CustomUser.objects.all()

    return render(request, 'users/user-management.html', {'users': users})


def edit_user(request, user_id):
    edituser = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=edituser)
        if form.is_valid():
            form.save()
            return redirect('/users/user-management/')  
        else:
            print(form.errors)
    else:
        form = UserEditForm(instance=edituser)
    return render(request, 'users/edit_user.html', {'form': form, 'edituser': edituser})


def delete_user(request, user_id):
    deluser = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        deluser.delete()
        return redirect('/users/user-management/')  
    return render(request, 'users/delete_user.html', {'deluser': deluser})

def recover_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.reset_token = None  # Clear the reset token
        user.reset_token_expiry = None  # Clear the expiry
        user.unsuccessful_login_count = 0  # Resets login count
        user.is_active = True  # Ensure the account is active
        user.save()
        return redirect('/users/user-management/')  
    return render(request, 'users/recover_user.html', {'user': user})

def create_patient(request):
    if request.method == 'POST':
        form = PatientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_management')  
    else:
        form = PatientCreationForm()

    return render(request, 'users/create_patient.html', {'form': form})

# List of patients
def patient_management(request):
    patients = Patient.objects.all()
    return render(request, 'users/patient_management.html', {'patients': patients})

def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)  # Get the patient object by its primary key (pk)
    if request.method == 'POST':
        form = PatientCreationForm(request.POST, instance=patient)  # Bind the form to the existing patient
        if form.is_valid():
            form.save()
            return redirect('patient_management')  # Redirect to patient management after saving changes
    else:
        form = PatientCreationForm(instance=patient)  # Prepopulate the form with patient data

    return render(request, 'users/edit_patient.html', {'form': form, 'patient': patient})

def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)  # Get the patient object by its primary key (pk)
    if request.method == 'POST':
        patient.delete()  # Delete the patient from the database
        return redirect('patient_management')  # Redirect to patient management after deletion

    return render(request, 'users/delete_patient.html', {'patient': patient})

# # list of low stock (< 120) medications
# def low_medications_management(request):
#     low_medications = Medications.objects.filter(is_low= True) # filter DB for tablet_count < 120
#     context = {'low_medications': low_medications} # passes dynamic data to template  
#     return render(request, 'users/low_medications_management.html', {'low_medications': low_medications})

# # list of orderable (< 50) medications
# def orderable_medications_management(request):
#     orderable_medications = Medications.objects.filter(is_orderable= True) # filter DB for tablet_count < 50
#     context = {'orderable_medications': orderable_medications} # passes dynamic data to template  
#     return render(request, 'users/orderale_medications_management.html', {'orderable_medications': orderable_medications})

# # list of expired and expiring soon medications
# def expiring_medications_management(request):
#     expired_medications = Medications.objects.filter(is_expired=True)
#     expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)
#     context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications} # passes dynamic data to template  
#     return render(request, 'users/expiring_medications_management.html', {'expired_medications': expired_medications}, {'expiring_soon_medications': expiring_soon_medications})

@login_required
def changePassword_view(request):
    if request.user.is_authenticated:
        currentUser = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, currentUser)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('home_view')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = ChangePasswordForm(currentUser)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'users/password_change.html', {'form': form})
def myprofile_view(request):
    currentUser = request.user
    return render(request, 'users/my_profile.html', {'user': currentUser})

# views.py
@login_required
def pharmacist_home(request):
    medications = Medications.objects.all()

    if request.method == 'POST':
        medication_id = request.POST.get('medication_id')
        quantity = int(request.POST.get('quantity'))

        medication = get_object_or_404(Medications, id=medication_id)
        if medication.tablet_count >= quantity:
            medication.tablet_count -= quantity
            medication.save()
            messages.success(request, f'Successfully sold {quantity} tablets of {medication.name}.')
        else:
            messages.error(request, f'Not enough stock to sell {quantity} tablets of {medication.name}.')

    return render(request, 'users/pharmacist_home.html', {'medications': medications})


def payment_method(request, order_id):
    if request.method == 'POST':
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']

            if payment_method == 'Credit/Debit':
                return redirect('card_info', order_id=order_id)

            if payment_method == 'Cash':
                return redirect('cash', order_id=order_id)

    else:
        form = PaymentForm()

    return render(request, 'users/payment.html', {'form': form})

def card_info(request, order_id):
    total = request.session.get('total')

    if request.method == 'POST':
        form = CardInfoForm(request.POST)
        if form.is_valid():
            # Process the form data
            return redirect('payment_confirmation', order_id=order_id)
    else:
        form = CardInfoForm()

    return render(request, 'users/card.html', {'form': form, 'order_id': order_id})


@login_required
def cash(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form = CashForm(request.POST or None)
    total = order.get_total_price()
    change = None
    error = None

    if request.method == 'POST':
        if form.is_valid():
            amount_given = form.cleaned_data['cash_given']
            if amount_given >= total:
                change = amount_given - total
                order.status = 'paid'
                order.save()
                return redirect('payment_confirmation', order_id=order_id)
            else:
                error = 'Insufficient amount given.'

    return render(request, 'users/cash.html', {'form': form, 'total': total, 'change': change, 'error': error, 'order': order})
@login_required
def payment_confirmation_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'complete'
    order.save()
    return render(request, 'users/payment_confirmation.html', {'order_id': order_id})


def manual_prescription(request):
    if request.method == 'POST':
        form = ManualPrescriptionForm(request.POST)

        if form.is_valid():
            prescription = Prescription(patient= form.cleaned_data['patient'], medication= form.cleaned_data['medication'], num_tablets= form.cleaned_data['num_tablets'], prescriber_name= form.cleaned_data['prescriber_name'])
            prescription.save()
        
            return redirect('prescription_confirmation')
    
    else:
        form = ManualPrescriptionForm()
    
    return render(request, 'users/create_prescription.html', {'form': form})

def prescription_confirmation(request):
    return render(request, 'users/prescription_confirmation.html')

def sign_prescriptions(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = SignatureForm(request.POST)
        if form.is_valid():
            order.status = 'signed'  # Update the status to 'payment_ready'
            order.save()
            messages.success(request, "Prescription signed successfully!")
            return redirect('view_orders')  # Redirect to the view orders page
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignatureForm()

    return render(request, 'sign_prescriptions.html', {'form': form, 'order_id': order_id})

def signature_confirmation(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "Order ID not found in session.")
        return redirect('home_view')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'users/signature_confirmation.html', {'order_id': order_id})
@login_required
def medications_view(request):
    medications = Medications.objects.all()

    if request.method == 'POST':
        medication_id = request.POST.get('medication_id')
        quantity = int(request.POST.get('quantity'))

        medication = get_object_or_404(Medications, id=medication_id)
        if medication.tablet_count >= quantity:
            medication.tablet_count -= quantity
            medication.save()
            messages.success(request, f'Successfully sold {quantity} tablets of {medication.name}.')
        else:
            messages.error(request, f'Not enough stock to sell {quantity} tablets of {medication.name}.')
    return render(request, 'users/medications_view.html', {'medications': medications})



@login_required
def create_order(request):
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        for key, value in request.POST.items():
            if key.startswith('medication_'):
                medication_id = key.split('_')[1]
                medication = Medications.objects.get(id=medication_id)
                try:
                    quantity = int(value)
                except ValueError:
                    quantity = 0
                if quantity > 0:
                    if medication.tablet_count >= quantity:
                        OrderItem.objects.create(order=order, medication=medication, quantity=quantity, price=medication.price)
                        medication.tablet_count -= quantity
                        medication.save()
                    else:
                        messages.error(request, f'Not enough stock for {medication.name}. Available: {medication.tablet_count}')
                        order.delete()
                        return redirect('create_order')
        return redirect('view_orders')

    medications = Medications.objects.all()
    return render(request, 'users/create_order.html', {'medications': medications})
@login_required
def view_orders(request):
    if request.user.user_type in [CustomUser.Cashier, CustomUser.Pharmacist, CustomUser.PharmacyTechnician, CustomUser.PharmacyManager]:
        orders = Order.objects.all().prefetch_related('items__medication', 'items__generic_item')
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__medication', 'items__generic_item')
    return render(request, 'users/view_orders.html', {'orders': orders})


@login_required
def checkout_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        for item in order.items.all():
            price_field = f'price_{item.id}'
            if price_field in request.POST:
                try:
                    new_price = float(request.POST[price_field])
                    item.price = new_price
                    item.save()
                except ValueError:
                    messages.error(request, f'Invalid price for {item.medication.name if item.medication else item.generic_item.name}.')
                    return redirect('checkout_order', order_id=order_id)

        new_item_name = request.POST.get('new_item_name')
        new_item_quantity = request.POST.get('new_item_quantity')
        new_item_price = request.POST.get('new_item_price')

        if new_item_name and new_item_quantity and new_item_price:
            try:
                new_item_quantity = int(new_item_quantity)
                new_item_price = float(new_item_price)
                new_generic_item = GenericItem.objects.create(name=new_item_name, price=new_item_price)
                OrderItem.objects.create(order=order, generic_item=new_generic_item, quantity=new_item_quantity, price=new_item_price)
            except ValueError:
                messages.error(request, 'Invalid input for new item.')
                return redirect('checkout_order', order_id=order_id)

        if 'confirm' in request.POST:
            order.status = 'waiting for payment'
            order.save()
            messages.success(request, 'Order status updated to waiting for payment.')
            return redirect('view_orders')

        total_price = sum(item.quantity * item.price for item in order.items.all())
        return render(request, 'users/checkout.html', {'order': order, 'total_price': total_price})
    return redirect('view_orders')




@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        for item in order.items.all():
            price_field = f'price_{item.id}'
            if price_field in request.POST:
                try:
                    new_price = float(request.POST[price_field])
                    item.price = new_price
                    item.save()
                except ValueError:
                    messages.error(request, f'Invalid price for {item.medication.name if item.medication else item.generic_item.name}.')
                    return redirect('checkout', order_id=order_id)

        new_item_name = request.POST.get('new_item_name')
        new_item_quantity = request.POST.get('new_item_quantity')
        new_item_price = request.POST.get('new_item_price')


        if new_item_name and new_item_quantity and new_item_price:
            try:
                new_item_quantity = int(new_item_quantity)
                new_item_price = float(new_item_price)
                new_generic_item = GenericItem.objects.create(name=new_item_name, price=new_item_price)
                OrderItem.objects.create(order=order, generic_item=new_generic_item, quantity=new_item_quantity, price=new_item_price)
            except ValueError:
                messages.error(request, 'Invalid input for new item.')
                return redirect('checkout', order_id=order_id)

        if 'confirm' in request.POST:
            order.status = 'sign_ready'
            order.save()
            messages.success(request, 'Order status updated to sign ready.')
            return redirect('view_orders')

    total_price = sum(item.price * item.quantity for item in order.items.all())
    return render(request, 'users/checkout.html', {'order': order, 'total_price': total_price, 'order_number': order.id})
"""
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            expiration_date = form.cleaned_data['expiration_date']
            tablet_count = form.cleaned_data['tablet_count']
            price = form.cleaned_data['price']

            # Check if the medication already exists
            medication, created = Medications.objects.get_or_create(
                name=name,
                expiration_date=expiration_date,
                defaults={'price': price}
            )

            if created:
                # If the medication is new, set the tablet count
                medication.tablet_count = tablet_count
            else:
                # If the medication already exists, update the tablet count
                medication.tablet_count += tablet_count

            medication.save()
            messages.success(request, f'Medication {name} has been added/updated successfully.')
            return redirect('medications_view')
    else:
        form = MedicationForm()

    return render(request, 'users/add_medication.html', {'form': form})

"""


def unfilled_prescriptions(request):
    unfilled_prescriptions = Prescription.objects.filter(is_filled=False)

    context = {'unfilled_prescriptions': unfilled_prescriptions}
    return render(request, 'users/unfilled_prescriptions.html', context)


def fill_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    medication = prescription.medication

    current_date = datetime.now().date()
    if medication.expiration_date and medication.expiration_date < current_date:
        messages.error(request, "The medicine is expired.")
        return redirect('unfilled_prescriptions')

    if medication.tablet_count >= prescription.num_tablets:
        medication.tablet_count -= prescription.num_tablets
        prescription.is_filled = True
        prescription.status = NOT_PICKED_UP
        log_prescription_filled(instance_id=prescription.pk, user=request.user)
        medication.save()
        prescription.save()

        # Create an order for the filled prescription
        order = Order.objects.create(user=request.user)
        OrderItem.objects.create(order=order, medication=medication, quantity=prescription.num_tablets, price=medication.price)

        messages.success(request, "Prescription filled successfully and order created!")
    else:
        messages.error(
            request,
            f"Insufficient stock of {medication.name}. Available: {medication.tablet_count}, Required: {prescription.num_tablets}."
        )

    return redirect('unfilled_prescriptions')


@login_required
def receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total_price = sum(item.price * item.quantity for item in order.items.all())
    return render(request, 'users/receipt.html', {'order': order, 'total_price': total_price})

def filled_prescriptions(request):
    form = FilledPrescriptionsForm(request.GET)

    if form.is_valid():
        patient = form.cleaned_data['patient']
        if patient:
            patient_id = patient.id
            filled_presciptions = Prescription.objects.filter(patient_id=patient_id, is_filled=True)
        else:
            filled_presciptions = Prescription.objects.filter(is_filled=True)

    context = {
        'filled_prescriptions' : filled_presciptions,
        'form' : form
    }

    return render(request, 'users/filled_prescriptions.html', context)
    
    def inventory_reports(request):
        if request.method == 'POST':
            form = InventoryReportsForm(request.POST)

            if form.is_valid():
                timeframe = form.cleaned_data['timeframe']

                if timeframe == 'Last 7 days':
                    return redirect('card_info', order_id=order_id) # change

                if timeframe == 'Last 30 days':
                    return redirect('cash', order_id=order_id) # change
                
                if timeframe == 'Last 12 months':
                    return redirect() # change

        else:
            form = InventoryReportsForm()

    return render(request, 'users/inv_report_timeframe.html', {'form': form})


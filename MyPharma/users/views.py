from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .models import PharmacyManager,PharmacyTechnician,Pharmacist,Cashier,GeneralUser,CustomUser, Medications, Patient
from .forms import CustomUser, FirstPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from users.decorators import pharmacy_manager_required
from .forms import LoginForm, UserEditForm,PatientCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .forms import UserCreationForm, UserRegistrationForm
import csv
from .forms import CSVUploadForm
from io import TextIOWrapper
from datetime import datetime


@login_required
def home_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    if user.user_type == CustomUser.PharmacyManager:
        return redirect('/users/manager_home')
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

@login_required
def customer_home(request):
    return render(request, 'users/customer_home.html')

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

    return render(request, 'user_list.html', {'users': users})




def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/users/user-management/')  
        else:
            print(form.errors)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/edit_user.html', {'form': form, 'user': user})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('/users/user-management/')  
    return render(request, 'users/delete_user.html', {'user': user})

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


from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .models import PharmacyManager,PharmacyTechnician,Pharmacist,Cashier,GeneralUser,CustomUser
from .forms import CustomUser
from .models import PharmacyManager,PharmacyTechnician,Pharmacist,Cashier,GeneralUser, Medications
from .forms import CustomUser, FirstPasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .forms import UserCreationForm, UserRegistrationForm

import datetime

@login_required
def home_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    if user.user_type == CustomUser.PharmacyManager:
        return redirect('manager_home')
    else:
        return redirect('customer_home')

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
                return render(request, 'login.html', {'form': form})
            
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

    return render(request, 'login.html', {'form': form})



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
        
    return render(request, 'first_login.html')

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
    return render(request, 'register.html', {'form': form})

@login_required
def recover_account_view(request):
    if request.method == 'POST':
        # Check if the logged-in user is a Pharmacy Manager
        if request.user.user_type != '1':
            messages.error(request, 'You do not have permission to reset passwords.')
            return redirect('home_view')  # Redirect to a safe page

        email = request.POST.get('email')  # Get the email from the form

        if not email:  # Validate the inputs
            messages.error(request, 'Please fill out both fields.')
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
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('login_view')

        except CustomUser.DoesNotExist:
            # Handle the case where the user does not exist
            messages.error(request, 'No account found with that email address.')

    # Render the recovery form for GET requests
    return render(request, 'recover.html')


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

    return render(request, 'manager_home.html')

def manager_low_medications():
    # list of low stock medications
    low_medications = Medications.objects.filter(tablet_count__lt= 120) # filter DB for tablet_count < 120
    context = {'low_medications': low_medications} # passes dynamic data to template  

def manager_expiring_medications():
    #list of expired and expiring soon medications
    expired_medications = Medications.objects.filter(is_expired=True)
    expiring_soon_medications = Medications.objects.filter(is_expiring_soon=True)
    context = {'expired_medications': expired_medications, 'expiring_soon_medications': expiring_soon_medications} # passes dynamic data to template  

@login_required
def customer_home(request):
    return render(request, 'customer_home.html')

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


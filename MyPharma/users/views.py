from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .models import PharmacyManager,PharmacyTechnician,Pharmacist,Cashier,GeneralUser
from .forms import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

@login_required
def home_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, 'home.html', {'user_type': user.user_type})

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

def logout_view(request):
    logout(request)
    return render(request, 'login.html')

def contact_view(request):
    return render(request, 'contact.html')

def first_password_view(request):
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():  # checks to see if current password is correct, new password and confirming it is correct
            user = form.save()  # hashes new password and saves it to the database
            user.is_first_login = 0
            update_session_auth_hash(request, user)  # keeps the user logged in after changing the password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home_view')  
        
    return render(request, '.html') # FIX html part


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

            # Create role-specific profiles
            if user_type == CustomUser.PharmacyManager:
                PharmacyManager.objects.create(admin=user)

            elif user_type == CustomUser.PharmacyTechnician:
                PharmacyTechnician.objects.create(admin=user)

            elif user_type == CustomUser.Pharmicist:
                Pharmacist.objects.create(admin=user)

            elif user_type == CustomUser.Cashier:
                Cashier.objects.create(admin=user)

            else:
                GeneralUser.objects.create(admin=user)

            #log the user creation and redirect to register page
            messages.success(request, 'Registration successful.')
            return redirect('home_view')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

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


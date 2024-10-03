from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .models import PharmacyStaff,PharmacyManager,GeneralUser
from .forms import CustomUser
from .forms import LoginForm

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
      
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home_view')  
        else:
            #print(f"Failed login attempt: Username: {email}, Password: {password}")
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return render(request, 'login.html')

def contact_view(request):
    return render(request, 'contact.html')

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
            elif user_type == CustomUser.GeneralUser:
                PharmacyStaff.objects.create(admin=user)
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
 


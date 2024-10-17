import sys

sys.path.append('..')

from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password


from users.forms import CustomUser
from users.models import PharmacyManager,PharmacyTechnician,Pharmacist,Cashier,GeneralUser
from users.forms import CustomUser, FirstPasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def manager_home(request):
    return render(request, 'manager_home.html')
    
@login_required
def order_page(request):
    return render(request, 'order_page.html')


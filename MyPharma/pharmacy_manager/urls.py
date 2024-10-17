from django.urls import path
from .views import *

urlpatterns = [
    path('manager_home/', manager_home, name='manager_home'),
    path('low_stock/', manager_low_medications, name='low_stock')
]
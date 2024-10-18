from django.urls import path
from .views import *

urlpatterns = [
    path('manager_home/', manager_home, name='manager_home'),
    path('low_medications_management/', low_medications_management, name='low_medications_management'),
    path('expiring_medications_management/', expiring_medications_management, name='expiring_medications_management'),
    path('all_medications_view/', all_medications_view, name='all_medications_view')
]
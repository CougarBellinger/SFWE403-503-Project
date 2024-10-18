from django.urls import path
from .views import *

urlpatterns = [
    path('manager_home/', manager_home, name='manager_home'),
    path('low_medications_management/', low_medications_management, name='low_medications_management'),
    path('orderable_medications_management/', orderable_medications_management, name='orderable_medications_management'),
    path('expiring_medications_management/', expiring_medications_management, name='expiring_medications_management'),
    path('remove_medications/<int:pk>/', remove_medications, name='remove_medications')
    
]
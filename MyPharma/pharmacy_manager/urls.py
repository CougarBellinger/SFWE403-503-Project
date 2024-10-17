from django.urls import path
from .views import *

urlpatterns = [
    path('manager_home/', manager_home, name='manager_home'),
    path('order_page/', order_page, name='order_page')
]
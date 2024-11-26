from django.urls import path
from .views import *

urlpatterns = [
    path('manager_home/', manager_home, name='manager_home'),
    path('low_medications_management/', low_medications_management, name='low_medications_management'),
    path('expiring_medications_management/', expiring_medications_management, name='expiring_medications_management'),
    path('all_medications_view/', all_medications_view, name='all_medications_view'),
    path('activity_log/', activity_log, name='activity_log'),
    path('remove_medications/<int:pk>/', remove_medications, name='remove_medications'),
    path('sell_medication/', sell_medication_view, name='sell_medication'),
    path('add_medication/', add_medication_view, name='add_medication'),
    path('order_medications/<int:pk>/', order_medications, name='order_medications'),
    path('activity_details/<int:pk>/', activity_details, name='activity_details'),
    path('sign_prescriptions/', sign_prescriptions, name='sign_prescriptions'),
    path('financial_stats_reports/', financial_stats_reports, name='financial_stats_reports')
]
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
    path('financial_reports_timeframe/', financial_reports, name='financial_reports'),
    path('financial_reports_week/', financial_reports_week, name='financial_reports_week'),
    path('financial_reports_month/', financial_reports_month, name='financial_reports_month'),
    path('financial_reports_year/', financial_reports_year, name='financial_reports_year'),

    path('sign_prescriptions/', sign_prescriptions, name='sign_prescriptions'),
    path('inventory_reports_timeframe/', inventory_reports, name='inventory_reports'),
    path('inventory_reports_week/', inventory_reports_week, name='inventory_reports_week'),
    path('inventory_reports_month/', inventory_reports_month, name='inventory_reports_month'),
    path('inventory_reports_year/', inventory_reports_year, name='inventory_reports_year')
]
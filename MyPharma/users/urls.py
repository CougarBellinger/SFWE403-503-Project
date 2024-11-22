from django.urls import path
from .views import User_registration_view,view_orders, receipt_view, checkout, checkout_order, create_order, medications_view, pharmacist_home, home_view, cashier_home, login_view,logout_view, contact_view, recover_account_view, create_user, manager_home, customer_home, password_change,user_list, first_password_view, create_patient,delete_user,edit_user,recover_user,patient_management,edit_patient,delete_patient,changePassword_view,myprofile_view, payment_method, card_info, cash, payment_confirmation_page, manual_prescription, prescription_confirmation, sign_prescriptions, pharmacist_home, fill_prescription, unfilled_prescriptions, signature_confirmation



urlpatterns = [
    path('', home_view, name='home_view'),
    path('home/', home_view, name='home_view'),
    path('register/', User_registration_view, name='user_registration_view'), 
    path('login/', login_view, name='login_view'), 
    path('logout/', logout_view, name='logout_view'),
    path('recover/', recover_account_view, name='recover_account_view'), 
    path('login/', login_view, name='login_view'),
    path('customer_home/', customer_home, name='customer_home'),
    path('manager_home/', manager_home, name='manager_home'),
    path('cashier_home/', cashier_home, name='cashier_home'),
    path('contact/', contact_view, name='contact_view'),
    path('create_user/', create_user, name='create_user'),
    path('customer_home/', customer_home, name='customer_home'),
    path('password_change/', password_change, name='password_change'),
    path('user_list/', user_list, name='user_list'),
    path('contact/', contact_view, name='contact_view'), 
    path('updatepassword/', first_password_view, name='first_password_view'),
    path('user-management/', user_list, name='user_management'),
    path('<int:user_id>/recover/', recover_user, name='recover_user'),
    path('<int:user_id>/edit/', edit_user, name='edit_user'),
    path('<int:user_id>/delete/', delete_user, name='delete_user'),
    path('create_patient/', create_patient, name='create_patient'),
    path('patient_management/', patient_management, name='patient_management'),
    path('edit/<int:pk>/', edit_patient, name='edit_patient'),
    path('delete/<int:pk>/', delete_patient, name='delete_patient'),
    path('changePassword/', changePassword_view, name='changePassword_view'),
    path('myprofile/', myprofile_view, name='myprofile_view'),

    path('pharmacist_home/', pharmacist_home, name='pharmacist_home'),
    path('medications/', medications_view, name='medications_view'),
    path('create_order/', create_order, name='create_order'),
    path('view_orders/', view_orders, name='view_orders'),
    path('checkout_order/<int:order_id>/', checkout_order, name='checkout_order'),
    path('checkout/<int:order_id>/', checkout, name='checkout'),

    path('payment_method/<int:order_id>', payment_method, name='payment_method'),
    path('card/<int:order_id>/', card_info, name='card_info'),
    path('cash/<int:order_id>/', cash, name='cash'),

    path('payment_confirmation/<int:order_id>/', payment_confirmation_page, name='payment_confirmation'),

    path('manual_prescription/', manual_prescription, name='manual_prescription'),
    path('prescription_confirmation/', prescription_confirmation, name='prescription_confirmation'),
    path('/users/sign_prescriptions/<int:order_id>/', sign_prescriptions, name='sign_prescriptions'),
    path('signature_confirmation/<int:order_id>/', signature_confirmation, name='signature_confirmation'),
    path('pharmacist_home/', pharmacist_home, name='pharmacist_home'),
    path('unfilled-prescriptions/', unfilled_prescriptions, name='unfilled_prescriptions'),
    path('fill-prescription/<int:pk>/', fill_prescription, name='fill_prescription'),
    path('receipt/<int:order_id>/', receipt_view, name='receipt_view'),

]

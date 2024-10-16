from django.urls import path
from .views import User_registration_view, home_view, login_view,logout_view, contact_view, recover_account_view, create_user, manager_home, customer_home, password_change,user_list, first_password_view, create_patient,delete_user,edit_user,recover_user,patient_management,edit_patient,delete_patient


urlpatterns = [
    path('', home_view, name='home_view'),
    path('home/', home_view, name='home_view'),
    path('register/', User_registration_view, name='user_registration_view'), 
    path('login/', login_view, name='login_view'), 
    path('logout/', logout_view, name='logout_view'),
    path('recover/', recover_account_view, name='recover_account_view'), 
    path('login/', login_view, name='login_view'), 
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
]

from django.urls import path
from .views import User_registration_view, home_view, login_view,logout_view, contact_view, recover_account_view, create_user, manager_home, customer_home, password_change,user_list, first_password_view


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
    path('updatepassword/', first_password_view, name='first_password_view')
]

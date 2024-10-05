from django.urls import path
from .views import User_registration_view, home_view, login_view, contact_view, recover_account_view

urlpatterns = [
    path('', home_view, name='home_view'),
    path('home/', home_view, name='home_view'),
    path('register/', User_registration_view, name='user_registration_view'), 
    path('login/', login_view, name='login_view'), 
    path('logout/', login_view, name='logout_view'),
    path('recover/', recover_account_view, name='recover_account_view'), 
    path('login/', login_view, name='login_view'), 
    path('contact/', contact_view, name='contact_view'), 

]

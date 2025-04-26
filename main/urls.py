from django.urls import path
from main.views import login_register, register

app_name = 'main'

urlpatterns = [
    path('', login_register, name='login_register'),
    path('register/', register, name='register'), 
]
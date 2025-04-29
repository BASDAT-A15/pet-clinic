from django.urls import path
from main.views import login_register, register, login, profile_klien, profile_frontdesk, profile_dokter, profile_perawat, update_password, logout_view

app_name = 'main'

urlpatterns = [
    path('', login_register, name='login_register'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile-klien/', profile_klien, name='profile_klien'),
    path('profile-frontdesk/', profile_frontdesk, name='profile_frontdesk'),
    path('profile-dokter/', profile_dokter, name='profile_dokter'),
    path('profile-perawat/', profile_perawat, name='profile_perawat'),
    path('update-password/', update_password, name='update_password'),
    path('logout/', logout_view, name='logout'),
]
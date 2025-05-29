from django.urls import path
from main.views import login_register, register, login, profile_klien, profile_frontdesk, profile_dokter, profile_perawat, update_password, logout_view, update_profile, debug_session

app_name = 'main'

urlpatterns = [
    path('', login_register, name='login_register'),
    path('register/', register, name='register'),
    path('register/<str:role>/', register, name='register_with_role'),
    path('login/', login, name='login'),
    path('profile-klien/', profile_klien, name='profile_klien'),
    path('profile-front-desk/', profile_frontdesk, name='profile_front_desk'),
    path('profile-dokter/', profile_dokter, name='profile_dokter_hewan'),
    path('profile-perawat/', profile_perawat, name='profile_perawat_hewan'),
    path('update-password/', update_password, name='update_password'),
    path('logout/', logout_view, name='logout'),
    path('update-profile/', update_profile, name='update_profile'),
    path('debug-session/', debug_session, name='debug_session'),  # Temporary debug route
]
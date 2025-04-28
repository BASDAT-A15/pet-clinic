from django.shortcuts import render, redirect

def login_register(request):
    return render(request, 'login_register.html')

def register(request):
    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')

def profile_klien(request):
    return render(request, 'profile_klien.html')

def profile_frontdesk(request):
    return render(request, 'profile_frontdesk.html')

def profile_dokter(request):
    return render(request, 'profile_dokter.html')

def profile_perawat(request):
    return render(request, 'profile_perawat.html')

def update_password(request):
    return render(request, 'update_password.html')
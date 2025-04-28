from django.shortcuts import render, redirect

def login_register(request):
    return render(request, 'login_register.html')

def register(request):
    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')
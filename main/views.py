from django.shortcuts import render, redirect
from .models import Klien

def login_register(request):
    return render(request, 'login_register.html')

def register(request):
    return render(request, 'register.html')
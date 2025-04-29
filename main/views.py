from django.shortcuts import render, redirect
from .forms import (
    IndividuRegistrationForm, 
    PerusahaanRegistrationForm, 
    FrontDeskOfficerForm,
    DokterHewanForm,
    PerawatHewanForm
)

def login_register(request):
    return render(request, 'login_register.html')

def register(request):
    role = request.GET.get('role', None)
    form = None

    if not role:
        return render(request, 'register.html')  # Return role selection page if no role is chosen

    if role == 'individu':
        form = IndividuRegistrationForm()
        form_title = "Klien - Individu"
    elif role == 'perusahaan':
        form = PerusahaanRegistrationForm()
        form_title = "Klien - Perusahaan"
    elif role == 'front_desk_officer':
        form = FrontDeskOfficerForm()
        form_title = "Front-Desk Officer"
    elif role == 'dokter_hewan':
        form = DokterHewanForm()
        form_title = "Dokter Hewan"
    elif role == 'perawat_hewan':
        form = PerawatHewanForm()
        form_title = "Perawat Hewan"
    else:
        return render(request, 'error.html', {'message': 'Role tidak valid'})

    return render(request, 'register_form.html', {
        'form': form,
        'form_title': form_title,
    })

def login(request):
    return render(request, 'login.html')
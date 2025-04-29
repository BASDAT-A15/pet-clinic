from django import forms

class IndividuRegistrationForm(forms.Form):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(max_length=100, label='Nama Depan')
    middle_name = forms.CharField(max_length=100, label='Nama Tengah', required=False)
    last_name = forms.CharField(max_length=100, label='Nama Belakang')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    phone_number = forms.CharField(max_length=15, label='Nomor Telepon')
    address = forms.CharField(widget=forms.Textarea, label='Alamat')

class PerusahaanRegistrationForm(forms.Form):
    email = forms.EmailField(label='Email')
    company_name = forms.CharField(max_length=200, label='Nama Perusahaan')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    phone_number = forms.CharField(max_length=15, label='Nomor Telepon')
    address = forms.CharField(widget=forms.Textarea, label='Alamat')

class FrontDeskOfficerForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    phone_number = forms.CharField(max_length=15, label='Nomor Telepon')
    date_received = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Tanggal Diterima')
    address = forms.CharField(widget=forms.Textarea, label='Alamat')

class DokterHewanForm(forms.Form):
    practice_license_number = forms.CharField(max_length=100, label='Nomor Izin Praktik')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    phone_number = forms.CharField(max_length=15, label='Nomor Telepon')
    date_received = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Tanggal Diterima')
    address = forms.CharField(widget=forms.Textarea, label='Alamat')
    competency = forms.CharField(max_length=100, label='Kompetensi', required=False)
    certificate_number = forms.CharField(max_length=100, label='Nomor Sertifikat', required=False)
    certificate_name = forms.CharField(max_length=200, label='Nama Sertifikat', required=False)
    practice_schedule = forms.CharField(max_length=100, label='Jadwal Praktik', required=False)

class PerawatHewanForm(forms.Form):
    practice_license_number = forms.CharField(max_length=100, label='Nomor Izin Praktik')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    phone_number = forms.CharField(max_length=15, label='Nomor Telepon')
    date_received = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Tanggal Diterima')
    address = forms.CharField(widget=forms.Textarea, label='Alamat')
    competency = forms.CharField(max_length=100, label='Kompetensi', required=False)
    certificate_number = forms.CharField(max_length=100, label='Nomor Sertifikat', required=False)
    certificate_name = forms.CharField(max_length=200, label='Nama Sertifikat', required=False)
    practice_schedule = forms.CharField(max_length=100, label='Jadwal Praktik', required=False)

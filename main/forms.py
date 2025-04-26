from django import forms
from .models import User, Individu, Perusahaan

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password', 'alamat', 'nomor_telepon']
        widgets = {
            'password': forms.PasswordInput(),
        }

class IndividuForm(forms.ModelForm):
    class Meta:
        model = Individu
        fields = ['nama_depan', 'nama_tengah', 'nama_belakang']

class PerusahaanForm(forms.ModelForm):
    class Meta:
        model = Perusahaan
        fields = ['nama_perusahaan']

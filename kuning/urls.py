from django.urls import path
from kuning import views

app_name = 'kuning'

urlpatterns = [
    path('jenis-hewan', views.list_jenis_hewan, name='list_jenis_hewan'), 
]
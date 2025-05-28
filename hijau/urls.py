from django.urls import path
from . import views

app_name = 'hijau'

urlpatterns = [
    path('list_perawatan/', views.list_perawatan, name='list_perawatan'),
    path('create_perawatan/', views.create_perawatan, name='create_perawatan'),
    path('update_perawatan/<str:id_kunjungan>/', views.update_perawatan, name='update_perawatan'),
    path('delete_perawatan/', views.delete_perawatan, name='delete_perawatan'),
    path('list_kunjungan/', views.list_kunjungan, name='list_kunjungan'),
    path('create_kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update_kunjungan/', views.update_kunjungan, name='update_kunjungan'),
    path('delete_kunjungan/', views.delete_kunjungan, name='delete_kunjungan'),
    path('create_rekam_medis/', views.create_rekam_medis, name='create_rekam_medis'),
    path('list_rekam_medis/', views.list_medis, name='list_rekam_medis'),
    path('update_rekam_medis/', views.update_rekam_medis, name='update_rekam_medis'),
]
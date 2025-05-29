from django.urls import path
from . import views

app_name = 'hijau'

urlpatterns = [
    # Original URLs
    path('list_perawatan/', views.list_perawatan, name='list_perawatan'),
    path('create_perawatan/', views.create_perawatan, name='create_perawatan'),
    path('api/kunjungan/<str:kunjungan_id>/', views.get_kunjungan_details, name='get_kunjungan_details'),
      # AJAX Endpoints - ADD THESE
    path('api/treatment/<str:id_kunjungan>/', views.get_treatment_details, name='get_treatment_details'),
    path('api/update-treatment/', views.update_treatment_ajax, name='update_treatment_ajax'),
    path('api/delete-treatment/', views.delete_treatment_ajax, name='delete_treatment_ajax'),
    path('api/visit-medical-info/<str:visit_id>/', views.get_visit_medical_info, name='get_visit_medical_info'),
      # Other URLs
    path('list_kunjungan/', views.list_kunjungan, name='list_kunjungan'),
    path('create_kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update_kunjungan/', views.update_kunjungan, name='update_kunjungan'),
    path('delete_kunjungan/', views.delete_kunjungan, name='delete_kunjungan'),
    path('create_rekam_medis/', views.create_rekam_medis, name='create_rekam_medis'),
    path('list_rekam_medis/', views.list_medis, name='list_rekam_medis'),
    path('update_rekam_medis/', views.update_rekam_medis, name='update_rekam_medis'),
    path('view_rekam_medis/', views.view_rekam_medis, name='view_rekam_medis'),
]
from django.urls import path, re_path
from merah import views

app_name = 'merah'

urlpatterns = [
    path('', views.list_vaksinasi, name='list_vaksinasi'), 
    path('add-vaksin/', views.add_vaksinasi, name='add_vaksinasi'), 
    path('update-vaksin/<str:id_kunjungan>/', views.update_vaksinasi, name='update_vaksinasi'), 
    path('vaksinasi/delete/<str:id_kunjungan>/', views.delete_vaksinasi, name='delete_vaksinasi'),
]

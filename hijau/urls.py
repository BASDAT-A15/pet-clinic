from django.urls import path
from . import views

urlpatterns = [
    path('list_perawatan/', views.list_perawatan, name='list_perawatan'),
    path('create_perawatan/', views.create_perawatan, name='create_perawatan'),
    path('update_perawatan/', views.update_perawatan, name='update_perawatan'),
    path('delete_perawatan/', views.delete_perawatan, name='delete_perawatan'),  # URL untuk konfirmasi delete

]

from django.shortcuts import render

jenis_hewan = [
    {'no': 1, 'id_jenis': 'HWN001', 'nama_jenis': 'Kucing'},
    {'no': 2, 'id_jenis': 'HWN002', 'nama_jenis': 'Anjing'},
    {'no': 3, 'id_jenis': 'HWN003', 'nama_jenis': 'Hamster'},
]
    

def list_jenis_hewan(request):
    return render(request, 'jenis-hewan/list.html', {'jenis_hewan': jenis_hewan})
from django.shortcuts import render

jenis_hewan = [
    {'no': 1, 'id_jenis': 'HWN001', 'nama_jenis': 'Kucing'},
    {'no': 2, 'id_jenis': 'HWN002', 'nama_jenis': 'Anjing'},
    {'no': 3, 'id_jenis': 'HWN003', 'nama_jenis': 'Hamster'},
]
    
daftar_hewan = [
    {
            'id': 1,
            'pemilik': 'John Doe',
            'jenis_hewan': 'Kucing',
            'nama': 'Snowy',
            'tanggal_lahir': '9 Februari 2020',
            'foto': '/static/images/cat1.jpg',
            'url_foto': 'https://kucingsaya.com'

    },
    {
            'id': 2,
            'pemilik': 'PT Aku Sayang Hewan',
            'jenis_hewan': 'Anjing',
            'nama': 'Blacky',
            'tanggal_lahir': '15 November 2019',
            'foto': '/static/images/dog1.jpg',
            'url_foto': 'https://anjingsaya.com'

    },
    {
            'id': 3,
            'pemilik': 'PT Pecinta Kucing',
            'jenis_hewan': 'Hamster',
            'nama': 'Hamseung',
            'tanggal_lahir': '15 Oktober 2024',
            'foto': '/static/images/hamster1.jpg',
            'url_foto': 'https://hamstersaya.com'
    }
]

def list_jenis_hewan(request):
    return render(request, 'jenis-hewan/list.html', {'jenis_hewan': jenis_hewan})

def list_hewan(request):
    for hewan in daftar_hewan:
        parts = hewan['tanggal_lahir'].split(' ')
        day = parts[0].zfill(2)  
        
        month_map = {
            'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04',
            'Mei': '05', 'Juni': '06', 'Juli': '07', 'Agustus': '08',
            'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'
        }
        
        month = month_map.get(parts[1], '01') 
        year = parts[2] 
        
        hewan['tanggal_lahir_formatted'] = f"{day}-{month}-{year}"
    return render(request, 'daftar-hewan/list_hewan.html', {'daftar_hewan': daftar_hewan})

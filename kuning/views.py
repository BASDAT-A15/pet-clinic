from django.shortcuts import render

jenis_hewan = [
    {'no': 1, 'id_jenis': '607ecc9e-7feb-4f6a-8ba9-6ef6bb99ff9f', 'nama_jenis': 'Kucing'},
    {'no': 2, 'id_jenis': 'e8b6b2f5-b992-427b-8600-9910d1ee221b', 'nama_jenis': 'Anjing'},
    {'no': 3, 'id_jenis': '17ca2368-540c-4f80-a336-321c6c987a9f', 'nama_jenis': 'Hamster'},
]
    
daftar_hewan = [
    {
            'id': 'a31be95d-cf2d-4df1-9463-9742a524e07d',
            'pemilik': 'John Doe',
            'jenis_hewan': 'Kucing',
            'nama': 'Snowy',
            'tanggal_lahir': '9 Februari 2020',
            'foto': '/static/images/cat1.jpg',
            'url_foto': 'https://kucingsaya.com'

    },
    {
            'id': 'd92abd5f-ae01-4b2b-9b21-d1ee6e040c26',
            'pemilik': 'PT Aku Sayang Hewan',
            'jenis_hewan': 'Anjing',
            'nama': 'Blacky',
            'tanggal_lahir': '15 November 2019',
            'foto': '/static/images/dog1.jpg',
            'url_foto': 'https://anjingsaya.com'

    },
    {
            'id': 'd7458f28-d431-4289-8f29-d024988d051a',
            'pemilik': 'PT Pecinta Kucing',
            'jenis_hewan': 'Hamster',
            'nama': 'Hamseung',
            'tanggal_lahir': '15 Oktober 2024',
            'foto': '/static/images/hamster1.jpg',
            'url_foto': 'https://hamstersaya.com'
    }
]

def list_jenis_hewan(request):
    role = "frontdesk"  # opsi role dokter atau frontdesk
    
    return render(request, 'jenis-hewan/list.html', {
        'jenis_hewan': jenis_hewan,
        'role': role
    })

def list_hewan(request):
    role = 'frontdesk' # opsi role klien atau frontdesk
    if role == 'klien':
        filtered_hewan = [daftar_hewan[0]]
    else:
        filtered_hewan = daftar_hewan

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
    return render(request, 'daftar-hewan/list_hewan.html', {
        'daftar_hewan': filtered_hewan,
        'role' : role
    })

from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

# Data Dummy
DUMMY_VACCINATIONS = [
    {
        'id_kunjungan': 'KJN001',
        'tanggal': 'Rabu, 5 Februari 2025',
        'kode_vaksin': 'VAC001',
        'nama_vaksin': 'Feline Panleukopenia',
        'stok': 100
    },
    {
        'id_kunjungan': 'KJN002',
        'tanggal': 'Jumat, 21 Februari 2025',
        'kode_vaksin': 'VAC002',
        'nama_vaksin': 'Canine Parvovirus',
        'stok': 200
    },
    {
        'id_kunjungan': 'KJN003',
        'tanggal': 'Selasa, 15 Maret 2025',
        'kode_vaksin': 'VAC003',
        'nama_vaksin': 'Canine Adenovirus',
        'stok': 300
    }
]

DUMMY_VACCINES = [
    {'kode_vaksin': 'VAC001', 'nama_vaksin': 'Feline Panleukopenia', 'harga': 100000, 'stok': 100, 'used': False},
    {'kode_vaksin': 'VAC002', 'nama_vaksin': 'Canine Parvovirus', 'harga': 150000, 'stok': 200, 'used': False},
    {'kode_vaksin': 'VAC003', 'nama_vaksin': 'Canine Adenovirus', 'harga': 180000, 'stok': 300, 'used': True}
]

DUMMY_CLIENTS = [
    {
        'id': 1,
        'email': 'client1@example.com',
        'nama': 'Client 1',
        'jenis': 'Individu',
        'nomor_identitas': '5f4dcc3b5aa765d61d8327deb882cf99',
        'nama_lengkap': 'Rizki Maulana',
        'nama_perusahaan': '',
        'alamat': 'Jl. Melati Indah No. 23, Kel. Sukamaju, Kec. Cibinong, Kab. Bogor, Jawa Barat, 16914',
        'telepon': '081234567890',
        'tanggal_registrasi': '2023-01-15',
        'pets': [
            {'id': 1, 'nama': 'Luna', 'jenis': 'Kucing', 'tanggal_lahir': '2022-05-14'},
            {'id': 2, 'nama': 'Max', 'jenis': 'Anjing', 'tanggal_lahir': '2021-11-03'},
            {'id': 3, 'nama': 'Coco', 'jenis': 'Kelinci', 'tanggal_lahir': '2023-01-27'}
        ]
    },
    {
        'id': 2,
        'email': 'client2@example.com',
        'nama': 'Client 2',
        'jenis': 'Perusahaan',
        'nomor_identitas': 'e10adc3949ba59abbe56e057f20f883e',
        'nama_lengkap': '',
        'nama_perusahaan': 'PT Hewan Perkasa',
        'alamat': 'Jl. Anggrek No. 45, Kel. Sukamaju, Kec. Cibinong, Kab. Bogor, Jawa Barat, 16914',
        'telepon': '089876543210',
        'tanggal_registrasi': '2023-02-20',
        'pets': [
            {'id': 4, 'nama': 'Bella', 'jenis': 'Kucing', 'tanggal_lahir': '2021-08-10'},
            {'id': 5, 'nama': 'Charlie', 'jenis': 'Anjing', 'tanggal_lahir': '2020-12-25'}
        ]
    },
    {
        'id': 3,
        'email': 'client3@example.com',
        'nama': 'Client 3',
        'jenis': 'Individu',
        'nomor_identitas': '52b4bc65d8a4eac1b977305205e9330e',
        'nama_lengkap': 'Siti Nurhaliza',
        'nama_perusahaan': '',
        'alamat': 'Jl. Mawar No. 12, Kel. Sukamaju, Kec. Cibinong, Kab. Bogor, Jawa Barat, 16914',
        'telepon': '087654321098',
        'tanggal_registrasi': '2023-03-10',
        'pets': [
            {'id': 6, 'nama': 'Milo', 'jenis': 'Anjing', 'tanggal_lahir': '2022-07-30'}
        ]
    }
]

def list_vaksinasi(request):
    return render(request, 'klinik/list_vaksinasi.html', {
        'vaksinasi_list': DUMMY_VACCINATIONS
    })

def add_vaksinasi(request):
    return render(request, 'klinik/add_vaksinasi.html', {
        'kunjungan_options': DUMMY_VACCINATIONS,
        'vaksin_options': DUMMY_VACCINES
    })

def update_vaksinasi(request, id_kunjungan):
    selected_vaccination = next(
        (v for v in DUMMY_VACCINATIONS if v['id_kunjungan'] == id_kunjungan), 
        None
    )
    return render(request, 'klinik/update_vaksinasi.html', {
        'kunjungan': selected_vaccination,
        'vaksin_options': DUMMY_VACCINES
    })
    
def delete_vaksinasi(request, id_kunjungan):
    if request.method == 'POST':
        # Cari vaksinasi yang akan dihapus
        global DUMMY_VACCINATIONS
        vaksinasi_dihapus = None
        
        # Cari data yang akan dihapus
        for vaksinasi in DUMMY_VACCINATIONS:
            if vaksinasi['id_kunjungan'] == id_kunjungan:
                vaksinasi_dihapus = vaksinasi
                break
        
        if vaksinasi_dihapus:
            DUMMY_VACCINATIONS = [v for v in DUMMY_VACCINATIONS if v['id_kunjungan'] != id_kunjungan]
            
            for vaksin in DUMMY_VACCINES:
                if vaksin['kode'] == vaksinasi_dihapus['kode_vaksin']:
                    vaksin['stok'] += 1  
                    break
            
            messages.success(request, f'Vaksinasi {id_kunjungan} berhasil dihapus!')
        else:
            messages.error(request, f'Vaksinasi {id_kunjungan} tidak ditemukan!')
        
        return redirect('merah:list_vaksinasi')
    
    return redirect('merah:list_vaksinasi')

def list_vaksin(request):
    for vaksin in DUMMY_VACCINES:
        vaksin['can_delete'] = not vaksin['used']
    return render(request, 'klinik/list_vaksin.html', {
        'vaksin_list': DUMMY_VACCINES
    })

def add_vaksin(request):
    if request.method == 'POST':
        new_vaksin = {
            'kode_vaksin': f"VAC{len(DUMMY_VACCINES)+1:03d}",
            'nama_vaksin': request.POST.get('nama_vaksin'),
            'harga': int(request.POST.get('harga')),
            'stok': int(request.POST.get('stok')),
            'used': False
        }
        DUMMY_VACCINES.append(new_vaksin)
        return redirect('merah:list_vaksin')
    return render(request, 'klinik/add_vaksin.html')

def update_vaksin(request, kode_vaksin):
    vaksin = next((v for v in DUMMY_VACCINES if v['kode_vaksin'] == kode_vaksin), None)
    
    if request.method == 'POST':
        if vaksin:
            vaksin['nama_vaksin'] = request.POST.get('nama_vaksin')
            vaksin['harga'] = int(request.POST.get('harga'))
        return redirect('merah:list_vaksin')
    
    return render(request, 'klinik/update_vaksin.html', {'vaksin': vaksin})

def update_stok_vaksin(request, kode_vaksin):
    vaksin = next((v for v in DUMMY_VACCINES if v['kode_vaksin'] == kode_vaksin), None)
    
    if request.method == 'POST':
        if vaksin:
            vaksin['stok'] = int(request.POST.get('stok'))
        return redirect('merah:list_vaksin')
    
    return render(request, 'klinik/update_stock.html', {'vaksin': vaksin})

def delete_vaksin(request, kode_vaksin):
    if request.method == 'POST':  
        global DUMMY_VACCINES
        vaksin = next((v for v in DUMMY_VACCINES if v['kode_vaksin'] == kode_vaksin), None)
        
        if vaksin and not vaksin['used']:
            DUMMY_VACCINES = [v for v in DUMMY_VACCINES if v['kode_vaksin'] != kode_vaksin]
            messages.success(request, f'Vaksin {kode_vaksin} berhasil dihapus!')
        else:
            messages.error(request, f'Vaksin {kode_vaksin} tidak dapat dihapus!')
    
    return redirect('merah:list_vaksin')

def list_klien(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        filtered_clients = [
            client for client in DUMMY_CLIENTS 
            if search_query.lower() in client['nama'].lower() or 
               search_query.lower() in client['email'].lower()
        ]
    else:
        filtered_clients = DUMMY_CLIENTS
    
    clients_list = [
        {
            'id': client['id'],
            'email': client['email'],
            'nama': client['nama'],
            'jenis': client['jenis']
        }
        for client in filtered_clients
    ]
    
    return render(request, 'klinik/list_klien.html', {
        'clients': clients_list,
        'search_query': search_query
    })

def detail_klien(request, client_id):
    client = next((c for c in DUMMY_CLIENTS if c['id'] == client_id), None)
    
    return render(request, 'klinik/detail_klien.html', {
        'client': client,
        'pets': client['pets']
    })
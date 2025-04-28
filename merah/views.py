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
    {'kode': 'VAC001', 'nama': 'Feline Panleukopenia', 'stok': 100},
    {'kode': 'VAC002', 'nama': 'Canine Parvovirus', 'stok': 200},
    {'kode': 'VAC003', 'nama': 'Canine Adenovirus', 'stok': 300}
]

def list_vaksinasi(request):
    return render(request, 'vaksinasi/list_vaksinasi.html', {
        'vaksinasi_list': DUMMY_VACCINATIONS
    })

def add_vaksinasi(request):
    return render(request, 'vaksinasi/add_vaksinasi.html', {
        'kunjungan_options': DUMMY_VACCINATIONS,
        'vaksin_options': DUMMY_VACCINES
    })

def update_vaksinasi(request, id_kunjungan):
    selected_vaccination = next(
        (v for v in DUMMY_VACCINATIONS if v['id_kunjungan'] == id_kunjungan), 
        None
    )
    return render(request, 'vaksinasi/update_vaksinasi.html', {
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
            # Hapus dari list dummy
            DUMMY_VACCINATIONS = [v for v in DUMMY_VACCINATIONS if v['id_kunjungan'] != id_kunjungan]
            
            # Update stok vaksin (optional)
            for vaksin in DUMMY_VACCINES:
                if vaksin['kode'] == vaksinasi_dihapus['kode_vaksin']:
                    vaksin['stok'] += 1  # atau logika penambahan stok sesuai kebutuhan
                    break
            
            messages.success(request, f'Vaksinasi {id_kunjungan} berhasil dihapus!')
        else:
            messages.error(request, f'Vaksinasi {id_kunjungan} tidak ditemukan!')
        
        return redirect('merah:list_vaksinasi')
    
    # Jika bukan method POST, redirect ke list
    return redirect('merah:list_vaksinasi')
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TreatmentForm  # Form untuk Create dan Update

# Data hardcoded, menggantikan pemanggilan model
treatments = [
    {
        'id_kunjungan': 'KJN001',
        'id_klien': 'FD123',
        'nama_hewan': 'Snowy',
        'perawat_hewan': 'Joko',
        'dokter_hewan': 'Dr. Rizki',
        'front_desk_officer': 'Tina',
        'jenis_perawatan': 'TRM001 - Dental Care',
        'catatan_medis': 'Oke'
    },
    {
        'id_kunjungan': 'KJN002',
        'id_klien': 'KII123',
        'nama_hewan': 'Blacky',
        'perawat_hewan': 'Agus',
        'dokter_hewan': 'Dr. Safira',
        'front_desk_officer': 'Tini',
        'jenis_perawatan': 'TRM002 - Parasite Control',
        'catatan_medis': 'Sudah Baik'
    },
    {
        'id_kunjungan': 'KJN003',
        'id_klien': 'PKE123',
        'nama_hewan': 'Hamseung',
        'perawat_hewan': 'Budi',
        'dokter_hewan': 'Dr. Nanu',
        'front_desk_officer': 'Tono',
        'jenis_perawatan': 'TRM003 - Flea Treatment',
        'catatan_medis': 'Sehat'
    }
]

# Fungsi untuk menampilkan daftar perawatan
def list_perawatan(request):
    return render(request, 'list_perawatan.html', {
        'treatments': treatments
    })

# Fungsi untuk membuat perawatan baru (Create)
def create_perawatan(request):
    if request.method == 'POST':
        form = TreatmentForm(request.POST)
        if form.is_valid():
            # Simpan data treatment baru (hardcoded)
            new_treatment = form.cleaned_data
            treatments.append(new_treatment)  # Menambahkan perawatan baru ke list
            return redirect('list_perawatan')  # Redirect ke daftar perawatan setelah pembuatan
    else:
        form = TreatmentForm()

    return render(request, 'create_perawatan.html', {'form': form})

# Fungsi untuk memperbarui perawatan (Update)
def update_perawatan(request, id_kunjungan):
    # Cari treatment berdasarkan ID Kunjungan
    treatment = next((t for t in treatments if t['id_kunjungan'] == id_kunjungan), None)

    if not treatment:
        return redirect('list_perawatan')  # Jika tidak ditemukan, kembali ke daftar

    if request.method == 'POST':
        form = TreatmentForm(request.POST)
        if form.is_valid():
            # Update data treatment
            treatment.update(form.cleaned_data)
            return redirect('list_perawatan')  # Redirect setelah pembaruan
    else:
        # Isi form dengan data treatment yang ada
        initial_data = {
            'id_kunjungan': treatment['id_kunjungan'],
            'id_klien': treatment['id_klien'],
            'nama_hewan': treatment['nama_hewan'],
            'perawat_hewan': treatment['perawat_hewan'],
            'dokter_hewan': treatment['dokter_hewan'],
            'front_desk_officer': treatment['front_desk_officer'],
            'jenis_perawatan': treatment['jenis_perawatan'],
            'catatan_medis': treatment['catatan_medis']
        }
        form = TreatmentForm(initial=initial_data)

    return render(request, 'update_perawatan.html', {'form': form, 'treatment': treatment})

# Fungsi untuk menghapus perawatan (Delete)
def delete_perawatan(request, id_kunjungan):
    # Cari treatment berdasarkan ID Kunjungan
    treatment = next((t for t in treatments if t['id_kunjungan'] == id_kunjungan), None)

    if not treatment:
        return redirect('list_perawatan')  # Jika tidak ditemukan, kembali ke daftar

    if request.method == 'POST':
        # Hapus treatment
        treatments.remove(treatment)
        return redirect('list_perawatan')  # Redirect setelah penghapusan

    return render(request, 'delete_perawatan.html', {'treatment': treatment})

# Data Hardcoded untuk List Kunjungan
kunjungan_list = [
    {
        'id_kunjungan': 'KJN001',
        'id_klien': 'FD123',
        'nama_hewan': 'Snowy',
        'metode_kunjungan': 'Janji Temu',
        'waktu_mulai_penanganan': '03-04-2025 14:30:13',
        'waktu_akhir_penanganan': '03-04-2025 15:30:16',
        'rekam_medis': 'Lihat Rekam Medis'
    },
    {
        'id_kunjungan': 'KJN002',
        'id_klien': 'KII123',
        'nama_hewan': 'Blacky',
        'metode_kunjungan': 'Walk-In',
        'waktu_mulai_penanganan': '05-08-2025 12:30:27',
        'waktu_akhir_penanganan': '05-08-2025 13:30:19',
        'rekam_medis': 'Lihat Rekam Medis'
    },
    {
        'id_kunjungan': 'KJN003',
        'id_klien': 'PKE123',
        'nama_hewan': 'Hamseung',
        'metode_kunjungan': 'Darurat',
        'waktu_mulai_penanganan': '01-09-2025 16:30:51',
        'waktu_akhir_penanganan': '01-09-2025 18:00:33',
        'rekam_medis': 'Lihat Rekam Medis'
    }
]

def list_kunjungan(request):
    # Mengirim data kunjungan_list ke template
    return render(request, 'list_kunjungan.html', {'kunjungan_list': kunjungan_list})

def create_kunjungan(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan(request):
    return render(request, 'delete_kunjungan.html')

def create_rekam_medis(request):
    return render(request, 'create_rekam_medis.html')

def list_medis(request):
    return render(request, 'list_rekam_medis.html')

def update_rekam_medis(request):
    return render(request, 'update_rekam_medis.html')
import re
import psycopg2
from datetime import date
from utils.db_utils import get_db_connection
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def login_register(request):
    return render(request, 'login_register.html')

@require_http_methods(['GET', 'POST'])
def register(request):
    # Ambil role dari querystring
    role = request.GET.get('role')

    # Jika belum memilih role, tampilkan halaman pilihan role
    if not role:
        return render(request, 'register.html')

    # Map role → nama template
    template_map = {
        'individu':      'register_individu.html',
        'perusahaan':    'register_perusahaan.html',
        'front_desk':    'register_front_desk.html',
        'dokter_hewan':  'register_dokter_hewan.html',
        'perawat_hewan': 'register_perawat_hewan.html',
    }
    tpl = template_map.get(role)
    if not tpl:
        messages.error(request, "Role tidak valid.")
        return redirect('main:register')

    # Context dasar untuk render
    context = {
        'form_title': {
            'individu':      'Klien – Individu',
            'perusahaan':    'Klien – Perusahaan',
            'front_desk':    'Front-Desk Officer',
            'dokter_hewan':  'Dokter Hewan',
            'perawat_hewan': 'Perawat Hewan',
        }[role],
        'data': {},
        'errors': {},
        'non_field': None,
    }

    # Jika GET → tampilkan form kosong
    if request.method == 'GET':
        return render(request, tpl, context)

    # === Proses POST ===
    data = request.POST
    errors = {}
    email = data.get('email','').strip()
    pwd = data.get('password','').strip()
    alamat = data.get('alamat','').strip()
    telepon = data.get('nomor_telepon','').strip()

    # Validasi universal
    if not email:
        errors['email'] = 'Email wajib diisi.'
    if len(email) > 50:
        errors['email'] = 'Email terlalu panjang (maks 50 karakter).'
    if not pwd:
        errors['password'] = 'Password wajib diisi.'
    if not alamat:
        errors['alamat'] = 'Alamat wajib diisi.'
    if not telepon:
        errors['nomor_telepon'] = 'Nomor telepon wajib diisi.'
    if len(telepon) > 15:
        errors['nomor_telepon'] = 'Nomor telepon terlalu panjang (maks 15 karakter).'
    if not telepon.isdigit():
        errors['nomor_telepon'] = 'Nomor telepon hanya boleh angka.'
    
    # Validasi khusus front_desk
    if role == 'front_desk':
        tanggal_mulai = data.get('tanggal_mulai_kerja','').strip()
        if not tanggal_mulai:
            errors['tanggal_mulai_kerja'] = 'Tanggal mulai kerja wajib diisi.'

    # Jika ada error validasi → render ulang dengan pesan
    if errors:
        context.update({
            'data': data,
            'errors': errors,
        })
        return render(request, tpl, context)

    # Simpan ke DB
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        print(f"DEBUG: Attempting to insert user with email: {email}")
        
        # 1) Insert ke USER table
        cur.execute(
            'INSERT INTO "USER"(email, password, alamat, nomor_telepon) VALUES (%s, %s, %s, %s)',
            (email, pwd, alamat, telepon)
        )
        print("DEBUG: User inserted successfully")

        # 2) Insert PEGAWAI untuk front_desk
        if role == 'front_desk':
            tanggal_mulai = data.get('tanggal_mulai_kerja','').strip()
            print(f"DEBUG: Inserting PEGAWAI with tanggal_mulai_kerja: {tanggal_mulai}, email: {email}")
            
            cur.execute(
                'INSERT INTO PEGAWAI(tanggal_mulai_kerja, tanggal_akhir_kerja, email_user) '
                'VALUES (%s, NULL, %s)', 
                (tanggal_mulai, email)
            )
            print("DEBUG: PEGAWAI inserted successfully")
            
            # Ambil no_pegawai yang baru saja diinsert
            cur.execute(
                'SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s ORDER BY tanggal_mulai_kerja DESC LIMIT 1',
                (email,)
            )
            result = cur.fetchone()
            if not result:
                raise Exception("Failed to retrieve no_pegawai after insertion")
            
            no_pegawai = result[0]
            print(f"DEBUG: Retrieved no_pegawai: {no_pegawai}")

            # Insert ke FRONT_DESK
            cur.execute('INSERT INTO FRONT_DESK(no_front_desk) VALUES (%s)', (no_pegawai,))
            print("DEBUG: FRONT_DESK inserted successfully")
        
        # Commit transaction
        conn.commit()
        print("DEBUG: Transaction committed successfully")
        
        messages.success(request, 'Registrasi berhasil! Silakan login.')
        return redirect('main:login_register')

    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        
        if conn:
            conn.rollback()
            print("DEBUG: Transaction rolled back")
            
        # Tampilkan error yang lebih spesifik untuk debugging
        context['non_field'] = f'Terjadi kesalahan saat menyimpan data: {str(e)}'
        return render(request, tpl, context)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("DEBUG: Database connection closed")
            
def login(request):
    return render(request, 'login.html')

def profile_klien(request):
    return render(request, 'profile_klien.html')

def profile_frontdesk(request):
    return render(request, 'profile_frontdesk.html')

def profile_dokter(request):
    return render(request, 'profile_dokter.html')

def profile_perawat(request):
    return render(request, 'profile_perawat.html')

def update_password(request):
    return render(request, 'update_password.html')

@require_http_methods(['GET'])
def logout_view(request):
    request.session.flush()
    return redirect('main:login')
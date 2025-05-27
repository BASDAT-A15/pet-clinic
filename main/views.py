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
            
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    if not email or not password:
        messages.error(request, 'Email dan password wajib diisi.')
        return redirect('main:login')

    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        # 1) Autentikasi
        cur.execute(
            'SELECT email FROM "USER" WHERE email=%s AND password=%s',
            (email, password)
        )
        if not cur.fetchone():
            messages.error(request, 'Email atau password salah.')
            return redirect('main:login')

        # 2) Cek di KLIEN → INDIVIDU / PERUSAHAAN
        cur.execute('SELECT no_identitas, tanggal_registrasi FROM KLIEN WHERE email=%s', (email,))
        kli = cur.fetchone()
        if kli:
            no_identitas, tgl_reg = kli

            # tentukan tipe klien
            cur.execute('SELECT 1 FROM INDIVIDU WHERE no_identitas_klien=%s', (no_identitas,))
            if cur.fetchone():
                role = 'individu'
            else:
                role = 'perusahaan'

            # simpan session & redirect
            request.session['email']        = email
            request.session['role']         = role
            request.session['no_identitas'] = str(no_identitas)
            return redirect('main:profile_klien')

        # 3) Kalau bukan klien, cek PEGAWAI
        cur.execute(
            '''SELECT no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja
               FROM PEGAWAI WHERE email_user=%s
               ORDER BY tanggal_mulai_kerja DESC LIMIT 1''',
            (email,)
        )
        peg = cur.fetchone()
        if not peg:
            messages.error(request, 'Akun tidak terdaftar sebagai klien atau pegawai.')
            return redirect('main:login')

        no_pegawai, t_mulai, t_akhir = peg

        # 4) tentukan tipe pegawai
        # Front-Desk?
        cur.execute('SELECT 1 FROM FRONT_DESK WHERE no_front_desk=%s', (no_pegawai,))
        if cur.fetchone():
            role = 'front_desk'
            profile_url = 'main:profile_frontdesk'
        else:
            # Tenaga Medis → Dokter / Perawat
            cur.execute('SELECT no_izin_praktik FROM TENAGA_MEDIS WHERE no_tenaga_medis=%s', (no_pegawai,))
            medis = cur.fetchone()
            if not medis:
                messages.error(request, 'Data tenaga medis tidak lengkap.')
                return redirect('main:login')

            # Dokter vs Perawat
            cur.execute('SELECT 1 FROM DOKTER_HEWAN WHERE no_dokter_hewan=%s', (no_pegawai,))
            if cur.fetchone():
                role = 'dokter_hewan'
                profile_url = 'main:profile_dokter'
            else:
                role = 'perawat_hewan'
                profile_url = 'main:profile_perawat'

        # 5) simpan session & redirect
        request.session['email']      = email
        request.session['role']       = role
        request.session['no_pegawai'] = str(no_pegawai)
        return redirect(profile_url)

    except psycopg2.Error as e:
        print("Login DB error:", e)
        messages.error(request, 'Terjadi kesalahan server.')
        return redirect('main:login')

    finally:
        if conn:
            cur.close()
            conn.close()

@require_http_methods(['GET'])
def profile_klien(request):
    # 1) Pastikan sudah login
    email = request.session.get('email')
    if not email:
        return redirect('main:login')

    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        # 2) Ambil data USER
        cur.execute(
            'SELECT alamat, nomor_telepon FROM "USER" WHERE email = %s',
            (email,)
        )
        user_row = cur.fetchone()
        alamat, nomor_telepon = user_row

        # 3) Ambil data KLIEN
        cur.execute(
            'SELECT no_identitas, tanggal_registrasi FROM KLIEN WHERE email = %s',
            (email,)
        )
        kli_row = cur.fetchone()
        no_identitas, tanggal_reg = kli_row

        # 4) Cek apakah ini Individu atau Perusahaan
        #    Kita coba INDIVIDU dulu; kalau tidak ada, ambil PERUSAHAAN
        cur.execute(
            'SELECT nama_depan, nama_tengah, nama_belakang FROM INDIVIDU WHERE no_identitas_klien = %s',
            (no_identitas,)
        )
        indiv = cur.fetchone()
        if indiv:
            # bentuk full name
            nama_depan, nama_tengah, nama_belakang = indiv
            if nama_tengah:
                full_name = f"{nama_depan} {nama_tengah} {nama_belakang}"
            else:
                full_name = f"{nama_depan} {nama_belakang}"
        else:
            # Perusahaan
            cur.execute(
                'SELECT nama_perusahaan FROM PERUSAHAAN WHERE no_identitas_klien = %s',
                (no_identitas,)
            )
            nama_perusahaan = cur.fetchone()[0]
            full_name = nama_perusahaan

        # 5) Format tanggal (misal "26 Januari 2025")
        tanggal_str = tanggal_reg.strftime('%d %B %Y')

        context = {
            'no_identitas':    no_identitas,
            'email':           email,
            'full_name':       full_name,
            'tanggal_registrasi': tanggal_str,
            'alamat':          alamat,
            'nomor_telepon':   nomor_telepon,
        }
        return render(request, 'profile_klien.html', context)

    except Exception:
        # kalau ada error, redirect atau tampilkan pesan sesuai kebijakan
        return redirect('main:login')

    finally:
        if conn:
            cur.close()
            conn.close()

@require_http_methods(['GET'])
def profile_frontdesk(request):
    # 1) Cek session login
    email = request.session.get('email')
    if not email:
        return redirect('main:login')

    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        # 2) Ambil data USER (alamat & nomor_telepon)
        cur.execute(
            'SELECT alamat, nomor_telepon FROM "USER" WHERE email = %s',
            (email,)
        )
        alamat, nomor_telepon = cur.fetchone()

        # 3) Ambil data PEGAWAI
        cur.execute(
            '''SELECT no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja
               FROM PEGAWAI
               WHERE email_user = %s
               ORDER BY tanggal_mulai_kerja DESC
               LIMIT 1''',
            (email,)
        )
        no_pegawai, t_mulai, t_akhir = cur.fetchone()

        # 4) Format tanggal
        t_mulai_str  = t_mulai.strftime('%d %B %Y')
        t_akhir_str  = t_akhir.strftime('%d %B %Y') if t_akhir else '-'

        context = {
            'no_identitas':      no_pegawai,
            'email':             email,
            'tanggal_mulai':     t_mulai_str,
            'tanggal_akhir':     t_akhir_str,
            'alamat':            alamat,
            'nomor_telepon':     nomor_telepon,
        }
        return render(request, 'profile_front_desk.html', context)

    finally:
        if conn:
            cur.close()
            conn.close()

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
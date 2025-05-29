import re
import psycopg2
from datetime import date, datetime
from utils.db_utils import get_db_connection
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import logout
import uuid

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

        no_uuid = uuid.uuid4()

        
        # 1) Insert ke USER table
        cur.execute(
            'INSERT INTO "USER"(email, password, alamat, nomor_telepon) VALUES (%s, %s, %s, %s)',
            (email, pwd, alamat, telepon)
        )

        if role == "individu":
            nama_depan = data.get('nama_depan','').strip()
            nama_tengah = data.get('nama_tengah','').strip()
            nama_belakang = data.get('nama_belakang','').strip()

            cur.execute(
                'INSERT INTO KLIEN(no_identitas, tanggal_registrasi, email)'
                'VALUES (%s, %s, %s)', (no_uuid, datetime.today().date(), email)
            )

            cur.execute(
                'INSERT INTO INDIVIDU(no_identitas_klien, nama_depan, nama_tengah, nama_belakang )'
                'VALUES (%s, %s, %s, %s)',
                (no_uuid, nama_depan, nama_tengah, nama_belakang)
            )

        if role == "perusahaan":
            nama_perusahaan = data.get('nama_perusahaan','').strip()

            cur.execute(
                'INSERT INTO KLIEN(no_identitas, tanggal_registrasi, email)'
                'VALUES (%s, %s, %s) RETURNING no_identitas', (no_uuid, datetime.today().date(), email)
            )

            cur.execute(
                'INSERT INTO PERUSAHAAN(no_identitas_klien, nama_perusahaan) VALUES (%s, %s)',
                (no_uuid, nama_perusahaan)
            )

        if role == 'front_desk':
            tanggal_mulai = data.get('tanggal_mulai_kerja','').strip()
            
            cur.execute(
                'INSERT INTO PEGAWAI(no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user) '
                'VALUES (%s, %s, NULL, %s) ', (no_uuid, tanggal_mulai, email)
            )
            

            cur.execute('INSERT INTO FRONT_DESK(no_front_desk) VALUES (%s)', (no_uuid,))
        
        if role == 'perawat_hewan':
            tanggal_mulai = data.get('tanggal_mulai_kerja','').strip()
            
            nama_sertifikat = data.get('nama_sertifikat','').strip()
            no_sertifikat_kompetensi = data.get('no_sertifikat_kompetensi','').strip()

            cur.execute(
                'INSERT INTO PEGAWAI(no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user) '
                'VALUES (%s, %s, NULL, %s)', 
                (no_uuid, tanggal_mulai, email)
            )

            no_izin_praktik = data.get('no_izin_praktik','').strip()

            cur.execute('INSERT INTO TENAGA_MEDIS(no_tenaga_medis, no_izin_praktik)'
                        'VALUES (%s, %s)', (no_uuid, no_izin_praktik))
            
            cur.execute('INSERT INTO PERAWAT_HEWAN(no_perawat_hewan) VALUES (%s)', (no_uuid,))

            no_sertifikat_kompetensi = request.POST.getlist('no_sertifikat_kompetensi')
            nama_sertifikat = request.POST.getlist('nama_sertifikat')
            for no_sertifikat_kompetensi, nama_sertifikat in zip(no_sertifikat_kompetensi, nama_sertifikat):
                if no_sertifikat_kompetensi.strip() and nama_sertifikat.strip():
                    cur.execute(
                        'INSERT INTO SERTIFIKAT_KOMPETENSI(no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) '
                        'VALUES (%s, %s, %s)',
                        (no_sertifikat_kompetensi, no_uuid, nama_sertifikat)
                    )

        if role == 'dokter_hewan':
            tanggal_mulai = data.get('tanggal_mulai_kerja','').strip()
            
            nama_sertifikat = data.get('nama_sertifikat','').strip()
            no_sertifikat_kompetensi = data.get('no_sertifikat_kompetensi','').strip()

            cur.execute(
                'INSERT INTO PEGAWAI(no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user) '
                'VALUES (%s, %s, NULL, %s)', 
                (no_uuid, tanggal_mulai, email)
            )

            no_izin_praktik = data.get('no_izin_praktik','').strip()

            cur.execute('INSERT INTO TENAGA_MEDIS(no_tenaga_medis, no_izin_praktik)'
                        'VALUES (%s, %s)', (no_uuid, no_izin_praktik))
            
            cur.execute('INSERT INTO DOKTER_HEWAN(no_dokter_hewan) VALUES (%s)', (no_uuid,))

            no_sertifikat_kompetensi = request.POST.getlist('no_sertifikat_kompetensi')
            nama_sertifikat = request.POST.getlist('nama_sertifikat')
            for no_sertifikat_kompetensi, nama_sertifikat in zip(no_sertifikat_kompetensi, nama_sertifikat):
                if no_sertifikat_kompetensi.strip() and nama_sertifikat.strip():
                    cur.execute(
                        'INSERT INTO SERTIFIKAT_KOMPETENSI(no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) '
                        'VALUES (%s, %s, %s)',
                        (no_sertifikat_kompetensi, no_uuid, nama_sertifikat)
                    )

            hari_list = request.POST.getlist('hari')
            jam_list = request.POST.getlist('jam')
            for hari, jam in zip(hari_list, jam_list):
                if hari.strip() and jam.strip():
                    cur.execute(
                        'INSERT INTO JADWAL_PRAKTIK(no_dokter_hewan, hari, jam) VALUES (%s, %s, %s)',
                        (no_uuid, hari, jam)
                    )

        conn.commit()
        
        messages.success(request, 'Registrasi berhasil! Silakan login.')
        return redirect('main:login_register')

    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        
        if conn:
            conn.rollback()
            
        # Tampilkan error yang lebih spesifik untuk debugging
        
        full_msg  = str(e)
        clean_msg = full_msg.split('CONTEXT')[0].strip()
        context['non_field'] = clean_msg

        return render(request, tpl, context)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
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
            'no_pegawai':      no_pegawai,
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

@require_http_methods(['GET'])
def profile_perawat(request):
    email = request.session.get('email')
    role  = request.session.get('role')
    if not email or role != 'perawat_hewan':
        return redirect('main:login')

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # 1) Data USER
        cur.execute(
            'SELECT alamat, nomor_telepon FROM "USER" WHERE email=%s',
            (email,)
        )
        alamat, nomor_hp = cur.fetchone()

        # 2) Data PEGAWAI & TENAGA_MEDIS
        cur.execute(
            '''SELECT p.no_pegawai, p.tanggal_mulai_kerja, p.tanggal_akhir_kerja,
                      t.no_izin_praktik
               FROM PEGAWAI p
               JOIN TENAGA_MEDIS t ON t.no_tenaga_medis = p.no_pegawai
               JOIN PERAWAT_HEWAN pr ON pr.no_perawat_hewan = p.no_pegawai
               WHERE p.email_user = %s
               ORDER BY p.tanggal_mulai_kerja DESC
               LIMIT 1''',
            (email,)
        )
        
        no_peg, t_mulai, t_akhir, no_izin = cur.fetchone()

        # 3) Daftar sertifikat
        cur.execute(
            'SELECT no_sertifikat_kompetensi, nama_sertifikat '
            'FROM SERTIFIKAT_KOMPETENSI '
            'WHERE no_tenaga_medis = %s',
            (no_peg,)
        )
        sertis = cur.fetchall()  # list of tuples

        # 4) Format tanggal
        fmt = lambda d: d.strftime('%d %B %Y') if d else '-'
        t_mulai_s = fmt(t_mulai)
        t_akhir_s = fmt(t_akhir)

        context = {
            'data': {
                'no_pegawai':       str(no_peg),
                'no_izin_praktik':   no_izin,
                'email':            email,
                'tanggal_mulai':    t_mulai_s,
                'tanggal_akhir':    t_akhir_s,
                'alamat':           alamat,
                'nomor_telepon':    nomor_hp,
                'sertifikats':      sertis,
            },
            'edit_mode': False,
        }
        return render(request, 'profile_perawat.html', context)

    finally:
        cur.close()
        conn.close()

@require_http_methods(['GET'])
def profile_dokter(request):
    email = request.session.get('email')
    role  = request.session.get('role')
    if not email or role != 'dokter_hewan':
        return redirect('main:login')

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # 1) Data USER
        cur.execute(
            'SELECT alamat, nomor_telepon FROM "USER" WHERE email=%s',
            (email,)
        )
        alamat, nomor_hp = cur.fetchone()

        # 2) Data PEGAWAI & TENAGA_MEDIS
        cur.execute(
            '''SELECT p.no_pegawai, p.tanggal_mulai_kerja, p.tanggal_akhir_kerja,
                      t.no_izin_praktik
               FROM PEGAWAI p
               JOIN TENAGA_MEDIS t ON t.no_tenaga_medis = p.no_pegawai
               JOIN DOKTER_HEWAN d ON d.no_dokter_hewan = p.no_pegawai
               WHERE p.email_user = %s
               ORDER BY p.tanggal_mulai_kerja DESC
               LIMIT 1''',
            (email,)
        )
        no_peg, t_mulai, t_akhir, no_izin = cur.fetchone()

        # 3) Daftar sertifikat
        cur.execute(
            'SELECT no_sertifikat_kompetensi, nama_sertifikat '
            'FROM SERTIFIKAT_KOMPETENSI '
            'WHERE no_tenaga_medis = %s',
            (no_peg,)
        )
        sertis = cur.fetchall()

        # 4) Jadwal praktik
        cur.execute(
            'SELECT hari, jam FROM JADWAL_PRAKTIK WHERE no_dokter_hewan = %s',
            (no_peg,)
        )
        jadwals = cur.fetchall()

        # 5) Format tanggal
        fmt = lambda d: d.strftime('%d %B %Y') if d else '-'
        t_mulai_s = fmt(t_mulai)
        t_akhir_s = fmt(t_akhir)

        context = {
            'data': {
                'no_pegawai':       str(no_peg),
                'no_izin_praktik':  no_izin,
                'email':            email,
                'tanggal_mulai':    t_mulai_s,
                'tanggal_akhir':    t_akhir_s,
                'alamat':          alamat,
                'nomor_telepon':    nomor_hp,
                'sertifikats':     sertis,
                'jadwals':          jadwals,
            },
            'edit_mode': False,
        }
        return render(request, 'profile_dokter.html', context)

    finally:
        cur.close()
        conn.close()
        
@require_http_methods(['GET', 'POST'])
def update_password(request):
    if not request.session.get('email'):
        return redirect('main:login')

    if request.method == 'GET':
        return render(request, 'update_password.html')
    
    old_password = request.POST.get('old_password', '').strip()
    new_password = request.POST.get('new_password', '').strip()
    confirm_password = request.POST.get('confirm_password', '').strip()
    email = request.session.get('email')
    
    if not old_password or not new_password or not confirm_password:
        messages.error(request, 'Semua field wajib diisi.')
        return render(request, 'update_password.html')
        
    if new_password != confirm_password:
        messages.error(request, 'Password baru dan konfirmasi password tidak cocok.')
        return render(request, 'update_password.html')
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT 1 FROM "USER" WHERE email=%s AND password=%s', (email, old_password))
        if not cur.fetchone():
            messages.error(request, 'Password lama salah.')
            return render(request, 'update_password.html')
        
        cur.execute('UPDATE "USER" SET password=%s WHERE email=%s', (new_password, email))
        conn.commit()
        
        messages.success(request, 'Password berhasil diperbarui.')
        
        return redirect('main:login')
    
    except Exception as e:
        if conn:
            conn.rollback()
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'update_password.html')
    
    finally:
        if conn:
            cur.close()
            conn.close()

@require_http_methods(['GET','POST'])
def update_profile(request):
    email = request.session.get('email')
    role  = request.session.get('role')
    if not email or not role:
        return redirect('main:login')

    # Template mapping - moved outside to be available for both GET and POST
    tpl_map = {
        'individu':     'profile_klien.html',
        'perusahaan':   'profile_klien.html',
        'front_desk':   'profile_front_desk.html',
        'dokter_hewan': 'profile_dokter.html',
        'perawat_hewan':'profile_perawat.html',
    }

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # === GET: tampilkan form di sebelah tampilan profil ===
        if request.method == 'GET':
            # ambil data sama seperti profile view tapi simpan ke context['data']
            data = {}
            data['email'] = email
            # common fields from USER
            cur.execute('SELECT alamat,nomor_telepon FROM "USER" WHERE email=%s', (email,))
            user_data = cur.fetchone()
            if user_data:
                data['alamat'], data['nomor_telepon'] = user_data

            if role in ('individu','perusahaan'):
                cur.execute('SELECT no_identitas FROM KLIEN WHERE email=%s', (email,))
                klien_data = cur.fetchone()
                if klien_data:
                    data['no_identitas'] = klien_data[0]
                    if role=='individu':
                        cur.execute(
                          'SELECT nama_depan,nama_tengah,nama_belakang FROM INDIVIDU WHERE no_identitas_klien=%s',
                          (data['no_identitas'],)
                        )
                        individu_data = cur.fetchone()
                        if individu_data:
                            data['nama_depan'], data['nama_tengah'], data['nama_belakang'] = individu_data
                    else:
                        cur.execute(
                          'SELECT nama_perusahaan FROM PERUSAHAAN WHERE no_identitas_klien=%s',
                          (data['no_identitas'],)
                        )
                        perusahaan_data = cur.fetchone()
                        if perusahaan_data:
                            data['nama_perusahaan'] = perusahaan_data[0]

            else:  # pegawai
                cur.execute(
                  'SELECT no_pegawai,tanggal_mulai_kerja,tanggal_akhir_kerja '
                  'FROM PEGAWAI WHERE email_user=%s ORDER BY tanggal_mulai_kerja DESC LIMIT 1',
                  (email,)
                )
                pegawai_data = cur.fetchone()
                if pegawai_data:
                    no_peg, t_mulai, t_akhir = pegawai_data
                    data['no_pegawai'] = no_peg
                    data['tanggal_mulai'] = t_mulai
                    data['tanggal_akhir'] = t_akhir

                    # Store no_pegawai in session if not already there
                    if 'no_pegawai' not in request.session:
                        request.session['no_pegawai'] = str(no_peg)

                    if role in ('dokter_hewan', 'perawat_hewan'):
                        # Get no_izin_praktik
                        cur.execute(
                          'SELECT no_izin_praktik FROM TENAGA_MEDIS WHERE no_tenaga_medis=%s',
                          (no_peg,)
                        )
                        
                        izin_data = cur.fetchone()
                        if izin_data:
                            data['no_izin_praktik'] = izin_data[0]

                        # sertifikat list
                        cur.execute(
                          'SELECT no_sertifikat_kompetensi,nama_sertifikat '
                          'FROM SERTIFIKAT_KOMPETENSI WHERE no_tenaga_medis=%s',
                          (no_peg,)
                        )
                        data['sertifikats'] = cur.fetchall()
                        
                        if role=='dokter_hewan':
                            # jadwal
                            cur.execute(
                              'SELECT hari,jam FROM JADWAL_PRAKTIK WHERE no_dokter_hewan=%s',
                              (no_peg,)
                            )
                            data['jadwals'] = cur.fetchall()

            context = {
                'data': data,
                'edit_mode': True,
                'errors': {},
                'non_field': None,
            }
            return render(request, tpl_map[role], context)

        # === POST: proses update ===
        post = request.POST
        errors = {}

        # validasi universal
        alamat = post.get('alamat','').strip()
        telepon = post.get('nomor_telepon','').strip()
        if not alamat: 
            errors['alamat'] = 'Alamat wajib diisi.'
        if not telepon: 
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi.'

        # role‐specific validation
        if role=='individu':
            nama_depan = post.get('nama_depan','').strip()
            nama_belakang = post.get('nama_belakang','').strip()
            if not nama_depan: 
                errors['nama_depan'] = 'Nama depan wajib diisi.'
            if not nama_belakang: 
                errors['nama_belakang'] = 'Nama belakang wajib diisi.'
        elif role=='perusahaan':
            nama_perusahaan = post.get('nama_perusahaan','').strip()
            if not nama_perusahaan: 
                errors['nama_perusahaan'] = 'Nama perusahaan wajib diisi.'

        # Validate jadwal praktik format for dokter_hewan
        if role == 'dokter_hewan':
            jadwal_list = list(zip(post.getlist('hari'), post.getlist('jam')))
            for i, (hari, jam) in enumerate(jadwal_list):
                if hari.strip() and jam.strip():
                    # Simple validation for time format (e.g., "13.00-15.00")
                    if '-' not in jam or len(jam.split('-')) != 2:
                        errors[f'jam_praktik_{i}'] = f'Format jam praktik tidak valid untuk {hari}. Gunakan format: HH.MM-HH.MM'

        # If there are errors, return to form with error messages
        if errors:
            # Get current data to repopulate form
            data = dict(post.items())
            data['email'] = email
            
            # For dokter_hewan and perawat_hewan, rebuild sertifikats and jadwals from POST data
            if role in ('dokter_hewan', 'perawat_hewan'):
                # Rebuild sertifikats from form data
                no_sertifikat_list = post.getlist('no_sertifikat_kompetensi')
                nama_sertifikat_list = post.getlist('nama_sertifikat')
                data['sertifikats'] = list(zip(no_sertifikat_list, nama_sertifikat_list))
                
                if role == 'dokter_hewan':
                    # Rebuild jadwals from form data
                    hari_list = post.getlist('hari')
                    jam_list = post.getlist('jam')
                    data['jadwals'] = list(zip(hari_list, jam_list))

            context = {
                'data': data, 
                'errors': errors, 
                'edit_mode': True,
                'non_field': None
            }
            return render(request, tpl_map[role], context)

        # lakukan update ke database
        try:
            # Update USER table
            if hasattr(conn, 'notices'):
                conn.notices.clear()
                
            cur.execute(
                'UPDATE "USER" SET alamat=%s, nomor_telepon=%s WHERE email=%s',
                (alamat, telepon, email)
            )

            if role=='individu':
                cur.execute(
                  'UPDATE INDIVIDU SET nama_depan=%s, nama_tengah=%s, nama_belakang=%s '
                  'WHERE no_identitas_klien=(SELECT no_identitas FROM KLIEN WHERE email=%s)',
                  (
                    post['nama_depan'].strip(),
                    post.get('nama_tengah','').strip() or None,
                    post['nama_belakang'].strip(),
                    email
                  )
                )
            elif role=='perusahaan':
                cur.execute(
                  'UPDATE PERUSAHAAN SET nama_perusahaan=%s '
                  'WHERE no_identitas_klien=(SELECT no_identitas FROM KLIEN WHERE email=%s)',
                  (post['nama_perusahaan'].strip(), email)
                )
            else:  # pegawai (front_desk, dokter_hewan, perawat_hewan)
                no_pegawai = request.session.get('no_pegawai')
                if not no_pegawai:
                    # Get no_pegawai if not in session
                    cur.execute(
                      'SELECT no_pegawai FROM PEGAWAI WHERE email_user=%s ORDER BY tanggal_mulai_kerja DESC LIMIT 1',
                      (email,)
                    )
                    result = cur.fetchone()
                    if result:
                        no_pegawai = result[0]
                        request.session['no_pegawai'] = str(no_pegawai)

                if no_pegawai:
                    # Update tanggal akhir kerja
                    tanggal_akhir = post.get('tanggal_akhir_kerja') or None
                    cur.execute(
                      'UPDATE PEGAWAI SET tanggal_akhir_kerja=%s WHERE no_pegawai=%s',
                      (tanggal_akhir if tanggal_akhir else None, no_pegawai)
                    )
                    
                    # Tangkap NOTICE dari trigger & masukkan ke messages
                    # setelah: buang prefix "NOTICE:"
                    for notice in conn.notices:
                        text = notice.strip()
                        # Hapus kata "NOTICE:" di depan, kalau ada
                        if text.upper().startswith('NOTICE:'):
                            text = text[len('NOTICE:'):].strip()
                        messages.info(request, text)
                    conn.notices.clear()

                    if role in ('dokter_hewan','perawat_hewan'):
                        # Handle sertifikat kompetensi - replace all
                        cur.execute('DELETE FROM SERTIFIKAT_KOMPETENSI WHERE no_tenaga_medis=%s', (no_pegawai,))
                        
                        no_sertifikat_list = post.getlist('no_sertifikat_kompetensi')
                        nama_sertifikat_list = post.getlist('nama_sertifikat')
                        
                        for no_s, nm_s in zip(no_sertifikat_list, nama_sertifikat_list):
                            if no_s.strip() and nm_s.strip():
                                cur.execute(
                                  'INSERT INTO SERTIFIKAT_KOMPETENSI(no_sertifikat_kompetensi,no_tenaga_medis,nama_sertifikat) VALUES(%s,%s,%s)',
                                  (no_s.strip(), no_pegawai, nm_s.strip())
                                )

                         # jadwal hanya untuk dokter dan hanya jika masih aktif
            if role == 'dokter_hewan' and not tanggal_akhir:
                cur.execute(
                    'DELETE FROM jadwal_praktik WHERE no_dokter_hewan=%s',
                    (no_pegawai,)
                )
                for hari, jam in zip(
                        post.getlist('hari'),
                        post.getlist('jam')
                    ):
                    if hari.strip() and jam.strip():
                        cur.execute(
                            'INSERT INTO jadwal_praktik(no_dokter_hewan, hari, jam)'
                            ' VALUES(%s,%s,%s)',
                            (no_pegawai, hari.strip(), jam.strip())
                        )

            conn.commit()
            # IMPORTANT: Process PostgreSQL notices AFTER commit
            if hasattr(conn, 'notices') and conn.notices:
                for notice in conn.notices:
                    notice_text = notice.strip()
                    if 'INFO:' in notice_text:
                        # Extract the message after 'INFO:'
                        info_message = notice_text.split('INFO:', 1)[1].strip()
                        messages.info(request, info_message)
                    else:
                        messages.info(request, notice_text)
                # Clear notices after processing them
                conn.notices.clear()
            messages.success(request, 'Profil berhasil diperbarui!')
            
            # Redirect to appropriate profile page
            profile_url_map = {
                'individu':      'main:profile_klien',
                'perusahaan':    'main:profile_klien',
                'front_desk':    'main:profile_frontdesk',
                'dokter_hewan':  'main:profile_dokter',
                'perawat_hewan': 'main:profile_perawat',
            }
            return redirect(profile_url_map.get(role, 'main:login'))

        except Exception as e:
            conn.rollback()
            messages.error(request, f'Terjadi kesalahan saat memperbarui profil: {str(e)}')
            return redirect('main:update_profile')

    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('main:profile')
    finally:
        cur.close()
        conn.close()
        
@require_http_methods(['POST'])
def logout_view(request):
    request.session.flush()
    return redirect('main:login')

def debug_session(request):
    """Debug view to check current session information"""
    from django.http import HttpResponse
    
    email = request.session.get('email', 'Not set')
    role = request.session.get('role', 'Not set')
    no_pegawai = request.session.get('no_pegawai', 'Not set')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Session</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .info {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>Current Session Information</h1>
        <div class="info"><strong>Email:</strong> {email}</div>
        <div class="info"><strong>Role:</strong> {role}</div>
        <div class="info"><strong>No Pegawai:</strong> {no_pegawai}</div>
        <div class="info"><strong>All session data:</strong> {dict(request.session)}</div>
        <a href="/login/">Go to Login</a>
    </body>
    </html>
    """
    
    return HttpResponse(html)
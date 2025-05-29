from utils.db_utils import get_db_connection
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages

@require_http_methods(['GET'])
def list_vaksinasi(request):
    if request.session.get('role') != 'dokter_hewan':
        return HttpResponseForbidden("Hanya dokter hewan yang boleh akses.")

    no_dokter = request.session.get('no_pegawai')
    if not no_dokter:
        return HttpResponseForbidden("Session no_pegawai belum diset.")

    conn = get_db_connection()
    cur = conn.cursor()
    vaksinasi_list = []
    
    try:
        cur.execute("""
          SELECT k.id_kunjungan,
                 to_char(k.timestamp_awal, 'Day, DD Month YYYY') AS tanggal,
                 k.kode_vaksin,
                 v.nama
            FROM kunjungan k
            JOIN vaksin v ON v.kode = k.kode_vaksin
           WHERE k.no_dokter_hewan = %s
             AND k.kode_vaksin IS NOT NULL
        """, [no_dokter])
        rows = cur.fetchall()

        vaksinasi_list = [{
            'id_kunjungan': r[0],
            'tanggal': r[1],
            'kode_vaksin': r[2],
            'nama_vaksin': r[3],
        } for r in rows]

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/list_vaksinasi.html', {
        'vaksinasi_list': vaksinasi_list
    })

@require_http_methods(['GET', 'POST'])
def add_vaksinasi(request):
    # Hanya dokter hewan
    if request.session.get('role') != 'dokter_hewan':
        return HttpResponseForbidden("Hanya dokter hewan yang boleh akses.")
    no_dokter = request.session.get('no_pegawai')
    if not no_dokter:
        return HttpResponseForbidden("Session no_pegawai belum diset.")

    if request.method == 'POST':
        kunjungan = request.POST.get('id_kunjungan')
        vaksin    = request.POST.get('kode_vaksin')

        conn = get_db_connection()
        cur  = conn.cursor()
        try:
            cur.execute("""
              UPDATE kunjungan
                 SET kode_vaksin    = %s,
                     timestamp_akhir = date_trunc('second', now())
               WHERE id_kunjungan  = %s
                 AND no_dokter_hewan = %s
            """, (vaksin, kunjungan, no_dokter))
            conn.commit()
            messages.success(request, "Vaksinasi berhasil dibuat.")

            # ==== SESSION FIX ====
            email_val   = request.session.get('email')
            role_val    = request.session.get('role')
            pegawai_val = request.session.get('no_pegawai', None)

            request.session.cycle_key()
            request.session['email']      = email_val
            request.session['role']       = role_val
            if pegawai_val:
                request.session['no_pegawai'] = pegawai_val
            request.session.save()
            # ====================

            return redirect('merah:list_vaksinasi')

        except Exception as e:
            conn.rollback()
            messages.error(request, f'Gagal menambahkan vaksinasi: {e}')

            # Pastikan session tidak hilang
            request.session.modified = True
            return redirect('merah:add_vaksinasi')

        finally:
            cur.close()
            conn.close()

    # GET: render form
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
          SELECT id_kunjungan
            FROM kunjungan
           WHERE no_dokter_hewan = %s
             AND timestamp_akhir IS NULL
        """, (no_dokter,))
        kunjungan_options = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT kode, nama, stok FROM vaksin ORDER BY kode")
        vaksin_options = [
            {'kode_vaksin': r[0], 'nama_vaksin': r[1], 'stok': r[2]}
            for r in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/add_vaksinasi.html', {
        'kunjungan_options': kunjungan_options,
        'vaksin_options':    vaksin_options,
    })

@require_http_methods(['GET', 'POST'])
def update_vaksinasi(request, id_kunjungan):
    if request.session.get('role') != 'dokter_hewan':
        return HttpResponseForbidden("Hanya dokter hewan yang boleh akses.")
    no_dokter = request.session.get('no_pegawai')

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        if request.method == 'POST':
            vaksin = request.POST.get('kode_vaksin')

            try:
                cur.execute("""
                  UPDATE kunjungan
                     SET kode_vaksin = %s
                   WHERE id_kunjungan = %s
                     AND no_dokter_hewan = %s
                """, (vaksin, id_kunjungan, no_dokter))
                conn.commit()
                messages.success(request, "Vaksinasi berhasil diperbarui.")

                # ==== SESSION FIX ====
                email_val   = request.session.get('email')
                role_val    = request.session.get('role')
                pegawai_val = request.session.get('no_pegawai', None)

                request.session.cycle_key()
                request.session['email']      = email_val
                request.session['role']       = role_val
                if pegawai_val:
                    request.session['no_pegawai'] = pegawai_val
                request.session.save()
                # ====================

                return redirect('merah:list_vaksinasi')

            except Exception as e:
                conn.rollback()
                messages.error(request, f'Gagal memperbarui vaksinasi: {e}')
                request.session.modified = True
                return redirect('merah:update_vaksinasi', id_kunjungan=id_kunjungan)

        # GET → load current data
        cur.execute("""
          SELECT kode_vaksin
            FROM kunjungan
           WHERE id_kunjungan = %s
             AND no_dokter_hewan = %s
        """, (id_kunjungan, no_dokter))
        row = cur.fetchone()
        current_kode = row[0] if row else None

        cur.execute("SELECT kode, nama FROM vaksin ORDER BY kode")
        vaksin_options = [{'kode': r[0], 'nama': r[1]} for r in cur.fetchall()]

        return render(request, 'klinik/update_vaksinasi.html', {
            'id_kunjungan':    id_kunjungan,
            'current_kode':    current_kode,
            'vaksin_options':  vaksin_options,
        })

    finally:
        cur.close()
        conn.close()

@require_http_methods(['POST'])
def delete_vaksinasi(request, id_kunjungan):
    if request.session.get('role') != 'dokter_hewan':
        return HttpResponseForbidden("Hanya dokter hewan yang boleh akses.")
    no_dokter = request.session.get('no_pegawai')

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
          DELETE FROM kunjungan
           WHERE id_kunjungan = %s
             AND no_dokter_hewan = %s
        """, (id_kunjungan, no_dokter))
        conn.commit()
        messages.success(request, "Vaksinasi berhasil dihapus.")

        # ==== SESSION FIX ====
        email_val   = request.session.get('email')
        role_val    = request.session.get('role')
        pegawai_val = request.session.get('no_pegawai', None)

        request.session.cycle_key()
        request.session['email']      = email_val
        request.session['role']       = role_val
        if pegawai_val:
            request.session['no_pegawai'] = pegawai_val
        request.session.save()
        # ====================

        return redirect('merah:list_vaksinasi')

    except Exception as e:
        conn.rollback()
        messages.error(request, f'Gagal menghapus vaksinasi: {e}')
        request.session.modified = True
        return redirect('merah:list_vaksinasi')

    finally:
        cur.close()
        conn.close()

@require_http_methods(['GET'])
def list_vaksin_hewan(request):
    # 1) hanya Klien
    if request.session.get('role') not in ['individu', 'perusahaan']:
        return HttpResponseForbidden("Hanya klien yang boleh akses.")
    no_klien = request.session.get('no_identitas')
    if not no_klien:
        return HttpResponseForbidden("Session no_identitas belum diset.")

    pet_filter    = request.GET.get('pet', '').strip()
    vaksin_filter = request.GET.get('vaksin', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO petclinic;")

        # dropdown hewan klien
        cur.execute("""
            SELECT nama
              FROM hewan
             WHERE no_identitas_klien = %s
             ORDER BY nama
        """, [no_klien])
        pet_options = [r[0] for r in cur.fetchall()]

        # dropdown nama vaksin klien
        cur.execute("""
            SELECT DISTINCT v.nama
              FROM kunjungan k
              JOIN vaksin v ON v.kode = k.kode_vaksin
             WHERE k.no_identitas_klien = %s
               AND k.kode_vaksin IS NOT NULL
             ORDER BY v.nama
        """, [no_klien])
        vaksin_options = [r[0] for r in cur.fetchall()]

        # bangun WHERE
        wh = ["k.no_identitas_klien = %s", "k.kode_vaksin IS NOT NULL"]
        params = [no_klien]
        if pet_filter:
            wh.append("k.nama_hewan = %s"); params.append(pet_filter)
        if vaksin_filter:
            wh.append("v.nama = %s"); params.append(vaksin_filter)
        where_sql = " AND ".join(wh)

        # query data
        cur.execute(f"""
            SELECT k.id_kunjungan,
                   h.nama          AS pet,
                   v.nama          AS vaksin,
                   v.kode          AS kode_vaksin,
                   v.harga         AS harga,
                   to_char(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') AS waktu
              FROM kunjungan k
              JOIN hewan  h ON h.nama = k.nama_hewan
                           AND h.no_identitas_klien = k.no_identitas_klien
              JOIN vaksin v ON v.kode = k.kode_vaksin
             WHERE {where_sql}
             ORDER BY k.timestamp_awal DESC
        """, params)
        rows = cur.fetchall()

        vaksinasi_list = [{
            'id_kunjungan': r[0],
            'pet':          r[1],
            'vaksin':       r[2],
            'kode_vaksin':  r[3],
            'harga':        f"Rp{r[4]:,}".replace(",", "."),
            'waktu':        r[5],
        } for r in rows]

    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/list_vaksin_hewan.html', {
        'vaksinasi_list': vaksinasi_list,
        'pet_options':    pet_options,
        'vaksin_options': vaksin_options,
        'current_pet':    pet_filter,
        'current_vaksin': vaksin_filter,
    })

@require_http_methods(['GET'])
def list_vaksin(request):
    if request.session.get('role') != 'perawat_hewan': 
        return HttpResponseForbidden("Hanya perawathewan yang boleh akses.") 

    no_perawat = request.session.get('no_pegawai') 
    if not no_perawat: 
        return HttpResponseForbidden("Session no_pegawai belum diset.")
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SET search_path TO petclinic;")
        # semua vaksin, urut by waktu pembuatan (diasumsikan kolom timestamp dibuat auto)
        cur.execute("""
          SELECT kode, nama, harga, stok,
                 EXISTS( 
                  SELECT 1 FROM kunjungan k 
                    WHERE k.kode_vaksin = v.kode 
                 ) AS used 
            FROM vaksin v 
           ORDER BY v.kode DESC 
        """)
        rows = cur.fetchall()
        vaksin_list = []
        for kode, nama, harga, stok, used in rows:
            vaksin_list.append({
                'kode_vaksin': kode,
                'nama_vaksin': nama,
                'harga':       harga,
                'stok':        stok,
                'can_delete':  not used
            })
    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/list_vaksin.html', {
        'vaksin_list': vaksin_list
    })

@require_http_methods(['GET', 'POST'])
def add_vaksin(request):
    if request.session.get('role') != 'perawat_hewan':
        return HttpResponseForbidden("Hanya perawat hewan yang boleh akses.")
    no_perawat = request.session.get('no_pegawai')
    if not no_perawat:
        return HttpResponseForbidden("Session no_pegawai belum diset.")
    
    if request.method == 'POST':
        nama     = request.POST.get('nama_vaksin', '').strip()
        harga_str= request.POST.get('harga', '').strip()
        stok_str = request.POST.get('stok', '').strip()

        # Validasi input
        if not all([nama, harga_str, stok_str]):
            messages.error(request, "Semua field harus diisi.")
        else:
            try:
                harga = int(harga_str); stok = int(stok_str)
                if harga < 0 or stok < 0:
                    messages.error(request, "Harga dan stok tidak boleh negatif.")
                else:
                    conn = get_db_connection()
                    cur  = conn.cursor()
                    try:
                        # generate kode otomatis
                        cur.execute("SELECT MAX(kode) FROM vaksin")
                        row = cur.fetchone()[0]
                        if row and row.startswith('VAK'):
                            seq = int(row.replace('VAK','')) + 1
                        else:
                            seq = 1
                        kode = f"VAK{seq:03d}"

                        cur.execute(
                          "INSERT INTO vaksin(kode, nama, harga, stok) VALUES (%s,%s,%s,%s)",
                          (kode, nama, harga, stok)
                        )
                        conn.commit()
                        messages.success(request, f"Vaksin {kode} berhasil ditambahkan.")

                        # ==== SESSION FIX ====
                        email_val   = request.session.get('email')
                        role_val    = request.session.get('role')
                        pegawai_val = request.session.get('no_pegawai')

                        request.session.cycle_key()
                        request.session['email']      = email_val
                        request.session['role']       = role_val
                        request.session['no_pegawai'] = pegawai_val
                        request.session.save()
                        # ====================

                        return redirect('merah:list_vaksin')

                    except Exception as e:
                        conn.rollback()
                        messages.error(request, str(e))
                    finally:
                        cur.close()
                        conn.close()
            except ValueError:
                messages.error(request, "Harga dan stok harus berupa angka.")

        # POST-error: pastikan session tetap dipertahankan
        request.session.modified = True

    # GET: tampilkan form
    return render(request, 'klinik/add_vaksin.html')

@require_http_methods(['GET', 'POST'])
def update_vaksin(request, kode_vaksin):
    if request.session.get('role') != 'perawat_hewan':
        return HttpResponseForbidden("Hanya perawat hewan yang boleh akses.")
    no_perawat = request.session.get('no_pegawai')
    if not no_perawat:
        return HttpResponseForbidden("Session no_pegawai belum diset.")

    conn = get_db_connection()
    cur  = conn.cursor()
    vaksin = None
    try:
        # Load existing
        cur.execute("SELECT kode, nama, harga, stok FROM vaksin WHERE kode = %s", [kode_vaksin])
        row = cur.fetchone()
        if not row:
            raise Http404
        vaksin = {'kode_vaksin': row[0], 'nama_vaksin': row[1], 'harga': row[2], 'stok': row[3]}

        if request.method == 'POST':
            nama_str  = request.POST.get('nama_vaksin', '').strip()
            harga_str = request.POST.get('harga', '').strip()
            stok_str  = request.POST.get('stok', '').strip()

            if not all([nama_str, harga_str, stok_str]):
                messages.error(request, "Semua field harus diisi.")
            else:
                try:
                    harga = int(harga_str); stok = int(stok_str)
                    if harga < 0 or stok < 0:
                        messages.error(request, "Harga dan stok tidak boleh negatif.")
                    else:
                        cur.execute(
                          "UPDATE vaksin SET nama = %s, harga = %s, stok = %s WHERE kode = %s",
                          (nama_str, harga, stok, kode_vaksin)
                        )
                        conn.commit()
                        messages.success(request, f"Vaksin {kode_vaksin} berhasil diperbarui.")

                        # ==== SESSION FIX ====
                        email_val   = request.session.get('email')
                        role_val    = request.session.get('role')
                        pegawai_val = request.session.get('no_pegawai')

                        request.session.cycle_key()
                        request.session['email']      = email_val
                        request.session['role']       = role_val
                        request.session['no_pegawai'] = pegawai_val
                        request.session.save()
                        # ====================

                        return redirect('merah:list_vaksin')

                except ValueError:
                    messages.error(request, "Harga dan stok harus berupa angka.")
                except Exception as e:
                    conn.rollback()
                    messages.error(request, str(e))

            # POST-error: pertahankan session
            request.session.modified = True

    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/update_vaksin.html', {'vaksin': vaksin})

@require_http_methods(['GET', 'POST'])
def update_stok_vaksin(request, kode_vaksin):
    if request.session.get('role') != 'perawat_hewan':
        return HttpResponseForbidden("Hanya perawat hewan yang boleh akses.")
    no_perawat = request.session.get('no_pegawai')
    if not no_perawat:
        return HttpResponseForbidden("Session no_pegawai belum diset.")

    conn = get_db_connection()
    cur  = conn.cursor()
    vaksin = None
    try:
        # Load data vaksin
        cur.execute("SELECT kode, nama, stok FROM vaksin WHERE kode=%s", [kode_vaksin])
        row = cur.fetchone()
        if not row:
            raise Http404
        vaksin = {'kode_vaksin': row[0], 'nama_vaksin': row[1], 'stok': row[2]}

        if request.method == 'POST':
            stok_str = request.POST.get('stok', '').strip()

            if not stok_str:
                messages.error(request, "Stok harus diisi.")
            else:
                try:
                    stok = int(stok_str)
                    if stok < 0:
                        messages.error(request, "Stok tidak boleh negatif.")
                    else:
                        cur.execute(
                            "UPDATE vaksin SET stok = %s WHERE kode = %s",
                            (stok, kode_vaksin)
                        )
                        conn.commit()
                        messages.success(request, f"Stok vaksin {kode_vaksin} diubah menjadi {stok}.")

                        # ==== SESSION FIX ====
                        email_val   = request.session.get('email')
                        role_val    = request.session.get('role')
                        pegawai_val = request.session.get('no_pegawai')

                        request.session.cycle_key()
                        request.session['email']      = email_val
                        request.session['role']       = role_val
                        request.session['no_pegawai'] = pegawai_val
                        request.session.save()
                        # ====================

                        return redirect('merah:list_vaksin')

                except ValueError:
                    messages.error(request, "Stok harus berupa angka.")
                except Exception as e:
                    conn.rollback()
                    messages.error(request, str(e))

            # Jika ada error di POST, pertahankan session
            request.session.modified = True

    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/update_stock.html', {'vaksin': vaksin})

@require_http_methods(['POST'])
def delete_vaksin(request, kode_vaksin):
    if request.session.get('role') != 'perawat_hewan':
        return HttpResponseForbidden("Hanya perawat hewan yang boleh akses.")
    no_perawat = request.session.get('no_pegawai')
    if not no_perawat:
        return HttpResponseForbidden("Session no_pegawai belum diset.")

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("DELETE FROM vaksin WHERE kode = %s", [kode_vaksin])
        conn.commit()
        messages.success(request, f"Vaksin {kode_vaksin} berhasil dihapus.")

        # ==== SESSION FIX ====
        email_val   = request.session.get('email')
        role_val    = request.session.get('role')
        pegawai_val = request.session.get('no_pegawai')

        request.session.cycle_key()
        request.session['email']      = email_val
        request.session['role']       = role_val
        request.session['no_pegawai'] = pegawai_val
        request.session.save()
        # ====================

    except Exception as e:
        conn.rollback()
        messages.error(request, str(e))
        # Jika error, jangan hilangkan session
        request.session.modified = True
    finally:
        cur.close()
        conn.close()

    return redirect('merah:list_vaksin')
@require_http_methods(['GET'])
def list_klien(request):
    role = request.session.get('role') 
    no_identitas = request.session.get('no_identitas')
    # DEBUG: Print session info
    print(f"DEBUG - Role: {role}")
    print(f"DEBUG - No Identitas: {no_identitas}")
    if role in ['perusahaan', 'individu']:
        if no_identitas:
            return redirect('merah:detail_klien', client_id=no_identitas)
        else:
            return HttpResponseForbidden("Session tidak valid - no identitas tidak ditemukan.")
    
    # 1) Akses hanya Front-Desk Officer
    if request.session.get('role') not in ['individu', 'klien', 'front_desk']:
        return HttpResponseForbidden("Hanya Front-Desk Officer atau  Klien yang boleh akses.")

    search_query = request.GET.get('search', '').strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO petclinic;")
        cur.execute("""
            SELECT
              k.no_identitas,
              u.email,
              CASE
                WHEN i.no_identitas_klien IS NOT NULL
                  THEN concat(i.nama_depan, ' ',
                              coalesce(i.nama_tengah,''), ' ',
                              i.nama_belakang)
                ELSE p.nama_perusahaan
              END AS nama,
              CASE
                WHEN i.no_identitas_klien IS NOT NULL THEN 'Individu'
                ELSE 'Perusahaan'
              END AS jenis
            FROM klien k
            JOIN "USER" u ON u.email = k.email
            LEFT JOIN individu i ON i.no_identitas_klien = k.no_identitas
            LEFT JOIN perusahaan p ON p.no_identitas_klien = k.no_identitas
            WHERE
              (%s = ''
               OR lower(u.email) LIKE '%%' || %s || '%%'
               OR lower(
                    CASE
                      WHEN i.no_identitas_klien IS NOT NULL
                        THEN concat(i.nama_depan,' ',coalesce(i.nama_tengah,''),' ',i.nama_belakang)
                      ELSE p.nama_perusahaan
                    END
                 ) LIKE '%%' || %s || '%%')
            ORDER BY u.email
        """, [search_query, search_query, search_query])

        rows = cur.fetchall()
        clients = [{
            'no_identitas': r[0],
            'email':        r[1],
            'nama':         r[2].strip(),
            'jenis':        r[3]
        } for r in rows]
    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/list_klien.html', {
        'clients':      clients,
        'search_query': request.GET.get('search', '')
    })

@require_http_methods(['GET'])
def detail_klien(request, client_id):
    role = request.session.get('role')

    # 1) Jika Klien: hanya boleh lihat detail dirinya sendiri
    if role in ['individu', 'perusahaan']:  # Ubah dari 'klien' ke ['individu', 'perusahaan']
        no_klien = request.session.get('no_identitas')  # Ubah dari 'no_identitas_klien' ke 'no_identitas'
        print(f"DEBUG detail_klien - No klien from session: {no_klien}")
        
        if not no_klien or str(client_id) != str(no_klien):
            return HttpResponseForbidden("Anda hanya boleh melihat data Anda sendiri.")

    # 2) Front-Desk boleh lihat semua
    elif role != 'front_desk':
        return HttpResponseForbidden("Hanya Klien atau Front-Desk Officer yang boleh akses.")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO petclinic;")
        # ambil data klien
        cur.execute("""
            SELECT
              k.no_identitas,
              u.email,
              i.nama_depan, i.nama_tengah, i.nama_belakang,
              p.nama_perusahaan,
              u.alamat,
              u.nomor_telepon
            FROM klien k
            JOIN "USER" u ON u.email = k.email
            LEFT JOIN individu i ON i.no_identitas_klien = k.no_identitas
            LEFT JOIN perusahaan p ON p.no_identitas_klien = k.no_identitas
            WHERE k.no_identitas = %s
        """, [client_id])
        row = cur.fetchone()
        if not row:
            return render(request, '404.html', status=404)

        # unpack
        no_id, email, nd, nt, nb, np, alamat, telepon = row
        if nd:  # individu
            nama_lengkap = f"{nd} {nt or ''} {nb}".strip()
            jenis = 'Individu'
            nama_perusahaan = ''
        else:
            nama_lengkap = ''
            jenis = 'Perusahaan'
            nama_perusahaan = np

        client = {
            'nomor_identitas':   no_id,
            'email':             email,
            'jenis':             jenis,
            'nama_lengkap':      nama_lengkap,
            'nama_perusahaan':   nama_perusahaan,
            'alamat':            alamat,
            'telepon':           telepon,
        }

        # ambil hewan
        cur.execute("""
            SELECT
              h.nama,
              j.nama_jenis,
              to_char(h.tanggal_lahir, 'YYYY-MM-DD')
            FROM hewan h
            JOIN jenis_hewan j ON j.id = h.id_jenis
            WHERE h.no_identitas_klien = %s
            ORDER BY h.nama
        """, [client_id])

        pets = [{
            'nama':          r[0],
            'jenis':         r[1],
            'tanggal_lahir': r[2]
        } for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

    return render(request, 'klinik/detail_klien.html', {
        'client': client,
        'pets':   pets
    })

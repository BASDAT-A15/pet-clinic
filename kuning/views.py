from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from utils.db_utils import get_db_connection
import uuid

def list_jenis_hewan(request):
    if request.session.get('role') not in ['dokter_hewan', 'front_desk']:
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    
    role = request.session.get('role', '')  
    
    if request.method == 'POST' and 'namaJenis' in request.POST and role == 'front_desk':
        nama_jenis = request.POST.get('namaJenis', '').strip()
        
        if not nama_jenis:
            messages.error(request, 'Nama jenis hewan tidak boleh kosong.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            
            try:
                id_jenis = str(uuid.uuid4())
                
                cur.execute(
                    "INSERT INTO JENIS_HEWAN (id, nama_jenis) VALUES (%s, %s)",
                    (id_jenis, nama_jenis)
                )
                conn.commit()
                
                messages.success(request, f'Jenis hewan {nama_jenis} berhasil ditambahkan.')
            except Exception as e:
                conn.rollback()
                full_msg  = str(e)
                clean_msg = full_msg.split('CONTEXT')[0].strip()
                messages.error(request, clean_msg)
            finally:
                cur.close()
                conn.close()
                
    elif request.method == 'POST' and 'updateIdJenis' in request.POST and role == 'front_desk':
        id_jenis = request.POST.get('updateIdJenis', '')
        nama_jenis = request.POST.get('updateNamaJenis', '').strip()
        
        if not nama_jenis:
            messages.error(request, 'Nama jenis hewan tidak boleh kosong.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            
            try:
                cur.execute(
                    "UPDATE JENIS_HEWAN SET nama_jenis = %s WHERE id = %s",
                    (nama_jenis, id_jenis)
                )
                conn.commit()
                
                messages.success(request, f'Jenis hewan berhasil diperbarui menjadi {nama_jenis}.')
            except Exception as e:
                conn.rollback()
                messages.error(request, f'Gagal memperbarui jenis hewan: {str(e)}')
            finally:
                cur.close()
                conn.close()
                
    elif request.method == 'POST' and 'id_jenis' in request.POST and role == 'front_desk':
        id_jenis = request.POST.get('id_jenis', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "DELETE FROM JENIS_HEWAN WHERE id = %s",
                (id_jenis,)
            )
            conn.commit()
            
            messages.success(request, 'Jenis hewan berhasil dihapus.')
        except Exception as e:
            conn.rollback()
            messages.error(request, f'Gagal menghapus jenis hewan: {str(e)}')
        finally:
            cur.close()
            conn.close()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, nama_jenis FROM JENIS_HEWAN ORDER BY id ASC")
        jenis_hewan_data = cur.fetchall()
        
        cur.execute("""
            SELECT id_jenis 
            FROM HEWAN
            GROUP BY id_jenis
        """)
        used_types = [row[0] for row in cur.fetchall()]
        
        jenis_hewan = []
        for i, (id_jenis, nama_jenis) in enumerate(jenis_hewan_data, 1):
            jenis_hewan.append({
                'no': i,
                'id_jenis': id_jenis, 
                'nama_jenis': nama_jenis
            })
        
        return render(request, 'jenis-hewan/list.html', {
            'jenis_hewan': jenis_hewan,
            'role': role,
            'used_types': used_types  
        })
    finally:
        cur.close()
        conn.close()

def list_hewan(request):
    if request.session.get('role') not in ['individu', 'perusahaan', 'front_desk']:
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    
    role = request.session.get('role', '')
    user_id = request.session.get('no_identitas', '')
    
    if request.method == 'POST':
        if 'namaHewan' in request.POST and ('pemilik' in request.POST or role == 'individu' or role == 'perusahaan'):
            nama_hewan = request.POST.get('namaHewan', '').strip()
            tanggal_lahir = request.POST.get('tanggalLahir', '').strip()
            jenis_hewan = request.POST.get('jenisHewan', '').strip()
            url_foto = request.POST.get('urlFoto', '').strip()
            
            no_identitas_klien = request.POST.get('pemilik', user_id) if role == 'front_desk' else user_id
            
            if not nama_hewan or not tanggal_lahir or not jenis_hewan or not url_foto:
                messages.error(request, 'Semua field harus diisi.')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    parts = tanggal_lahir.split('-')
                    if len(parts) == 3:
                        tanggal_lahir_db = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:
                        tanggal_lahir_db = tanggal_lahir
                    
                    cur.execute(
                        "INSERT INTO HEWAN (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES (%s, %s, %s, %s, %s)",
                        (nama_hewan, no_identitas_klien, tanggal_lahir_db, jenis_hewan, url_foto)
                    )
                    conn.commit()
                    
                    messages.success(request, f'Hewan peliharaan {nama_hewan} berhasil ditambahkan.')
                except Exception as e:
                    conn.rollback()
                    messages.error(request, f'Gagal menambahkan hewan peliharaan: {str(e)}')
                finally:
                    cur.close()
                    conn.close()
        
        elif 'hewan_id' in request.POST and 'updateNamaHewan' in request.POST:
            hewan_id = request.POST.get('hewan_id', '').strip()
            nama_hewan = request.POST.get('updateNamaHewan', '').strip()
            tanggal_lahir = request.POST.get('updateTanggalLahir', '').strip()
            jenis_hewan = request.POST.get('updateJenisHewan', '').strip()
            url_foto = request.POST.get('updateUrlFoto', '').strip()
            
            no_identitas_klien = request.POST.get('updatePemilik', None)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            try:
                if role == 'individu' or role == 'perusahaan':
                    cur.execute(
                        "SELECT COUNT(*) FROM HEWAN WHERE nama = %s AND no_identitas_klien = %s",
                        (hewan_id, user_id)
                    )
                    count = cur.fetchone()[0]
                    if count == 0:
                        messages.error(request, 'Anda tidak memiliki akses untuk mengubah data hewan ini.')
                        cur.close()
                        conn.close()
                        return redirect('kuning:list_hewan')
                
                parts = tanggal_lahir.split('-')
                if len(parts) == 3:
                    tanggal_lahir_db = f"{parts[2]}-{parts[1]}-{parts[0]}"
                else:
                    tanggal_lahir_db = tanggal_lahir
                
                if role == 'front_desk' and no_identitas_klien:
                    cur.execute(
                        "UPDATE HEWAN SET nama = %s, id_jenis = %s, tanggal_lahir = %s, url_foto = %s, no_identitas_klien = %s WHERE nama = %s",
                        (nama_hewan, jenis_hewan, tanggal_lahir_db, url_foto, no_identitas_klien, hewan_id)
                    )
                else:
                    cur.execute(
                        "UPDATE HEWAN SET nama = %s, id_jenis = %s, tanggal_lahir = %s, url_foto = %s WHERE nama = %s",
                        (nama_hewan, jenis_hewan, tanggal_lahir_db, url_foto, hewan_id)
                    )
                
                conn.commit()
                messages.success(request, f'Data hewan {nama_hewan} berhasil diperbarui.')
            except Exception as e:
                conn.rollback()
                messages.error(request, f'Gagal memperbarui data hewan: {str(e)}')
            finally:
                cur.close()
                conn.close()
        
        elif 'deleteHewanId' in request.POST and role == 'front_desk':
            hewan_id = request.POST.get('deleteHewanId', '').strip()
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            try:
                cur.execute("DELETE FROM HEWAN WHERE nama = %s", (hewan_id,))
                conn.commit()
                messages.success(request, f'Data hewan {hewan_id} berhasil dihapus.')
            except Exception as e:
                conn.rollback()
                full_msg = str(e)
                clean_msg = full_msg.split('CONTEXT')[0].strip()
                messages.error(request, clean_msg)
            finally:
                cur.close()
                conn.close()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if role == 'individu' or role == 'perusahaan':
            cur.execute("""
                SELECT h.nama, i.nama_depan, i.nama_tengah, i.nama_belakang, 
                       p.nama_perusahaan, j.nama_jenis, 
                       h.tanggal_lahir, h.url_foto, h.id_jenis
                FROM HEWAN h
                JOIN KLIEN k ON h.no_identitas_klien = k.no_identitas
                LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
                LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
                JOIN JENIS_HEWAN j ON h.id_jenis = j.id
                WHERE h.no_identitas_klien = %s
                ORDER BY 
                    CASE 
                        WHEN i.nama_depan IS NOT NULL THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah, ''), ' ', i.nama_belakang)
                        ELSE p.nama_perusahaan
                    END ASC,
                    j.nama_jenis ASC,
                    h.nama ASC
            """, (user_id,))
        else:
            cur.execute("""
                SELECT h.nama, i.nama_depan, i.nama_tengah, i.nama_belakang, 
                       p.nama_perusahaan, j.nama_jenis, 
                       h.tanggal_lahir, h.url_foto, h.no_identitas_klien, h.id_jenis
                FROM HEWAN h
                JOIN KLIEN k ON h.no_identitas_klien = k.no_identitas
                LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
                LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
                JOIN JENIS_HEWAN j ON h.id_jenis = j.id
                ORDER BY 
                    CASE 
                        WHEN i.nama_depan IS NOT NULL THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah, ''), ' ', i.nama_belakang)
                        ELSE p.nama_perusahaan
                    END ASC,
                    j.nama_jenis ASC,
                    h.nama ASC
            """)
        
        hewan_data = cur.fetchall()
        
        # Remove the old active_visits query - we'll check each animal individually
        
        cur.execute("""
            SELECT k.no_identitas, 
                   CASE 
                       WHEN i.nama_depan IS NOT NULL THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah, ''), ' ', i.nama_belakang)
                       ELSE p.nama_perusahaan
                   END as nama
            FROM KLIEN k
            LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            ORDER BY nama ASC
        """)
        client_list = cur.fetchall()
        
        cur.execute("SELECT id, nama_jenis FROM JENIS_HEWAN ORDER BY nama_jenis ASC")
        jenis_hewan_list = cur.fetchall()
        
        daftar_hewan = []
        for row in hewan_data:
            if role == 'individu' or role == 'perusahaan':
                nama, nama_depan, nama_tengah, nama_belakang, nama_perusahaan, jenis_hewan, tanggal_lahir, url_foto, id_jenis = row
                no_identitas_klien = user_id  
            else:
                nama, nama_depan, nama_tengah, nama_belakang, nama_perusahaan, jenis_hewan, tanggal_lahir, url_foto, no_identitas_klien, id_jenis = row
            
            tanggal_formatted = tanggal_lahir.strftime('%d-%m-%Y') if tanggal_lahir else ''
            
            if nama_depan:
                if nama_tengah:
                    pemilik = f"{nama_depan} {nama_tengah} {nama_belakang}"
                else:
                    pemilik = f"{nama_depan} {nama_belakang}"
            else:
                pemilik = nama_perusahaan
            
            # Direct check for each animal if it has active visits
            cur.execute("""
                SELECT COUNT(*) 
                FROM KUNJUNGAN 
                WHERE nama_hewan = %s AND 
                (timestamp_akhir IS NULL OR timestamp_akhir > NOW())
            """, (nama,))
            has_active_visits = cur.fetchone()[0] > 0
            
            hewan_item = {
                'id': nama,
                'pemilik': pemilik,
                'jenis_hewan': jenis_hewan,
                'nama': nama,
                'tanggal_lahir': tanggal_formatted,
                'tanggal_lahir_formatted': tanggal_formatted,
                'url_foto': url_foto,
                'no_identitas_klien': no_identitas_klien,
                'id_jenis': id_jenis,
                'can_delete': not has_active_visits  # Direct check result
            }
            
            daftar_hewan.append(hewan_item)
        
        return render(request, 'daftar-hewan/list_hewan.html', {
            'daftar_hewan': daftar_hewan,
            'role': role,
            'client_list': client_list,
            'jenis_hewan_list': jenis_hewan_list
        })
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return render(request, 'daftar-hewan/list_hewan.html', {
            'daftar_hewan': [],
            'role': role
        })
    finally:
        cur.close()
        conn.close()
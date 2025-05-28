from django.shortcuts import render, redirect
from django.contrib import messages
from utils.db_utils import get_db_connection
from datetime import datetime

# PERAWATAN HEWAN (Animal Treatment) functions

# Function to list all treatments
def list_perawatan(request):
    conn = None
    cur = None
    treatments = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user role from session
        role = request.session.get('role')
        email = request.session.get('email')
        
        # If user is a klien (client), only show treatments for their animals
        if role == 'individu' or role == 'perusahaan':
            # Get the client's ID
            cur.execute(
                'SELECT no_identitas FROM KLIEN WHERE email = %s',
                (email,)
            )
            client_id = cur.fetchone()[0]
              # Get treatments for client's animals
            cur.execute('''
                SELECT kk.id_kunjungan, k.no_identitas_klien, h.nama, 
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_perawat_hewan LIMIT 1) as perawat,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_dokter_hewan LIMIT 1) as dokter,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_front_desk LIMIT 1) as front_desk,
                       p.kode_perawatan || ' - ' || p.nama_perawatan as jenis_perawatan,
                       kk.catatan
                FROM KUNJUNGAN_KEPERAWATAN kk
                JOIN KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan 
                                 AND kk.nama_hewan = k.nama_hewan 
                                 AND kk.no_identitas_klien = k.no_identitas_klien
                JOIN HEWAN h ON h.nama = k.nama_hewan AND h.no_identitas_klien = k.no_identitas_klien
                JOIN PERAWATAN p ON p.kode_perawatan = kk.kode_perawatan
                WHERE k.no_identitas_klien = %s
                ORDER BY k.timestamp_awal DESC
            ''', (client_id,))
            
        # If user is a dokter hewan (veterinarian)
        elif role == 'dokter_hewan':
            # Get the doctor's ID
            cur.execute(
                'SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s',
                (email,)
            )
            doctor_id = cur.fetchone()[0]
              # Get treatments for animals treated by this doctor
            cur.execute('''
                SELECT kk.id_kunjungan, k.no_identitas_klien, h.nama, 
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_perawat_hewan LIMIT 1) as perawat,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_dokter_hewan LIMIT 1) as dokter,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_front_desk LIMIT 1) as front_desk,
                       p.kode_perawatan || ' - ' || p.nama_perawatan as jenis_perawatan,
                       kk.catatan
                FROM KUNJUNGAN_KEPERAWATAN kk
                JOIN KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan 
                                 AND kk.nama_hewan = k.nama_hewan 
                                 AND kk.no_identitas_klien = k.no_identitas_klien
                JOIN HEWAN h ON h.nama = k.nama_hewan AND h.no_identitas_klien = k.no_identitas_klien
                JOIN PERAWATAN p ON p.kode_perawatan = kk.kode_perawatan
                WHERE k.no_dokter_hewan = %s
                ORDER BY k.timestamp_awal DESC
            ''', (doctor_id,))
            
        # For all other staff (perawat, front desk)
        else:            # Get all treatments
            cur.execute('''
                SELECT kk.id_kunjungan, k.no_identitas_klien, h.nama, 
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_perawat_hewan LIMIT 1) as perawat,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_dokter_hewan LIMIT 1) as dokter,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_front_desk LIMIT 1) as front_desk,
                       p.kode_perawatan || ' - ' || p.nama_perawatan as jenis_perawatan,
                       kk.catatan
                FROM KUNJUNGAN_KEPERAWATAN kk
                JOIN KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan 
                                 AND kk.nama_hewan = k.nama_hewan 
                                 AND kk.no_identitas_klien = k.no_identitas_klien
                JOIN HEWAN h ON h.nama = k.nama_hewan AND h.no_identitas_klien = k.no_identitas_klien
                JOIN PERAWATAN p ON p.kode_perawatan = kk.kode_perawatan
                ORDER BY k.timestamp_awal DESC
            ''')
        
        rows = cur.fetchall()
        for i, row in enumerate(rows, start=1):
            # Format email addresses for display
            perawat_email = row[3]
            dokter_email = row[4]
            front_desk_email = row[5]
            
            # Format doctor email with "dr." prefix
            formatted_dokter = f"dr. {dokter_email}" if dokter_email else "-"
            
            # Capitalize first letter of other emails
            formatted_perawat = perawat_email.capitalize() if perawat_email else "-"
            formatted_front_desk = front_desk_email.capitalize() if front_desk_email else "-"
            
            treatments.append({
                'no': i,
                'id_kunjungan': row[0],
                'id_klien': row[1],
                'nama_hewan': row[2],
                'perawat_hewan': formatted_perawat,
                'dokter_hewan': formatted_dokter,
                'front_desk_officer': formatted_front_desk,
                'jenis_perawatan': row[6],
                'catatan_medis': row[7] or "-"
            })
    
    except Exception as error:
        print(f"Error in list_perawatan: {error}")
        messages.error(request, f"Terjadi kesalahan: {error}")
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render(request, 'list_perawatan.html', {'treatments': treatments})

# Function to create a new treatment
def create_perawatan(request):
    conn = None
    cur = None
    
    # Check if user is authorized (must be a doctor)
    role = request.session.get('role')
    if role != 'dokter_hewan':
        messages.error(request, "Anda tidak memiliki izin untuk membuat perawatan")
        return redirect('hijau:list_perawatan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            id_kunjungan = request.POST.get('kunjungan')
            jenis_perawatan = request.POST.get('jenis_perawatan')
            catatan_medis = request.POST.get('catatan_medis', '')
            
            # Input validation
            if not id_kunjungan or not jenis_perawatan:
                messages.error(request, "Kunjungan dan jenis perawatan harus diisi")
                return redirect('hijau:create_perawatan')
            
            # Get the kunjungan details
            cur.execute('''
                SELECT nama_hewan, no_identitas_klien, no_front_desk, 
                       no_perawat_hewan, no_dokter_hewan
                FROM KUNJUNGAN 
                WHERE id_kunjungan = %s
            ''', (id_kunjungan,))
            
            kunjungan_data = cur.fetchone()
            if not kunjungan_data:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:create_perawatan')
            nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan = kunjungan_data
            
            # Create the treatment record in KUNJUNGAN_KEPERAWATAN
            cur.execute('''
                INSERT INTO KUNJUNGAN_KEPERAWATAN(
                    id_kunjungan, nama_hewan, no_identitas_klien, 
                    no_front_desk, no_perawat_hewan, no_dokter_hewan,
                    kode_perawatan, catatan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                id_kunjungan, 
                nama_hewan, 
                no_identitas_klien, 
                no_front_desk, 
                no_perawat_hewan, 
                no_dokter_hewan, 
                jenis_perawatan,
                catatan_medis
            ))
            
            conn.commit()
            messages.success(request, "Perawatan berhasil dibuat")
            return redirect('hijau:list_perawatan')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in create_perawatan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:create_perawatan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request (display form)
    else:
        # Fetch data for dropdowns
        client_list = []
        doctor_list = []
        nurse_list = []
        animal_list = []
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get clients (both individuals and companies)
            cur.execute('''
                SELECT k.no_identitas, i.nama_depan || ' ' || i.nama_belakang as nama
                FROM KLIEN k
                JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
                UNION
                SELECT k.no_identitas, p.nama_perusahaan as nama
                FROM KLIEN k
                JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
                ORDER BY nama
            ''')
            
            for row in cur.fetchall():
                client_list.append({
                    'id': row[0],
                    'name': row[1]
                })
            
            # Get doctors
            cur.execute('''
                SELECT p.no_pegawai, u.email
                FROM PEGAWAI p
                JOIN "USER" u ON p.email_user = u.email
                JOIN DOKTER_HEWAN d ON p.no_pegawai = d.no_dokter_hewan
                ORDER BY u.email
            ''')
            
            for row in cur.fetchall():
                doctor_list.append({
                    'id': row[0],
                    'email': row[1]
                })
            
            # Get nurses
            cur.execute('''
                SELECT p.no_pegawai, u.email
                FROM PEGAWAI p
                JOIN "USER" u ON p.email_user = u.email
                JOIN PERAWAT_HEWAN pw ON p.no_pegawai = pw.no_perawat_hewan
                ORDER BY u.email
            ''')
            
            for row in cur.fetchall():
                nurse_list.append({
                    'id': row[0],
                    'email': row[1]
                })
            
            # Get animals (will be filtered by client selection in the frontend)
            cur.execute('''
                SELECT h.nama, h.no_identitas_klien
                FROM HEWAN h
                ORDER BY h.nama
            ''')
            
            for row in cur.fetchall():
                animal_list.append({
                    'name': row[0],
                    'client_id': row[1]
                })
                
        except Exception as error:
            print(f"Error fetching data for create_kunjungan form: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        context = {
            'client_list': client_list,
            'doctor_list': doctor_list,
            'nurse_list': nurse_list,
            'animal_list': animal_list
        }
        
        return render(request, 'create_kunjungan.html', context)

# Function to update a visit
def update_kunjungan(request):
    # Check if user is authorized (must be front desk)
    role = request.session.get('role')
    if role != 'front_desk':
        messages.error(request, "Anda tidak memiliki izin untuk mengubah kunjungan")
        return redirect('hijau:list_kunjungan')
    
    # Get the visit ID from query parameters
    id_kunjungan = request.GET.get('id')
    
    if not id_kunjungan:
        messages.error(request, "ID Kunjungan diperlukan")
        return redirect('hijau:list_kunjungan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            client_id = request.POST.get('clientId')
            nama_hewan = request.POST.get('animalName')
            dokter_email = request.POST.get('doctor')
            perawat_email = request.POST.get('nurse')
            tipe_kunjungan = request.POST.get('visitMethod')
            timestamp_awal = request.POST.get('startTime')
            timestamp_akhir = request.POST.get('endTime') or None
            
            # Get doctor ID from email
            cur.execute(
                'SELECT p.no_pegawai FROM PEGAWAI p JOIN "USER" u ON p.email_user = u.email WHERE u.email = %s',
                (dokter_email,)
            )
            doctor_result = cur.fetchone()
            if not doctor_result:
                messages.error(request, f"Dokter dengan email {dokter_email} tidak ditemukan")
                return redirect(f'hijau:update_kunjungan?id={id_kunjungan}')
            doctor_id = doctor_result[0]
            
            # Get nurse ID from email
            cur.execute(
                'SELECT p.no_pegawai FROM PEGAWAI p JOIN "USER" u ON p.email_user = u.email WHERE u.email = %s',
                (perawat_email,)
            )
            nurse_result = cur.fetchone()
            if not nurse_result:
                messages.error(request, f"Perawat dengan email {perawat_email} tidak ditemukan")
                return redirect(f'hijau:update_kunjungan?id={id_kunjungan}')
            nurse_id = nurse_result[0]
            
            # Update the visit record
            cur.execute('''
                UPDATE KUNJUNGAN
                SET nama_hewan = %s, 
                    no_identitas_klien = %s,
                    no_dokter_hewan = %s,
                    no_perawat_hewan = %s,
                    tipe_kunjungan = %s,
                    timestamp_awal = %s,
                    timestamp_akhir = %s
                WHERE id_kunjungan = %s
            ''', (
                nama_hewan,
                client_id,
                doctor_id,
                nurse_id,
                tipe_kunjungan,
                timestamp_awal,
                timestamp_akhir,
                id_kunjungan
            ))
            
            if cur.rowcount == 0:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            conn.commit()
            messages.success(request, "Kunjungan berhasil diperbarui")
            return redirect('hijau:list_kunjungan')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in update_kunjungan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect(f'hijau:update_kunjungan?id={id_kunjungan}')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request (display form)
    else:
        visit_data = {}
        client_list = []
        doctor_list = []
        nurse_list = []
        animal_list = []
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get visit data
            cur.execute('''
                SELECT k.no_identitas_klien, k.nama_hewan, 
                       k.no_dokter_hewan, k.no_perawat_hewan, 
                       k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_dokter_hewan) as dokter_email,
                       (SELECT email FROM "USER" u JOIN PEGAWAI p ON u.email = p.email_user 
                        WHERE p.no_pegawai = k.no_perawat_hewan) as perawat_email
                FROM KUNJUNGAN k
                WHERE k.id_kunjungan = %s
            ''', (id_kunjungan,))
            
            row = cur.fetchone()
            if not row:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            # Format timestamps for the form
            timestamp_awal_str = row[5].strftime('%Y-%m-%dT%H:%M:%S') if row[5] else ''
            timestamp_akhir_str = row[6].strftime('%Y-%m-%dT%H:%M:%S') if row[6] else ''
            
            visit_data = {
                'id_kunjungan': id_kunjungan,
                'client_id': row[0],
                'nama_hewan': row[1],
                'doctor_id': row[2],
                'nurse_id': row[3],
                'tipe_kunjungan': row[4],
                'timestamp_awal': timestamp_awal_str,
                'timestamp_akhir': timestamp_akhir_str,
                'dokter_email': row[7],
                'perawat_email': row[8]
            }
            
            # Get clients (both individuals and companies)
            cur.execute('''
                SELECT k.no_identitas, i.nama_depan || ' ' || i.nama_belakang as nama
                FROM KLIEN k
                JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
                UNION
                SELECT k.no_identitas, p.nama_perusahaan as nama
                FROM KLIEN k
                JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
                ORDER BY nama
            ''')
            
            for row in cur.fetchall():
                client_list.append({
                    'id': row[0],
                    'name': row[1],
                    'selected': str(row[0]) == str(visit_data['client_id'])
                })
            
            # Get doctors
            cur.execute('''
                SELECT p.no_pegawai, u.email
                FROM PEGAWAI p
                JOIN "USER" u ON p.email_user = u.email
                JOIN DOKTER_HEWAN d ON p.no_pegawai = d.no_dokter_hewan
                ORDER BY u.email
            ''')
            
            for row in cur.fetchall():
                doctor_list.append({
                    'id': row[0],
                    'email': row[1],
                    'selected': str(row[0]) == str(visit_data['doctor_id'])
                })
            
            # Get nurses
            cur.execute('''
                SELECT p.no_pegawai, u.email
                FROM PEGAWAI p
                JOIN "USER" u ON p.email_user = u.email
                JOIN PERAWAT_HEWAN pw ON p.no_pegawai = pw.no_perawat_hewan
                ORDER BY u.email
            ''')
            
            for row in cur.fetchall():
                nurse_list.append({
                    'id': row[0],
                    'email': row[1],
                    'selected': str(row[0]) == str(visit_data['nurse_id'])
                })
            
            # Get animals for the selected client
            cur.execute('''
                SELECT h.nama, h.no_identitas_klien
                FROM HEWAN h
                WHERE h.no_identitas_klien = %s
                ORDER BY h.nama
            ''', (visit_data['client_id'],))
            
            for row in cur.fetchall():
                animal_list.append({
                    'name': row[0],
                    'client_id': row[1],
                    'selected': row[0] == visit_data['nama_hewan']
                })
                
        except Exception as error:
            print(f"Error fetching data for update_kunjungan form: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:list_kunjungan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        context = {
            'visit': visit_data,
            'client_list': client_list,
            'doctor_list': doctor_list,
            'nurse_list': nurse_list,
            'animal_list': animal_list
        }
        
        return render(request, 'update_kunjungan.html', context)

# Function to delete a visit
def delete_kunjungan(request):
    # Check if user is authorized (must be front desk)
    role = request.session.get('role')
    if role != 'front_desk':
        messages.error(request, "Anda tidak memiliki izin untuk menghapus kunjungan")
        return redirect('hijau:list_kunjungan')
    
    if request.method == 'POST':
        id_kunjungan = request.POST.get('id_kunjungan')
        
        if not id_kunjungan:
            messages.error(request, "ID Kunjungan diperlukan")
            return redirect('hijau:list_kunjungan')
        
        conn = None
        cur = None
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if the visit has any treatments
            cur.execute('''
                SELECT COUNT(*)
                FROM KUNJUNGAN_KEPERAWATAN
                WHERE id_kunjungan = %s
            ''', (id_kunjungan,))
            
            treatment_count = cur.fetchone()[0]
            
            if treatment_count > 0:
                # Delete all related treatments first
                cur.execute('''
                    DELETE FROM KUNJUNGAN_KEPERAWATAN
                    WHERE id_kunjungan = %s
                ''', (id_kunjungan,))
            
            # Delete the visit record
            cur.execute('''
                DELETE FROM KUNJUNGAN
                WHERE id_kunjungan = %s
            ''', (id_kunjungan,))
            
            if cur.rowcount == 0:
                messages.error(request, "Kunjungan tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            conn.commit()
            messages.success(request, "Kunjungan berhasil dihapus")
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in delete_kunjungan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    return redirect('hijau:list_kunjungan')

# REKAM MEDIS (Medical Record) functions

# Function to list medical records
def list_medis(request):
    id_kunjungan = request.GET.get('id')
    
    if not id_kunjungan:
        messages.error(request, "ID Kunjungan diperlukan")
        return redirect('hijau:list_kunjungan')
    
    conn = None
    cur = None
    has_medical_record = False
    medical_record = {}
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if medical record exists
        cur.execute('''
            SELECT suhu, berat_badan, catatan
            FROM KUNJUNGAN
            WHERE id_kunjungan = %s
        ''', (id_kunjungan,))
        
        row = cur.fetchone()
        if not row:
            messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
            return redirect('hijau:list_kunjungan')
        
        # If both suhu and berat_badan have values, consider it as having a medical record
        has_medical_record = row[0] is not None and row[1] is not None
        
        if has_medical_record:
            medical_record = {
                'id_kunjungan': id_kunjungan,
                'suhu': row[0],
                'berat_badan': row[1],
                'catatan': row[2] or ""
            }
        
    except Exception as error:
        print(f"Error in list_medis: {error}")
        messages.error(request, f"Terjadi kesalahan: {error}")
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    context = {
        'id_kunjungan': id_kunjungan,
        'has_medical_record': has_medical_record,
        'medical_record': medical_record
    }
    
    return render(request, 'list_rekam_medis.html', context)

# Function to create a medical record
def create_rekam_medis(request):
    # Check if user is authorized (must be a doctor)
    role = request.session.get('role')
    if role != 'dokter_hewan':
        messages.error(request, "Anda tidak memiliki izin untuk membuat rekam medis")
        return redirect('hijau:list_kunjungan')
    
    id_kunjungan = request.GET.get('id')
    
    if not id_kunjungan:
        messages.error(request, "ID Kunjungan diperlukan")
        return redirect('hijau:list_kunjungan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            suhu = request.POST.get('temperature')
            berat_badan = request.POST.get('weight')
            catatan = request.POST.get('notes', '')
            
            # Input validation
            if not suhu or not berat_badan:
                messages.error(request, "Suhu dan berat badan harus diisi")
                return redirect(f'hijau:create_rekam_medis?id={id_kunjungan}')
            
            # Update the kunjungan record with medical data
            cur.execute('''
                UPDATE KUNJUNGAN
                SET suhu = %s, berat_badan = %s, catatan = %s
                WHERE id_kunjungan = %s
            ''', (suhu, berat_badan, catatan, id_kunjungan))
            
            if cur.rowcount == 0:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            conn.commit()
            messages.success(request, "Rekam medis berhasil dibuat")
            return redirect(f'hijau:list_rekam_medis?id={id_kunjungan}')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in create_rekam_medis: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect(f'hijau:create_rekam_medis?id={id_kunjungan}')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request (display form)
    else:
        # Get kunjungan details for context
        kunjungan_details = {}
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT k.nama_hewan, 
                       CASE 
                           WHEN i.no_identitas_klien IS NOT NULL THEN i.nama_depan || ' ' || i.nama_belakang
                           ELSE p.nama_perusahaan
                       END as nama_klien
                FROM KUNJUNGAN k
                LEFT JOIN INDIVIDU i ON k.no_identitas_klien = i.no_identitas_klien
                LEFT JOIN PERUSAHAAN p ON k.no_identitas_klien = p.no_identitas_klien
                WHERE k.id_kunjungan = %s
            ''', (id_kunjungan,))
            
            row = cur.fetchone()
            if not row:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            kunjungan_details = {
                'id_kunjungan': id_kunjungan,
                'nama_hewan': row[0],
                'nama_klien': row[1]
            }
                
        except Exception as error:
            print(f"Error fetching data for create_rekam_medis form: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:list_kunjungan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        context = {
            'kunjungan': kunjungan_details
        }
        
        return render(request, 'create_rekam_medis.html', context)

# Function to update a medical record
def update_rekam_medis(request):
    # Check if user is authorized (must be a doctor)
    role = request.session.get('role')
    if role != 'dokter_hewan':
        messages.error(request, "Anda tidak memiliki izin untuk mengubah rekam medis")
        return redirect('hijau:list_kunjungan')
    
    id_kunjungan = request.GET.get('id')
    
    if not id_kunjungan:
        messages.error(request, "ID Kunjungan diperlukan")
        return redirect('hijau:list_kunjungan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            suhu = request.POST.get('bodyTemp')
            berat_badan = request.POST.get('weight')
            catatan = request.POST.get('notes', '')
            
            # Input validation
            if not suhu or not berat_badan:
                messages.error(request, "Suhu dan berat badan harus diisi")
                return redirect(f'hijau:update_rekam_medis?id={id_kunjungan}')
            
            # Update the kunjungan record with medical data
            cur.execute('''
                UPDATE KUNJUNGAN
                SET suhu = %s, berat_badan = %s, catatan = %s
                WHERE id_kunjungan = %s
            ''', (suhu, berat_badan, catatan, id_kunjungan))
            
            if cur.rowcount == 0:
                messages.error(request, f"Kunjungan dengan ID {id_kunjungan} tidak ditemukan")
                return redirect('hijau:list_kunjungan')
            
            conn.commit()
            messages.success(request, "Rekam medis berhasil diperbarui")
            return redirect(f'hijau:list_rekam_medis?id={id_kunjungan}')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in update_rekam_medis: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect(f'hijau:update_rekam_medis?id={id_kunjungan}')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request (display form)
    else:
        # Fetch data for dropdown menus
        kunjungan_list = []
        jenis_perawatan_list = []
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get doctor's ID
            email = request.session.get('email')
            cur.execute(
                'SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s',
                (email,)
            )
            doctor_id = cur.fetchone()[0]
            
            # Get active visits for this doctor
            cur.execute('''
                SELECT k.id_kunjungan, h.nama, i.nama_depan || ' ' || i.nama_belakang as nama_klien
                FROM KUNJUNGAN k
                JOIN HEWAN h ON h.nama = k.nama_hewan AND h.no_identitas_klien = k.no_identitas_klien
                JOIN KLIEN kl ON kl.no_identitas = k.no_identitas_klien
                JOIN INDIVIDU i ON i.no_identitas_klien = kl.no_identitas
                WHERE k.no_dokter_hewan = %s AND k.timestamp_akhir IS NULL
                UNION
                SELECT k.id_kunjungan, h.nama, p.nama_perusahaan as nama_klien
                FROM KUNJUNGAN k
                JOIN HEWAN h ON h.nama = k.nama_hewan AND h.no_identitas_klien = k.no_identitas_klien
                JOIN KLIEN kl ON kl.no_identitas = k.no_identitas_klien
                JOIN PERUSAHAAN p ON p.no_identitas_klien = kl.no_identitas
                WHERE k.no_dokter_hewan = %s AND k.timestamp_akhir IS NULL
                ORDER BY id_kunjungan
            ''', (doctor_id, doctor_id))
            
            for row in cur.fetchall():
                kunjungan_list.append({
                    'id': row[0],
                    'display': f"{row[0]} - {row[1]} ({row[2]})"
                })
            
            # Get available treatment types
            cur.execute('''
                SELECT kode_perawatan, nama_perawatan
                FROM PERAWATAN
                ORDER BY kode_perawatan
            ''')
            
            for row in cur.fetchall():
                jenis_perawatan_list.append({
                    'kode': row[0],
                    'display': f"{row[0]} - {row[1]}"
                })
                
        except Exception as error:
            print(f"Error fetching data for create_perawatan form: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        context = {
            'kunjungan_list': kunjungan_list,
            'jenis_perawatan_list': jenis_perawatan_list
        }
        
        return render(request, 'create_perawatan.html', context)

# Function to update an existing treatment
def update_perawatan(request, id_kunjungan=None):
    conn = None
    cur = None
    
    # Check if user is authorized (must be a doctor)
    role = request.session.get('role')
    if role != 'dokter_hewan':
        messages.error(request, "Anda tidak memiliki izin untuk mengubah perawatan")
        return redirect('hijau:list_perawatan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            id_kunjungan = request.POST.get('kunjungan')
            jenis_perawatan_new = request.POST.get('jenis_perawatan')
            kode_perawatan_old = request.POST.get('kode_perawatan_old')
            catatan_medis = request.POST.get('catatan_medis', '')
            
            # Input validation
            if not id_kunjungan or not jenis_perawatan_new or not kode_perawatan_old:
                messages.error(request, "Kunjungan dan jenis perawatan harus diisi")
                return redirect('hijau:list_perawatan')
            
            # Check if treatment type has changed
            if jenis_perawatan_new != kode_perawatan_old:
                # Get treatment details to maintain other data
                cur.execute('''
                    SELECT nama_hewan, no_identitas_klien, no_front_desk, 
                           no_perawat_hewan, no_dokter_hewan
                    FROM KUNJUNGAN_KEPERAWATAN 
                    WHERE id_kunjungan = %s AND kode_perawatan = %s
                ''', (id_kunjungan, kode_perawatan_old))
                
                treatment_data = cur.fetchone()
                if not treatment_data:
                    messages.error(request, "Perawatan tidak ditemukan")
                    return redirect('hijau:list_perawatan')
                
                nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan = treatment_data
                
                # Delete old treatment record
                cur.execute('''
                    DELETE FROM KUNJUNGAN_KEPERAWATAN
                    WHERE id_kunjungan = %s AND kode_perawatan = %s
                ''', (id_kunjungan, kode_perawatan_old))
                
                # Create new treatment record with updated type
                cur.execute('''
                    INSERT INTO KUNJUNGAN_KEPERAWATAN(
                        id_kunjungan, nama_hewan, no_identitas_klien, 
                        no_front_desk, no_perawat_hewan, no_dokter_hewan,
                        kode_perawatan)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    id_kunjungan, 
                    nama_hewan, 
                    no_identitas_klien, 
                    no_front_desk, 
                    no_perawat_hewan, 
                    no_dokter_hewan, 
                    jenis_perawatan_new
                ))
            
            # Update the catatan field in KUNJUNGAN table
            cur.execute('''
                UPDATE KUNJUNGAN
                SET catatan = %s
                WHERE id_kunjungan = %s
            ''', (catatan_medis, id_kunjungan))
            
            conn.commit()
            messages.success(request, "Perawatan berhasil diperbarui")
            return redirect('hijau:list_perawatan')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in update_perawatan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:list_perawatan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request (display form)
    else:
        treatment_data = {}
        jenis_perawatan_list = []
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get treatment data
            cur.execute('''
                SELECT kk.kode_perawatan, p.nama_perawatan, k.catatan
                FROM KUNJUNGAN_KEPERAWATAN kk
                JOIN KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan
                JOIN PERAWATAN p ON kk.kode_perawatan = p.kode_perawatan
                WHERE kk.id_kunjungan = %s
            ''', (id_kunjungan,))
            
            row = cur.fetchone()
            if not row:
                messages.error(request, "Perawatan tidak ditemukan")
                return redirect('hijau:list_perawatan')
            
            treatment_data = {
                'id_kunjungan': id_kunjungan,
                'kode_perawatan': row[0],
                'jenis_perawatan': row[0],
                'catatan_medis': row[2] or ""
            }
            
            # Get available treatment types
            cur.execute('''
                SELECT kode_perawatan, nama_perawatan
                FROM PERAWATAN
                ORDER BY kode_perawatan
            ''')
            
            for row in cur.fetchall():
                jenis_perawatan_list.append({
                    'kode': row[0],
                    'display': f"{row[0]} - {row[1]}",
                    'selected': row[0] == treatment_data['kode_perawatan']
                })
                
        except Exception as error:
            print(f"Error fetching data for update_perawatan form: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:list_perawatan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
        context = {
            'treatment': treatment_data,
            'jenis_perawatan_list': jenis_perawatan_list
        }
        
        return render(request, 'update_perawatan.html', context)

# Function to delete a treatment
def delete_perawatan(request):
    # Check if user is authorized (must be a doctor)
    role = request.session.get('role')
    if role != 'dokter_hewan':
        messages.error(request, "Anda tidak memiliki izin untuk menghapus perawatan")
        return redirect('hijau:list_perawatan')
    
    if request.method == 'POST':
        id_kunjungan = request.POST.get('id_kunjungan')
        kode_perawatan = request.POST.get('kode_perawatan')
        
        if not id_kunjungan or not kode_perawatan:
            messages.error(request, "ID Kunjungan dan kode perawatan diperlukan")
            return redirect('hijau:list_perawatan')
        
        conn = None
        cur = None
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Delete the treatment record
            cur.execute('''
                DELETE FROM KUNJUNGAN_KEPERAWATAN
                WHERE id_kunjungan = %s AND kode_perawatan = %s
            ''', (id_kunjungan, kode_perawatan))
            
            if cur.rowcount == 0:
                messages.error(request, "Perawatan tidak ditemukan")
                return redirect('hijau:list_perawatan')
            
            conn.commit()
            messages.success(request, "Perawatan berhasil dihapus")
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in delete_perawatan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    return redirect('hijau:list_perawatan')

# KUNJUNGAN (Visit) functions

# Function to list all visits
def list_kunjungan(request):
    conn = None
    cur = None
    kunjungan_list = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user role from session
        role = request.session.get('role')
        email = request.session.get('email')
        
        # If user is a klien (client), only show their visits
        if role == 'individu' or role == 'perusahaan':
            # Get the client's ID
            cur.execute(
                'SELECT no_identitas FROM KLIEN WHERE email = %s',
                (email,)
            )
            client_id = cur.fetchone()[0]
            
            # Get visits for this client
            cur.execute('''
                SELECT k.id_kunjungan, k.no_identitas_klien, k.nama_hewan, 
                       k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir
                FROM KUNJUNGAN k
                WHERE k.no_identitas_klien = %s
                ORDER BY k.timestamp_awal DESC
            ''', (client_id,))
            
        # If user is a front desk officer
        elif role == 'front_desk':
            # Get all visits
            cur.execute('''
                SELECT k.id_kunjungan, k.no_identitas_klien, k.nama_hewan, 
                       k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir
                FROM KUNJUNGAN k
                ORDER BY k.timestamp_awal DESC
            ''')
            
        # If user is medical staff (doctor or nurse)
        else:
            # Get staff ID
            cur.execute(
                'SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s',
                (email,)
            )
            staff_id = cur.fetchone()[0]
            
            # Get visits for this staff member
            if role == 'dokter_hewan':
                cur.execute('''
                    SELECT k.id_kunjungan, k.no_identitas_klien, k.nama_hewan, 
                           k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir
                    FROM KUNJUNGAN k
                    WHERE k.no_dokter_hewan = %s
                    ORDER BY k.timestamp_awal DESC
                ''', (staff_id,))
            else:
                cur.execute('''
                    SELECT k.id_kunjungan, k.no_identitas_klien, k.nama_hewan, 
                           k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir
                    FROM KUNJUNGAN k
                    WHERE k.no_perawat_hewan = %s
                    ORDER BY k.timestamp_awal DESC
                ''', (staff_id,))
        
        rows = cur.fetchall()
        for row in rows:
            # Format timestamps
            timestamp_awal = row[4].strftime('%d-%m-%Y %H:%M:%S') if row[4] else '-'
            timestamp_akhir = row[5].strftime('%d-%m-%Y %H:%M:%S') if row[5] else '-'
            
            kunjungan_list.append({
                'id_kunjungan': row[0],
                'id_klien': row[1],
                'nama_hewan': row[2],
                'metode_kunjungan': row[3],
                'waktu_mulai_penanganan': timestamp_awal,
                'waktu_akhir_penanganan': timestamp_akhir,
            })
    
    except Exception as error:
        print(f"Error in list_kunjungan: {error}")
        messages.error(request, f"Terjadi kesalahan: {error}")
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render(request, 'list_kunjungan.html', {'kunjungan_list': kunjungan_list})

# Function to create a new visit
def create_kunjungan(request):
    # Check if user is authorized (must be front desk)
    role = request.session.get('role')
    if role != 'front_desk':
        messages.error(request, "Anda tidak memiliki izin untuk membuat kunjungan")
        return redirect('hijau:list_kunjungan')
    
    # If POST request (form submission)
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get form data
            client_id = request.POST.get('clientId')
            nama_hewan = request.POST.get('animalName')
            dokter_email = request.POST.get('doctor')
            perawat_email = request.POST.get('nurse')
            tipe_kunjungan = request.POST.get('visitMethod')
            timestamp_awal = request.POST.get('startTime')
            timestamp_akhir = request.POST.get('endTime') or None
            
            # Get front desk ID
            email = request.session.get('email')
            cur.execute(
                'SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s',
                (email,)
            )
            front_desk_id = cur.fetchone()[0]
            
            # Get doctor ID
            cur.execute(
                'SELECT p.no_pegawai FROM PEGAWAI p JOIN "USER" u ON p.email_user = u.email WHERE u.email = %s',
                (dokter_email,)
            )
            doctor_id = cur.fetchone()[0]
            
            # Get nurse ID
            cur.execute(
                'SELECT p.no_pegawai FROM PEGAWAI p JOIN "USER" u ON p.email_user = u.email WHERE u.email = %s',
                (perawat_email,)
            )
            nurse_id = cur.fetchone()[0]
            
            # Generate UUID for the new visit
            cur.execute("SELECT gen_random_uuid()")
            id_kunjungan = cur.fetchone()[0]
            
            # Create the visit record
            cur.execute('''
                INSERT INTO KUNJUNGAN(
                    id_kunjungan, nama_hewan, no_identitas_klien, 
                    no_front_desk, no_perawat_hewan, no_dokter_hewan,
                    kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                id_kunjungan, 
                nama_hewan, 
                client_id, 
                front_desk_id, 
                nurse_id, 
                doctor_id, 
                'VAK001', # Default vaccine code
                tipe_kunjungan,
                timestamp_awal,
                timestamp_akhir
            ))
            
            conn.commit()
            messages.success(request, "Kunjungan berhasil dibuat")
            return redirect('hijau:list_kunjungan')
            
        except Exception as error:
            if conn:
                conn.rollback()
            print(f"Error in create_kunjungan: {error}")
            messages.error(request, f"Terjadi kesalahan: {error}")
            return redirect('hijau:create_kunjungan')
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # If GET request
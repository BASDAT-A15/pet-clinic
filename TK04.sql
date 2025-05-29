CREATE OR REPLACE FUNCTION check_email_exists()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN
        IF EXISTS (
            SELECT 1 
            FROM "USER" 
            WHERE LOWER(email) = LOWER(NEW.email)
        ) THEN
            RAISE EXCEPTION 'Email "%" sudah terdaftar, gunakan email lain.', NEW.email;
        END IF;
    END IF;
    
    IF TG_OP = 'UPDATE' THEN
        IF OLD.email != NEW.email THEN
            IF EXISTS (
                SELECT 1 
                FROM "USER" 
                WHERE LOWER(email) = LOWER(NEW.email)
                AND email != OLD.email
            ) THEN
                RAISE EXCEPTION 'Email "%" sudah terdaftar, gunakan email lain.', NEW.email;
            END IF;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION validate_kunjungan_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.timestamp_akhir IS NOT NULL THEN
        IF NEW.timestamp_akhir < NEW.timestamp_awal THEN
            RAISE EXCEPTION 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_kunjungan_timestamp
BEFORE INSERT OR UPDATE ON KUNJUNGAN
FOR EACH ROW
EXECUTE FUNCTION validate_kunjungan_timestamp();




CREATE OR REPLACE FUNCTION validate_kepemilikan_hewan()
RETURNS TRIGGER AS $$
DECLARE
    nama_pemilik TEXT;
    is_valid BOOLEAN;
BEGIN
    is_valid := EXISTS (
        SELECT 1 
        FROM HEWAN 
        WHERE nama = NEW.nama_hewan 
        AND no_identitas_klien = NEW.no_identitas_klien
    );
    
    IF NOT is_valid THEN
        SELECT 
            CASE 
                WHEN i.no_identitas_klien IS NOT NULL THEN 
                    CONCAT(i.nama_depan, 
                           CASE WHEN i.nama_tengah IS NOT NULL THEN ' ' || i.nama_tengah ELSE '' END,
                           ' ', i.nama_belakang)
                WHEN p.no_identitas_klien IS NOT NULL THEN 
                    p.nama_perusahaan
                ELSE 
                    NEW.no_identitas_klien::TEXT
            END INTO nama_pemilik
        FROM KLIEN k
        LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
        LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
        WHERE k.no_identitas = NEW.no_identitas_klien;
        
        IF nama_pemilik IS NULL THEN
            nama_pemilik := NEW.no_identitas_klien::TEXT;
        END IF;
        
        RAISE EXCEPTION 'Hewan "%" tidak terdaftar atas nama pemilik "%" .', NEW.nama_hewan, nama_pemilik;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_kepemilikan_hewan
BEFORE INSERT OR UPDATE ON KUNJUNGAN
FOR EACH ROW
EXECUTE FUNCTION validate_kepemilikan_hewan();
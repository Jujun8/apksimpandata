import streamlit as st
import psycopg2
import json

# 1. Konfigurasi Koneksi Database (Samakan dengan application.properties Java Anda)
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="db_kominfo_data",
        user="postgres",
        password="rahasia123",
        port="5432"
    )

# 2. Judul Aplikasi
st.set_page_config(page_title="Pusat Data Kominfo", layout="centered")
st.title("🏛️ Pengumpulan Data Sektoral")
st.subheader("Formulir Input Data Antar Dinas")

# 3. Form Input
with st.form("form_data_dinas"):
    st.write("Silakan isi data di bawah ini:")
    
    # Meta Data
    form_id = st.number_input("ID Formulir", min_value=1, value=1)
    opd_id = st.number_input("ID Dinas (OPD)", min_value=1, value=101)
    
    st.divider()
    
    # Contoh Data Dinamis (Ini yang akan masuk ke kolom JSONB)
    nama_petugas = st.text_input("Nama Petugas Penginput")
    kategori_data = st.selectbox("Kategori Data", ["Kesehatan", "Pendidikan", "Infrastruktur"])
    jumlah_capaian = st.number_input("Nilai Capaian (Angka)", min_value=0)
    catatan_tambahan = st.text_area("Catatan/Kendala")
    
    submitted = st.form_submit_state = st.form_submit_button("Kirim Data ke Kominfo")

# 4. Logika Penyimpanan (Sinkron dengan struktur tabel Java)
if submitted:
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Susun data jawaban menjadi format JSON (Dictionary Python)
        jawaban_json = {
            "nama_petugas": nama_petugas,
            "kategori": kategori_data,
            "nilai": jumlah_capaian,
            "catatan": catatan_tambahan
        }
        
        # Query SQL (Sesuaikan nama kolom dengan tabel di Java/Postgres)
        query = """
            INSERT INTO tabel_submissions (form_id, opd_pengirim_id, data_jawaban)
            VALUES (%s, %s, %s)
        """
        
        cur.execute(query, (form_id, opd_id, json.dumps(jawaban_json)))
        conn.commit()
        
        st.success("✅ Data berhasil dikirim dan disimpan di Database Pusat!")
        
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"❌ Gagal menyimpan data: {e}")

# 5. Fitur Tambahan: Lihat Data Terkini
if st.checkbox("Tampilkan Data Terakhir yang Masuk"):
    st.write("Data dari tabel_submissions (PostgreSQL):")
    # Logika fetch data bisa ditambahkan di sini

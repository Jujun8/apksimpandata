import streamlit as st
import json
import os
from datetime import datetime

# Nama file untuk menyimpan data
DATA_FILE = "data_simpanan_dinas.json"

# Fungsi untuk menyimpan data ke file JSON
def simpan_ke_json(data_baru):
    # 1. Baca data lama jika file sudah ada
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data_list = json.load(f)
            except json.JSONDecodeError:
                data_list = []
    else:
        data_list = []

    # 2. Tambahkan data baru
    data_list.append(data_baru)

    # 3. Tulis kembali ke file
    with open(DATA_FILE, "w") as f:
        json.dump(data_list, f, indent=4)

# --- Tampilan Aplikasi ---
st.set_page_config(page_title="Pusat Data Kominfo", page_icon="📁")
st.title("📁 Pengumpulan Data Sektoral")
st.info("Mode Penyimpanan: File Lokal (JSON)")

with st.form("form_input"):
    nama_dinas = st.text_input("Nama Dinas (OPD)")
    kategori = st.selectbox("Kategori Data", ["Kesehatan", "Pendidikan", "Sosial", "Ekonomi"])
    isi_data = st.text_area("Detail Laporan/Data")
    
    submitted = st.form_submit_button("Simpan Data")

if submitted:
    if nama_dinas and isi_data:
        # Buat struktur data
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dinas": nama_dinas,
            "kategori": kategori,
            "data": isi_data
        }
        
        # Jalankan fungsi simpan
        simpan_ke_json(payload)
        st.success(f"✅ Data dari {nama_dinas} berhasil disimpan ke file {DATA_FILE}!")
    else:
        st.warning("Mohon isi semua bidang yang tersedia.")

# --- Fitur Lihat Data ---
st.divider()
if st.checkbox("Lihat Semua Data yang Tersimpan"):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            list_data = json.load(f)
            st.write(f"Total entri: {len(list_data)}")
            st.json(list_data)
    else:
        st.info("Belum ada data yang tersimpan.")

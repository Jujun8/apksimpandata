import streamlit as st
import os
import json
from datetime import datetime

# --- CONFIGURASI DASAR ---
UPLOAD_DIR = "uploads"
LOG_FILE = "data_log.json"
ADMIN_PASSWORD = "admin123"  # Silakan ganti password ini

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Fungsi untuk menyimpan catatan ke JSON
def save_log(entry):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: logs = json.load(f)
            except: logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Navigation")
role = st.sidebar.radio("Pilih Role:", ["User (Pengirim Data)", "Admin (Dinas Kominfo)"])

# --- HALAMAN USER (TANPA PASSWORD) ---
if role == "User (Pengirim Data)":
    st.title("📤 Form Pengumpulan Data")
    st.info("Silakan unggah dokumen atau laporan dinas Anda di bawah ini.")

    with st.form("user_form", clear_on_submit=True):
        nama_dinas = st.text_input("Nama Dinas/Instansi")
        perihal = st.text_input("Perihal Data")
        uploaded_file = st.file_uploader("Pilih File (PDF, Excel, Docx)", type=['pdf', 'xlsx', 'docx', 'csv'])
        
        submit = st.form_submit_button("Kirim Data")

    if submit:
        if nama_dinas and uploaded_file:
            # Simpan file fisik
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Simpan catatan ke JSON
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dinas": nama_dinas,
                "perihal": perihal,
                "file_name": uploaded_file.name,
                "saved_path": file_path
            }
            save_log(log_entry)
            st.success(f"✅ Berhasil! File '{uploaded_file.name}' telah terkirim ke Admin.")
        else:
            st.error("Mohon isi nama dinas dan lampirkan file.")

# --- HALAMAN ADMIN (DENGAN PASSWORD) ---
else:
    st.title("🔐 Panel Admin Kominfo")
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Akses Diterima. Berikut adalah data yang terkumpul:")
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                data_logs = json.load(f)
            
            # Tampilkan dalam bentuk Tabel
            if data_logs:
                st.table(data_logs)
                
                # Fitur tambahan: Download File yang sudah diupload
                st.subheader("Daftar File di Server:")
                for log in data_logs:
                    with open(log['saved_path'], "rb") as file:
                        st.download_button(
                            label=f"Unduh {log['file_name']} (dari {log['dinas']})",
                            data=file,
                            file_name=log['file_name'],
                            key=log['saved_path']
                        )
            else:
                st.write("Belum ada data masuk.")
        else:
            st.write("Belum ada aktivitas pengiriman data.")
            
    elif password != "" and password != ADMIN_PASSWORD:
        st.error("Password Salah! Akses ditolak.")

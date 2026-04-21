import streamlit as st
import os
import json
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- KONEKSI GOOGLE DRIVE ---
def login_gdrive():
    gauth = GoogleAuth()
    # Mencoba load kredensial yang sudah tersimpan
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Jika belum ada, lakukan autentikasi (hanya dijalankan sekali di lokal)
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    # Simpan kredensial untuk penggunaan berikutnya
    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)

drive = login_gdrive()
LOG_FILE = "data_log.json"
ADMIN_PASSWORD = "admin123"

# --- FUNGSI HELPER ---
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_all_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Navigasi")
role = st.sidebar.radio("Pilih Role:", ["User (Pengirim Data)", "Admin (Dinas Kominfo)"])

# --- HALAMAN USER ---
if role == "User (Pengirim Data)":
    st.title("📤 Form Pengumpulan Data (Direct to G-Drive)")
    with st.form("user_form", clear_on_submit=True):
        nama_dinas = st.text_input("Nama Dinas/Instansi")
        perihal = st.text_input("Perihal Data")
        uploaded_file = st.file_uploader("Pilih File")
        submit = st.form_submit_button("Kirim Data")

    if submit:
        if nama_dinas and uploaded_file:
            # 1. Simpan sementara di lokal untuk diupload
            temp_path = uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 2. Upload ke Google Drive
            gfile = drive.CreateFile({'title': f"{nama_dinas}_{uploaded_file.name}"})
            gfile.SetContentFile(temp_path)
            gfile.Upload()
            
            # Ambil link file untuk admin
            file_link = gfile['alternateLink']
            
            # 3. Simpan log
            logs = load_logs()
            logs.append({
                "id": len(logs) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dinas": nama_dinas,
                "perihal": perihal,
                "file_name": uploaded_file.name,
                "gdrive_link": file_link
            })
            save_all_logs(logs)
            
            # Hapus file sementara di lokal
            os.remove(temp_path)
            st.success("✅ File berhasil diunggah langsung ke Google Drive!")
        else:
            st.error("Mohon lengkapi data.")

# --- HALAMAN ADMIN ---
else:
    st.title("🔐 Panel Admin Kominfo")
    password = st.text_input("Password Admin:", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Akses Diterima.")
        data_logs = load_logs()

        if data_logs:
            st.subheader("Data Terkumpul")
            st.table(data_logs)

            st.divider()
            st.subheader("📝 Edit & Akses File")
            
            for log in data_logs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{log['dinas']}** - {log['perihal']}")
                with col2:
                    # Link langsung ke Google Drive
                    st.link_button("Buka File", log['gdrive_link'])
        else:
            st.write("Belum ada data masuk.")

import streamlit as st
import os
import json
from datetime import datetime

# --- KONFIGURASI DASAR ---
UPLOAD_DIR = "uploads"
LOG_FILE = "data_log.json"
ADMIN_PASSWORD = "admin123"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Fungsi untuk membaca log
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

# Fungsi untuk menyimpan seluruh list log
def save_all_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Navigasi")
role = st.sidebar.radio("Pilih Role:", ["User (Pengirim Data)", "Admin (Dinas Kominfo)"])

# --- HALAMAN USER ---
if role == "User (Pengirim Data)":
    st.title("📤 Form Pengumpulan Data")
    with st.form("user_form", clear_on_submit=True):
        nama_dinas = st.text_input("Nama Dinas/Instansi")
        perihal = st.text_input("Perihal Data")
        uploaded_file = st.file_uploader("Pilih File", type=['pdf', 'xlsx', 'docx', 'csv'])
        submit = st.form_submit_button("Kirim Data")

    if submit:
        if nama_dinas and uploaded_file:
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            logs = load_logs()
            logs.append({
                "id": len(logs) + 1, # Tambahkan ID unik untuk mempermudah edit
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dinas": nama_dinas,
                "perihal": perihal,
                "file_name": uploaded_file.name,
                "saved_path": file_path
            })
            save_all_logs(logs)
            st.success("✅ Data berhasil dikirim!")
        else:
            st.error("Mohon lengkapi data.")

# --- HALAMAN ADMIN ---
else:
    st.title("🔐 Panel Admin Kominfo")
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Akses Diterima.")
        data_logs = load_logs()

        if data_logs:
            # 1. Tampilkan Tabel Data Terkini
            st.subheader("Data Terkumpul")
            st.table(data_logs)

            # 2. Fitur Edit Data
            st.divider()
            st.subheader("📝 Edit Data")
            
            # Pilih ID data yang ingin diedit
            list_id = [item['id'] for item in data_logs]
            id_pilihan = st.selectbox("Pilih ID Data yang ingin diubah:", list_id)
            
            # Ambil data lama berdasarkan ID
            index_pilihan = next((index for (index, d) in enumerate(data_logs) if d["id"] == id_pilihan), None)
            data_lama = data_logs[index_pilihan]

            # Form Edit
            with st.form("edit_form"):
                new_dinas = st.text_input("Nama Dinas", value=data_lama['dinas'])
                new_perihal = st.text_input("Perihal", value=data_lama['perihal'])
                st.info(f"File: {data_lama['file_name']} (File tidak dapat diubah di sini)")
                
                btn_update = st.form_submit_button("Simpan Perubahan")

            if btn_update:
                data_logs[index_pilihan]['dinas'] = new_dinas
                data_logs[index_pilihan]['perihal'] = new_perihal
                save_all_logs(data_logs)
                st.success(f"✅ Data ID {id_pilihan} Berhasil Diperbarui!")
                st.rerun() # Refresh halaman untuk melihat perubahan

            # 3. Fitur Download
            st.divider()
            st.subheader("📁 Download File")
            for log in data_logs:
                if os.path.exists(log['saved_path']):
                    with open(log['saved_path'], "rb") as file:
                        st.download_button(
                            label=f"Unduh {log['file_name']} ({log['dinas']})",
                            data=file,
                            file_name=log['file_name'],
                            key=f"dl_{log['id']}"
                        )
        else:
            st.write("Belum ada data masuk.")
            
    elif password != "":
        st.error("Password Salah!")

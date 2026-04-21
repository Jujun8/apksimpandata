import streamlit as st
import pandas as pd
import sqlite3
import os

# --- KONEKSI DATABASE ---
def init_db():
    conn = sqlite3.connect('data_opd.db')
    c = conn.cursor()
    # Membuat tabel jika belum ada
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventaris (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_barang TEXT,
            kategori TEXT,
            jumlah INTEGER,
            kondisi TEXT,
            tanggal_input DATE
        )
    ''')
    conn.commit()
    return conn

# --- FUNGSI CRUD ---
def simpan_data(nama, kategori, jumlah, kondisi, tanggal):
    conn = sqlite3.connect('data_opd.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO inventaris (nama_barang, kategori, jumlah, kondisi, tanggal_input)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, kategori, jumlah, kondisi, tanggal))
    conn.commit()
    conn.close()

def tampilkan_data():
    conn = sqlite3.connect('data_opd.db')
    df = pd.read_sql_query("SELECT * FROM inventaris", conn)
    conn.close()
    return df

# --- UI STREAMLIT ---
st.set_page_config(page_title="Sistem Informasi Aset OPD", layout="wide")

st.title("🏛️ Pengelolaan Data Inventaris OPD")
st.markdown("Gunakan formulir di bawah untuk mencatat aset baru.")

# Inisialisasi DB
init_db()

# Membuat dua kolom (Form Input & Tabel Data)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Input Data Baru")
    with st.form("form_aset", clear_on_submit=True):
        nama_barang = st.text_input("Nama Barang")
        kategori = st.selectbox("Kategori", ["Elektronik", "Mebel", "Kendaraan", "Alat Kantor"])
        jumlah = st.number_input("Jumlah Unit", min_value=1, step=1)
        kondisi = st.radio("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])
        tanggal = st.date_input("Tanggal Perolehan")
        
        submit = st.form_submit_button("Simpan ke Database")
        
        if submit:
            if nama_barang:
                simpan_data(nama_barang, kategori, jumlah, kondisi, tanggal)
                st.success(f"Data {nama_barang} berhasil disimpan!")
                st.rerun() # Refresh untuk update tabel
            else:
                st.error("Nama barang tidak boleh kosong!")

with col2:
    st.subheader("Daftar Inventaris Terdaftar")
    data = tampilkan_data()
    
    if not data.empty:
        # Menampilkan tabel
        st.dataframe(data, use_container_width=True)
        
        # Fitur Export ke Excel/CSV
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name='data_inventaris_opd.csv',
            mime='text/csv',
        )
    else:
        st.info("Belum ada data yang tersimpan.")

# Sidebar Informasi
st.sidebar.info(f"Penyimpanan aktif: **Local SQLite (data_opd.db)**")

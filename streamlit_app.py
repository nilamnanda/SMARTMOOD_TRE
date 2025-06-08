# 🚨 INI HARUS PALING ATAS!
import streamlit as st
st.set_page_config(page_title="SmartMood Tracker", layout="centered")

# 📦 Import lainnya
import pandas as pd
from datetime import datetime
import os

# 📁 Inisialisasi CSV jika belum ada
CSV_FILE = "smartmood_data.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Username", "Akademik", "Sosial", "Kesehatan", "Lainnya", "Mood"])
    df_init.to_csv(CSV_FILE, index=False)

# 👤 Login pengguna (multi-user)
st.title("🧠 SmartMood Tracker - Versi Multi User")
username = st.text_input("Masukkan nama pengguna kamu:")

if username:
    st.success(f"Login sebagai *{username}*")

    st.header("✍️ Input Mood & Aktivitas")

    aktivitas_akademik = st.selectbox("Akademik", ["(Pilih satu)", "Belajar", "Tugas", "Ujian", "Tidak belajar"])
    aktivitas_sosial = st.selectbox("Sosial", ["(Pilih satu)", "Bertemu teman", "Sendiri", "Berargumen", "Kumpul keluarga"])
    aktivitas_kesehatan = st.selectbox("Kesehatan", ["(Pilih satu)", "Olahraga", "Istirahat", "Kurang tidur", "Makan sehat", "Makan junk food"])
    aktivitas_lainnya = st.selectbox("Lainnya", ["(Pilih satu)", "Main game", "Nonton", "Scroll medsos", "Meditasi", "Overthinking"])

    rating = st.slider("Rating mood hari ini (1-5)", min_value=1, max_value=5)

    if st.button("Simpan"):
        tanggal = datetime.now().strftime("%Y-%m-%d")

        df = pd.read_csv(CSV_FILE)

        new_data = {
            "Tanggal": tanggal,
            "Username": username,
            "Akademik": aktivitas_akademik,
            "Sosial": aktivitas_sosial,
            "Kesehatan": aktivitas_kesehatan,
            "Lainnya": aktivitas_lainnya,
            "Mood": rating
        }

        df = df.append(new_data, ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        st.success("Data berhasil disimpan!")

else:
    st.info("Masukkan nama pengguna dulu untuk memulai.")

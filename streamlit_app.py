import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 🟢 HARUS PALING ATAS (setelah import)
st.set_page_config(page_title="SmartMood", layout="centered")

# --------------------------
# 🔐 Simulasi login user
# --------------------------
# Data login (bisa kamu ganti ke file JSON atau DB)
USER_CREDENTIALS = {
    "nilam": "1234",
    "andi": "5678",
    "budi": "abcd"
}

# --------------------------
# 📦 Setup session
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --------------------------
# 🔐 Login Form
# --------------------------
if not st.session_state.logged_in:
    st.title("🧠 SmartMood Tracker - Versi Multi User")

    username = st.text_input("Masukkan username:")
    password = st.text_input("Masukkan password:", type="password")

    if st.button("🔓 Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login sebagai *{username}*")
        else:
            st.error("Username atau password salah.")

    st.stop()  # ⛔ Stop agar tidak render bagian bawah sebelum login

# --------------------------
# 🧠 Setelah Login
# --------------------------
st.title(f"Selamat datang, {st.session_state.username} 👋")

# Data CSV per user
data_file = f"data_{st.session_state.username}.csv"

# Input aktivitas
st.subheader("📋 Input Mood & Aktivitas")
tanggal = st.date_input("Tanggal", datetime.now().date())

aktivitas_akademik = st.selectbox("Aktivitas Akademik", ["-", "Belajar", "Tugas", "Tidak Ada"])
aktivitas_sosial = st.selectbox("Aktivitas Sosial", ["-", "Ngobrol", "Main", "Sendirian"])
aktivitas_kesehatan = st.selectbox("Aktivitas Kesehatan", ["-", "Olahraga", "Tidur cukup", "Makan sehat", "Tidak Sehat"])
aktivitas_lainnya = st.selectbox("Aktivitas Lainnya", ["-", "Game", "Nonton", "Rebahan", "Scrolling", "Meditasi"])

rating_mood = st.slider("Rating mood hari ini (1 = buruk, 5 = sangat baik)", 1, 5, 3)

if st.button("✅ Simpan Data"):
    new_data = {
        "Tanggal": tanggal.strftime("%Y-%m-%d"),
        "Akademik": aktivitas_akademik,
        "Sosial": aktivitas_sosial,
        "Kesehatan": aktivitas_kesehatan,
        "Lainnya": aktivitas_lainnya,
        "RatingMood": rating_mood
    }

    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df = df[df["Tanggal"] != new_data["Tanggal"]]  # hindari duplikat tanggal
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])

    df.to_csv(data_file, index=False)
    st.success("✅ Data berhasil disimpan!")

# --------------------------
# 📊 Lihat Data
# --------------------------
st.subheader("📈 Riwayat Mood Kamu")
if os.path.exists(data_file):
    df = pd.read_csv(data_file)
    st.dataframe(df)
    st.line_chart(df.set_index("Tanggal")["RatingMood"])
else:
    st.info("Belum ada data disimpan.")

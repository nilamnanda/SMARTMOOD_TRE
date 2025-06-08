import streamlit as st
import pandas as pd
import datetime
import os

# ========== Setup Awal ==========
st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("🧠 SmartMood Tracker")

# ========== Inisialisasi Data ==========
data_file = "mood_data.csv"
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Tanggal", "Username", "Mood", "Akademik", "Sosial", "Kesehatan", "Lainnya"])
    df.to_csv(data_file, index=False)

# ========== Login Sederhana ==========
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("🔐 Login")

    if submit_login:
        if username and password:
            st.session_state.username = username
            st.session_state.login = True
            st.success(f"Login sebagai *{username}*")
        else:
            st.error("Username dan Password wajib diisi.")
    st.stop()

# ========== Menu Navigasi ==========
menu = st.sidebar.selectbox("📋 Menu", ["Input Mood Harian", "Lihat Grafik Mood", "Lihat Data CSV", "Reset Data", "Tentang", "Logout"])

# ========== Data Aktivitas ==========
aktivitas_kategori = {
    "Akademik": {
        "positif": ["Belajar", "Mengerjakan tugas", "Membaca buku"],
        "negatif": ["Menunda tugas", "Tidak belajar"]
    },
    "Sosial": {
        "positif": ["Bertemu teman", "Bersosialisasi", "Diskusi kelompok"],
        "negatif": ["Mengisolasi diri", "Bertengkar"]
    },
    "Kesehatan": {
        "positif": ["Olahraga", "Makan sehat", "Tidur cukup"],
        "negatif": ["Begadang", "Makan junk food", "Tidak olahraga"]
    },
    "Lainnya": {
        "positif": ["Meditasi", "Menonton film", "Bermain musik"],
        "negatif": ["Scroll medsos berlebihan", "Main game terus-menerus"]
    }
}

# ========== Halaman Input Mood ==========
if menu == "Input Mood Harian":
    st.header("✍️ Input Mood & Aktivitas")

    with st.form("form_mood"):
        today = datetime.date.today()
        tanggal = st.date_input("Tanggal", today)

        akademik = st.selectbox("Akademik", ["(Pilih satu)"] + aktivitas_kategori["Akademik"]["positif"] + aktivitas_kategori["Akademik"]["negatif"])
        sosial = st.selectbox("Sosial", ["(Pilih satu)"] + aktivitas_kategori["Sosial"]["positif"] + aktivitas_kategori["Sosial"]["negatif"])
        kesehatan = st.selectbox("Kesehatan", ["(Pilih satu)"] + aktivitas_kategori["Kesehatan"]["positif"] + aktivitas_kategori["Kesehatan"]["negatif"])
        lainnya = st.selectbox("Lainnya", ["(Pilih satu)"] + aktivitas_kategori["Lainnya"]["positif"] + aktivitas_kategori["Lainnya"]["negatif"])

        mood = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        submit = st.form_submit_button("Simpan")

    if submit:
        if "(Pilih satu)" in [akademik, sosial, kesehatan, lainnya]:
            st.warning("Harap pilih satu aktivitas dari setiap kategori.")
        else:
            new_data = pd.DataFrame([[tanggal, st.session_state.username, mood, akademik, sosial, kesehatan, lainnya]],
                                    columns=["Tanggal", "Username", "Mood", "Akademik", "Sosial", "Kesehatan", "Lainnya"])
            df = pd.read_csv(data_file)
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(data_file, index=False)
            st.success("Data mood & aktivitas berhasil disimpan!")

# ========== Lihat Data CSV ==========
elif menu == "Lihat Data CSV":
    st.header("📊 Data Mood & Aktivitas")
    df = pd.read_csv(data_file)
    st.dataframe(df)
    st.download_button("⬇️ Unduh CSV", df.to_csv(index=False), file_name="data_mood.csv", mime="text/csv")

# ========== Reset Data ==========
elif menu == "Reset Data":
    st.header("⚠️ Reset Data")
    if st.button("Hapus Semua Data"):
        df = pd.DataFrame(columns=["Tanggal", "Username", "Mood", "Akademik", "Sosial", "Kesehatan", "Lainnya"])
        df.to_csv(data_file, index=False)
        st.success("Semua data telah dihapus.")

# ========== Tentang ==========
elif menu == "Tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown("""
    **SmartMood Tracker** membantu pengguna mencatat mood harian dan aktivitas mereka dalam berbagai kategori.

    Dikembangkan untuk meningkatkan kesadaran diri dan keseimbangan aktivitas.
    """)

# ========== Logout ==========
elif menu == "Logout":
    st.session_state.login = False
    st.experimental_rerun()

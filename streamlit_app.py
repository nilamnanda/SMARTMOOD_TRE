import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import random

# ========== Konfigurasi Awal ==========
st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood Tracker")

DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ========== Login Simulasi ==========
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.login:
    st.subheader("🔐 Masukkan nama pengguna kamu:")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username and password:
            st.session_state.login = True
            st.session_state.username = username
            st.rerun()
        else:
            st.warning("Mohon masukkan username dan password.")
    st.stop()

username = st.session_state.username
filename = f"{DATA_FOLDER}/data_{username}.csv"

st.sidebar.success(f"Login sebagai: {username}")
menu = st.sidebar.radio("Menu", [
    "📅 Input Mood Harian", 
    "📊 Grafik & Heatmap", 
    "📂 Lihat Data", 
    "📌 Statistik", 
    "ℹ️ Tentang Aplikasi", 
    "🧹 Reset Data", 
    "🚪 Logout"
])

# ========== Saran berdasarkan kombinasi mood dan aktivitas ==========
def get_saran(aktivitas, mood):
    saran_dict = {
        "Mengerjakan tugas": ["Lanjutkan konsistensimu!", "Bagus! Jangan lupa istirahat sejenak."],
        "Belajar": ["Coba variasikan metode belajar agar tidak bosan.", "Bagus! Belajar rutin membuahkan hasil."],
        "Membaca": ["Coba baca topik baru hari ini.", "Terus membaca, wawasanmu makin luas!"],
        "Bersosialisasi": ["Waktu bersama teman bisa menyegarkan pikiran.", "Pertahankan koneksi sosialmu!"],
        "Bertemu teman": ["Semoga pertemuannya menyenangkan!", "Teman adalah penguat semangat."],
        "Bergabung dalam komunitas": ["Coba aktif berdiskusi ya!", "Pengalaman baru bisa kamu dapat dari sini."],
        "Menonton": ["Pastikan tetap seimbang dengan waktu produktif ya.", "Tonton hal yang menginspirasi!"] ,
        "Bermain game": ["Ingat waktu ya! Jangan sampai lupa kewajiban.", "Gaming boleh, asal tetap terkontrol."],
        "Tidur cukup": ["Kualitas tidur yang baik bantu jaga mood.", "Pertahankan pola tidur sehatmu."],
        "Begadang": ["Coba atur waktu tidur agar lebih teratur.", "Terlalu sering begadang bisa menurunkan performa harian."]
    }
    return random.choice(saran_dict.get(aktivitas, ["Lanjutkan aktivitas positifmu!"]))

# ========== Penilaian Mood Berdasarkan Aktivitas ==========
def penilaian_mood(mood, aktivitas):
    aktivitas_negatif = ["Begadang"]
    aktivitas_positif = ["Tidur cukup", "Belajar", "Mengerjakan tugas", "Membaca", "Bersosialisasi", "Bertemu teman", "Bergabung dalam komunitas"]

    if aktivitas in aktivitas_negatif:
        if mood >= 4:
            return "⚠️ Mood tampak baik tapi aktivitas kurang sehat"
    elif aktivitas in aktivitas_positif:
        if mood <= 2:
            return "😟 Aktivitasmu baik, mungkin ada faktor lain yang memengaruhi mood"
    return "✅ Mood dan aktivitas tampak sejalan"

# ========== Input Mood Harian ==========
if menu == "📅 Input Mood Harian":
    st.subheader("📅 Input Mood dan Aktivitas Harian")
    tanggal = st.date_input("Tanggal", datetime.now().date())
    mood = st.slider("Skor Mood (1=buruk, 5=baik)", 1, 5, 3)

    aktivitas_kategori = st.selectbox("Pilih kategori aktivitas", ["Akademik", "Sosial", "Lainnya"])

    if aktivitas_kategori == "Akademik":
        aktivitas_opsi = ["Mengerjakan tugas", "Belajar", "Membaca"]
    elif aktivitas_kategori == "Sosial":
        aktivitas_opsi = ["Bersosialisasi", "Bertemu teman", "Bergabung dalam komunitas"]
    else:
        aktivitas_opsi = ["Menonton", "Bermain game", "Tidur cukup", "Begadang"]

    aktivitas = st.selectbox("Pilih aktivitas yang dilakukan", aktivitas_opsi)
    saran = get_saran(aktivitas, mood)
    evaluasi = penilaian_mood(mood, aktivitas)

    if st.button("📅 Simpan"):
        new_row = pd.DataFrame([{
            "Tanggal": tanggal,
            "Aktivitas": aktivitas,
            "Kategori": aktivitas_kategori,
            "Mood": mood,
            "Saran": saran,
            "Evaluasi": evaluasi
        }])
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
        df.to_csv(filename, index=False)
        st.success("✅ Data berhasil disimpan!")
        st.info(f"💡 Saran: {saran}")
        st.info(f"🧠 Evaluasi: {evaluasi}")

# ========== Grafik & Heatmap ==========
elif menu == "📊 Grafik & Heatmap":
    st.subheader("📈 Grafik & Heatmap Mood")
    if not os.path.exists(filename):
        st.info("Belum ada data untuk ditampilkan.")
    else:
        df = pd.read_csv(filename)
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df = df.sort_values("Tanggal")

        df["Week"] = df["Tanggal"].dt.isocalendar().week
        weekly_mood = df.groupby("Week")["Mood"].mean()
        st.line_chart(weekly_mood)

        df["Weekday"] = df["Tanggal"].dt.weekday
        weeks = sorted(df["Week"].unique())
        heatmap_data = np.full((7, len(weeks)), np.nan)
        week_map = {week: i for i, week in enumerate(weeks)}

        for _, row in df.iterrows():
            heatmap_data[int(row["Weekday"]), week_map[row["Week"]]] = row["Mood"]

        fig, ax = plt.subplots(figsize=(10, 4))
        cax = ax.imshow(heatmap_data, cmap="YlOrBr", aspect="auto", vmin=1, vmax=5)
        ax.set_yticks(np.arange(7))
        ax.set_yticklabels(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"])
        ax.set_xticks(np.arange(len(weeks)))
        ax.set_xticklabels([f"Minggu {w}" for w in weeks])
        for i in range(7):
            for j in range(len(weeks)):
                if not np.isnan(heatmap_data[i, j]):
                    ax.text(j, i, int(heatmap_data[i, j]), ha="center", va="center", color="black")
        plt.colorbar(cax, ax=ax, label="Mood")
        st.pyplot(fig)

# ========== Tampilkan Data ==========
elif menu == "📂 Lihat Data":
    st.subheader("📂 Data Tersimpan")
    if not os.path.exists(filename):
        st.warning("Belum ada data.")
    else:
        df = pd.read_csv(filename)
        st.dataframe(df)
        st.download_button("⬇️ Unduh CSV", data=df.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")

# ========== Statistik ==========
elif menu == "📌 Statistik":
    st.subheader("📌 Statistik Singkat")
    if not os.path.exists(filename):
        st.warning("Belum ada data.")
    else:
        df = pd.read_csv(filename)
        st.metric("Hari tercatat", df["Tanggal"].nunique())
        st.metric("Mood rata-rata", round(df["Mood"].mean(), 2))
        st.metric("Aktivitas unik", df["Aktivitas"].nunique())

# ========== Tentang ==========
elif menu == "ℹ️ Tentang Aplikasi":
    st.subheader("ℹ️ Info Aplikasi")
    st.markdown("""
    **SmartMood Tracker** adalah aplikasi pelacak suasana hati harian.
    - Input mood dan aktivitas
    - Lihat grafik dan heatmap
    - Evaluasi kombinasi aktivitas & mood
    - Unduh data pribadi
    """)

# ========== Reset Data ==========
elif menu == "🧹 Reset Data":
    if st.button("🗑️ Hapus semua data?"):
        if os.path.exists(filename):
            os.remove(filename)
            st.success("Data berhasil dihapus!")

# ========== Logout ==========
elif menu == "🚪 Logout":
    st.session_state.clear()
    st.success("Berhasil logout.")
    st.rerun()

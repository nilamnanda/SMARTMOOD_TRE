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

# ========== Fungsi Tambahan ==========
aktivitas_negatif = ["berdebat", "tidak produktif", "malas", "tidak ngapa-ngapain", "marah"]
aktivitas_positif = ["olahraga", "belajar", "membaca", "meditasi", "bertemu teman", "kerja"]
saran_bahagia = [
    "Tetap pertahankan semangatmu hari ini!",
    "Bagikan kebahagiaanmu ke orang lain!",
    "Cari cara baru untuk bersyukur hari ini!",
    "Jaga kesehatan fisik dan mentalmu!",
    "Gunakan energi positif ini untuk menyelesaikan tugas penting!",
    "Tantang dirimu dengan sesuatu yang baru dan menyenangkan!",
    "Ajak orang terdekat untuk merayakan momen baikmu!"
]

aktivitas_opsi = aktivitas_positif + aktivitas_negatif + ["istirahat", "menonton", "jalan-jalan", "mendengarkan musik", "masak"]


def klasifikasi_mood(mood, aktivitas):
    aktivitas_lower = aktivitas.lower()
    if any(neg in aktivitas_lower for neg in aktivitas_negatif):
        if mood >= 4:
            return "Campur Aduk"
        elif mood <= 2:
            return "Sedih"
    if any(pos in aktivitas_lower for pos in aktivitas_positif):
        if mood >= 4:
            return "Bahagia"
    if mood <= 2:
        return "Sedih"
    elif mood == 3:
        return "Netral"
    return "Cukup Senang"

def saran_mood(klasifikasi):
    if klasifikasi == "Bahagia":
        return random.choice(saran_bahagia)
    elif klasifikasi == "Sedih":
        return "Coba lakukan aktivitas yang kamu sukai atau berbicara dengan teman."
    elif klasifikasi == "Campur Aduk":
        return "Mungkin kamu merasa bingung hari ini. Luangkan waktu untuk refleksi."
    elif klasifikasi == "Netral":
        return "Hari yang biasa saja. Coba lakukan sesuatu yang menyenangkan."
    return "Terus jaga keseimbangan harimu."

# ========== Input Mood Harian ==========
if menu == "📅 Input Mood Harian":
    st.subheader("📅 Input Mood dan Aktivitas Harian")
    tanggal = st.date_input("Tanggal", datetime.now().date())
    aktivitas = st.selectbox("Pilih aktivitas hari ini", sorted(aktivitas_opsi))
    mood = st.slider("Skor Mood (1=buruk, 5=baik)", 1, 5, 3)

    if st.button("📅 Simpan"):
        klasifikasi = klasifikasi_mood(mood, aktivitas)
        saran = saran_mood(klasifikasi)
        new_row = pd.DataFrame([{
            "Tanggal": tanggal,
            "Aktivitas": aktivitas,
            "Mood": mood,
            "Klasifikasi": klasifikasi,
            "Saran": saran
        }])
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
        df.to_csv(filename, index=False)
        st.success(f"✅ Data berhasil disimpan! Mood kamu diklasifikasikan sebagai: {klasifikasi}")
        st.info(f"💡 Saran: {saran}")

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
    - Dapatkan saran dan kutipan
    - Lihat grafik dan heatmap
    - Unduh dan reset data
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

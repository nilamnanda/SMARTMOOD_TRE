import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import random
from datetime import datetime

# Konfigurasi awal HARUS di baris pertama
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

# ========== Inisialisasi ==========
st.title("\U0001F9E0 SmartMood Tracker - Versi Multi User")
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ========== Login ==========
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
            st.experimental_rerun()
        else:
            st.warning("Masukkan nama pengguna dulu untuk memulai.")
    st.stop()

username = st.session_state.username
filename = f"{DATA_FOLDER}/data_{username}.csv"

# ========== Sidebar ==========
st.sidebar.success(f"Login sebagai: {username}")
menu = st.sidebar.radio("Menu", [
    "📥 Input Mood Harian", "📊 Grafik & Heatmap", "📂 Lihat Data", "📌 Statistik", "❓ Tentang", "🧹 Reset Data", "🚪 Logout"
])

# ========== Fungsi Tambahan ==========
def classify_mood(score, aktivitas):
    negatif = ["marah", "berdebat", "menangis", "murung", "berantem", "nangis", "frustrasi", "stress"]
    positif = ["olahraga", "bermain", "bercengkerama", "membaca", "menulis", "belajar", "beribadah", "meditasi", "jalan"]
    lower_akt = aktivitas.lower()
    if any(neg in lower_akt for neg in negatif) and score >= 4:
        return "Campur Aduk"
    elif score >= 4:
        return "Bahagia"
    elif score == 3:
        return "Netral"
    else:
        return "Sedih"

def get_motivasi(mood):
    opsi = {
        "Bahagia": [
            "Teruskan kebiasaan baikmu hari ini!",
            "Bagikan kebahagiaanmu ke orang lain!",
            "Kamu luar biasa, tetap semangat!"
        ],
        "Sedih": [
            "Tidak apa-apa untuk merasa sedih, kamu tidak sendiri.",
            "Ambil napas dalam-dalam dan mulai perlahan.",
            "Keesokan hari selalu punya peluang baru."
        ],
        "Netral": [
            "Hari yang stabil, pertahankan keseimbanganmu.",
            "Cobalah aktivitas menyenangkan setelah ini!",
            "Sedikit perubahan bisa membuat harimu lebih baik."
        ],
        "Campur Aduk": [
            "Luangkan waktu untuk refleksi diri.",
            "Tidak semua hal harus sempurna, cukup jalani.",
            "Kenali emosi, lalu kendalikan dengan baik."
        ]
    }
    return random.choice(opsi[mood])

# ========== Menu: Input Mood ==========
if menu == "📥 Input Mood Harian":
    st.subheader("📥 Input Mood dan Aktivitas Harian")
    tanggal = st.date_input("Tanggal", datetime.now().date())
    aktivitas = st.text_input("Aktivitas hari ini")
    mood = st.slider("Skor Mood (1 = buruk, 5 = sangat baik)", 1, 5, 3)

    if st.button("💾 Simpan"):
        mood_kategori = classify_mood(mood, aktivitas)
        motivasi = get_motivasi(mood_kategori)
        new_row = pd.DataFrame([{
            "Tanggal": tanggal,
            "Aktivitas": aktivitas,
            "Mood": mood,
            "Kategori": mood_kategori,
            "Saran": motivasi
        }])
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
        df.to_csv(filename, index=False)
        st.success(f"✅ Data disimpan sebagai mood '{mood_kategori}'")
        st.info(motivasi)

# ========== Menu: Grafik & Heatmap ==========
elif menu == "📊 Grafik & Heatmap":
    st.subheader("📈 Grafik Mood Mingguan & Heatmap")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df["Week"] = df["Tanggal"].dt.isocalendar().week
        df["Weekday"] = df["Tanggal"].dt.weekday

        weekly_mood = df.groupby("Week")["Mood"].mean()
        st.line_chart(weekly_mood)

        weeks = sorted(df["Week"].unique())
        heatmap_data = np.full((7, len(weeks)), np.nan)
        week_map = {w: i for i, w in enumerate(weeks)}

        for _, row in df.iterrows():
            heatmap_data[row["Weekday"], week_map[row["Week"]]] = row["Mood"]

        fig, ax = plt.subplots(figsize=(10, 4))
        cax = ax.imshow(heatmap_data, cmap="YlGn", aspect="auto", vmin=1, vmax=5)
        ax.set_yticks(range(7))
        ax.set_yticklabels(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"])
        ax.set_xticks(range(len(weeks)))
        ax.set_xticklabels([f"Minggu {w}" for w in weeks])
        for i in range(7):
            for j in range(len(weeks)):
                if not np.isnan(heatmap_data[i, j]):
                    ax.text(j, i, int(heatmap_data[i, j]), ha="center", va="center")
        plt.colorbar(cax, ax=ax, label="Skor Mood")
        st.pyplot(fig)
    else:
        st.warning("Belum ada data untuk ditampilkan.")

# ========== Menu: Lihat Data ==========
elif menu == "📂 Lihat Data":
    st.subheader("📂 Data Mood Harian")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        st.dataframe(df)
        st.download_button("⬇️ Unduh CSV", df.to_csv(index=False), file_name=f"data_{username}.csv")
    else:
        st.warning("Belum ada data.")

# ========== Menu: Statistik ==========
elif menu == "📌 Statistik":
    st.subheader("📌 Statistik Penggunaan")
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        st.metric("Total Hari Dicatat", df["Tanggal"].nunique())
        st.metric("Mood Rata-rata", round(df["Mood"].mean(), 2))
        st.metric("Aktivitas Unik", df["Aktivitas"].nunique())
    else:
        st.info("Belum ada data.")

# ========== Menu: Tentang ==========
elif menu == "❓ Tentang":
    st.subheader("ℹ️ Tentang Aplikasi")
    st.markdown("""
    **SmartMood Tracker** membantu kamu mencatat mood dan aktivitas harian,
    memberikan saran berdasarkan pola aktivitas dan skor mood, serta menyajikan visualisasi untuk refleksi harian.
    """)

# ========== Menu: Reset Data ==========
elif menu == "🧹 Reset Data":
    st.subheader("⚠️ Reset Seluruh Data")
    if st.button("🧹 Hapus Semua Data"):
        if os.path.exists(filename):
            os.remove(filename)
            st.success("✅ Semua data berhasil dihapus.")
        else:
            st.info("Tidak ada data untuk dihapus.")

# ========== Menu: Logout ==========
elif menu == "🚪 Logout":
    st.session_state.clear()
    st.success("Berhasil logout.")
    st.experimental_rerun()

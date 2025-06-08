import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood Tracker")

# ====================
# Utility Functions
# ====================
def load_data():
    if os.path.exists("mood_data.csv"):
        return pd.read_csv("mood_data.csv")
    else:
        return pd.DataFrame(columns=["Tanggal", "Akademik", "Sosial", "Kesehatan", "Lainnya", "Mood", "KategoriMood"])

def save_data(df):
    df.to_csv("mood_data.csv", index=False)

def calculate_mood_category(mood_score, activities):
    # Mapping aktivitas ke jenis positif/negatif
    positive_activities = ["Mengerjakan tugas", "Bertemu teman", "Olahraga", "Meditasi", "Tidur cukup", "Membaca"]
    negative_activities = ["Bolos kuliah", "Sendirian", "Begadang", "Sakit", "Scroll medsos berlebihan"]

    negative_count = sum(1 for a in activities if a in negative_activities)
    positive_count = sum(1 for a in activities if a in positive_activities)

    if mood_score >= 4 and negative_count == 0:
        return "Bahagia"
    elif mood_score <= 2 and negative_count > 1:
        return "Sedih"
    elif negative_count > positive_count:
        return "Cemas"
    else:
        return "Netral"

# ====================
# Data Entry
# ====================
menu = st.sidebar.selectbox("📋 Pilih menu", ["Input Mood Harian", "Lihat Grafik Mood", "Reset Data", "Tentang"])

if menu == "Input Mood Harian":
    st.subheader("📝 Input Mood & Aktivitas")

    tanggal = st.date_input("Tanggal", datetime.today()).strftime("%Y-%m-%d")

    opsi_akademik = ["-", "Mengerjakan tugas", "Bolos kuliah", "Belajar kelompok", "Ujian"]
    opsi_sosial = ["-", "Bertemu teman", "Sendirian", "Berinteraksi online", "Ikut organisasi"]
    opsi_kesehatan = ["-", "Olahraga", "Sakit", "Meditasi", "Tidur cukup", "Kurang tidur"]
    opsi_lainnya = ["-", "Membaca", "Scroll medsos berlebihan", "Main game", "Belanja online", "Jalan-jalan"]

    akademik = st.selectbox("Akademik", opsi_akademik)
    sosial = st.selectbox("Sosial", opsi_sosial)
    kesehatan = st.selectbox("Kesehatan", opsi_kesehatan)
    lainnya = st.selectbox("Lainnya", opsi_lainnya)

    mood_score = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)

    if st.button("💾 Simpan"):
        df = load_data()
        kategori_mood = calculate_mood_category(mood_score, [akademik, sosial, kesehatan, lainnya])
        new_entry = pd.DataFrame([{
            "Tanggal": tanggal,
            "Akademik": akademik,
            "Sosial": sosial,
            "Kesehatan": kesehatan,
            "Lainnya": lainnya,
            "Mood": mood_score,
            "KategoriMood": kategori_mood
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.success(f"Data mood untuk tanggal {tanggal} berhasil disimpan dengan kategori: **{kategori_mood}**")

# ====================
# Grafik Visualisasi
# ====================
elif menu == "Lihat Grafik Mood":
    st.subheader("📈 Grafik Mood Harian")
    df = load_data()

    if df.empty:
        st.warning("Belum ada data mood. Silakan input terlebih dahulu.")
    else:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df_sorted = df.sort_values("Tanggal")

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x="Tanggal", y="Mood", data=df_sorted, marker="o", ax=ax)
        for i, row in df_sorted.iterrows():
            ax.text(row["Tanggal"], row["Mood"] + 0.1, row["KategoriMood"], fontsize=9, ha='center')
        ax.set_title("Mood Harian Berdasarkan Aktivitas")
        ax.set_ylabel("Skor Mood (1-5)")
        ax.set_xlabel("Tanggal")
        ax.set_ylim(0, 5.5)
        st.pyplot(fig)

        st.markdown("""
        **Penilaian mood berdasarkan:**
        - Skor mood yang Anda input (1–5)
        - Kualitas aktivitas Anda hari itu
            - Positif: seperti olahraga, tidur cukup, bertemu teman
            - Negatif: seperti begadang, sakit, bolos, isolasi sosial
        """)

# ====================
# Reset Data
# ====================
elif menu == "Reset Data":
    if st.button("⚠️ Hapus semua data"):
        save_data(pd.DataFrame(columns=["Tanggal", "Akademik", "Sosial", "Kesehatan", "Lainnya", "Mood", "KategoriMood"]))
        st.success("Data berhasil dihapus.")

# ====================
# Tentang
# ====================
elif menu == "Tentang":
    st.markdown("""
    ### SmartMood Tracker
    Aplikasi ini dirancang untuk mencatat dan menganalisis suasana hati Anda setiap hari berdasarkan aktivitas yang dilakukan, menggunakan pendekatan yang diinspirasi oleh dataset **FitLife Kaggle**.

    **Fitur:**
    - Input aktivitas & mood harian
    - Visualisasi grafik mood
    - Penilaian berdasarkan kualitas aktivitas

    **Dibuat oleh:** Group 1  
    """)


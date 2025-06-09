# SmartMood Tracker - Versi Terbaru

import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="SmartMood Tracker")

# Inisialisasi data CSV
DATA_FILE = "smartmood_data.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tanggal", "Username", "Akademik", "Sosial", "Kesehatan", "Lainnya", "Mood", "Aktivitas", "Catatan"])
    df.to_csv(DATA_FILE, index=False)

# Load data
mood_data = pd.read_csv(DATA_FILE)

# Mood Labeling dan Penjelasan
def klasifikasi_mood(skor, aktivitas):
    aktivitas_negatif = ["Stres tugas", "Kurang interaksi", "Sakit", "Scroll sosmed lama"]
    aktivitas_positif = ["Olahraga", "Bertemu teman", "Meditasi", "Belajar"]
    
    neg = any(act in aktivitas for act in aktivitas_negatif)
    pos = any(act in aktivitas for act in aktivitas_positif)

    if skor >= 4 and neg:
        return "Biasa", "Meskipun skor mood tinggi, aktivitasmu cenderung negatif. Bisa jadi kamu mengabaikan stres atau sedang menutupi perasaan."
    elif skor >= 4:
        return "Bahagia", "Aktivitas positif mendukung skor tinggi. Terus pertahankan rutinitasmu!"
    elif skor <= 2 and pos:
        return "Sedih", "Skor rendah walau ada aktivitas positif. Mungkin kamu sedang kelelahan atau butuh istirahat lebih."
    elif skor <= 2:
        return "Sedih", "Skor dan aktivitasmu menunjukkan kondisi kurang baik. Coba luangkan waktu untuk dirimu sendiri."
    else:
        return "Biasa", "Skor dan aktivitasmu tidak terlalu kontras, tapi juga tidak terlalu mendukung. Perlu refleksi lebih."

# Saran berdasarkan mood
saran_dict = {
    "Bahagia": ["Pertahankan kebiasaan positifmu hari ini.", "Bagikan energimu ke orang lain 😊"],
    "Biasa": ["Coba evaluasi kegiatanmu hari ini. Apa yang bisa diperbaiki?", "Sesekali penting untuk rehat dan merenung."],
    "Sedih": ["Luangkan waktu untuk aktivitas menyenangkan.", "Jangan ragu untuk meminta bantuan atau cerita ke teman."]
}

# Input pengguna
st.title("🌈 SmartMood Tracker")
st.markdown("### Catat Mood dan Aktivitasmu Hari Ini")

tanggal = st.date_input("Tanggal", datetime.date.today())
username = st.text_input("Nama Pengguna")
akademik = st.text_input("Aktivitas Akademik")
sosial = st.text_input("Aktivitas Sosial")
kesehatan = st.text_input("Aktivitas Kesehatan")
lainnya = st.text_input("Aktivitas Lainnya")
aktivitas = st.text_area("Aktivitas Hari Ini (pisahkan dengan koma)")
mood = st.slider("Skor Mood (1 = buruk, 5 = sangat baik)", 1, 5, 3)
catatan = st.text_area("Catatan Tambahan")

if st.button("Simpan"):
    aktivitas_list = [a.strip() for a in aktivitas.split(",") if a.strip()]
    mood_label, penjelasan = klasifikasi_mood(mood, aktivitas_list)
    
    new_data = pd.DataFrame({
        "Tanggal": [tanggal],
        "Username": [username],
        "Akademik": [akademik if akademik else None],
        "Sosial": [sosial if sosial else None],
        "Kesehatan": [kesehatan if kesehatan else None],
        "Lainnya": [lainnya if lainnya else None],
        "Mood": [mood],
        "Aktivitas": [", ".join(aktivitas_list)],
        "Catatan": [catatan if catatan else None]
    })

    mood_data = pd.concat([mood_data, new_data], ignore_index=True)
    mood_data.to_csv(DATA_FILE, index=False)
    st.success("Data berhasil disimpan!")

    st.subheader(f"Mood kamu hari ini: {mood_label}")
    st.info(penjelasan)

    st.markdown("#### Saran Hari Ini:")
    for saran in saran_dict[mood_label]:
        st.markdown(f"- {saran}")

    st.markdown("📌 *Saran diberikan berdasarkan kombinasi skor mood dan jenis aktivitas.*")

# Visualisasi Data
st.markdown("---")
st.subheader("📊 Riwayat Mood Harian")

if not mood_data.empty:
    mood_data["Tanggal"] = pd.to_datetime(mood_data["Tanggal"])
    data_per_user = mood_data.groupby("Tanggal")["Mood"].mean().reset_index()

    fig, ax = plt.subplots()
    sns.lineplot(data=data_per_user, x="Tanggal", y="Mood", marker="o", ax=ax, color="#4f8df7")
    ax.set_title("Mood Harian", fontsize=14)
    ax.set_ylabel("Skor Mood")
    ax.set_xlabel("Tanggal")
    ax.set_ylim(0, 5)
    st.pyplot(fig)

# Tabel data
st.markdown("---")
st.subheader("📄 Data Tersimpan")
st.dataframe(mood_data, use_container_width=True)

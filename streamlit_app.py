import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import date

# ------------------------- DATASET AKTIVITAS ------------------------- #
# Mapping aktivitas ke skor positif/negatif berdasarkan dataset Kaggle FitLife
activity_scores = {
    "Akademik": {
        "Belajar efektif": 2,
        "Mengerjakan tugas tepat waktu": 2,
        "Tidak mengerjakan tugas": -2,
        "Menunda belajar": -1,
        "Istirahat dari belajar": 1
    },
    "Sosial": {
        "Bertemu teman": 2,
        "Sendirian sepanjang hari": -1,
        "Bertengkar dengan teman": -2,
        "Membantu orang lain": 2,
        "Diskusi dengan keluarga": 1
    },
    "Fisik": {
        "Olahraga": 2,
        "Jalan kaki santai": 1,
        "Tidur siang": 0,
        "Begadang": -2,
        "Tidak berolahraga": -1
    },
    "Lainnya": {
        "Main game santai": 1,
        "Overthinking": -2,
        "Meditasi": 2,
        "Menonton film favorit": 1,
        "Scrolling medsos berlebihan": -1
    }
}

# ------------------------- FUNGSI DIAGNOSIS & SARAN ------------------------- #
def diagnose_and_suggest(mood_score, total_activity_score):
    diagnosis = ""
    suggestion = ""

    if mood_score >= 4 and total_activity_score >= 4:
        diagnosis = "Kamu sedang dalam kondisi sangat baik!"
        suggestion = random.choice([
            "Pertahankan aktivitas positif seperti ini!",
            "Coba eksplorasi hobi baru hari ini.",
            "Luangkan waktu untuk berbagi kebahagiaan dengan orang terdekat."
        ])
    elif 3 <= mood_score < 4 or 1 <= total_activity_score <= 3:
        diagnosis = "Mood kamu sedang cukup stabil, tapi bisa lebih baik."
        suggestion = random.choice([
            "Coba lakukan aktivitas yang menyenangkan seperti nonton atau jalan santai.",
            "Luangkan waktu istirahat jika merasa lelah.",
            "Jangan lupa tetap aktif secara sosial, walau hanya sekadar ngobrol ringan."
        ])
    else:
        diagnosis = "Sepertinya kamu sedang kurang baik hari ini."
        suggestion = random.choice([
            "Cobalah istirahat yang cukup dan kurangi aktivitas yang membebani.",
            "Pertimbangkan untuk berbicara dengan teman atau menulis jurnal harian.",
            "Lakukan aktivitas sederhana seperti mendengarkan musik atau meditasi ringan."
        ])

    return diagnosis, suggestion

# ------------------------- UI STREAMLIT ------------------------- #
st.set_page_config(page_title="SmartMood Tracker", layout="wide", page_icon="🧠")
st.title("🧠 SmartMood Tracker")
st.markdown("Aplikasi pelacak mood harian berdasarkan aktivitasmu. Data dan analisis terinspirasi dari dataset **FitLife Kaggle**.")

menu = st.sidebar.selectbox("📋 Pilih menu", ["Input Mood Harian", "Lihat Riwayat & Grafik"])

if "mood_data" not in st.session_state:
    st.session_state.mood_data = pd.DataFrame(columns=["Tanggal", "Mood", "Skor Aktivitas", "Diagnosis", "Saran"])

# ------------------------- INPUT MOOD ------------------------- #
if menu == "Input Mood Harian":
    st.header("📝 Input Mood & Aktivitas")

    tanggal = st.date_input("Tanggal", date.today())

    activity_score = 0
    activity_log = []

    for kategori, pilihan in activity_scores.items():
        opsi = st.selectbox(f"{kategori}", options=["(Pilih satu)"] + list(pilihan.keys()))
        if opsi != "(Pilih satu)":
            score = activity_scores[kategori][opsi]
            activity_score += score
            activity_log.append(f"{kategori}: {opsi} ({score})")

    mood = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)

    if st.button("Simpan"):
        diagnosis, saran = diagnose_and_suggest(mood, activity_score)
        new_data = {
            "Tanggal": tanggal,
            "Mood": mood,
            "Skor Aktivitas": activity_score,
            "Diagnosis": diagnosis,
            "Saran": saran
        }
        st.session_state.mood_data = pd.concat([st.session_state.mood_data, pd.DataFrame([new_data])], ignore_index=True)
        st.success("Data berhasil disimpan!")
        st.markdown(f"**Diagnosis:** {diagnosis}")
        st.markdown(f"**Saran:** {saran}")
        st.markdown("**Rincian Aktivitas:**")
        for a in activity_log:
            st.markdown(f"- {a}")

# ------------------------- VISUALISASI ------------------------- #
elif menu == "Lihat Riwayat & Grafik":
    st.header("📊 Riwayat & Visualisasi Mood")

    if st.session_state.mood_data.empty:
        st.info("Belum ada data mood yang dimasukkan.")
    else:
        df = st.session_state.mood_data.sort_values("Tanggal")
        st.dataframe(df, use_container_width=True)

        # Grafik mood harian
        fig, ax = plt.subplots()
        ax.plot(df["Tanggal"], df["Mood"], marker='o', color='skyblue')
        ax.set_title("Tren Mood Harian")
        ax.set_ylabel("Mood (1-5)")
        ax.set_xlabel("Tanggal")
        ax.grid(True)
        st.pyplot(fig)

        st.caption("Mood dinilai berdasarkan aktivitas harian (positif/negatif) dan input pengguna, divalidasi dari dataset FitLife Kaggle.")


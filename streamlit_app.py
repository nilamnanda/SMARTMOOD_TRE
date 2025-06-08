import streamlit as st
import pandas as pd
import random
import datetime
import os

# Inisialisasi CSV jika belum ada
csv_file = 'mood_log.csv'
if not os.path.exists(csv_file):
    df_init = pd.DataFrame(columns=['Tanggal', 'Aktivitas', 'Skor Mood', 'Total Skor'])
    df_init.to_csv(csv_file, index=False)

# Fungsi klasifikasi dan saran berbasis mood
motivational_quotes = [
    "Setiap hari adalah awal yang baru.",
    "Hujan akan berhenti. Tetap semangat.",
    "Kamu sudah bertahan sejauh ini. Lanjutkan.",
    "Waktu sulit akan berlalu.",
    "Kamu tidak sendiri."
]

saran_berdasarkan_mood = {
    1: [
        "Coba bersih-bersih kamar untuk suasana baru.",
        "Jalan santai 10 menit bisa bantu meredakan stres.",
        "Tulis jurnal atau luapkan isi hati di catatan."
    ],
    2: [
        "Beri waktu untuk diri sendiri dan istirahat sejenak.",
        "Dengarkan lagu yang menenangkan.",
        "Hubungi teman terdekat dan curhat ringan."
    ],
    3: [
        "Mood kamu sedang cukup stabil, tapi bisa lebih baik.",
        "Coba lakukan aktivitas yang menyenangkan seperti nonton atau jalan santai.",
        "Main game ringan atau buat playlist favorit."
    ],
    4: [
        "Kamu sedang cukup bahagia, teruskan aktivitas positif.",
        "Bantu orang lain hari ini, itu bisa memperkuat rasa bahagia.",
        "Coba eksplorasi tempat baru atau masakan baru."
    ],
    5: [
        "Mood kamu sangat baik! Bagikan energi positif ke sekitar.",
        "Pertahankan dengan olahraga ringan atau meditasi.",
        "Ambil tantangan kecil yang menyenangkan hari ini."
    ]
}

def diagnosis_mood(skor):
    if skor <= 2:
        return "Mood kamu sedang rendah, jaga diri dan ambil waktu istirahat."
    elif skor == 3:
        return "Mood kamu sedang cukup stabil, tapi bisa lebih baik."
    elif skor >= 4:
        return "Mood kamu tergolong baik, pertahankan!"

def tampilkan_saran(skor):
    saran = random.choice(saran_berdasarkan_mood[skor])
    kutipan = random.choice(motivational_quotes)
    return f"{saran}\n\nMotivasi: {kutipan}"

# Fungsi untuk menghitung total skor berdasarkan aktivitas
aktivitas_positif = ['Olahraga', 'Meditasi', 'Bertemu teman', 'Membaca', 'Berjalan santai']
aktivitas_negatif = ['Begadang', 'Marah-marah', 'Malas gerak', 'Terlalu banyak scroll medsos']

def nilai_aktivitas(aktivitas):
    if aktivitas in aktivitas_positif:
        return 1
    elif aktivitas in aktivitas_negatif:
        return -1
    return 0

# Sidebar menu
menu = st.sidebar.selectbox("\U0001F4D3 Pilih menu", ["Input Mood Harian", "Lihat Riwayat & Grafik"])

if menu == "Input Mood Harian":
    st.title("Catatan Mood Harian")

    aktivitas = st.selectbox("Aktivitas hari ini", aktivitas_positif + aktivitas_negatif + ['Lainnya'])
    skor_mood = st.slider("Rating mood hari ini (1–5)", 1, 5, 3)

    if st.button("Simpan"):
        skor_aktivitas = nilai_aktivitas(aktivitas)
        total_skor = skor_mood + skor_aktivitas

        tanggal = datetime.date.today().strftime('%Y-%m-%d')

        new_row = pd.DataFrame({
            'Tanggal': [tanggal],
            'Aktivitas': [aktivitas],
            'Skor Mood': [skor_mood],
            'Total Skor': [total_skor]
        })

        df = pd.read_csv(csv_file)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(csv_file, index=False)

        st.success("Data berhasil disimpan!")

        st.markdown(f"**Diagnosis:** {diagnosis_mood(skor_mood)}")
        st.markdown(f"**Saran:** {tampilkan_saran(skor_mood)}")
        st.markdown("**Rincian Aktivitas:**")
        st.write(f"Aktivitas: {aktivitas}, Skor Aktivitas: {skor_aktivitas}, Total Skor: {total_skor}")

if menu == "Lihat Riwayat & Grafik":
    st.title("Riwayat dan Grafik Mood")

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.dataframe(df.tail(10))

        st.line_chart(df[['Skor Mood', 'Total Skor']])
        st.bar_chart(df['Skor Mood'])
        st.markdown("Grafik mood harian berdasarkan input pengguna dan aktivitas terkait.")
    else:
        st.warning("Belum ada data tersimpan.")

import streamlit as st
import pandas as pd
import datetime
import altair as alt
import os

# ------------------ Konfigurasi Awal ------------------
st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("📘 SmartMood Tracker")
st.markdown("Deteksi mood otomatis berdasarkan aktivitas harianmu. Yuk mulai!")

# ------------------ Input Harian ------------------
tanggal = st.date_input("📅 Pilih Tanggal", datetime.date.today())

kategori_aktivitas = {
    "Akademik": ["Belajar efektif", "Stres tugas", "Tidak ada kegiatan"],
    "Sosial": ["Ngobrol santai", "Canggung banget", "Tidak berinteraksi"],
    "Kesehatan": ["Olahraga ringan", "Sakit", "Tidur seharian"],
    "Lainnya": ["Belanja banyak", "Main HP terus", "Meditasi"]
}

aktivitas_input = {}
for kategori, opsi in kategori_aktivitas.items():
    aktivitas_input[kategori] = st.selectbox(f"{kategori}", opsi)

# ------------------ Deteksi Mood Otomatis ------------------
aktivitas_negatif = [
    "Stres tugas", "Canggung banget", "Sakit", "Belanja banyak",
    "Main HP terus", "Tidak ada kegiatan", "Tidur seharian", "Tidak berinteraksi"
]
aktivitas_positif = [
    "Belajar efektif", "Ngobrol santai", "Olahraga ringan", "Meditasi"
]

skor = 0
for aktivitas in aktivitas_input.values():
    if aktivitas in aktivitas_positif:
        skor += 1
    elif aktivitas in aktivitas_negatif:
        skor -= 1

if skor >= 2:
    mood = "Bahagia"
elif skor <= -1:
    mood = "Sedih"
else:
    mood = "Biasa"

# ------------------ Simpan ke CSV ------------------
data_file = "mood_data.csv"
new_data = {
    "Tanggal": tanggal.strftime("%Y-%m-%d"),
    "Mood": mood,
    **aktivitas_input
}
df_new = pd.DataFrame([new_data])

if os.path.exists(data_file):
    df = pd.read_csv(data_file)
    df = pd.concat([df, df_new], ignore_index=True)
else:
    df = df_new
df.to_csv(data_file, index=False)

# ------------------ Output Mood ------------------
st.subheader("🎯 Mood Hari Ini")
st.markdown(f"**Mood kamu:** {'😊 Bahagia' if mood == 'Bahagia' else '😐 Biasa' if mood == 'Biasa' else '😔 Sedih'}")

if mood == "Bahagia" and skor <= 0:
    st.warning("⚠️ Mood tinggi tapi aktivitasmu cenderung negatif. Coba evaluasi lebih dalam.")
elif mood == "Biasa":
    st.info("🔄 Harimu cukup netral. Mungkin tidak buruk, tapi bisa lebih baik.")
elif mood == "Sedih":
    st.error("💤 Hari yang berat, jangan lupa istirahat dan sayangi dirimu.")
elif mood == "Bahagia":
    st.success("🌟 Kamu menjalani hari yang positif! Pertahankan semangat ini ya.")

# ------------------ Kutipan Motivasi ------------------
motivasi = {
    "Bahagia": "🌈 Teruskan energi positifmu hari ini!",
    "Biasa": "🪷 Hari ini mungkin datar, tapi malam selalu membawa harapan baru.",
    "Sedih": "🌙 Malam akan berlalu. Pagi membawa kesempatan baru untuk bangkit."
}
st.markdown(f"💡 *{motivasi[mood]}*")

# ------------------ Visualisasi Mood ------------------
st.markdown("## 📊 Mood Tracker Visual")

df = pd.read_csv(data_file)
df['Tanggal'] = pd.to_datetime(df['Tanggal'])

warna_mood = {
    "Bahagia": "#4CAF50",   # Hijau
    "Biasa": "#f48fb1",     # Pink
    "Sedih": "#e57373"      # Merah
}

bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Tanggal:T', title='Tanggal'),
    y=alt.Y('count():Q', title='Jumlah Catatan'),
    color=alt.Color('Mood:N', scale=alt.Scale(domain=list(warna_mood.keys()), range=list(warna_mood.values())), legend=alt.Legend(title="Mood"))
).properties(width=700, height=400)

st.altair_chart(bar_chart, use_container_width=True)

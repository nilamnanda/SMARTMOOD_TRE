import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Inisialisasi data CSV
CSV_FILE = "smartmood_data.csv"

# Load atau inisialisasi DataFrame
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Tanggal", "Username", "Akademik", "Sosial", "Kesehatan", "Lainnya", "Mood", "Aktivitas", "Catatan"])

# Judul Aplikasi
st.title("🌤️ SmartMood Tracker")

# Form Input
with st.form("mood_form"):
    st.subheader("Isi Mood Harianmu")
    tanggal = st.date_input("Tanggal", value=datetime.today())
    username = st.text_input("Username")
    mood = st.slider("Skor Mood (1 = Sangat Buruk, 5 = Sangat Baik)", 1, 5, 3)

    st.write("### Pilih Aktivitas Hari Ini")
    akademik = st.checkbox("Tugas / Belajar")
    sosial = st.checkbox("Bertemu teman / keluarga")
    kesehatan = st.checkbox("Olahraga / Istirahat cukup")
    lainnya = st.checkbox("Aktivitas lainnya")
    aktivitas_lain = st.text_area("Rincian Aktivitas", placeholder="Contoh: Stres tugas, Sakit, Scroll sosmed lama")

    catatan = st.text_input("Catatan tambahan")

    submit = st.form_submit_button("Simpan")

# Simpan data
if submit:
    new_data = {
        "Tanggal": tanggal,
        "Username": username,
        "Akademik": "Tugas / Belajar" if akademik else None,
        "Sosial": "Bertemu teman / keluarga" if sosial else None,
        "Kesehatan": "Olahraga / Istirahat cukup" if kesehatan else None,
        "Lainnya": "Aktivitas lainnya" if lainnya else None,
        "Mood": mood,
        "Aktivitas": aktivitas_lain,
        "Catatan": catatan
    }
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("Mood berhasil disimpan!")

# Tampilkan Dataframe
if not df.empty:
    st.subheader("📊 Data Mood Harian")
    st.dataframe(df.tail(10), use_container_width=True)

    # Grafik Mood
    st.subheader("📈 Grafik Mood Harian")
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df_sorted = df.sort_values(by='Tanggal')

    plt.figure(figsize=(10, 4))
    sns.lineplot(x=df_sorted['Tanggal'], y=df_sorted['Mood'], marker='o', color='skyblue')
    plt.xticks(rotation=45)
    plt.ylim(0, 5.5)
    plt.title("Mood Over Time")
    plt.ylabel("Skor Mood")
    plt.xlabel("Tanggal")
    st.pyplot(plt)

    # Diagnosa dan Saran
    st.subheader("🧠 Diagnosa & Saran")
    latest = df_sorted.iloc[-1]
    aktivitas = latest['Aktivitas'].lower() if pd.notna(latest['Aktivitas']) else ""

    penjelasan = ""
    saran = ""
    mood_value = latest['Mood']

    aktivitas_buruk = any(neg in aktivitas for neg in ["stres", "capek", "sakit", "kurang interaksi", "scroll sosmed"])

    if mood_value == 3:
        if aktivitas_buruk:
            penjelasan = "Mood kamu tergolong 'biasa saja' karena meskipun skornya netral, aktivitasmu cenderung negatif."
        else:
            penjelasan = "Mood kamu netral. Mungkin harimu berjalan biasa saja tanpa hal menonjol."
    elif mood_value >= 4:
        if aktivitas_buruk:
            penjelasan = "Meski skor mood tinggi, ada aktivitas negatif. Perlu refleksi lebih lanjut."
        else:
            penjelasan = "Mood kamu baik! Aktivitas mendukung suasana hati positif."
    elif mood_value <= 2:
        penjelasan = "Mood kamu rendah. Aktivitas negatif dapat memperparah kondisi."

    # Saran berdasarkan mood dan aktivitas
    if mood_value <= 2:
        saran = "Coba istirahat cukup, hindari stres, dan cari teman bicara."
    elif mood_value == 3:
        saran = "Mungkin kamu butuh selingan ringan, seperti jalan-jalan atau menonton film lucu."
    elif mood_value >= 4:
        if aktivitas_buruk:
            saran = "Jaga mood baikmu dengan aktivitas yang sehat dan hindari kebiasaan buruk yang bisa mengganggu."
        else:
            saran = "Pertahankan rutinitas positifmu. Kamu berada di jalur yang baik!"

    st.info(f"**Penjelasan:** {penjelasan}")
    st.success(f"**Saran:** {saran}")
else:
    st.warning("Belum ada data yang tersimpan.")

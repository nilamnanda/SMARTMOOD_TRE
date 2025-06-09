import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="SmartMood Tracker", layout="wide")

# Dummy user login
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username and password:
            return True
        else:
            st.sidebar.warning("Please enter username and password.")
    return False

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("mood_data.csv", parse_dates=["Tanggal"])
        df["Tanggal"] = pd.to_datetime(df["Tanggal"]).dt.date
        return df
    except:
        return pd.DataFrame(columns=["Tanggal", "Mood", "Aktivitas", "Kategori", "Skor"])

# Save new entry
def save_data(new_entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("mood_data.csv", index=False)

# Klasifikasi aktivitas: positif/negatif/netral
aktivitas_positif = ["Olahraga", "Meditasi", "Baca Buku", "Belajar", "Bersosialisasi", "Produktif"]
aktivitas_negatif = ["Begadang", "Terlalu Lama Main Game", "Melamun", "Stres", "Menunda-nunda", "Mengeluh"]
aktivitas_netral = ["Makan", "Tidur", "Jalan-jalan", "Dengar Musik", "Menonton"]

# Motivasi dan refleksi
motivasi = {
    "Bahagia": [
        "Pertahankan semangat positifmu!",
        "Kamu sedang dalam jalur yang baik. Teruskan!",
        "Hari ini kamu bersinar terang. 😊"
    ],
    "Sedih": [
        "Tidak apa-apa merasa sedih. Luangkan waktu untuk dirimu.",
        "Kesedihan adalah bagian dari proses. Kamu kuat!",
        "Besok adalah kesempatan baru untuk merasa lebih baik."
    ],
    "Biasa": [
        "Hari yang biasa pun berharga.",
        "Gunakan waktu ini untuk refleksi dan recharge.",
        "Tidak setiap hari harus luar biasa — cukup bernapas dan bersyukur."
    ],
    "Refleksi": [
        "Moodmu tinggi tapi aktivitas kurang sehat. Jaga keseimbangan ya!",
        "Kamu terlihat baik, tapi coba pikirkan kembali pola harianmu.",
        "Perhatikan tanda-tanda kecil kelelahan atau distraksi."
    ]
}

# Diagnosis dan saran berdasarkan aktivitas
def get_diagnosis(mood, aktivitas, skor):
    if any(a in aktivitas for a in aktivitas_negatif) and skor > 7:
        return "Bahagia", motivasi["Refleksi"]
    elif skor >= 8:
        return "Bahagia", motivasi["Bahagia"]
    elif skor >= 5:
        return "Biasa", motivasi["Biasa"]
    else:
        return "Sedih", motivasi["Sedih"]

def classify_activity(aktivitas):
    if aktivitas in aktivitas_positif:
        return "Positif"
    elif aktivitas in aktivitas_negatif:
        return "Negatif"
    elif aktivitas in aktivitas_netral:
        return "Netral"
    else:
        return "Tidak Diketahui"

# Input harian
def input_mood():
    st.subheader("🌤️ Input Mood Harian")
    tanggal = st.date_input("Tanggal", datetime.today())
    mood = st.slider("Seberapa baik perasaanmu hari ini?", 1, 10, 5)
    aktivitas = st.multiselect("Pilih aktivitasmu hari ini:", aktivitas_positif + aktivitas_negatif + aktivitas_netral)

    if st.button("Simpan"):
        kategori_list = [classify_activity(a) for a in aktivitas]
        mood_status, saran_list = get_diagnosis(mood, aktivitas, mood)
        new_entry = {
            "Tanggal": tanggal,
            "Mood": mood_status,
            "Aktivitas": ", ".join(aktivitas),
            "Kategori": ", ".join(kategori_list),
            "Skor": mood
        }
        save_data(new_entry)
        st.success(f"Mood kamu hari ini: **{mood_status}**")
        st.info("Saran untukmu hari ini:")
        for s in saran_list:
            st.write(f"- {s}")

# Visualisasi mood
def visualize():
    st.subheader("📈 Visualisasi Mood")
    df = load_data()
    if df.empty:
        st.warning("Belum ada data mood.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Tren Mood Harian")
        df_plot = df.sort_values("Tanggal")
        plt.figure(figsize=(10, 4))
        sns.lineplot(x="Tanggal", y="Skor", data=df_plot, marker="o", color="#4f8a8b")
        plt.xticks(rotation=45)
        plt.ylabel("Skor Mood")
        st.pyplot(plt.gcf())

    with col2:
        st.write("### Distribusi Mood")
        plt.figure(figsize=(6, 4))
        sns.countplot(x="Mood", data=df, palette="Set2")
        plt.ylabel("Jumlah Hari")
        st.pyplot(plt.gcf())

    st.markdown("""
    **Keterangan Mood:**
    - **Bahagia**: Skor tinggi dan aktivitas positif
    - **Sedih**: Skor rendah
    - **Biasa**: Skor sedang atau aktivitas netral
    - **Refleksi**: Skor tinggi tapi aktivitas negatif
    """)

# Main
st.title("🧠 SmartMood Tracker")
st.markdown("Pantau mood harianmu berdasarkan aktivitas dan skor keseharian dengan motivasi dan visualisasi interaktif.")

if login():
    tab1, tab2 = st.tabs(["📋 Input Mood", "📊 Visualisasi"])
    with tab1:
        input_mood()
    with tab2:
        visualize()
else:
    st.warning("Silakan login dari sidebar untuk menggunakan aplikasi.")

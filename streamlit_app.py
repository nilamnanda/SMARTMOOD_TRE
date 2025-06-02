import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood Tracker - Versi Kompleks")

# Inisialisasi skor aktivitas
aktivitas_skor = {
    "Olahraga": 3,
    "Tidur cukup": 2,
    "Main HP berlebihan": -2,
    "Makan sehat": 2,
    "Tugas selesai": 4,
    "Overthinking": -3,
    "Nugas mendekati deadline": -2,
    "Belajar santai": 1,
    "Nonton film": 1,
    "Scroll TikTok": -1,
    "Curhat dengan teman": 3
}

# Fungsi klasifikasi mood
def classify_mood(score):
    if score >= 8:
        return "Bahagia", "Pertahankan rutinitas positif kamu!"
    elif score >= 5:
        return "Cukup Baik", "Kamu berada di jalur yang benar."
    elif score >= 2:
        return "Biasa saja", "Coba tambahkan aktivitas menyenangkan."
    elif score >= 0:
        return "Kurang Baik", "Coba hindari hal-hal negatif."
    else:
        return "Buruk", "Butuh self-care dan support segera."

# Fungsi untuk menyimpan data
@st.cache_data

def load_data(file):
    return pd.read_csv(file)

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(filename, index=False)

# Fungsi rekursif (untuk penilaian UAS)
def recursive_sum(lst):
    if not lst:
        return 0
    return lst[0] + recursive_sum(lst[1:])

# Fungsi rekomendasi berdasarkan histori

def rekomendasi_berbasis_histori(df):
    top_mood = df[df['Mood'].str.contains("Bahagia")]
    if top_mood.empty:
        return "Belum cukup data bahagia untuk rekomendasi."
    rekom = top_mood['Aktivitas'].value_counts().idxmax()
    return f"Berdasarkan histori, coba lakukan aktivitas: **{rekom}** untuk mood terbaik!"

# Menu navigasi
menu = st.sidebar.selectbox("Menu", ["Input Harian", "Grafik Mood", "Data CSV", "Simulasi Mood"])
file = "smartmood_data.csv"

if menu == "Input Harian":
    st.header("✍️ Catat Mood Harian Kamu")
    nama = st.text_input("Nama lengkap")
    aktivitas = []
    for i in range(1, 4):
        pilihan = st.selectbox(f"Aktivitas #{i}", ["(Pilih aktivitas)"] + list(aktivitas_skor.keys()), key=i)
        if pilihan != "(Pilih aktivitas)":
            aktivitas.append(pilihan)

    rating = st.slider("Rating mood kamu hari ini (1-5)", 1, 5)

    if st.button("💾 Simpan Catatan"):
        skor_total = recursive_sum([aktivitas_skor.get(a, 0) for a in aktivitas]) + rating * 2
        mood, saran = classify_mood(skor_total)
        today = datetime.now().strftime("%Y-%m-%d")
        data = [{"Tanggal": today, "Nama": nama, "Aktivitas": ", ".join(aktivitas), "Rating": rating, "Skor": skor_total, "Mood": mood}]
        save_to_csv(data, file)
        st.success(f"Data disimpan! Mood kamu hari ini: {mood} 🧠")
        st.info(f"Saran: {saran}")

        if os.path.exists(file):
            df_histori = pd.read_csv(file)
            st.info(rekomendasi_berbasis_histori(df_histori))

elif menu == "Grafik Mood":
    st.header("📊 Grafik Analisis Mood")
    if os.path.exists(file):
        df = pd.read_csv(file)
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])

        st.subheader("Mood Score per Hari")
        fig, ax = plt.subplots()
        df_grouped = df.groupby("Tanggal")["Skor"].mean()
        ax.plot(df_grouped.index, df_grouped.values, marker='o')
        ax.set_ylabel("Skor")
        ax.set_title("Mood Score Harian")
        st.pyplot(fig)

        st.subheader("📈 Tren Skor Mingguan per Kategori")
        last_week = df[df['Tanggal'] >= (datetime.now() - timedelta(days=7))]
        trend_data = last_week.copy()
        trend_data["Kategori"] = trend_data["Aktivitas"].str.split(", ").explode()
        trend_group = trend_data.groupby(["Tanggal", "Kategori"])["Skor"].mean().reset_index()
        pivot = trend_group.pivot(index="Tanggal", columns="Kategori", values="Skor")

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        pivot.plot(ax=ax2, marker='o')
        ax2.set_title("Tren Skor Rata-Rata Mingguan per Kategori")
        ax2.set_ylabel("Skor")
        ax2.legend(title="Kategori")
        st.pyplot(fig2)

        st.subheader("📅 Heatmap Kalender Mood")
        df_calendar = df.groupby("Tanggal")["Skor"].mean().reset_index()
        df_calendar['Tanggal'] = pd.to_datetime(df_calendar['Tanggal'])
        df_calendar['Day'] = df_calendar['Tanggal'].dt.day
        df_calendar['Week'] = df_calendar['Tanggal'].dt.isocalendar().week
        pivot_heatmap = df_calendar.pivot_table(index='Week', columns='Day', values='Skor', aggfunc='mean')

        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.heatmap(pivot_heatmap, cmap="YlGnBu", linewidths=0.5, ax=ax3, cbar_kws={"label": "Skor Mood"})
        ax3.set_title("Heatmap Kalender Mood (mingguan)")
        st.pyplot(fig3)

elif menu == "Data CSV":
    st.header("📂 Data CSV")
    if os.path.exists(file):
        df_user = pd.read_csv(file)
        st.subheader("📊 Tabel Interaktif")
        gb = GridOptionsBuilder.from_dataframe(df_user)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(filterable=True, sortable=True, resizable=True)
        gridOptions = gb.build()
        AgGrid(df_user, gridOptions=gridOptions, height=300)
    else:
        st.warning("Belum ada data.")

elif menu == "Simulasi Mood":
    st.header("🔁 Simulasi Mood Harian")
    aktivitas_simulasi = []
    for i in range(1, 4):
        pilihan = st.selectbox(f"Aktivitas #{i}", ["(Pilih aktivitas)"] + list(aktivitas_skor.keys()), key=f"sim_{i}")
        if pilihan != "(Pilih aktivitas)":
            aktivitas_simulasi.append(pilihan)

    rating_sim = st.slider("Rating mood simulasi (1-5)", 1, 5, 3)

    if st.button("🔍 Simulasikan"):
        skor_total = recursive_sum([aktivitas_skor.get(a, 0) for a in aktivitas_simulasi]) + rating_sim * 2
        mood, saran = classify_mood(skor_total)
        st.success(f"Hasil simulasi mood: {mood}")
        st.info(f"Saran: {saran}")

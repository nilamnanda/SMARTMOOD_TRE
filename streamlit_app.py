# (seluruh import dan pengaturan awal tetap sama)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime, timedelta

# ... (aktivitas_skor, kategori_aktivitas, saran_dict, classify_mood, diagnosis_kaggle tetap sama)

def simpan_data(username, tanggal, aktivitas_data, rating, mood, saran, catatan, diagnosis):
    filename = f"{DATA_FOLDER}/data_{username}.csv"
    records = []
    for kategori, aktivitas in aktivitas_data.items():
        skor = aktivitas_skor.get(aktivitas, 0)
        records.append([tanggal, kategori, aktivitas, skor, rating, mood, saran, catatan, diagnosis])
    df_new = pd.DataFrame(records, columns=["Tanggal", "Kategori", "Aktivitas", "Skor", "Rating", "Mood", "Saran", "Catatan", "Diagnosis"])
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filename, index=False)

# ... fungsi hitung_streak tetap sama

# ========== Streamlit UI ==========

st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("🧠 SmartMood Tracker")
st.write("Refleksi mood kamu berdasarkan aktivitas harian 💡")

# Login sederhana
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.login:
    username = st.text_input("Masukkan username:")
    password = st.text_input("Password (simulasi)", type="password")
    if st.button("🔐 Login"):
        if username and password:
            st.session_state.login = True
            st.session_state.username = username
        else:
            st.warning("Masukkan username dan password dengan benar.")

if st.session_state.login:
    username = st.session_state.username
    st.success(f"Login sebagai **{username}**")
    file = f"{DATA_FOLDER}/data_{username}.csv"

    menu = st.sidebar.selectbox("📋 Menu", [
        "Input Mood Harian", 
        "Lihat Grafik Mood", 
        "Lihat Data CSV", 
        "Reset Data", 
        "Tentang", 
        "Logout"])

    if menu == "Input Mood Harian":
        st.header("✍️ Input Mood & Aktivitas")
        tanggal = st.date_input("Tanggal aktivitas", datetime.now())
        aktivitas_data = {}
        total_skor = 0
        for kategori, daftar in kategori_aktivitas.items():
            pilihan = st.selectbox(f"{kategori}", ["(Pilih satu)"] + daftar, key=kategori)
            if pilihan != "(Pilih satu)":
                aktivitas_data[kategori] = pilihan
                total_skor += aktivitas_skor.get(pilihan, 0)

        rating = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")

        if st.button("✅ Simpan"):
            mood, saran = classify_mood(total_skor + rating * 2)
            diagnosis = diagnosis_kaggle(total_skor + rating * 2)
            simpan_data(username, tanggal.strftime("%Y-%m-%d"), aktivitas_data, rating, mood, saran, catatan, diagnosis)
            st.success(f"Mood kamu hari ini: {mood}")
            st.info(f"Saran: {saran}")
            st.warning(f"🔍 Diagnosis menurut data FitLife: {diagnosis}")

    elif menu == "Lihat Grafik Mood":
        st.header("📊 Grafik Mood Harian")
        if not os.path.exists(file):
            st.warning("Belum ada data.")
        else:
            df = pd.read_csv(file)
            if len(df) < 3:
                st.warning("Data belum cukup (min. 3 hari).")
            else:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'])
                df_daily = df.groupby("Tanggal").mean(numeric_only=True).reset_index()
                warna = df.groupby("Tanggal")["Mood"].last().map(lambda m: "green" if "Bahagia" in m else ("gold" if "Biasa" in m else "blue"))
                fig, ax = plt.subplots(figsize=(10,4))
                ax.bar(df_daily["Tanggal"].dt.strftime("%d-%b"), df_daily["Skor"], color=warna)
                ax.set_title(f"Mood Harian - {username}")
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Skor Mood")
                ax.grid(True)
                st.pyplot(fig)

                streak = hitung_streak(df)
                st.success(f"🔥 Konsistensi: {streak} hari berturut-turut!")

    elif menu == "Lihat Data CSV":
        st.header("📂 Data Aktivitas & Mood")
        if not os.path.exists(file):
            st.warning("Belum ada data.")
        else:
            df_user = pd.read_csv(file)
            st.dataframe(df_user)
            st.download_button("⬇️ Unduh Data CSV", data=df_user.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")

    elif menu == "Reset Data":
        if st.button("❌ Reset semua data"):
            if os.path.exists(file):
                os.remove(file)
                st.success("Data berhasil direset.")
            else:
                st.warning("Tidak ada data untuk dihapus.")

    elif menu == "Tentang":
        st.header("📘 Tentang SmartMood")
        st.markdown("""
        SmartMood Tracker membantumu melacak suasana hati berdasarkan aktivitas harian.  
        Fitur:
        - Input 4 kategori aktivitas & rating harian
        - Klasifikasi otomatis mood
        - Saran empatik & reflektif
        - Grafik perkembangan mood
        - Deteksi *streak* harian (konsistensi)
        - Diagnostik berbasis pola dari dataset FitLife
        - Sekarang mendukung input tanggal manual!
        """)

    elif menu == "Logout":
        st.session_state.clear()
        st.rerun()

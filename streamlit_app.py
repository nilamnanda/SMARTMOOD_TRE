import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Setup awal
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Konfigurasi halaman
st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood Tracker")

# Login user
if "login" not in st.session_state:
    st.session_state.login = False
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
    file = f"{DATA_FOLDER}/data_{username}.csv"
    st.sidebar.title(f"Hai, {username}!")
    menu = st.sidebar.radio("📋 Menu", ["Input Mood", "Lihat Data & Grafik", "Tentang", "Logout"])

    # ====================== INPUT MOOD ======================
    if menu == "Input Mood":
        st.header("📥 Input Mood dan Aktivitas Harian")
        col1, col2 = st.columns(2)
        with col1:
            selected_date = st.date_input("Tanggal", datetime.now())
        with col2:
            activity = st.text_input("Aktivitas hari ini (misal: belajar, olahraga, rebahan)")

        mood = st.slider("Skor Mood (1=buruk, 5=baik)", 1, 5, 3)

        if st.button("💾 Simpan"):
            new_row = {"date": selected_date, "activity": activity, "mood": mood}
            if os.path.exists(file):
                df = pd.read_csv(file)
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            else:
                df = pd.DataFrame([new_row])
            df.to_csv(file, index=False)
            st.success("✅ Data berhasil disimpan!")

    # ====================== LIHAT GRAFIK & DATA ======================
    elif menu == "Lihat Data & Grafik":
        st.header("📊 Data dan Visualisasi Mood")
        if os.path.exists(file):
            df = pd.read_csv(file)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            st.subheader("📅 Data Mood Harian")
            st.dataframe(df, use_container_width=True)

            # Line chart mingguan
            df["week"] = df["date"].dt.isocalendar().week
            weekly_mood = df.groupby("week")["mood"].mean()
            st.subheader("📈 Tren Mood Mingguan")
            st.line_chart(weekly_mood)

            # Heatmap
            st.subheader("🗓️ Heatmap Mood Mingguan")
            df["weekday"] = df["date"].dt.weekday  # 0=Senin
            weeks = sorted(df["week"].unique())
            heatmap_data = np.full((7, len(weeks)), np.nan)
            week_map = {week: i for i, week in enumerate(weeks)}

            for _, row in df.iterrows():
                week_idx = week_map[row["week"]]
                heatmap_data[int(row["weekday"]), week_idx] = row["mood"]

            fig, ax = plt.subplots(figsize=(10, 4))
            cax = ax.imshow(heatmap_data, cmap="YlOrBr", aspect="auto", vmin=1, vmax=5)
            ax.set_yticks(np.arange(7))
            ax.set_yticklabels(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"])
            ax.set_xticks(np.arange(len(weeks)))
            ax.set_xticklabels([f"Minggu {w}" for w in weeks])
            for i in range(7):
                for j in range(len(weeks)):
                    if not np.isnan(heatmap_data[i, j]):
                        ax.text(j, i, int(heatmap_data[i, j]), ha="center", va="center", color="black")
            plt.colorbar(cax, ax=ax, label="Mood")
            st.pyplot(fig)

            # Statistik
            st.subheader("📌 Statistik Ringkas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📆 Hari tercatat", df["date"].nunique())
            with col2:
                st.metric("😊 Mood rata-rata", round(df["mood"].mean(), 2))
            with col3:
                st.metric("🏃 Aktivitas unik", df["activity"].nunique())

            st.download_button("⬇️ Unduh CSV", df.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")
        else:
            st.info("Belum ada data, silakan input terlebih dahulu.")

    # ====================== TENTANG ======================
    elif menu == "Tentang":
        st.header("📘 Tentang SmartMood Tracker")
        st.markdown("""
        SmartMood membantu kamu melacak suasana hati dan aktivitas harian dengan:
        - Input mood berdasarkan aktivitas dan tanggal
        - Visualisasi tren mood mingguan dan heatmap kalender
        - Statistik ringkas dan ekspor data CSV
        - Sistem login per pengguna
        """)

    # ====================== LOGOUT ======================
    elif menu == "Logout":
        st.session_state.clear()
        st.rerun()

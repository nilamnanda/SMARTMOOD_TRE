import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ========== Harus Paling Atas ==========
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

# ========== Folder Simpan ==========
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ========== Simulasi Login ==========
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.login:
    st.title("🔐 Login SmartMood Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username and password:
            st.session_state.login = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.warning("Mohon masukkan username dan password.")
    st.stop()

username = st.session_state.username
filename = f"{DATA_FOLDER}/data_{username}.csv"

st.sidebar.success(f"Login sebagai: {username}")
menu = st.sidebar.radio("Menu", [
    "📥 Input Mood Harian", 
    "📊 Grafik & Heatmap", 
    "📂 Lihat Data", 
    "📌 Statistik & Saran", 
    "🚪 Logout"
])

# ========== Mood & Aktivitas Sinkron ==========
def nilai_mood_dari_aktivitas(aktivitas):
    negatif = ["begadang", "melelahkan", "toxic", "bertengkar", "lelah", "stress"]
    positif = ["olahraga", "meditasi", "berjalan", "keluarga", "healing", "jalan-jalan", "tidur cukup"]
    
    skor = 3
    aktivitas = aktivitas.lower()

    if any(neg in aktivitas for neg in negatif):
        skor -= 1
    if any(pos in aktivitas for pos in positif):
        skor += 1

    return max(1, min(skor, 5))

def saran_dari_mood(mood):
    if mood <= 2:
        return "😟 Kamu terlihat lelah. Coba istirahat, lakukan meditasi, atau jalan-jalan ringan."
    elif mood == 3:
        return "🙂 Mood kamu netral. Pertahankan dengan aktivitas sehat seperti olahraga ringan."
    elif mood >= 4:
        return "😄 Kamu dalam suasana hati yang baik. Bagus! Teruskan kebiasaan positifmu."
    return ""

# ========== Input ==========
if menu == "📥 Input Mood Harian":
    st.header("📥 Input Mood dan Aktivitas Harian")
    tanggal = st.date_input("Tanggal", datetime.now().date())
    aktivitas = st.text_area("Aktivitas hari ini (pisahkan dengan koma)", placeholder="Contoh: olahraga, nonton film, makan junk food")
    
    if aktivitas:
        mood = nilai_mood_dari_aktivitas(aktivitas)
        st.success(f"Skor mood otomatis berdasarkan aktivitas: {mood}")
        st.write(saran_dari_mood(mood))
        if st.button("💾 Simpan"):
            new_row = pd.DataFrame([{
                "Tanggal": tanggal,
                "Aktivitas": aktivitas,
                "Mood": mood
            }])
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row
            df.to_csv(filename, index=False)
            st.success("✅ Data berhasil disimpan!")

# ========== Grafik ==========
elif menu == "📊 Grafik & Heatmap":
    st.header("📊 Grafik Mood & Heatmap")
    if not os.path.exists(filename):
        st.warning("Belum ada data.")
    else:
        df = pd.read_csv(filename)
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df = df.sort_values("Tanggal")
        df["Week"] = df["Tanggal"].dt.isocalendar().week
        df["Weekday"] = df["Tanggal"].dt.weekday
        weekly_mood = df.groupby("Week")["Mood"].mean()
        st.subheader("📈 Mood Mingguan")
        st.line_chart(weekly_mood)

        # Heatmap
        weeks = sorted(df["Week"].unique())
        heatmap_data = np.full((7, len(weeks)), np.nan)
        week_map = {week: i for i, week in enumerate(weeks)}
        for _, row in df.iterrows():
            heatmap_data[int(row["Weekday"]), week_map[row["Week"]]] = row["Mood"]

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

# ========== Data ==========
elif menu == "📂 Lihat Data":
    st.header("📂 Data Tersimpan")
    if not os.path.exists(filename):
        st.info("Belum ada data.")
    else:
        df = pd.read_csv(filename)
        st.dataframe(df)
        st.download_button("⬇️ Unduh CSV", data=df.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")

# ========== Statistik & Saran ==========
elif menu == "📌 Statistik & Saran":
    st.header("📌 Statistik & Rekomendasi")
    if not os.path.exists(filename):
        st.warning("Belum ada data.")
    else:
        df = pd.read_csv(filename)
        st.metric("📆 Hari Dicatat", df["Tanggal"].nunique())
        st.metric("😊 Rata-rata Mood", round(df["Mood"].mean(), 2))
        st.metric("🏷️ Aktivitas Unik", df["Aktivitas"].nunique())
        st.subheader("💡 Saran Terbaru:")
        st.write(saran_dari_mood(df["Mood"].iloc[-1]))

# ========== Logout ==========
elif menu == "🚪 Logout":
    st.session_state.clear()
    st.success("Berhasil logout.")
    st.experimental_rerun()

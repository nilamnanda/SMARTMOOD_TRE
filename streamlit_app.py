import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

st.title("🧠 SmartMood: Daily Emotion & Activity Tracker")

# Inisialisasi data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["date", "activity", "mood"])

# ======================= INPUT HARIAN =========================
st.header("📥 Input Mood dan Aktivitas Harian")

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Tanggal", datetime.now())
with col2:
    activity = st.text_input("Aktivitas hari ini (misal: belajar, olahraga, rebahan)")

mood = st.slider("Skor Mood (1=buruk, 5=baik)", 1, 5, 3)

if st.button("💾 Simpan"):
    new_row = {"date": selected_date, "activity": activity, "mood": mood}
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ Data berhasil disimpan!")

st.divider()

# ======================= TAMPILKAN DATA ========================
st.header("📊 Data yang Tersimpan")

df = st.session_state.data.copy()
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Belum ada data, silakan input terlebih dahulu.")

st.divider()

# ======================= TREN MOOD MINGGUAN =====================
if not df.empty:
    st.header("📈 Tren Mood Mingguan (Line Chart)")
    df["week"] = df["date"].dt.isocalendar().week
    weekly_mood = df.groupby("week")["mood"].mean()
    st.line_chart(weekly_mood)

# ======================= HEATMAP MOOD ===========================
    st.header("🗓️ Heatmap Mood Mingguan (Kalender Visual)")

    df["weekday"] = df["date"].dt.weekday  # 0=Mon ... 6=Sun
    df["week"] = df["date"].dt.isocalendar().week
    weeks = sorted(df["week"].unique())
    heatmap_data = np.full((7, len(weeks)), np.nan)
    week_map = {week: i for i, week in enumerate(weeks)}

    for _, row in df.iterrows():
        week_idx = week_map[row["week"]]
        heatmap_data[int(row["weekday"]), week_idx] = row["mood"]

    fig, ax = plt.subplots(figsize=(10, 4))
    cax = ax.imshow(heatmap_data, cmap="YlOrBr", aspect="auto", vmin=1, vmax=5)

    ax.set_yticks(np.arange(7))
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xticks(np.arange(len(weeks)))
    ax.set_xticklabels([f"Minggu {w}" for w in weeks])

    for i in range(7):
        for j in range(len(weeks)):
            if not np.isnan(heatmap_data[i, j]):
                ax.text(j, i, int(heatmap_data[i, j]), ha="center", va="center", color="black")

    plt.colorbar(cax, ax=ax, label="Skor Mood")
    st.pyplot(fig)

# ======================= SIMULASI MOOD ==========================
    st.header("🔮 Simulasi Mood Berdasarkan Aktivitas")

    with st.expander("Coba simulasi prediksi mood"):
        options = {
            "belajar": 3,
            "olahraga": 5,
            "rebahan": 2,
            "nongkrong": 4,
            "tidur cukup": 5,
            "kerja kelompok": 3,
        }
        act = st.selectbox("Pilih aktivitas", list(options.keys()))
        st.info(f"Prediksi mood setelah **{act}**: {options[act]} / 5")

# ======================= STATISTIK RINGKASAN ===================
    st.header("📌 Statistik Singkat")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📆 Hari tercatat", df["date"].nunique())
    with col2:
        st.metric("😊 Mood rata-rata", round(df["mood"].mean(), 2))
    with col3:
        st.metric("🏃 Aktivitas unik", df["activity"].nunique())

    # Export to CSV
    st.download_button("⬇️ Download Data sebagai CSV", df.to_csv(index=False), file_name="smartmood_data.csv", mime="text/csv")

# ======================= LOGOUT / AKHIR =========================
st.divider()
st.markdown("🔚 Terima kasih telah menggunakan **SmartMood**! Jaga terus kesehatan mentalmu 💖")

if st.button("🚪 Logout (Reset Aplikasi)"):
    st.session_state.clear()
    st.experimental_rerun()

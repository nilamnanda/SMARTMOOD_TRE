import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# ===== Konfigurasi =====
st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood Tracker")
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ===== Skor Aktivitas Berdasarkan Analisis Kaggle =====
aktivitas_skor = {
    "Belajar": 4, "Ngerjain tugas": 3, "Proyekan": 3,
    "Dikejar deadline": 1, "Ikut kelas/zoom": 3,
    "Bertemu teman": 5, "Rapat organisasi": 3, "Nongkrong": 4,
    "Diam di kos": 2, "Chat panjang": 4,
    "Tidur cukup": 5, "Makan sehat": 4, "Olahraga": 5,
    "Begadang": 1, "Lupa makan": 1,
    "Scroll TikTok": 2, "Main game": 3, "Nonton film": 3,
    "Ngegalau": 1, "Tidak melakukan apa-apa": 1
}

kategori_aktivitas = {
    "Akademik": ["Belajar", "Ngerjain tugas", "Proyekan", "Dikejar deadline", "Ikut kelas/zoom"],
    "Sosial": ["Bertemu teman", "Rapat organisasi", "Nongkrong", "Diam di kos", "Chat panjang"],
    "Kesehatan": ["Tidur cukup", "Makan sehat", "Olahraga", "Begadang", "Lupa makan"],
    "Lainnya": ["Scroll TikTok", "Main game", "Nonton film", "Ngegalau", "Tidak melakukan apa-apa"]
}

saran_dict = {
    "Sedih": "Coba beri waktu untuk dirimu sendiri. Mungkin dengan aktivitas positif seperti olahraga ringan atau tidur cukup.",
    "Netral": "Harimu cukup seimbang. Kamu bisa coba menambah kegiatan sosial atau fisik agar lebih baik.",
    "Bahagia": "Keren! Suasana hatimu positif. Pertahankan kebiasaan baikmu dan sebarkan energi positif ke sekitar!"
}

# ===== Fungsi Mood Berdasarkan Total Skor (berdasarkan FitLife) =====
def classify_mood(score):
    if score < 12:
        return "Sedih", saran_dict["Sedih"]
    elif score < 18:
        return "Netral", saran_dict["Netral"]
    else:
        return "Bahagia", saran_dict["Bahagia"]

def diagnosis_kaggle(score):
    if score >= 18:
        return "Aktivitasmu optimal! Kamu mendekati pola hidup seimbang menurut analisis FitLife."
    elif score >= 12:
        return "Kamu menjalani hari yang cukup baik. Tambahkan aktivitas sosial dan fisik untuk hasil maksimal."
    else:
        return "Moodmu rendah. Berdasarkan data FitLife, kombinasi tidur cukup dan interaksi sosial bisa membantu."

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

# ===== Login Section =====
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🧠 SmartMood Tracker")
st.caption("Versi analitik berbasis data FitLife (Kaggle)")

if not st.session_state.login:
    username = st.text_input("Masukkan Username:")
    password = st.text_input("Masukkan Password:", type="password")
    if st.button("🔐 Login"):
        if username and password:
            st.session_state.login = True
            st.session_state.username = username
        else:
            st.error("Username dan Password tidak boleh kosong.")

if st.session_state.login:
    username = st.session_state.username
    file = f"{DATA_FOLDER}/data_{username}.csv"
    menu = st.sidebar.selectbox("📋 Menu", [
        "Input Mood Harian", "Grafik & Statistik", "Lihat Data", "Reset Data", "Tentang", "Logout"
    ])

    if menu == "Input Mood Harian":
        st.header("📥 Input Mood Harian")
        tanggal = st.date_input("Tanggal:", datetime.now())
        aktivitas_data = {}
        total_skor = 0
        for kategori, daftar in kategori_aktivitas.items():
            pilihan = st.selectbox(f"{kategori}", ["(Pilih)"] + daftar, key=kategori)
            if pilihan != "(Pilih)":
                aktivitas_data[kategori] = pilihan
                total_skor += aktivitas_skor.get(pilihan, 0)
        rating = st.slider("Rating mood (1–5)", 1, 5, 3)
        catatan = st.text_area("Catatan (opsional):")
        
        total_skor += rating * 2  # bobot dari rating

        if st.button("✅ Simpan"):
            mood, saran = classify_mood(total_skor)
            diagnosis = diagnosis_kaggle(total_skor)
            simpan_data(username, tanggal.strftime("%Y-%m-%d"), aktivitas_data, rating, mood, saran, catatan, diagnosis)
            st.success(f"Hasil Mood: **{mood}**")
            st.info(f"💡 Saran: {saran}")
            st.warning(f"📊 Diagnosis: {diagnosis}")

    elif menu == "Grafik & Statistik":
        st.header("📈 Visualisasi Mood")
        if not os.path.exists(file):
            st.warning("Belum ada data.")
        else:
            df = pd.read_csv(file)
            df['Tanggal'] = pd.to_datetime(df['Tanggal'])
            df_harian = df.groupby("Tanggal")["Skor"].mean().reset_index()
            df_harian["Mood"] = df.groupby("Tanggal")["Mood"].last().values

            # Line chart
            st.subheader("Mood Harian (Skor Total)")
            st.line_chart(df_harian.set_index("Tanggal")["Skor"])

            # Heatmap Mingguan
            st.subheader("📅 Heatmap Mood Mingguan")
            df_harian["Week"] = df_harian["Tanggal"].dt.isocalendar().week
            df_harian["Day"] = df_harian["Tanggal"].dt.weekday
            weeks = sorted(df_harian["Week"].unique())
            heatmap_data = np.full((7, len(weeks)), np.nan)
            week_map = {week: i for i, week in enumerate(weeks)}

            for _, row in df_harian.iterrows():
                heatmap_data[int(row["Day"]), week_map[row["Week"]]] = row["Skor"]

            fig, ax = plt.subplots(figsize=(10, 4))
            cax = ax.imshow(heatmap_data, cmap="YlOrRd", vmin=5, vmax=25)
            ax.set_yticks(np.arange(7))
            ax.set_yticklabels(["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"])
            ax.set_xticks(np.arange(len(weeks)))
            ax.set_xticklabels([f"Minggu {w}" for w in weeks])
            for i in range(7):
                for j in range(len(weeks)):
                    if not np.isnan(heatmap_data[i, j]):
                        ax.text(j, i, int(heatmap_data[i, j]), ha="center", va="center", color="black")
            plt.colorbar(cax, ax=ax, label="Skor Mood")
            st.pyplot(fig)

    elif menu == "Lihat Data":
        st.header("📂 Data Aktivitas & Mood")
        if os.path.exists(file):
            df = pd.read_csv(file)
            st.dataframe(df)
            st.download_button("⬇️ Unduh Data CSV", df.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")
        else:
            st.info("Belum ada data untuk ditampilkan.")

    elif menu == "Reset Data":
        if st.button("❌ Hapus semua data"):
            if os.path.exists(file):
                os.remove(file)
                st.success("Data berhasil dihapus.")
            else:
                st.warning("Tidak ada data untuk dihapus.")

    elif menu == "Tentang":
        st.header("ℹ️ Tentang Aplikasi")
        st.markdown("""
        **SmartMood Tracker** adalah alat pelacak mood harian berbasis data  
        dari analisis **FitLife Kaggle Dataset**.  
        Semua penilaian dan diagnosis mengikuti pola nyata dari data pengguna sebenarnya.
        """)

    elif menu == "Logout":
        st.session_state.clear()
        st.experimental_rerun()

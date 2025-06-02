import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# ====== Konstanta & Setup ======
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

aktivitas_skor = {
    "Belajar": 5, "Ngerjain tugas": 6, "Proyekan": 7, "Dikejar deadline": 3, "Ikut kelas/zoom": 5,
    "Bertemu teman": 8, "Rapat organisasi": 6, "Nongkrong": 7, "Diam di kos": 3, "Chat panjang": 6,
    "Tidur cukup": 9, "Makan sehat": 7, "Olahraga": 8, "Begadang": 2, "Lupa makan": 1,
    "Scroll TikTok": 3, "Main game": 4, "Nonton film": 5, "Ngegalau": 2, "Tidak melakukan apa-apa": 1
}

kategori_aktivitas = {
    "Akademik": ["Belajar", "Ngerjain tugas", "Proyekan", "Dikejar deadline", "Ikut kelas/zoom"],
    "Sosial": ["Bertemu teman", "Rapat organisasi", "Nongkrong", "Diam di kos", "Chat panjang"],
    "Kesehatan": ["Tidur cukup", "Makan sehat", "Olahraga", "Begadang", "Lupa makan"],
    "Lainnya": ["Scroll TikTok", "Main game", "Nonton film", "Ngegalau", "Tidak melakukan apa-apa"]
}

saran_dict = {
    "😢 Sedih": "Sepertinya harimu berat. Coba tarik napas dalam, dengarkan musik tenang, dan beri dirimu ruang untuk istirahat.",
    "😐 Biasa": "Mungkin hari ini terasa datar, tapi kamu hebat karena tetap menjalani. Pelan-pelan saja, semua baik-baik aja.",
    "😊 Bahagia": "Wah, kamu lagi di atas angin! Simpan energi ini dan bagi kebahagiaanmu ke orang terdekat, yuk."
}

# ====== Fungsi Utilitas ======
def classify_mood(score):
    if score < 10: return "😢 Sedih", saran_dict["😢 Sedih"]
    elif score < 20: return "😐 Biasa", saran_dict["😐 Biasa"]
    return "😊 Bahagia", saran_dict["😊 Bahagia"]

def diagnosis_kaggle(score):
    if score >= 22:
        return "Aktivitasmu menunjukkan keseimbangan yang baik antara fisik, sosial, dan akademik."
    elif score >= 15:
        return "Hari cukup seimbang, tapi bisa ditingkatkan dengan aktivitas sehat."
    return "Skor rendah sering berkaitan dengan kurangnya aktivitas sosial dan kesehatan."

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

def hitung_streak(df):
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df = df.sort_values('Tanggal', ascending=False)
    streak = 0
    today = datetime.now().date()
    for t in df['Tanggal']:
        if t.date() == today - timedelta(days=streak):
            streak += 1
        else:
            break
    return streak

# ====== Streamlit App ======
st.set_page_config(page_title="SmartMood Tracker", layout="wide")
st.title("🧠 SmartMood: Daily Emotion & Activity Tracker")

# ====== Login Section ======
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""

if not st.session_state.login:
    username = st.text_input("Masukkan username:")
    password = st.text_input("Password", type="password")
    if st.button("🔐 Login"):
        if username and password:
            st.session_state.login = True
            st.session_state.username = username
        else:
            st.warning("Masukkan username dan password.")

# ====== Setelah Login ======
if st.session_state.login:
    username = st.session_state.username
    file = f"{DATA_FOLDER}/data_{username}.csv"

    st.sidebar.title("📋 Menu")
    menu = st.sidebar.radio("Navigasi:", ["Input Mood", "Grafik", "Data CSV", "Tentang", "Logout"])

    # ========= INPUT =========
    if menu == "Input Mood":
        st.header("✍️ Input Aktivitas & Mood Harian")
        aktivitas_data = {}
        skor_list = []

        for kategori, daftar in kategori_aktivitas.items():
            pilihan = st.selectbox(f"{kategori}", ["(Pilih satu)"] + daftar, key=kategori)
            if pilihan != "(Pilih satu)":
                aktivitas_data[kategori] = pilihan
                skor_list.append(aktivitas_skor.get(pilihan, 0))

        rating = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")
        tanggal = datetime.now().strftime("%Y-%m-%d")

        if st.button("✅ Simpan"):
            total_skor = sum(skor_list) + rating * 2
            mood, saran = classify_mood(total_skor)
            diagnosis = diagnosis_kaggle(total_skor)
            simpan_data(username, tanggal, aktivitas_data, rating, mood, saran, catatan, diagnosis)

            st.success(f"Mood kamu hari ini: {mood}")
            st.info(f"Saran: {saran}")
            st.warning(f"🔍 Diagnosis: {diagnosis}")

    # ========= GRAFIK =========
    elif menu == "Grafik":
        if not os.path.exists(file):
            st.warning("Belum ada data.")
        else:
            df = pd.read_csv(file)
            if df.empty:
                st.warning("Belum ada data.")
            else:
                df["Tanggal"] = pd.to_datetime(df["Tanggal"])
                df_harian = df.groupby("Tanggal")["Skor"].mean().reset_index()
                df_harian["Mood"] = df.groupby("Tanggal")["Mood"].last().values

                st.subheader("📊 Grafik Mood Harian")
                warna = df_harian["Mood"].map(lambda m: "green" if "Bahagia" in m else ("orange" if "Biasa" in m else "blue"))
                fig, ax = plt.subplots(figsize=(10,4))
                ax.bar(df_harian["Tanggal"].dt.strftime("%d-%b"), df_harian["Skor"], color=warna)
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Skor Mood")
                ax.set_title("Mood Harian")
                st.pyplot(fig)

                # Streak
                streak = hitung_streak(df)
                st.success(f"🔥 Konsistensi: {streak} hari berturut-turut!")

                # Heatmap Mingguan
                st.subheader("🗓️ Heatmap Mood Mingguan")
                df_heat = df.groupby("Tanggal")["Rating"].mean().reset_index()
                df_heat["Tanggal"] = pd.to_datetime(df_heat["Tanggal"])
                df_heat["Week"] = df_heat["Tanggal"].dt.isocalendar().week
                df_heat["Weekday"] = df_heat["Tanggal"].dt.weekday

                heatmap = np.full((7, df_heat["Week"].nunique()), np.nan)
                weeks = sorted(df_heat["Week"].unique())
                wmap = {w: i for i, w in enumerate(weeks)}

                for _, row in df_heat.iterrows():
                    heatmap[int(row["Weekday"]), wmap[row["Week"]]] = row["Rating"]

                fig2, ax2 = plt.subplots(figsize=(10, 4))
                cax = ax2.imshow(heatmap, cmap="YlGn", vmin=1, vmax=5)
                ax2.set_yticks(np.arange(7))
                ax2.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
                ax2.set_xticks(np.arange(len(weeks)))
                ax2.set_xticklabels([f"Minggu {w}" for w in weeks])
                plt.colorbar(cax, ax=ax2, label="Rating Mood")
                st.pyplot(fig2)

    # ========= DATA CSV =========
    elif menu == "Data CSV":
        st.header("📂 Data Aktivitas & Mood")
        if os.path.exists(file):
            df_user = pd.read_csv(file)
            st.dataframe(df_user)
            st.download_button("⬇️ Unduh CSV", df_user.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")
        else:
            st.warning("Data belum tersedia.")

    # ========= TENTANG =========
    elif menu == "Tentang":
        st.markdown("""
        ## 📘 Tentang SmartMood
        SmartMood Tracker adalah alat bantu untuk merefleksikan suasana hati dan aktivitas harian.
        
        **Fitur:**
        - Login personal
        - Input aktivitas + rating mood
        - Klasifikasi mood otomatis
        - Grafik harian & heatmap mingguan
        - Simulasi prediksi mood
        - Statistik & ekspor CSV

        💡 Cocok untuk pelajar, mahasiswa, atau siapa pun yang ingin mengenali pola hidupnya!
        """)

    # ========= LOGOUT =========
    elif menu == "Logout":
        st.session_state.clear()
        st.experimental_rerun()

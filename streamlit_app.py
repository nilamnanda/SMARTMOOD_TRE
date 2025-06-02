import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# === Konstanta dan Setup Awal ===
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

# === Fungsi Logika dan Data ===
def classify_mood(score):
    if score < 10:
        mood = "😢 Sedih"
    elif score < 20:
        mood = "😐 Biasa"
    else:
        mood = "😊 Bahagia"
    return mood, saran_dict[mood]

def diagnosis_kaggle(score):
    if score >= 22:
        return "Aktivitasmu menunjukkan keseimbangan yang baik antara fisik, sosial, dan akademik. Ini mendekati pola optimal dalam dataset FitLife."
    elif score >= 15:
        return "Kamu menjalani hari yang cukup seimbang, meskipun masih bisa ditingkatkan dengan aktivitas sehat seperti olahraga atau tidur cukup."
    else:
        return "Dalam data FitLife, skor rendah sering berkaitan dengan kurangnya aktivitas sosial dan kesehatan. Coba ubah rutinitas agar lebih positif."

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

def recursive_sum(scores, idx=0):
    if idx >= len(scores):
        return 0
    return scores[idx] + recursive_sum(scores, idx + 1)

def find_max_while(scores):
    i, max_score = 0, float('-inf')
    while i < len(scores):
        if scores[i] > max_score:
            max_score = scores[i]
        i += 1
    return max_score

# === Antarmuka Streamlit ===
st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("🧠 SmartMood Tracker")

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
    st.sidebar.title("📋 Menu")
    menu = st.sidebar.radio("Pilih menu:", ["Input Mood Harian", "Grafik Mood", "Data CSV", "Reset Data", "Tentang", "Logout"])

    if menu == "Input Mood Harian":
        st.header("✍️ Input Mood & Aktivitas")
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
            total_skor = recursive_sum(skor_list) + rating * 2
            mood, saran = classify_mood(total_skor)
            diagnosis = diagnosis_kaggle(total_skor)
            simpan_data(username, tanggal, aktivitas_data, rating, mood, saran, catatan, diagnosis)
            st.success(f"Mood kamu hari ini: {mood}")
            st.info(f"Saran: {saran}")
            st.warning(f"🔍 Diagnosis: {diagnosis}")

            arr = np.array(skor_list)
            st.caption(f"Statistik skor (NumPy): Mean={np.mean(arr):.2f}, Std={np.std(arr):.2f}, Max={np.max(arr)}, Min={np.min(arr)}")
            max_skor = find_max_while(skor_list)
            st.caption(f"Skor tertinggi ditemukan dengan while-loop: {max_skor}")

    elif menu == "Grafik Mood":
        st.header("📊 Grafik Mood Harian")
        if not os.path.exists(file):
            st.warning("Belum ada data.")
        else:
            df = pd.read_csv(file)
            if len(df) < 3:
                st.warning("Data belum cukup (min. 3 hari)")
            else:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'])
                df_daily = df.groupby("Tanggal")["Skor"].mean().reset_index()
                mood_label = df.groupby("Tanggal")["Mood"].last()
                warna = mood_label.map(lambda m: "green" if "Bahagia" in m else ("gold" if "Biasa" in m else "blue"))
                fig, ax = plt.subplots(figsize=(10,4))
                ax.bar(df_daily["Tanggal"].dt.strftime("%d-%b"), df_daily["Skor"], color=warna)
                ax.set_title(f"Mood Harian - {username}")
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Skor Mood")
                st.pyplot(fig)

                streak = hitung_streak(df)
                st.success(f"🔥 Konsistensi: {streak} hari berturut-turut!")

    elif menu == "Data CSV":
        st.header("📂 Data Aktivitas & Mood")
        if os.path.exists(file):
            df_user = pd.read_csv(file)
            st.dataframe(df_user)
            st.download_button("⬇️ Unduh Data CSV", data=df_user.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")
        else:
            st.warning("Belum ada data.")

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
        - Input aktivitas dari 4 kategori + rating harian
        - Klasifikasi mood otomatis & saran reflektif
        - Statistik dengan NumPy & fungsi rekursif
        - Grafik perkembangan mood (Matplotlib)
        - Deteksi streak harian (konsistensi)
        - Diagnostik berbasis pola dataset FitLife
        """)

    elif menu == "Logout":
        st.session_state.login = False
        st.rerun()

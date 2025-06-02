import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# ========== Pengaturan Data ==========
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

def classify_mood(score):
    if score < 10:
        mood = "😢 Sedih"
    elif score < 20:
        mood = "😐 Biasa"
    else:
        mood = "😊 Bahagia"
    return mood, saran_dict[mood]

def simpan_data(username, tanggal, aktivitas_data, rating, mood, saran, catatan):
    filename = f"{DATA_FOLDER}/data_{username}.csv"
    records = []
    for kategori, aktivitas in aktivitas_data.items():
        skor = aktivitas_skor.get(aktivitas, 0)
        records.append([tanggal, kategori, aktivitas, skor, rating, mood, saran, catatan])
    df_new = pd.DataFrame(records, columns=["Tanggal", "Kategori", "Aktivitas", "Skor", "Rating", "Mood", "Saran", "Catatan"])
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

# ========== Streamlit UI ==========
st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("🧠 SmartMood Tracker")
st.write("Refleksi mood kamu berdasarkan aktivitas harian 💡")

# Login State
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    username = st.text_input("Masukkan username:")
    password = st.text_input("Password (simulasi)", type="password")
    if username and password:
        st.session_state.username = username
        st.session_state.login = True
        st.rerun()
    else:
        st.warning("Masukkan username dan password.")
else:
    username = st.session_state.username
    st.success(f"Login sebagai **{username}**")
    menu = st.sidebar.selectbox("📋 Menu", ["Input Mood Harian", "Lihat Grafik Mood", "Reset Data", "Tentang", "Logout"])

    file = f"{DATA_FOLDER}/data_{username}.csv"

    if menu == "Input Mood Harian":
        st.header("✍️ Input Mood & Aktivitas")
        aktivitas_data = {}
        total_skor = 0
        for kategori, daftar in kategori_aktivitas.items():
            pilihan = st.selectbox(f"{kategori}", ["(Pilih satu)"] + daftar, key=kategori)
            if pilihan != "(Pilih satu)":
                aktivitas_data[kategori] = pilihan
                total_skor += aktivitas_skor.get(pilihan, 0)

        rating = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")
        tanggal = datetime.now().strftime("%Y-%m-%d")

        if st.button("✅ Simpan"):
            mood, saran = classify_mood(total_skor + rating * 2)
            simpan_data(username, tanggal, aktivitas_data, rating, mood, saran, catatan)
            st.success(f"Mood kamu hari ini: {mood}")
            st.info(f"Saran: {saran}")

            if os.path.exists(file):
                st.subheader("📂 Riwayat Data Kamu")
                df_user = pd.read_csv(file)
                st.dataframe(df_user)
                st.download_button("⬇️ Unduh Data CSV", data=df_user.to_csv(index=False), file_name=f"data_{username}.csv", mime="text/csv")

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
        - Saran yang empatik & validasi diri
        - Grafik perkembangan mood
        - Deteksi *streak* harian (konsistensi)
        """)

    elif menu == "Logout":
        st.session_state.login = False
        st.rerun()

import streamlit as st
import pandas as pd
import datetime
import os
import random

# ====================== Konfigurasi Halaman =======================
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

# ====================== Inisialisasi Session =======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

DATA_FILE = "smartmood_data.csv"

# ====================== User Login Data (Dummy) =======================
USERS = {
    "user1": "password123",
    "user2": "rahasiaku",
    "admin": "adminpass"
}

# ====================== Kategori & Aktivitas =======================
aktivitas_kategori = {
    "Akademik": {
        "positif": ["Tugas selesai", "Belajar fokus", "Laprak rapi"],
        "negatif": ["Tugas numpuk", "Belajar ngaret", "Stres tugas"]
    },
    "Sosial": {
        "positif": ["Ngobrol santai", "Main bareng", "Jalan-jalan"],
        "negatif": ["Sendiri aja", "Kurang interaksi", "Canggung banget"]
    },
    "Kesehatan": {
        "positif": ["Tidur cukup", "Makan sehat", "Gerak ringan"],
        "negatif": ["Begadang terus", "Lupa makan", "Kurang gerak"]
    },
    "Lainnya": {
        "positif": ["Denger musik", "Beres kamar"],
        "negatif": ["Main terus", "Scroll sosmed lama", "Belanja banyak"]
    }
}

# ====================== Fungsi =======================
def simpan_data(tanggal, username, mood, aktivitas, catatan):
    new_data = pd.DataFrame([{
        "Tanggal": tanggal,
        "Username": username,
        "Mood": mood,
        "Aktivitas": aktivitas,
        "Catatan": catatan
    }])
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(DATA_FILE, index=False)

def klasifikasi_mood(mood_score, aktivitas):
    negatif = sum(1 for a in aktivitas if any(a in aktivitas_kategori[k]['negatif'] for k in aktivitas_kategori))
    positif = sum(1 for a in aktivitas if any(a in aktivitas_kategori[k]['positif'] for k in aktivitas_kategori))
    if mood_score >= 4 and positif > negatif:
        return "Bahagia"
    elif mood_score <= 2 and negatif >= positif:
        return "Sedih"
    else:
        return "Biasa"

def saran_mood(kategori):
    saran_dict = {
        "Bahagia": [
            "Kamu sedang berada di titik baik, terus pertahankan rutinitas positifmu ya! 😊",
            "Senang melihatmu bahagia! Jangan lupa sebar energi positifmu ke orang sekitar. 💛"
        ],
        "Sedih": [
            "Tidak apa-apa merasa sedih. Cobalah istirahat atau berbicara dengan seseorang yang kamu percaya. 🤗",
            "Hari ini berat, tapi kamu hebat karena tetap bertahan. 💪 Coba lakukan hal kecil yang kamu suka."
        ],
        "Biasa": [
            "Mungkin hari ini terasa datar, tapi kamu hebat karena tetap menjalani. Pelan-pelan saja, semua baik-baik aja. 🙂",
            "Keseimbangan juga penting. Kamu menjalani hari ini dengan cukup stabil. 👍"
        ]
    }
    return random.choice(saran_dict.get(kategori, ["Tetap semangat!"]))

def diagnosis_aktivitas(kategori):
    diagnosis_dict = {
        "Bahagia": "✨ Menurut data FitLife: Hari kamu terlihat penuh energi dan produktif! Pertahankan pola ini ya.",
        "Sedih": "📉 Menurut data FitLife: Ada tanda-tanda kelelahan atau stres. Coba sempatkan olahraga ringan atau tidur lebih awal.",
        "Biasa": "🔍 Diagnosis menurut data FitLife: Kamu menjalani hari yang cukup seimbang, meskipun masih bisa ditingkatkan dengan aktivitas sehat seperti olahraga atau tidur cukup."
    }
    return diagnosis_dict.get(kategori, "")

def kutipan_motivasi():
    quotes = [
        "Hidup adalah 10% apa yang terjadi pada kita dan 90% bagaimana kita meresponsnya.",
        "Setiap hari adalah kesempatan baru untuk menjadi lebih baik.",
        "Jangan biarkan kemarin menghabiskan terlalu banyak dari hari ini."
    ]
    return random.choice(quotes)

# ====================== Login Page =======================
def login():
    st.title("🔐 Login SmartMood Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("🔓 Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login berhasil sebagai *{username}*")
            st.experimental_rerun()
        else:
            st.error("Username atau password salah. Silakan coba lagi.")

# ====================== Main App =======================
def main_app():
    st.sidebar.title("📋 Menu")
    menu = st.sidebar.selectbox("Pilih menu", [
        "Input Mood Harian", "Lihat Grafik Mood", "Lihat Data CSV", "Reset Data", "Tentang", "Logout"])

    if menu == "Input Mood Harian":
        st.header("📝 Input Mood & Aktivitas")
        tanggal = st.date_input("Tanggal", datetime.date.today())

        aktivitas_dipilih = []
        for kategori, data in aktivitas_kategori.items():
            pilihan = st.selectbox(f"{kategori}", data['positif'] + data['negatif'], index=None, placeholder="(Pilih satu)")
            if pilihan:
                aktivitas_dipilih.append(pilihan)

        mood = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")

        if st.button("✅ Simpan"):
            if aktivitas_dipilih:
                simpan_data(tanggal, st.session_state.username, mood, ", ".join(aktivitas_dipilih), catatan)
                kategori = klasifikasi_mood(mood, aktivitas_dipilih)
                st.success(f"Mood kamu hari ini: {'😊' if kategori == 'Bahagia' else '😢' if kategori == 'Sedih' else '😐'} {kategori}")
                st.info(f"Saran: {saran_mood(kategori)}")
                st.markdown(f"<div style='background-color:#e0e0a8;padding:10px;border-radius:5px'><b>🔍 Diagnosis menurut data FitLife:</b> {diagnosis_aktivitas(kategori)}</div>", unsafe_allow_html=True)
                st.markdown(f"> 💡 *{kutipan_motivasi()}*")
            else:
                st.warning("Pilih minimal satu aktivitas.")

    elif menu == "Lihat Grafik Mood":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df_user = df[df["Username"] == st.session_state.username]
            df_user["Tanggal"] = pd.to_datetime(df_user["Tanggal"])
            st.line_chart(df_user.set_index("Tanggal")["Mood"])
        else:
            st.warning("Belum ada data.")

    elif menu == "Lihat Data CSV":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            st.dataframe(df[df["Username"] == st.session_state.username])
        else:
            st.warning("Belum ada data.")

    elif menu == "Reset Data":
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("Data berhasil di-reset.")
        else:
            st.info("Data sudah kosong.")

    elif menu == "Tentang":
        st.subheader("Tentang Aplikasi")
        st.write("SmartMood Tracker adalah aplikasi untuk mencatat mood harian dan aktivitas, serta memberikan saran dan diagnosis berdasarkan data FitLife. Aplikasi ini dirancang untuk membantu kamu memahami perasaan dan kebiasaan sehari-hari.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Berhasil logout.")
        st.experimental_rerun()

# ====================== App Start =======================
if not st.session_state.logged_in:
    login()
else:
    main_app()

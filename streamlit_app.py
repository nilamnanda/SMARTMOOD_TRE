import streamlit as st
import pandas as pd
import datetime
import os
import random
import json
import hashlib

# ================== Konfigurasi Halaman ==================
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

# ================== Session State ==================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

DATA_FILE = "smartmood_data.csv"
USER_FILE = "users.json"

# ================== Utility Functions ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ============== Mood Activity Categories ==============
aktivitas_kategori = {
    "Akademik": {
        "positif": ["Tugas selesai", "Belajar", "Laprak selesai"],
        "negatif": ["Tugas numpuk", "Menunda Belajar", "Stres tugas"]
    },
    "Sosial": {
        "positif": ["Ngobrol santai", "Main bareng", "Jalan-jalan"],
        "negatif": ["Sendiri aja", "Kurang interaksi", "Canggung banget"]
    },
    "Kesehatan": {
        "positif": ["Tidur cukup", "Makan sehat", "Gerak ringan"],
        "negatif": ["Begadang terus", "Lupa makan", "Kurang gerak", "Sakit"]
    },
    "Lainnya": {
        "positif": ["Denger musik", "Beres kamar"],
        "negatif": ["Main terus", "Scroll sosmed lama", "Belanja banyak"]
    }
}

# ============== Fungsi Pendukung ==============
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

def diagnosis_aktivitas(kategori):
    diagnosis_dict = {
        "Bahagia": "🌈 Aktivitasmu tampak positif dan kamu merasa baik. Cobalah lanjutkan dengan berjalan santai atau menulis jurnal malam ini.",
        "Sedih": "💤 Aktivitasmu tampak berat, dan kamu mungkin merasa lelah. Cobalah tidur lebih awal atau lakukan pernapasan dalam untuk tenang.",
        "Biasa": "🧠 Aktivitasmu tampak berat, tapi kamu merasa baik. Hati-hati jangan sampai lelah yang tertunda, ya. Coba dengarkan musik atau berjalan sebentar."
    }
    return diagnosis_dict.get(kategori, "Tetap semangat!")

def kutipan_motivasi():
    quotes = [
        "Hidup adalah 10% apa yang terjadi pada kita dan 90% bagaimana kita meresponsnya.",
        "Setiap hari adalah kesempatan baru untuk menjadi lebih baik.",
        "Jangan biarkan kemarin menghabiskan terlalu banyak dari hari ini."
    ]
    return random.choice(quotes)

# ============== Login Page (Auto Register) ==============
def login_register_page():
    st.title("🔐 SmartMood Tracker")
    st.write("Masukkan username dan password untuk login. Jika belum punya akun, akan dibuat otomatis.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Masuk"):
        users = load_users()
        hashed = hash_password(password)

        if username in users:
            if users[username] == hashed:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Selamat datang kembali, {username}!")
                st.experimental_rerun()  # ✅ Perbaikan di sini
            else:
                st.error("Password salah.")
        else:
            users[username] = hashed
            save_users(users)
            st.success(f"Akun baru dibuat untuk {username}. Selamat datang!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()  # ✅ Perbaikan di sini

# ============== Aplikasi Utama ==============
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
                st.markdown(f"<div style='background-color:#f5f5dc;padding:10px;border-radius:5px'><b>{diagnosis_aktivitas(kategori)}</b></div>", unsafe_allow_html=True)
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
        st.write("SmartMood Tracker adalah aplikasi untuk mencatat mood harian dan aktivitas, serta memberikan diagnosis berdasarkan data FitLife. Dibuat untuk membantumu memahami perasaan dan kebiasaan harian secara lebih personal.")

    elif menu == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Berhasil logout. Sampai jumpa lagi ya, semangat terus! 💪")
        st.experimental_rerun()  # ✅ Perbaikan di sini

# ============== Start Aplikasi ==============
if not st.session_state.logged_in:
    login_register_page()
else:
    main_app()

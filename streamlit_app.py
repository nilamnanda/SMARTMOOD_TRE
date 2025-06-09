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

def diagnosis_aktivitas(aktivitas):
    pesan = []

    for a in aktivitas:
        if a in ["Tugas selesai", "Belajar", "Laprak selesai"]:
            pesan.append("📘 Kamu produktif hari ini! Luangkan waktu untuk bersantai agar tetap seimbang.")
        elif a in ["Tugas numpuk", "Menunda Belajar", "Stres tugas"]:
            pesan.append("📚 Sepertinya tugas membuatmu tertekan. Cobalah buat to-do list sederhana untuk mengurangi beban.")
        elif a in ["Ngobrol santai", "Main bareng", "Jalan-jalan"]:
            pesan.append("👫 Interaksi sosial yang hangat bisa jadi penyemangat. Pertahankan hubungan baik ini.")
        elif a in ["Sendiri aja", "Kurang interaksi", "Canggung banget"]:
            pesan.append("🌧 Merasa sendiri itu manusiawi. Mungkin waktunya chat teman lama atau ikut kegiatan baru?")
        elif a in ["Tidur cukup", "Makan sehat", "Gerak ringan"]:
            pesan.append("💪 Gaya hidup sehatmu keren! Tubuhmu pasti berterima kasih.")
        elif a in ["Begadang terus", "Lupa makan", "Kurang gerak", "Sakit"]:
            pesan.append("⚠ Jangan abaikan sinyal tubuhmu. Istirahat, makan yang cukup, dan coba peregangan kecil.")
        elif a in ["Denger musik", "Beres kamar"]:
            pesan.append("🎶 Aktivitas simpel seperti ini bisa bantu mengatur suasana hati. Good job!")
        elif a in ["Main terus", "Scroll sosmed lama", "Belanja banyak"]:
            pesan.append("🌀 Terjebak distraksi memang sering terjadi. Yuk coba atur waktu mainmu lebih bijak.")

    if not pesan:
        return "✨ Tetap semangat! Apapun harimu, kamu sudah melakukan yang terbaik."
    else:
        return "\n".join(random.sample(pesan, min(3, len(pesan))))

def kutipan_motivasi():
    quotes = [
        "🌤 Setiap pagi adalah kesempatan untuk memulai ulang dengan lebih baik.",
        "🌱 Pelan-pelan tidak apa-apa, yang penting kamu tetap berjalan.",
        "💖 Tidak semua hari harus produktif. Kadang bertahan aja udah hebat.",
        "🌈 Kamu tidak harus kuat setiap saat, yang penting kamu terus mencoba.",
        "☕ Tarik napas dalam-dalam. Kamu sudah sejauh ini. Lanjutkan dengan lembut.",
        "🕊 Kadang, istirahat adalah bentuk kemajuan yang tersembunyi.",
        "🌙 Hari ini mungkin berat, tapi malam selalu membawa harapan baru.",
        "🔥 Kamu punya kekuatan untuk melewati ini, bahkan jika kamu belum merasakannya sekarang.",
        "📖 Hidup tidak selalu soal hasil, tapi tentang perjalanan dan cerita yang kamu buat.",
        "🫶 Kamu tidak sendiri. Banyak orang sedang berjuang seperti kamu—dan itu nggak apa-apa."
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
                st.rerun()
            else:
                st.error("Password salah.")
        else:
            users[username] = hashed
            save_users(users)
            st.success(f"Akun baru dibuat untuk {username}. Selamat datang!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()

# ============== Aplikasi Utama ==============
def main_app():
    st.sidebar.title("📋 Menu")
    menu = st.sidebar.selectbox("Pilih menu", [
        "Input Mood Harian", "Lihat Grafik Mood", "Lihat Data CSV", "Reset Data", "Tentang", "Logout"])

    if menu == "Input Mood Harian":
        st.header("📝 Input Mood & Aktivitas")
        st.caption("🎯 Penilaian mood berdasarkan skala 1-5, dengan mempertimbangkan kombinasi aktivitas harian yang kamu lakukan.")

        tanggal = st.date_input("Tanggal", datetime.date.today())
        aktivitas_dipilih = []

        for kategori, data in aktivitas_kategori.items():
            opsi = ["(Pilih satu)"] + data['positif'] + data['negatif']
            pilihan = st.selectbox(f"{kategori}", opsi)
            if pilihan != "(Pilih satu)":
                aktivitas_dipilih.append(pilihan)

        mood = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")

        if st.button("✅ Simpan"):
            if aktivitas_dipilih:
                simpan_data(tanggal, st.session_state.username, mood, ", ".join(aktivitas_dipilih), catatan)
                kategori = klasifikasi_mood(mood, aktivitas_dipilih)
                warna = "#eecbff"  # pink-ungu
                st.markdown(f"""
                    <div style='background-color:{warna};padding:10px;border-radius:10px;'>
                    <b>Mood kamu hari ini: {'😊' if kategori == 'Bahagia' else '😢' if kategori == 'Sedih' else '😐'} {kategori}</b><br><br>
                    {diagnosis_aktivitas(aktivitas_dipilih)}</div>
                    """, unsafe_allow_html=True)
                st.markdown(f"> 💡 {kutipan_motivasi()}")
            else:
                st.warning("Pilih minimal satu aktivitas.")

    elif menu == "Lihat Grafik Mood":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df_user = df[df["Username"] == st.session_state.username]
            df_user["Tanggal"] = pd.to_datetime(df_user["Tanggal"])
            df_user = df_user.sort_values("Tanggal")
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
        st.write("SmartMood Tracker adalah aplikasi untuk mencatat mood harian dan aktivitas, serta memberikan diagnosis berdasarkan aktivitas kamu. Dibuat untuk membantumu memahami perasaan dan kebiasaan harian secara lebih personal.")

    elif menu == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Berhasil logout. Sampai jumpa lagi ya, semangat terus! 💪")
        st.rerun()

# ============== Start Aplikasi ==============
if not st.session_state.logged_in:
    login_register_page()
else:
    main_app()

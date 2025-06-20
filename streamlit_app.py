import streamlit as st
import pandas as pd
import datetime
import os
import random
import json
import hashlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

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
    kategori = klasifikasi_mood(mood, aktivitas)
    new_data = pd.DataFrame([{
        "Tanggal": tanggal,
        "Username": username,
        "Mood": mood,
        "Aktivitas": aktivitas,
        "Catatan": catatan,
        "Klasifikasi": kategori
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

def kutipan_motivasi(saran_level):
    quotes_map = {
        "buruk": [
            "💖 Perasaanmu valid. Kamu berhak istirahat tanpa merasa bersalah.",
            "🌙 Gelapnya malam tidak selamanya. Cahaya pagi akan datang juga.",
            "🕊 Ambil waktu untuk dirimu sendiri. Ketenangan itu juga produktif."
        ],
        "cukup": [
            "☕ Pelan-pelan saja. Tidak semua orang berjalan dengan kecepatan yang sama.",
            "📖 Hidup bukan perlombaan. Nikmati setiap babnya, termasuk yang sulit.",
            "🌈 Kamu sedang tumbuh, meskipun sekarang rasanya lambat atau tidak terlihat."
        ],
        "baik": [
            "🌤 Hari yang baik! Teruskan langkahmu, dan jaga dirimu tetap seimbang.",
            "🌱 Maju satu langkah kecil pun tetaplah kemajuan. Kamu sedang bertumbuh.",
            "🔥 Teruskan semangatmu, tapi jangan lupa rehat juga ya."
        ]
    }

    # ambil kutipan pertama dari kategori tersebut (atau bisa pakai index tertentu jika mau dinamis)
    return quotes_map.get(saran_level, ["🌱 Tetap semangat, satu hari satu langkah."])[0]

# ============== Login/Register Page ==============
def login_register_page():
    st.title("🔐 SmartMood Tracker")
    st.write("Masukkan username dan password untuk login. Jika belum punya akun, akan dibuat otomatis.")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Masuk", key="login_button"):
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


# ============== Main App ==============
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
                simpan_data(tanggal, st.session_state.username, mood, aktivitas_dipilih, catatan)
                kategori = klasifikasi_mood(mood, aktivitas_dipilih)
                warna = "#eecbff"
                st.markdown(f"""
                    <div style='background-color:{warna};padding:10px;border-radius:10px;'>
                    <b>Mood kamu hari ini: {'😊' if kategori == 'Bahagia' else '😢' if kategori == 'Sedih' else '😐'} {kategori}</b><br><br>
                    {diagnosis_aktivitas(aktivitas_dipilih)}</div>
                    """, unsafe_allow_html=True)

                # Penilaian level mood
                if mood <= 2:
                    saran_level = "buruk"
                elif mood == 3:
                    saran_level = "cukup"
                else:
                    saran_level = "baik"

                # Tampilkan kutipan motivasi sesuai level
                st.markdown(f"💡 {kutipan_motivasi(saran_level)}")
            else:
                st.warning("Pilih minimal satu aktivitas.")

           

    elif menu == "Lihat Grafik Mood":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df_user = df[df["Username"] == st.session_state.username]
            df_user["Tanggal"] = pd.to_datetime(df_user["Tanggal"])
            df_user = df_user.sort_values("Tanggal")

            st.subheader("📊 Visualisasi Mood Harian")

            warna_map = {"Bahagia": "#88e36b", "Biasa": "#ffb1e1", "Sedih": "#f87171"}
            df_user["Warna"] = df_user["Klasifikasi"].map(warna_map)

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df_user["Tanggal"], df_user["Mood"], color=df_user["Warna"], width=0.6)

            ax.set_ylim(0, 5)
            ax.set_xlabel("Tanggal")
            ax.set_ylabel("Skor Mood")
            ax.set_title("📅 Mood Tracker Berwarna Berdasarkan Klasifikasi")

            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            plt.xticks(rotation=45, ha='right')

            ax.grid(axis='y', linestyle='--', alpha=0.7)
            legend_elements = [Patch(facecolor=warna_map[k], label=k) for k in warna_map]
            ax.legend(handles=legend_elements, title="Klasifikasi Mood")

            st.pyplot(fig)
            st.caption("🎨 Warna grafik mewakili mood kamu: Hijau (Bahagia), Merah (Sedih), Pink (Biasa).")
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
        st.write(
            "SmartMood Tracker adalah aplikasi untuk mencatat mood harian dan aktivitas, "
            "serta memberikan diagnosis berdasarkan aktivitas kamu. Dibuat untuk membantumu "
            "memahami perasaan dan kebiasaan harian secara lebih personal."
        )

    elif menu == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Berhasil logout. Sampai jumpa lagi ya, semangat terus! 💪")
        st.rerun()  # ✅ versi terbaru yang benar


# ============== Jalankan Aplikasi ==============
if not st.session_state.logged_in:
    login_register_page()
else:
    main_app()

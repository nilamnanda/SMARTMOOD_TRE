import streamlit as st
import pandas as pd
import datetime
import os
import random

# ====================== Inisialisasi =======================
st.set_page_config(page_title="SmartMood Tracker", layout="wide")
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

DATA_FILE = "smartmood_data.csv"

# ====================== Aktivitas & Kategori =======================
aktivitas_kategori = {
    "Akademik": {
        "positif": ["Mengerjakan tugas", "Membaca buku", "Belajar hal baru"],
        "negatif": ["Menunda tugas", "Menunda Belajar" , " , ]
    },
    "Sosial": {
        "positif": ["Bertemu teman", "Berbincang dengan keluarga", "Bersosialisasi di luar"],
        "negatif": ["Bertengkar", "Mengisolasi diri"]
    },
    "Kesehatan": {
        "positif": ["Tidur cukup", "Olahraga", "Makan sehat"],
        "negatif": ["Begadang", "Makan junk food"]
    },
    "Lainnya": {
        "positif": ["Meditasi", "Mendengarkan musik", "Nonton film"],
        "negatif": ["Bermain game terlalu lama", "Scrolling medsos berlebihan"]
    }
}
all_activities = sum([v['positif'] + v['negatif'] for v in aktivitas_kategori.values()], [])

# ====================== Fungsi =======================
def simpan_data(tanggal, username, mood, aktivitas):
    new_data = pd.DataFrame([{"Tanggal": tanggal, "Username": username, "Mood": mood, "Aktivitas": aktivitas}])
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
        return "Netral"

def diagnosis_mood(kategori):
    return {
        "Bahagia": "Mood kamu sedang sangat baik! Terus pertahankan kebiasaan positifmu.",
        "Sedih": "Mood kamu sedang kurang baik. Mungkin aktivitas yang kamu lakukan cukup mempengaruhi perasaanmu.",
        "Netral": "Mood kamu sedang cukup stabil, tapi bisa lebih baik."
    }.get(kategori, "")

def saran_mood(kategori):
    saran_pilihan = {
        "Bahagia": [
            "Pertahankan rutinitas positifmu hari ini 💪",
            "Bagikan kebahagiaanmu pada orang lain 😊",
            "Gunakan energi positif ini untuk mencapai targetmu 🎯"
        ],
        "Sedih": [
            "Coba lakukan aktivitas menyenangkan, seperti nonton atau jalan santai 🎬🚶",
            "Berbincanglah dengan teman atau keluarga 👨‍👩‍👧‍👦",
            "Istirahat yang cukup dan jangan terlalu memaksakan diri 😴"
        ],
        "Netral": [
            "Kamu bisa mencoba hal baru agar harimu lebih berwarna 🌈",
            "Lakukan hobi favoritmu hari ini 🎨🎸",
            "Luangkan waktu untuk diri sendiri dan refleksi 📖"
        ]
    }
    return random.choice(saran_pilihan.get(kategori, ["Tetap semangat!"]))

def kutipan_motivasi():
    quotes = [
        "🌟 Hidup adalah 10% apa yang terjadi padamu dan 90% bagaimana kamu meresponnya.",
        "✨ Setiap hari adalah kesempatan baru untuk tumbuh.",
        "🔥 Jangan biarkan kemarin menghabiskan terlalu banyak dari hari ini.",
        "💡 Kamu lebih kuat dari yang kamu pikirkan.",
        "💫 Lakukan hal kecil dengan cinta yang besar."
    ]
    return quotes[datetime.datetime.now().day % len(quotes)]

# ====================== Login Page =======================
def login():
    st.title("🔐 Login Pengguna")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("🔓 Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Berhasil login sebagai *{username}*")
        else:
            st.error("Username dan password harus diisi!")

# ====================== Main Page =======================
def main_app():
    st.sidebar.title("📋 Pilih menu")
    menu = st.sidebar.selectbox("Menu", [
        "Input Mood Harian", "Lihat Grafik Mood", "Lihat Data CSV", "Reset Data", "Tentang", "Logout"])

    if menu == "Input Mood Harian":
        st.header("📝 Input Mood & Aktivitas")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        aktivitas_dipilih = []
        for kategori, isi in aktivitas_kategori.items():
            pilihan = st.selectbox(f"{kategori}", isi["positif"] + isi["negatif"], index=None, placeholder="(Pilih satu)")
            if pilihan:
                aktivitas_dipilih.append(pilihan)
        mood = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)

        if st.button("💾 Simpan"):
            if aktivitas_dipilih:
                simpan_data(tanggal, st.session_state.username, mood, ", ".join(aktivitas_dipilih))
                klasifikasi = klasifikasi_mood(mood, aktivitas_dipilih)
                st.success(f"Mood kamu hari ini: **{klasifikasi}**")
                st.subheader("🧠 Diagnosis:")
                st.info(diagnosis_mood(klasifikasi))
                st.subheader("🎯 Saran:")
                st.warning(saran_mood(klasifikasi))
                st.subheader("📖 Kutipan Motivasi:")
                st.markdown(f"> 💡 *{kutipan_motivasi()}*")
            else:
                st.warning("⚠️ Pilih minimal satu aktivitas.")

    elif menu == "Lihat Grafik Mood":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df_user = df[df["Username"] == st.session_state.username]
            if not df_user.empty:
                df_user["Tanggal"] = pd.to_datetime(df_user["Tanggal"])
                st.line_chart(df_user.set_index("Tanggal")["Mood"])
            else:
                st.info("Belum ada data untuk pengguna ini.")
        else:
            st.warning("Belum ada data tersimpan.")

    elif menu == "Lihat Data CSV":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            st.dataframe(df[df["Username"] == st.session_state.username])
        else:
            st.warning("Data belum tersedia.")

    elif menu == "Reset Data":
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("✅ Semua data berhasil direset.")
        else:
            st.info("Tidak ada data yang perlu dihapus.")

    elif menu == "Tentang":
        st.subheader("ℹ️ Tentang Aplikasi")
        st.write("""
        SmartMood Tracker adalah aplikasi yang membantu kamu melacak mood harian 
        dan aktivitas secara efisien. Dengan fitur klasifikasi, saran, dan kutipan motivasi, 
        aplikasi ini dirancang agar kamu bisa memahami dirimu lebih baik setiap hari.
        """)

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# ====================== Start App =======================
if not st.session_state.logged_in:
    login()
else:
    main_app()

import streamlit as st
import pandas as pd
import datetime
import os

# ====================== Inisialisasi =======================
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

DATA_FILE = "smartmood_data.csv"

# ====================== Kategori & Aktivitas =======================
aktivitas_kategori = {
    "Akademik": {
        "positif": ["Mengerjakan tugas"],
        "negatif": ["Belajar"]
    },
    "Sosial": {
        "positif": ["Bertemu teman"],
        "negatif": []
    },
    "Kesehatan": {
        "positif": ["Tidur cukup"],
        "negatif": []
    },
    "Lainnya": {
        "positif": [],
        "negatif": ["Bermain game"]
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
    negatif = sum(1 for a in aktivitas if any(a in aktivitas_kategori[kat]['negatif'] for kat in aktivitas_kategori))
    positif = sum(1 for a in aktivitas if any(a in aktivitas_kategori[kat]['positif'] for kat in aktivitas_kategori))
    if mood_score >= 4 and positif > negatif:
        return "Bahagia"
    elif mood_score <= 2 and negatif >= positif:
        return "Sedih"
    else:
        return "Netral"

def saran_mood(kategori):
    saran_dict = {
        "Bahagia": "Pertahankan rutinitas positifmu hari ini, dan terus semangat!",
        "Sedih": "Coba lakukan aktivitas menyenangkan, seperti bertemu teman atau tidur cukup.",
        "Netral": "Kamu bisa mencoba hal baru agar harimu lebih berwarna."
    }
    return saran_dict.get(kategori, "Tetap semangat!")

def kutipan_motivasi():
    quotes = [
        "Hidup adalah 10% apa yang terjadi pada kita dan 90% bagaimana kita meresponsnya.",
        "Setiap hari adalah kesempatan baru untuk menjadi lebih baik.",
        "Jangan biarkan kemarin menghabiskan terlalu banyak dari hari ini."
    ]
    return quotes[datetime.datetime.now().day % len(quotes)]

# ====================== Login Page =======================
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("🔓 Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login sebagai *{username}*")
        else:
            st.error("Silakan isi semua kolom.")

# ====================== Main Page =======================
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

        if st.button("Simpan"):
            if aktivitas_dipilih:
                simpan_data(tanggal, st.session_state.username, mood, ", ".join(aktivitas_dipilih))
                kategori = klasifikasi_mood(mood, aktivitas_dipilih)
                st.success(f"Mood hari ini: {kategori}")
                st.info(saran_mood(kategori))
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
        st.write("SmartMood Tracker adalah aplikasi untuk mencatat mood harian dan aktivitas, serta memberikan saran dan motivasi berdasarkan data.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# ====================== App Start =======================
if not st.session_state.logged_in:
    login()
else:
    main_app()

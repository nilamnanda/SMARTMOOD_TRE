import streamlit as st
import pandas as pd
import datetime
import os
import random
import json
import hashlib
import altair as alt
import plotly.express as px

# ================== Konfigurasi ==================
st.set_page_config(page_title="SmartMood Tracker", layout="wide")

DATA_FILE = "smartmood_data.csv"
USER_FILE = "users.json"
BACKUP_FILE = "smartmood_backup.csv"

# ================== Session State ==================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# ================== Fungsi Utility ==================
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

# ================== Data Aktivitas ==================
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

# ================== Fungsi Mood & Diagnosa ==================
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
        for k, jenis in aktivitas_kategori.items():
            if a in jenis['positif']:
                pesan.append(f"✅ Aktivitas positif: *{a}* — terus pertahankan kebiasaan baik ini.")
            elif a in jenis['negatif']:
                pesan.append(f"⚠ Aktivitas negatif: *{a}* — coba cari cara sehat untuk mengimbanginya.")
    if not pesan:
        return "✨ Tetap semangat! Apapun harimu, kamu sudah melakukan yang terbaik."
    return "\n".join(random.sample(pesan, min(3, len(pesan))))

def kutipan_motivasi():
    quotes = [
        "🌤 Setiap pagi adalah kesempatan untuk memulai ulang dengan lebih baik.",
        "🌱 Pelan-pelan tidak apa-apa, yang penting kamu tetap berjalan.",
        "💖 Tidak semua hari harus produktif. Kadang bertahan aja udah hebat.",
        "🌈 Kamu tidak harus kuat setiap saat, yang penting kamu terus mencoba.",
        "🕊 Kadang, istirahat adalah bentuk kemajuan yang tersembunyi.",
        "🔥 Kamu punya kekuatan untuk melewati ini, bahkan jika kamu belum merasakannya sekarang.",
    ]
    return random.choice(quotes)

# ================== Fungsi Data ==================
def simpan_data(tanggal, username, mood, aktivitas, catatan):
    kategori = klasifikasi_mood(mood, aktivitas)
    new_data = pd.DataFrame([{
        "Tanggal": tanggal,
        "Username": username,
        "Mood": mood,
        "Aktivitas": ", ".join(aktivitas),
        "Catatan": catatan,
        "Klasifikasi": kategori
    }])
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(DATA_FILE, index=False)

def backup_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df.to_csv(BACKUP_FILE, index=False)

# ================== Login/Register ==================
def login_page():
    st.title("🔐 SmartMood Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        users = load_users()
        hashed = hash_password(password)
        if username in users and users[username] == hashed:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Selamat datang kembali, {username}!")
            st.rerun()
        elif username not in users:
            users[username] = hashed
            save_users(users)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Akun baru dibuat untuk {username}. Selamat datang!")
            st.rerun()
        else:
            st.error("Password salah.")

# ================== Tampilan Utama ==================
def main_app():
    st.sidebar.title("📋 Menu")
    menu = st.sidebar.radio("Pilih menu", ["Dashboard", "Input Mood", "Grafik", "Data", "Reset", "Tentang", "Logout"])

    if menu == "Dashboard":
        st.header("📊 Ringkasan Mood")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = df[df["Username"] == st.session_state.username]
            if df.empty:
                st.info("Belum ada data.")
                return
            total = df["Klasifikasi"].value_counts()
            st.metric("Hari Bahagia", total.get("Bahagia", 0))
            st.metric("Hari Sedih", total.get("Sedih", 0))
            st.metric("Hari Biasa", total.get("Biasa", 0))
            st.metric("Rata-rata Mood", round(df["Mood"].mean(), 2))
        else:
            st.info("Belum ada data.")

    elif menu == "Input Mood":
        st.header("📝 Input Mood Harian")
        tanggal = st.date_input("Tanggal", datetime.date.today())
        aktivitas_dipilih = []
        for kategori, data in aktivitas_kategori.items():
            pilihan = st.selectbox(f"{kategori}", ["(Pilih satu)"] + data['positif'] + data['negatif'])
            if pilihan != "(Pilih satu)":
                aktivitas_dipilih.append(pilihan)
        mood = st.slider("Mood (1 - 5)", 1, 5, 3)
        catatan = st.text_area("Catatan harian (opsional):")

        if st.button("✅ Simpan"):
            if aktivitas_dipilih:
                simpan_data(tanggal, st.session_state.username, mood, aktivitas_dipilih, catatan)
                kategori = klasifikasi_mood(mood, aktivitas_dipilih)
                st.success(f"Mood kamu hari ini: {kategori}")
                st.markdown(diagnosis_aktivitas(aktivitas_dipilih))
                st.markdown(f"> 💬 *{kutipan_motivasi()}*")
            else:
                st.warning("Pilih minimal satu aktivitas.")

    elif menu == "Grafik":
        st.header("📈 Grafik Mood Harian")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = df[df["Username"] == st.session_state.username]
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
            df = df.sort_values("Tanggal")
            if df.empty:
                st.warning("Belum ada data.")
                return

            # Grafik Altair
            warna_map = {"Bahagia": "#FFD700", "Biasa": "#B0BEC5", "Sedih": "#EF5350"}
            df["Warna"] = df["Klasifikasi"].map(warna_map)
            st.altair_chart(alt.Chart(df).mark_circle(size=100).encode(
                x='Tanggal:T',
                y='Mood:Q',
                color=alt.Color('Klasifikasi:N', scale=alt.Scale(domain=list(warna_map.keys()), range=list(warna_map.values()))),
                tooltip=['Tanggal:T', 'Mood:Q', 'Klasifikasi:N']
            ).properties(height=400), use_container_width=True)

            # Grafik Heatmap Plotly (14 hari terakhir)
            st.subheader("🗓 Heatmap Mood (14 Hari Terakhir)")
            df_14 = df[df["Tanggal"] >= pd.Timestamp.today() - pd.Timedelta(days=14)]
            if not df_14.empty:
                fig = px.density_heatmap(df_14, x="Tanggal", y="Username", z="Mood", nbinsx=14, color_continuous_scale="RdYlGn", title="Heatmap Mood")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Belum ada data.")

    elif menu == "Data":
        st.header("📄 Data Mood")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = df[df["Username"] == st.session_state.username]
            st.dataframe(df)
            st.download_button("📥 Download Data CSV", data=df.to_csv(index=False).encode(), file_name="smartmood_export.csv")
        else:
            st.info("Belum ada data.")

    elif menu == "Reset":
        st.warning("⚠️ Data kamu akan dihapus permanen. Backup otomatis akan dibuat.")
        if st.button("🔄 Reset Data"):
            backup_data()
            os.remove(DATA_FILE)
            st.success("Data berhasil dihapus dan backup disimpan.")
            st.rerun()

    elif menu == "Tentang":
        st.subheader("ℹ Tentang Aplikasi")
        st.markdown("""
        SmartMood Tracker membantu kamu memahami pola mood harian dengan mencatat aktivitas dan memberikan insight personal.
        Dibuat dengan ❤️ oleh tim yang peduli akan kesehatan mental.
        """)

    elif menu == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Berhasil logout. Sampai jumpa lagi!")
        st.rerun()

# ================== Jalankan Aplikasi ==================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()

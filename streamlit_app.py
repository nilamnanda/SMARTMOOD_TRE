import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import hashlib
import os
import random

DATA_FILE = "smartmood_data.csv"
USER_FILE = "users.txt"

st.set_page_config(page_title="SmartMood Tracker", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

aktivitas_kategori = {
    "Akademik": {
        "positif": ["Menyelesaikan tugas", "Belajar efektif", "Mendapat nilai bagus"],
        "negatif": ["Menunda tugas", "Tidak belajar", "Nilai jelek"]
    },
    "Sosial": {
        "positif": ["Bertemu teman", "Kumpul keluarga", "Membantu orang lain"],
        "negatif": ["Bertengkar", "Merasa kesepian", "Dikritik orang"]
    },
    "Kesehatan": {
        "positif": ["Olahraga", "Makan sehat", "Tidur cukup"],
        "negatif": ["Begadang", "Makan junk food", "Sakit"]
    },
    "Hiburan": {
        "positif": ["Nonton film", "Main game", "Mendengarkan musik"],
        "negatif": ["Main gadget terlalu lama", "Overthinking", "Scroll media sosial terus-menerus"]
    }
}

motivasi_list = [
    "Setiap hari adalah kesempatan baru untuk jadi lebih baik.",
    "Kamu sudah melangkah sejauh ini, teruskan!",
    "Tidak apa-apa merasa lelah. Istirahatlah sejenak dan lanjutkan lagi.",
    "Tersenyumlah, bahkan hari yang buruk pun akan berlalu.",
    "Kamu tidak sendirian. Kamu hebat sudah bertahan sejauh ini.",
    "Emosi datang dan pergi — yang penting kamu tetap melangkah."
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            lines = f.readlines()
        users = {}
        for line in lines:
            uname, pwd = line.strip().split(",")
            users[uname] = pwd
        return users
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        for uname, pwd in users.items():
            f.write(f"{uname},{pwd}\n")

def klasifikasi_mood(score, aktivitas):
    aktivitas_pos = sum([1 for a in aktivitas if any(a in lst for lst in [v["positif"] for v in aktivitas_kategori.values()])])
    aktivitas_neg = sum([1 for a in aktivitas if any(a in lst for lst in [v["negatif"] for v in aktivitas_kategori.values()])])
    
    if score >= 4 and aktivitas_pos > aktivitas_neg:
        return "Bahagia"
    elif score <= 2 and aktivitas_neg >= aktivitas_pos:
        return "Sedih"
    else:
        return "Biasa"

def diagnosis_aktivitas(aktivitas):
    pesan = ""
    for kategori, data in aktivitas_kategori.items():
        positif = [a for a in aktivitas if a in data["positif"]]
        negatif = [a for a in aktivitas if a in data["negatif"]]
        if positif or negatif:
            pesan += f"**{kategori}**: "
            if positif:
                pesan += f"✅ {', '.join(positif)}. "
            if negatif:
                pesan += f"⚠️ {', '.join(negatif)}. "
            pesan += "\n"
    return pesan

def kutipan_motivasi():
    return random.choice(motivasi_list)

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = df.fillna("")
        df["date"] = pd.to_datetime(df["date"])
        df["aktivitas"] = df["aktivitas"].apply(lambda x: x.split(";") if isinstance(x, str) else [])
        return df
    return pd.DataFrame(columns=["username", "date", "mood_score", "aktivitas", "mood_label"])

def save_data(df):
    df["aktivitas"] = df["aktivitas"].apply(lambda x: ";".join(x) if isinstance(x, list) else x)
    df.to_csv(DATA_FILE, index=False)

def plot_emotional_scale(df):
    emoji_map = {
        "Sedih": "😢",
        "Biasa": "😐",
        "Bahagia": "😊"
    }
    color_map = {
        "Sedih": "#ff4d4d",
        "Biasa": "#ffa94d",
        "Bahagia": "#4dcc88"
    }

    df["emoji"] = df["mood_label"].map(emoji_map)
    df["color"] = df["mood_label"].map(color_map)

    plt.figure(figsize=(10, 2))
    ax = plt.gca()
    for i, row in df.iterrows():
        ax.add_patch(patches.Rectangle((i, 0), 1, 1, color=row["color"]))
        ax.text(i + 0.5, 0.5, row["emoji"], ha='center', va='center', fontsize=20)

    plt.xlim(0, len(df))
    plt.ylim(0, 1)
    plt.axis('off')
    st.pyplot(plt)

def main_page():
    st.title("🧠 SmartMood Tracker")
    st.markdown("Halo, **{}**! Catat mood & aktivitasmu hari ini.".format(st.session_state.username))

    df = load_data()
    today = datetime.date.today()
    tanggal = st.date_input("Pilih Tanggal", today)

    mood_score = st.slider("Bagaimana perasaanmu hari ini?", 1, 5, 3, format="%d")
    aktivitas_semua = sum([v["positif"] + v["negatif"] for v in aktivitas_kategori.values()], [])
    aktivitas = st.multiselect("Apa saja yang kamu lakukan hari ini?", aktivitas_semua)

    if st.button("Simpan"):
        mood_label = klasifikasi_mood(mood_score, aktivitas)
        new_data = pd.DataFrame([{
            "username": st.session_state.username,
            "date": tanggal,
            "mood_score": mood_score,
            "aktivitas": aktivitas,
            "mood_label": mood_label
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success("✅ Data berhasil disimpan!")

    st.subheader("📊 Visualisasi Mood")
    user_df = df[df["username"] == st.session_state.username].sort_values("date")
    if not user_df.empty:
        plot_emotional_scale(user_df)

        st.subheader("🩺 Diagnosis & Refleksi")
        last_row = user_df.iloc[-1]
        st.markdown(f"**Mood Terakhir:** `{last_row['mood_label']}` (skor: {last_row['mood_score']})")
        if last_row['mood_label'] == "Biasa":
            st.info("📎 Moodmu hari ini terasa netral. Mungkin kamu mengalami kombinasi pengalaman positif dan negatif.")
        st.markdown(diagnosis_aktivitas(last_row["aktivitas"]))
        st.markdown(f"💡 _{kutipan_motivasi()}_")

def login_page():
    st.title("🔐 Login SmartMood Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()

    if st.button("Login"):
        if username in users and users[username] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Username atau password salah!")

    if st.button("Buat Akun Baru"):
        if username in users:
            st.warning("Username sudah terdaftar.")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("Akun berhasil dibuat. Silakan login.")

def logout():
    if st.session_state.logged_in:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()

if st.session_state.logged_in:
    main_page()
    logout()
else:
    login_page()

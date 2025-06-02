import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ========== Konfigurasi ==========
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

# ========== ML TRAINING ==========
def buat_dataset_sintetis():
    data = []
    for _ in range(200):
        akademik = np.random.randint(0, 10)
        sosial = np.random.randint(0, 10)
        kesehatan = np.random.randint(0, 10)
        rating = np.random.randint(1, 6)
        total = akademik + sosial + kesehatan + rating * 2
        if total < 15:
            label = "😢 Sedih"
        elif total < 22:
            label = "😐 Biasa"
        else:
            label = "😊 Bahagia"
        data.append([akademik, sosial, kesehatan, rating, label])
    return pd.DataFrame(data, columns=["Akademik", "Sosial", "Kesehatan", "Rating", "Mood"])

@st.cache_resource
def train_model():
    df = buat_dataset_sintetis()
    X = df[["Akademik", "Sosial", "Kesehatan", "Rating"]]
    y = df["Mood"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    return model, report

model, report = train_model()

# ========== Streamlit UI ==========
st.set_page_config(page_title="SmartMood ML", layout="centered")
st.title("🤖 SmartMood Tracker + ML")

st.subheader("Input Aktivitas Harian")
akademik = st.slider("Skor Akademik", 0, 10, 5)
sosial = st.slider("Skor Sosial", 0, 10, 5)
kesehatan = st.slider("Skor Kesehatan", 0, 10, 5)
rating = st.slider("Rating mood hari ini (1-5)", 1, 5, 3)

if st.button("🔍 Prediksi Mood"):
    features = [[akademik, sosial, kesehatan, rating]]
    pred = model.predict(features)[0]
    st.success(f"Prediksi mood kamu: {pred}")
    st.info(f"Saran: {saran_dict[pred]}")

st.markdown("---")
st.subheader("📊 Evaluasi Model")
st.json(report)
 

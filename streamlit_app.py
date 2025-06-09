import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================
# Fungsi bantu penilaian mood
# =========================
def klasifikasi_mood(skor, aktivitas):
    aktivitas_buruk = ['Begadang', 'Stres Berat', 'Terlambat', 'Overthinking']
    aktivitas_baik = ['Olahraga', 'Meditasi', 'Belajar', 'Bersosialisasi', 'Tidur Cukup']

    if skor >= 8:
        if any(a in aktivitas for a in aktivitas_buruk):
            return 'Biasa'
        return 'Bahagia'
    elif skor >= 6:
        if any(a in aktivitas for a in aktivitas_buruk):
            return 'Sedih'
        return 'Senang'
    elif skor >= 4:
        return 'Biasa'
    elif skor >= 2:
        return 'Sedih'
    else:
        return 'Sangat Sedih'

# =========================
# Fungsi visualisasi mood 2 minggu terakhir
# =========================
def tampilkan_mood_dua_minggu(df):
    st.subheader("📊 Mood-mu dua minggu ini")

    mood_mapping = {
        'Sangat Sedih': 0,
        'Sedih': 1,
        'Biasa': 2,
        'Senang': 3,
        'Bahagia': 4
    }
    emoji_mapping = {
        4: "😄",
        3: "🙂",
        2: "😐",
        1: "☹️",
        0: "😭"
    }
    colors = ["#ffe5ec", "#ffbaba", "#ffeabf", "#d2f6c5", "#b3f0dc"]

    df['level'] = df['Mood'].map(mood_mapping)
    df['date_str'] = pd.to_datetime(df['Tanggal']).dt.strftime("%d\n%b")

    fig = go.Figure()
    for level in range(5):
        temp_df = df[df['level'] == level]
        fig.add_trace(go.Scatter(
            x=temp_df['date_str'],
            y=[level] * len(temp_df),
            mode="markers",
            marker=dict(size=20, color=colors[level]),
            showlegend=False,
            hoverinfo="skip"
        ))

    fig.update_yaxes(
        tickvals=list(range(5)),
        ticktext=[emoji_mapping[i] for i in range(5)],
        title=""
    )
    fig.update_layout(
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        plot_bgcolor="white",
        xaxis_title="Tanggal",
        title="Mood-mu dua minggu ini"
    )
    st.plotly_chart(fig)

# =========================
# Streamlit App
# =========================
st.set_page_config(page_title="SmartMood Tracker", layout="centered")
st.title("🌟 SmartMood Tracker")

st.markdown("""
Selamat datang di SmartMood Tracker! 🌈 
Lacak suasana hatimu dan dapatkan wawasan berdasarkan aktivitas harianmu.
""")

# Simulasi Data CSV dua minggu terakhir (bisa diganti dengan data asli pengguna)
data_simulasi = {
    'Tanggal': [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)],
    'Skor Mood': [9, 8, 7, 5, 4, 4, 2, 1, 3, 6, 8, 7, 7, 9],
    'Aktivitas': [
        'Olahraga', 'Tidur Cukup', 'Belajar', 'Stres Berat', 'Begadang',
        'Overthinking', 'Begadang', 'Stres Berat', 'Belajar', 'Meditasi',
        'Olahraga', 'Bersosialisasi', 'Tidur Cukup', 'Olahraga']
}
df_mood = pd.DataFrame(data_simulasi)
df_mood['Mood'] = df_mood.apply(lambda row: klasifikasi_mood(row['Skor Mood'], row['Aktivitas']), axis=1)

# Tampilkan heatmap seperti gambar referensi
tampilkan_mood_dua_minggu(df_mood)

st.markdown("---")

# Form input baru
date_input = st.date_input("Tanggal Hari Ini", datetime.today())
skor_input = st.slider("Berapa skor mood-mu hari ini? (0 - sangat buruk, 10 - sangat baik)", 0, 10, 5)
aktivitas_input = st.multiselect("Aktivitas apa saja yang kamu lakukan hari ini?", [
    'Olahraga', 'Belajar', 'Tidur Cukup', 'Bersosialisasi', 'Meditasi',
    'Stres Berat', 'Begadang', 'Terlambat', 'Overthinking'])

if st.button("Simpan Mood Hari Ini"):
    mood_baru = klasifikasi_mood(skor_input, aktivitas_input)
    st.success(f"Mood kamu hari ini diklasifikasikan sebagai **{mood_baru}**")
    st.balloons()

    # Simpan ke data simulasi (atau bisa ke CSV/database)
    df_mood = pd.concat([df_mood, pd.DataFrame.from_records([{ 
        'Tanggal': date_input.strftime("%Y-%m-%d"),
        'Skor Mood': skor_input,
        'Aktivitas': ', '.join(aktivitas_input),
        'Mood': mood_baru
    }])], ignore_index=True)

    # Update visualisasi
    tampilkan_mood_dua_minggu(df_mood)

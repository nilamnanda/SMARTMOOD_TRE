import streamlit as st
import hashlib
import json
import os

# ============================
# FUNGSI LOGIN & REGISTER
# ============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.txt", "w") as f:
        json.dump(users, f)

def login_page():
    st.title("🔐 Login SmartMood Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()

    if st.button("Login / Register"):
        if username == "" or password == "":
            st.warning("Silakan isi username dan password.")
            return

        if username in users:
            if users[username] == hash_password(password):
                st.success(f"Selamat datang kembali, {username}!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Password salah. Coba lagi.")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success(f"Akun baru berhasil dibuat. Selamat datang, {username}!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()

# ============================
# APP UTAMA
# ============================
def main():
    st.set_page_config(page_title="SmartMood Tracker", layout="centered", page_icon="🧠")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        st.success(f"Halo, {st.session_state.username}! Kamu sudah login.")
        # Di sini nanti kamu bisa lanjut ke halaman utama SmartMood Tracker

if __name__ == "__main__":
    main()

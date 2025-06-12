import streamlit as st
from user_data import load_users, save_users

USERS = load_users()

menu = st.sidebar.radio("Menu", ["Login", "Registrasi"])

if menu == "Login":
    st.title("🔐 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USERS and USERS[username] == password:
            st.success(f"Selamat datang, {username}!")
            if username == "admin":
                st.subheader("📋 Daftar Seluruh User")
                st.json(USERS)
        else:
            st.error("Username atau password salah!")

elif menu == "Registrasi":
    st.title("📝 Registrasi Pengguna Baru")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_pass = st.text_input("Konfirmasi Password", type="password")
    daftar_btn = st.button("Daftar")

    if daftar_btn:
        if username == "" or password == "" or confirm_pass == "":
            st.warning("Semua kolom harus diisi.")
        elif username in USERS:
            st.warning("Username sudah digunakan. Pilih yang lain.")
        elif password != confirm_pass:
            st.warning("Password dan konfirmasi tidak sama.")
        else:
            USERS[username] = password
            save_users(USERS)
            st.success("Registrasi berhasil! Silakan login.")

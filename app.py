import streamlit as st
import json
import os
import hashlib
import pandas as pd
import altair as alt
from datetime import date
import io
from pandas import ExcelWriter

def hash_password(password):
     return hashlib.sha256(password.encode()).hexdigest()

# ---------- Konfigurasi ----------
st.set_page_config(page_title="Reporting Pengeluaran", page_icon="💸")
USER_FILE = "users.json"

# ---------- Inisialisasi User ----------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({"admin": "admin123"}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------- Session State ----------
for key in ["logged_in", "user", "show_register"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else "" if key == "user" else False

# ---------- UI Sidebar: Login atau Daftar ----------
st.sidebar.title(":lock: Login")

if not st.session_state.logged_in:
    if not st.session_state.show_register:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_btn = st.sidebar.button("Login")

        if login_btn:
            users = load_users()
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.sidebar.error("Username atau password salah!")

        st.sidebar.markdown("---")
        if st.sidebar.button("Belum punya akun? Daftar"):
            st.session_state.show_register = True
        st.stop()

    else:
        st.sidebar.subheader(":memo: Registrasi")
        new_username = st.sidebar.text_input("Username Baru")
        new_password = st.sidebar.text_input("Password Baru", type="password")
        confirm_password = st.sidebar.text_input("Konfirmasi Password", type="password")
        daftar_btn = st.sidebar.button("Daftar")

        if daftar_btn:
            users = load_users()
            if new_username == "" or new_password == "" or confirm_password == "":
                st.sidebar.warning("Semua kolom harus diisi.")
            elif new_username in users:
                st.sidebar.warning("Username sudah digunakan.")
            elif new_password != confirm_password:
                st.sidebar.warning("Password tidak cocok.")
            else:
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                users[new_username] = hashed_password
                save_users(users)
                st.sidebar.success("Registrasi berhasil. Silakan login.")
                st.session_state.show_register = False

        if st.sidebar.button("Kembali ke Login"):
            st.session_state.show_register = False
        st.stop()

# ---------- Setelah Login ----------
st.sidebar.success(f"Login sebagai: {st.session_state.user}")
if st.sidebar.button("Logout", key="logout"):
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.rerun()

# ---------- Panel Admin ----------
if st.session_state.user == "admin":
    menu_admin = st.sidebar.radio("👑 Panel Admin", ["Daftar Semua User", "Laporan Pengeluaran"])

    if menu_admin == "Daftar Semua User":
             st.subheader("📋 Daftar Seluruh Pengguna")
             st.title(":busts_in_silhouette: Daftar Semua User")
             st.json(load_users())
    if st.session_state.user == "admin":
        # 👇 Tempel di sini kodingan admin panel
        st.title("🛠️ Admin Panel")
        menu_admin = st.radio("Pilih Fitur", ["Daftar Semua User", "Reset Password", "Hapus User"])

        users = load_users()

    if menu_admin == "Reset Password":
            user_list = [u for u in users.keys() if u != "admin"]
            target_user = st.selectbox("Pilih user", user_list)
            new_pass = st.text_input("Password baru", type="password")
    if st.button("🔁 Reset Password"):
                users[target_user] = new_pass
                with open("users.json", "w") as f:
                    json.dump(users, f)
                st.success(f"Password untuk {target_user} telah direset.")

    if menu_admin == "Hapus User":
            user_list = [u for u in users.keys() if u != "admin"]
            target_user = st.selectbox("Pilih user untuk dihapus", user_list)
    if st.button("🗑️ Hapus User"):
                users.pop(target_user)
                with open("users.json", "w") as f:
                    json.dump(users, f)
                st.success(f"User {target_user} berhasil dihapus.")
    elif menu_admin == "Laporan Pengeluaran" :
         st.title (": money_with_wings: Laporan Pengeluaran Bulanan")
else:
    st.title(":money_with_wings: Laporan Pengeluaran Bulanan")

# ---------- Data & Input ----------
user_key = f"pengeluaran_{st.session_state.user}"
if user_key not in st.session_state:
    st.session_state[user_key] = []
data = st.session_state[user_key]

with st.form("form_pengeluaran"):
    tanggal = st.date_input("Tanggal", value=date.today())
    kategori = st.selectbox("Kategori", ["Makan", "Transport", "Belanja", "Lainnya"])
    keterangan = st.text_input("Keterangan")
    nominal_input = st.text_input("Nominal (Rp)")

    if nominal_input.replace(".", "").isdigit():
        nominal = int(nominal_input.replace(".", ""))
        formatted_nominal = f"{nominal:,}".replace(",", ".")
        st.info(f":moneybag: Nominal yang akan disimpan: Rp {formatted_nominal}")
    else:
        nominal = 0
        st.warning("Masukkan hanya angka untuk nominal.")

    simpan = st.form_submit_button("Simpan Pengeluaran")

if simpan and nominal > 0:
    data.append({"tanggal": str(tanggal), "kategori": kategori, "Keterangan": keterangan, "nominal": nominal})
    st.rerun()

# ---------- Output Daftar & Chart ----------
st.subheader(":page_facing_up: Daftar Pengeluaran")
if not data:
    st.info("Belum ada data pengeluaran.")
else:
    for i, item in enumerate(data):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"{i+1}. {item['tanggal']} | {item['kategori']} | Rp {item['nominal']:,} | {item.get('Keterangan', '-')}")
        with col2:
            if st.button("🖑️ Hapus", key=f"hapus-{i}"):
                data.pop(i)
                st.rerun()

    df = pd.DataFrame(data)
    df_chart = df.groupby("kategori")["nominal"].sum().reset_index()
    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("kategori:N", title="Kategori"),
        y=alt.Y("nominal:Q", title="Total Pengeluaran (Rp)"),
        tooltip=["kategori", "nominal"]
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

# ---------- Download Laporan ----------
if data:
    st.subheader(":paperclip: Download Laporan Pengeluaran")
    output = io.BytesIO()
    df = pd.DataFrame(data)

    with ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Pengeluaran")
        writer.close()
        processed_data = output.getvalue()

    st.download_button(
        label="⬇️ Download Excel",
        data=processed_data,
        file_name="laporan_pengeluaran.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

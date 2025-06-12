import pandas as pd
import altair as alt
import streamlit as st
from datetime import date
import io
from pandas import ExcelWriter

# Konfigurasi tampilan halaman
st.set_page_config(page_title="Reporting Pengeluaran", page_icon="💸")
st.title("💸 Laporan Pengeluaran Bulanan")

# Inisialisasi session state
if "pengeluaran" not in st.session_state:
    st.session_state.pengeluaran = []

# Form input pengeluaran
with st.form("form_pengeluaran"):
    tanggal = st.date_input("Tanggal", value=date.today())
    kategori = st.selectbox("Kategori", ["Makan", "Transport", "Belanja", "Lainnya"])
    keterangan = st.text_input("Keterangan")
    nominal_input = st.text_input("Nominal (Rp)")

    if nominal_input.replace(".", "").isdigit():
        nominal = int(nominal_input.replace(".", ""))
        formatted_nominal = f"{nominal:,}".replace(",", ".")
        st.info(f"💰 Nominal yang akan disimpan: Rp {formatted_nominal}")
    else:
        nominal = 0
        st.warning("Masukkan hanya angka untuk nominal.")

    simpan = st.form_submit_button("Simpan Pengeluaran")

# Simpan data setelah submit
if simpan and nominal > 0:
    st.session_state.pengeluaran.append({
        "tanggal": str(tanggal),
        "kategori": kategori,
        "Keterangan": keterangan,
        "nominal": nominal
    })

    st.rerun()

# Daftar pengeluaran
st.subheader("📋 Daftar Pengeluaran")

if not st.session_state.pengeluaran:
    st.info("Belum ada data pengeluaran.")
else:
    for i, item in enumerate(st.session_state.pengeluaran):
        keterangan_item = item.get("Keterangan", "-")
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"{i+1}. {item['tanggal']} | {item['kategori']} | Rp {item['nominal']:,} | {keterangan_item}")
        with col2:
            if st.button("🗑️ Hapus", key=f"hapus-{i}"):
                st.session_state.pengeluaran.pop(i)
                st.experimental_rerun()

# Visualisasi pengeluaran
if st.session_state.pengeluaran:
    df = pd.DataFrame(st.session_state.pengeluaran)
    df_chart = df.groupby("kategori")["nominal"].sum().reset_index()

    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("kategori:N", title="Kategori"),
        y=alt.Y("nominal:Q", title="Total Pengeluaran (Rp)"),
        tooltip=["kategori", "nominal"]
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)

# Download laporan
if st.session_state.pengeluaran:
    st.subheader("📎 Download Laporan Pengeluaran")
    output = io.BytesIO()
    df = pd.DataFrame(st.session_state.pengeluaran)

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

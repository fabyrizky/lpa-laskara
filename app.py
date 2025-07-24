# Streamlit LPA-LASKARA Surveyor Hub
# Author: <M Faby Rizky K>
# Requirements: streamlit, pandas, openpyxl, plotly, streamlit-authenticator
# pip install streamlit pandas openpyxl plotly streamlit-authenticator

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import uuid
import os

# ──────────────────────────────────────────────
# 0. CONFIG & STYLING
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="LASKARA Surveyor Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Simple in-memory user store (demo only). Replace with DB / OAuth later.
USERS = {
    "surveyor1": {"name": "Surveyor A", "password": "laskara2025"},
    "surveyor2": {"name": "Surveyor B", "password": "laskara2025"},
}

def check_login(username, password):
    return USERS.get(username, {}).get("password") == password

# ──────────────────────────────────────────────
# 1. AUTHENTICATION FLOW (minimal)
# ──────────────────────────────────────────────
def login_form():
    st.title("Selamat datang di LASKARA Surveyor Hub 🏥")
    st.markdown("Silakan login untuk melanjutkan.")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted and check_login(username, password):
            st.session_state["user"] = username
            st.session_state["name"] = USERS[username]["name"]
            st.rerun()
        elif submitted:
            st.error("Username / Password salah!")

# ──────────────────────────────────────────────
# 2. MAIN APP
# ──────────────────────────────────────────────
def main_app():
    st.sidebar.title(f"Halo, {st.session_state['name']}!")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    menu = st.sidebar.selectbox(
        "Menu Utama",
        [
            "🏠 Dashboard Ringkas",
            "📝 Form Survei Baru",
            "📊 Riwayat & Analitik",
            "📥 Download Template",
            "ℹ️ Panduan & Etika",
        ],
    )

    # Ensure session state for survey data
    if "surveys" not in st.session_state:
        st.session_state["surveys"] = []

    # ─────────────────────────────
    if menu == "🏠 Dashboard Ringkas":
        st.header("Dashboard Ringkas")
        total = len(st.session_state["surveys"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Survei", total)
        col2.metric("Klinik Utama", sum(1 for s in st.session_state["surveys"] if s["Jenis"] == "Klinik Utama"))
        col3.metric("Laboratorium", sum(1 for s in st.session_state["surveys"] if s["Jenis"] == "Laboratorium"))

        if total:
            df = pd.DataFrame(st.session_state["surveys"])
            fig = px.histogram(
                df,
                x="Jenis",
                color="Hasil",
                title="Distribusi Hasil Akreditasi",
                category_orders={"Hasil": ["Memenuhi", "Perbaikan", "Tidak Memenuhi"]},
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─────────────────────────────
    elif menu == "📝 Form Survei Baru":
        st.header("Form Survei Baru")
        with st.form("survei"):
            col1, col2 = st.columns(2)
            jenis = col1.selectbox("Jenis Fasyankes", ["Klinik Utama", "Laboratorium", "UPD"])
            nama = col1.text_input("Nama Fasyankes")
            prov = col2.selectbox("Provinsi", sorted(["Jakarta", "Jawa Barat", "Bali", "Papua", "Sulawesi", "Kalimantan", "Lainnya"]))
            tgl = col2.date_input("Tanggal Survei", datetime.date.today())
            hasil = st.select_slider("Hasil Akreditasi", options=["Memenuhi", "Perbaikan", "Tidak Memenuhi"])
            catatan = st.text_area("Catatan / Temuan Utama", height=150)

            if st.form_submit_button("Simpan Survei"):
                record = {
                    "ID": str(uuid.uuid4())[:8],
                    "Jenis": jenis,
                    "Nama Fasyankes": nama,
                    "Provinsi": prov,
                    "Tanggal": tgl.isoformat(),
                    "Hasil": hasil,
                    "Catatan": catatan,
                }
                st.session_state["surveys"].append(record)
                st.success("Survei tersimpan! ✔️")

    # ─────────────────────────────
    elif menu == "📊 Riwayat & Analitik":
        st.header("Riwayat & Analitik")
        if not st.session_state["surveys"]:
            st.info("Belum ada data survei.")
        else:
            df = pd.DataFrame(st.session_state["surveys"])
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"laskara_survei_{datetime.date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    # ─────────────────────────────
    elif menu == "📥 Download Template":
        st.header("Download Template")
        st.write("Gunakan template Excel berikut untuk impor massal.")
        template = pd.DataFrame(
            columns=["Jenis", "Nama Fasyankes", "Provinsi", "Tanggal", "Hasil", "Catatan"]
        )
        st.download_button(
            label="📄 Download Template Excel",
            data=template.to_csv(index=False).encode("utf-8"),
            file_name="template_survei_laskara.csv",
            mime="text/csv",
        )

    # ─────────────────────────────
    elif menu == "ℹ️ Panduan & Etika":
        st.header("Panduan & Kode Etik Surveyor")
        st.markdown(
            """
        ### Prinsip Utama LASKARA
        1. **Integritas** – Tidak menerima gratifikasi apapun.  
        2. **Objektivitas** – Penilaian berbasis bukti & standar.  
        3. **Kerahasiaan** – Data pasien & fasyankes dilindungi.  
        4. **Profesionalisme** – Mengikuti SOP & etika surveyor.

        ### Konflik Kepentingan
        - Hindari jabatan rangkap atau afiliasi dengan fasyankes yang disurvei.  
        - Laporkan pelanggaran via [laskara-ethics@example.com](mailto:laskara-ethics@example.com).
        """,
            unsafe_allow_html=True,
        )

# ──────────────────────────────────────────────
# 3. ROUTING
# ──────────────────────────────────────────────
if "user" not in st.session_state:
    login_form()
else:
    main_app()

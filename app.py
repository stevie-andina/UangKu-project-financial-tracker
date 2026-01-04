import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

#halaman utama
st.set_page_config(page_title="UangKu - Financial Tracker", layout="wide")

st.markdown("""
            <style>
            /* mengubah background utama */
            .stApp {
                background-color: #0e1117;
                color: #e0e0e0;
            }
            /*style card*/
            div[data-testid="stMetricValue"] {
                color:#d4af37;
            }
            /*style tombol*/
            .stButton>button {
                background-color: #00695c;
                color: white;
                border-radius: 10px;
                border: none;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #004d40;
                border: 1px solid #d4af37;
            }
            /* input field */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #1a1c23;
                color: #ffffff;
                border: 1px solid #333;
            }
            </style>
            """, unsafe_allow_html=True)

DB_FILE ="data_uangku.csv"
BUDGET_FILE ="pemasukan_config.txt"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if 'Jumlah' in df.columns:
                df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce').fillna(0)
            return df
        except Exception:
            return pd.DataFrame(columns=['Tanggal', 'Tipe', 'Kategori', 'Jumlah', 'Keterangan'])
    return pd.DataFrame(columns=['Tanggal', 'Tipe', 'Kategori', 'Jumlah', 'Keterangan'])

def get_pemasukan():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, 'r') as file:
            try:
                return float(file.read().strip())
            except ValueError:
                return 0.0
    return 0.0

#header
st.title("💵 UangKu - Self Financial Tracker")
st.markdown("*Hemat hey anak kos!*")
st.divider()

#muat data
st.sidebar.title("➤ Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard", "Input Transaksi", "Pengaturan"])

data_df = load_data()
current_pemasukan = get_pemasukan()

if menu == "Pengaturan":
    st.header("⚙️Pengaturan Pemasukan Bulanan")
    new_pemasukan = st.number_input("Masukkan jumlah pemasukan bulanan Anda (Rp)", min_value=0.0, value=current_pemasukan, step=100000.0, format="%f")
    if st.button("Update Pemasukan"):
        with open(BUDGET_FILE, 'w') as file:
            file.write(str(new_pemasukan))
        st.success("Pemasukan berhasil disimpan!")
        st.rerun()
    
    st.divider()
    if st.button("Reset Data Transaksi"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.clear()
        st.warning("Data transaksi dihapus.")
        st.rerun()

elif menu == "Input Transaksi":
    st.header("📝 Input Transaksi Baru")
    with st.form("transaksi_form"):
        tipe = st.selectbox("Tipe Transaksi", ["Pengeluaran", "Tabungan"])
        kategori = st.text_input("Kategori")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%f")
        keterangan = st.text_area("Keterangan (opsional)")
        submitted = st.form_submit_button("Simpan Transaksi")
        
        if submitted:
            if jumlah <= 0:
                st.error("Jumlah harus diisi lebih dari 0.")
            else:
                ket_final = keterangan.strip() if keterangan.strip() != "" else "-"
                
                new_entry = pd.DataFrame([{
                    'Tanggal': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Tipe': tipe,
                    'Kategori': kategori if tipe == "Pengeluaran" else "Tabungan",
                    'Jumlah': jumlah,
                    'Keterangan': ket_final
                }])
                data_df = pd.concat([data_df, new_entry], ignore_index=True)
                data_df.to_csv(DB_FILE, index=False)
                st.success("Transaksi berhasil disimpan!")
                st.balloons()
                st.rerun()

elif menu == "Tabungan Pribadi":
    st.header("🏦 Alokasi Tabungan Bulanan")
    st.info("Catat uang yang kamu simpan.")
    with st.form("form_tabungan_khusus", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            jml_tab = st.number_input("Nominal (Rp)", min_value=0.0, step=50000.0)
        with col2:
            ket_tab = st.text_input("Tujuan Tabungan (Boleh Kosong)")
        
        if st.form_submit_button("Simpan ke Tabungan"):
            if jml_tab > 0:
                ket_tab_final = ket_tab.strip() if ket_tab.strip() != "" else "-"
                new_tab = pd.DataFrame([{
                    "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Tipe": "Tabungan",
                    "Kategori": "Tabungan",
                    "Jumlah": jml_tab,
                    "Keterangan": ket_tab_final
                }])
                data_df = pd.concat([data_df, new_tab], ignore_index=True)
                data_df.to_csv(DB_FILE, index=False)
                st.success(f"Berhasil menabung Rp {jml_tab:,.0f}!")
                st.rerun()
            else:
                st.error("Masukkan nominal tabungan.")

else: #Dashboard 
    mask_pengeluaran = data_df['Tipe'] == 'Pengeluaran'
    mask_tabungan = data_df['Tipe'] == 'Tabungan'

    total_pengeluaran = data_df.loc[mask_pengeluaran, 'Jumlah'].sum()
    total_tabungan = data_df.loc[mask_tabungan, 'Jumlah'].sum()
    sisa_saldo = current_pemasukan - total_pengeluaran - total_tabungan

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pemasukan Bulanan (Rp)", f"{current_pemasukan:,.0f}")
    m2.metric("Total Pengeluaran (Rp)", f"{total_pengeluaran:,.0f}")
    m3.metric("Total Tabungan (Rp)", f"{total_tabungan:,.0f}")
    m4.metric("Sisa Saldo (Rp)", f"{sisa_saldo:,.0f}")
    
    st.divider()

    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.subheader("📊 Analisis Keuangan")
        if not data_df.empty:
            fig_pie = px.pie(
                data_df,
                values='Jumlah',
                names='Kategori',
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Emrld,
                title="Persentase Alokasi Uang"
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Belum ada data untuk dianalisis.")
            
    with col_chart2:
        st.subheader("📜 Riwayat Transaksi Terbaru")
        if not data_df.empty:
            # Tampilkan 10 transaksi terakhir
            st.dataframe(
                data_df.sort_values(by='Tanggal', ascending=False).head(10), 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("Riwayat masih kosong.")

        
    #footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2026 UangKu. by Stevy - All rights reserved.")

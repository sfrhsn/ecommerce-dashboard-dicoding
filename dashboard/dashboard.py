import streamlit as st
import pandas as pd
from pathlib import Path

# Konfigurasi Halaman
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

st.title("E-Commerce Public Dataset Analysis")
st.write(
    "Dashboard interaktif untuk menganalisis tren pesanan, total pembayaran, "
    "kinerja pengiriman, dan skor ulasan pelanggan."
)

# Jalur File Data
data_path = Path(__file__).parent / "main_data.csv"
review_path = Path(__file__).parent / "review_comparison.csv"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    
    if "total_orders_x" in df.columns:
        df.rename(columns={"total_orders_x": "total_orders"}, inplace=True)
    elif "total_orders_y" in df.columns:
        df.rename(columns={"total_orders_y": "total_orders"}, inplace=True)
        
    numeric_cols = ["total_orders", "total_payment", "late_percentage", "avg_delivery_days"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    return df

# Verifikasi File Utama
if not data_path.exists():
    st.error(f"File `main_data.csv` tidak ditemukan di folder `{Path(__file__).parent}`.")
    st.stop()

try:
    monthly = load_data(data_path)
except Exception as e:
    st.error(f"Gagal membaca data utama: {e}")
    st.stop()

# Mengurutkan bulan 
if "month" in monthly.columns:
    monthly["month"] = monthly["month"].astype(str)
    monthly = monthly.sort_values("month").reset_index(drop=True)

# Sidebar Filter Bulan
st.sidebar.header("Filter Data")

if "month" in monthly.columns and not monthly.empty:
    months = monthly["month"].dropna().unique().tolist()
    selected_months = st.sidebar.multiselect(
        "Pilih Periode Bulan:",
        options=months,
        default=months
    )
    filtered = monthly[monthly["month"].isin(selected_months)].copy()
else:
    filtered = monthly.copy()
    st.sidebar.info("Data bulanan belum tersedia.")


st.subheader("Ringkasan Performa")
col1, col2, col3, col4 = st.columns(4)

total_orders = filtered["total_orders"].sum() if "total_orders" in filtered.columns else 0
total_payment = filtered["total_payment"].sum() if "total_payment" in filtered.columns else 0
avg_late = filtered["late_percentage"].mean() if "late_percentage" in filtered.columns else 0
avg_days = filtered["avg_delivery_days"].mean() if "avg_delivery_days" in filtered.columns else 0

col1.metric("Total Pesanan", f"{total_orders:,.0f}")
col2.metric("Total Pembayaran", f"BRL {total_payment:,.2f}")
col3.metric("Rata-rata Keterlambatan", f"{avg_late:.2f}%")
col4.metric("Rata-rata Durasi", f"{avg_days:.1f} Hari")

st.markdown("---")


st.subheader("1. Tren Pesanan dan Total Pembayaran Bulanan")

if not filtered.empty and "total_orders" in filtered.columns and "total_payment" in filtered.columns:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("**Jumlah Pesanan (Orders)**")
        chart_data1 = filtered[["month", "total_orders"]].set_index("month")
        st.line_chart(chart_data1)
        
    with col_chart2:
        st.write("**Total Pembayaran (Payment Value)**")
        chart_data2 = filtered[["month", "total_payment"]].set_index("month")
        st.line_chart(chart_data2)


st.subheader("2. Ketepatan Waktu dan Rata-rata Durasi Pengiriman")

if not filtered.empty and "late_percentage" in filtered.columns and "avg_delivery_days" in filtered.columns:
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        st.write("**Persentase Keterlambatan (%)**")
        chart_del1 = filtered[["month", "late_percentage"]].set_index("month")
        st.line_chart(chart_del1)
        
    with col_del2:
        st.write("**Rata-rata Waktu Pengiriman (Hari)**")
        chart_del2 = filtered[["month", "avg_delivery_days"]].set_index("month")
        st.line_chart(chart_del2)


st.subheader("3. Rata-Rata Skor Ulasan Berdasarkan Status Pengiriman")

if review_path.exists():
    reviews_data = pd.read_csv(review_path)
    if "average_review_score" in reviews_data.columns:
        reviews_data["average_review_score"] = pd.to_numeric(reviews_data["average_review_score"], errors="coerce")
    
    col_rev1, col_rev2 = st.columns([1, 1])
    with col_rev1:
        st.dataframe(reviews_data[["delivery_status", "average_review_score", "total_reviews"]], use_container_width=True, hide_index=True)
    with col_rev2:
        st.bar_chart(reviews_data.set_index("delivery_status")["average_review_score"])

with st.expander("Lihat Detail Tabel Data Bulanan"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
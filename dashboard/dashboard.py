
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

st.title("E-Commerce Public Dataset")
st.write(
    "Dashboard untuk menganalisis tren pesanan, pembayaran, "
    "ketepatan pengiriman, dan ulasan pelanggan."
)

data_path = Path(__file__).parent / "main_data.csv"

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

if not data_path.exists():
    st.error(
        "File main_data.csv tidak ditemukan. "
        "Pastikan file berada di folder yang sama dengan dashboard.py."
    )
    st.stop()

try:
    data = load_data(data_path)
except Exception as e:
    st.error(f"Data gagal dibaca: {e}")
    st.stop()

# Memeriksa kolom yang dibutuhkan
required_columns = [
    "record_type",
    "month",
    "total_orders",
    "total_payment",
    "late_percentage",
    "avg_delivery_days",
    "delivery_status",
    "average_review_score",
    "total_reviews"
]

missing_columns = [
    col for col in required_columns if col not in data.columns
]

if missing_columns:
    st.error(
        "Kolom berikut belum tersedia di main_data.csv: "
        + ", ".join(missing_columns)
    )
    st.stop()

data["record_type"] = data["record_type"].astype(str).str.strip().str.lower()

# Mengubah kolom angka agar bisa dihitung
numeric_columns = [
    "total_orders",
    "total_payment",
    "late_percentage",
    "avg_delivery_days",
    "average_review_score",
    "total_reviews"
]

for column in numeric_columns:
    data[column] = pd.to_numeric(data[column], errors="coerce")

sales = data[data["record_type"] == "sales"].copy()
delivery = data[data["record_type"] == "delivery"].copy()
monthly_data = data[data["record_type"] == "monthly"].copy()
reviews = data[data["record_type"] == "review"].copy()

# Mendukung CSV yang menggunakan kategori monthly
if not monthly_data.empty:
    if sales.empty:
        sales = monthly_data.copy()
    if delivery.empty:
        delivery = monthly_data.copy()

# Menggabungkan data penjualan dan pengiriman berdasarkan bulan
sales_monthly = (
    sales.groupby("month", as_index=False)
    .agg(
        total_orders=("total_orders", "sum"),
        total_payment=("total_payment", "sum")
    )
)

delivery_monthly = (
    delivery.groupby("month", as_index=False)
    .agg(
        late_percentage=("late_percentage", "mean"),
        avg_delivery_days=("avg_delivery_days", "mean")
    )
)

monthly = pd.merge(
    sales_monthly,
    delivery_monthly,
    on="month",
    how="outer"
)

# Mengurutkan bulan secara kronologis jika format YYYY-MM
monthly = monthly.sort_values("month").reset_index(drop=True)

st.sidebar.header("Filter Data")

if not monthly.empty:
    months = monthly["month"].dropna().astype(str).unique().tolist()

    selected_months = st.sidebar.multiselect(
        "Pilih bulan",
        options=months,
        default=months
    )

    filtered = monthly[
        monthly["month"].astype(str).isin(selected_months)
    ].copy()
else:
    filtered = monthly.copy()
    st.sidebar.info("Data bulanan belum tersedia.")

st.subheader("Ringkasan")

col1, col2, col3 = st.columns(3)

total_orders = filtered["total_orders"].sum()
total_payment = filtered["total_payment"].sum()

late_values = filtered["late_percentage"].dropna()
average_late = late_values.mean() if not late_values.empty else None

col1.metric(
    "Total Pesanan",
    f"{total_orders:,.0f}"
)

col2.metric(
    "Total Pembayaran",
    f"R$ {total_payment:,.2f}"
)

col3.metric(
    "Rata-rata Keterlambatan",
    f"{average_late:.2f}%"
    if average_late is not None
    else "Belum tersedia"
)

st.subheader("1. Tren Pesanan dan Pembayaran Bulanan")

if not filtered.empty:
    sales_chart = filtered.set_index("month")[
        ["total_orders", "total_payment"]
    ]

    st.line_chart(sales_chart)
else:
    st.info("Pilih setidaknya satu bulan untuk melihat grafik.")

st.subheader("2. Ketepatan dan Waktu Pengiriman")

delivery_chart_data = filtered[
    ["month", "late_percentage", "avg_delivery_days"]
].dropna(
    how="all",
    subset=["late_percentage", "avg_delivery_days"]
)

if not delivery_chart_data.empty:
    delivery_chart = delivery_chart_data.set_index("month")[
        ["late_percentage", "avg_delivery_days"]
    ]

    st.line_chart(delivery_chart)

    st.caption(
        "Persentase keterlambatan ditampilkan dalam persen, "
        "sedangkan rata-rata waktu pengiriman ditampilkan dalam hari."
    )
else:
    st.info("Data pengiriman tidak tersedia untuk filter bulan ini.")

st.subheader("3. Skor Ulasan Berdasarkan Ketepatan Pengiriman")

if not reviews.empty:
    review_summary = (
        reviews.groupby("delivery_status", as_index=False)
        .agg(
            average_review_score=("average_review_score", "mean"),
            total_reviews=("total_reviews", "sum")
        )
    )

    review_chart = review_summary.set_index("delivery_status")[
        ["average_review_score"]
    ]

    st.bar_chart(review_chart)

    st.dataframe(
        review_summary,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Data perbandingan ulasan belum tersedia.")

with st.expander("Lihat data bulanan"):
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )


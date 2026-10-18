
# E-Commerce Data Analysis

## Deskripsi
Proyek ini menganalisis data E-Commerce Public Dataset untuk memahami tren pesanan dan pembayaran, ketepatan pengiriman, serta hubungan ketepatan pengiriman dengan ulasan pelanggan.

## Tujuan Analisis
1. Mengetahui tren jumlah pesanan dan total pembayaran setiap bulan.
2. Menganalisis persentase keterlambatan dan rata-rata waktu pengiriman.
3. Membandingkan skor ulasan pelanggan berdasarkan status pengiriman.

## Struktur Folder
- `dashboard/`: berisi file dashboard Streamlit dan data hasil analisis.
- `data/`: berisi dataset yang digunakan.
- `notebook.ipynb`: proses analisis data.
- `requirements.txt`: daftar library Python yang dibutuhkan.

## Cara Menjalankan Dashboard
1. Pastikan Python sudah terinstal.
2. Instal library yang dibutuhkan:

   `pip install -r requirements.txt`

3. Masuk ke folder dashboard:

   `cd dashboard`

4. Jalankan dashboard:

   `python -m streamlit run dashboard/dashboard.py`

5. Buka alamat lokal yang ditampilkan di terminal.

## Teknologi
- Python
- Pandas
- Streamlit
- Matplotlib dan Seaborn untuk visualisasi pada notebook.

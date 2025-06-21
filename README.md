Berikut adalah README untuk dokumentasi proyek tugas kelompok 6 BI-B 2025:

---

# 📊 Proyek Business Intelligence - Kelompok 6 BI-B 2025

## 📁 Deskripsi Proyek

Proyek ini merupakan bagian dari tugas kuliah Business Intelligence 2025 yang bertujuan untuk melakukan proses **ETL (Extract, Transform, Load)** dan menampilkan hasil visualisasi data menggunakan dashboard interaktif.

---

## 👥 Anggota Kelompok

* **Ruchil Amelinda** (2211522006)
* **Vioni Wijaya Putri** (2211522016)
* **Isra Rahma Dina** (2211522030)

---

## 🚀 Langkah Menjalankan Proyek

### 1. 📦 Persiapan Database

* Buka MySQL dan buat database baru dengan nama:

```sql
CREATE DATABASE playstoredb;
```

* Jalankan file `schema.sql` untuk membuat struktur tabel yang dibutuhkan:

```sql
-- Di dalam Query Editor MySQL atau melalui CLI:
USE playstoredb;
-- Salin seluruh isi dari schema.sql dan jalankan
```

### 2. 📥 Instalasi Dependencies Python

Pastikan kamu menggunakan Python 3.8 atau lebih baru. Jalankan perintah berikut untuk menginstall semua dependensi:

```bash
pip install -r requirements.txt
```

### 3. 🔄 Menjalankan Proses ETL

Lakukan proses ETL untuk mengambil data dari dataset dan memasukkannya ke dalam database:

```bash
python etl/etl_process.py
```

Tunggu proses selesai. Proses ini akan memuat dan membersihkan data, lalu memasukkannya ke database `playstoredb`.

### 4. 📊 Menjalankan Dashboard

Terakhir, jalankan dashboard interaktif untuk melihat visualisasi:

```bash
python dashboard/app.py
```

Dashboard akan terbuka di browser pada `http://localhost:5000` atau alamat yang tertera di terminal.

---

## 📎 Struktur Folder

```
├── dashboard/
│   └── app.py
├── etl/
│   └── etl_process.py
├── dw/
│   └── schema.sql
├── requirements.txt
└── README.md
```

---

## 🛠 Tools & Teknologi

* Python
* MySQL
* Pandas, SQLAlchemy
* Flask (untuk dashboard)
* Matplotlib / Plotly / Seaborn (visualisasi)

---

## 📌 Catatan

* Pastikan MySQL Server aktif sebelum menjalankan ETL.
* Jika terdapat error koneksi database, cek konfigurasi `host`, `user`, `password`, dan `database` di file koneksi ETL.

---

Jika butuh bantuan lebih lanjut, silakan hubungi anggota kelompok melalui platform komunikasi yang telah disepakati.

---


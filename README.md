# 🛡️ Delta Force Community Bot (Enterprise Edition)

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Aiogram Version](https://img.shields.io/badge/aiogram-3.4+-orange.svg)
![Database](https://img.shields.io/badge/database-SQLAlchemy-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

Bot Telegram **Enterprise-Grade** yang dirancang khusus untuk koordinasi komunitas **Delta Force Indonesia**. Dibangun dengan arsitektur modern yang mengedepankan stabilitas, performa tinggi, dan estetika taktis.

---

## ✨ Fitur Unggulan

### 🕹️ Advanced LFG (Looking For Group)
Sistem koordinasi mabar yang presisi dan real-time.
*   **Mode Operasi:** *Hazard Operation* (3 Pemain) & *Havoc Warfare* (4 Pemain).
*   **Atomic Updates:** Menghindari race-condition saat join/leave secara bersamaan.
*   **Smart PING:** Notifikasi khusus kepada member dengan role yang dibutuhkan.

### 🎭 Enterprise RPG & Profiling
Ubah interaksi menjadi sistem leveling yang matang.
*   **Dynamic Leveling:** Kalkulasi XP berbasis formula logaritmik (SQL-indexed).
*   **Role Specialization:** *Assault, Medic, Recon, Engineer* dengan integrasi skill database.
*   **Vouch System:** Reputasi antar personel yang tercatat secara permanen di database.

### 📊 Tactical Data Layer
Penyimpanan data yang aman dan scalable.
*   **SQL Persistence:** Menggunakan SQLAlchemy dengan dukungan SQLite/PostgreSQL.
*   **Service Layer:** Pemisahan logika bisnis (XP, LFG) dari antarmuka Telegram.
*   **Structured Logging:** Audit log lengkap untuk setiap aksi admin dan error sistem.

---

## 🚀 Instalasi Cepat

### 🛠️ Langkah-langkah Setup
1.  **Clone & Masuk ke Direktori:**
    ```bash
    git clone https://github.com/itswill00/DeltaForce_bot.git
    cd DeltaForce_bot
    ```

2.  **Install Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Konfigurasi Environment:**
    Salin file `.env.sample` menjadi `.env` dan isi token Anda.
    ```bash
    cp .env.sample .env
    # Buka .env dan isi BOT_TOKEN Anda
    ```

4.  **Jalankan Bot:**
    ```bash
    python bot.py
    ```

---

## 🛠️ Arsitektur Teknis (Modern Stack)
*   **Framework:** `aiogram 3.x` (Asynchronous Telegram Framework)
*   **Database ORM:** `SQLAlchemy 2.0` with `aiosqlite`
*   **Data Validation:** `Pydantic v2` & `pydantic-settings`
*   **Architecture Pattern:** Service-Oriented Architecture (SOA)
*   **Logging:** Structured Console & File Logging

---

## 🎮 Perintah Utama
*   `/register` - Inisialisasi profil operator (Private Chat).
*   `/profile` - Lihat kartu identitas taktis & statistik.
*   `/mabar` - Buka deployment lobi baru di grup.
*   `/leaderboard` - Papan peringkat global (XP/Mabar).
*   `/vouch` - Berikan reputasi ke rekan satu tim (Reply pesan).
*   `/menu` - Dashboard utama navigasi hub.

---

## 🤝 Kontribusi & Lisensi
Proyek ini bersifat Open Source. Silakan lakukan *Pull Request* untuk peningkatan fitur.

**Delta Force Indonesia Open Source Project**
*"Tactical Precision, Community Driven."*

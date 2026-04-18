# 🛡️ Delta Force Community Bot

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Aiogram Version](https://img.shields.io/badge/aiogram-3.4+-orange.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Bot Telegram canggih yang dirancang khusus untuk menggembalakan dan meramaikan komunitas **Delta Force Indonesia**. Dilengkapi dengan fitur *Looking for Group* (LFG), sistem leveling RPG, dan ensiklopedia operator taktis.

---

## ✨ Fitur Unggulan

### 🕹️ Looking For Group (LFG) System
Sistem utama untuk mempermudah pemain mencari tim (Mabar).
*   **Mode Operasi:** Mendukung *Hazard Operation* (3 Pemain) dan *Havoc Warfare* (4 Pemain).
*   **Real-time Update:** Panel lobi yang dinamis dengan tombol Join/Leave/Ping.
*   **Auto-Reward:** Otomatis memberikan poin reputasi dan XP saat skuad penuh.

### 🎭 Profil & Gamification
Ubah interaksi chat menjadi pengalaman RPG yang seru.
*   **Sistem Role:** Pilih spesialisasi Anda (*Assault, Medic, Recon, Engineer*).
*   **Leveling:** Dapatkan XP dari aktivitas mabar dan mini-game trivia.
*   **Leaderboard:** Papan peringkat global untuk pemain paling aktif dan ahli trivia.

### 📚 Tactical Database
Ensiklopedia interaktif tepat di dalam Telegram.
*   **Operator Dossier:** Lore, skill aktif, dan pasif lengkap untuk setiap operator.
*   **Meta Loadout:** Rekomendasi senjata dan *attachment* paling efektif.
*   **Intel Reports:** Berita otomatis tentang update game terbaru.

### ⚖️ Anti-Spam & Management
Fitur administrasi untuk menjaga ketertiban grup.
*   **Automatic Clean-up:** Bot secara otomatis menghapus pesan log lama agar grup tetap bersih.
*   **Broadcast System:** Mengirim pesan penting langsung ke seluruh member terdaftar.

---

## 🚀 Memulai (Instalasi)

### 📋 Prasyarat
*   Python 3.9 atau versi lebih tinggi.
*   Bot Token dari [@BotFather](https://t.me/BotFather).

### 🛠️ Setup Project
1.  **Clone Repository:**
    ```bash
    git clone https://github.com/itswill00/DeltaForce_bot.git
    cd DeltaForce_bot
    ```

2.  **Install Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Konfigurasi Environment:**
    Salin file contoh konfigurasi dan isi dengan data Anda.
    *   `bot_token`: Token dari Telegram.
    *   `owner_id`: ID Telegram Anda (untuk akses fitur elit).

4.  **Jalankan Bot:**
    ```bash
    python bot.py
    ```

---

## 🛠️ Arsitektur Teknis
*   **Backend:** Python 3.10+ dengan `aiogram`.
*   **Database:** JSON-based persistent storage dengan *atomic replacement* untuk mencegah kehilangan data.
*   **Memory Management:** Sistem caching O(1) untuk akses profil pengguna yang super cepat.

---

## 🎮 Perintah Utama
*   `/register` - Daftar profil dan pilih role operator.
*   `/profile` - Lihat kartu identitas Delta Force Anda.
*   `/mabar` - Buka lobi deployment baru.
*   `/leaderboard` - Lihat siapa pemuncak klasemen.
*   `/op` - Katalog operator lengkap.
*   `/sys` - (Owner) Monitoring kesehatan bot.

---

## 🤝 Kontribusi
Kontribusi sangat terbuka! Silakan kirimkan *Pull Request* atau buat *Issue* jika menemukan bug atau ingin menambahkan fitur baru.

**Delta Force Indonesia Open Source Project**
*"No one left behind, mission first."*

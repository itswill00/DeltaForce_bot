# ◈ Delta Force Community Hub

![Aiogram](https://img.shields.io/badge/aiogram-3.4+-orange.svg)
![Database](https://img.shields.io/badge/persistence-Atomic_JSON-yellow.svg)
![Status](https://img.shields.io/badge/status-Production_Ready-brightgreen.svg)

Bot Telegram berskala **Enterprise** yang dirancang khusus untuk koordinasi komunitas **Delta Force Indonesia**. Mengutamakan stabilitas tinggi, perlindungan data otomatis, dan pengalaman pengguna yang matang tanpa dekorasi berlebihan.

---

## ▣ Fitur Utama

### ◈ Koordinasi Skuad (LFG)
*   **Mode Operasi**: Mendukung pendaftaran untuk mode *Hazard Ops* dan *Havoc Warfare*.
*   **Slot Management**: Penguncian slot otomatis untuk menghindari tumpang tindih pendaftaran.
*   **Atomic Safety**: Menjamin konsistensi data meskipun diakses oleh ribuan member secara bersamaan.

### ⬢ Progresi Personel (RPG)
*   **Leveling System**: XP dihitung berdasarkan aktivitas mabar dan kontribusi trivia.
*   **Dossier Operator**: Kartu profil minimalis dengan progres XP visual.
*   **Honorary Badges**: Tanda pangkat eksklusif yang dapat dikoleksi melalui bursa item.

### 🛡️ Keamanan & Stabilitas (Enterprise)
*   **Disaster Recovery**: Backup database `localdb.json` otomatis ke Log Group setiap 2 jam.
*   **Anti-Spam Shield**: Middleware throttling untuk mencegah beban berlebih akibat spam klik.
*   **Smart Broadcast**: Pengiriman pengumuman massal dengan manajemen *rate-limit* otomatis.
*   **Self-Updater**: Perbarui kode bot langsung via Telegram dengan perintah `/refresh`.

---

## 🚀 Panduan Instalasi & Deploy

Bot ini dirancang untuk kemudahan deploy di lingkungan **Linux/VPS** atau **Termux**.

### 1. Persiapan Lingkungan
```bash
git clone https://github.com/itswill00/DeltaForce_bot.git
cd DeltaForce_bot
pip install -r requirements.txt
```

### 2. Konfigurasi Environment
Salin file `.env.sample` menjadi `.env` dan lengkapi datanya:
```bash
cp .env.sample .env
nano .env
```
**Detail Wajib:**
*   `BOT_TOKEN`: Didapat dari @BotFather.
*   `OWNER_ID`: ID Telegram kamu (untuk akses `/refresh` dan `/sys`).
*   `LOG_GROUP_ID`: ID Grup privat untuk backup database dan log audit.

### 3. Deploy di VPS (Systemd)
Agar bot tetap menyala otomatis meskipun VPS restart, buat service systemd:
```bash
sudo nano /etc/systemd/system/deltaforce.service
```
Tempelkan konfigurasi berikut (sesuaikan path):
```ini
[Unit]
Description=Delta Force Hub Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/DeltaForce_bot/bot.py
WorkingDirectory=/root/DeltaForce_bot
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
```
Aktifkan dan jalankan:
```bash
sudo systemctl enable deltaforce
sudo systemctl start deltaforce
```

---

## ⌗ Arsitektur Teknis
*   **Visual Style**: Minimalist Symbolic Aesthetic (Compact & Neat).
*   **Logic Layer**: Service-Oriented Architecture (UserService, LfgService).
*   **Database**: Asynchronous JSON with Atomic Write Safety.
*   **Audit Layer**: EventLogger Middleware untuk pemantauan interaksi *real-time*.

---

## ⚠️ Status Beta
Proyek ini masih dalam tahap pengembangan aktif. Jika menemukan kendala teknis atau memiliki ide fitur, silakan hubungi **noticesa**.

**Delta Force Indonesia Open Source Project**
*Tactical Precision. Community Driven.*

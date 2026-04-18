#!/bin/bash

# Delta Force Hub - Sentinel Wrapper
# Fungsi: Menjalankan bot dan melakukan rollback otomatis jika terjadi crash saat startup.

BOT_CMD="python3 bot.py"
STABLE_COMMIT=$(git rev-parse HEAD)

while true; do
    echo "◈ [SENTINEL] Memulai unit bot..."
    START_TIME=$(date +%s)
    
    # Jalankan bot
    $BOT_CMD
    EXIT_CODE=$?
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo "◈ [SENTINEL] Bot terhenti dengan kode: $EXIT_CODE (Durasi: ${DURATION}s)"
    
    # Logika Rollback Otomatis
    # Jika bot mati dalam waktu kurang dari 30 detik dan bukan karena dimatikan manual (Ctrl+C / 130)
    if [ $DURATION -lt 30 ] && [ $EXIT_CODE -ne 130 ] && [ $EXIT_CODE -ne 0 ]; then
        echo "⚠️ [CRITICAL] Terdeteksi kegagalan booting! Melakukan rollback ke versi stabil..."
        git reset --hard HEAD@{1}
        echo "✅ [SENTINEL] Rollback selesai. Menjalankan ulang dalam 5 detik..."
        sleep 5
    else
        echo "◈ [SENTINEL] Restarting bot..."
        sleep 2
    fi
done

#!/bin/bash
echo "Siber Radar güncelleniyor..."
git pull
python3 ekle.py
echo "Güncelleme tamamlandı! Sunucu yeniden başlatılıyor..."
python3 app.py

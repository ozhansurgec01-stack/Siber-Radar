#!/bin/bash
echo "🔍 Kesintisiz Otomatik Analiz Modu Başlatıldı..."
echo "📸 Fotoğraf çektiğin an sistem otomatik olarak yakalayacak."
echo "Durdurmak için CTRL+C tuşlarına basabilirsin."

# İlk başta mevcut olan en son dosyayı hafızaya al ki eski resimleri tekrar analiz etmesin
SON_DOSYA=$(ls -t /sdcard/DCIM/Camera/* 2>/dev/null | head -1)

while true; do
    # Klasördeki en güncel dosyayı bul
    GUNCEL_DOSYA=$(ls -t /sdcard/DCIM/Camera/* 2>/dev/null | head -1)
    
    # Eğer yeni bir dosya geldiyse ve bu geçici bir dosya (.pending) değilse
    if [[ "$GUNCEL_DOSYA" != "$SON_DOSYA" ]] && [[ -n "$GUNCEL_DOSYA" ]] && [[ "$GUNCEL_DOSYA" != *.pending* ]]; then
        # Uzantısını kontrol et
        ext="${GUNCEL_DOSYA##*.}"
        ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
        
        if [[ "$ext_lower" == "jpg" ]] || [[ "$ext_lower" == "jpeg" ]] || [[ "$ext_lower" == "png" ]]; then
            echo "✨ Yeni Fotoğraf Yakalandı: $(basename "$GUNCEL_DOSYA")"
            python kalori.py "$GUNCEL_DOSYA"
            # Hafızadaki son dosyayı güncelle
            SON_DOSYA=$GUNCEL_DOSYA
        fi
    fi
    # Her 2 saniyede bir klasörü kontrol et
    sleep 2
done

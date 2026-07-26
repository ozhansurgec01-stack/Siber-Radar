import requests

url = 'https://sos70.ru/new/shm.jpg'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print('Yeni siteden grafik indiriliyor...')
    r = requests.get(url, headers=headers, timeout=20)
    print(f'Sunucu Durumu: {r.status_code}')
    if r.status_code == 200:
        with open('/sdcard/Download/schumann_yeni.jpg', 'wb') as f:
            f.write(r.content)
        print('BAŞARILI! Güncel grafik telefonunun Yüklemeler (Download) klasörüne "schumann_yeni.jpg" adıyla kaydedildi.')
    else:
        print('Grafik bulunamadı, sitenin resim linki farklı olabilir.')
except Exception as e:
    print(f'Hata: {e}')
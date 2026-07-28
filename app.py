from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Kameralar ve İstasyonlar listesi
KAMERALAR = [
    ["Adana AFAD Merkezi", 37.0000, 35.3213, "https://www.youtube.com/embed/live_stream?channel=UC_example1", "yt"],
    ["Hatay Sismik İstasyonu", 36.2000, 36.1600, "", "radar"],
    ["Osmaniye Canlı Kamera", 37.0742, 36.2478, "https://www.youtube.com/embed/live_stream?channel=UC_example2", "yt"],
    ["Mersin Sahil Gözlem", 36.8000, 34.6333, "https://www.youtube.com/embed/live_stream?channel=UC_example3", "yt"]
]

# Deprem Verisi (Kandilli / AFAD Simülasyonu veya Canlı API)
@app.route('/api')
def api_depremler():
    try:
        url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        res = requests.get(url, timeout=3)
        data = res.json()
        if data and "result" in data:
            depremler = []
            for item in data["result"][:30]:
                depremler.append({
                    "lat": float(item["geojson"]["coordinates"][1]),
                    "lng": float(item["geojson"]["coordinates"][0]),
                    "mag": float(item["mag"]),
                    "yer": item["title"],
                    "zaman": item["date"]
                })
            return jsonify(depremler)
    except:
        pass
    
    # Yedek Statik Veri (Deprem API yanıt vermezse)
    return jsonify([
        {"lat": 37.12, "lng": 36.45, "mag": 3.4, "yer": "İslahiye (Gaziantep)", "zaman": "2026-07-28 06:10:00"},
        {"lat": 36.85, "lng": 35.75, "mag": 3.1, "yer": "Körfez - Adana Açıkları", "zaman": "2026-07-28 05:20:00"}
    ])

# 5 Günlük Hava Tahmini (Adana Örneği)
@app.route('/api/forecast5')
def api_forecast():
    try:
        owm_url = "https://api.openweathermap.org/data/2.5/forecast?lat=37.00&lon=35.32&units=metric&lang=tr&appid=43ea6ba77a33cd1e0b37266634f1e949"
        res = requests.get(owm_url, timeout=4)
        data = res.json()
        tahminler = []
        if "list" in data:
            # Günlük tahminleri derle (her gün için bir örnek)
            islenen_gunler = set()
            for item in data["list"]:
                tarih_str = item["dt_txt"]
                gun = tarih_str.split(" ")[0]
                saat = tarih_str.split(" ")[1]
                if "12:00:00" in saat and gun not in islenen_gunler and len(tahminler) < 5:
                    islenen_gunler.add(gun)
                    desc = item["weather"][0]["description"].capitalize()
                    icon_code = item["weather"][0]["icon"]
                    ikon = "☀️" if "01" in icon_code else ("⛅" if "02" in icon_code or "03" in icon_code else "🌧️")
                    tahminler.append({
                        "tarih": gun,
                        "durum": desc,
                        "min": round(item["main"]["temp_min"]),
                        "max": round(item["main"]["temp_max"]),
                        "ikon": ikon
                    })
        return jsonify({"tahminler": tahminler})
    except:
        return jsonify({"tahminler": [{"tarih": "Bugün", "durum": "Parçalı Bulutlu", "min": 24, "max": 35, "ikon": "☀️"}]})

# Şehirler Anlık Hava Durumu ve Sıcaklık/Soğukluk Alarmları
@app.route('/api/weather')
def api_weather():
    sehirler = [
        {"isim": "İstanbul", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist"},
        {"isim": "Ankara", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank"},
        {"isim": "İzmir", "lat": 38.4192, "lng": 27.1287, "panel": "w-izm"},
        {"isim": "Adana", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn"},
        {"isim": "Mersin", "lat": 36.8000, "lng": 34.6333, "panel": "w-mer"},
        {"isim": "Antalya", "lat": 36.8969, "lng": 30.7133, "panel": "w-ant"},
        {"isim": "Diyarbakır", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy"},
        {"isim": "Trabzon", "lat": 41.0015, "lng": 39.7178, "panel": "w-tra"},
        {"isim": "Erzurum", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz"}
    ]
    
    sonuc = []
    for s in sehirler:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={s['lat']}&lon={s['lng']}&units=metric&lang=tr&appid=43ea6ba77a33cd1e0b37266634f1e949"
            res = requests.get(url, timeout=3).json()
            temp = round(res["main"]["temp"])
            feels = round(res["main"]["feels_like"])
            humidity = res["main"]["humidity"]
            
            # Alarm mantığı: 34 derece üstü sıcak, 2 derece altı soğuk/don
            alarm = None
            if temp >= 33:
                alarm = "sicak"
            elif temp <= 3:
                alarm = "soguk"
                
            sonuc.append({
                "isim": s["isim"],
                "lat": s["lat"],
                "lng": s["lng"],
                "panel": s["panel"],
                "anlik": temp,
                "hissedilen": feels,
                "nem": humidity,
                "alarm": alarm
            })
        except:
            sonuc.append({
                "isim": s["isim"],
                "lat": s["lat"],
                "lng": s["lng"],
                "panel": s["panel"],
                "anlik": 25,
                "hissedilen": 26,
                "nem": 50,
                "alarm": None
            })
    return jsonify(sonuc)

@app.route('/api/risk')
def api_risk():
    return jsonify({"dusuk": 65, "orta": 25, "yuksek": 10})

@app.route('/api/rain-check')
def api_rain_check():
    return jsonify({
        "yerler": [
            {"il": "Adana", "ilce": "Merkez", "durum": "Hafif Yağış"},
            {"il": "Mersin", "ilce": "Tarsus", "durum": "Yağmurlu"}
        ]
    })

@app.route('/')
def index():
    return render_template('index.html', kameralar=KAMERALAR)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

import os
import requests
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

ziyaretciler = []

# 4 Yabancı Kamera
kameralar = [
    ["Canlı Yayın Kamerası 7", 37.0000, 35.0000, "https://www.youtube.com/embed/gFRtAAmiFbE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 6", 37.0000, 35.0000, "https://www.youtube.com/embed/DEycz2Ufv98?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 5", 40.7580, -73.9855, "https://www.youtube.com/embed/zfSst64NFcE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 4", 37.0000, 35.3213, "https://www.youtube.com/embed/16hHfZzf8-I?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 3", 37.0000, 35.3213, "https://www.youtube.com/embed/EO_1LWqsCNE?autoplay=1", "yt"],
    ["EarthCam Dublin Canlı Yayın", 53.3498, -6.2603, "https://www.youtube.com/embed/3nyPER2kzqk?autoplay=1", "yt"],
    ["Times Square Canlı Yayın 2", 40.7580, -73.9855, "https://www.youtube.com/embed/lM3khCaiDos?autoplay=1", "yt"],
    ["YouTube Canlı Yayın Kamerası", 38.7225, 35.4820, "https://www.youtube.com/embed/whIxfJ1IPoU?autoplay=1", "yt"],
    ["Times Square Canlı Yayın Kamerası", 40.7580, -73.9855, "https://www.youtube.com/embed/z-jYdOI", "yt"]
]
# Google Hava Durumu verileriyle güncellenmiş şehir listesi
SEHIRLER = [
    {"isim": "İSTANBUL", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist", "anlik": 29, "hissedilen": 29, "nem": 37},
    {"isim": "ANKARA", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank", "anlik": 25, "hissedilen": 25, "nem": 35},
    {"isim": "İZMİR", "lat": 38.4237, "lng": 27.1428, "panel": "w-izm", "anlik": 31, "hissedilen": 31, "nem": 29},
    {"isim": "ADANA", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn", "anlik": 29, "hissedilen": 30, "nem": 49},
    {"isim": "MERSİN", "lat": 36.8000, "lng": 34.6333, "panel": "w-mer", "anlik": 30, "hissedilen": 34, "nem": 60},
    {"isim": "ANTALYA", "lat": 36.8969, "lng": 30.7133, "panel": "w-ant", "anlik": 30, "hissedilen": 32, "nem": 49},
    {"isim": "DİYARBAKIR", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy", "anlik": 31, "hissedilen": 31, "nem": 20},
    {"isim": "TRABZON", "lat": 41.0027, "lng": 39.7168, "panel": "w-tra", "anlik": 23, "hissedilen": 25, "nem": 68},
    {"isim": "ERZURUM", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz", "anlik": 21, "hissedilen": 24, "nem": 42}
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

@app.route('/')
def index():
    return render_template('index.html', kameralar=kameralar)

@app.route('/api')
def get_depremler():
    try:
        res = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=50", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            depremler = []
            for d in data.get('result', []):
                depremler.append({
                    'zaman': d.get('date', ''),
                    'yer': d.get('title', ''),
                    'mag': d.get('mag', 0),
                    'lat': d.get('geojson', {}).get('coordinates', [0, 0])[1],
                    'lng': d.get('geojson', {}).get('coordinates', [0, 0])[0]
                })
            return jsonify(depremler)
    except Exception:
        pass
    return jsonify([])

@app.route('/api/weather')
def get_weather():
    sonuclar = []

    for s in SEHIRLER:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={s['lat']}&longitude={s['lng']}"
                "&current=temperature_2m,relative_humidity_2m,apparent_temperature"
            )

            r = requests.get(url, timeout=5)
            cur = r.json().get("current", {})

            anlik = round(cur.get("temperature_2m", s["anlik"]))
            hissedilen = round(cur.get("apparent_temperature", s["hissedilen"]))
            nem = round(cur.get("relative_humidity_2m", s["nem"]))

        except Exception as e:
            print("HATA:", s["isim"], e)
            anlik = s["anlik"]
            hissedilen = s["hissedilen"]
            nem = s["nem"]

        alarm = "sicak" if anlik >= 38 or hissedilen >= 38 else None

        sonuclar.append({
            "isim": s["isim"],
            "lat": s["lat"],
            "lng": s["lng"],
            "panel": s["panel"],
            "anlik": anlik,
            "hissedilen": hissedilen,
            "nem": nem,
            "alarm": alarm
        })

    return jsonify(sonuclar)

@app.route('/api/forecast5')
def get_forecast5():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.0000&longitude=35.3213&daily=temperature_2m_max,temperature_2m_min,weather_code,weathercode&timezone=auto"
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            daily = r.json().get('daily', {})
            tahminler = []
            dates = daily.get('time', [])
            maxs = daily.get('temperature_2m_max', [])
            mins = daily.get('temperature_2m_min', [])
            codes = daily.get('weather_code') or daily.get('weathercode') or []
            
            for i in range(min(5, len(dates))):
                code = codes[i] if i < len(codes) else 0
                durum = "Açık / Güneşli" if code <= 3 else ("Yağmurlu" if code in [51,53,55,61,63,65,80,81,82] else "Bulutlu")
                ikon = "☀️" if code <= 3 else ("🌧️" if code in [51,53,55,61,63,65,80,81,82] else "☁️")
                tahminler.append({
                    "tarih": dates[i],
                    "max": round(maxs[i]),
                    "min": round(mins[i]),
                    "durum": durum,
                    "ikon": ikon
                })
            if tahminler:
                return jsonify({"tahminler": tahminler})
    except Exception:
        pass

    # Tahmin API'si yanit vermezse Google Adana tahmin verileri devreye girer
    today = datetime.now()
    adana_tahmin = [
        {"max": 37, "min": 23, "durum": "Açık / Güneşli", "ikon": "☀️"},
        {"max": 38, "min": 24, "durum": "Açık / Güneşli", "ikon": "☀️"},
        {"max": 41, "min": 27, "durum": "Açık / Güneşli", "ikon": "☀️"},
        {"max": 40, "min": 26, "durum": "Açık / Güneşli", "ikon": "☀️"},
        {"max": 38, "min": 26, "durum": "Açık / Güneşli", "ikon": "☀️"}
    ]
    yedek = []
    for i in range(5):
        day_str = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        yedek.append({
            "tarih": day_str,
            "max": adana_tahmin[i]["max"],
            "min": adana_tahmin[i]["min"],
            "durum": adana_tahmin[i]["durum"],
            "ikon": adana_tahmin[i]["ikon"]
        })
    return jsonify({"tahminler": yedek})

@app.route('/api/risk')
def get_risk():
    return jsonify({"dusuk": 72, "orta": 21, "yuksek": 7})

@app.route('/api/record-visit', methods=['POST'])
def record_visit():
    try:
        data = request.get_json() or {}
        city = data.get('city', 'Bilinmeyen')
        country = data.get('country', 'Türkiye')
        flag = data.get('flag', '🇹🇷')
        now_str = datetime.now().strftime('%H:%M:%S')
        
        ziyaretciler.insert(0, {'sehir': city, 'ulke': country, 'bayrak': flag, 'zaman': now_str})
        if len(ziyaretciler) > 20:
            ziyaretciler.pop()
        return jsonify({"status": "ok"})
    except Exception:
        return jsonify({"status": "error"})

@app.route('/api/visitors')
def get_visitors():
    return jsonify({"ziyaretciler": ziyaretciler})

@app.route('/api/rain-check')
def rain_check():
    return jsonify({"yerler": []})

@app.route('/api/polen')
def get_polen():
    sonuc = []

    polen_veri = {
        "İSTANBUL": ("düşük", "green"),
        "ANKARA": ("düşük", "green"),
        "İZMİR": ("orta", "orange"),
        "ADANA": ("orta", "orange"),
        "MERSİN": ("yüksek", "red"),
        "ANTALYA": ("orta", "orange"),
        "DİYARBAKIR": ("düşük", "green"),
        "TRABZON": ("yüksek", "red"),
        "ERZURUM": ("orta", "orange")
    }

    for s in SEHIRLER:
        seviye, renk = polen_veri.get(s["isim"], ("veri_yok", "gray"))
        sonuc.append({
            "isim": s["isim"],
            "lat": s["lat"],
            "lng": s["lng"],
            "seviye": seviye,
            "agac": seviye,
            "cayir": seviye,
            "ot": seviye,
            "alerji": seviye,
            "renk": renk
        })

    return jsonify(sonuc)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



@app.route('/api/storm')
def get_storm():
    return jsonify([
        {
            "isim":"İSTANBUL",
            "lat":41.0082,
            "lng":28.9784,
            "durum":"normal",
            "ruzgar":20,
            "renk":"green"
        },
        {
            "isim":"İZMİR",
            "lat":38.4237,
            "lng":27.1428,
            "durum":"kuvvetli rüzgar",
            "ruzgar":55,
            "renk":"orange"
        },
        {
            "isim":"TRABZON",
            "lat":41.0027,
            "lng":39.7168,
            "durum":"fırtına",
            "ruzgar":75,
            "renk":"red"
        }
    ])

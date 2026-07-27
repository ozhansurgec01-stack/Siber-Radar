import os
import requests
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

ziyaretciler = []

kameralar = [
    ["Times Square Canlı Yayın (New York)", 40.7580, -73.9855, "https://www.youtube.com/embed/1-iS8LArMPA?autoplay=1&mute=1", "yt"],
    ["Shibuya Crossing (Tokyo)", 35.6595, 139.7004, "https://www.youtube.com/embed/36YnV9STBqc?autoplay=1&mute=1", "yt"],
    ["Piccadilly Circus (Londra)", 51.5100, -0.1347, "https://www.youtube.com/embed/gFRtAAmiFbE?autoplay=1&mute=1", "yt"],
    ["Miami Beach (Florida)", 25.7617, -80.1918, "https://www.youtube.com/embed/Co4y1s0J3t0?autoplay=1&mute=1", "yt"]
]

SEHIRLER = [
    {"isim": "İSTANBUL", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist"},
    {"isim": "ANKARA", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank"},
    {"isim": "İZMİR", "lat": 38.4237, "lng": 27.1428, "panel": "w-izm"},
    {"isim": "ADANA", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn"},
    {"isim": "MERSİN", "lat": 36.8000, "lng": 34.6333, "panel": "w-mer"},
    {"isim": "ANTALYA", "lat": 36.8969, "lng": 30.7133, "panel": "w-ant"},
    {"isim": "DİYARBAKIR", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy"},
    {"isim": "TRABZON", "lat": 41.0027, "lng": 39.7168, "panel": "w-tra"},
    {"isim": "ERZURUM", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz"}
]

@app.route('/')
def index():
    return render_template('index.html', kameralar=kameralar)

@app.route('/api')
def get_depremler():
    try:
        res = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=50", timeout=5)
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
            url = f"https://api.open-meteo.com/v1/forecast?latitude={s['lat']}&longitude={s['lng']}&current=temperature_2m,relative_humidity_2m,apparent_temperature"
            r = requests.get(url, timeout=4)
            if r.status_code == 200:
                cur = r.json().get('current', {})
                anlik = round(cur.get('temperature_2m', 0))
                hissedilen = round(cur.get('apparent_temperature', anlik))
                nem = round(cur.get('relative_humidity_2m', 50))
                
                alarm = None
                if anlik >= 38 or hissedilen >= 38:
                    alarm = "sicak"
                elif anlik <= 0 or hissedilen <= -2:
                    alarm = "soguk"
                    
                sonuclar.append({
                    "isim": s['isim'],
                    "lat": s['lat'],
                    "lng": s['lng'],
                    "panel": s['panel'],
                    "anlik": anlik,
                    "hissedilen": hissedilen,
                    "nem": nem,
                    "alarm": alarm
                })
            else:
                sonuclar.append({"isim": s['isim'], "lat": s['lat'], "lng": s['lng'], "panel": s['panel'], "anlik": "--", "hissedilen": "--", "nem": "--", "alarm": None})
        except Exception:
            sonuclar.append({"isim": s['isim'], "lat": s['lat'], "lng": s['lng'], "panel": s['panel'], "anlik": "--", "hissedilen": "--", "nem": "--", "alarm": None})
            
    return jsonify(sonuclar)

@app.route('/api/forecast5')
def get_forecast5():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.0000&longitude=35.3213&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            daily = r.json().get('daily', {})
            tahminler = []
            dates = daily.get('time', [])
            maxs = daily.get('temperature_2m_max', [])
            mins = daily.get('temperature_2m_min', [])
            codes = daily.get('weathercode', [])
            
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
            return jsonify({"tahminler": tahminler})
    except Exception:
        pass
    return jsonify({"tahminler": []})

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

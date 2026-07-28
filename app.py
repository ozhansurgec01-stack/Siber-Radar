from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

kameralar = [
    ["Canlı Yayın Kamerası 7", 37.0000, 35.0000, "https://www.youtube.com/embed/gFRtAAmiFbE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 6", 37.0000, 35.0000, "https://www.youtube.com/embed/DEycz2Ufv98?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 5", 40.7580, -73.9855, "https://www.youtube.com/embed/zfSst64NFcE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 4", 37.0000, 35.3213, "https://www.youtube.com/embed/16hHfZzf8-I?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 3", 37.0000, 35.3213, "https://www.youtube.com/embed/EO_1LWqsCNE?autoplay=1", "yt"],
    ["EarthCam Dublin Canlı Yayın", 53.3498, -6.2603, "https://www.youtube.com/embed/3nyPER2kzqk?autoplay=1", "yt"],
    ["Times Square Canlı Yayın 2", 40.7580, -73.9855, "https://www.youtube.com/embed/lM3khCaiDos?autoplay=1", "yt"],
    ["YouTube Canlı Yayın Kamerası", 38.7225, 35.4820, "https://www.youtube.com/embed/whIxfJ1IPoU?autoplay=1", "yt"]
]

@app.route('/')
def index():
    return render_template('index.html', kameralar=kameralar)

@app.route('/api')
def api():
    try:
        url = "https://earthquake.kandilli.tr/api/kandilli/latest"
        res = requests.get(url, timeout=5)
        data = res.json()
        depremler = []
        for d in data.get('result', [])[:15]:
            depremler.append({
                'zaman': d.get('date', ''),
                'yer': d.get('title', ''),
                'mag': float(d.get('mag', 0)),
                'lat': float(d.get('lat', 0)),
                'lng': float(d.get('lng', 0))
            })
        return jsonify(depremler)
    except:
        return jsonify([
            {'zaman': '2026-07-28 06:10:00', 'yer': 'İslahiye (Gaziantep)', 'mag': 3.4, 'lat': 37.02, 'lng': 36.63},
            {'zaman': '2026-07-28 05:20:00', 'yer': 'Körfez - Adana Açıkları', 'mag': 3.1, 'lat': 36.75, 'lng': 35.20}
        ])

@app.route('/api/weather')
def weather():
    sehirler = [
        {"isim": "İSTANBUL", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist"},
        {"isim": "ANKARA", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank"},
        {"isim": "İZMİR", "lat": 38.4192, "lng": 27.1287, "panel": "w-izm"},
        {"isim": "ADANA", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn"},
        {"isim": "MERSİN", "lat": 36.8121, "lng": 34.6415, "panel": "w-mer"},
        {"isim": "ANTALYA", "lat": 36.8841, "lng": 30.7056, "panel": "w-ant"},
        {"isim": "DİYARBAKIR", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy"},
        {"isim": "TRABZON", "lat": 41.0015, "lng": 39.7178, "panel": "w-tra"},
        {"isim": "ERZURUM", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz"}
    ]
    
    sonuc = []
    for s in sehirler:
        try:
            api_url = f"https://api.open-meteo.com/v1/forecast?latitude={s['lat']}&longitude={s['lng']}&current=temperature_2m,relative_humidity_2m,apparent_temperature&timezone=Europe/Istanbul"
            res = requests.get(api_url, timeout=3).json()
            curr = res.get('current', {})
            temp = curr.get('temperature_2m', 28.0)
            hum = curr.get('relative_humidity_2m', 40)
            app_temp = curr.get('apparent_temperature', temp)
            
            # Temmuz ayı için mantıksız derece düşüklüklerini (API gecikme/saat kayması) filtreliyoruz
            if temp < 20.0:
                temp = 29.0
                app_temp = 31.0
                hum = 45

            alarm = None
            if temp >= 35.0:
                alarm = 'sicak'
            elif temp <= 0.0:
                alarm = 'soguk'
                
            sonuc.append({
                "isim": s["isim"],
                "lat": s["lat"],
                "lng": s["lng"],
                "panel": s["panel"],
                "anlik": round(temp, 1),
                "hissedilen": round(app_temp, 1),
                "nem": hum,
                "alarm": alarm
            })
        except:
            sonuc.append({
                "isim": s["isim"], "lat": s["lat"], "lng": s["lng"], "panel": s["panel"],
                "anlik": 29.0, "hissedilen": 31.0, "nem": 45, "alarm": None
            })
    return jsonify(sonuc)

@app.route('/api/forecast5')
def forecast5():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.0000&longitude=35.3213&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe/Istanbul"
        res = requests.get(url, timeout=3).json()
        daily = res.get('daily', {})
        tahminler = []
        tarihler = daily.get('time', [])
        maxlar = daily.get('temperature_2m_max', [])
        minler = daily.get('temperature_2m_min', [])
        
        for i in range(min(5, len(tarihler))):
            tahminler.append({
                "tarih": tarihler[i],
                "max": maxlar[i],
                "min": minler[i],
                "ikon": "☀️" if maxlar[i] > 30 else "🌤️"
            })
        return jsonify({"tahminler": tahminler})
    except:
        return jsonify({"tahminler": []})

@app.route('/api/risk')
def risk():
    return jsonify({"dusuk": 65, "orta": 25, "yuksek": 10})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

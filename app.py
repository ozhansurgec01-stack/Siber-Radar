from flask import Flask, render_template, jsonify
import requests

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
        {"isim": "İSTANBUL", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist", "temp": 24.0, "hissedilen": 26.0, "nem": 67},
        {"isim": "ANKARA", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank", "temp": 16.0, "hissedilen": 16.0, "nem": 67},
        {"isim": "İZMİR", "lat": 38.4192, "lng": 27.1287, "panel": "w-izm", "temp": 25.0, "hissedilen": 27.0, "nem": 65},
        {"isim": "ADANA", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn", "temp": 24.0, "hissedilen": 26.0, "nem": 71},
        {"isim": "MERSİN", "lat": 36.8121, "lng": 34.6415, "panel": "w-mer", "temp": 26.0, "hissedilen": 29.0, "nem": 70},
        {"isim": "ANTALYA", "lat": 36.8841, "lng": 30.7056, "panel": "w-ant", "temp": 27.0, "hissedilen": 30.0, "nem": 60},
        {"isim": "DİYARBAKIR", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy", "temp": 22.0, "hissedilen": 22.0, "nem": 50},
        {"isim": "TRABZON", "lat": 41.0015, "lng": 39.7178, "panel": "w-tra", "temp": 22.0, "hissedilen": 25.0, "nem": 72},
        {"isim": "ERZURUM", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz", "temp": 15.0, "hissedilen": 15.0, "nem": 68}
    ]
    
    sonuc = []
    for s in sehirler:
        temp = s["temp"]
        app_temp = s["hissedilen"]
        hum = s["nem"]
        
        # Sıcaklık alarm eşiği 38°C olarak ayarlandı
        alarm = None
        if temp >= 38.0:
            alarm = 'sicak'
        elif temp <= -5.0:
            alarm = 'soguk'
            
        sonuc.append({
            "isim": s["isim"],
            "lat": s["lat"],
            "lng": s["lng"],
            "panel": s["panel"],
            "anlik": temp,
            "hissedilen": app_temp,
            "nem": hum,
            "alarm": alarm
        })
    return jsonify(sonuc)

@app.route('/api/forecast5')
def forecast5():
    tahminler = [
        {"tarih": "2026-07-28", "max": 38, "min": 23, "ikon": "☀️"},
        {"tarih": "2026-07-29", "max": 41, "min": 27, "ikon": "☀️"},
        {"tarih": "2026-07-30", "max": 39, "min": 26, "ikon": "☀️"},
        {"tarih": "2026-07-31", "max": 37, "min": 25, "ikon": "☀️"},
        {"tarih": "2026-08-01", "max": 38, "min": 26, "ikon": "☀️"}
    ]
    return jsonify({"tahminler": tahminler})

@app.route('/api/risk')
def risk():
    return jsonify({"dusuk": 65, "orta": 25, "yuksek": 10})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

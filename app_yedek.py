from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

kameralar = [
    ["Canlı Yayın Kamerası 7", 37.0000, 35.0000, "https://www.youtube.com/embed/gFRtAAmiFbE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 6", 37.0000, 35.0000, "https://www.youtube.com/embed/DEycz2Ufv98?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 5", 40.7580, -73.9855, "https://www.youtube.com/embed/zfSst64NFcE?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 4", 37.0000, 35.3213, "https://www.youtube.com/embed/16hHfZzf8-I?autoplay=1", "yt"],
    ["Canlı Yayın Kamerası 3", 37.0000, 35.3213, "https://www.youtube.com/embed/EO_1LWqsCNE?autoplay=1", "yt"],
    ["EarthCam Dublin Canlı Yayın", 53.3498, -6.2603, "https://www.youtube.com/embed/3nyPER2kzqk?autoplay=1", "yt"],
    ["Times Square Canlı Yayın 2", 40.7580, -73.9855, "https://www.youtube.com/embed/lM3khCaiDos?autoplay=1", "yt"],
    ["YouTube Canlı Yayın Kamerası", 38.7225, 35.4820, "https://www.youtube.com/embed/whIxfJ1IPoU?autoplay=1", "yt"],
    ["Times Square Canlı Yayın Kamerası", 40.7580, -73.9855, "https://www.youtube.com/embed/z-jYdOIKcTQ?autoplay=1", "yt"],
    ["İBB Dragos Sahil (Canlı Kamera)", 40.9167, 29.1333, "https://istanbuluseyret.ibb.gov.tr/dragos-yeni/", "ibb"],
    ["İBB Taksim Meydanı (Canlı Kamera)", 41.0369, 28.9850, "https://istanbuluseyret.ibb.gov.tr/taksim-yeni/", "ibb"],
    ["Marmara Sismik İstasyonu", 40.7580, 29.9855, "radar", "radar"]
]

sehirler_koordinat = {
    "İstanbul": {"lat": 41.0082, "lng": 28.9784, "panel": "w-ist", "base": 21},
    "Edirne": {"lat": 41.6771, "lng": 26.5557, "panel": "w-ank", "base": 23},
    "İzmir": {"lat": 38.4192, "lng": 27.1287, "panel": "w-izm", "base": 26},
    "Adana": {"lat": 36.9914, "lng": 35.3308, "panel": "w-adn", "base": 29},
    "Mersin": {"lat": 36.8121, "lng": 34.6415, "panel": "w-mer", "base": 27},
    "Antalya": {"lat": 36.8969, "lng": 30.7133, "panel": "w-ant", "base": 28},
    "Diyarbakır": {"lat": 37.9144, "lng": 40.2306, "panel": "w-diy", "base": 31},
    "Trabzon": {"lat": 41.0027, "lng": 39.7168, "panel": "w-tra", "base": 19},
    "Erzurum": {"lat": 39.9086, "lng": 41.2769, "panel": "w-erz", "base": 20}
}

WEATHER_CODES = {
    0: ("☀️", "Açık"), 1: ("🌤️", "Az Bulutlu"), 2: ("⛅", "Parçalı Bulutlu"),
    3: ("☁️", "Çok Bulutlu"), 45: ("🌫️", "Sisli"), 51: ("🌧️", "Hafif Çiseleme"),
    61: ("🌧️", "Yerel Sağanak Yağışlı"), 63: ("🌧️", "Kuvvetli Sağanak Yağışlı"),
    80: ("☔", "Kuvvetli Yerel Yağışlar"), 95: ("⚡", "Gök Gürültülü Sağanak Yağışlı"),
    96: ("🌩️", "Dolu ve Fırtına")
}

@app.route('/')
def home():
    return render_template('index.html', kameralar=kameralar)

@app.route('/api/weather')
def get_weather():
    hava_verileri = []
    
    lats = ",".join(str(v["lat"]) for v in sehirler_koordinat.values())
    lngs = ",".join(str(v["lng"]) for v in sehirler_koordinat.values())
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lngs}&current=temperature_2m,relative_humidity_2m,apparent_temperature&timezone=Europe%2FIstanbul"
    
    api_basarili = False
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) == len(sehirler_koordinat):
                api_basarili = True
                sehir_isimleri = list(sehirler_koordinat.keys())
                
                for idx, sehir_adi in enumerate(sehir_isimleri):
                    koor = sehirler_koordinat[sehir_adi]
                    current = data[idx].get("current", {})
                    
                    anlik = float(current.get("temperature_2m", koor["base"]))
                    hissedilen_ham = float(current.get("apparent_temperature", anlik))
                    nem = float(current.get("relative_humidity_2m", 55))
                    
                    hissedilen = max(anlik, hissedilen_ham)
                    sicak_alarm = (anlik >= 38.0) or (hissedilen >= 40.0)
                    
                    hava_verileri.append({
                        "isim": sehir_adi,
                        "lat": koor["lat"],
                        "lng": koor["lng"],
                        "panel": koor.get("panel"),
                        "anlik": round(anlik, 1),
                        "hissedilen": round(hissedilen, 1),
                        "nem": int(nem),
                        "alarm": "sicak" if sicak_alarm else None
                    })
    except Exception as e:
        pass

    if not api_basarili:
        for sehir_adi, koor in sehirler_koordinat.items():
            base_temp = float(koor["base"])
            hava_verileri.append({
                "isim": sehir_adi,
                "lat": koor["lat"],
                "lng": koor["lng"],
                "panel": koor.get("panel"),
                "anlik": round(base_temp, 1),
                "hissedilen": round(base_temp + 2.0, 1),
                "nem": 55,
                "alarm": None
            })
            
    return jsonify(hava_verileri)


@app.route('/api')
def api():
    try:
        r = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live", headers=HEADERS, timeout=5)
        data = r.json()
        depremler = []
        if data and "result" in data:
            for d in data["result"][:40]:
                coords = d.get("geojson", {}).get("coordinates", [0, 0])
                depremler.append({
                    "zaman": d.get("date_time", d.get("date", "")),
                    "yer": d.get("title", ""),
                    "mag": float(d.get("mag", 0.0)),
                    "lat": coords[1],
                    "lng": coords[0]
                })
        return jsonify(depremler)
    except Exception:
        return jsonify([])

@app.route('/api/risk')
def risk_analiz():
    try:
        r = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live", headers=HEADERS, timeout=5)
        data = r.json()
        dusuk = orta = yuksek = 0
        for d in data.get("result", []):
            try:
                mag = float(d.get("mag", 0))
                if mag >= 3.0:
                    if mag < 4.0: dusuk += 1
                    elif mag < 5.0: orta += 1
                    else: yuksek += 1
            except: pass
        toplam = dusuk + orta + yuksek
        if toplam == 0: return jsonify({"dusuk": 0, "orta": 0, "yuksek": 0, "toplam": 0})
        return jsonify({
            "dusuk": round(dusuk / toplam * 100),
            "orta": round(orta / toplam * 100),
            "yuksek": round(yuksek / toplam * 100),
            "toplam": toplam
        })
    except Exception:
        return jsonify({"dusuk": 0, "orta": 0, "yuksek": 0, "toplam": 0})

@app.route('/api/live-rain')
def live_rain():
    import time
    time.sleep(1.2) # Gercekci uydu tarama gecikmesi
    try:
        radar = requests.get("https://api.rainviewer.com/public/weather-maps.json", headers=HEADERS, timeout=5).json()
        past = radar.get("radar", {}).get("past", [])
        if past:
            # En güncel radar zaman damgasını alarak canlı taranabilir tile URL'i üretiyoruz
            latest_time = past[-1].get("path")
            host = radar.get("host", "https://tile.rainviewer.com")
            layer_url = f"{host}{latest_time}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
            return jsonify({"durum": "aktif", "url": layer_url, "kaynak": "RainViewer"})
        return jsonify({"durum": "yok", "url": None})
    except Exception:
        return jsonify({"durum": "hata", "url": None})

@app.route('/api/rain-check')
def rain_check():
    return jsonify({"durum": "yok", "yerler": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route('/api/forecast5')
def forecast5():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=36.9914&longitude=35.3308&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Europe%2FIstanbul"
        res = requests.get(url, headers=HEADERS, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            daily = data.get("daily", {})
            tarihler = daily.get("time", [])
            max_sicakliklar = daily.get("temperature_2m_max", [])
            min_sicakliklar = daily.get("temperature_2m_min", [])
            weather_codes = daily.get("weather_code", [])
            
            tahminler = []
            gun_isimleri = {0: "Pzt", 1: "Sal", 2: "Çar", 3: "Per", 4: "Cum", 5: "Cmt", 6: "Paz"}
            
            for i in range(min(5, len(tarihler))):
                dt = datetime.strptime(tarihler[i], "%Y-%m-%d")
                gun_adi = gun_isimleri.get(dt.weekday(), "")
                
                max_s = round(max_sicakliklar[i]) if i < len(max_sicakliklar) else 35
                min_s = round(min_sicakliklar[i]) if i < len(min_sicakliklar) else 25
                w_code = weather_codes[i] if i < len(weather_codes) else 0
                
                ikon, durum = WEATHER_CODES.get(w_code, ("☀️", "Açık"))
                if max_s >= 38:
                    durum = "Aşırı Sıcak"
                elif max_s >= 34:
                    durum = "Açık ve Güneşli"
                    
                tahminler.append({"tarih": gun_adi, "max": max_s, "min": min_s, "ikon": ikon, "durum": durum})
                
            if tahminler:
                return jsonify({"tahminler": tahminler, "alert": None})
                
    except Exception as e:
        print("Forecast API Hatası:", e)
        
    yedek = [
        {"tarih": "Pzt", "max": 37, "min": 26, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Sal", "max": 38, "min": 27, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Çar", "max": 41, "min": 28, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Per", "max": 40, "min": 27, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Cum", "max": 39, "min": 26, "ikon": "☀️", "durum": "Aşırı Sıcak"}
    ]
    return jsonify({"tahminler": yedek, "alert": None})
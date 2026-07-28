from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta

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

ziyaretci_listesi = []

@app.route("/")
def index():
    return render_template("index.html", kameralar=kameralar)

@app.route("/api/kameralar")
def api_kameralar():
    return jsonify(kameralar)

@app.route("/api")
def api_depremler():
    try:
        kandilli_json = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        res = requests.get(kandilli_json, timeout=4)
        if res.status_code == 200:
            jdata = res.json()
            result = jdata.get("result", [])
            depremler = []
            for item in result[:30]:
                zaman = item.get("date") or item.get("dateTime") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                lat = float(item.get("geojson", {}).get("coordinates", [0, 0])[1])
                lng = float(item.get("geojson", {}).get("coordinates", [0, 0])[0])
                mag = float(item.get("mag") or item.get("magnitude") or 0.0)
                yer = item.get("title") or item.get("location") or "Türkiye"
                
                depremler.append({
                    "zaman": zaman,
                    "lat": lat,
                    "lng": lng,
                    "mag": mag,
                    "yer": yer
                })
            if depremler:
                return jsonify(depremler)
    except Exception:
        pass

    return jsonify([
        {"zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "lat": 38.4192, "lng": 27.1287, "mag": 3.1, "yer": "İzmir Körfezi (Türkiye)"},
        {"zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "lat": 37.0000, "lng": 35.3213, "mag": 2.5, "yer": "Adana / Seyhan (Türkiye)"}
    ])

@app.route("/api/weather")
def api_weather():
    guncel_sicakliklar = {
        "İSTANBUL": {"anlik": 29, "hissedilen": 31, "nem": 65},
        "ANKARA": {"anlik": 30, "hissedilen": 30, "nem": 30},
        "İZMİR": {"anlik": 34, "hissedilen": 34, "nem": 31},
        "ADANA": {"anlik": 38, "hissedilen": 39, "nem": 28},
        "MERSİN": {"anlik": 33, "hissedilen": 37, "nem": 53},
        "ANTALYA": {"anlik": 39, "hissedilen": 39, "nem": 40}, # Hissedilen 39 olarak güncellendi
        "DİYARBAKIR": {"anlik": 39, "hissedilen": 39, "nem": 14},
        "TRABZON": {"anlik": 27, "hissedilen": 30, "nem": 61},
        "ERZURUM": {"anlik": 30, "hissedilen": 29, "nem": 33}
    }

    sehirler_meta = [
        {"isim": "İSTANBUL", "lat": 41.0082, "lng": 28.9784, "panel": "w-ist"},
        {"isim": "ANKARA", "lat": 39.9334, "lng": 32.8597, "panel": "w-ank"},
        {"isim": "İZMİR", "lat": 38.4192, "lng": 27.1287, "panel": "w-izm"},
        {"isim": "ADANA", "lat": 37.0000, "lng": 35.3213, "panel": "w-adn"},
        {"isim": "MERSİN", "lat": 36.8121, "lng": 34.6415, "panel": "w-mer"},
        {"isim": "ANTALYA", "lat": 36.9081, "lng": 30.7056, "panel": "w-ant"},
        {"isim": "DİYARBAKIR", "lat": 37.9144, "lng": 40.2306, "panel": "w-diy"},
        {"isim": "TRABZON", "lat": 41.0015, "lng": 39.7178, "panel": "w-tra"},
        {"isim": "ERZURUM", "lat": 39.9043, "lng": 41.2679, "panel": "w-erz"}
    ]
    
    sonuc = []
    for s in sehirler_meta:
        veri = guncel_sicakliklar.get(s["isim"], {"anlik": 30, "hissedilen": 32, "nem": 40})
        anlik = veri["anlik"]
        hissedilen = veri["hissedilen"]
        nem = veri["nem"]
            
        alarm = "sicak" if anlik >= 38 or hissedilen >= 38 else "normal"
        sonuc.append({
            "isim": s["isim"], "lat": s["lat"], "lng": s["lng"],
            "anlik": anlik, "hissedilen": hissedilen, "nem": nem,
            "alarm": alarm, "panel": s["panel"]
        })
    return jsonify(sonuc)

@app.route("/api/forecast5")
def api_forecast5():
    return jsonify({"tahminler": [
        {"tarih": "2026-07-28", "durum": "Güneşli", "min": "26", "max": "38", "ikon": "☀️"},
        {"tarih": "2026-07-29", "durum": "Güneşli", "min": "27", "max": "39", "ikon": "☀️"},
        {"tarih": "2026-07-30", "durum": "Güneşli", "min": "26", "max": "38", "ikon": "☀️"},
        {"tarih": "2026-07-31", "durum": "Güneşli", "min": "25", "max": "37", "ikon": "☀️"},
        {"tarih": "2026-08-01", "durum": "Güneşli", "min": "27", "max": "40", "ikon": "☀️"}
    ]})

@app.route("/api/risk")
def api_risk():
    return jsonify({"dusuk": 50, "orta": 30, "yuksek": 20})

@app.route("/api/record-visit", methods=["POST"])
def api_record_visit():
    data = request.json
    if data:
        yeni_ziyaretci = {
            "sehir": data.get("city", "Bilinmiyor"),
            "ulke": data.get("country", "Türkiye"),
            "bayrak": data.get("flag", "🇹🇷"),
            "zaman": datetime.now().strftime("%H:%M:%S")
        }
        ziyaretci_listesi.insert(0, yeni_ziyaretci)
        if len(ziyaretci_listesi) > 20:
            ziyaretci_listesi.pop()
    return jsonify({"status": "success"})

@app.route("/api/visitors")
def api_visitors():
    return jsonify({"ziyaretciler": ziyaretci_listesi})

@app.route("/api/rain-check")
def api_rain_check():
    return jsonify({"yerler": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

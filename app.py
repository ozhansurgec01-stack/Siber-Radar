from flask import Flask, jsonify, render_template, request
import urllib.request
import json

app = Flask(__name__)

import time
online_users = {}

@app.before_request
def track_online():
    ip = request.remote_addr
    online_users[ip] = time.time()

@app.route('/api/online')
def online():
    now = time.time()
    aktif = [x for x,t in online_users.items() if now-t < 300]
    return jsonify({"online": len(aktif)})

@app.route('/')
def index():
    context = {
        "kameralar": json.load(open("kameralar.json", encoding="utf-8")),
        "risk": {"durum": "Normal", "seviye": 0},
        "depremler": []
    }
    return render_template('index.html', **context)

@app.route('/api/rain-check')
def rain_check():
    # Türkiye'nin ana yağış bölgelerini anlık tarayan dinamik koordinat listesi
    noktalar = [
        ("Karadeniz", "Trabzon", "Merkez", 41.0015, 39.7178),
        ("Karadeniz", "Rize", "Merkez", 41.0201, 40.5234),
        ("Karadeniz", "Samsun", "Merkez", 41.2867, 36.33),
        ("Karadeniz", "Ordu", "Merkez", 40.9839, 37.8764),
        ("Karadeniz", "Düzce", "Merkez", 40.8400, 31.1600),
        ("Karadeniz", "Bolu", "Merkez", 40.7350, 31.6061),
        ("Doğu Akdeniz", "Adana", "Merkez", 37.0000, 35.3213),
        ("Doğu Akdeniz", "Hatay", "Antakya", 36.2021, 36.1607),
        ("Marmara", "İstanbul", "Merkez", 41.0082, 28.9784),
        ("Ege", "İzmir", "Merkez", 38.4192, 27.1287),
        ("İç Anadolu", "Ankara", "Merkez", 39.9200, 32.8500)
    ]

    sonuc = []
    for bolge, il, ilce, lat, lon in noktalar:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=weathercode"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    code = data.get("current", {}).get("weathercode", 0)
                    
                    # 50 ve üzeri kodlar (çiseleme, sağanak, yağmur ve fırtına)
                    if code >= 50:
                        sonuc.append({"bolge": bolge, "il": il, "ilce": ilce, "durum": "🌧️ (Aktif Yağış)"})
        except Exception:
            continue

    return jsonify({"durum": "aktif", "yerler": sonuc, "kaynak": "Open-Meteo Live API"})



@app.route('/api/weather')
def weather():
    import urllib.request, json

    sehirler=[
        ("İSTANBUL","w-ist",41.0082,28.9784),
        ("ANKARA","w-ank",39.9334,32.8597),
        ("İZMİR","w-izm",38.4237,27.1428),
        ("ADANA","w-ada",37.0000,35.3213),
        ("ANTALYA","w-ant",36.8969,30.7133),
        ("MERSİN","w-mer",36.8121,34.6415),
        ("DİYARBAKIR","w-diy",37.9144,40.2306),
        ("TRABZON","w-tra",41.0027,39.7168),
        ("ERZURUM","w-erz",39.9043,41.2679),
        ("HAKKARİ","w-hak",37.5744,43.7408)
    ]

    sonuc=[]

    for isim,panel,lat,lng in sehirler:
        try:
            url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,apparent_temperature,relative_humidity_2m"
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})

            with urllib.request.urlopen(req,timeout=5) as r:
                d=json.loads(r.read().decode())

            sic=d["current"]["temperature_2m"]
            hiss=d["current"]["apparent_temperature"]
            nem=d["current"]["relative_humidity_2m"]

            alarm=None
            if sic>=38:
                alarm="sicak"
            elif sic<=0:
                alarm="soguk"

            sonuc.append({
                "isim":isim,
                "panel":panel,
                "anlik":round(sic),
                "hissedilen":round(hiss),
                "nem":round(nem),
                "alarm":alarm,
                "lat":lat,
                "lng":lng
            })

        except Exception as e:
            print("Hava hata:",isim,e)

    return jsonify(sonuc)

@app.route('/api/risk')
def risk():
    return jsonify({"durum":"Normal","seviye":0,"renk":"green"})

@app.route('/api/forecast5')
def forecast5():
    return jsonify({
        "tahminler": [
            {"ikon":"☀️","tarih":"Bugün","durum":"Açık","min":25,"max":39},
            {"ikon":"⛅","tarih":"Yarın","durum":"Parçalı Bulutlu","min":24,"max":37},
            {"ikon":"☀️","tarih":"3. Gün","durum":"Açık","min":25,"max":38},
            {"ikon":"🌧️","tarih":"4. Gün","durum":"Yağış ihtimali","min":23,"max":34},
            {"ikon":"☀️","tarih":"5. Gün","durum":"Açık","min":25,"max":39}
        ]
    })

@app.route("/api")
def deprem():
    import requests
    try:
        url="https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        r=requests.get(url,timeout=10)
        print("DEPREM STATUS:",r.status_code)
        data=r.json()

        liste=[]
        for d in data.get("result",[]):
            c=d.get("geojson",{}).get("coordinates",[None,None])
            if c[0] is None:
                continue

            liste.append({
                "lat":c[1],
                "lng":c[0],
                "mag":float(d.get("mag") or 0),
                "yer":d.get("title","Bilinmeyen"),
                "zaman":d.get("date_time","")
            })

        print("DEPREM ADET:",len(liste))
        return jsonify(liste)

    except Exception as e:
        print("DEPREM HATA:",e)
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

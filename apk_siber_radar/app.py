from flask import Flask, jsonify, render_template
import urllib.request
import json

app = Flask(__name__)

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
    sehirler = [
        {"isim":"İSTANBUL","panel":"w-ist","lat":41.0082,"lng":28.9784,"anlik":28,"hissedilen":29,"nem":60},
        {"isim":"ANKARA","panel":"w-ank","lat":39.9334,"lng":32.8597,"anlik":27,"hissedilen":29,"nem":43},
        {"isim":"İZMİR","panel":"w-izm","lat":38.4237,"lng":27.1428,"anlik":32,"hissedilen":34,"nem":43},
        {"isim":"ADANA","panel":"w-adn","lat":37.0,"lng":35.3213,"anlik":38,"hissedilen":40,"nem":35},
        {"isim":"ANTALYA","panel":"w-ant","lat":36.89,"lng":30.70,"anlik":36,"hissedilen":38,"nem":45},
        {"isim":"MERSİN","panel":"w-mer","lat":36.8121,"lng":34.6415,"anlik":31,"hissedilen":37,"nem":62},
        {"isim":"DİYARBAKIR","panel":"w-diy","lat":37.9144,"lng":40.2306,"anlik":40,"hissedilen":38,"nem":10},
        {"isim":"TRABZON","panel":"w-tra","lat":41.0027,"lng":39.7168,"anlik":27,"hissedilen":30,"nem":55},
        {"isim":"ERZURUM","panel":"w-erz","lat":39.9043,"lng":41.2679,"anlik":31,"hissedilen":30,"nem":27}
    ]

    for s in sehirler:
        if s["anlik"] >= 38:
            s["alarm"] = "sicak"
        elif s["anlik"] <= 0:
            s["alarm"] = "soguk"
        else:
            s["alarm"] = None

    return jsonify(sehirler)

@app.route('/api')
def deprem():
    import requests
    try:
        r=requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live",timeout=10)
        data=r.json()
        print("TOPLAM:",len(data.get("result",[])))

        liste=[]
        for d in data.get("result",[]):
            if float(d.get("mag") or 0) < 3.0: continue
            c=d.get("geojson",{}).get("coordinates",[0,0])

            liste.append({
                "lat": c[1],
                "lng": c[0],
                "mag": float(d.get("mag") or 0),
                "yer": d.get("title",""),
                "zaman": d.get("date_time","")
            })

        return jsonify(liste)

    except Exception as e:
        print("DEPREM HATA:",e)
        return jsonify([])

@app.route('/api/risk')
def risk():
    return jsonify({"durum":"Normal","seviye":0,"renk":"green"})

@app.route('/api/forecast5')
def forecast5():
    return jsonify({"tahmin":[
        {"gun":"Bugün","durum":"Açık"},
        {"gun":"Yarın","durum":"Parçalı Bulutlu"},
        {"gun":"3. Gün","durum":"Açık"},
        {"gun":"4. Gün","durum":"Yağış ihtimali"},
        {"gun":"5. Gün","durum":"Açık"}
    ]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

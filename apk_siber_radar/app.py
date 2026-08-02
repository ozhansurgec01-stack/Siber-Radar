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
    return jsonify({"durum":"aktif","sicaklik":25,"hava":"Açık","kaynak":"Siber Radar"})

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

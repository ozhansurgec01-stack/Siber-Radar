from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Kameralar listesi
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

@app.route('/api/kameralar')
def get_kameralar():
    return jsonify(kameralar)

@app.route('/api/weather/<city>')
def get_city_weather(city):
    try:
        # Örnek uyumlu hava durumu verisi
        return jsonify({
            "city": city,
            "temp": "28°C",
            "description": "Açık ve Güneşli",
            "humidity": "%45"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/forecast/<city>')
def get_city_forecast(city):
    try:
        # 5 günlük tahmin mock verisi
        return jsonify([
            {"day": "Pazartesi", "temp": "29°C", "condition": "Güneşli"},
            {"day": "Salı", "temp": "31°C", "condition": "Bulutlu"},
            {"day": "Çarşamba", "temp": "28°C", "condition": "Yağmurlu"},
            {"day": "Perşembe", "temp": "30°C", "condition": "Güneşli"},
            {"day": "Cuma", "temp": "32°C", "condition": "Güneşli"}
        ])
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/earthquakes')
def get_earthquakes():
    try:
        # Kandilli / AFAD benzeri örnek deprem verisi
        return jsonify([
            {"title": "Adana - Kozan", "mag": "3.4", "date": "2026-07-27 21:00:00", "depth": "7.0 km"}
        ])
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

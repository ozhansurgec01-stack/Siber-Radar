from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import requests

import os
import json
from flask import request

ZIYARETCI_DOSYA = "ziyaretciler.json"
HAVA_CACHE = "hava_cache.json"

def gercek_ip_al():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip

def ip_konum_bilgi(ip):
    try:
        data = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
        return {
            "ulke": data.get("country_name","Bilinmiyor"),
            "sehir": data.get("city","Bilinmiyor"),
            "lat": data.get("latitude",0),
            "lon": data.get("longitude",0),
            "isp": data.get("org","Bilinmiyor")
        }
    except Exception as e:
        return {"ulke":"Bilinmiyor","sehir":"Bilinmiyor","lat":0,"lon":0,"isp":"Bilinmiyor"}

def ziyaretci_kaydet():
    ip = gercek_ip_al()

    # Bulut/veri merkezi IP filtreleri
    engelli_prefix = (
        "3.", "18.", "34.", "35.", "52.", "54.",
        "5.161.", "178.156.",
        "10.", "127.", "192.168.", "172.16.", "172.17.", "172.18.",
        "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
        "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
        "172.29.", "172.30.", "172.31."
    )
    if ip.startswith(engelli_prefix):
        return

    konum = ip_konum_bilgi(ip)

    isp = konum.get("isp","").lower()
    engelli = ["amazon", "aws", "google", "cloud", "hetzner", "digitalocean", "azure", "microsoft", "ovh"]
    if any(x in isp for x in engelli):
        return

    kayit = {
        "ip": ip,
        "ulke": konum["ulke"],
        "sehir": konum["sehir"],
        "lat": konum.get("lat",konum.get("enlem",0)),
        "lon": konum.get("lon",konum.get("boylam",0)),
        "isp": konum["isp"],
        "zaman": datetime.now(ZoneInfo('Europe/Istanbul')).strftime("%Y-%m-%d %H:%M:%S"),
        "tarayici": request.headers.get("User-Agent","Bilinmiyor"),
        "metod": request.method
    }
    try:
        liste=[]
        if os.path.exists(ZIYARETCI_DOSYA):
            with open(ZIYARETCI_DOSYA,"r",encoding="utf-8") as f:
                liste=json.load(f)
        bulundu = False
        for eski in liste:
            if eski.get("ip") == ip:
                eski.update(kayit)
                eski["son_giris"] = kayit["zaman"]
                bulundu = True
                break

        if not bulundu:
            liste.append(kayit)
        with open(ZIYARETCI_DOSYA,"w",encoding="utf-8") as f:
            json.dump(liste,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print("Ziyaretci hata:",e)
app = Flask(__name__)

API_KEY = "47c985532d16457337f109fb907d8a60"
WEATHER_KEY = "a1f5b4f963e7409d9eb121923263007"

# Arayüzdeki hava durumu panelleriyle eşleşen şehir koordinatları ve kodları
SEHIRLER = [
    {"isim": "İstanbul", "lat": 41.0082, "lng": 28.9784, "query": "Istanbul", "panel": "w-ist"},
    {"isim": "Ankara", "lat": 39.9334, "lng": 32.8597, "query": "Ankara", "panel": "w-ank"},
    {"isim": "İzmir", "lat": 38.4192, "lng": 27.1287, "query": "Izmir", "panel": "w-izm"},
    {"isim": "Adana Seyhan", "lat": 37.0000, "lng": 35.3213, "query": "Seyhan,Adana,TR", "panel": "w-adn"},
    {"isim": "Mersin", "lat": 36.8121, "lng": 34.6415, "query": "Mersin", "panel": "w-mer"},
    {"isim": "Antalya", "lat": 36.8841, "lng": 30.7056, "query": "Antalya", "panel": "w-ant"},
    {"isim": "Diyarbakır", "lat": 37.9144, "lng": 40.2306, "query": "Diyarbakir", "panel": "w-diy"},
    {"isim": "Trabzon", "lat": 41.0015, "lng": 39.7178, "query": "Trabzon", "panel": "w-tra"},
    {"isim": "Balıkesir", "lat": 39.6484, "lng": 27.8826, "query": "Balikesir", "panel": "w-bal"},
{"isim": "Erzurum", "lat": 39.9043, "lng": 41.2679, "query": "Erzurum", "panel": "w-erz"}
]

@app.route('/')
def home():
    import json
    try:
        with open(os.path.join(os.path.dirname(__file__),"kameralar.json"),"r",encoding="utf-8") as f:
            kameralar=json.load(f)
    except Exception as e:
        kameralar=[]
    ziyaretci_kaydet()
    return render_template('index.html', kameralar=kameralar)


@app.route('/api/cameras')
def cameras():
    import json
    try:
        with open("kameralar.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify([
            {
                "isim": x[0],
                "lat": x[1],
                "lng": x[2],
                "link": x[3],
                "type": x[4]
            }
            for x in data
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api')
def api_status():
    try:
        url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        r = requests.get(url, timeout=10)
        veri = r.json()

        liste = []

        for d in veri.get("result", [])[:50]:
            c = d.get("geojson", {}).get("coordinates", [0,0])
            liste.append({
                "zaman": datetime.strptime(d.get("date_time",""), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S"),
                "yer": d.get("title", ""),
                "mag": float(d.get("mag", 0)),
                "lat": float(c[1]),
                "lng": float(c[0])
            })

        return jsonify(liste)

    except Exception as e:
        print("Deprem hata:", e)
        return jsonify({"error": repr(e)})

@app.route('/api/weather')
def weather():
    try:
        if os.path.exists(HAVA_CACHE):
            with open(HAVA_CACHE,"r",encoding="utf-8") as f:
                cache=json.load(f)

            zaman=datetime.fromisoformat(cache.get("zaman",""))
            if (datetime.now()-zaman).total_seconds() < 300:
                return jsonify(cache["veri"])
    except Exception as e:
        pass # hata: print(e)

    sonuclar = []

    for s in SEHIRLER:
        try:
            url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_KEY}&q={s['lat']},{s['lng']}&aqi=no"
            resp = requests.get(url, timeout=5)

            if resp.status_code == 200:
                c = resp.json()["current"]

                temp = round(c["temp_c"])
                feels = round(c["heatindex_c"])
                humidity = c["humidity"]

                wind = round(c.get("wind_kph", 0))
                wind_alarm = None

                if wind >= 60:
                    wind_alarm = "firtina"
                elif wind >= 40:
                    wind_alarm = "kuvvetli"

                fire_risk = "dusuk"
                if temp >= 35 and humidity <= 30 and wind >= 30:
                    fire_risk = "yuksek"
                elif temp >= 30 and humidity <= 40:
                    fire_risk = "orta"

                alarm = None
                if temp >= 38 or feels >= 38:
                    alarm = "sicak"
                elif temp <= 0:
                    alarm = "soguk"

                sonuclar.append({
                    "isim": s["isim"],
                    "lat": s["lat"],
                    "lng": s["lng"],
                    "anlik": temp,
                    "hissedilen": feels,
                    "nem": humidity,
                    "wind": wind,
                    "wind_alarm": wind_alarm,
                    "fire_risk": fire_risk,
                    "panel": s["panel"],
                    "alarm": alarm
                })

        except Exception as e:
            pass # hata: print(e)

    try:
        with open(HAVA_CACHE,"w",encoding="utf-8") as f:
            json.dump({
                "zaman": datetime.now().isoformat(),
                "veri": sonuclar
            },f,ensure_ascii=False,indent=2)
    except Exception as e:
        pass # hata: print(e)

    return jsonify(sonuclar)

@app.route('/api/risk')
def risk():
    return jsonify({"dusuk": 70, "orta": 20, "yuksek": 10})

@app.route('/api/forecast5')
def forecast5():
    try:
        url=f"https://api.openweathermap.org/data/2.5/forecast?lat=37.025&lon=35.371&appid={API_KEY}&units=metric&lang=tr"
        data=requests.get(url,timeout=10).json()

        gunler={}
        for x in data["list"]:
            tarih=x["dt_txt"].split(" ")[0]
            if tarih not in gunler:
                gunler[tarih]={
                    "min":round(x["main"]["temp_min"]),
                    "max":round(x["main"]["temp_max"]),
                    "durum":x["weather"][0]["description"]
                }
            else:
                gunler[tarih]["min"]=min(gunler[tarih]["min"],round(x["main"]["temp_min"]))
                gunler[tarih]["max"]=max(gunler[tarih]["max"],round(x["main"]["temp_max"]))

        sonuc=[]
        for tarih,v in list(gunler.items())[:5]:
            sonuc.append({
                "ikon":"☀️",
                "tarih":tarih,
                "durum":v["durum"],
                "min":v["min"],
                "max":v["max"]
            })

        return jsonify({"tahminler":sonuc})

    except Exception as e:
        return jsonify({"tahminler":[]})
@app.route('/api/rain-check')
def rain_check():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat=37.025&lon=35.371&appid={API_KEY}&units=metric&lang=tr"
        r = requests.get(url, timeout=10).json()

        hava = r.get("weather", [{}])[0].get("description", "").lower()

        if any(x in hava for x in ["yağmur", "rain", "sağanak", "drizzle", "fırtına"]):
            durum = "Yağmur yağıyor"
        else:
            durum = "Yağış yok / Açık"

        return jsonify({
            "yerler": [
                {
                    "il": "Adana",
                    "ilçe": "Merkez",
   "ilce": "Merkez",
                    "durum": durum
                }
            ]
        })

    except Exception as e:
        return jsonify({"yerler":[{"il":"Adana","ilçe":"Merkez","ilce":"Merkez","durum":"Veri alınamadı"}]})

@app.route('/api/storm')
def storm():
    sonuc=[]
    try:
        for s in SEHIRLER:
            try:
                url=f"http://api.openweathermap.org/data/2.5/weather?lat={s['lat']}&lon={s['lng']}&appid={API_KEY}&units=metric&lang=tr"
                d=requests.get(url,timeout=5).json()

                ruzgar=round(d.get("wind",{}).get("speed",0)*3.6)
                sicaklik=round(d.get("main",{}).get("temp",0))

                if ruzgar >= 60:
                    durum="🌪️ Fırtına uyarısı"
                elif ruzgar >= 40:
                    durum="⚠️ Fırtına riski"
                else:
                    continue

                sonuc.append({
                    "isim":s["isim"],
                    "ruzgar":ruzgar,
                    "sicaklik":sicaklik,
                    "durum":durum,
                    "kontrol": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                pass # hata: print(e)

        return jsonify(sonuc)

    except Exception:
        return jsonify([])
@app.route('/api/get-visits', methods=['GET'])
def api_get_visits_fix():
    return jsonify([])






# ===== OTOMATİK ZİYARETÇİ KAYIT SİSTEMİ =====

import json
from datetime import datetime
from flask import request

ONLINE_FILE = "ziyaretciler.json"


def otomatik_kayit():

    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )

    if "," in ip:
        ip = ip.split(",")[0]

    engelli_prefix = (
        "3.", "18.", "34.", "35.", "52.", "54.",
        "5.161.", "178.156.",
        "10.", "127.", "192.168.", "172.16.", "172.17.", "172.18.",
        "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
        "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
        "172.29.", "172.30.", "172.31."
    )

    if ip.startswith(engelli_prefix):
        return


    sehir = "Bilinmiyor"
    ulke = "Bilinmiyor"


    try:
        geo = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=3
        ).json()

        sehir = geo.get("city","Bilinmiyor")
        ulke = geo.get("country_name","Bilinmiyor")

    except Exception as e:
        pass # hata: print(e)


    try:
        with open(
            ONLINE_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            liste=json.load(f)

    except Exception as e:
        liste=[]


    yeni = {
        "ip": ip,
        "sehir": sehir,
        "ulke": ulke,
        "son_giris": datetime.now(ZoneInfo('Europe/Istanbul')).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


    bulundu=False

    for kisi in liste:
        if kisi.get("ip")==ip:
            kisi.update(yeni)
            bulundu=True


    if not bulundu:
        liste.append(yeni)


    with open(
        ONLINE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            liste,
            f,
            ensure_ascii=False,
            indent=2
        )


@app.before_request
def ziyaretci_otomatik():

    if request.path == "/":
        otomatik_kayit()


# ===== SON =====



@app.route("/api/ziyaretciler")
def ziyaretciler_api():
    try:
        with open("ziyaretciler.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return []


@app.route("/ziyaretci_panel")
def ziyaretci_panel():
    return """
    <div style="background:#080d18;color:#00ecff;padding:15px;font-family:monospace;border:2px solid #00ecff;border-radius:10px">
    <h3>📡👤</h3>
    <div id="liste">Yükleniyor...</div>
    </div>
    <script>
    fetch('/api/ziyaretciler')
    .then(r=>r.json())
    .then(d=>{
        let t="";
        d.forEach(x=>{
            t+=`🌐 IP: ${x.ip}<br>📍 ${x.sehir} / ${x.ulke}<br>🏢 ISP: ${x.isp || "Bilinmiyor"}<br>📱 ${x.tarayici || "Bilinmiyor"}<br>🔗 Metod: ${x.metod || "GET"}<br>🕒 ${x.son_giris || x.zaman || "Bilinmiyor"}<hr>`;
        });
        document.getElementById("liste").innerHTML=t||"Kayıt yok";
    });
    </script>
    """



# ==============================
# GELİŞMİŞ ZİYARETÇİ TAKİP SİSTEMİ
# ==============================

import os
import json
import requests
from datetime import datetime
from flask import request



def gercek_ip_al():
    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )

    if ip and "," in ip:
        ip = ip.split(",")[0].strip()

    return ip


def ip_konum_bilgi(ip):
    try:
        data = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=5
        ).json()

        return {
            "ulke": data.get("country_name","Bilinmiyor"),
            "sehir": data.get("city","Bilinmiyor"),
            "enlem": data.get("latitude",0),
            "boylam": data.get("longitude",0),
            "isp": data.get("org","Bilinmiyor")
        }

    except Exception:
        return {
            "ulke":"Bilinmiyor",
            "sehir":"Bilinmiyor",
            "enlem":0,
            "boylam":0,
            "isp":"Bilinmiyor"
        }




@app.route("/api/online")
def online_sayisi():
    try:
        with open("ziyaretciler.json","r",encoding="utf-8") as f:
            liste=json.load(f)

        simdi=datetime.now(ZoneInfo('Europe/Istanbul'))
        sayi=0
        aktif={}

        for x in liste:
            try:
                zaman=datetime.strptime(
                    x.get("son_giris", x.get("zaman","")),
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=ZoneInfo('Europe/Istanbul'))

                if (simdi-zaman).total_seconds() <= 300:
                    sayi += 1
                    aktif=x
            except Exception as e:
                pass # hata: print(e)

        konum=""
        if aktif:
            konum=aktif.get("ulke","Bilinmiyor")+" / "+aktif.get("sehir","Bilinmiyor")

        return {"online": sayi, "konum": konum}

    except Exception:
        return {"online": 0, "konum": ""}



@app.route('/api/polen')
def polen():
    return jsonify({
        "durum":"Veri hazırlanıyor",
        "kaynak":"OpenWeather",
        "veri":[]
    })


@app.route('/api/heatmap')
def heatmap():
    return jsonify([])





@app.route("/api/yanginin")
def yangin_alarm():
    try:
        import io, requests

        url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/763d612c3fd36fdca0ce4239ebac5263/VIIRS_SNPP_NRT/24,34,46,43/1"

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return jsonify({
                "error": "NASA FIRMS bağlantı hatası",
                "status": res.status_code
            }), 500

        import csv

        rows = csv.DictReader(io.StringIO(res.text))

        yanginlar = []

        for row in rows:
            lat = float(row["latitude"])
            lng = float(row["longitude"])
            print("NASA NOKTA:", lat, lng)

            # Türkiye yaklaşık sınır filtresi
            if 35.8 <= lat <= 42.1 and 26.0 <= lng <= 44.8:
                iller = [
            ("Balıkesir", 39.65, 27.88),
            ("İzmir", 38.42, 27.14),
            ("Muğla", 37.21, 28.36),
            ("Antalya", 36.89, 30.70),
            ("Çanakkale", 40.15, 26.40)
        ]

        il = "Bilinmeyen"

        for isim, ilat, ilng in iller:
            if abs(lat-ilat) < 2.5 and abs(lng-ilng) < 2.5:
                il = isim
                break

        yanginlar.append({
            "aktif": True,
            "il": il,
            "lat": lat,
            "lng": lng,
            "frp": float(row["frp"])
        })

        return jsonify(yanginlar)

    except Exception as e:
        import traceback
        return jsonify({
            "error": repr(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

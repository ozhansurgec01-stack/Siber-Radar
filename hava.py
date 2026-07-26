import urllib.request
import json
import ssl

def get_weather():
    # Adana için Anlık ve 5 Günlük Senkronize Veri URL'si
    url = "https://api.open-meteo.com/v1/forecast?latitude=37.0000&longitude=35.3213&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print("Hava durumu çekme hatası:", e)
        return None

if __name__ == "__main__":
    print(get_weather())

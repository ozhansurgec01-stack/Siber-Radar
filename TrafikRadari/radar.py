import os
import time
import subprocess
import threading
from PIL import Image, ImageChops, ImageStat
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)
son_gecisler = []

# --- BALKON AYARLARI ---
ESIK_DEGERI = 5.0        
YOL_MESAFESI = 10.0      

HTML_SAYFASI = """
<!DOCTYPE html>
<html>
<head>
    <title>Termux Canlı Yol Radarı</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #121214; color: #e1e1e6; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #ff9100; margin-bottom: 5px; }
        .live-badge { background: #00e676; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block; animation: blink 1.5s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        .card { background: #202024; border-radius: 8px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-top: 4px solid #ff9100; }
        .hiz-box { font-size: 48px; font-weight: bold; color: #ff9100; margin: 10px 0; }
        .hiz-birim { font-size: 16px; color: #a8a8b3; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #29292e; }
        th { color: #ff9100; font-size: 14px; }
        tr:nth-child(even) { background: #29292e; }
    </style>
    <script>
        setInterval(function() {
            fetch('/veri').then(response => response.json()).then(data => {
                if(data.length > 0) {
                    document.getElementById('son_hiz').innerText = data[0].hiz;
                    document.getElementById('son_tur').innerText = data[0].tur;
                    let tabloHtml = "";
                    data.forEach(arac => {
                        tabloHtml += `<tr><td>${arac.zaman}</td><td>${arac.tur}</td><td>${arac.sure}</td><td style="color:#ff9100;font-weight:bold;">${arac.hiz} km/h</td></tr>`;
                    });
                    document.getElementById('tablo_govde').innerHTML = tabloHtml;
                }
            });
        }, 1000);
    </script>
</head>
<body>
    <div class="container">
        <h1>🌐 TRAFİK RADARI (BALKON MODU)</h1>
        <div class="live-badge">YEREL PANEL AKTİF</div>
        <div class="card">
            <div id="son_tur" style="font-size: 18px; color: #a8a8b3;">Yol İzleniyor...</div>
            <div class="hiz-box"><span id="son_hiz">0.0</span> <span class="hiz-birim">km/h</span></div>
        </div>
        <div class="card" style="border-top: 4px solid #333;">
            <h3 style="margin: 0; text-align: left;">📋 Geçiş Geçmişi</h3>
            <table>
                <thead><tr><th>Saat</th><th>Tür</th><th>Süre</th><th>Hız</th></tr></thead>
                <tbody id="tablo_govde"><tr><td colspan="4" style="text-align:center;color:#7c7c8a;">Araç bekleniyor...</td></tr></tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def radar_cekirdek():
    global son_gecisler
    if os.path.exists("stream.jpg"): os.remove("stream.jpg")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "android_camera", "-input_queue_size", "10",
        "-video_size", "640x480", "-camera_index", "0", "-i", "0", 
        "-pix_fmt", "yuv420p", "-vframes", "100000", "-update", "1", "stream.jpg"
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    while not os.path.exists("stream.jpg"): time.sleep(0.5)
    os.system("cp stream.jpg bos_yol.jpg")
    
    hareket_basladi_mi = False
    baslangic_zamani = 0
    last_trigger = 0
    
    while True:
        try:
            if not os.path.exists("stream.jpg"): continue
            
            img1 = Image.open("bos_yol.jpg").convert("L")
            img2 = Image.open("stream.jpg").convert("L")
            
            diff = ImageChops.difference(img1, img2)
            stat = ImageStat.Stat(diff)
            fark = stat.mean[0]
            su_an = time.time()
            
            if fark > 1.0:
                print(f"[Anlık Değişim]: {fark:.2f}", end="\r")
            
            if fark > ESIK_DEGERI:
                if not hareket_basladi_mi:
                    baslangic_zamani = su_an
                    hareket_basladi_mi = True
                last_trigger = su_an
            else:
                if hareket_basladi_mi and (su_an - last_trigger > 0.4):
                    gecen_sure = last_trigger - baslangic_zamani
                    if gecen_sure > 0.05:
                        hiz_kh = (YOL_MESAFESI / gecen_sure) * 3.6
                        if 3.0 <= hiz_kh <= 180.0:
                            zaman_damgasi = time.strftime('%H:%M:%S')
                            
                            if hiz_kh < 15.0: araç_türü = "🚲 Bisiklet / Elektrikli"
                            elif hiz_kh < 45.0: araç_türü = "🛵 Motosiklet"
                            else: araç_türü = "🚗 Araba"
                            
                            yeni_veri = {"zaman": zaman_damgasi, "tur": araç_türü, "sure": f"{gecen_sure:.2f} sn", "hiz": f"{hiz_kh:.1f}"}
                            son_gecisler.insert(0, yeni_veri)
                            if len(son_gecisler) > 10: son_gecisler.pop()
                            print(f"\n[RADAR] {araç_türü} Geçti! Hız: {hiz_kh:.1f} km/h\n")
                            
                    hareket_basladi_mi = False
            
            os.system("cp stream.jpg bos_yol.jpg")
            time.sleep(0.02)
        except Exception:
            continue

@app.route('/')
def index(): 
    return render_template_string(HTML_SAYFASI)

@app.route('/veri')
def veri(): 
    return jsonify(son_gecisler)

threading.Thread(target=radar_cekirdek, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

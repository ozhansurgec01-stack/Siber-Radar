from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;padding:8px;background:#000;font-family:Arial,sans-serif;}
h1{text-align:center;font-size:28px;margin:15px 0 25px;}
.card{width:96%;height:105px;margin:10px auto;padding:10px;border-radius:35px;text-align:center;box-sizing:border-box;}
.card h2{font-size:20px;margin:5px;}
.card p{font-size:28px;margin:8px;}
</style>
</head>

<body>

<h1>Canlı Altın & Kripto</h1>

<div class="card btc">₿ BTC<br><div class="fiyat">{{btc}}</div></div>

<div class="card a24">🟡 24 AYAR GRAM<br><div class="fiyat">{{g24}}</div></div>

<div class="card a22">🟠 22 AYAR GRAM<br><div class="fiyat">{{g22}}</div></div>

<div class="card ceyrek">🟢 ÇEYREK ALTIN<br><div class="fiyat">{{ceyrek}}</div></div>

<div class="card yarim">🔵 YARIM ALTIN<br><div class="fiyat">{{yarim}}</div></div>

<div class="card tam">🔴 TAM ALTIN<br><div class="fiyat">{{tam}}</div></div>

</body>
</html>
"""


def veri():

    btc="Veri yok"
    g24="Veri yok"
    g22="Veri yok"
    ceyrek="Veri yok"
    yarim="Veri yok"
    tam="Veri yok"

    try:
        b=requests.get(
        "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
        timeout=10).json()

        btc="$"+b["price"]

    except Exception as e:
        print("BTC:",e)


    try:
        a=requests.get(
        "https://finans.truncgil.com/today.json",
        timeout=10).json()

        g24=a["gram-altin"]["Satış"]
        g22=a["22-ayar-bilezik"]["Satış"]
        ceyrek=a["ceyrek-altin"]["Satış"]
        yarim=a["yarim-altin"]["Satış"]
        tam=a["tam-altin"]["Satış"]

    except Exception as e:
        print("ALTIN:",e)


    return btc,g24,g22,ceyrek,yarim,tam


@app.route("/")
def index():

    btc,g24,g22,c,y,t=veri()

    return render_template_string(
        HTML,
        btc=btc,
        g24=g24,
        g22=g22,
        ceyrek=c,
        yarim=y,
        tam=t
    )


app.run(host="0.0.0.0",port=5000)

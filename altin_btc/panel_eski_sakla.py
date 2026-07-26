from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{
background:#050505;
color:white;
font-family:Arial;
text-align:center;
}

h1{
color:#00eaff;
text-shadow:0 0 20px #00eaff;
}

.card{
margin:20px;
padding:30px;
border-radius:35px;
border:3px solid #00eaff;
box-shadow:0 0 25px #00eaff;
}

.gold{
border-color:#ffd000;
box-shadow:0 0 25px #ffd000;
}

.title{
font-size:25px;
}

.price{
font-size:38px;
font-weight:bold;
margin-top:15px;
}

</style>
</head>

<body>

<h1>🪙 Canlı Altın & Kripto</h1>

<div class="card">
<div class="title">₿ BTC</div>
<div class="price">{{btc}} $</div>
</div>


<div class="card gold">
<div class="title">🌍 ONS ALTIN</div>
<div class="price">{{ons}} $</div>
</div>


<div class="card gold">
<div class="title">🟡 GRAM ALTIN 24 AYAR</div>
<div class="price">{{gram}} TL</div>
</div>


<div class="card gold">
<div class="title">🟠 ÇEYREK ALTIN</div>
<div class="price">{{ceyrek}} TL</div>
</div>


</body>
</html>
"""


def veri():

    btc="Veri yok"
    ons="Veri yok"
    gram="Veri yok"
    ceyrek="Veri yok"


    # BTC
    try:
        r=requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=10)

        btc=r.json()["bitcoin"]["usd"]

    except:
        pass


    # ALTIN
    try:
        r=requests.get(
        "https://api.metals.live/v1/spot/gold",
        timeout=10)

        ons=float(r.json()[0]["gold"])

        gram=round(ons*0.03215*40,2)
        ceyrek=round(gram*1.75,2)

    except:
        pass


    return btc,ons,gram,ceyrek



@app.route("/")
def home():

    btc,ons,gram,ceyrek=veri()

    return render_template_string(
        HTML,
        btc=btc,
        ons=ons,
        gram=gram,
        ceyrek=ceyrek
    )


app.run(host="0.0.0.0",port=5000)

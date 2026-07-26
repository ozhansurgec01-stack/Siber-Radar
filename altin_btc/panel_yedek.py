from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>

<meta name="viewport" content="width=device-width, initial-scale=1">

<meta http-equiv="refresh" content="5">

<style>

body{
background:#000;
color:white;
font-family:Arial;
text-align:center;
margin:0;
padding:8px;
}

h1{
font-size:28px;
}

.card{
width:95%;
max-width:380px;
margin:8px auto;
padding:10px;
border-radius:28px;
border:3px solid;
}

.title{
font-size:21px;
}

.price{
font-size:32px;
margin-top:6px;
}


.btc{
color:#00eaff;
border-color:#00eaff;
}

.ons{
color:white;
border-color:white;
}

.altin24{
color:#ffd700;
border-color:#ffd700;
}

.altin22{
color:#ff9900;
border-color:#ff9900;
}

.ceyrek{
color:#00ff00;
border-color:#00ff00;
}

.yarim{
color:#00ffff;
border-color:#00ffff;
}

.tam{
color:#ff3333;
border-color:#ff3333;
}


@media(max-width:500px){

.title{
font-size:18px;
}

.price{
font-size:28px;
}

.card{
padding:8px;
}

}

</style>

</head>


<body>


<h1>Canlı Altın & Kripto</h1>


<div class="card btc">
<div class="title">₿ BTC</div>
<div class="price">${{btc}}</div>
</div>


<div class="card ons">
<div class="title">🌍 ONS ALTIN</div>
<div class="price">${{ons}}</div>
</div>


<div class="card altin24">
<div class="title">🟡 GRAM ALTIN 24 AYAR</div>
<div class="price">{{gram24}}</div>
</div>


<div class="card altin22">
<div class="title">🟠 GRAM ALTIN 22 AYAR</div>
<div class="price">{{gram22}}</div>
</div>


<div class="card ceyrek">
<div class="title">🟠 ÇEYREK ALTIN</div>
<div class="price">{{ceyrek}}</div>
</div>


<div class="card yarim">
<div class="title">🟢 YARIM ALTIN</div>
<div class="price">{{yarim}}</div>
</div>


<div class="card tam">
<div class="title">🔴 TAM ALTIN</div>
<div class="price">{{tam}}</div>
</div>


</body>
</html>
"""


def sayiya_cevir(x):
    try:
        if isinstance(x,str):
            x=x.replace(".","").replace(",",".")
        return float(x)

    except:
        return 0


def formatla(x):

    try:
        x=float(x)

        return "{:,.2f}".format(x)\
        .replace(",", "X")\
        .replace(".", ",")\
        .replace("X",".")

    except:
        return "Veri yok"



def veri_al():

    btc="Veri yok"
    ons="Veri yok"

    gram24="Veri yok"
    gram22="Veri yok"
    ceyrek="Veri yok"
    yarim="Veri yok"
    tam="Veri yok"



    # BTC

    try:

        b=requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=8
        ).json()

        btc=formatla(b["price"])

    except Exception as e:
        print("BTC hata:",e)



    # ALTIN

    try:

        a=requests.get(
            "https://finans.truncgil.com/today.json",
            timeout=8
        ).json()


        gram24=sayiya_cevir(
            a["gram-altin"]["Satış"]
        )


        gram22=gram24*0.916


        ceyrek=sayiya_cevir(
            a["ceyrek-altin"]["Satış"]
        )


        yarim=sayiya_cevir(
            a["yarim-altin"]["Satış"]
        )


        tam=sayiya_cevir(
            a["tam-altin"]["Satış"]
        )


        gram24=formatla(gram24)
        gram22=formatla(gram22)
        ceyrek=formatla(ceyrek)
        yarim=formatla(yarim)
        tam=formatla(tam)



    except Exception as e:

        print("Altın hata:",e)



    # ONS

    try:

        o=requests.get(
            "https://api.gold-api.com/price/XAU",
            timeout=8
        ).json()


        ons=formatla(
            o["price"]
        )


    except Exception as e:

        print("Ons hata:",e)



    return (
        btc,
        ons,
        gram24,
        gram22,
        ceyrek,
        yarim,
        tam
    )




@app.route("/")

def ana():

    veriler=veri_al()


    return render_template_string(
        HTML,
        btc=veriler[0],
        ons=veriler[1],
        gram24=veriler[2],
        gram22=veriler[3],
        ceyrek=veriler[4],
        yarim=veriler[5],
        tam=veriler[6]
    )



app.run(
    host="0.0.0.0",
    port=5000
)

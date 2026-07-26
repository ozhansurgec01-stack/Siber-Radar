cat <<EOF > finans.py
from flask import Flask, render_template_string
import yfinance as yf

app = Flask(__name__)

HTML_TEMPLATE = """
<html>
<head>
    <meta http-equiv="refresh" content="60">
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: sans-serif; padding: 20px; }
        .card { background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 12px; }
        h1 { color: #03dac6; }
        .price { font-size: 1.4em; color: #ffffff; }
    </style>
</head>
<body>
    <h1>Finans Takip (60sn Güncel)</h1>
    {% for name, price in data.items() %}
    <div class="card">
        <div>{{ name }}</div>
        <div class="price">{{ price }} TL</div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    # Altın fiyatlarını çekmek için BIST/Finansal tickerlar
    # NOT: yfinance üzerinden TRY bazlı altın verisi için semboller:
    tickers = {
        "Gram Altın": "XAUTRY=X",
        "Dolar/TL": "USDTRY=X",
        "Bitcoin": "BTC-USD"
    }
    
    results = {}
    for name, ticker in tickers.items():
        t = yf.Ticker(ticker)
        data = t.history(period="1d")
        if not data.empty:
            results[name] = f"{data['Close'].iloc[-1]:.2f}"
            
    return render_template_string(HTML_TEMPLATE, data=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

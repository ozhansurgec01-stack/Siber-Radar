import json
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Kameralari JSON dosyasindan yukle
if os.path.exists("kameralar.json"):
    with open("kameralar.json", "r", encoding="utf-8") as f:
        kameralar = json.load(f)
else:
    kameralar = []

@app.route("/")
def index():
    return render_template("index.html", kameralar=kameralar)

@app.route("/api/kameralar")
def api_kameralar():
    return jsonify(kameralar)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

python server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

data = {}

@app.route("/update", methods=["POST"])
def update():
    global data
    data = request.json
    return "OK"

@app.route("/get")
def get():
    return jsonify(data)

app.run(host="0.0.0.0", port=5000)

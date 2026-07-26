from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <title>Radar</title>
</head>
<body style="background:black;color:lime;font-family:monospace;">
<h2>RADAR ACTIVE</h2>
<div id="t">loading...</div>

<script>
async function load(){
  let r = await fetch('/data');
  let d = await r.json();
  document.getElementById("t").innerHTML =
    "TARGETS: " + d.length;
}
setInterval(load, 3000);
load();
</script>

</body>
</html>
"""

def get_data():
    try:
        r = requests.get("https://opensky-network.org/api/states/all", timeout=10)
        j = r.json()

        out = []
        for p in j.get("states", []):
            if p and p[5] and p[6]:
                out.append({"lat": p[6], "lon": p[5]})

        return out[:50]

    except:
        return []

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/data")
def data():
    return jsonify(get_data())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

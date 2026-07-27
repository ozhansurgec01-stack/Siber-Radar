from flask import Flask, render_template

app = Flask(__name__)

# Güvenli ve hatasız boş kamera listesi
kameralar = []

@app.route('/')
def index():
    return render_template('index.html', kameralar=kameralar)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

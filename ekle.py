with open('app.py', 'r') as f:
    content = f.read()

rota = '''
@app.route('/api/forecast5')
def forecast5():
    yedek = [
        {"tarih": "Pzt", "max": 37, "min": 26, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Sal", "max": 38, "min": 27, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Çar", "max": 41, "min": 28, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Per", "max": 40, "min": 27, "ikon": "☀️", "durum": "Aşırı Sıcak"},
        {"tarih": "Cum", "max": 39, "min": 26, "ikon": "☀️", "durum": "Aşırı Sıcak"}
    ]
    return jsonify({"tahminler": yedek, "alert": None})
'''

if '/api/forecast5' not in content:
    with open('app.py', 'a') as f:
        f.write(rota)
    print("Başarıyla eklendi!")
else:
    print("Zaten ekliydi.")

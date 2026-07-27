import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

yeni_kameralar = 'kameralar = []'

if "kameralar =" in content:
    content = re.sub(r'kameralar\s*=\s*\[.*?\]', yeni_kameralar, content, flags=re.DOTALL)
else:
    content += "\n" + yeni_kameralar

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Kamera listesi başarıyla temizlendi!")

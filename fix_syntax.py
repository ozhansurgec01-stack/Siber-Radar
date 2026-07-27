with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned_lines = []
i = 0
while i < len(lines):
    if 'kameralar' in lines[i]:
        cleaned_lines.append('kameralar = []\n')
        i += 1
        # Eski listeden kalan artık satırları ve parantezleri atla
        while i < len(lines) and (any(k in lines[i] for k in ['[', ']', 'Canlı', 'Kamerası', 'YouTube', 'EarthCam', 'Times Square']) or lines[i].strip() == ']' or lines[i].strip() == '],' or lines[i].strip() == ']'):
            i += 1
    else:
        cleaned_lines.append(lines[i])
        i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("Syntax hatası ve artık parantezler temizlendi!")

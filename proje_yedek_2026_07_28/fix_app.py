import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski kameralar tanımını tamamen temizle ve en baştan hatasız boş liste koy
content = re.sub(r'^[ \t]*kameralar\s*=.*?(?=\n\S|\Z)', '', content, flags=re.DOTALL | re.MULTILINE)
content = re.sub(r'^[ \t]*kameralar\s*=\s*\[.*?\]', 'kameralar = []', content, flags=re.DOTALL | re.MULTILINE)

if "kameralar =" not in content:
    content += "\nkameralar = []\n"

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py girinti hatasından arındırıldı!")

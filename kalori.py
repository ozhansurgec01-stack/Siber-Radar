import os
import sys
import base64
import requests
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

console = Console()

def logo_yazdir():
    logo = Text("\n🍏 AI KALORİ SİHRBAZI 🍏\n", style="bold green blink", justify="center")
    logo.append("=========================", style="bold yellow")
    console.print(Panel(logo, border_style="green"))

def kalori_hesapla(resim_yolu):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print(Panel("[red]❌ Hata: GEMINI_API_KEY bulunamadı![/red]", title="Sistem Hatası", border_style="red"))
        return

    if not os.path.exists(resim_yolu):
        console.print(Panel(f"[red]❌ Hata: Dosya bulunamadı:[/red] [yellow]{resim_yolu}[/yellow]", title="Dosya Hatası", border_style="red"))
        return

    console.print(Panel(f"[cyan]📷 Görsel Sıkıştırılıyor ve Optimize Ediliyor...[/cyan]", border_style="blue"))
    
    try:
        img = Image.open(resim_yolu)
        img.thumbnail((1024, 1024))
        img.save("temp_optimize.jpg", "JPEG")
        with open("temp_optimize.jpg", "rb") as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        os.remove("temp_optimize.jpg")
    except Exception as e:
        console.print(Panel(f"[red]❌ Görsel işlenirken hata oluştu:[/red] {e}", border_style="red"))
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="[bold magenta]🤖 Gemini Yapay Zekası tabağınızı inceliyor...[/bold magenta]", total=None)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # İstemi menemen/yumurta ihtimallerini doğru süzmesi için güncelledik
        prompt = (
            "Bu fotoğraftaki yemeği detaylıca analiz et. Eğer fotoğrafta domatesli, soğanlı/soğansız yumurta veya menemen benzeri bir Türk lezzeti varsa bunu tulum peyniri ezmesiyle karıştırma, doğru teşhis koy. "
            "1. Yiyeceğin ismini kalın harflerle tespit et. "
            "2. Porsiyon miktarını tahmin et. "
            "3. Kalori, protein, karbonhidrat ve yağ değerlerini hesapla. "
            "Sonuçları Markdown formatında, başlıklar ve emojiler kullanarak şık bir tablo/liste şeklinde Türkçe sun."
        )

        payload = {
            "contents": [{
                "parts": [{"text": prompt}, {"inlineData": {"mimeType": "image/jpeg", "data": img_data}}]
            }]
        }

        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
            res_json = response.json()
            if 'error' in res_json:
                console.print(Panel(f"[red]❌ Google API Hatası:[/red] {res_json['error']['message']}", border_style="red"))
                return
            analiz_sonucu = res_json['candidates'][0]['content']['parts'][0]['text']
            console.print("\n")
            md = Markdown(analiz_sonucu)
            console.print(Panel(md, title="🍏 YAPAY ZEKA KALORİ ANALİZ RAPORU", border_style="green", expand=False))
            console.print("\n[bold gold1]✨ Afiyet olsun! Sağlıklı günler dilerim. ✨[/bold gold1]\n")
        except Exception as e:
            console.print(Panel(f"[red]❌ Analiz sırasında genel bir hata oluştu:[/red] {e}", border_style="red"))

if __name__ == "__main__":
    logo_yazdir()
    if len(sys.argv) < 2:
        console.print("[yellow]Kullanım:[/yellow] python kalori.py <resim_yolu>")
    else:
        kalori_hesapla(sys.argv[1])

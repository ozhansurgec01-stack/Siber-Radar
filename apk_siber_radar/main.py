from kivy.app import App
from kivy.uix.webview import WebView
import threading
import subprocess
import time

class SiberRadar(App):
    def build(self):
        threading.Thread(target=self.server, daemon=True).start()
        time.sleep(3)
        return WebView(url="http://127.0.0.1:5000")

    def server(self):
        subprocess.Popen(["python", "app.py"])

SiberRadar().run()

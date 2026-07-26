from kivy.app import App
from threading import Thread
from jnius import autoclass
import app  # Senin Flask dosyanın adı app.py ise burası 'app' kalmalı

def start_flask():
    app.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

class PanelApp(App):
    def build(self):
        Thread(target=start_flask, daemon=True).start()
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True) # Bu çok önemli, CSS/JS için şart
        webview.setWebViewClient(WebViewClient())
        webview.loadUrl('http://127.0.0.1:5000')
        activity.setContentView(webview)
        return webview

if __name__ == '__main__':
    PanelApp().run()

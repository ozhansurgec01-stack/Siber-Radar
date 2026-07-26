import yfinance as yf
import ta

def analiz(sembol, isim):
    print("\n================")
    print(isim)

    veri = yf.download(sembol, period="6mo", interval="1d", progress=False)

    if veri.empty:
        print("Veri alinamadi")
        return

    kapanis = veri["Close"].squeeze()

    if len(kapanis) < 50:
        print("Yeterli veri yok")
        return

    fiyat = float(kapanis.iloc[-1])

    rsi = ta.momentum.RSIIndicator(
        kapanis
    ).rsi().iloc[-1]

    ema20 = ta.trend.EMAIndicator(
        kapanis, window=20
    ).ema_indicator().iloc[-1]

    ema50 = ta.trend.EMAIndicator(
        kapanis, window=50
    ).ema_indicator().iloc[-1]

    print("Fiyat:", round(fiyat, 2))
    print("RSI:", round(float(rsi), 2))

    if ema20 > ema50:
        print("Trend: YUKARI")
    else:
        print("Trend: ASAGI")

    if rsi < 30:
        print("Sinyal: AL")
    elif rsi > 70:
        print("Sinyal: SAT")
    else:
        print("Sinyal: BEKLE")


analiz("BTC-USD", "BITCOIN")

analiz("GC=F", "ALTIN XAU/USD")

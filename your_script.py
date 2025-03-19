from iqoptionapi.stable_api import IQ_Option
import time
import numpy as np
from datetime import datetime
import pytz
import firebase_admin
from firebase_admin import credentials, firestore

# **🔥 Firebase Setup**
cred = credentials.Certificate("service-account.json")  # 🔥 अपनी JSON Key का सही नाम डालें
firebase_admin.initialize_app(cred)
db = firestore.client()

# **IQ Option लॉगिन डिटेल्स**
email = "vigivaj570@oziere.com"
password = "Vigivaj@570"

Iq = IQ_Option(email, password)
Iq.connect()
if Iq.check_connect():
    print("✔️ Login Successful!")
else:
    print("❌ Login Failed!")
    exit()

# **🔥 बाइनरी ट्रेडिंग के लिए मार्केट्स की लिस्ट**
markets = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", "USDCHF", "USDCAD", "GBPJPY", "EURJPY",
    "AAPL", "GOOG", "AMZN", "XAUUSD", "XAGUSD", "WTICOUSD"
]

# **🔥 टाइमफ्रेम**
timeframe = 60  # 1-minute candles
india_tz = pytz.timezone('Asia/Kolkata')

# **🔥 EMA Calculation Function**
def calculate_ema(data, period=10):
    close_prices = [candle['close'] for candle in data]
    ema = np.mean(close_prices[-period:])
    return ema

# **🔥 Firebase में Signal Save करने की Function**
def save_signal(market, signal_type):
    data = {
        "market": market,
        "signal": signal_type,
        "timestamp": firestore.SERVER_TIMESTAMP  # 🔥 Automatic Server Timestamp
    }
    db.collection("signals").add(data)
    print(f"📌 Signal Saved: {market} -> {signal_type}")

# **🔥 Signal Generation Function (EMA Strategy)**
def generate_signals():
    for market in markets:
        candles = Iq.get_candles(market, timeframe, 2, time.time())  # Only get last 2 candles
        ema = calculate_ema(candles)

        last_price = candles[-1]['close']
        prev_candle = candles[-2]
        
        # ✅ **EMA Based Signal Strategy**
        # **BUY SIGNAL**
        if prev_candle['close'] < ema and last_price > ema:
            time.sleep(60)  # Wait for the next candle
            next_candle = Iq.get_candles(market, timeframe, 1, time.time())[0]
            if next_candle['close'] > next_candle['open']:  
                print(f"🔼 BUY Signal for {market}")
                save_signal(market, "BUY")  # 🔥 Firebase में Save

        # **SELL SIGNAL**
        elif prev_candle['close'] > ema and last_price < ema:
            time.sleep(60)  # Wait for the next candle
            next_candle = Iq.get_candles(market, timeframe, 1, time.time())[0]
            if next_candle['close'] < next_candle['open']:  
                print(f"🔽 SELL Signal for {market}")
                save_signal(market, "SELL")  # 🔥 Firebase में Save

# **🔥 Run the Strategy Based on Candle Close Time**
while True:
    india_time = datetime.now(india_tz)
    if india_time.second == 0:  
        generate_signals()  # 🚀 Auto-Generate Signals
    time.sleep(1)
      

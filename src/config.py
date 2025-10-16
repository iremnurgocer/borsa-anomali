"""
Konfigurasyon Dosyasi

Bu dosyada proje genelinde kullanilan ayarlari tutuyorum.
Buradan klasor yollarini, anomali tespit parametrelerini ve
diger ayarlari yonetiyorum.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasi varsa yukluyorum (opsiyonel)
load_dotenv()

# Proje ana dizinini ve alt klasorleri tanimliyorum
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

# Klasorler yoksa olusturuyorum
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Borsa ile ilgili ayarlar
class ExchangeConfig:
    """
    Borsa baglanti ayarlari
    
    Bunlari .env dosyasindan veya dogrudan buradan ayarlayabilirsin
    """
    # Hangi borsa kullanilacak (binance, bybit, okx, kraken...)
    EXCHANGE = os.getenv("EXCHANGE", "binance")  
    
    # Hangi parite analiz edilecek
    SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
    
    # Zaman araligi (1m, 5m, 15m, 1h, 4h, 1d)
    TIMEFRAME = os.getenv("TIMEFRAME", "15m")
    
    # Kac gunluk veri cekilecek
    DAYS_BACK = int(os.getenv("DAYS_BACK", "60"))
    
    # API anahtarlari (opsiyonel - public veriler icin gerekmiyor)
    API_KEY = os.getenv("API_KEY", "")
    API_SECRET = os.getenv("API_SECRET", "")


# Anomali tespit ayarlari
class AnomalyConfig:
    """
    Anomali tespit algoritmalari icin parametreler
    
    Bu parametreleri degistirerek anomali tespitinin hassasligini ayarlayabilirsin
    """
    # Beklenen anomali orani (0.05 = %5 anomali bekliyorum)
    CONTAMINATION = 0.05
    
    # Isolation Forest icin agac sayisi (yuksek = daha dogru ama yavas)
    N_ESTIMATORS = 100
    
    # Rastgelelik kontrolu (tekrarlanabilir sonuclar icin)
    RANDOM_STATE = 42
    
    # Z-Score esigi (3'un uzerindekiler anomali sayilir)
    Z_SCORE_THRESHOLD = 3.0
    
    # IQR carpani (1.5 standart, 3.0 sadece cok ekstrem outlier'lar)
    IQR_MULTIPLIER = 1.5
    
    # Hangi yontemleri kullanacagiz
    METHODS = ["isolation_forest", "z_score", "iqr"]
    
    # Grafik olusturulsun mu (opsiyonel)
    PLOT_RESULTS = True
    SAVE_PLOTS = True


# Veri isleme ayarlari
class DataConfig:
    """
    Veri isleme ve ozellik cikarimi ayarlari
    """
    # Hangi fiyat sutunu kullanilacak (open, high, low, close)
    # Mum kapanis fiyatlarini kullaniyorum
    PRICE_COLUMN = "close"
    
    # Ek ozellikler ekleyelim mi? (volatilite, momentum vs.)
    ADD_FEATURES = True
    
    # Hangi ozellikler eklenecek
    FEATURES = [
        "price_change",     # Fiyat degisimi (mutlak)
        "price_pct_change", # Yuzde degisim
        "volume_change",    # Hacim degisimi
        "volatility",       # Volatilite (standart sapma)
        "price_momentum"    # Momentum (fiyat trendi)
    ]
    
    # Veri kayit formati
    SAVE_FORMAT = "csv"  # csv veya json


# Log seviyesi
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Borsa Anomali Tespit Sistemi

Bu projeyi borsa verilerinden anormal fiyat hareketlerini tespit etmek icin gelistirdim. Herhangi bir borsadan veri cekip, makine ogrenmesi algoritmalari ile anomalileri buluyor.

## Ozellikler

- 100+ borsadan veri cekme (Binance, Bybit, OKX, Kraken...)
- 3 farkli makine ogrenmesi yontemi ile anomali tespiti
- Zaman damgali anomali kayitlari
- CSV ve JSON formatinda ciktilar
- 60 gunluk veri analizi
- 15 dakikalik mum verileri

## Gereksinimler

- Python 3.9 veya uzeri
- Internet baglantisi (veri cekmek icin)

## Kurulum

1. Gerekli kutuphaneleri yukle:

```bash
pip install ccxt pandas numpy scikit-learn matplotlib python-dotenv seaborn
```

veya

```bash
pip install -r requirements.txt
```

## Kullanim

### Basit Kullanim

```bash
py anomali_tespiti.py
```

Program calisir ve sonuclari `results/` klasorune kaydeder.

### Ayarlari Degistirme

`anomali_tespiti.py` dosyasini ac ve degistir:

```python
BORSA = "binance"      # Binance, bybit, okx, kraken...
PARITE = "BTC/USDT"    # BTC/USDT, ETH/USDT, SOL/USDT...
TIMEFRAME = "15m"      # 15m, 1h, 4h, 1d...
GUN_SAYISI = 60        # Kac gunluk veri cekilecek
```

## Sonuclar

Program calistiktan sonra su dosyalar olusur:

```
results/
  - anomaliler_TARIH.csv    <- Zaman damgali anomaliler (EN ONEMLI)
  - tum_veri_TARIH.csv      <- Tum veriler
  - ozet_TARIH.json         <- Detayli rapor

data/
  - ham_veri_TARIH.csv      <- Ham OHLCV verisi
```

### anomaliler_TARIH.csv Ornegi

```csv
timestamp,close,ensemble_oy
2025-10-05 02:45:00,124031.44,2.0
2025-10-05 03:30:00,124010.12,2.0
```

- `timestamp`: Anomalinin gerceklestigi zaman
- `close`: Kapanis fiyati
- `ensemble_oy`: Kac yontem anomali dediyse (2-3 guvenilir)

## Anomali Tespit Yontemleri

1. **Isolation Forest**: Makine ogrenmesi tabanli, en guclu yontem
2. **Z-Score**: Istatistiksel yontem, hizli ve basit
3. **IQR**: Ceyrekler arasi aralik, robust yontem

Program bu 3 yontemi birlestirir (Ensemble Voting) ve en az 2 yontemin anomali dedigi verileri secr. Bu sekilde daha guvenilir sonuc elde eder.

## Proje Yapisi

```
borsa-anomali/
├── anomali_tespiti.py      # Ana program
├── src/                    # Kaynak kodlar
│   ├── config.py           # Ayarlar
│   ├── data_fetcher.py     # Veri cekme
│   ├── data_processor.py   # Veri isleme
│   ├── anomaly_detector.py # Anomali tespiti
│   └── visualizer.py       # Gorsellestime
├── results/                # Sonuclar
├── data/                   # Ham veriler
└── requirements.txt        # Gerekli kutuphaneler
```

## Nasil Calisir?

1. **Veri Cekme**: CCXT kutuphanesi ile borsadan OHLCV verisi ceker
2. **Veri Temizleme**: Eksik ve hatali verileri temizler
3. **Ozellik Cikarimi**: Fiyat degisimi, volatilite gibi ozellikler ekler
4. **Anomali Tespiti**: 3 farkli algoritma ile anormal hareketleri bulur
5. **Sonuc Kaydetme**: Zaman damgali anomalileri CSV ve JSON olarak kaydeder

## Ornekler

### Farkli Parite Analizi

```python
# anomali_tespiti.py dosyasinda:
PARITE = "ETH/USDT"  # Ethereum
```

### Farkli Borsa

```python
BORSA = "bybit"  # Bybit borsasi
```

### Farkli Zaman Araligi

```python
TIMEFRAME = "1h"    # 1 saatlik mumlar
GUN_SAYISI = 30     # 30 gunluk veri
```

### Hangi borsalar destekleniyor?

100+ borsa: Binance, Bybit, OKX, Kraken, Coinbase, Huobi, KuCoin ve daha fazlasi.

### Program ne kadar surede calisiyor?

60 gunluk veri icin yaklasik 30-60 saniye.

## Sorun Giderme

### "ModuleNotFoundError" hatasi

```bash
pip install ccxt pandas numpy scikit-learn
```

### "Symbol not found" hatasi

Parite adini kontrol et. Dogru format: `BTC/USDT` (slash ile)


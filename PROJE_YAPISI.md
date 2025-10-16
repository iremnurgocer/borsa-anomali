# Proje Yapisi

Bu dokumanda projenin dosya yapisini ve her dosyanin ne ise yaradigini anlatiyorum.

## Genel Yapi

```
borsa-anomali/
├── anomali_tespiti.py          # Ana program (buradan calistir)
├── requirements.txt            # Gerekli kutuphaneler
├── README.md                   # Proje dokumantasyonu
├── KULLANIM_KILAVUZU.md       # Nasil kullanilir kilavuzu
├── PROJE_YAPISI.md            # Bu dosya
├── .gitignore                  # Git icin ignore kurallari
│
├── src/                        # Kaynak kodlar
│   ├── __init__.py
│   ├── config.py
│   ├── data_fetcher.py
│   ├── data_processor.py
│   ├── anomaly_detector.py
│   └── visualizer.py
│
├── data/                       # Ham veriler (otomatik olusur)
│   └── ham_veri_*.csv
│
└── results/                    # Sonuclar (otomatik olusur)
    ├── anomaliler_*.csv
    ├── tum_veri_*.csv
    └── ozet_*.json
```

---

## Ana Dosyalar

### anomali_tespiti.py

**Ne yapar**: Ana program. Butun islemi yoneten dosya.

**Icerigi**:
- Ayarlar (BORSA, PARITE, TIMEFRAME, GUN_SAYISI)
- 4 adimlik islem akisi:
  1. Veri cekme
  2. Veri isleme
  3. Anomali tespiti
  4. Sonuc kaydetme

**Nasil kullanilir**: 
```bash
py anomali_tespiti.py
```

**Ne zaman degistirirsin**: 
- Farkli borsa kullanmak istersen
- Farkli parite analiz etmek istersen
- Timeframe veya gun sayisini degistirmek istersen

### requirements.txt

**Ne yapar**: Gerekli Python kutuphanelerini listeler.

**Icerigi**:
```
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
python-dotenv>=1.0.0
seaborn>=0.12.0
```

**Nasil kullanilir**:
```bash
pip install -r requirements.txt
```

### README.md

**Ne yapar**: Projenin ana dokumantasyonu.

**Icerigi**:
- Proje tanitimi
- Kurulum adimlari
- Hizli baslangic
- Sikca sorulan sorular

### KULLANIM_KILAVUZU.md

**Ne yapar**: Detayli kullanim kilavuzu.

**Icerigi**:
- Adim adim kurulum
- Ayar degistirme
- Sorun giderme
- Ornekler

### .gitignore

**Ne yapar**: Git'in gormezden gelmesi gereken dosyalari listeler.

**Icerigi**:
- Python cache dosyalari
- Veri dosyalari
- Sonuc dosyalari
- IDE ayar dosyalari

---

## src/ Klasoru (Kaynak Kodlar)

Bu klasorde programin ana modulleri var. Bunlari genellikle degistirmene gerek yok.

### src/__init__.py

**Ne yapar**: src klasorunu Python paketi yapar.

**Icerigi**: Bos veya versiyon bilgisi.

### src/config.py

**Ne yapar**: Proje genelinde kullanilan ayarlari tutar.

**Icerigi**:
- Klasor yollari (DATA_DIR, RESULTS_DIR)
- Anomali tespit parametreleri
- Veri isleme ayarlari

**Ne zaman degistirirsin**: Nadiren. Ileri seviye ayarlar icin.

### src/data_fetcher.py

**Ne yapar**: Borsadan veri ceker.

**Ana sinif**: `DataFetcher`

**Ne yapar**:
```python
fetcher = DataFetcher("binance")
df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=60)
```

**Ozellikler**:
- 100+ borsaya baglanir (CCXT kullanarak)
- OHLCV verisi ceker (Open, High, Low, Close, Volume)
- Buyuk veri setlerini parca parca ceker
- Rate limiting koruması var

**Fonksiyonlar**:
- `__init__()`: Borsaya baglanir
- `fetch_ohlcv()`: Veri ceker
- `get_available_symbols()`: Mevcut pariteleri listeler
- `get_exchange_info()`: Borsa bilgilerini doner

### src/data_processor.py

**Ne yapar**: Veriyi temizler ve hazirlar.

**Ana sinif**: `DataProcessor`

**Ne yapar**:
```python
processor = DataProcessor(df)
processor.clean_data()
processor.add_features(['price_change', 'volatility'])
X = processor.prepare_for_anomaly_detection("close")
```

**Ozellikler**:
- Eksik verileri temizler
- Hatali fiyatlari kaldirir
- Teknik ozellikler ekler:
  - Fiyat degisimi
  - Yuzde degisim
  - Volatilite
  - Momentum
  - Hacim degisimi

**Fonksiyonlar**:
- `clean_data()`: Veriyi temizler
- `add_features()`: Teknik ozellikler ekler
- `prepare_for_anomaly_detection()`: Anomali tespiti icin hazirlar
- `get_statistics()`: Istatistikleri hesaplar

### src/anomaly_detector.py

**Ne yapar**: Anomali tespiti yapar.

**Ana sinif**: `AnomalyDetector`

**Ne yapar**:
```python
detector = AnomalyDetector(contamination=0.05)
results = detector.detect_all_methods(X)
ensemble_pred, votes = detector.ensemble_voting(results, min_votes=2)
```

**Ozellikler**:
- 3 farkli yontem kullanir:
  1. Isolation Forest (makine ogrenmesi)
  2. Z-Score (istatistiksel)
  3. IQR (ceyrekler arasi aralik)
- Ensemble voting ile yontemleri birlesitirir
- Her anomaliye guvenilirlik skoru verir

**Fonksiyonlar**:
- `detect_isolation_forest()`: ML tabanli tespit
- `detect_z_score()`: Istatistiksel tespit
- `detect_iqr()`: IQR tabanli tespit
- `detect_all_methods()`: Tum yontemleri calistirir
- `ensemble_voting()`: Yontemleri birlesitirir

### src/visualizer.py

**Ne yapar**: Sonuclari gorsellestirir (opsiyonel).

**Ana sinif**: `AnomalyVisualizer`

**Ne yapar**:
```python
visualizer = AnomalyVisualizer(df)
visualizer.plot_multiple_methods(results, ensemble_pred)
```

**Ozellikler**:
- Fiyat grafikleri ciziyor
- Anomalileri isaretliyor
- Yontemleri karsilastiriyor
- PNG formatinda kaydediyor

**Fonksiyonlar**:
- `plot_price_with_anomalies()`: Fiyat + anomali grafigi
- `plot_multiple_methods()`: Yontem karsilastirmasi
- `plot_anomaly_scores()`: Anomali skorlari
- `plot_statistics()`: Istatistikler

**Not**: Su an ana programda kullanilmiyor. Istersen ekleyebilirsin.

---

## data/ Klasoru

**Ne yapar**: Ham OHLCV verilerini saklar.

**Otomatik olusur**: Program ilk calistirildiginda olusur.

**Icerigi**:
```
data/
├── ham_veri_20251016_143754.csv
├── ham_veri_20251016_144328.csv
└── ...
```

**Dosya formati**: CSV
```csv
timestamp_ms,open,high,low,close,volume,timestamp
1759632300000,123673.0,124129.25,123537.27,124031.44,522.62761,2025-10-05 02:45:00
```

**Ne zaman silinir**: Disk alani azalirsa eski dosyalari silebilirsin.

---

## results/ Klasoru

**Ne yapar**: Anomali tespit sonuclarini saklar.

**Otomatik olusur**: Program ilk calistirildiginda olusur.

**Icerigi**:
```
results/
├── anomaliler_20251016_143754.csv      # Zaman damgali anomaliler
├── tum_veri_20251016_143754.csv        # Tum veriler
├── ozet_20251016_143754.json           # JSON rapor
└── ...
```

### anomaliler_*.csv (EN ONEMLI)

**Ne yapar**: Sadece anomali olan verileri tutar.

**Format**:
```csv
timestamp,close,ensemble_oy
2025-10-05 02:45:00,124031.44,2.0
```

**Sutunlar**:
- `timestamp`: Tarih ve saat
- `close`: Kapanis fiyati
- `ensemble_oy`: Guvenilirlik (2-3 iyi)
- Diger teknik sutunlar

### tum_veri_*.csv

**Ne yapar**: Tum verileri tutar (normal + anomali).

**Icerigi**: Ham veri + anomali skorlari + oylama sonuclari

### ozet_*.json

**Ne yapar**: Detayli JSON raporu.

**Format**:
```json
{
  "borsa": "binance",
  "parite": "BTC/USDT",
  "timeframe": "15m",
  "gun_sayisi": 60,
  "toplam_mum": 5759,
  "toplam_anomali": 143
}
```

---

## Dosya Isimlendirme

Tum sonuc dosyalari zaman damgali:
```
anomaliler_YYYYMMDD_HHMMSS.csv
          └─── 20251016_143754
               └─── 2025/10/16 14:37:54
```

Bu sayede her calistirma farkli dosyalar olusturur ve onceki sonuclar kaybolmaz.

---

## Veri Akisi

```
1. anomali_tespiti.py
   └─> data_fetcher.py     (Borsadan veri ceker)
       └─> data/ham_veri_*.csv
           └─> data_processor.py   (Veriyi temizler)
               └─> anomaly_detector.py   (Anomali tespit eder)
                   └─> results/anomaliler_*.csv
                   └─> results/tum_veri_*.csv
                   └─> results/ozet_*.json
```

---

## Hangi Dosyalari Degistirebilirsin?

### Guvenle Degistirebilirsin:
- `anomali_tespiti.py` (ayarlar kismini)
- `README.md` (kendi notlarin icin)

### Degistirme (ileri seviye):
- `src/config.py` (ileri seviye ayarlar)
- `src/*.py` dosyalari (kod bilgisi gerekir)

### Asla Degistirme:
- `requirements.txt` (kutuphane surumlerini bozabilir)
- `.gitignore` (Git'i bozabilir)

---

## Disk Alani Yonetimi

### data/ klasoru

- Ham veriler burada
- Her calistirma ~1-5 MB
- Ayda bir temizleyebilirsin

### results/ klasoru

- Sonuclar burada
- Her calistirma ~2-10 MB
- Onemli sonuclari yedekle, gerisini sil

### Temizlik komutu (Windows):

```bash
# Eski veri dosyalarini sil
del data\ham_veri_*.csv

# Eski sonuc dosyalarini sil (DIKKAT: Hepsini siler!)
del results\*.*
```

---

## Ozet

Bu proje 3 ana katmandan olusuyor:

1. **Veri Katmani** (data_fetcher, data_processor)
   - Veri ceker ve hazirlar

2. **Analiz Katmani** (anomaly_detector)
   - Anomali tespiti yapar

3. **Sunum Katmani** (anomali_tespiti, visualizer)
   - Sonuclari kaydeder ve gosterir

Her katman bagimsiz calisir, bu yuzden kod temiz ve anlasilir.

---

**Soru**: Hangi dosyayi okumalisin?
- Hizli baslangic icin: `README.md`
- Detayli kullanim icin: `KULLANIM_KILAVUZU.md`
- Proje yapisi icin: `PROJE_YAPISI.md` (bu dosya)
- Kod okumak icin: `src/` klasoru

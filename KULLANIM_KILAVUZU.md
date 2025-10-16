# Kullanim Kilavuzu

Bu dokumanda programi nasil kullanacagini adim adim anlatiyorum.

## Hizli Baslangic

### 1. Kutuphaneleri Yukle (Ilk Seferlik)

```bash
pip install ccxt pandas numpy scikit-learn matplotlib python-dotenv seaborn
```

### 2. Programi Calistir

```bash
py anomali_tespiti.py
```

### 3. Sonuclari Incele

Sonuclar `results/` klasorunde:
- `anomaliler_*.csv` dosyasini ac (Excel veya Notepad ile)

Bu kadar!

---

## Detayli Kullanim

### Adim 1: Kurulum

#### Gerekli Programlar

1. **Python 3.9+** yuklu olmali
   - Kontrol et: `python --version`
   
2. **Pip** yuklu olmali (Python ile birlikte gelir)
   - Kontrol et: `pip --version`

#### Kutuphaneleri Yukle

Terminal'i ac ve su komutu calistir:

```bash
pip install ccxt pandas numpy scikit-learn matplotlib python-dotenv seaborn
```

Yukleme 5-10 dakika surebilir. Bitene kadar bekle.

### Adim 2: Ayarlari Yapilandirma

`anomali_tespiti.py` dosyasini bir metin editoruyle ac (Notepad, VS Code, vs.)

En ustte su satirlari goreceksin:

```python
BORSA = "binance"      # Hangi borsadan veri cekilecek
PARITE = "BTC/USDT"    # Hangi parite analiz edilecek
TIMEFRAME = "15m"      # Kac dakikalik mumlar
GUN_SAYISI = 60        # Kac gunluk veri cekilecek
```

#### Borsa Degistirme

```python
BORSA = "binance"   # Binance
BORSA = "bybit"     # Bybit
BORSA = "okx"       # OKX
BORSA = "kraken"    # Kraken
```

**Desteklenen borsalar**: binance, bybit, okx, kraken, coinbase, huobi, kucoin, gateio, bitget ve 90+ daha fazla

#### Parite Degistirme

```python
PARITE = "BTC/USDT"   # Bitcoin
PARITE = "ETH/USDT"   # Ethereum
PARITE = "SOL/USDT"   # Solana
PARITE = "BNB/USDT"   # Binance Coin
PARITE = "XRP/USDT"   # Ripple
```

**Onemli**: Slash (/) kullanmalisin: `BTC/USDT` dogru, `BTCUSDT` yanlis

#### Timeframe Degistirme

```python
TIMEFRAME = "1m"    # 1 dakika
TIMEFRAME = "5m"    # 5 dakika
TIMEFRAME = "15m"   # 15 dakika (varsayilan)
TIMEFRAME = "1h"    # 1 saat
TIMEFRAME = "4h"    # 4 saat
TIMEFRAME = "1d"    # 1 gun
```

#### Gun Sayisi Degistirme

```python
GUN_SAYISI = 7      # 1 hafta
GUN_SAYISI = 30     # 1 ay
GUN_SAYISI = 60     # 2 ay (varsayilan)
GUN_SAYISI = 90     # 3 ay
```

**Not**: Cok fazla gun secersen program yavas calisabilir.

### Adim 3: Programi Calistirma

#### Windows'ta

1. Proje klasorune git
2. Adres cubuguna `cmd` yaz ve Enter'a bas
3. Su komutu yaz:

```bash
py anomali_tespiti.py
```

veya

```bash
python anomali_tespiti.py
```

#### Program Ciktisi

Program calisirken su sekilde cikti verir:

```
======================================================================
               BORSA ANOMALI TESPIT SISTEMI
======================================================================

Ayarlar:
   Borsa: BINANCE
   Parite: BTC/USDT
   Timeframe: 15m
   Veri Araligi: Son 60 gun
   Analiz: Mum kapanis fiyatlari
======================================================================

======================================================================
ADIM 1: VERI CEKILIYOR
======================================================================
BINANCE borsasina baglandi
Beklenen veri: ~5,760 mum
Bu islem biraz zaman alabilir, bekleyin...

Veri cekiliyor: BTC/USDT (15m) - Son 60 gun
5760 adet veri cekildi

======================================================================
ADIM 2: VERI ISLENIYOR
======================================================================
Veri temizleniyor...
   Veri temiz (5760 satir)
Teknik ozellikler ekleniyor...
   4 ozellik eklendi

======================================================================
ADIM 3: ANOMALI TESPITI YAPILIYOR
======================================================================
...
Toplam 143 adet anomali buldum

======================================================================
ISLEM TAMAMLANDI
======================================================================
```

### Adim 4: Sonuclari Inceleme

Program bitince `results/` klasorunde dosyalar olusur.

#### En Onemli Dosya: anomaliler_*.csv

Bu dosyada zaman damgali anomaliler var. Excel'de acabilirsin:

```csv
timestamp,close,ensemble_oy
2025-10-05 02:45:00,124031.44,2.0
2025-10-05 03:30:00,124010.12,2.0
```

**Sutunlar**:
- `timestamp`: Anomalinin gerceklestigi tarih ve saat
- `close`: O andaki kapanis fiyati
- `ensemble_oy`: Kac yontem anomali dediyse
  - 3 oy = Cok guvenilir (3 yontem de anomali dedi)
  - 2 oy = Guvenilir (2 yontem anomali dedi)
  - 1 oy = Zayif (1 yontem anomali dedi)

#### Diger Dosyalar

- `tum_veri_*.csv`: Tum veriler (normal + anomali)
- `ozet_*.json`: JSON formatinda detayli rapor
- `data/ham_veri_*.csv`: Ham OHLCV verisi

### Adim 5: Sonuclari Degerlendirme

#### Anomali Nedir?

Anomali, normal fiyat hareketlerinden sapan olaylardir. Ornegin:
- Ani fiyat atisi
- Ani fiyat dususu
- Normal disi hacim artisi

#### Guvenilir Anomaliler

`ensemble_oy` sutununa bak:
- **3 oy**: En guvenilir, 3 yontem de anomali dedi
- **2 oy**: Guvenilir, 2 yontem anomali dedi
- **1 oy**: Daha az guvenilir, sadece 1 yontem dedi

**Tavsiye**: 2 ve 3 oy alan anomalilere odaklan.

---

## Ornekler

### Ornek 1: Bitcoin Haftalik Analiz

```python
# anomali_tespiti.py dosyasinda:
BORSA = "binance"
PARITE = "BTC/USDT"
TIMEFRAME = "1h"
GUN_SAYISI = 7
```

Calistir:
```bash
py anomali_tespiti.py
```

### Ornek 2: Ethereum Aylik Analiz

```python
BORSA = "binance"
PARITE = "ETH/USDT"
TIMEFRAME = "15m"
GUN_SAYISI = 30
```

### Ornek 3: Bybit Borsasi

```python
BORSA = "bybit"
PARITE = "BTC/USDT"
TIMEFRAME = "1h"
GUN_SAYISI = 60
```

---

## Sorun Giderme

### Problem: "py komutu bulunamadi"

**Cozum**: `python` kullan:
```bash
python anomali_tespiti.py
```

### Problem: "ModuleNotFoundError: No module named 'ccxt'"

**Cozum**: Kutuphaneleri yukle:
```bash
pip install ccxt pandas numpy scikit-learn
```

### Problem: "Symbol 'XYZ/USDT' not found"

**Cozum**: 
1. Parite adini kontrol et (slash kullanmalisin: `BTC/USDT`)
2. O paritenin sectigin borsada oldugunu kontrol et

### Problem: Program cok yavas calisiyor

**Cozum**:
1. Gun sayisini azalt: `GUN_SAYISI = 30`
2. Daha buyuk timeframe kullan: `TIMEFRAME = "1h"`

### Problem: Hic anomali bulunamadi

**Cozum**:
1. Normal bir durum olabilir, tum veriler normal olabilir
2. Daha fazla gun ekle: `GUN_SAYISI = 90`
3. Daha kucuk timeframe dene: `TIMEFRAME = "5m"`

---

## Ileri Seviye

### Anomali Tespit Parametrelerini Degistirme

`anomali_tespiti.py` dosyasinda su satiri bul:

```python
detector = AnomalyDetector(contamination=0.05)
```

`contamination` parametresi veride ne kadar anomali beklendigini belirler:
- `0.01` = %1 anomali bekliyorum (cok az)
- `0.05` = %5 anomali bekliyorum (varsayilan)
- `0.10` = %10 anomali bekliyorum (cok)

Daha fazla anomali bulmak istiyorsan artir: `contamination=0.10`

### Minimum Oy Sayisini Degistirme

```python
ensemble_tahmin, oylar = detector.ensemble_voting(sonuclar, min_votes=2)
```

`min_votes` parametresi en az kac yontemin anomali demesi gerektigini belirler:
- `min_votes=1` = 1 yontem yeterli (daha cok anomali bulur)
- `min_votes=2` = 2 yontem gerekli (varsayilan, dengeli)
- `min_votes=3` = 3 yontem gerekli (en guvenilir, az anomali bulur)

---

## Ipuclari

1. Ilk testte kucuk gun sayisi kullan (7-30 gun) - hizli test icin
2. Ensemble_oy >= 2 olan anomalilere odaklan - daha guvenilir
3. Farkli timeframe'ler dene - farkli anomaliler bulabilirsin
4. Sonuclari Excel'de ac - daha kolay incelenebilir
5. Eski sonuc dosyalarini sil - disk alani kazanmak icin

---

## Sonuc

Bu program:
- Borsadan veri ceker
- 3 farkli yontemle anomali tespit eder
- Zaman damgali sonuclar verir
- Kullanimi cok kolay

Sorularin olursa README.md dosyasina bak veya bana ulas.


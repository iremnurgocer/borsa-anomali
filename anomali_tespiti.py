"""
BORSA ANOMALI TESPIT SISTEMI

Bu programi borsa verilerinden anomali tespiti yapmak icin yazdim.
Herhangi bir borsadan veri cekip, makine ogrenmesi ile anormal fiyat
hareketlerini tespit ediyor.

Nasil calisir:
1. CCXT kutuphanesi ile borsadan veri ceker
2. Veriyi temizler ve hazirlar
3. 3 farkli algoritma ile anomali tespiti yapar
4. Sonuclari CSV ve JSON formatinda kaydeder

Calistirmak icin: py anomali_tespiti.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.anomaly_detector import AnomalyDetector
from src.config import DATA_DIR, RESULTS_DIR
from datetime import datetime
import json

# Buradan ayarlari degistirebilirsin
BORSA = "binance"      # Hangi borsadan veri cekilecek
PARITE = "BTC/USDT"    # Hangi parite analiz edilecek (BTC/USDT, ETH/USDT vs.)
TIMEFRAME = "15m"      # Kac dakikalik mumlar (15m = 15 dakika)
GUN_SAYISI = 60        # Kac gunluk veri cekilecek

# Ana program buradan basliyor

def main():
    # Ekrana program bilgilerini yazdiriyorum
    print("\n" + "="*70)
    print(" "*15 + "BORSA ANOMALI TESPIT SISTEMI")
    print("="*70)
    print(f"\nAyarlar:")
    print(f"   Borsa: {BORSA.upper()}")
    print(f"   Parite: {PARITE}")
    print(f"   Timeframe: {TIMEFRAME}")
    print(f"   Veri Araligi: Son {GUN_SAYISI} gun")
    print(f"   Analiz: Mum kapanis fiyatlari")
    print("="*70)
    
    # Dosya isimleri icin zaman damgasi olusturuyorum
    zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # ADIM 1: Borsadan veri cekme
        print(f"\n{'='*70}")
        print("ADIM 1: VERI CEKILIYOR")
        print("="*70)
        
        # Veri cekme objesi olusturuyorum
        fetcher = DataFetcher(BORSA)
        
        # Kac tane mum verisi gelmesi gerektigini hesapliyorum
        beklenen_veri = GUN_SAYISI * 24 * (60 // int(TIMEFRAME.replace('m', '')))
        print(f"\nBeklenen veri: ~{beklenen_veri:,} mum")
        print(f"Bu islem biraz zaman alabilir, bekleyin...\n")
        
        # Simdi borsadan veriyi cekiyorum
        df = fetcher.fetch_ohlcv(PARITE, TIMEFRAME, days_back=GUN_SAYISI)
        
        # Ham veriyi data klasorune kaydediyorum
        ham_veri_dosyasi = DATA_DIR / f"ham_veri_{zaman_damgasi}.csv"
        df.to_csv(ham_veri_dosyasi, index=False)
        
        # ADIM 2: Veriyi temizleme ve hazirlama
        print(f"\n{'='*70}")
        print("ADIM 2: VERI ISLENIYOR")
        print("="*70)
        
        # Veri isleme objesi olusturuyorum
        processor = DataProcessor(df)
        
        # Veriyi temizliyorum (eksik degerler, hatali fiyatlar vs.)
        processor.clean_data()
        
        # Ek ozellikler ekliyorum (fiyat degisimi, volatilite vs.)
        processor.add_features(['price_change', 'price_pct_change', 'volume_change', 'volatility'])
        
        # Veri hakkinda ozet bilgileri ekrana yazdiriyorum
        stats = processor.get_statistics()
        print(f"\nVeri Ozeti:")
        print(f"   Toplam Mum: {stats['total_rows']:,} adet")
        print(f"   Tarih: {stats['date_range']['start'][:10]} - {stats['date_range']['end'][:10]}")
        print(f"   Gun: {stats['date_range']['days']} gun")
        print(f"   Fiyat: ${stats['price_stats']['min']:,.2f} - ${stats['price_stats']['max']:,.2f}")
        print(f"   Ortalama: ${stats['price_stats']['mean']:,.2f}")
        
        # Anomali tespiti icin mum kapanis fiyatlarini hazirliyorum
        X = processor.prepare_for_anomaly_detection("close")
        
        # ADIM 3: Makine ogrenmesi ile anomali tespiti
        print(f"\n{'='*70}")
        print("ADIM 3: ANOMALI TESPITI YAPILIYOR")
        print("="*70)
        
        # Anomali tespit modeli olusturuyorum (contamination = beklenen anomali orani)
        detector = AnomalyDetector(contamination=0.05)
        
        # 3 farkli yontemle anomali tespiti yapiyorum
        # - Isolation Forest: Makine ogrenmesi tabanli
        # - Z-Score: Istatistiksel yontem
        # - IQR: Ceyrekler arasi aralik yontemi
        sonuclar = detector.detect_all_methods(X, methods=["isolation_forest", "z_score", "iqr"])
        
        # En az 2 yontemin anomali dedigi verileri seciyorum (daha guvenilir)
        ensemble_tahmin, oylar = detector.ensemble_voting(sonuclar, min_votes=2)
        
        # ADIM 4: Sonuclari dosyalara kaydetme
        print(f"\n{'='*70}")
        print("ADIM 4: SONUCLAR KAYDEDILIYOR")
        print("="*70)
        
        # Orijinal veriye anomali sonuclarini ekliyorum
        sonuc_df = processor.df.copy()
        
        # Her yontemin sonucunu ayri sutunlarda sakliyorum
        for yontem, (tahminler, skorlar) in sonuclar.items():
            sonuc_df[f'{yontem}_anomali'] = tahminler
            sonuc_df[f'{yontem}_skor'] = skorlar
        
        # Birlestirilmis sonuclari da ekliyorum
        sonuc_df['ensemble_anomali'] = ensemble_tahmin
        sonuc_df['ensemble_oy'] = oylar
        
        # Sadece anomali olarak isaretlenen verileri filtreliyorum
        # Bunlar zaman damgali olarak kaydedilecek
        anomaliler_df = sonuc_df[sonuc_df['ensemble_anomali'] == -1].copy()
        
        # Sonuc dosyalarinin isimlerini hazirliyorum
        tum_sonuclar = RESULTS_DIR / f"tum_veri_{zaman_damgasi}.csv"
        anomaliler_dosya = RESULTS_DIR / f"anomaliler_{zaman_damgasi}.csv"
        ozet_rapor = RESULTS_DIR / f"ozet_{zaman_damgasi}.json"
        
        # Tum verileri (anomali + normal) results klasorune kaydediyorum
        sonuc_df.to_csv(tum_sonuclar, index=False)
        print(f"\nTum veriler: {tum_sonuclar.name}")
        
        # Eger anomali bulunmussa, onlari ayri bir dosyaya kaydediyorum
        # Bu dosya en onemli cikti - zaman damgali anomaliler burada
        if len(anomaliler_df) > 0:
            anomaliler_df.to_csv(anomaliler_dosya, index=False)
            print(f"Anomaliler: {anomaliler_dosya.name}")
        
        # JSON formatinda ozet rapor hazirliyorum
        # Bu raporda tum istatistikler ve anomali sayilari var
        rapor = {
            'tarih': zaman_damgasi,
            'borsa': BORSA,
            'parite': PARITE,
            'timeframe': TIMEFRAME,
            'gun_sayisi': GUN_SAYISI,
            'toplam_mum': len(sonuc_df),
            'anomali_sayilari': {
                yontem: int((tahmin == -1).sum())
                for yontem, (tahmin, _) in sonuclar.items()
            },
            'toplam_anomali': int((ensemble_tahmin == -1).sum()),
            'fiyat_istatistikleri': stats['price_stats']
        }
        
        # JSON raporunu kaydediyorum
        with open(ozet_rapor, 'w', encoding='utf-8') as f:
            json.dump(rapor, f, indent=2, ensure_ascii=False)
        
        print(f"Ozet rapor: {ozet_rapor.name}")
        
        # Sonuclari ekrana yazdiriyorum
        print(f"\n{'='*70}")
        print("SONUCLAR")
        print("="*70)
        
        if len(anomaliler_df) > 0:
            print(f"\nToplam {len(anomaliler_df)} adet anomali buldum\n")
            
            # Ilk 20 anomaliyi ekrana yazdiriyorum
            # (Hepsini yazdirmiyorum cunku cok uzun olabilir)
            gosterilecek = min(20, len(anomaliler_df))
            print(f"Ilk {gosterilecek} Anomali:\n")
            print(anomaliler_df[['timestamp', 'close', 'ensemble_oy']].head(gosterilecek).to_string(index=False))
            
            if len(anomaliler_df) > 20:
                print(f"\n... ve {len(anomaliler_df) - 20} tane daha var")
            
            # Anomalilerin guvenilirlik dagilimini gosteriyorum
            # Oy sayisi ne kadar yuksekse o kadar guvenilir
            oy_dagilimi = anomaliler_df['ensemble_oy'].value_counts().sort_index(ascending=False)
            print(f"\nGuvenilirlik Dagilimi:")
            print("(Oy sayisi yuksek = daha guvenilir anomali)")
            for oy, sayi in oy_dagilimi.items():
                if oy == 3:
                    print(f"   {int(oy)} oy: {sayi} anomali (3 yontem de anomali dedi)")
                elif oy == 2:
                    print(f"   {int(oy)} oy: {sayi} anomali (2 yontem anomali dedi)")
                else:
                    print(f"   {int(oy)} oy: {sayi} anomali (1 yontem anomali dedi)")
        else:
            print("\nHic anomali bulamadim.")
        
        # Program bitti, ozet bilgileri yazdiriyorum
        print(f"\n{'='*70}")
        print("ISLEM TAMAMLANDI")
        print("="*70)
        
        print(f"\nOzet:")
        print(f"   Cekilen Veri: {len(sonuc_df):,} mum")
        print(f"   Bulunan Anomali: {len(anomaliler_df)} adet")
        print(f"   Anomali Orani: %{(len(anomaliler_df)/len(sonuc_df)*100):.2f}")
        
        print(f"\nOlusturulan Dosyalar:")
        print(f"   results/ klasorunde:")
        print(f"      anomaliler_{zaman_damgasi}.csv  <- EN ONEMLI DOSYA")
        print(f"      tum_veri_{zaman_damgasi}.csv    <- Tum veriler")
        print(f"      ozet_{zaman_damgasi}.json       <- JSON rapor")
        print(f"   data/ klasorunde:")
        print(f"      ham_veri_{zaman_damgasi}.csv    <- Ham veri")
        
        print(f"\n{'='*70}")
        print("Program basariyla tamamlandi!")
        print("="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nIslem kullanici tarafindan iptal edildi.")
        return 1
        
    except Exception as e:
        print(f"\n\nHATA OLUSTU: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


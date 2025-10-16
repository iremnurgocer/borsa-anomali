"""
Veri Isleme Modulu

Borsadan cekilen ham verileri temizleyip, analiz icin hazirliyorum.
Ayrica ekstra ozellikler (fiyat degisimi, volatilite vs.) ekliyorum.
"""

import pandas as pd
import numpy as np
from typing import List, Optional


class DataProcessor:
    """
    Bu sinif veriyi temizliyor ve hazirlıyor
    
    Yaptiklarim:
    - Eksik ve hatali verileri temizliyorum
    - Teknik ozellikler ekliyorum (volatilite, momentum vs.)
    - Anomali tespiti icin veriyi hazirliyorum
    """
    
    def __init__(self, df: pd.DataFrame):
        # Veriyi alip kopyasini olusturuyorum
        self.df = df.copy()
        self._validate_dataframe()
    
    def _validate_dataframe(self):
        """DataFrame'in gerekli sütunlara sahip olduğunu kontrol eder"""
        required_columns = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(f"DataFrame'de eksik sütunlar: {missing_columns}")
        
        if self.df.empty:
            raise ValueError("DataFrame boş!")
    
    def clean_data(self) -> pd.DataFrame:
        """Veriyi temizler"""
        print("Veri temizleniyor...")
        
        initial_rows = len(self.df)
        
        # Eksik değerleri kontrol et
        missing_count = self.df.isnull().sum().sum()
        if missing_count > 0:
            print(f"   {missing_count} eksik deger bulundu, temizleniyor...")
            self.df = self.df.dropna()
        
        # Sıfır veya negatif fiyatları temizle
        invalid_prices = (
            (self.df['open'] <= 0) | 
            (self.df['high'] <= 0) | 
            (self.df['low'] <= 0) | 
            (self.df['close'] <= 0)
        )
        if invalid_prices.any():
            print(f"   {invalid_prices.sum()} gecersiz fiyat bulundu, temizleniyor...")
            self.df = self.df[~invalid_prices]
        
        # Duplicate timestamp'leri kaldır
        duplicates = self.df.duplicated(subset=['timestamp'], keep='first')
        if duplicates.any():
            print(f"   {duplicates.sum()} tekrarlanan timestamp bulundu, temizleniyor...")
            self.df = self.df[~duplicates]
        
        # Index'i sıfırla
        self.df = self.df.reset_index(drop=True)
        
        removed_rows = initial_rows - len(self.df)
        if removed_rows > 0:
            print(f"   {removed_rows} satir temizlendi ({len(self.df)} satir kaldi)")
        else:
            print(f"   Veri temiz ({len(self.df)} satir)")
        
        return self.df
    
    def add_features(self, features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Teknik özellikler ekler
        
        Args:
            features: Eklenecek özellikler listesi
                     None ise tüm özellikler eklenir
        
        Returns:
            DataFrame: Özelliklerle zenginleştirilmiş veri
        """
        print("Teknik ozellikler ekleniyor...")
        
        if features is None:
            features = [
                "price_change",
                "price_pct_change", 
                "volume_change",
                "volatility",
                "price_momentum"
            ]
        
        for feature in features:
            if feature == "price_change":
                # Fiyat değişimi (mutlak)
                self.df['price_change'] = self.df['close'].diff()
            
            elif feature == "price_pct_change":
                # Fiyat değişimi (yüzde)
                self.df['price_pct_change'] = self.df['close'].pct_change() * 100
            
            elif feature == "volume_change":
                # Hacim değişimi (yüzde)
                self.df['volume_change'] = self.df['volume'].pct_change() * 100
            
            elif feature == "volatility":
                # Volatilite (son 20 mumun standart sapması)
                self.df['volatility'] = self.df['close'].rolling(window=20, min_periods=1).std()
            
            elif feature == "price_momentum":
                # Momentum (son 14 mumun fiyat değişimi)
                self.df['price_momentum'] = self.df['close'].diff(14)
            
            elif feature == "high_low_range":
                # Mum aralığı (high - low)
                self.df['high_low_range'] = self.df['high'] - self.df['low']
            
            elif feature == "high_low_pct":
                # Mum aralığı yüzdesi
                self.df['high_low_pct'] = ((self.df['high'] - self.df['low']) / self.df['low']) * 100
            
            elif feature == "body_size":
                # Mum gövde büyüklüğü
                self.df['body_size'] = abs(self.df['close'] - self.df['open'])
            
            elif feature == "upper_shadow":
                # Üst gölge
                self.df['upper_shadow'] = self.df['high'] - self.df[['open', 'close']].max(axis=1)
            
            elif feature == "lower_shadow":
                # Alt gölge
                self.df['lower_shadow'] = self.df[['open', 'close']].min(axis=1) - self.df['low']
        
        # İlk satırlardaki NaN'ları kaldır (rolling/diff işlemlerinden)
        initial_rows = len(self.df)
        self.df = self.df.dropna().reset_index(drop=True)
        
        if initial_rows > len(self.df):
            print(f"   {len(features)} ozellik eklendi ({initial_rows - len(self.df)} NaN satir kaldirildi)")
        else:
            print(f"   {len(features)} ozellik eklendi")
        
        return self.df
    
    def prepare_for_anomaly_detection(
        self, 
        target_column: str = "close",
        additional_columns: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Anomali tespiti için veriyi hazırlar
        
        Args:
            target_column: Ana hedef sütun (genellikle 'close')
            additional_columns: Ek sütunlar (çok boyutlu analiz için)
        
        Returns:
            numpy array: Anomali tespiti için hazır veri
        """
        if target_column not in self.df.columns:
            raise ValueError(f"'{target_column}' sütunu bulunamadı")
        
        if additional_columns:
            # Çok boyutlu analiz
            columns = [target_column] + additional_columns
            missing = [col for col in columns if col not in self.df.columns]
            if missing:
                raise ValueError(f"Eksik sütunlar: {missing}")
            
            X = self.df[columns].values
            print(f"Veri hazirlandi: {X.shape[1]} ozellik, {X.shape[0]} gozlem")
        else:
            # Tek boyutlu analiz
            X = self.df[target_column].values.reshape(-1, 1)
            print(f"Veri hazirlandi: '{target_column}' sutunu, {X.shape[0]} gozlem")
        
        return X
    
    def get_statistics(self) -> dict:
        """Veri hakkında istatistiksel bilgi döner"""
        stats = {
            'total_rows': len(self.df),
            'date_range': {
                'start': str(self.df['timestamp'].min()),
                'end': str(self.df['timestamp'].max()),
                'days': (self.df['timestamp'].max() - self.df['timestamp'].min()).days
            },
            'price_stats': {
                'min': float(self.df['close'].min()),
                'max': float(self.df['close'].max()),
                'mean': float(self.df['close'].mean()),
                'std': float(self.df['close'].std()),
                'range': float(self.df['close'].max() - self.df['close'].min())
            },
            'volume_stats': {
                'min': float(self.df['volume'].min()),
                'max': float(self.df['volume'].max()),
                'mean': float(self.df['volume'].mean()),
                'std': float(self.df['volume'].std())
            }
        }
        
        return stats
    
    def save_data(self, filepath: str, format: str = "csv"):
        """
        Veriyi kaydeder
        
        Args:
            filepath: Dosya yolu
            format: Dosya formatı ('csv' veya 'json')
        """
        if format == "csv":
            self.df.to_csv(filepath, index=False)
        elif format == "json":
            self.df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError(f"Desteklenmeyen format: {format}")
        
        print(f"Veri kaydedildi: {filepath}")


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher("binance")
    df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=7)
    
    processor = DataProcessor(df)
    processor.clean_data()
    processor.add_features()
    
    print("\nVeri İstatistikleri:")
    import json
    print(json.dumps(processor.get_statistics(), indent=2))
    
    X = processor.prepare_for_anomaly_detection("close")
    print(f"\nHazırlanan veri şekli: {X.shape}")


"""
Anomali Tespit Modulu

Bu modulu fiyat verilerinden anormal hareketleri tespit etmek icin yazdim.
3 farkli yontem kullaniyorum:
1. Isolation Forest (makine ogrenmesi)
2. Z-Score (istatistiksel)
3. IQR (ceyrekler arasi aralik)

En guvenilir sonucu almak icin bu yontemleri birlestiriyorum.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Anomali tespit sinifi
    
    contamination parametresi: Veride ne kadar anomali beklendigini belirliyor
    Ornegin 0.05 = %5 anomali bekliyorum demek
    """
    
    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        # Parametreleri ayarliyorum
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.scaler = StandardScaler()
        
    def detect_isolation_forest(self, X: np.ndarray) -> np.ndarray:
        """
        Isolation Forest yöntemi ile anomali tespiti
        
        Args:
            X: Veri matrisi (n_samples, n_features)
            
        Returns:
            numpy array: Anomali etiketleri (1: normal, -1: anomali)
        """
        print(f"Isolation Forest ile tespit ediliyor...")
        
        # Veriyi normalize et
        X_scaled = self.scaler.fit_transform(X)
        
        # Model oluştur ve eğit
        model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1  # Tüm CPU çekirdeklerini kullan
        )
        
        predictions = model.fit_predict(X_scaled)
        
        # Anomali skorlarını al
        anomaly_scores = model.score_samples(X_scaled)
        
        anomaly_count = np.sum(predictions == -1)
        print(f"   {anomaly_count} anomali tespit edildi (%{(anomaly_count/len(X)*100):.2f})")
        
        return predictions, anomaly_scores
    
    def detect_z_score(
        self, 
        X: np.ndarray, 
        threshold: float = 3.0
    ) -> np.ndarray:
        """
        Z-Score yöntemi ile anomali tespiti
        
        Args:
            X: Veri matrisi
            threshold: Z-score eşik değeri (genellikle 2-3 arası)
            
        Returns:
            numpy array: Anomali etiketleri (1: normal, -1: anomali)
        """
        print(f"Z-Score yontemi ile tespit ediliyor (threshold={threshold})...")
        
        # Her özellik için z-score hesapla
        z_scores = np.abs((X - np.mean(X, axis=0)) / np.std(X, axis=0))
        
        # Herhangi bir özellikte threshold'u aşanları anomali olarak işaretle
        predictions = np.ones(len(X), dtype=int)
        anomalies = np.any(z_scores > threshold, axis=1)
        predictions[anomalies] = -1
        
        anomaly_count = np.sum(predictions == -1)
        print(f"   {anomaly_count} anomali tespit edildi (%{(anomaly_count/len(X)*100):.2f})")
        
        return predictions, z_scores.max(axis=1)
    
    def detect_iqr(
        self, 
        X: np.ndarray, 
        multiplier: float = 1.5
    ) -> np.ndarray:
        """
        IQR (Interquartile Range) yöntemi ile anomali tespiti
        
        Args:
            X: Veri matrisi
            multiplier: IQR çarpanı (1.5: outlier, 3.0: extreme outlier)
            
        Returns:
            numpy array: Anomali etiketleri (1: normal, -1: anomali)
        """
        print(f"IQR yontemi ile tespit ediliyor (multiplier={multiplier})...")
        
        predictions = np.ones(len(X), dtype=int)
        scores = np.zeros(len(X))
        
        # Her özellik için IQR hesapla
        for feature_idx in range(X.shape[1]):
            feature_data = X[:, feature_idx]
            
            Q1 = np.percentile(feature_data, 25)
            Q3 = np.percentile(feature_data, 75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            # Alt veya üst sınırın dışındakiler anomali
            outliers = (feature_data < lower_bound) | (feature_data > upper_bound)
            predictions[outliers] = -1
            
            # Score hesapla (sınırlardan ne kadar uzak)
            distances = np.where(
                feature_data < lower_bound,
                lower_bound - feature_data,
                np.where(
                    feature_data > upper_bound,
                    feature_data - upper_bound,
                    0
                )
            )
            scores = np.maximum(scores, distances / IQR)
        
        anomaly_count = np.sum(predictions == -1)
        print(f"   {anomaly_count} anomali tespit edildi (%{(anomaly_count/len(X)*100):.2f})")
        
        return predictions, scores
    
    def detect_moving_average(
        self,
        data: np.ndarray,
        window: int = 20,
        threshold: float = 2.0
    ) -> np.ndarray:
        """
        Hareketli ortalama sapması ile anomali tespiti
        
        Args:
            data: 1D veri dizisi
            window: Hareketli ortalama pencere boyutu
            threshold: Standart sapma çarpanı
            
        Returns:
            numpy array: Anomali etiketleri
        """
        print(f"Moving Average yontemi ile tespit ediliyor (window={window})...")
        
        if data.ndim > 1:
            data = data.flatten()
        
        # Hareketli ortalama ve standart sapma
        rolling_mean = pd.Series(data).rolling(window=window, min_periods=1).mean().values
        rolling_std = pd.Series(data).rolling(window=window, min_periods=1).std().values
        
        # Sapma hesapla
        deviations = np.abs(data - rolling_mean) / (rolling_std + 1e-8)
        
        # Threshold'u aşanlar anomali
        predictions = np.ones(len(data), dtype=int)
        predictions[deviations > threshold] = -1
        
        anomaly_count = np.sum(predictions == -1)
        print(f"   ✓ {anomaly_count} anomali tespit edildi (%{(anomaly_count/len(data)*100):.2f})")
        
        return predictions, deviations
    
    def detect_all_methods(
        self,
        X: np.ndarray,
        methods: Optional[List[str]] = None,
        z_score_threshold: float = 3.0,
        iqr_multiplier: float = 1.5
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Tüm yöntemlerle anomali tespiti yapar
        
        Args:
            X: Veri matrisi
            methods: Kullanılacak yöntemler listesi
            z_score_threshold: Z-score eşiği
            iqr_multiplier: IQR çarpanı
            
        Returns:
            dict: Her yöntem için (predictions, scores) tuple'ı
        """
        if methods is None:
            methods = ["isolation_forest", "z_score", "iqr"]
        
        results = {}
        
        print(f"\n{'='*60}")
        print(f"ANOMALI TESPITI BASLIYOR - {len(methods)} yontem")
        print(f"{'='*60}\n")
        
        if "isolation_forest" in methods:
            pred, scores = self.detect_isolation_forest(X)
            results["isolation_forest"] = (pred, scores)
        
        if "z_score" in methods:
            pred, scores = self.detect_z_score(X, threshold=z_score_threshold)
            results["z_score"] = (pred, scores)
        
        if "iqr" in methods:
            pred, scores = self.detect_iqr(X, multiplier=iqr_multiplier)
            results["iqr"] = (pred, scores)
        
        if "moving_average" in methods:
            pred, scores = self.detect_moving_average(X)
            results["moving_average"] = (pred, scores)
        
        print(f"\n{'='*60}")
        print("TUM YONTEMLER TAMAMLANDI")
        print(f"{'='*60}\n")
        
        return results
    
    def ensemble_voting(
        self,
        results: Dict[str, Tuple[np.ndarray, np.ndarray]],
        min_votes: int = 2
    ) -> np.ndarray:
        """
        Çoklu yöntem sonuçlarını birleştirerek oylama yapar
        
        Args:
            results: detect_all_methods() sonuçları
            min_votes: Anomali olması için minimum oy sayısı
            
        Returns:
            numpy array: Birleştirilmiş anomali etiketleri
        """
        print(f"Ensemble Voting yapiliyor (min_votes={min_votes})...")
        
        # Her satır için oylama
        n_samples = len(next(iter(results.values()))[0])
        votes = np.zeros(n_samples)
        
        for method_name, (predictions, _) in results.items():
            # -1 (anomali) oyları say
            votes += (predictions == -1).astype(int)
        
        # Minimum oy sayısına göre karar ver
        ensemble_predictions = np.where(votes >= min_votes, -1, 1)
        
        anomaly_count = np.sum(ensemble_predictions == -1)
        print(f"   Ensemble: {anomaly_count} anomali tespit edildi")
        print(f"   Yontem basina anomali sayilari:")
        for method_name, (predictions, _) in results.items():
            count = np.sum(predictions == -1)
            print(f"      - {method_name}: {count}")
        
        return ensemble_predictions, votes


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    from data_processor import DataProcessor
    
    fetcher = DataFetcher("binance")
    df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=7)
    
    processor = DataProcessor(df)
    processor.clean_data()
    processor.add_features()
    
    X = processor.prepare_for_anomaly_detection("close")
    
    detector = AnomalyDetector(contamination=0.05)
    results = detector.detect_all_methods(X)
    
    ensemble_pred, votes = detector.ensemble_voting(results, min_votes=2)
    
    print(f"\n✓ Test başarılı!")


"""
Görselleştirme Modülü
Anomali tespit sonuçlarını görselleştirir
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Optional
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Türkçe karakter desteği ve stil
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")


class AnomalyVisualizer:
    """Anomali tespit sonuçlarını görselleştiren sınıf"""
    
    def __init__(self, df: pd.DataFrame, figsize: Tuple[int, int] = (15, 10)):
        """
        Args:
            df: Veri DataFrame'i (timestamp ve close sütunları gerekli)
            figsize: Grafik boyutu
        """
        self.df = df.copy()
        self.figsize = figsize
        
    def plot_price_with_anomalies(
        self,
        anomaly_predictions: np.ndarray,
        method_name: str = "Anomali Tespiti",
        save_path: Optional[str] = None
    ):
        """
        Fiyat grafiğinde anomalileri gösterir
        
        Args:
            anomaly_predictions: Anomali etiketleri (-1: anomali, 1: normal)
            method_name: Yöntem adı (grafik başlığı için)
            save_path: Kaydedilecek dosya yolu (opsiyonel)
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Normal veriler
        normal_mask = anomaly_predictions == 1
        anomaly_mask = anomaly_predictions == -1
        
        # Fiyat çizgisi
        ax.plot(
            self.df.loc[normal_mask, 'timestamp'],
            self.df.loc[normal_mask, 'close'],
            'b-',
            label='Normal',
            linewidth=1.5,
            alpha=0.7
        )
        
        # Anomaliler
        ax.scatter(
            self.df.loc[anomaly_mask, 'timestamp'],
            self.df.loc[anomaly_mask, 'close'],
            color='red',
            s=100,
            marker='o',
            label='Anomali',
            zorder=5,
            edgecolors='darkred',
            linewidths=2
        )
        
        ax.set_xlabel('Zaman', fontsize=12, fontweight='bold')
        ax.set_ylabel('Fiyat (Close)', fontsize=12, fontweight='bold')
        ax.set_title(f'{method_name} - Fiyat ve Anomaliler', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   💾 Grafik kaydedildi: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_multiple_methods(
        self,
        results: Dict[str, Tuple[np.ndarray, np.ndarray]],
        ensemble_predictions: Optional[np.ndarray] = None,
        save_path: Optional[str] = None
    ):
        """
        Çoklu yöntem sonuçlarını karşılaştırmalı gösterir
        
        Args:
            results: Her yöntem için (predictions, scores) içeren dict
            ensemble_predictions: Ensemble sonuçları (opsiyonel)
            save_path: Kaydedilecek dosya yolu (opsiyonel)
        """
        n_methods = len(results) + (1 if ensemble_predictions is not None else 0)
        fig, axes = plt.subplots(n_methods, 1, figsize=(15, 5 * n_methods))
        
        if n_methods == 1:
            axes = [axes]
        
        # Her yöntem için subplot
        for idx, (method_name, (predictions, scores)) in enumerate(results.items()):
            ax = axes[idx]
            
            normal_mask = predictions == 1
            anomaly_mask = predictions == -1
            
            # Fiyat çizgisi
            ax.plot(
                self.df.loc[normal_mask, 'timestamp'],
                self.df.loc[normal_mask, 'close'],
                'b-',
                linewidth=1.5,
                alpha=0.7,
                label='Normal'
            )
            
            # Anomaliler
            ax.scatter(
                self.df.loc[anomaly_mask, 'timestamp'],
                self.df.loc[anomaly_mask, 'close'],
                color='red',
                s=80,
                marker='o',
                label=f'Anomali ({np.sum(anomaly_mask)})',
                zorder=5,
                edgecolors='darkred',
                linewidths=1.5
            )
            
            ax.set_ylabel('Fiyat', fontsize=11, fontweight='bold')
            ax.set_title(f'{method_name.upper()}', fontsize=12, fontweight='bold')
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Ensemble sonuçları varsa
        if ensemble_predictions is not None:
            ax = axes[-1]
            
            normal_mask = ensemble_predictions == 1
            anomaly_mask = ensemble_predictions == -1
            
            ax.plot(
                self.df.loc[normal_mask, 'timestamp'],
                self.df.loc[normal_mask, 'close'],
                'g-',
                linewidth=1.5,
                alpha=0.7,
                label='Normal'
            )
            
            ax.scatter(
                self.df.loc[anomaly_mask, 'timestamp'],
                self.df.loc[anomaly_mask, 'close'],
                color='darkred',
                s=100,
                marker='*',
                label=f'Anomali ({np.sum(anomaly_mask)})',
                zorder=5,
                edgecolors='black',
                linewidths=2
            )
            
            ax.set_xlabel('Zaman', fontsize=11, fontweight='bold')
            ax.set_ylabel('Fiyat', fontsize=11, fontweight='bold')
            ax.set_title('ENSEMBLE VOTING (Birleşik Sonuç)', fontsize=12, fontweight='bold')
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   💾 Karşılaştırma grafiği kaydedildi: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_anomaly_scores(
        self,
        results: Dict[str, Tuple[np.ndarray, np.ndarray]],
        save_path: Optional[str] = None
    ):
        """
        Anomali skorlarını gösterir
        
        Args:
            results: Her yöntem için (predictions, scores) içeren dict
            save_path: Kaydedilecek dosya yolu (opsiyonel)
        """
        n_methods = len(results)
        fig, axes = plt.subplots(n_methods, 1, figsize=(15, 4 * n_methods))
        
        if n_methods == 1:
            axes = [axes]
        
        for idx, (method_name, (predictions, scores)) in enumerate(results.items()):
            ax = axes[idx]
            
            # Skorları çiz
            ax.plot(
                self.df['timestamp'],
                scores,
                'b-',
                linewidth=1,
                alpha=0.6,
                label='Anomali Skoru'
            )
            
            # Anomalileri işaretle
            anomaly_mask = predictions == -1
            ax.scatter(
                self.df.loc[anomaly_mask, 'timestamp'],
                scores[anomaly_mask],
                color='red',
                s=50,
                marker='o',
                label='Tespit Edilen Anomaliler',
                zorder=5
            )
            
            ax.set_ylabel('Skor', fontsize=11, fontweight='bold')
            ax.set_title(f'{method_name.upper()} - Anomali Skorları', fontsize=12, fontweight='bold')
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        axes[-1].set_xlabel('Zaman', fontsize=11, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   💾 Skor grafiği kaydedildi: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_statistics(
        self,
        results: Dict[str, Tuple[np.ndarray, np.ndarray]],
        ensemble_predictions: Optional[np.ndarray] = None,
        save_path: Optional[str] = None
    ):
        """
        İstatistiksel özet grafiği
        
        Args:
            results: Her yöntem için (predictions, scores) içeren dict
            ensemble_predictions: Ensemble sonuçları (opsiyonel)
            save_path: Kaydedilecek dosya yolu (opsiyonel)
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Yöntem başına anomali sayısı
        method_names = list(results.keys())
        anomaly_counts = [np.sum(pred == -1) for pred, _ in results.values()]
        
        if ensemble_predictions is not None:
            method_names.append('Ensemble')
            anomaly_counts.append(np.sum(ensemble_predictions == -1))
        
        axes[0].bar(method_names, anomaly_counts, color='steelblue', edgecolor='black')
        axes[0].set_ylabel('Anomali Sayısı', fontsize=12, fontweight='bold')
        axes[0].set_title('Yöntemlere Göre Anomali Sayıları', fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45)
        
        # Değerler üzerine sayıları yaz
        for i, count in enumerate(anomaly_counts):
            axes[0].text(i, count + max(anomaly_counts)*0.02, str(count), 
                        ha='center', va='bottom', fontweight='bold')
        
        # Yöntem başına anomali yüzdesi
        total_samples = len(self.df)
        anomaly_percentages = [(count / total_samples) * 100 for count in anomaly_counts]
        
        axes[1].bar(method_names, anomaly_percentages, color='coral', edgecolor='black')
        axes[1].set_ylabel('Anomali Yüzdesi (%)', fontsize=12, fontweight='bold')
        axes[1].set_title('Yöntemlere Göre Anomali Yüzdeleri', fontsize=13, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
        
        # Değerler üzerine yüzdeleri yaz
        for i, pct in enumerate(anomaly_percentages):
            axes[1].text(i, pct + max(anomaly_percentages)*0.02, f'{pct:.2f}%', 
                        ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   💾 İstatistik grafiği kaydedildi: {save_path}")
        
        plt.show()
        plt.close()


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    from data_processor import DataProcessor
    from anomaly_detector import AnomalyDetector
    
    fetcher = DataFetcher("binance")
    df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=7)
    
    processor = DataProcessor(df)
    processor.clean_data()
    processor.add_features()
    
    X = processor.prepare_for_anomaly_detection("close")
    
    detector = AnomalyDetector(contamination=0.05)
    results = detector.detect_all_methods(X)
    ensemble_pred, votes = detector.ensemble_voting(results, min_votes=2)
    
    visualizer = AnomalyVisualizer(processor.df)
    visualizer.plot_multiple_methods(results, ensemble_pred)
    visualizer.plot_statistics(results, ensemble_pred)


"""
Borsa Veri Cekme Modulu

Bu modulu borsalardan veri cekmek icin yazdim.
CCXT kutuphanesi sayesinde 100+ farkli borsadan veri cekebiliyor.
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time


class DataFetcher:
    """
    Bu sinif borsalardan veri cekmeyi sagliyor
    
    Nasil kullanilir:
        fetcher = DataFetcher("binance")
        df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=60)
    """
    
    def __init__(self, exchange_name: str = "binance", api_key: str = "", api_secret: str = ""):
        # Borsa baglantisini olusturuyorum
        # API key zorunlu degil, public veriler icin gerekmiyor
        self.exchange_name = exchange_name.lower()
        self.exchange = self._initialize_exchange(api_key, api_secret)
        
    def _initialize_exchange(self, api_key: str, api_secret: str) -> ccxt.Exchange:
        # Secilen borsaya baglaniyorum
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            config = {
                'enableRateLimit': True,  # Rate limiting koruması
                'timeout': 30000,
            }
            
            if api_key and api_secret:
                config['apiKey'] = api_key
                config['secret'] = api_secret
                
            exchange = exchange_class(config)
            print(f"{self.exchange_name.upper()} borsasina baglandi")
            return exchange
            
        except AttributeError:
            available_exchanges = ", ".join(ccxt.exchanges[:10])
            raise ValueError(
                f"'{self.exchange_name}' borsası desteklenmiyor. "
                f"Mevcut borsalar: {available_exchanges}..."
            )
        except Exception as e:
            raise ConnectionError(f"Borsaya bağlanırken hata: {e}")
    
    def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = "15m", 
        days_back: int = 60,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        OHLCV (Open, High, Low, Close, Volume) verilerini çeker
        
        Args:
            symbol: Trading çifti (örn: BTC/USDT)
            timeframe: Zaman dilimi (1m, 5m, 15m, 1h, 4h, 1d)
            days_back: Kaç gün öncesinden başlasın
            limit: Maksimum kayıt sayısı
            
        Returns:
            DataFrame: OHLCV verileri
        """
        try:
            # Sembolün mevcut olup olmadığını kontrol et
            self.exchange.load_markets()
            if symbol not in self.exchange.symbols:
                raise ValueError(f"'{symbol}' sembolü {self.exchange_name}'de bulunamadı")
            
            # Zaman aralığını hesapla
            since = self._calculate_since_timestamp(days_back)
            
            print(f"Veri cekiliyor: {symbol} ({timeframe}) - Son {days_back} gun")
            print(f"   Baslangic: {datetime.fromtimestamp(since/1000)}")
            
            # Veriyi çek (büyük veri setleri için parça parça)
            all_ohlcv = []
            current_since = since
            
            while True:
                # Batch olarak çek
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=current_since,
                    limit=1000  # Çoğu borsa max 1000 kayıt döner
                )
                
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                
                # Son zaman damgasını al
                last_timestamp = ohlcv[-1][0]
                
                # Limit kontrolü
                if limit and len(all_ohlcv) >= limit:
                    all_ohlcv = all_ohlcv[:limit]
                    break
                
                # Eğer güncel zamana ulaştıysak dur
                if last_timestamp >= int(time.time() * 1000):
                    break
                
                # Sonraki batch için timestamp'i güncelle
                current_since = last_timestamp + 1
                
                # Rate limit koruması
                time.sleep(self.exchange.rateLimit / 1000)
            
            # DataFrame'e çevir
            df = self._ohlcv_to_dataframe(all_ohlcv)
            
            print(f"{len(df)} adet veri cekildi")
            print(f"   Tarih araligi: {df['timestamp'].min()} - {df['timestamp'].max()}")
            
            return df
            
        except ccxt.NetworkError as e:
            raise ConnectionError(f"Ağ hatası: {e}")
        except ccxt.ExchangeError as e:
            raise ValueError(f"Borsa hatası: {e}")
        except Exception as e:
            raise Exception(f"Veri çekerken hata: {e}")
    
    def _calculate_since_timestamp(self, days_back: int) -> int:
        """Kaç gün öncesinin timestamp'ini hesaplar"""
        since_date = datetime.now() - timedelta(days=days_back)
        return int(since_date.timestamp() * 1000)
    
    def _ohlcv_to_dataframe(self, ohlcv_data: list) -> pd.DataFrame:
        """OHLCV listesini DataFrame'e çevirir"""
        df = pd.DataFrame(
            ohlcv_data,
            columns=['timestamp_ms', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Timestamp'i datetime'a çevir
        df['timestamp'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
        
        # Sırala ve index'i sıfırla
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def get_available_symbols(self, quote_currency: str = "USDT") -> list:
        """
        Borsada mevcut sembolleri listeler
        
        Args:
            quote_currency: Karşı para birimi (USDT, BTC, EUR, etc.)
            
        Returns:
            list: Sembol listesi
        """
        self.exchange.load_markets()
        symbols = [s for s in self.exchange.symbols if quote_currency in s]
        return sorted(symbols)
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Borsa hakkında bilgi döner"""
        return {
            'name': self.exchange.name,
            'id': self.exchange.id,
            'has_ohlcv': self.exchange.has['fetchOHLCV'],
            'timeframes': list(self.exchange.timeframes.keys()) if self.exchange.has['fetchOHLCV'] else [],
            'rate_limit': self.exchange.rateLimit,
        }


if __name__ == "__main__":
    # Test
    fetcher = DataFetcher("binance")
    print(f"\nBorsa bilgisi: {fetcher.get_exchange_info()}")
    
    # Örnek veri çekme
    df = fetcher.fetch_ohlcv("BTC/USDT", "15m", days_back=7)
    print(f"\nÇekilen veri özeti:")
    print(df.head())
    print(f"\nVeri şekli: {df.shape}")


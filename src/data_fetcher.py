"""Data fetcher module for retrieving market data from Alpaca.

Provides clean interface for fetching historical and real-time
BTC/USD price data.
"""
from typing import List, Optional
import pandas as pd
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

from config.settings import Config


class AlpacaDataFetcher:
    """Client for fetching cryptocurrency data from Alpaca.
    
    Handles authentication and provides methods for fetching
    historical bars and real-time quotes.
    """
    
    def __init__(self, config: Config):
        """Initialize data fetcher with configuration.
        
        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        self._client: Optional[CryptoHistoricalDataClient] = None
    
    def _get_client(self) -> CryptoHistoricalDataClient:
        """Get or create Alpaca data client (lazy initialization).
        
        Returns:
            Configured CryptoHistoricalDataClient instance
        """
        if self._client is None:
            self._client = CryptoHistoricalDataClient(
                api_key=self.config.api_key,
                secret_key=self.config.api_secret
            )
        return self._client
    
    def get_historical_bars(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.Minute,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Fetch historical price bars for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            timeframe: Bar timeframe (default 1 minute)
            limit: Number of bars to fetch (max 10000)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            client = self._get_client()
            
            end = datetime.now()
            start = end - timedelta(minutes=limit + 5)
            
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            bars = client.get_crypto_bars(request)
            
            if bars is None or bars.df is None or bars.df.empty:
                return None
            
            return bars.df
            
        except Exception as e:
            print(f"Error fetching historical bars: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            
        Returns:
            Latest price or None if error
        """
        bars = self.get_historical_bars(symbol, limit=1)
        
        if bars is None or bars.empty:
            return None
        
        return float(bars['close'].iloc[-1])


def extract_closes(bars: Optional[pd.DataFrame]) -> List[float]:
    """Extract closing prices from bars DataFrame.
    
    Args:
        bars: DataFrame with OHLCV data from Alpaca
        
    Returns:
        List of closing prices (oldest to newest)
    """
    if bars is None or bars.empty or 'close' not in bars.columns:
        return []
    
    return bars['close'].tolist()

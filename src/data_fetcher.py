"""Data fetcher module for retrieving market data from Alpaca.

Provides clean interface for fetching historical and real-time
BTC/USD price data.
"""
from typing import List, Optional
import pandas as pd
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoLatestQuoteRequest
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
        timeframe: TimeFrame = TimeFrame.Hour,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Fetch historical price bars for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            timeframe: Bar timeframe (default 1 hour for crypto)
            limit: Number of bars to fetch (max 10000)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            client = self._get_client()
            
            end = datetime.now()
            # For crypto, use longer time range to ensure we get data
            if timeframe == TimeFrame.Minute:
                start = end - timedelta(minutes=limit * 2)
            elif timeframe == TimeFrame.Hour:
                start = end - timedelta(hours=limit * 2)
            else:
                start = end - timedelta(days=limit)
            
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            bars = client.get_crypto_bars(request)
            
            if bars is None or bars.df is None or bars.df.empty:
                print(f"Warning: No data returned for {symbol}")
                return None
            
            return bars.df
            
        except Exception as e:
            print(f"Error fetching historical bars: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol using real-time quote.
        
        Uses the latest quote endpoint for most current price data,
        falling back to historical bars if not available.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            
        Returns:
            Latest price or None if error
        """
        try:
            client = self._get_client()
            
            # Try to get latest quote (real-time data)
            request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = client.get_crypto_latest_quote(request)
            
            if quotes and symbol in quotes:
                quote = quotes[symbol]
                # Use mid price between bid and ask
                if hasattr(quote, 'bid_price') and hasattr(quote, 'ask_price'):
                    mid_price = (quote.bid_price + quote.ask_price) / 2
                    return float(mid_price)
                elif hasattr(quote, 'price'):
                    return float(quote.price)
            
            # Fallback to historical bars if quote not available
            bars = self.get_historical_bars(symbol, limit=1)
            if bars is not None and not bars.empty:
                return float(bars['close'].iloc[-1])
            
            return None
            
        except Exception as e:
            print(f"Error fetching latest price: {e}")
            # Fallback to historical bars
            try:
                bars = self.get_historical_bars(symbol, limit=1)
                if bars is not None and not bars.empty:
                    return float(bars['close'].iloc[-1])
            except:
                pass
            return None


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

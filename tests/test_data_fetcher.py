"""Tests for data fetcher module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd


class TestDataFetcher:
    """Test Alpaca data fetcher functionality."""

    def test_fetcher_initializes_with_config(self):
        """Test that fetcher initializes with config object."""
        from src.data_fetcher import AlpacaDataFetcher
        from config.settings import Config
        
        config = Config(
            api_key="test_key",
            api_secret="test_secret",
            paper_mode=True
        )
        
        fetcher = AlpacaDataFetcher(config)
        
        assert fetcher.config == config

    @patch("src.data_fetcher.CryptoHistoricalDataClient")
    def test_get_historical_bars_calls_api(self, mock_client_class):
        """Test that get_historical_bars makes API call with correct parameters."""
        from src.data_fetcher import AlpacaDataFetcher
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_crypto_bars.return_value.df = pd.DataFrame({
            'open': [100.0, 101.0],
            'high': [102.0, 103.0],
            'low': [99.0, 100.0],
            'close': [101.0, 102.0],
            'volume': [1000, 1100]
        })
        
        config = Config(api_key="test", api_secret="test", paper_mode=True)
        fetcher = AlpacaDataFetcher(config)
        
        bars = fetcher.get_historical_bars("BTC/USD", limit=100)
        
        mock_client.get_crypto_bars.assert_called_once()
        assert bars is not None
        assert len(bars) == 2

    def test_extract_closes_returns_price_list(self):
        """Test that extract_closes returns list of closing prices."""
        from src.data_fetcher import extract_closes
        
        mock_bars = pd.DataFrame({
            'close': [100.0, 101.0, 102.0, 103.0, 104.0]
        })
        
        closes = extract_closes(mock_bars)
        
        assert closes == [100.0, 101.0, 102.0, 103.0, 104.0]

    def test_extract_closes_handles_empty_data(self):
        """Test that extract_closes handles empty DataFrame."""
        from src.data_fetcher import extract_closes
        
        empty_bars = pd.DataFrame()
        
        closes = extract_closes(empty_bars)
        
        assert closes == []

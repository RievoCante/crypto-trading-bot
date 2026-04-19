"""Tests for main trading bot orchestrator."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys


class TestTradingBot:
    """Test main trading bot functionality."""

    def test_bot_initializes_components(self):
        """Test bot initializes all required components."""
        # Clear cached imports to ensure proper isolation
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
            
        with patch("src.data_fetcher.AlpacaDataFetcher") as mock_fetcher, \
             patch("src.trade_engine.TradeEngine") as mock_engine, \
             patch("src.paper_trader.PaperTrader") as mock_trader:
            
            from src.main import TradingBot
            from config.settings import Config
            
            config = Config(
                api_key="test",
                api_secret="test",
                paper_mode=True,
                btc_symbol="BTC/USD"
            )
            
            bot = TradingBot(config)
            
            assert bot.config == config
            assert bot.data_fetcher is not None
            assert bot.trade_engine is not None
            
            # Clean up
            if 'src.main' in sys.modules:
                del sys.modules['src.main']

    def test_run_single_cycle(self):
        """Test running a single trading cycle."""
        # Clear cached imports to ensure proper isolation
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
            
        with patch("src.data_fetcher.AlpacaDataFetcher") as mock_fetcher_class, \
             patch("src.trade_engine.TradeEngine") as mock_engine_class, \
             patch("src.paper_trader.PaperTrader") as mock_trader_class:
            
            from src.main import TradingBot
            from config.settings import Config
            
            # Setup mock instances
            mock_fetcher_instance = MagicMock()
            mock_fetcher_instance.get_historical_bars.return_value = pd.DataFrame({
                'close': list(range(100, 150))
            })
            mock_fetcher_class.return_value = mock_fetcher_instance
            
            mock_engine_instance = MagicMock()
            mock_engine_instance.process_signal.return_value = {
                'symbol': 'BTC/USD',
                'qty': 0.25,
                'side': 'buy',
                'type': 'market'
            }
            mock_engine_class.return_value = mock_engine_instance
            
            mock_trader_instance = MagicMock()
            mock_trader_instance.execute_order.return_value = True
            mock_trader_instance.btc_position = 0.0
            mock_trader_instance.get_portfolio_value.return_value = 50000.0
            mock_trader_class.return_value = mock_trader_instance
            
            config = Config(
                api_key="test",
                api_secret="test",
                paper_mode=True,
                trading_interval_minutes=5
            )
            
            bot = TradingBot(config)
            
            # Run one cycle
            bot._run_cycle()
            
            # Verify data was fetched
            mock_fetcher_instance.get_historical_bars.assert_called_once()
            # Verify signal was processed
            mock_engine_instance.process_signal.assert_called_once()
            # Verify order was executed
            mock_trader_instance.execute_order.assert_called_once()
            
            # Clean up
            if 'src.main' in sys.modules:
                del sys.modules['src.main']

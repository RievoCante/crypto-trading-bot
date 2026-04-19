"""Integration tests for the trading bot."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys


class TestFullTradingCycle:
    """Integration test: full trading cycle with all components."""

    def test_paper_trading_cycle_with_buy_signal(self):
        """Test complete paper trading cycle that generates a buy signal."""
        # Clear cached imports
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
        if 'src.strategy' in sys.modules:
            del sys.modules['src.strategy']
            
        with patch("src.data_fetcher.AlpacaDataFetcher") as mock_fetcher, \
             patch("src.trade_engine.TradeEngine") as mock_engine, \
             patch("src.paper_trader.PaperTrader") as mock_trader, \
             patch("src.strategy.calculate_rsi") as mock_rsi, \
             patch("src.strategy.detect_macd_crossover") as mock_macd:
            
            from src.main import TradingBot
            from config.settings import Config
            
            # Setup: Oversold RSI + Bullish MACD = BUY signal
            mock_rsi.return_value = 25.0
            mock_macd.return_value = "bullish"
            
            mock_fetcher_instance = MagicMock()
            mock_fetcher_instance.get_historical_bars.return_value = pd.DataFrame({
                'close': list(range(100, 150))
            })
            mock_fetcher_instance.get_latest_price.return_value = 40000.0
            mock_fetcher.return_value = mock_fetcher_instance
            
            mock_engine_instance = MagicMock()
            mock_engine_instance.process_signal.return_value = {
                'symbol': 'BTC/USD',
                'qty': 0.25,
                'side': 'buy',
                'type': 'market'
            }
            mock_engine.return_value = mock_engine_instance
            
            mock_trader_instance = MagicMock()
            mock_trader_instance.execute_order.return_value = True
            mock_trader_instance.btc_position = 0.0
            mock_trader_instance.get_portfolio_value.return_value = 100000.0
            mock_trader.return_value = mock_trader_instance
            
            config = Config(
                api_key="test",
                api_secret="test",
                paper_mode=True
            )
            
            bot = TradingBot(config)
            bot.trader = mock_trader_instance
            
            bot._run_cycle()
            
            mock_fetcher_instance.get_historical_bars.assert_called_once()
            mock_engine_instance.process_signal.assert_called_once()
            mock_trader_instance.execute_order.assert_called_once()
            
            # Clean up
            if 'src.main' in sys.modules:
                del sys.modules['src.main']
            if 'src.strategy' in sys.modules:
                del sys.modules['src.strategy']


class TestRiskManagementIntegration:
    """Integration tests for risk management."""

    def test_daily_loss_limit_blocks_trading(self):
        """Test that trading is blocked when daily loss limit is exceeded."""
        # Clear cached imports
        if 'src.main' in sys.modules:
            del sys.modules['src.main']
        if 'src.strategy' in sys.modules:
            del sys.modules['src.strategy']
            
        with patch("src.data_fetcher.AlpacaDataFetcher") as mock_fetcher, \
             patch("src.trade_engine.TradeEngine") as mock_engine, \
             patch("src.paper_trader.PaperTrader") as mock_trader, \
             patch("src.strategy.calculate_rsi") as mock_rsi:
            
            from src.main import TradingBot
            from config.settings import Config
            
            mock_rsi.return_value = 50.0
            
            mock_fetcher_instance = MagicMock()
            mock_fetcher_instance.get_historical_bars.return_value = pd.DataFrame({
                'close': list(range(100, 150))
            })
            mock_fetcher.return_value = mock_fetcher_instance
            
            mock_engine_instance = MagicMock()
            mock_engine_instance.process_signal.return_value = None
            mock_engine.return_value = mock_engine_instance
            
            mock_trader_instance = MagicMock()
            mock_trader_instance.get_portfolio_value.return_value = 95000.0
            mock_trader.return_value = mock_trader_instance
            
            config = Config(
                api_key="test",
                api_secret="test",
                paper_mode=True,
                daily_loss_limit_pct=0.05
            )
            
            bot = TradingBot(config)
            bot.trader = mock_trader_instance
            bot.starting_portfolio_value = 100000.0
            
            bot._run_cycle()
            
            mock_trader_instance.execute_order.assert_not_called()
            
            # Clean up
            if 'src.main' in sys.modules:
                del sys.modules['src.main']
            if 'src.strategy' in sys.modules:
                del sys.modules['src.strategy']

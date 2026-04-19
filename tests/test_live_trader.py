"""Tests for live trader module."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLiveTrader:
    """Test live trading executor."""

    @patch("src.live_trader.TradingClient")
    def test_trader_initializes_with_config(self, mock_client_class):
        """Test live trader initializes with config."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        config = Config(
            api_key="live_key",
            api_secret="live_secret",
            paper_mode=False
        )
        
        trader = LiveTrader(config)
        
        assert trader.config == config

    @patch("src.live_trader.TradingClient")
    def test_execute_buy_order(self, mock_client_class):
        """Test executing a buy order via Alpaca API."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_order = MagicMock()
        mock_order.id = "order-123"
        mock_order.symbol = "BTC/USD"
        mock_order.qty = "0.5"
        mock_order.side.value = "buy"
        mock_order.type.value = "market"
        mock_order.status.value = "new"
        mock_order.created_at = None
        mock_client.submit_order.return_value = mock_order
        
        config = Config(api_key="key", api_secret="secret", paper_mode=False)
        trader = LiveTrader(config)
        
        order = {
            'symbol': 'BTC/USD',
            'qty': 0.5,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'gtc'
        }
        
        result = trader.execute_order(order)
        
        assert result is not None
        assert result['id'] == "order-123"

    @patch("src.live_trader.TradingClient")
    def test_execute_order_handles_api_error(self, mock_client_class):
        """Test error handling when API call fails."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.submit_order.side_effect = Exception("API Error")
        
        config = Config(api_key="key", api_secret="secret", paper_mode=False)
        trader = LiveTrader(config)
        
        order = {
            'symbol': 'BTC/USD',
            'qty': 0.5,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'gtc'
        }
        
        result = trader.execute_order(order)
        
        assert result is None

    @patch("src.live_trader.TradingClient")
    def test_get_positions(self, mock_client_class):
        """Test getting current positions."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_position = MagicMock()
        mock_position.symbol = "BTC/USD"
        mock_position.qty = "0.5"
        mock_position.avg_entry_price = "35000.00"
        mock_position.current_price = "40000.00"
        mock_position.market_value = "20000.00"
        mock_position.unrealized_pl = "2500.00"
        mock_client.get_all_positions.return_value = [mock_position]
        
        config = Config(api_key="key", api_secret="secret", paper_mode=False)
        trader = LiveTrader(config)
        
        positions = trader.get_positions()
        
        assert "BTC/USD" in positions
        assert positions["BTC/USD"]["qty"] == 0.5

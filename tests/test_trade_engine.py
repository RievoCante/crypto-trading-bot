"""Tests for trade engine module."""
import pytest
from unittest.mock import Mock, patch
from src.strategy import Signal


class TestTradeEngine:
    """Test trade engine functionality."""

    def test_engine_initializes_with_config(self):
        """Test that trade engine initializes with config."""
        from src.trade_engine import TradeEngine
        from config.settings import Config
        
        config = Config(
            api_key="test",
            api_secret="test",
            paper_mode=True,
            max_position_pct=0.20,
            max_order_notional=10000.0
        )
        
        engine = TradeEngine(config)
        
        assert engine.config == config

    def test_calculate_position_size_respects_max_position(self):
        """Test position size calculation respects max position limit."""
        from src.trade_engine import calculate_position_size
        
        position_size = calculate_position_size(
            portfolio_value=50000.0,
            current_btc_position=0.0,
            btc_price=40000.0,
            max_position_pct=0.20
        )
        
        # Max position = $50,000 * 0.20 = $10,000
        # At $40,000/BTC = 0.25 BTC
        assert position_size == 0.25

    def test_calculate_position_size_respects_max_notional(self):
        """Test position size respects max order notional limit."""
        from src.trade_engine import calculate_position_size
        
        position_size = calculate_position_size(
            portfolio_value=1000000.0,
            current_btc_position=0.0,
            btc_price=40000.0,
            max_position_pct=0.20,
            max_order_notional=5000.0
        )
        
        # Limited by max_order_notional: $5,000 / $40,000 = 0.125 BTC
        assert position_size == 0.125

    def test_check_risk_limits_allows_normal_trade(self):
        """Test risk check passes for normal trade within limits."""
        from src.trade_engine import check_risk_limits
        
        result = check_risk_limits(
            daily_pnl_pct=0.01,
            daily_loss_limit_pct=0.05,
            new_position_pct=0.15,
            max_position_pct=0.20
        )
        
        assert result is True

    def test_check_risk_limits_blocks_when_daily_loss_exceeded(self):
        """Test risk check blocks when daily loss limit exceeded."""
        from src.trade_engine import check_risk_limits
        
        result = check_risk_limits(
            daily_pnl_pct=-0.06,
            daily_loss_limit_pct=0.05,
            new_position_pct=0.10,
            max_position_pct=0.20
        )
        
        assert result is False

    def test_process_signal_generates_buy_order(self):
        """Test that BUY signal generates appropriate order."""
        from src.trade_engine import TradeEngine
        from config.settings import Config
        from src.strategy import Signal
        
        config = Config(
            api_key="test",
            api_secret="test",
            max_position_pct=0.20
        )
        
        engine = TradeEngine(config)
        
        order = engine.process_signal(
            signal=Signal.BUY,
            current_price=40000.0,
            portfolio_value=50000.0,
            current_btc_position=0.0,
            daily_pnl_pct=0.0
        )
        
        assert order is not None
        assert order['side'] == 'buy'
        assert order['symbol'] == 'BTC/USD'
        assert order['qty'] > 0

    def test_process_signal_generates_sell_order(self):
        """Test that SELL signal generates appropriate order."""
        from src.trade_engine import TradeEngine
        from config.settings import Config
        from src.strategy import Signal
        
        config = Config(api_key="test", api_secret="test")
        engine = TradeEngine(config)
        
        order = engine.process_signal(
            signal=Signal.SELL,
            current_price=40000.0,
            portfolio_value=50000.0,
            current_btc_position=0.5,
            daily_pnl_pct=0.0
        )
        
        assert order is not None
        assert order['side'] == 'sell'
        assert order['qty'] == 0.5

    def test_process_signal_returns_none_for_hold(self):
        """Test that HOLD signal returns no order."""
        from src.trade_engine import TradeEngine
        from config.settings import Config
        from src.strategy import Signal
        
        config = Config(api_key="test", api_secret="test")
        engine = TradeEngine(config)
        
        order = engine.process_signal(
            signal=Signal.HOLD,
            current_price=40000.0,
            portfolio_value=50000.0,
            current_btc_position=0.0,
            daily_pnl_pct=0.0
        )
        
        assert order is None

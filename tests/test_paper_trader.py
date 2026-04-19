"""Tests for paper trader module."""
import pytest
from unittest.mock import Mock, patch


class TestPaperTrader:
    """Test paper trading simulator."""

    def test_trader_initializes_with_starting_balance(self):
        """Test paper trader initializes with starting balance."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=100000.0)
        
        assert trader.cash_balance == 100000.0
        assert trader.btc_position == 0.0

    def test_execute_buy_deducts_cash_and_adds_btc(self):
        """Test buy execution updates balances correctly."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=50000.0)
        
        order = {
            'symbol': 'BTC/USD',
            'qty': 0.5,
            'side': 'buy',
            'type': 'market'
        }
        
        result = trader.execute_order(order, fill_price=40000.0)
        
        assert result is True
        assert trader.btc_position == 0.5
        assert trader.cash_balance == 30000.0

    def test_execute_sell_adds_cash_and_removes_btc(self):
        """Test sell execution updates balances correctly."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=30000.0, initial_btc=0.5)
        
        order = {
            'symbol': 'BTC/USD',
            'qty': 0.5,
            'side': 'sell',
            'type': 'market'
        }
        
        result = trader.execute_order(order, fill_price=40000.0)
        
        assert result is True
        assert trader.btc_position == 0.0
        assert trader.cash_balance == 50000.0

    def test_get_portfolio_value_calculates_correctly(self):
        """Test portfolio value calculation."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=30000.0, initial_btc=0.5)
        
        value = trader.get_portfolio_value(btc_price=40000.0)
        
        assert value == 50000.0

    def test_trade_history_records_trades(self):
        """Test that trades are recorded in history."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=50000.0)
        
        order = {
            'symbol': 'BTC/USD',
            'qty': 0.5,
            'side': 'buy',
            'type': 'market'
        }
        
        trader.execute_order(order, fill_price=40000.0)
        
        assert len(trader.trade_history) == 1
        assert trader.trade_history[0]['side'] == 'buy'

"""Tests for strategy module."""
import pytest
import pandas as pd
import numpy as np


class TestRSICalculation:
    """Test RSI (Relative Strength Index) calculations."""

    def test_rsi_calculation_with_known_data(self):
        """Test RSI calculation with known price data."""
        from src.strategy import calculate_rsi
        
        prices = [100, 102, 104, 103, 101, 99, 97, 98, 100, 102, 104, 106, 108, 110, 112]
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100

    def test_rsi_returns_none_for_insufficient_data(self):
        """Test that RSI returns None when there isn't enough data."""
        from src.strategy import calculate_rsi
        
        prices = [100, 101, 102]
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is None

    def test_rsi_high_when_prices_increasing(self):
        """Test that RSI is high when prices are consistently increasing."""
        from src.strategy import calculate_rsi
        
        prices = list(range(100, 120))
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert rsi > 70

    def test_rsi_low_when_prices_decreasing(self):
        """Test that RSI is low when prices are consistently decreasing."""
        from src.strategy import calculate_rsi
        
        prices = list(range(120, 100, -1))
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert rsi < 30


class TestMACDCalculation:
    """Test MACD (Moving Average Convergence Divergence) calculations."""

    def test_macd_calculation_returns_tuple(self):
        """Test MACD calculation returns macd_line, signal_line, histogram."""
        from src.strategy import calculate_macd
        
        prices = list(range(100, 150))
        
        result = calculate_macd(prices, fast=12, slow=26, signal=9)
        
        assert result is not None
        macd_line, signal_line, histogram = result
        assert isinstance(macd_line, float)
        assert isinstance(signal_line, float)
        assert isinstance(histogram, float)

    def test_macd_returns_none_for_insufficient_data(self):
        """Test that MACD returns None when there isn't enough data."""
        from src.strategy import calculate_macd
        
        prices = [100, 101, 102]
        
        result = calculate_macd(prices, fast=12, slow=26, signal=9)
        
        assert result is None

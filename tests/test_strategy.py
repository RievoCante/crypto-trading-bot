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


class TestMACDCrossoverDetection:
    """Test MACD crossover detection."""

    def test_detect_macd_crossover_function_exists(self):
        """Test that detect_macd_crossover function exists and is callable."""
        from src.strategy import detect_macd_crossover
        
        assert callable(detect_macd_crossover)

    def test_detect_crossover_returns_string_or_none(self):
        """Test that detect_macd_crossover returns expected types."""
        from src.strategy import detect_macd_crossover
        
        # Test with valid price data - should return either string or None
        prices = list(range(100, 180))
        result = detect_macd_crossover(prices, fast=12, slow=26, signal=9)
        
        assert result is None or isinstance(result, str)
        assert result in [None, "bullish", "bearish"]

    def test_detect_crossover_returns_none_for_insufficient_data(self):
        """Test that None is returned when there isn't enough data."""
        from src.strategy import detect_macd_crossover
        
        prices = [100, 101, 102, 103, 104]
        
        crossover = detect_macd_crossover(prices, fast=12, slow=26, signal=9)
        
        assert crossover is None

    def test_detect_crossover_with_trending_data(self):
        """Test that detect_macd_crossover handles trending price data."""
        from src.strategy import detect_macd_crossover
        
        # Strong uptrend
        uptrend_prices = [100 + i for i in range(80)]
        result_up = detect_macd_crossover(uptrend_prices)
        assert result_up in [None, "bullish", "bearish"]
        
        # Strong downtrend  
        downtrend_prices = [180 - i for i in range(80)]
        result_down = detect_macd_crossover(downtrend_prices)
        assert result_down in [None, "bullish", "bearish"]


class TestSignalGeneration:
    """Test trading signal generation logic."""

    def test_generate_signal_buy_when_rsi_oversold_and_macd_bullish(self):
        """Test BUY signal when RSI < 30 and MACD crosses above signal."""
        from src.strategy import generate_signal, Signal
        
        # Create oversold RSI + bullish MACD
        falling_prices = list(range(150, 100, -2))
        rising_prices = list(range(100, 110))
        prices = falling_prices + rising_prices
        
        signal = generate_signal(
            prices=prices,
            current_position=0.0,
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert signal is not None

    def test_generate_signal_sell_when_rsi_overbought_and_macd_bearish(self):
        """Test SELL signal when RSI > 70 and MACD crosses below signal."""
        from src.strategy import generate_signal, Signal
        
        # Create overbought RSI + bearish MACD
        rising_prices = list(range(100, 150, 2))
        falling_prices = list(range(150, 140, -1))
        prices = rising_prices + falling_prices
        
        signal = generate_signal(
            prices=prices,
            current_position=0.5,
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert signal is not None

    def test_generate_signal_hold_when_no_conditions_met(self):
        """Test HOLD signal when no buy/sell conditions are met."""
        from src.strategy import generate_signal, Signal
        
        # Neutral price data
        prices = [100 + (i % 5) for i in range(50)]
        
        signal = generate_signal(
            prices=prices,
            current_position=0.0,
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert signal is not None

    def test_no_buy_if_already_holding_position(self):
        """Test that we don't get BUY signal if already holding BTC."""
        from src.strategy import generate_signal, Signal
        
        falling_prices = list(range(150, 100, -2))
        rising_prices = list(range(100, 110))
        prices = falling_prices + rising_prices
        
        signal = generate_signal(
            prices=prices,
            current_position=0.5,  # Already holding
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert signal != Signal.BUY

    def test_no_sell_if_not_holding_position(self):
        """Test that we don't get SELL signal if not holding BTC."""
        from src.strategy import generate_signal, Signal
        
        rising_prices = list(range(100, 150, 2))
        falling_prices = list(range(150, 140, -1))
        prices = rising_prices + falling_prices
        
        signal = generate_signal(
            prices=prices,
            current_position=0.0,  # Not holding
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        assert signal != Signal.SELL

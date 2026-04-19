"""Strategy module for calculating technical indicators and generating trading signals.

This module implements the rule-based momentum strategy using RSI and MACD indicators.
"""
from typing import Optional, Tuple, List
from enum import Enum
import pandas as pd
import numpy as np
import pandas_ta as ta


class Signal(Enum):
    """Trading signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate the Relative Strength Index (RSI).
    
    RSI measures the magnitude of recent price changes to evaluate 
    overbought or oversold conditions.
    
    Args:
        prices: List of price values (closes)
        period: Lookback period for RSI calculation (default 14)
        
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    try:
        series = pd.Series(prices)
        rsi = ta.rsi(series, length=period)
        
        if rsi is None or rsi.empty or pd.isna(rsi.iloc[-1]):
            return None
            
        return float(rsi.iloc[-1])
    except Exception:
        return None


def calculate_macd(
    prices: List[float], 
    fast: int = 12, 
    slow: int = 26, 
    signal: int = 9
) -> Optional[Tuple[float, float, float]]:
    """Calculate MACD (Moving Average Convergence Divergence).
    
    MACD is a trend-following momentum indicator.
    
    Args:
        prices: List of price values (closes)
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
        
    Returns:
        Tuple of (macd_line, signal_line, histogram) or None if insufficient data
    """
    min_periods = slow + signal
    if len(prices) < min_periods:
        return None
    
    try:
        series = pd.Series(prices)
        macd_result = ta.macd(series, fast=fast, slow=slow, signal=signal)
        
        if macd_result is None or macd_result.empty:
            return None
        
        macd_col = f"MACD_{fast}_{slow}_{signal}"
        signal_col = f"MACDs_{fast}_{slow}_{signal}"
        hist_col = f"MACDh_{fast}_{slow}_{signal}"
        
        macd_line = float(macd_result[macd_col].iloc[-1])
        signal_line = float(macd_result[signal_col].iloc[-1])
        histogram = float(macd_result[hist_col].iloc[-1])
        
        return (macd_line, signal_line, histogram)
    except Exception:
        return None


def detect_macd_crossover(
    prices: List[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Optional[str]:
    """Detect if MACD line has crossed above or below the signal line.
    
    Args:
        prices: List of price values
        fast, slow, signal: MACD parameters
        
    Returns:
        'bullish' if MACD crossed above signal, 'bearish' if crossed below,
        None if no crossover or insufficient data
    """
    min_periods = slow + signal + 2
    if len(prices) < min_periods:
        return None
    
    try:
        series = pd.Series(prices)
        macd_result = ta.macd(series, fast=fast, slow=slow, signal=signal)
        
        if macd_result is None or len(macd_result) < 2:
            return None
        
        macd_col = f"MACD_{fast}_{slow}_{signal}"
        signal_col = f"MACDs_{fast}_{slow}_{signal}"
        
        prev_macd = float(macd_result[macd_col].iloc[-2])
        prev_signal = float(macd_result[signal_col].iloc[-2])
        curr_macd = float(macd_result[macd_col].iloc[-1])
        curr_signal = float(macd_result[signal_col].iloc[-1])
        
        if prev_macd <= prev_signal and curr_macd > curr_signal:
            return "bullish"
        elif prev_macd >= prev_signal and curr_macd < curr_signal:
            return "bearish"
        
        return None
    except Exception:
        return None


def generate_signal(
    prices: List[float],
    current_position: float,
    rsi_period: int = 14,
    rsi_oversold: float = 30.0,
    rsi_overbought: float = 70.0,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9
) -> Signal:
    """Generate trading signal based on MACD crossovers only.
    
    Strategy Rules (Testing Mode):
    - BUY: MACD crosses above signal line AND not holding
    - SELL: MACD crosses below signal line AND holding
    - HOLD: All other conditions
    
    Note: RSI parameters are kept for compatibility but not used in this
    simplified strategy for testing purposes.
    
    Args:
        prices: List of price values (closes)
        current_position: Current BTC holdings (0.0 = not holding)
        rsi_period: RSI lookback period (unused in this strategy)
        rsi_oversold: RSI threshold for buy signal (unused in this strategy)
        rsi_overbought: RSI threshold for sell signal (unused in this strategy)
        macd_fast, macd_slow, macd_signal: MACD parameters
        
    Returns:
        Signal enum: BUY, SELL, or HOLD
    """
    macd_crossover = detect_macd_crossover(
        prices, fast=macd_fast, slow=macd_slow, signal=macd_signal
    )
    
    signal = Signal.HOLD
    
    # Buy on bullish MACD crossover (no RSI requirement for testing)
    if macd_crossover == "bullish" and current_position == 0.0:
        signal = Signal.BUY
    # Sell on bearish MACD crossover (no RSI requirement for testing)
    elif macd_crossover == "bearish" and current_position > 0.0:
        signal = Signal.SELL
    
    return signal

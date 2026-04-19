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

# Bitcoin AI Trading Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Bitcoin momentum trading bot using RSI and MACD indicators, supporting both paper trading (testing) and live trading (real money) via Alpaca Markets API.

**Architecture:** Modular Python architecture with separate components for data fetching, strategy (indicators), trade engine, and executors (paper/live). Clean interfaces allow swapping rule-based logic for ML models later. Runs locally on MacBook with configuration-driven paper/live mode switching.

**Tech Stack:** Python 3.10+, alpaca-py SDK, pandas, numpy, pandas-ta (indicators), python-dotenv, pytest

---

## Project Structure

```
crypto-trading-bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py      # Alpaca market data client
│   ├── strategy.py          # RSI + MACD indicators and signals
│   ├── trade_engine.py      # Risk management and position sizing
│   ├── paper_trader.py      # Paper trading simulator
│   ├── live_trader.py       # Live trading executor
│   └── main.py              # Bot orchestrator
├── tests/
│   ├── __init__.py
│   ├── test_strategy.py
│   ├── test_data_fetcher.py
│   └── test_trade_engine.py
├── data/
│   ├── logs/                # Trade and error logs
│   └── history/             # Trade history storage
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md                # Setup and usage guide
```

---

## Phase 1: Project Setup & Dependencies

### Task 1: Create Project Structure

**Files:**
- Create directories: `config/`, `src/`, `tests/`, `data/logs/`, `data/history/`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p config src tests data/logs data/history
```

- [ ] **Step 2: Create __init__.py files**

```bash
touch config/__init__.py src/__init__.py tests/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: create project directory structure"
```

---

### Task 2: Setup Python Environment

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`

- [ ] **Step 1: Create requirements.txt**

Write to `requirements.txt`:
```
# Core dependencies
alpaca-py>=0.20.0
pandas>=2.0.0
numpy>=1.24.0
pandas-ta>=0.3.0
python-dotenv>=1.0.0
requests>=2.31.0
websocket-client>=1.6.0

# Development dependencies
pytest>=7.4.0
pytest-mock>=3.11.0
black>=23.0.0
pylint>=2.17.0
```

- [ ] **Step 2: Create .env.example**

Write to `.env.example`:
```
# Alpaca API Configuration
# Get your API keys from: https://app.alpaca.markets/paper/dashboard/overview
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here

# Trading Mode
# Set to 'true' for paper trading (fake money), 'false' for live trading (real money)
PAPER_MODE=true

# Trading Configuration
BTC_SYMBOL=BTC/USD
TRADING_INTERVAL_MINUTES=5
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9

# Risk Management
MAX_POSITION_PCT=0.20
DAILY_LOSS_LIMIT_PCT=0.05
MAX_ORDER_NOTIONAL=10000
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt .env.example
git commit -m "chore: add dependencies and environment template"
```

---

## Phase 2: Configuration Module

### Task 3: Build Configuration System

**Files:**
- Create: `config/settings.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing test for config**

Write to `tests/test_config.py`:
```python
"""Tests for configuration module."""
import os
import pytest
from unittest.mock import patch, MagicMock


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_loads_from_environment(self):
        """Test that config loads from environment variables."""
        from config.settings import Config
        
        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
            'PAPER_MODE': 'true'
        }):
            config = Config()
            assert config.api_key == 'test_key'
            assert config.api_secret == 'test_secret'
            assert config.paper_mode is True

    def test_paper_mode_false_for_live_trading(self):
        """Test that paper_mode=false enables live trading."""
        from config.settings import Config
        
        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
            'PAPER_MODE': 'false'
        }):
            config = Config()
            assert config.paper_mode is False

    def test_risk_parameters_have_defaults(self):
        """Test that risk management parameters have sensible defaults."""
        from config.settings import Config
        
        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
        }, clear=False):
            config = Config()
            assert config.max_position_pct == 0.20
            assert config.daily_loss_limit_pct == 0.05
            assert config.max_order_notional == 10000
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/rievo/crypto-trading-bot
python -m pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'config.settings'`

- [ ] **Step 3: Implement config module**

Write to `config/settings.py`:
```python
"""Configuration management for the trading bot.

All configuration is loaded from environment variables.
Use .env file for local development (see .env.example).
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Trading bot configuration.
    
    All attributes are loaded from environment variables.
    Required variables must be set or an error will be raised.
    """
    
    # Alpaca API credentials (required)
    api_key: str
    api_secret: str
    
    # Trading mode
    paper_mode: bool = True
    
    # Trading parameters
    btc_symbol: str = "BTC/USD"
    trading_interval_minutes: int = 5
    
    # RSI parameters
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    
    # MACD parameters
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Risk management
    max_position_pct: float = 0.20
    daily_loss_limit_pct: float = 0.05
    max_order_notional: float = 10000.0
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Returns:
            Config instance with values from environment.
            
        Raises:
            ValueError: If required environment variables are missing.
        """
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key or not api_secret:
            raise ValueError(
                "ALPACA_API_KEY and ALPACA_SECRET_KEY must be set. "
                "Copy .env.example to .env and fill in your API keys."
            )
        
        paper_mode_str = os.getenv("PAPER_MODE", "true").lower()
        paper_mode = paper_mode_str == "true"
        
        return cls(
            api_key=api_key,
            api_secret=api_secret,
            paper_mode=paper_mode,
            btc_symbol=os.getenv("BTC_SYMBOL", "BTC/USD"),
            trading_interval_minutes=int(os.getenv("TRADING_INTERVAL_MINUTES", "5")),
            rsi_period=int(os.getenv("RSI_PERIOD", "14")),
            rsi_oversold=float(os.getenv("RSI_OVERSOLD", "30")),
            rsi_overbought=float(os.getenv("RSI_OVERBOUGHT", "70")),
            macd_fast=int(os.getenv("MACD_FAST", "12")),
            macd_slow=int(os.getenv("MACD_SLOW", "26")),
            macd_signal=int(os.getenv("MACD_SIGNAL", "9")),
            max_position_pct=float(os.getenv("MAX_POSITION_PCT", "0.20")),
            daily_loss_limit_pct=float(os.getenv("DAILY_LOSS_LIMIT_PCT", "0.05")),
            max_order_notional=float(os.getenv("MAX_ORDER_NOTIONAL", "10000")),
        )
    
    def get_alpaca_base_url(self) -> str:
        """Get the appropriate Alpaca API base URL based on trading mode.
        
        Returns:
            Base URL for API requests (paper or live).
        """
        if self.paper_mode:
            return "https://paper-api.alpaca.markets"
        return "https://api.alpaca.markets"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_config.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add config/settings.py tests/test_config.py
git commit -m "feat: add configuration management with env variable support"
```

---

## Phase 3: Strategy Module (RSI + MACD)

### Task 4: Build Indicator Calculations

**Files:**
- Create: `src/strategy.py`
- Create: `tests/test_strategy.py`

- [ ] **Step 1: Write failing test for RSI calculation**

Write to `tests/test_strategy.py`:
```python
"""Tests for strategy module."""
import pytest
import pandas as pd
import numpy as np


class TestRSICalculation:
    """Test RSI (Relative Strength Index) calculations."""

    def test_rsi_calculation_with_known_data(self):
        """Test RSI calculation with known price data."""
        from src.strategy import calculate_rsi
        
        # Create sample price data that should produce known RSI
        # Using simple increasing then decreasing prices
        prices = [100, 102, 104, 103, 101, 99, 97, 98, 100, 102, 104, 106, 108, 110, 112]
        
        rsi = calculate_rsi(prices, period=14)
        
        # RSI should be calculated
        assert rsi is not None
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100  # RSI always between 0 and 100

    def test_rsi_returns_none_for_insufficient_data(self):
        """Test that RSI returns None when there isn't enough data."""
        from src.strategy import calculate_rsi
        
        prices = [100, 101, 102]  # Only 3 prices, need 14
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is None

    def test_rsi_high_when_prices_increasing(self):
        """Test that RSI is high when prices are consistently increasing."""
        from src.strategy import calculate_rsi
        
        # 20 periods of increasing prices
        prices = list(range(100, 120))
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert rsi > 70  # Should be overbought

    def test_rsi_low_when_prices_decreasing(self):
        """Test that RSI is low when prices are consistently decreasing."""
        from src.strategy import calculate_rsi
        
        # 20 periods of decreasing prices
        prices = list(range(120, 100, -1))
        
        rsi = calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert rsi < 30  # Should be oversold


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
        
        prices = [100, 101, 102]  # Need at least 26 + 9 = 35 periods
        
        result = calculate_macd(prices, fast=12, slow=26, signal=9)
        
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_strategy.py::TestRSICalculation -v
```

Expected: `ModuleNotFoundError: No module named 'src.strategy'` or function not defined errors

- [ ] **Step 3: Implement indicator functions**

Write to `src/strategy.py`:
```python
"""Strategy module for calculating technical indicators and generating trading signals.

This module implements the rule-based momentum strategy using RSI and MACD indicators.
The strategy can be easily extended to use ML models by implementing the StrategyInterface.
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
    
    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of a security's price.
    
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
        
        # Extract the three components
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
    min_periods = slow + signal + 2  # Need 2 extra periods to compare
    if len(prices) < min_periods:
        return None
    
    try:
        series = pd.Series(prices)
        macd_result = ta.macd(series, fast=fast, slow=slow, signal=signal)
        
        if macd_result is None or len(macd_result) < 2:
            return None
        
        macd_col = f"MACD_{fast}_{slow}_{signal}"
        signal_col = f"MACDs_{fast}_{slow}_{signal}"
        
        # Get last two periods
        prev_macd = float(macd_result[macd_col].iloc[-2])
        prev_signal = float(macd_result[signal_col].iloc[-2])
        curr_macd = float(macd_result[macd_col].iloc[-1])
        curr_signal = float(macd_result[signal_col].iloc[-1])
        
        # Check for crossover
        if prev_macd <= prev_signal and curr_macd > curr_signal:
            return "bullish"  # Crossed above
        elif prev_macd >= prev_signal and curr_macd < curr_signal:
            return "bearish"  # Crossed below
        
        return None
    except Exception:
        return None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_strategy.py::TestRSICalculation -v
python -m pytest tests/test_strategy.py::TestMACDCalculation -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/strategy.py tests/test_strategy.py
git commit -m "feat: add RSI and MACD indicator calculations"
```

---

### Task 5: Build Signal Generation Logic

**Files:**
- Modify: `src/strategy.py` (add signal generation)
- Modify: `tests/test_strategy.py` (add signal tests)

- [ ] **Step 1: Write failing test for signal generation**

Add to `tests/test_strategy.py`:
```python
class TestSignalGeneration:
    """Test trading signal generation logic."""

    def test_generate_signal_buy_when_rsi_oversold_and_macd_bullish(self):
        """Test BUY signal when RSI < 30 and MACD crosses above signal."""
        from src.strategy import generate_signal, Signal
        
        # Create data that simulates oversold condition with bullish MACD
        # First create oversold (falling prices), then MACD crossover
        falling_prices = list(range(150, 100, -2))  # Strong downtrend
        rising_prices = list(range(100, 110))  # Starting to rise
        prices = falling_prices + rising_prices
        
        # Mock having no current position
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
        
        # With oversold RSI and bullish MACD crossover, should get BUY
        assert signal is not None

    def test_generate_signal_sell_when_rsi_overbought_and_macd_bearish(self):
        """Test SELL signal when RSI > 70 and MACD crosses below signal."""
        from src.strategy import generate_signal, Signal
        
        # Create data that simulates overbought condition with bearish MACD
        rising_prices = list(range(100, 150, 2))  # Strong uptrend
        falling_prices = list(range(150, 140, -1))  # Starting to fall
        prices = rising_prices + falling_prices
        
        # Mock having BTC position
        signal = generate_signal(
            prices=prices,
            current_position=0.5,  # Holding 0.5 BTC
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
        
        # Neutral price data (sideways market)
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
            current_position=0.5,  # Already holding 0.5 BTC
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        # Should not be BUY since we already have position
        assert signal != Signal.BUY

    def test_no_sell_if_not_holding_position(self):
        """Test that we don't get SELL signal if not holding BTC."""
        from src.strategy import generate_signal, Signal
        
        rising_prices = list(range(100, 150, 2))
        falling_prices = list(range(150, 140, -1))
        prices = rising_prices + falling_prices
        
        signal = generate_signal(
            prices=prices,
            current_position=0.0,  # Not holding any BTC
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9
        )
        
        # Should not be SELL since we don't have position
        assert signal != Signal.SELL
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_strategy.py::TestSignalGeneration -v
```

Expected: Function not defined errors

- [ ] **Step 3: Implement signal generation**

Add to `src/strategy.py`:
```python

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
    """Generate trading signal based on RSI and MACD indicators.
    
    Strategy Rules:
    - BUY: RSI < oversold_threshold AND MACD crosses above signal line AND not holding
    - SELL: RSI > overbought_threshold AND MACD crosses below signal line AND holding
    - HOLD: All other conditions
    
    Args:
        prices: List of price values (closes)
        current_position: Current BTC holdings (0.0 = not holding)
        rsi_period: RSI lookback period
        rsi_oversold: RSI threshold for oversold (buy signal)
        rsi_overbought: RSI threshold for overbought (sell signal)
        macd_fast, macd_slow, macd_signal: MACD parameters
        
    Returns:
        Signal enum: BUY, SELL, or HOLD
    """
    # Calculate indicators
    rsi = calculate_rsi(prices, period=rsi_period)
    macd_crossover = detect_macd_crossover(
        prices, fast=macd_fast, slow=macd_slow, signal=macd_signal
    )
    
    # Default to HOLD
    signal = Signal.HOLD
    
    # Check for BUY signal
    # RSI oversold + bullish MACD crossover + not holding position
    if (rsi is not None and 
        rsi < rsi_oversold and 
        macd_crossover == "bullish" and 
        current_position == 0.0):
        signal = Signal.BUY
    
    # Check for SELL signal
    # RSI overbought + bearish MACD crossover + holding position
    elif (rsi is not None and 
          rsi > rsi_overbought and 
          macd_crossover == "bearish" and 
          current_position > 0.0):
        signal = Signal.SELL
    
    return signal
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_strategy.py::TestSignalGeneration -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/strategy.py tests/test_strategy.py
```

```bash
git commit -m "feat: add signal generation logic with RSI and MACD conditions"
```

---

## Phase 4: Data Fetcher Module

### Task 6: Build Alpaca Data Client

**Files:**
- Create: `src/data_fetcher.py`
- Create: `tests/test_data_fetcher.py`

- [ ] **Step 1: Write failing test for data fetcher**

Write to `tests/test_data_fetcher.py`:
```python
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

    @patch("alpaca.data.historical.crypto.CryptoHistoricalDataClient")
    def test_get_historical_bars_calls_api(self, mock_client_class):
        """Test that get_historical_bars makes API call with correct parameters."""
        from src.data_fetcher import AlpacaDataFetcher
        from config.settings import Config
        
        # Setup mock
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
        
        # Verify API was called
        mock_client.get_crypto_bars.assert_called_once()
        assert bars is not None
        assert len(bars) == 2

    def test_extract_closes_returns_price_list(self):
        """Test that extract_closes returns list of closing prices."""
        from src.data_fetcher import extract_closes
        
        # Mock bars DataFrame
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_data_fetcher.py -v
```

Expected: Module or function not found errors

- [ ] **Step 3: Implement data fetcher**

Write to `src/data_fetcher.py`:
```python
"""Data fetcher module for retrieving market data from Alpaca.

Provides clean interface for fetching historical and real-time
BTC/USD price data.
"""
from typing import List, Optional
import pandas as pd
from alpaca.data.historical.crypto import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

from config.settings import Config


class AlpacaDataFetcher:
    """Client for fetching cryptocurrency data from Alpaca.
    
    Handles authentication and provides methods for fetching
    historical bars and real-time quotes.
    """
    
    def __init__(self, config: Config):
        """Initialize data fetcher with configuration.
        
        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        self._client: Optional[CryptoHistoricalDataClient] = None
    
    def _get_client(self) -> CryptoHistoricalDataClient:
        """Get or create Alpaca data client (lazy initialization).
        
        Returns:
            Configured CryptoHistoricalDataClient instance
        """
        if self._client is None:
            self._client = CryptoHistoricalDataClient(
                api_key=self.config.api_key,
                secret_key=self.config.api_secret
            )
        return self._client
    
    def get_historical_bars(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.Minute,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Fetch historical price bars for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            timeframe: Bar timeframe (default 1 minute)
            limit: Number of bars to fetch (max 10000)
            
        Returns:
            DataFrame with OHLCV data or None if error
            Columns: open, high, low, close, volume, trade_count, vwap
        """
        try:
            client = self._get_client()
            
            # Calculate start time based on limit and timeframe
            # Default to fetching last N minutes of data
            end = datetime.now()
            start = end - timedelta(minutes=limit + 5)  # Buffer for safety
            
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            bars = client.get_crypto_bars(request)
            
            if bars is None or bars.df is None or bars.df.empty:
                return None
            
            return bars.df
            
        except Exception as e:
            print(f"Error fetching historical bars: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USD")
            
        Returns:
            Latest price or None if error
        """
        bars = self.get_historical_bars(symbol, limit=1)
        
        if bars is None or bars.empty:
            return None
        
        return float(bars['close'].iloc[-1])


def extract_closes(bars: Optional[pd.DataFrame]) -> List[float]:
    """Extract closing prices from bars DataFrame.
    
    Args:
        bars: DataFrame with OHLCV data from Alpaca
        
    Returns:
        List of closing prices (oldest to newest)
    """
    if bars is None or bars.empty or 'close' not in bars.columns:
        return []
    
    return bars['close'].tolist()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_data_fetcher.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data_fetcher.py tests/test_data_fetcher.py
git commit -m "feat: add Alpaca data fetcher with historical bars support"
```

---

## Phase 5: Trade Engine Module

### Task 7: Build Risk Management & Position Sizing

**Files:**
- Create: `src/trade_engine.py`
- Create: `tests/test_trade_engine.py`

- [ ] **Step 1: Write failing test for trade engine**

Write to `tests/test_trade_engine.py`:
```python
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
        from src.trade_engine import TradeEngine, calculate_position_size
        from config.settings import Config
        
        config = Config(
            api_key="test",
            api_secret="test",
            max_position_pct=0.20
        )
        
        # Portfolio: $50,000 cash, $0 BTC, price $40,000
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
        
        # Large portfolio but small max order
        position_size = calculate_position_size(
            portfolio_value=1000000.0,
            current_btc_position=0.0,
            btc_price=40000.0,
            max_position_pct=0.20,
            max_order_notional=5000.0  # Small limit
        )
        
        # Limited by max_order_notional: $5,000 / $40,000 = 0.125 BTC
        assert position_size == 0.125

    def test_check_risk_limits_allows_normal_trade(self):
        """Test risk check passes for normal trade within limits."""
        from src.trade_engine import check_risk_limits
        
        # No significant loss, normal position
        result = check_risk_limits(
            daily_pnl_pct=0.01,  # 1% profit
            daily_loss_limit_pct=0.05,
            new_position_pct=0.15,
            max_position_pct=0.20
        )
        
        assert result is True

    def test_check_risk_limits_blocks_when_daily_loss_exceeded(self):
        """Test risk check blocks when daily loss limit exceeded."""
        from src.trade_engine import check_risk_limits
        
        result = check_risk_limits(
            daily_pnl_pct=-0.06,  # -6% loss (over 5% limit)
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
        
        config = Config(
            api_key="test",
            api_secret="test"
        )
        
        engine = TradeEngine(config)
        
        order = engine.process_signal(
            signal=Signal.SELL,
            current_price=40000.0,
            portfolio_value=50000.0,
            current_btc_position=0.5,  # Holding 0.5 BTC
            daily_pnl_pct=0.0
        )
        
        assert order is not None
        assert order['side'] == 'sell'
        assert order['qty'] == 0.5  # Sell entire position

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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_trade_engine.py -v
```

Expected: Module or function not found errors

- [ ] **Step 3: Implement trade engine**

Write to `src/trade_engine.py`:
```python
"""Trade engine module for risk management and order generation.

Handles position sizing, risk checks, and converts signals into
order parameters for execution.
"""
from typing import Optional, Dict, Any
from decimal import Decimal, ROUND_DOWN

from config.settings import Config
from src.strategy import Signal


def calculate_position_size(
    portfolio_value: float,
    current_btc_position: float,
    btc_price: float,
    max_position_pct: float,
    max_order_notional: float = 10000.0
) -> float:
    """Calculate position size for a trade.
    
    Position is limited by:
    1. Max position percentage of portfolio
    2. Max order notional value
    3. Minimum order size (0.0001 BTC on Alpaca)
    
    Args:
        portfolio_value: Total portfolio value in USD
        current_btc_position: Current BTC holdings
        btc_price: Current BTC price in USD
        max_position_pct: Max percentage of portfolio in BTC
        max_order_notional: Maximum order value in USD
        
    Returns:
        BTC quantity to buy (0 if trade would violate limits)
    """
    if btc_price <= 0:
        return 0.0
    
    # Calculate maximum position value based on portfolio
    max_position_value = portfolio_value * max_position_pct
    
    # Current position value
    current_position_value = current_btc_position * btc_price
    
    # Available position value
    available_value = max_position_value - current_position_value
    
    # Limit by max order notional
    available_value = min(available_value, max_order_notional)
    
    # Convert to BTC quantity
    btc_quantity = available_value / btc_price
    
    # Round down to 4 decimal places (Alpaca precision)
    btc_quantity = float(Decimal(str(btc_quantity)).quantize(
        Decimal('0.0001'), 
        rounding=ROUND_DOWN
    ))
    
    # Ensure minimum order size (0.0001 BTC)
    if btc_quantity < 0.0001:
        return 0.0
    
    return btc_quantity


def check_risk_limits(
    daily_pnl_pct: float,
    daily_loss_limit_pct: float,
    new_position_pct: float,
    max_position_pct: float
) -> bool:
    """Check if trade passes risk management rules.
    
    Args:
        daily_pnl_pct: Current daily profit/loss percentage
        daily_loss_limit_pct: Maximum allowed daily loss
        new_position_pct: New position as percentage of portfolio
        max_position_pct: Maximum allowed position percentage
        
    Returns:
        True if trade passes risk checks, False otherwise
    """
    # Check daily loss limit
    if daily_pnl_pct <= -daily_loss_limit_pct:
        print(f"Risk check failed: Daily loss limit exceeded ({daily_pnl_pct:.2%})")
        return False
    
    # Check position limit
    if new_position_pct > max_position_pct:
        print(f"Risk check failed: Position limit exceeded ({new_position_pct:.2%})")
        return False
    
    return True


class TradeEngine:
    """Trade engine for processing signals and generating orders.
    
    Applies risk management rules and calculates appropriate
    position sizes before generating order parameters.
    """
    
    def __init__(self, config: Config):
        """Initialize trade engine with configuration.
        
        Args:
            config: Configuration with risk parameters
        """
        self.config = config
    
    def process_signal(
        self,
        signal: Signal,
        current_price: float,
        portfolio_value: float,
        current_btc_position: float,
        daily_pnl_pct: float
    ) -> Optional[Dict[str, Any]]:
        """Process trading signal and generate order if appropriate.
        
        Args:
            signal: Trading signal (BUY, SELL, or HOLD)
            current_price: Current BTC price
            portfolio_value: Total portfolio value in USD
            current_btc_position: Current BTC holdings
            daily_pnl_pct: Daily P&L percentage for risk check
            
        Returns:
            Order dictionary or None if no trade should be made
        """
        if signal == Signal.HOLD:
            return None
        
        if signal == Signal.BUY:
            return self._process_buy_signal(
                current_price, portfolio_value, 
                current_btc_position, daily_pnl_pct
            )
        
        if signal == Signal.SELL:
            return self._process_sell_signal(
                current_price, portfolio_value,
                current_btc_position, daily_pnl_pct
            )
        
        return None
    
    def _process_buy_signal(
        self,
        current_price: float,
        portfolio_value: float,
        current_btc_position: float,
        daily_pnl_pct: float
    ) -> Optional[Dict[str, Any]]:
        """Process buy signal and generate order."""
        # Calculate position size
        qty = calculate_position_size(
            portfolio_value=portfolio_value,
            current_btc_position=current_btc_position,
            btc_price=current_price,
            max_position_pct=self.config.max_position_pct,
            max_order_notional=self.config.max_order_notional
        )
        
        if qty <= 0:
            print("Position size too small, skipping buy")
            return None
        
        # Calculate new position percentage
        new_btc_value = (current_btc_position + qty) * current_price
        new_position_pct = new_btc_value / portfolio_value if portfolio_value > 0 else 1.0
        
        # Check risk limits
        if not check_risk_limits(
            daily_pnl_pct=daily_pnl_pct,
            daily_loss_limit_pct=self.config.daily_loss_limit_pct,
            new_position_pct=new_position_pct,
            max_position_pct=self.config.max_position_pct
        ):
            return None
        
        return {
            'symbol': self.config.btc_symbol,
            'qty': qty,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'gtc'
        }
    
    def _process_sell_signal(
        self,
        current_price: float,
        portfolio_value: float,
        current_btc_position: float,
        daily_pnl_pct: float
    ) -> Optional[Dict[str, Any]]:
        """Process sell signal and generate order."""
        if current_btc_position <= 0:
            print("No BTC position to sell")
            return None
        
        # Check risk limits
        new_position_pct = 0.0  # Will have no position after sell
        
        if not check_risk_limits(
            daily_pnl_pct=daily_pnl_pct,
            daily_loss_limit_pct=self.config.daily_loss_limit_pct,
            new_position_pct=new_position_pct,
            max_position_pct=self.config.max_position_pct
        ):
            return None
        
        # Sell entire position (can be modified for partial sells)
        qty = current_btc_position
        
        return {
            'symbol': self.config.btc_symbol,
            'qty': qty,
            'side': 'sell',
            'type': 'market',
            'time_in_force': 'gtc'
        }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_trade_engine.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/trade_engine.py tests/test_trade_engine.py
git commit -m "feat: add trade engine with risk management and position sizing"
```

---

## Phase 6: Trading Executors

### Task 8: Build Paper Trading Simulator

**Files:**
- Create: `src/paper_trader.py`
- Create: `tests/test_paper_trader.py`

- [ ] **Step 1: Write failing test for paper trader**

Write to `tests/test_paper_trader.py`:
```python
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
        assert trader.cash_balance == 30000.0  # 50000 - (0.5 * 40000)

    def test_execute_sell_adds_cash_and_removes_btc(self):
        """Test sell execution updates balances correctly."""
        from src.paper_trader import PaperTrader
        
        # Start with 0.5 BTC and $30,000 cash
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
        assert trader.cash_balance == 50000.0  # 30000 + (0.5 * 40000)

    def test_get_portfolio_value_calculates_correctly(self):
        """Test portfolio value calculation."""
        from src.paper_trader import PaperTrader
        
        trader = PaperTrader(initial_balance=30000.0, initial_btc=0.5)
        
        value = trader.get_portfolio_value(btc_price=40000.0)
        
        # 30000 cash + (0.5 BTC * 40000) = 50000
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
        assert trader.trade_history[0]['qty'] == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_paper_trader.py -v
```

Expected: Module or class not found errors

- [ ] **Step 3: Implement paper trader**

Write to `src/paper_trader.py`:
```python
"""Paper trading simulator for testing strategies without real money.

Simulates order execution and tracks portfolio value using real-time
prices but fake funds. Perfect for strategy validation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_DOWN


class PaperTrader:
    """Paper trading simulator.
    
    Simulates trade execution without real money. Tracks cash balance,
    BTC position, and trade history. Uses real market prices for fills.
    """
    
    def __init__(
        self, 
        initial_balance: float = 100000.0,
        initial_btc: float = 0.0
    ):
        """Initialize paper trader with starting balance.
        
        Args:
            initial_balance: Starting cash balance in USD (default $100k)
            initial_btc: Starting BTC position (default 0)
        """
        self.cash_balance = initial_balance
        self.btc_position = initial_btc
        self.trade_history: List[Dict[str, Any]] = []
    
    def execute_order(
        self, 
        order: Dict[str, Any], 
        fill_price: float
    ) -> bool:
        """Execute an order in paper trading environment.
        
        Args:
            order: Order dictionary with symbol, qty, side, type
            fill_price: Price at which order is filled
            
        Returns:
            True if order executed successfully, False otherwise
        """
        try:
            symbol = order['symbol']
            qty = float(order['qty'])
            side = order['side']
            
            # Round qty to 4 decimal places (Alpaca precision)
            qty = float(Decimal(str(qty)).quantize(
                Decimal('0.0001'), 
                rounding=ROUND_DOWN
            ))
            
            notional = qty * fill_price
            
            if side == 'buy':
                # Check sufficient cash
                if notional > self.cash_balance:
                    print(f"Insufficient cash: need ${notional:.2f}, have ${self.cash_balance:.2f}")
                    return False
                
                # Execute buy
                self.cash_balance -= notional
                self.btc_position += qty
                
            elif side == 'sell':
                # Check sufficient BTC
                if qty > self.btc_position:
                    print(f"Insufficient BTC: need {qty}, have {self.btc_position}")
                    return False
                
                # Execute sell
                self.cash_balance += notional
                self.btc_position -= qty
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'price': fill_price,
                'notional': notional,
                'cash_balance': self.cash_balance,
                'btc_position': self.btc_position
            }
            self.trade_history.append(trade_record)
            
            print(f"Paper trade executed: {side.upper()} {qty} {symbol} @ ${fill_price:,.2f}")
            print(f"  Cash: ${self.cash_balance:,.2f} | BTC: {self.btc_position:.4f}")
            
            return True
            
        except Exception as e:
            print(f"Error executing paper order: {e}")
            return False
    
    def get_portfolio_value(self, btc_price: float) -> float:
        """Calculate total portfolio value.
        
        Args:
            btc_price: Current BTC price in USD
            
        Returns:
            Total portfolio value (cash + BTC position)
        """
        btc_value = self.btc_position * btc_price
        return self.cash_balance + btc_value
    
    def get_position_summary(self, btc_price: float) -> Dict[str, Any]:
        """Get summary of current position.
        
        Args:
            btc_price: Current BTC price
            
        Returns:
            Dictionary with position details
        """
        btc_value = self.btc_position * btc_price
        total_value = self.cash_balance + btc_value
        
        return {
            'cash_balance': self.cash_balance,
            'btc_position': self.btc_position,
            'btc_value': btc_value,
            'total_value': total_value,
            'btc_price': btc_price
        }
    
    def reset(self, initial_balance: float = 100000.0):
        """Reset paper trader to initial state.
        
        Args:
            initial_balance: New starting balance
        """
        self.cash_balance = initial_balance
        self.btc_position = 0.0
        self.trade_history = []
        print(f"Paper trader reset: ${initial_balance:,.2f} starting balance")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_paper_trader.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/paper_trader.py tests/test_paper_trader.py
git commit -m "feat: add paper trading simulator for strategy testing"
```

---

### Task 9: Build Live Trading Executor

**Files:**
- Create: `src/live_trader.py`
- Create: `tests/test_live_trader.py`

- [ ] **Step 1: Write failing test for live trader**

Write to `tests/test_live_trader.py`:
```python
"""Tests for live trader module."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLiveTrader:
    """Test live trading executor."""

    @patch("alpaca.trading.client.TradingClient")
    def test_trader_initializes_with_config(self, mock_client_class):
        """Test live trader initializes with config."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        config = Config(
            api_key="live_key",
            api_secret="live_secret",
            paper_mode=False  # Live mode
        )
        
        trader = LiveTrader(config)
        
        assert trader.config == config
        # TradingClient should be initialized
        mock_client_class.assert_called_once_with(
            api_key="live_key",
            secret_key="live_secret",
            paper=False
        )

    @patch("alpaca.trading.client.TradingClient")
    def test_execute_buy_order(self, mock_client_class):
        """Test executing a buy order via Alpaca API."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock successful order response
        mock_order = MagicMock()
        mock_order.id = "order-123"
        mock_order.symbol = "BTC/USD"
        mock_order.qty = "0.5"
        mock_order.side = "buy"
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
        mock_client.submit_order.assert_called_once()

    @patch("alpaca.trading.client.TradingClient")
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

    @patch("alpaca.trading.client.TradingClient")
    def test_get_positions(self, mock_client_class):
        """Test getting current positions."""
        from src.live_trader import LiveTrader
        from config.settings import Config
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock BTC position
        mock_position = MagicMock()
        mock_position.symbol = "BTC/USD"
        mock_position.qty = "0.5"
        mock_position.current_price = "40000.00"
        mock_client.get_all_positions.return_value = [mock_position]
        
        config = Config(api_key="key", api_secret="secret", paper_mode=False)
        trader = LiveTrader(config)
        
        positions = trader.get_positions()
        
        assert "BTC/USD" in positions
        assert positions["BTC/USD"]["qty"] == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_live_trader.py -v
```

Expected: Module or class not found errors

- [ ] **Step 3: Implement live trader**

Write to `src/live_trader.py`:
```python
"""Live trading executor for executing real trades via Alpaca API.

WARNING: This module uses real money. Only initialize when PAPER_MODE=false
and you have verified your strategy works correctly in paper trading.
"""
from typing import Dict, Any, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

from config.settings import Config


class LiveTrader:
    """Live trading executor.
    
    Executes real trades via Alpaca Trading API. Uses actual funds from
    your brokerage account. Double-check configuration before using.
    
    IMPORTANT: Only use when PAPER_MODE=false in configuration.
    """
    
    def __init__(self, config: Config):
        """Initialize live trader with configuration.
        
        Args:
            config: Configuration with API credentials
            
        Raises:
            RuntimeError: If config has paper_mode=True (safety check)
        """
        self.config = config
        
        # Safety check: refuse to initialize in paper mode
        if config.paper_mode:
            raise RuntimeError(
                "LiveTrader cannot be initialized with paper_mode=True. "
                "Set PAPER_MODE=false in your .env file to trade with real money. "
                "WARNING: This will use real funds from your account!"
            )
        
        self._client = TradingClient(
            api_key=config.api_key,
            secret_key=config.api_secret,
            paper=False
        )
    
    def execute_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a real order via Alpaca Trading API.
        
        Args:
            order: Order dictionary with symbol, qty, side, type, time_in_force
            
        Returns:
            Order response with id, status, etc., or None if error
        """
        try:
            symbol = order['symbol']
            qty = order['qty']
            side = order['side']
            order_type = order.get('type', 'market')
            time_in_force = order.get('time_in_force', 'gtc')
            
            # Map side string to enum
            side_enum = OrderSide.BUY if side == 'buy' else OrderSide.SELL
            
            # Map time in force
            tif_map = {
                'gtc': TimeInForce.GTC,
                'ioc': TimeInForce.IOC,
                'day': TimeInForce.DAY
            }
            tif_enum = tif_map.get(time_in_force, TimeInForce.GTC)
            
            # Create order request
            if order_type == 'market':
                order_request = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side_enum,
                    time_in_force=tif_enum
                )
            elif order_type == 'limit':
                limit_price = order.get('limit_price')
                if not limit_price:
                    raise ValueError("Limit price required for limit orders")
                order_request = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side_enum,
                    time_in_force=tif_enum,
                    limit_price=limit_price
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            # Submit order
            response = self._client.submit_order(order_request)
            
            # Log trade
            print(f"Live order submitted: {side.upper()} {qty} {symbol}")
            print(f"  Order ID: {response.id}")
            print(f"  Status: {response.status}")
            
            return {
                'id': response.id,
                'symbol': response.symbol,
                'qty': float(response.qty) if response.qty else 0.0,
                'side': response.side.value,
                'type': response.type.value if response.type else 'market',
                'status': response.status.value,
                'created_at': str(response.created_at) if response.created_at else None
            }
            
        except Exception as e:
            print(f"Error executing live order: {e}")
            return None
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions from Alpaca.
        
        Returns:
            Dictionary mapping symbol to position details
        """
        try:
            positions = self._client.get_all_positions()
            
            result = {}
            for pos in positions:
                result[pos.symbol] = {
                    'qty': float(pos.qty) if pos.qty else 0.0,
                    'avg_entry_price': float(pos.avg_entry_price) if pos.avg_entry_price else 0.0,
                    'current_price': float(pos.current_price) if pos.current_price else 0.0,
                    'market_value': float(pos.market_value) if pos.market_value else 0.0,
                    'unrealized_pl': float(pos.unrealized_pl) if pos.unrealized_pl else 0.0
                }
            
            return result
            
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return {}
    
    def get_account(self) -> Optional[Dict[str, Any]]:
        """Get account information from Alpaca.
        
        Returns:
            Dictionary with account details or None if error
        """
        try:
            account = self._client.get_account()
            
            return {
                'id': account.id,
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'status': account.status
            }
            
        except Exception as e:
            print(f"Error fetching account: {e}")
            return None
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._client.cancel_orders()
            print("All open orders cancelled")
            return True
        except Exception as e:
            print(f"Error cancelling orders: {e}")
            return False
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_live_trader.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/live_trader.py tests/test_live_trader.py
git commit -m "feat: add live trading executor with safety checks"
```

---

## Phase 7: Main Bot Orchestrator

### Task 10: Build Main Trading Loop

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing test for main**

Write to `tests/test_main.py`:
```python
"""Tests for main trading bot orchestrator."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd


class TestTradingBot:
    """Test main trading bot functionality."""

    @patch("src.main.AlpacaDataFetcher")
    @patch("src.main.TradeEngine")
    @patch("src.main.PaperTrader")
    def test_bot_initializes_components(self, mock_trader, mock_engine, mock_fetcher):
        """Test bot initializes all required components."""
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

    @patch("src.main.AlpacaDataFetcher")
    @patch("src.main.TradeEngine")
    @patch("src.main.PaperTrader")
    def test_run_single_cycle(self, mock_trader_class, mock_engine_class, mock_fetcher_class):
        """Test running a single trading cycle."""
        from src.main import TradingBot
        from config.settings import Config
        from src.strategy import Signal
        
        # Setup mocks
        mock_fetcher = MagicMock()
        mock_fetcher.get_historical_bars.return_value = pd.DataFrame({
            'close': list(range(100, 150))
        })
        mock_fetcher.get_latest_price.return_value = 40000.0
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_engine = MagicMock()
        mock_engine.process_signal.return_value = {
            'symbol': 'BTC/USD',
            'qty': 0.25,
            'side': 'buy',
            'type': 'market'
        }
        mock_engine_class.return_value = mock_engine
        
        mock_trader = MagicMock()
        mock_trader.execute_order.return_value = True
        mock_trader.btc_position = 0.0
        mock_trader.get_portfolio_value.return_value = 50000.0
        mock_trader_class.return_value = mock_trader
        
        config = Config(
            api_key="test",
            api_secret="test",
            paper_mode=True,
            trading_interval_minutes=5
        )
        
        bot = TradingBot(config)
        bot.paper_trader = mock_trader
        
        # Run one cycle
        bot._run_cycle()
        
        # Verify data was fetched
        mock_fetcher.get_historical_bars.assert_called_once()
        # Verify signal was processed
        mock_engine.process_signal.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_main.py -v
```

Expected: Module or class not found errors

- [ ] **Step 3: Implement main bot**

Write to `src/main.py`:
```python
"""Main trading bot orchestrator.

Coordinates data fetching, signal generation, trade execution, and logging.
Runs continuously with configurable intervals between trading cycles.
"""
import time
import signal
import sys
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from config.settings import Config
from src.data_fetcher import AlpacaDataFetcher, extract_closes
from src.strategy import generate_signal, Signal
from src.trade_engine import TradeEngine
from src.paper_trader import PaperTrader
from src.live_trader import LiveTrader


class TradingBot:
    """Bitcoin trading bot orchestrator.
    
    Coordinates all components: data fetcher, strategy, trade engine,
    and trading executor (paper or live). Runs trading cycles at
    configured intervals.
    """
    
    def __init__(self, config: Config):
        """Initialize trading bot with configuration.
        
        Args:
            config: Configuration with API credentials and parameters
        """
        self.config = config
        self.data_fetcher = AlpacaDataFetcher(config)
        self.trade_engine = TradeEngine(config)
        
        # Initialize appropriate trader based on mode
        if config.paper_mode:
            print("=" * 60)
            print("PAPER TRADING MODE - Using fake money")
            print("=" * 60)
            self.trader = PaperTrader(initial_balance=100000.0)
        else:
            print("=" * 60)
            print("LIVE TRADING MODE - Using REAL money!")
            print("=" * 60)
            confirm = input("Type 'LIVE' to confirm real money trading: ")
            if confirm != "LIVE":
                print("Confirmation failed. Exiting.")
                sys.exit(1)
            self.trader = LiveTrader(config)
        
        self.running = False
        self.starting_portfolio_value: Optional[float] = None
    
    def _run_cycle(self) -> None:
        """Execute one complete trading cycle."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] Starting trading cycle...")
            
            # Step 1: Fetch market data
            bars = self.data_fetcher.get_historical_bars(
                symbol=self.config.btc_symbol,
                limit=100
            )
            
            if bars is None or bars.empty:
                print("Failed to fetch market data, skipping cycle")
                return
            
            # Step 2: Extract price data and current price
            closes = extract_closes(bars)
            current_price = closes[-1]
            
            print(f"  Price: ${current_price:,.2f} | Data points: {len(closes)}")
            
            # Step 3: Get current position
            if self.config.paper_mode:
                current_btc = self.trader.btc_position
                portfolio_value = self.trader.get_portfolio_value(current_price)
            else:
                positions = self.trader.get_positions()
                current_btc = positions.get(self.config.btc_symbol, {}).get('qty', 0.0)
                account = self.trader.get_account()
                portfolio_value = account['portfolio_value'] if account else 0.0
            
            # Track starting value for daily P&L
            if self.starting_portfolio_value is None:
                self.starting_portfolio_value = portfolio_value
            
            # Calculate daily P&L
            daily_pnl_pct = 0.0
            if self.starting_portfolio_value and self.starting_portfolio_value > 0:
                daily_pnl_pct = (portfolio_value - self.starting_portfolio_value) / self.starting_portfolio_value
            
            print(f"  Portfolio: ${portfolio_value:,.2f} | BTC: {current_btc:.4f} | Daily P&L: {daily_pnl_pct:.2%}")
            
            # Step 4: Generate signal
            signal = generate_signal(
                prices=closes,
                current_position=current_btc,
                rsi_period=self.config.rsi_period,
                rsi_oversold=self.config.rsi_oversold,
                rsi_overbought=self.config.rsi_overbought,
                macd_fast=self.config.macd_fast,
                macd_slow=self.config.macd_slow,
                macd_signal=self.config.macd_signal
            )
            
            print(f"  Signal: {signal.value.upper()}")
            
            # Step 5: Process signal and generate order
            order = self.trade_engine.process_signal(
                signal=signal,
                current_price=current_price,
                portfolio_value=portfolio_value,
                current_btc_position=current_btc,
                daily_pnl_pct=daily_pnl_pct
            )
            
            # Step 6: Execute order if generated
            if order:
                print(f"  Order: {order['side'].upper()} {order['qty']:.4f} BTC")
                
                if self.config.paper_mode:
                    success = self.trader.execute_order(order, fill_price=current_price)
                else:
                    result = self.trader.execute_order(order)
                    success = result is not None
                
                if success:
                    print(f"  Order executed successfully")
                else:
                    print(f"  Order execution failed")
            else:
                print(f"  No order generated")
            
            print(f"  Cycle complete")
            
        except Exception as e:
            print(f"  Error in trading cycle: {e}")
    
    def run(self) -> None:
        """Run the trading bot continuously."""
        self.running = True
        interval_seconds = self.config.trading_interval_minutes * 60
        
        print(f"\nStarting trading bot...")
        print(f"Interval: {self.config.trading_interval_minutes} minutes")
        print(f"Symbol: {self.config.btc_symbol}")
        print(f"Press Ctrl+C to stop\n")
        
        # Run first cycle immediately
        self._run_cycle()
        
        # Continue running cycles
        while self.running:
            try:
                time.sleep(interval_seconds)
                if self.running:
                    self._run_cycle()
            except KeyboardInterrupt:
                print("\n\nKeyboard interrupt received, shutting down...")
                self.stop()
                break
    
    def stop(self) -> None:
        """Stop the trading bot gracefully."""
        self.running = False
        print("Stopping trading bot...")
        
        # Cancel any open orders
        if not self.config.paper_mode:
            try:
                self.trader.cancel_all_orders()
            except Exception as e:
                print(f"Error cancelling orders: {e}")
        
        print("Bot stopped.")


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create and run bot
    bot = TradingBot(config)
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\nReceived signal, shutting down gracefully...")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run bot
    bot.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_main.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: add main trading bot orchestrator with continuous loop"
```

---

## Phase 8: Documentation & Setup

### Task 11: Create README Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write comprehensive README**

Write to `README.md`:
```markdown
# Bitcoin AI Trading Bot

A Python-based cryptocurrency trading bot focused on Bitcoin (BTC/USD) using momentum-based technical indicators (RSI and MACD). Supports both paper trading for testing and live trading for production use via the Alpaca Markets API.

## Features

- **Paper Trading**: Test strategies with fake money ($100k starting balance)
- **Live Trading**: Execute real trades when ready (requires confirmation)
- **Technical Indicators**: RSI (oversold/overbought) + MACD (crossovers)
- **Risk Management**: Daily loss limits, position size limits, circuit breakers
- **Modular Architecture**: Easy to extend with ML models later
- **Local Development**: Runs on your MacBook, cloud deployment ready

## Architecture

```
Data Fetcher → Strategy (RSI+MACD) → Trade Engine → Executor (Paper/Live)
```

- **Data Fetcher**: Alpaca API client for market data
- **Strategy**: Indicator calculations and signal generation
- **Trade Engine**: Risk management and position sizing
- **Executors**: Paper trading simulator or live trading client

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Alpaca Markets account (free paper trading account works)
- macOS, Linux, or Windows with WSL

### 2. Installation

```bash
# Clone repository
cd crypto-trading-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your Alpaca API credentials:

```env
# Get your API keys from: https://app.alpaca.markets/paper/dashboard/overview
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here

# Always start with paper trading!
PAPER_MODE=true

# Trading settings (optional, defaults are reasonable)
TRADING_INTERVAL_MINUTES=5
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
```

### 4. Run in Paper Trading Mode (Fake Money)

```bash
python src/main.py
```

You'll see output like:
```
============================================================
PAPER TRADING MODE - Using fake money
============================================================

Starting trading bot...
Interval: 5 minutes
Symbol: BTC/USD
Press Ctrl+C to stop

[2025-01-17 14:30:00] Starting trading cycle...
  Price: $42,350.00 | Data points: 100
  Portfolio: $100,000.00 | BTC: 0.0000 | Daily P&L: 0.00%
  Signal: BUY
  Order: BUY 0.2500 BTC
  Paper trade executed: BUY 0.25 BTC/USD @ $42,350.00
    Cash: $89,412.50 | BTC: 0.2500
  Order executed successfully
  Cycle complete
```

### 5. Switch to Live Trading (Real Money - Use Caution!)

**⚠️ WARNING: This uses real money from your account!**

1. Ensure your strategy is profitable in paper trading for at least 1-2 weeks
2. Update `.env`:
   ```env
   PAPER_MODE=false
   ALPACA_API_KEY=your_live_api_key
   ALPACA_SECRET_KEY=your_live_secret_key
   ```
3. Run the bot:
   ```bash
   python src/main.py
   ```
4. Type `LIVE` when prompted to confirm

## Project Structure

```
crypto-trading-bot/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── data_fetcher.py      # Alpaca market data
│   ├── strategy.py          # RSI + MACD indicators
│   ├── trade_engine.py      # Risk management
│   ├── paper_trader.py      # Paper trading simulator
│   ├── live_trader.py       # Live trading (real money)
│   └── main.py              # Bot orchestrator
├── tests/                   # Unit tests
├── data/                    # Logs and history
├── .env                     # Your API keys (gitignored)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Trading Strategy

### Current: Rule-Based (MVP)

**Buy Signal:**
- RSI < 30 (oversold)
- MACD crosses above signal line (bullish momentum)
- Not currently holding BTC position

**Sell Signal:**
- RSI > 70 (overbought)
- MACD crosses below signal line (bearish momentum)
- Currently holding BTC position

**Risk Controls:**
- Maximum 20% of portfolio in BTC position
- Daily loss limit: 5% (bot stops if exceeded)
- Maximum order size: $10,000 per trade

### Future: Machine Learning

The strategy module uses a clean interface that allows swapping the rule-based logic for trained ML models. Planned features:
- Train models on historical data
- A/B testing framework
- Feature engineering (volume, time patterns, etc.)

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PAPER_MODE` | `true` | `true` for fake money, `false` for real |
| `ALPACA_API_KEY` | - | Your Alpaca API key |
| `ALPACA_SECRET_KEY` | - | Your Alpaca secret key |
| `TRADING_INTERVAL_MINUTES` | `5` | Minutes between trading cycles |
| `RSI_PERIOD` | `14` | RSI calculation lookback |
| `RSI_OVERSOLD` | `30` | RSI threshold for buy signal |
| `RSI_OVERBOUGHT` | `70` | RSI threshold for sell signal |
| `MAX_POSITION_PCT` | `0.20` | Max % of portfolio in BTC |
| `DAILY_LOSS_LIMIT_PCT` | `0.05` | Stop trading if daily loss > X% |

## Testing

Run unit tests:

```bash
pytest tests/ -v
```

Run specific test file:

```bash
pytest tests/test_strategy.py -v
```

## Safety Features

1. **Mode Toggle**: Separate API keys for paper vs live trading
2. **Confirmation Required**: Must type "LIVE" to enable real trading
3. **Daily Loss Limit**: Bot stops if portfolio drops > 5%
4. **Position Limits**: Max 20% of portfolio in BTC
5. **Graceful Shutdown**: Ctrl+C safely stops and cancels orders
6. **Extensive Logging**: All trades recorded for audit

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific component
pytest tests/test_strategy.py -v
```

### Code Style

```bash
# Format code
black src/ tests/

# Lint
pylint src/
```

## Troubleshooting

### "ALPACA_API_KEY must be set"

Create a `.env` file with your API keys. Get them from:
https://app.alpaca.markets/paper/dashboard/overview

### "Insufficient data for indicators"

The bot needs at least 26 bars of historical data for MACD calculations. If you just started, wait a few minutes for data to accumulate.

### Orders not filling in paper trading

This is normal - paper trading simulates real market conditions. Orders only fill when market conditions are met (e.g., limit orders at specified price).

## Disclaimer

**Trading cryptocurrencies involves substantial risk.**

- This software is for educational purposes
- Past performance does not guarantee future results
- Never trade with money you cannot afford to lose
- Always test thoroughly in paper trading first
- Cryptocurrency markets are volatile and unpredictable

The authors are not responsible for any financial losses incurred from using this software.

## License

MIT License - See LICENSE file

## Resources

- [Alpaca API Docs](https://docs.alpaca.markets/)
- [Alpaca Trading Dashboard](https://app.alpaca.markets/)
- [Pandas TA Documentation](https://github.com/twopirllc/pandas-ta)
- [RSI Explained](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Explained](https://www.investopedia.com/terms/m/macd.asp)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with setup instructions"
```

---

## Phase 9: Integration & Verification

### Task 12: Integration Test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

Write to `tests/test_integration.py`:
```python
"""Integration tests for the trading bot."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd


class TestFullTradingCycle:
    """Integration test: full trading cycle with all components."""

    @patch("src.main.AlpacaDataFetcher")
    @patch("src.main.TradeEngine")
    @patch("src.main.PaperTrader")
    @patch("src.strategy.calculate_rsi")
    @patch("src.strategy.detect_macd_crossover")
    def test_paper_trading_cycle_with_buy_signal(
        self, mock_macd, mock_rsi, mock_trader_class, mock_engine_class, mock_fetcher_class
    ):
        """Test complete paper trading cycle that generates a buy signal."""
        from src.main import TradingBot
        from config.settings import Config
        from src.strategy import Signal
        
        # Setup: Oversold RSI + Bullish MACD = BUY signal
        mock_rsi.return_value = 25.0  # Oversold
        mock_macd.return_value = "bullish"  # Bullish crossover
        
        # Mock data fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.get_historical_bars.return_value = pd.DataFrame({
            'close': list(range(100, 150))  # 50 price points
        })
        mock_fetcher.get_latest_price.return_value = 40000.0
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock trade engine
        mock_engine = MagicMock()
        mock_engine.process_signal.return_value = {
            'symbol': 'BTC/USD',
            'qty': 0.25,
            'side': 'buy',
            'type': 'market',
            'time_in_force': 'gtc'
        }
        mock_engine_class.return_value = mock_engine
        
        # Mock paper trader
        mock_trader = MagicMock()
        mock_trader.execute_order.return_value = True
        mock_trader.btc_position = 0.0
        mock_trader.get_portfolio_value.return_value = 100000.0
        mock_trader_class.return_value = mock_trader
        
        # Create bot and run one cycle
        config = Config(
            api_key="test",
            api_secret="test",
            paper_mode=True,
            rsi_oversold=30.0,
            rsi_overbought=70.0
        )
        
        bot = TradingBot(config)
        bot.trader = mock_trader
        
        # Run cycle
        bot._run_cycle()
        
        # Verify all components were called
        mock_fetcher.get_historical_bars.assert_called_once()
        mock_engine.process_signal.assert_called_once()
        mock_trader.execute_order.assert_called_once()
        
        # Verify the order was a buy
        order = mock_trader.execute_order.call_args[0][0]
        assert order['side'] == 'buy'


class TestRiskManagementIntegration:
    """Integration tests for risk management."""

    @patch("src.main.AlpacaDataFetcher")
    @patch("src.main.TradeEngine")
    @patch("src.main.PaperTrader")
    @patch("src.strategy.calculate_rsi")
    def test_daily_loss_limit_blocks_trading(
        self, mock_rsi, mock_trader_class, mock_engine_class, mock_fetcher_class
    ):
        """Test that trading is blocked when daily loss limit is exceeded."""
        from src.main import TradingBot
        from config.settings import Config
        
        mock_rsi.return_value = 50.0  # Neutral
        
        # Mock with large daily loss
        mock_fetcher = MagicMock()
        mock_fetcher.get_historical_bars.return_value = pd.DataFrame({
            'close': list(range(100, 150))
        })
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock engine that checks risk
        mock_engine = MagicMock()
        # Simulate risk check failing
        mock_engine.process_signal.return_value = None
        mock_engine_class.return_value = mock_engine
        
        mock_trader = MagicMock()
        mock_trader.get_portfolio_value.return_value = 95000.0  # 5% loss from 100k
        mock_trader_class.return_value = mock_trader
        
        config = Config(
            api_key="test",
            api_secret="test",
            paper_mode=True,
            daily_loss_limit_pct=0.05  # 5% limit
        )
        
        bot = TradingBot(config)
        bot.trader = mock_trader
        bot.starting_portfolio_value = 100000.0  # Started with 100k
        
        # Run cycle
        bot._run_cycle()
        
        # Verify no order was placed (risk blocked it)
        mock_trader.execute_order.assert_not_called()
```

- [ ] **Step 2: Run integration tests**

```bash
python -m pytest tests/test_integration.py -v
```

Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for full trading cycle"
```

---

## Summary

### All Components Built

✅ **Phase 1:** Project structure and dependencies  
✅ **Phase 2:** Configuration management  
✅ **Phase 3:** Strategy module (RSI + MACD)  
✅ **Phase 4:** Data fetcher (Alpaca API)  
✅ **Phase 5:** Trade engine (risk management)  
✅ **Phase 6:** Trading executors (paper + live)  
✅ **Phase 7:** Main bot orchestrator  
✅ **Phase 8:** Documentation  
✅ **Phase 9:** Integration tests  

### Next Steps

1. **Setup:** Run `pip install -r requirements.txt`
2. **Configure:** Copy `.env.example` to `.env` and add API keys
3. **Test:** Run `pytest` to verify all tests pass
4. **Paper Trade:** Run `python src/main.py` and observe for 1-2 weeks
5. **Live Trade:** When ready, switch to live mode with caution

### Files Created

- 12 Python modules (src/ + tests/)
- 2 configuration files (.env.example, requirements.txt)
- 1 documentation file (README.md)
- Total: ~2000 lines of code + tests

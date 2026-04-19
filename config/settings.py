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
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
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

        # Validate numeric environment variables
        try:
            trading_interval_minutes = int(os.getenv("TRADING_INTERVAL_MINUTES", "5"))
        except ValueError:
            raise ValueError(f"TRADING_INTERVAL_MINUTES must be a valid integer, got: {os.getenv('TRADING_INTERVAL_MINUTES')}")

        try:
            rsi_period = int(os.getenv("RSI_PERIOD", "14"))
        except ValueError:
            raise ValueError(f"RSI_PERIOD must be a valid integer, got: {os.getenv('RSI_PERIOD')}")

        try:
            rsi_oversold = float(os.getenv("RSI_OVERSOLD", "30"))
        except ValueError:
            raise ValueError(f"RSI_OVERSOLD must be a valid number, got: {os.getenv('RSI_OVERSOLD')}")

        try:
            rsi_overbought = float(os.getenv("RSI_OVERBOUGHT", "70"))
        except ValueError:
            raise ValueError(f"RSI_OVERBOUGHT must be a valid number, got: {os.getenv('RSI_OVERBOUGHT')}")

        try:
            macd_fast = int(os.getenv("MACD_FAST", "12"))
        except ValueError:
            raise ValueError(f"MACD_FAST must be a valid integer, got: {os.getenv('MACD_FAST')}")

        try:
            macd_slow = int(os.getenv("MACD_SLOW", "26"))
        except ValueError:
            raise ValueError(f"MACD_SLOW must be a valid integer, got: {os.getenv('MACD_SLOW')}")

        try:
            macd_signal = int(os.getenv("MACD_SIGNAL", "9"))
        except ValueError:
            raise ValueError(f"MACD_SIGNAL must be a valid integer, got: {os.getenv('MACD_SIGNAL')}")

        try:
            max_position_pct = float(os.getenv("MAX_POSITION_PCT", "0.20"))
        except ValueError:
            raise ValueError(f"MAX_POSITION_PCT must be a valid number, got: {os.getenv('MAX_POSITION_PCT')}")

        try:
            daily_loss_limit_pct = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "0.05"))
        except ValueError:
            raise ValueError(f"DAILY_LOSS_LIMIT_PCT must be a valid number, got: {os.getenv('DAILY_LOSS_LIMIT_PCT')}")

        try:
            max_order_notional = float(os.getenv("MAX_ORDER_NOTIONAL", "10000"))
        except ValueError:
            raise ValueError(f"MAX_ORDER_NOTIONAL must be a valid number, got: {os.getenv('MAX_ORDER_NOTIONAL')}")

        return cls(
            api_key=api_key,
            api_secret=api_secret,
            paper_mode=paper_mode,
            btc_symbol=os.getenv("BTC_SYMBOL", "BTC/USD"),
            trading_interval_minutes=trading_interval_minutes,
            rsi_period=rsi_period,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
            max_position_pct=max_position_pct,
            daily_loss_limit_pct=daily_loss_limit_pct,
            max_order_notional=max_order_notional,
        )
    
    def get_alpaca_base_url(self) -> str:
        """Get the appropriate Alpaca API base URL based on trading mode.
        
        Returns:
            Base URL for API requests (paper or live).
        """
        if self.paper_mode:
            return "https://paper-api.alpaca.markets"
        return "https://api.alpaca.markets"

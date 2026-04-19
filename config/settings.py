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
    api_key: str = None  # type: ignore
    api_secret: str = None  # type: ignore
    
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
    
    def __post_init__(self):
        """Load from environment if api_key/api_secret not provided."""
        if self.api_key is None or self.api_secret is None:
            loaded = Config.from_env()
            self.api_key = loaded.api_key
            self.api_secret = loaded.api_secret
            self.paper_mode = loaded.paper_mode
            self.btc_symbol = loaded.btc_symbol
            self.trading_interval_minutes = loaded.trading_interval_minutes
            self.rsi_period = loaded.rsi_period
            self.rsi_oversold = loaded.rsi_oversold
            self.rsi_overbought = loaded.rsi_overbought
            self.macd_fast = loaded.macd_fast
            self.macd_slow = loaded.macd_slow
            self.macd_signal = loaded.macd_signal
            self.max_position_pct = loaded.max_position_pct
            self.daily_loss_limit_pct = loaded.daily_loss_limit_pct
            self.max_order_notional = loaded.max_order_notional
    
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

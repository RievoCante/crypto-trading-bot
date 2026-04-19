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
    
    max_position_value = portfolio_value * max_position_pct
    current_position_value = current_btc_position * btc_price
    available_value = max_position_value - current_position_value
    available_value = min(available_value, max_order_notional)
    
    btc_quantity = available_value / btc_price
    btc_quantity = float(Decimal(str(btc_quantity)).quantize(
        Decimal('0.0001'), rounding=ROUND_DOWN
    ))
    
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
    if daily_pnl_pct <= -daily_loss_limit_pct:
        print(f"Risk check failed: Daily loss limit exceeded ({daily_pnl_pct:.2%})")
        return False
    
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
        
        new_btc_value = (current_btc_position + qty) * current_price
        new_position_pct = new_btc_value / portfolio_value if portfolio_value > 0 else 1.0
        
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
        
        new_position_pct = 0.0
        
        if not check_risk_limits(
            daily_pnl_pct=daily_pnl_pct,
            daily_loss_limit_pct=self.config.daily_loss_limit_pct,
            new_position_pct=new_position_pct,
            max_position_pct=self.config.max_position_pct
        ):
            return None
        
        qty = current_btc_position
        
        return {
            'symbol': self.config.btc_symbol,
            'qty': qty,
            'side': 'sell',
            'type': 'market',
            'time_in_force': 'gtc'
        }

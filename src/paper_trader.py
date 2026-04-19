"""Paper trading simulator for testing strategies without real money.

Simulates order execution and tracks portfolio value using real-time
prices but fake funds.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_DOWN


class PaperTrader:
    """Paper trading simulator."""
    
    def __init__(
        self, 
        initial_balance: float = 100000.0,
        initial_btc: float = 0.0
    ):
        """Initialize paper trader with starting balance."""
        self.cash_balance = initial_balance
        self.btc_position = initial_btc
        self.trade_history: List[Dict[str, Any]] = []
    
    def execute_order(
        self, 
        order: Dict[str, Any], 
        fill_price: float
    ) -> bool:
        """Execute an order in paper trading environment."""
        try:
            symbol = order['symbol']
            qty = float(order['qty'])
            side = order['side']
            
            qty = float(Decimal(str(qty)).quantize(
                Decimal('0.0001'), rounding=ROUND_DOWN
            ))
            
            notional = qty * fill_price
            
            if side == 'buy':
                if notional > self.cash_balance:
                    print(f"Insufficient cash: need ${notional:.2f}, have ${self.cash_balance:.2f}")
                    return False
                
                self.cash_balance -= notional
                self.btc_position += qty
                
            elif side == 'sell':
                if qty > self.btc_position:
                    print(f"Insufficient BTC: need {qty}, have {self.btc_position}")
                    return False
                
                self.cash_balance += notional
                self.btc_position -= qty
            
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
        """Calculate total portfolio value."""
        btc_value = self.btc_position * btc_price
        return self.cash_balance + btc_value
    
    def reset(self, initial_balance: float = 100000.0):
        """Reset paper trader to initial state."""
        self.cash_balance = initial_balance
        self.btc_position = 0.0
        self.trade_history = []
        print(f"Paper trader reset: ${initial_balance:,.2f} starting balance")

"""Live trading executor for executing real trades via Alpaca API.

WARNING: This module uses real money. Only initialize when PAPER_MODE=false.
"""
from typing import Dict, Any, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from config.settings import Config


class LiveTrader:
    """Live trading executor.
    
    Executes real trades via Alpaca Trading API. Uses actual funds from
    your brokerage account. Double-check configuration before using.
    """
    
    def __init__(self, config: Config):
        """Initialize live trader with configuration.
        
        Raises:
            RuntimeError: If config has paper_mode=True (safety check)
        """
        self.config = config
        
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
        """Execute a real order via Alpaca Trading API."""
        try:
            symbol = order['symbol']
            qty = order['qty']
            side = order['side']
            order_type = order.get('type', 'market')
            time_in_force = order.get('time_in_force', 'gtc')
            
            side_enum = OrderSide.BUY if side == 'buy' else OrderSide.SELL
            
            tif_map = {
                'gtc': TimeInForce.GTC,
                'ioc': TimeInForce.IOC,
                'day': TimeInForce.DAY
            }
            tif_enum = tif_map.get(time_in_force, TimeInForce.GTC)
            
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
            
            response = self._client.submit_order(order_request)
            
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
        """Get current positions from Alpaca."""
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
        """Get account information from Alpaca."""
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
        """Cancel all open orders."""
        try:
            self._client.cancel_orders()
            print("All open orders cancelled")
            return True
        except Exception as e:
            print(f"Error cancelling orders: {e}")
            return False

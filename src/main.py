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
    and trading executor (paper or live).
    """
    
    def __init__(self, config: Config):
        """Initialize trading bot with configuration."""
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
            
            # Step 2: Extract price data and get latest real-time price
            closes = extract_closes(bars)
            
            # Get latest real-time price (fresher than historical bars)
            latest_price = self.data_fetcher.get_latest_price(self.config.btc_symbol)
            current_price = latest_price if latest_price is not None else closes[-1]
            
            latest_str = f"{latest_price:,.2f}" if latest_price else "N/A"
            print(f"  Price: ${current_price:,.2f} | Data points: {len(closes)} (Live: ${latest_str})")
            
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
                macd_signal=self.config.macd_signal,
                test_mode=self.config.test_mode
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

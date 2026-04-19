# Bitcoin AI Trading Bot

A Python-based cryptocurrency trading bot focused on Bitcoin (BTC/USD) using MACD technical indicators. Supports both paper trading for testing and live trading for production use via the Alpaca Markets API.

## Features

- **Paper Trading**: Test strategies with fake money via Alpaca's paper trading API (trades appear in dashboard)
- **Live Trading**: Execute real trades when ready (requires confirmation)
- **Technical Indicators**: MACD crossovers for momentum-based signals
- **Test Mode**: Force immediate trades to verify bot functionality
- **Risk Management**: Position size limits, daily loss circuit breakers
- **Modular Architecture**: Easy to extend with ML models later
- **Real-Time Prices**: Uses Alpaca's latest quote endpoint for current prices

## Architecture

```
Data Fetcher → Strategy (MACD) → Trade Engine → Alpaca API (Paper/Live)
```

**Key Components:**
- **Data Fetcher**: Gets real-time BTC prices from Alpaca API
- **Strategy**: MACD-only signals (simplified for testing)
- **Trade Engine**: Risk management and position sizing
- **LiveTrader**: Sends orders to Alpaca (works for both paper and live)

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Alpaca Markets account (free paper trading account at https://app.alpaca.markets)

### 2. Installation

```bash
cd crypto-trading-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your Alpaca API credentials from https://app.alpaca.markets/paper/dashboard/overview

### 4. Run in Paper Trading Mode (Fake Money)

```bash
cd /Users/rievo/crypto-trading-bot
python -m src.main
```

You'll see output like:
```
============================================================
PAPER TRADING MODE - Using fake money
============================================================
LiveTrader initialized in PAPER mode (orders go to Alpaca's paper trading system)
Using Alpaca Paper Trading API - trades will appear in dashboard

Starting trading bot...
Interval: 1 minutes
Symbol: BTC/USD
Press Ctrl+C to stop

[2026-04-19 14:16:55] Starting trading cycle...
  Price: $75,260.99 | Data points: 100 (Live: $75,260.99)
  Portfolio: $100,000.00 | BTC: 0.0000 | Daily P&L: 0.00%
  [TEST MODE] Forcing BUY signal for testing
  Signal: BUY
  Order: BUY 0.1328 BTC
  Live order submitted: BUY 0.1328 BTC/USD
    Order ID: d9b1e7d8-b7dc-4302-b70d-9acb064ec349
    Status: OrderStatus.PENDING_NEW
  Order executed successfully
  Cycle complete
```

### 5. View Your Trades

Check your Alpaca paper trading dashboard:
https://app.alpaca.markets/paper/dashboard/overview

You should see:
- Your BTC position under "Top Positions"
- The filled order under "Recent Orders"
- Updated cash balance (~$90,000 after buying $10,000 worth of BTC)

## Trading Strategy

**Current Strategy (MACD-Only for Testing):**

**Buy Signal:**
- MACD crosses above signal line (bullish momentum)
- Not currently holding BTC position

**Sell Signal:**
- MACD crosses below signal line (bearish momentum)
- Currently holding BTC position

**Risk Controls:**
- Maximum 20% of portfolio in BTC position
- Maximum order size: $10,000 per trade
- Daily loss limit: 5%

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PAPER_MODE` | `true` | `true`=paper trading, `false`=real money |
| `TEST_MODE` | `false` | `true`=force immediate trades (for testing) |
| `ALPACA_API_KEY` | - | Your Alpaca API key |
| `ALPACA_SECRET_KEY` | - | Your Alpaca secret key |
| `TRADING_INTERVAL_MINUTES` | `5` | Minutes between trading cycles |
| `MACD_FAST` | `12` | MACD fast EMA period |
| `MACD_SLOW` | `26` | MACD slow EMA period |
| `MACD_SIGNAL` | `9` | MACD signal line period |
| `MAX_POSITION_PCT` | `0.20` | Max % of portfolio in BTC |
| `MAX_ORDER_NOTIONAL` | `10000` | Max order value in USD |
| `DAILY_LOSS_LIMIT_PCT` | `0.05` | Stop trading if daily loss > X% |

### Test Mode

Enable test mode to force immediate trades (ignores MACD signals):

```env
TEST_MODE=true
```

This is useful for verifying the bot works correctly. The bot will:
- BUY immediately if not holding BTC
- SELL immediately if holding BTC

**Disable test mode for actual MACD-based trading:**
```env
TEST_MODE=false
```

## Project Structure

```
crypto-trading-bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management with TEST_MODE
├── src/
│   ├── __init__.py
│   ├── main.py              # Bot orchestrator with Alpaca API integration
│   ├── data_fetcher.py      # Alpaca market data with real-time prices
│   ├── strategy.py          # MACD-only strategy with test mode override
│   ├── trade_engine.py      # Risk management and position sizing
│   ├── paper_trader.py      # Local simulator (not currently used)
│   └── live_trader.py       # Alpaca API executor (paper + live)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_config.py       # Configuration tests
│   ├── test_data_fetcher.py # Data fetcher tests
│   ├── test_strategy.py     # Strategy tests (MACD-only)
│   ├── test_trade_engine.py # Trade engine tests
│   ├── test_paper_trader.py # Paper trader tests
│   ├── test_live_trader.py  # Live trader tests
│   ├── test_main.py         # Main bot tests
│   └── test_integration.py  # Integration tests
├── data/
│   ├── logs/                # Trade logs (local)
│   └── history/             # Trade history (local)
├── docs/
│   ├── design-spec.md       # Design specification
│   └── implementation-plan.md # Implementation plan
├── .env                     # API keys and settings (gitignored)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── README.md              # This file
└── CLAUDE.md              # Agent context for other AI assistants
```

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

1. **Paper Trading First**: All orders go to Alpaca's paper trading system by default
2. **Dashboard Visibility**: Paper trades appear in Alpaca dashboard for verification
3. **Test Mode**: Force trades immediately to verify functionality
4. **Position Limits**: Max 20% of portfolio in BTC, max $10,000 per order
5. **Daily Loss Limit**: Bot stops if portfolio drops > 5% in a day
6. **Live Trading Confirmation**: Must type "LIVE" to enable real money trading
7. **Graceful Shutdown**: Ctrl+C safely stops and cancels pending orders

## Switch to Live Trading (Real Money - Use Extreme Caution!)

⚠️ **WARNING: This uses real money from your account!**

1. **Test thoroughly** in paper trading for 1-2 weeks
2. **Verify** all trades appear correctly in the dashboard
3. **Update** `.env`:
   ```env
   PAPER_MODE=false
   ALPACA_API_KEY=your_live_api_key
   ALPACA_SECRET_KEY=your_live_secret_key
   TEST_MODE=false
   ```
4. **Run** the bot: `python -m src.main`
5. **Confirm** by typing `LIVE` when prompted

## API Keys Setup

Get your API keys from:
- **Paper Trading**: https://app.alpaca.markets/paper/dashboard/overview
- **Live Trading**: https://app.alpaca.markets/live/dashboard/overview

## Troubleshooting

### No trades appearing in dashboard
- Verify `PAPER_MODE=true` in `.env`
- Check that API keys are correct
- Ensure `TEST_MODE=true` for immediate trades
- Look at bot output for error messages

### Price seems wrong (stale data)
- The bot uses Alpaca's latest quote endpoint for real-time prices
- Historical bars can be delayed in free tier
- Live price should match current market (~$75k for BTC)

### Bot shows "HOLD" constantly
- With `TEST_MODE=false`, bot waits for MACD crossovers
- These don't happen every cycle - be patient
- Use `TEST_MODE=true` to force trades for testing

## Performance

- **Latency**: ~100-500ms per API call to Alpaca
- **Intervals**: Configurable (1 minute recommended for testing, 5-15 minutes for production)
- **Rate Limits**: Alpaca allows 200 requests per minute (plenty for this bot)

## Disclaimer

**Trading cryptocurrencies involves substantial risk.**

- This software is for educational purposes
- Past performance does not guarantee future results
- Never trade with money you cannot afford to lose
- Always test thoroughly in paper trading first
- Cryptocurrency markets are volatile and unpredictable

The authors are not responsible for any financial losses incurred from using this software.

## Resources

- [Alpaca API Docs](https://docs.alpaca.markets/)
- [Alpaca Paper Trading Dashboard](https://app.alpaca.markets/paper/dashboard/overview)
- [MACD Explained](https://www.investopedia.com/terms/m/macd.asp)
- [Alpaca Crypto Trading Docs](https://docs.alpaca.markets/docs/crypto-trading)

## License

MIT License - See LICENSE file

## Contributing

This is a personal trading bot project. Feel free to fork and modify for your own use.

---

**Current Status**: ✅ Fully functional with paper trading verified
**Last Updated**: April 2026
**Version**: 1.0.0

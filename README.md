# Bitcoin AI Trading Bot

A Python-based cryptocurrency trading bot focused on Bitcoin (BTC/USD) using momentum-based technical indicators (RSI and MACD). Supports both paper trading for testing and live trading for production use via the Alpaca Markets API.

## Features

- **Paper Trading**: Test strategies with fake money ($100k starting balance)
- **Live Trading**: Execute real trades when ready (requires confirmation)
- **Technical Indicators**: RSI (oversold/overbought) + MACD (crossovers)
- **Risk Management**: Daily loss limits, position size limits, circuit breakers
- **Modular Architecture**: Easy to extend with ML models later
- **Local Development**: Runs on your MacBook

## Architecture

```
Data Fetcher → Strategy (RSI+MACD) → Trade Engine → Executor (Paper/Live)
```

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Alpaca Markets account (free paper trading account works)

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
```

### 5. Switch to Live Trading (Real Money - Use Caution!)

⚠️ **WARNING: This uses real money from your account!**

1. Test thoroughly in paper trading for 1-2 weeks
2. Update `.env`:
   ```env
   PAPER_MODE=false
   ALPACA_API_KEY=your_live_api_key
   ALPACA_SECRET_KEY=your_live_secret_key
   ```
3. Run and type `LIVE` when prompted to confirm

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
│   ├── live_trader.py       # Live trading executor
│   └── main.py              # Bot orchestrator
├── tests/                   # Unit tests
├── data/
│   ├── logs/                # Trade logs
│   └── history/             # Trade history
├── .env                     # API keys (gitignored)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Trading Strategy

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
- Daily loss limit: 5%
- Maximum order size: $10,000 per trade

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PAPER_MODE` | `true` | `true`=fake money, `false`=real money |
| `ALPACA_API_KEY` | - | Your Alpaca API key |
| `ALPACA_SECRET_KEY` | - | Your Alpaca secret key |
| `TRADING_INTERVAL_MINUTES` | `5` | Minutes between cycles |
| `RSI_PERIOD` | `14` | RSI calculation period |
| `RSI_OVERSOLD` | `30` | Buy threshold |
| `RSI_OVERBOUGHT` | `70` | Sell threshold |
| `MAX_POSITION_PCT` | `0.20` | Max % in BTC |
| `DAILY_LOSS_LIMIT_PCT` | `0.05` | Stop if daily loss > X% |

## Testing

Run unit tests:
```bash
pytest tests/ -v
```

## Safety Features

1. **Mode Toggle**: Separate API keys for paper vs live
2. **Confirmation Required**: Must type "LIVE" for real trading
3. **Daily Loss Limit**: Bot stops if portfolio drops > 5%
4. **Position Limits**: Max 20% of portfolio in BTC
5. **Graceful Shutdown**: Ctrl+C safely stops and cancels orders
6. **Extensive Logging**: All trades recorded

## Disclaimer

**Trading cryptocurrencies involves substantial risk.**

- This software is for educational purposes
- Past performance does not guarantee future results
- Never trade with money you cannot afford to lose
- Always test thoroughly in paper trading first

The authors are not responsible for any financial losses incurred from using this software.

## Resources

- [Alpaca API Docs](https://docs.alpaca.markets/)
- [Alpaca Trading Dashboard](https://app.alpaca.markets/)
- [RSI Explained](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Explained](https://www.investopedia.com/terms/m/macd.asp)

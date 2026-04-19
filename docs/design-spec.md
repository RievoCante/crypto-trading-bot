# Bitcoin AI Trading Bot - Design Specification

**Date:** 2025-01-17  
**Status:** Approved for Implementation  
**Scope:** Initial MVP with rule-based strategy (RSI + MACD), extensible for ML later

---

## 1. Overview

### 1.1 Purpose
Build a cryptocurrency trading bot focused on Bitcoin (BTC/USD) using momentum-based technical indicators (RSI and MACD). The bot supports both paper trading (fake money) for strategy testing and live trading (real money) for production use.

### 1.2 Goals
- Provide a safe learning environment for algorithmic trading via paper trading
- Implement a rule-based strategy that can be extended with ML models later
- Ensure safety through risk management controls (loss limits, position sizing)
- Run locally on MacBook during development, with cloud deployment option for production

### 1.3 Non-Goals
- Multi-cryptocurrency support (Bitcoin only for MVP)
- High-frequency trading (target: 5-15 minute intervals)
- Advanced order types (Market and Limit orders only)
- Web dashboard (CLI output for MVP)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ Data Fetcher │ -> │   Strategy   │ -> │ Trade Engine│ -> │  Executor   │
│  (Alpaca API)│    │(RSI + MACD)  │    │ (Paper/Live)│    │  (Logs/Trades)│
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | Key Decisions |
|-----------|---------------|---------------|
| Data Fetcher | Connect to Alpaca API, fetch BTC/USD price data | Use REST API for historical, WebSocket optional for real-time |
| Strategy | Calculate RSI and MACD, generate BUY/SELL/HOLD signals | Rule-based initially, swappable for ML model later |
| Trade Engine | Process signals, calculate position sizes, route to executor | Stateless, receives signal, returns order parameters |
| Paper Trader | Simulate trades, track fake portfolio | Separate module from live trading for safety |
| Live Trader | Execute real orders via Alpaca API | Only activated when PAPER_MODE=false and explicitly confirmed |
| Main Runner | Orchestrate pipeline, handle config, manage lifecycle | Configurable intervals, graceful shutdown |

### 2.3 Data Flow

**Trading Loop (runs every 5-15 minutes):**

1. **Fetch Data** → Get latest BTC/USD price and recent history (OHLCV bars)
2. **Calculate Indicators** → Compute RSI (14-period) and MACD on price data
3. **Generate Signal** → Evaluate strategy rules, return BUY, SELL, or HOLD
4. **Execute Trade** → If signal differs from current position, place order
5. **Log & Monitor** → Record trade details, update portfolio tracking, print status

---

## 3. Trading Strategy

### 3.1 Strategy Logic (Rule-Based MVP)

```
IF (RSI < 30) AND (MACD crosses above Signal Line) AND (not holding BTC):
    → BUY signal
    
IF (RSI > 70) AND (MACD crosses below Signal Line) AND (holding BTC):
    → SELL signal
    
ELSE:
    → HOLD (no action)
```

### 3.2 Parameter Configuration

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| RSI_PERIOD | 14 | Lookback period for RSI calculation |
| RSI_OVERSOLD | 30 | RSI threshold for buy signal |
| RSI_OVERBOUGHT | 70 | RSI threshold for sell signal |
| MACD_FAST | 12 | Fast EMA period for MACD |
| MACD_SLOW | 26 | Slow EMA period for MACD |
| MACD_SIGNAL | 9 | Signal line period for MACD |
| TRADING_INTERVAL | 5 minutes | Time between strategy evaluations |

### 3.3 Future ML Extension

The strategy module will be designed with a clean interface to allow swapping the rule-based logic for a trained ML model:

```python
class StrategyInterface:
    def generate_signal(self, market_data) -> Signal:
        """Return BUY, SELL, or HOLD based on input data"""
        pass
```

---

## 4. Risk Management & Safety

### 4.1 Mode Toggle (Critical Safety Feature)

- **PAPER_MODE=true**: All trades go to paper trading environment (fake money)
- **PAPER_MODE=false**: Trades go to live account (real money)
- Separate API keys for paper and live accounts
- Environment variable `APCA_API_BASE_URL` switches between:
  - Paper: `https://paper-api.alpaca.markets`
  - Live: `https://api.alpaca.markets`

### 4.2 Risk Controls

| Control | Default | Purpose |
|---------|---------|---------|
| Daily Loss Limit | 5% | Stop trading if portfolio drops >5% in a day |
| Position Size Limit | 20% | Maximum 20% of portfolio in BTC position |
| Max Order Size | $10,000 | Single order notional limit |
| Cooldown Period | 1 minute | Minimum time between orders |

### 4.3 Error Handling & Recovery

| Error Type | Response |
|------------|----------|
| API Timeout | Retry with exponential backoff (max 3 attempts) |
| Invalid Signal | Log warning, skip cycle, continue operation |
| Insufficient Funds | Log warning, skip trade, notify user |
| Rate Limit Exceeded | Back off and retry after reset |
| Network Disconnection | Queue signals, reconnect and resume |

### 4.4 Graceful Shutdown

On SIGINT (Ctrl+C) or SIGTERM:
1. Stop fetching new data
2. Complete current trading cycle if safe
3. Cancel any pending orders
4. Save current state to disk
5. Log shutdown event
6. Exit cleanly

---

## 5. Alpaca API Integration

### 5.1 Supported Features

**Trading API:**
- Symbol: `BTC/USD` (Bitcoin to US Dollar)
- Order Types: Market, Limit, Stop Limit
- Time in Force: `gtc` (good till canceled), `ioc` (immediate or cancel)
- Fractional Orders: Yes, minimum 0.0001 BTC
- Trading Hours: 24/7

**Market Data API:**
- Historical Bars: OHLCV data for indicator calculation
- Real-time Data: WebSocket streaming available
- Data Source: Alpaca's own exchange (v1beta3 endpoint)

### 5.2 API Endpoints

| Purpose | URL |
|---------|-----|
| Paper Trading | `https://paper-api.alpaca.markets` |
| Live Trading | `https://api.alpaca.markets` |
| Market Data | `https://data.alpaca.markets` |
| WebSocket | `wss://stream.data.alpaca.markets/v1beta3/crypto/us` |

### 5.3 Fees (Live Trading)

- **Maker Fee**: 15 bps (0.15%) for adding liquidity
- **Taker Fee**: 25 bps (0.25%) for removing liquidity
- Fee charged in the received asset (e.g., buying BTC incurs fee in BTC)

---

## 6. Project Structure

```
crypto-trading-bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration: API keys, thresholds, mode toggle
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py      # Alpaca market data client (REST + WebSocket)
│   ├── strategy.py          # RSI + MACD indicator logic + signal generation
│   ├── trade_engine.py      # Position sizing, risk checks, order preparation
│   ├── paper_trader.py      # Paper trading executor (simulated trades)
│   ├── live_trader.py       # Live trading executor (real orders)
│   └── main.py              # Bot orchestrator, main loop, CLI
├── tests/
│   ├── __init__.py
│   ├── test_strategy.py     # Unit tests for indicator calculations
│   ├── test_data_fetcher.py  # Mock API tests
│   └── test_trade_engine.py  # Risk management tests
├── data/
│   ├── logs/                # Trade and error logs
│   └── history/             # Historical trade data
├── backtest/
│   └── backtest.py          # Historical data testing script
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # Setup and usage instructions
```

---

## 7. Tech Stack

### 7.1 Core Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| alpaca-py | Official Alpaca Python SDK | ^0.20.0 |
| pandas | Data manipulation, time-series | ^2.0.0 |
| numpy | Numerical calculations | ^1.24.0 |
| pandas-ta | Technical analysis indicators | ^0.3.0 |
| python-dotenv | Environment variable management | ^1.0.0 |
| requests | HTTP client (fallback) | ^2.31.0 |
| websocket-client | WebSocket connections | ^1.6.0 |

### 7.2 Development Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| pytest | Unit testing framework | ^7.4.0 |
| pytest-mock | Mocking for tests | ^3.11.0 |
| black | Code formatting | ^23.0.0 |
| pylint | Code linting | ^2.17.0 |

---

## 8. Testing Strategy

### 8.1 Unit Testing

**Components to Test:**
1. **Strategy Module**: 
   - RSI calculation accuracy
   - MACD crossover detection
   - Signal generation with known data
   
2. **Data Fetcher**:
   - API response parsing
   - Error handling (timeouts, invalid responses)
   - Data transformation to DataFrame
   
3. **Trade Engine**:
   - Position sizing calculations
   - Risk limit enforcement
   - Order parameter generation

### 8.2 Paper Trading Tests

**Duration:** 1-2 weeks  
**Objectives:**
- Verify strategy generates expected signals
- Confirm order execution flow
- Validate portfolio tracking accuracy
- Test error recovery mechanisms

**Success Criteria:**
- No crashes during 2-week period
- Accurate trade logging
- Signals align with indicator calculations

### 8.3 Backtesting

**Approach:**
- Fetch 6+ months of BTC/USD historical data from Alpaca
- Simulate trades using historical prices
- Calculate performance metrics:
  - Win rate (% of profitable trades)
  - Profit/Loss ratio
  - Maximum drawdown
  - Sharpe ratio

---

## 9. Deployment

### 9.1 Local Development (MacBook)

**Setup:**
1. Create Python virtual environment
2. Install dependencies from requirements.txt
3. Configure .env file with API keys
4. Set PAPER_MODE=true for testing
5. Run: `python src/main.py`

### 9.2 Future Cloud Deployment (Optional)

**Platform Options:**
- AWS EC2 (t3.micro or t3.small)
- DigitalOcean Droplet
- Google Cloud Run

**Considerations:**
- 24/7 uptime for continuous trading
- Environment variable management for secrets
- Log aggregation and monitoring
- Automatic restart on failure

---

## 10. Security Considerations

### 10.1 API Key Management

- Store API keys in `.env` file (gitignored)
- Never commit keys to version control
- Use separate keys for paper and live trading
- Rotate keys periodically

### 10.2 Operational Security

- Run bot in paper mode for extended testing before live trading
- Implement daily loss limits as circuit breakers
- Log all trading activity for audit trail
- Keep software dependencies updated

### 10.3 Data Privacy

- No user data collected beyond trading activity
- Logs stored locally only
- No third-party analytics or tracking

---

## 11. Monitoring & Logging

### 11.1 Logged Events

| Event Type | Information Logged |
|------------|-------------------|
| Signal Generated | Timestamp, signal type, indicator values, price |
| Order Placed | Order ID, symbol, side, quantity, type, price |
| Order Filled | Fill price, quantity, fees, timestamp |
| Error | Error type, stack trace, context |
| Shutdown | Reason, final portfolio state |

### 11.2 CLI Output

Real-time display in terminal:
```
[2025-01-17 14:30:00] Fetching BTC/USD data...
[2025-01-17 14:30:01] Price: $42,350.00 | RSI: 28.5 | MACD: -45.2
[2025-01-17 14:30:01] SIGNAL: BUY (RSI oversold + MACD crossing up)
[2025-01-17 14:30:02] Order placed: BUY 0.023 BTC @ market
[2025-01-17 14:30:03] Order filled: Bought 0.023 BTC @ $42,348.50
[2025-01-17 14:30:03] Portfolio: $50,000 USD | 0.023 BTC ($973.62)
```

---

## 12. Future Enhancements

### 12.1 ML Integration (Phase 2)

- Train supervised learning model on historical features
- Features: RSI, MACD, volume, price action patterns, time of day
- Model types to evaluate: Random Forest, XGBoost, LSTM
- A/B testing framework comparing rule-based vs ML performance

### 12.2 Additional Features (Phase 3)

- Web dashboard for monitoring (Flask/Streamlit)
- Multi-cryptocurrency support (ETH, SOL)
- Telegram/Discord bot notifications
- Advanced order types (stop-loss, trailing stop)
- Strategy optimization via backtesting engine

---

## 13. Success Metrics

### 13.1 MVP Success Criteria

- [ ] Bot runs continuously in paper mode without crashes for 2 weeks
- [ ] Strategy generates BUY/SELL signals aligned with RSI/MACD rules
- [ ] All trades logged accurately with timestamps and prices
- [ ] Risk controls (loss limits, position sizing) function correctly
- [ ] Clean transition from paper to live trading (user confirmation required)

### 13.2 Performance Benchmarks

**Paper Trading Targets:**
- Win rate: >45% (momentum strategies typically 40-55%)
- Risk-adjusted return: Positive Sharpe ratio
- Maximum drawdown: <10%

---

## 14. Open Questions & Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| WebSocket vs REST for data? | Start with REST polling | Simpler implementation, switch to WebSocket if latency becomes issue |
| SQLite vs file logs? | File logs for MVP | Simpler, easier to inspect; migrate to DB if needed |
| Docker containerization? | Not for MVP | Adds complexity; add if deploying to cloud |
| Telegram notifications? | Post-MVP | Focus on core functionality first |

---

## 15. Approval

**Design Status:** ✅ Approved for Implementation  
**Approved By:** User  
**Next Step:** Create implementation plan via writing-plans skill

---

## Appendix A: Alpaca Crypto Trading Notes

### A.1 Supported Symbols

Query available assets:
```bash
curl --request GET 'https://api.alpaca.markets/v2/assets?asset_class=crypto' \
--header 'Apca-Api-Key-Id: <KEY>' \
--header 'Apca-Api-Secret-Key: <SECRET>'
```

### A.2 Example Order

```bash
curl --request POST 'https://paper-api.alpaca.markets/v2/orders' \
--header 'Apca-Api-Key-Id: <KEY>' \
--header 'Apca-Api-Secret-Key: <SECRET>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "symbol": "BTC/USD",
  "qty": "0.0001",
  "side": "buy",
  "type": "market",
  "time_in_force": "gtc"
}'
```

### A.3 Market Data Example

```bash
curl 'https://data.alpaca.markets/v1beta3/crypto/us/latest/orderbooks?symbols=BTC/USD'
```

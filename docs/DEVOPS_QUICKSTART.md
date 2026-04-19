# 🚀 DevOps Quickstart - Monitor Your Trading Bot

## Essential Commands (Memorize These!)

### 1. Check If Bot Is Running
```bash
docker ps --filter "name=crypto-trading-bot"
```
**What to see:** `STATUS: Up X minutes` ✅
**Red flag:** `STATUS: Exited` or empty ❌

### 2. View Real-Time Logs
```bash
docker logs -f crypto-trading-bot
```
**What to watch for:**
- ✅ "Signal: BUY/SELL" → Trade happening
- ✅ "Order executed successfully" → Trade completed
- ⚠️ "Error" → Something wrong
- ⚠️ "HOLD" → Waiting for signal (normal)

### 3. Check Resource Usage
```bash
docker stats crypto-trading-bot --no-stream
```
**Good signs:**
- CPU: 0-5% (normal)
- Memory: <200MB (good)
- Network: Active (fetching prices)

**Bad signs:**
- CPU: >50% constantly (problem)
- Memory: Growing continuously (memory leak)

### 4. Interactive Dashboard
```bash
./monitor.sh
```
**Shows:**
- Live container status
- Trade count
- Recent activity
- Resource usage
- Latest signal

Press `Ctrl+C` to exit.

---

## Common Scenarios

### Scenario 1: "Is my bot still running?"
```bash
# Quick check
docker ps | grep crypto-trading-bot

# Detailed check
docker inspect --format='{{.State.Status}}' crypto-trading-bot
```

### Scenario 2: "Why did my bot stop?"
```bash
# Check logs for errors
docker logs --tail 100 crypto-trading-bot 2>&1 | grep -i "error"

# Check exit code
docker inspect crypto-trading-bot --format='{{.State.ExitCode}}'

# Common exit codes:
# 0 = Stopped normally
# 1 = Error/crash
# 137 = Out of memory
# 143 = Container killed
```

### Scenario 3: "How many trades has my bot made?"
```bash
# Count all successful trades
docker logs crypto-trading-bot 2>&1 | grep "Order executed successfully" | wc -l

# See buy vs sell
docker logs crypto-trading-bot 2>&1 | grep "Signal: BUY" | wc -l
docker logs crypto-trading-bot 2>&1 | grep "Signal: SELL" | wc -l
```

### Scenario 4: "I want to see trades in real-time"
```bash
# Watch for trades only
docker logs -f crypto-trading-bot 2>&1 | grep -E "(BUY|SELL|Order)"
```

---

## Troubleshooting Flowchart

```
Bot not working?
    │
    ├── Check: docker ps
    │   ├── Running? → Check logs
    │   └── Stopped? → Check exit code
    │
    ├── Check: docker logs
    │   ├── Errors? → Fix error, restart
    │   ├── No trades? → Enable TEST_MODE
    │   └── HOLD signals? → Wait for MACD
    │
    └── Check: docker stats
        ├── High CPU? → Check for infinite loops
        ├── High memory? → Restart container
        └── No network? → Check internet
```

---

## Daily Checklist (2 Minutes)

Run this every morning:

```bash
# 1. Quick status
echo "=== Bot Status ==="
docker ps --filter "name=crypto-trading-bot" --format "{{.Names}}: {{.Status}}"

# 2. Trade count
echo "=== Trades Today ==="
docker logs --since 24h crypto-trading-bot 2>&1 | grep "Order executed" | wc -l

# 3. Errors
echo "=== Errors ==="
docker logs --since 24h crypto-trading-bot 2>&1 | grep -i "error" | wc -l
```

---

## Advanced Monitoring

### Health Check Status
```bash
docker inspect --format='{{.State.Health.Status}}' crypto-trading-bot
```
**Values:**
- `healthy` ✅ All checks passed
- `unhealthy` ❌ Too many failures
- `starting` ⏳ Still initializing

### Restart History
```bash
docker inspect --format='{{.RestartCount}}' crypto-trading-bot
```
**What it means:**
- 0 = No restarts (good)
- 1+ = Container crashed and was restarted

### Resource Limits
```bash
# Check if hitting limits
docker stats --no-stream --format "CPU: {{.CPUPerc}} | Mem: {{.MemPerc}} | Limit: {{.MemLimit}}"
```

---

## Monitoring Best Practices

### ✅ DO:
- Check logs daily for errors
- Monitor trade count to ensure activity
- Watch memory usage (should be stable ~100MB)
- Set up alerts (see docs/MONITORING.md)
- Persist logs outside container

### ❌ DON'T:
- Ignore error messages in logs
- Let logs fill up disk (use log rotation)
- Run without monitoring for days
- Ignore high CPU/memory usage

---

## Quick Fixes

### Restart Bot
```bash
docker restart crypto-trading-bot
```

### Stop Bot
```bash
docker-compose down
```

### Start Bot
```bash
docker-compose up -d
```

### Get Shell Inside Container
```bash
docker exec -it crypto-trading-bot /bin/bash
```

---

## Dashboard Access

View your trades:
- **Paper Trading**: https://app.alpaca.markets/paper/dashboard/overview
- **Live Trading**: https://app.alpaca.markets/live/dashboard/overview

---

## Learn More

Full monitoring guide:
```bash
cat docs/MONITORING.md
```

---

**Remember: Good DevOps = Prevent problems, don't just react to them!**

Monitor proactively, not just when things break.

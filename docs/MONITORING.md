# DevOps Monitoring Guide for Crypto Trading Bot

## Essential Docker Commands

### Container Status
```bash
# Check if container is running
docker ps --filter "name=crypto-trading-bot"

# Check all containers (including stopped)
docker ps -a --filter "name=crypto-trading-bot"

# View container stats (CPU, memory, network)
docker stats crypto-trading-bot --no-stream

# Continuous monitoring
docker stats crypto-trading-bot
```

### Logs
```bash
# View recent logs
docker logs --tail 100 crypto-trading-bot

# Follow logs in real-time (like tail -f)
docker logs -f crypto-trading-bot

# View logs with timestamps
docker logs --tail 50 --timestamps crypto-trading-bot

# Search for specific events
docker logs crypto-trading-bot 2>&1 | grep -E "(BUY|SELL|Error|Order)"
```

### Health Checks
```bash
# Check container health
docker inspect --format='{{.State.Status}}' crypto-trading-bot

# Check exit code (if stopped)
docker inspect --format='{{.State.ExitCode}}' crypto-trading-bot

# Check when container started
docker inspect --format='{{.State.StartedAt}}' crypto-trading-bot

# Check restart count
docker inspect --format='{{.RestartCount}}' crypto-trading-bot
```

### Resource Usage
```bash
# Memory usage
docker exec crypto-trading-bot ps aux --sort=-%mem

# Disk usage
docker system df -v

# Container size
docker ps --size --filter "name=crypto-trading-bot"
```

## Advanced Monitoring

### Check Trading Activity
```bash
# Watch for trades in real-time
watch -n 5 'docker logs --tail 20 crypto-trading-bot 2>&1 | grep -E "(BUY|SELL|Order)"'

# Count successful trades
docker logs crypto-trading-bot 2>&1 | grep "Order executed successfully" | wc -l

# Check for errors
docker logs crypto-trading-bot 2>&1 | grep -i "error" | tail -20
```

### Environment Variables
```bash
# Check bot configuration
docker exec crypto-trading-bot printenv | grep -E "(PAPER|TEST|TRADING)"

# Check Python version in container
docker exec crypto-trading-bot python --version

# Check installed packages
docker exec crypto-trading-bot pip list
```

### Network Monitoring
```bash
# Check network connectivity
docker exec crypto-trading-bot ping -c 3 data.alpaca.markets

# Check open connections
docker exec crypto-trading-bot netstat -an

# Check DNS resolution
docker exec crypto-trading-bot nslookup data.alpaca.markets
```

## Log Management

### Persist Logs
Logs are already stored in:
- Host: `./data/logs/`
- Container: `/app/data/logs/`

### Rotate Logs
```bash
# Current log file size
ls -lh data/logs/

# Compress old logs
gzip data/logs/trade_*.log

# Clean up old logs (keep last 30 days)
find data/logs/ -name "*.log" -mtime +30 -delete
```

## Troubleshooting

### If Container Stops
```bash
# Check why it stopped
docker logs --tail 100 crypto-trading-bot 2>&1 | tail -50

# Check exit code
docker inspect crypto-trading-bot --format='{{.State.ExitCode}}'

# Common exit codes:
# 0 = Success
# 1 = General error
# 137 = Out of memory (OOM)
# 143 = Container stopped
```

### Restart Container
```bash
# Restart with docker-compose
docker-compose restart

# Or with docker
docker restart crypto-trading-bot

# View restart logs
docker logs --tail 50 crypto-trading-bot
```

## Monitoring Dashboard

### Create a Simple Dashboard
```bash
#!/bin/bash
# save as: monitor.sh

while true; do
    clear
    echo "=== Crypto Trading Bot Monitor ==="
    echo "Time: $(date)"
    echo ""
    
    # Container Status
    STATUS=$(docker inspect --format='{{.State.Status}}' crypto-trading-bot 2>/dev/null || echo "NOT FOUND")
    echo "Status: $STATUS"
    
    # Recent Activity
    echo ""
    echo "--- Recent Activity ---"
    docker logs --tail 10 crypto-trading-bot 2>&1 | tail -5
    
    # Trade Count
    echo ""
    echo "--- Trade Count ---"
    TRADES=$(docker logs crypto-trading-bot 2>&1 | grep "Order executed successfully" | wc -l)
    echo "Total trades: $TRADES"
    
    # Errors
    ERRORS=$(docker logs crypto-trading-bot 2>&1 | grep -i "error" | wc -l)
    echo "Total errors: $ERRORS"
    
    sleep 5
done
```

## Alerting

### Basic Alerting Script
```bash
#!/bin/bash
# save as: alert.sh

# Check if container is running
if ! docker ps | grep -q "crypto-trading-bot"; then
    echo "ALERT: Container is not running!"
    # Send email/notification here
fi

# Check for errors in last 5 minutes
RECENT_ERRORS=$(docker logs --since 5m crypto-trading-bot 2>&1 | grep -c "Error")
if [ "$RECENT_ERRORS" -gt 0 ]; then
    echo "ALERT: $RECENT_ERRORS errors in last 5 minutes!"
fi
```

## Best Practices

1. **Always monitor logs** - Use `docker logs -f` when testing
2. **Check resource usage** - CPU/memory should be stable
3. **Set up alerts** - Know immediately if bot stops
4. **Persist logs** - Keep trade history outside container
5. **Use health checks** - Docker can auto-restart on failure
6. **Monitor disk space** - Logs can fill up disk over time

## Quick Health Check

Run this one-liner for instant status:
```bash
docker ps --filter "name=crypto-trading-bot" --format "{{.Names}}: {{.Status}} ({{.RunningFor}})" && docker stats --no-stream --format "CPU: {{.CPUPerc}} | RAM: {{.MemUsage}}" crypto-trading-bot
```

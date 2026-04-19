#!/bin/bash
# Crypto Trading Bot Monitor
# Usage: ./monitor.sh

CONTAINER_NAME="crypto-trading-bot"
REFRESH_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear_screen() {
    printf "\033c"  # Clear screen properly
}

print_header() {
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║       🚀 CRYPTO TRADING BOT - MONITORING DASHBOARD        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

check_container_status() {
    local status=$(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME 2>/dev/null || echo "NOT FOUND")
    local exit_code=$(docker inspect --format='{{.State.ExitCode}}' $CONTAINER_NAME 2>/dev/null || echo "N/A")
    local started=$(docker inspect --format='{{.State.StartedAt}}' $CONTAINER_NAME 2>/dev/null | cut -d'T' -f2 | cut -d'.' -f1 || echo "N/A")
    
    echo "📊 CONTAINER STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ "$status" == "running" ]; then
        echo -e "Status: ${GREEN}✅ RUNNING${NC}"
        echo "Started: $started"
    elif [ "$status" == "exited" ]; then
        echo -e "Status: ${RED}❌ STOPPED (Exit Code: $exit_code)${NC}"
        if [ "$exit_code" == "137" ]; then
            echo -e "${RED}⚠️  Container stopped due to Out of Memory (OOM)${NC}"
        elif [ "$exit_code" == "1" ]; then
            echo -e "${RED}⚠️  Container crashed with error${NC}"
        fi
    elif [ "$status" == "NOT FOUND" ]; then
        echo -e "Status: ${RED}❌ CONTAINER NOT FOUND${NC}"
    else
        echo -e "Status: ${YELLOW}⚠️  $status${NC}"
    fi
    echo ""
}

show_resource_usage() {
    local stats=$(docker stats --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}|{{.PIDs}}" $CONTAINER_NAME 2>/dev/null)
    
    if [ -n "$stats" ]; then
        IFS='|' read -r cpu mem netio pids <<< "$stats"
        
        echo "💻 RESOURCE USAGE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "CPU Usage:    $cpu"
        echo "Memory:       $mem"
        echo "Network I/O:  $netio"
        echo "Processes:    $pids"
        echo ""
    fi
}

show_recent_activity() {
    echo "📈 RECENT ACTIVITY (Last 5 Cycles)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Get recent logs
    local logs=$(docker logs --tail 30 $CONTAINER_NAME 2>&1 | grep -E "(Starting trading cycle|Signal:|Order:|executed|Error)" | tail -10)
    
    if [ -n "$logs" ]; then
        echo "$logs"
    else
        echo "No recent activity..."
    fi
    echo ""
}

show_trade_stats() {
    echo "💰 TRADE STATISTICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count successful trades
    local buy_trades=$(docker logs $CONTAINER_NAME 2>&1 | grep -c "Signal: BUY" 2>/dev/null || echo 0)
    local sell_trades=$(docker logs $CONTAINER_NAME 2>&1 | grep -c "Signal: SELL" 2>/dev/null || echo 0)
    local total_trades=$((buy_trades + sell_trades))
    
    # Count errors
    local errors=$(docker logs $CONTAINER_NAME 2>&1 | grep -c "Error" 2>/dev/null || echo 0)
    
    echo "Buy Orders:   $buy_trades"
    echo "Sell Orders:  $sell_trades"
    echo -e "Total Trades: ${GREEN}$total_trades${NC}"
    
    if [ "$errors" -gt 0 ]; then
        echo -e "Errors:       ${RED}$errors${NC}"
    else
        echo -e "Errors:       ${GREEN}0${NC} ✅"
    fi
    echo ""
}

show_latest_signal() {
    echo "🔔 LATEST SIGNAL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local last_signal=$(docker logs --tail 50 $CONTAINER_NAME 2>&1 | grep "Signal:" | tail -1)
    local last_price=$(docker logs --tail 50 $CONTAINER_NAME 2>&1 | grep "Price:" | tail -1)
    
    if [ -n "$last_signal" ]; then
        if echo "$last_signal" | grep -q "BUY"; then
            echo -e "${GREEN}$last_signal${NC} 🟢"
        elif echo "$last_signal" | grep -q "SELL"; then
            echo -e "${RED}$last_signal${NC} 🔴"
        else
            echo -e "${YELLOW}$last_signal${NC} ⚪"
        fi
    fi
    
    if [ -n "$last_price" ]; then
        echo "$last_price"
    fi
    echo ""
}

show_config() {
    echo "⚙️  CONFIGURATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local paper_mode=$(docker exec $CONTAINER_NAME printenv PAPER_MODE 2>/dev/null || echo "unknown")
    local test_mode=$(docker exec $CONTAINER_NAME printenv TEST_MODE 2>/dev/null || echo "unknown")
    local interval=$(docker exec $CONTAINER_NAME printenv TRADING_INTERVAL_MINUTES 2>/dev/null || echo "unknown")
    
    echo "Paper Mode:   $paper_mode"
    echo "Test Mode:    $test_mode"
    echo "Interval:     ${interval}m"
    echo ""
}

show_help() {
    echo ""
    echo "📖 QUICK COMMANDS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Logs:        docker logs -f $CONTAINER_NAME"
    echo "Restart:     docker restart $CONTAINER_NAME"
    echo "Stop:        docker-compose down"
    echo "Start:       docker-compose up -d"
    echo "Shell:       docker exec -it $CONTAINER_NAME /bin/bash"
    echo ""
    echo "Press Ctrl+C to exit monitor"
}

# Main loop
echo "Starting monitor for $CONTAINER_NAME..."
echo "Refresh interval: ${REFRESH_INTERVAL}s"
echo ""
sleep 1

while true; do
    clear_screen
    print_header
    check_container_status
    show_config
    show_resource_usage
    show_latest_signal
    show_recent_activity
    show_trade_stats
    show_help
    
    sleep $REFRESH_INTERVAL
done

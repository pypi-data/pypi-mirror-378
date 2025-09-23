# GeneBot CLI Inline Help Examples

## Enhanced Help System

The GeneBot CLI includes an enhanced help system with comprehensive examples and interactive guidance.

### Interactive Help System

```bash
# Launch interactive help
genebot help --interactive

# Get help for specific command
genebot help add-crypto --examples

# Show configuration examples
genebot config-help --examples
```

## Command Examples by Category

### Account Management Examples

#### Adding Crypto Exchange Accounts

```bash
# Interactive mode (recommended for beginners)
genebot add-crypto

# Binance testnet account
genebot add-crypto binance --name binance-test --mode demo \
  --api-key $BINANCE_TEST_KEY --api-secret $BINANCE_TEST_SECRET

# Coinbase Pro live account
genebot add-crypto coinbase --name coinbase-main --mode live \
  --api-key $COINBASE_KEY --api-secret $COINBASE_SECRET \
  --api-passphrase $COINBASE_PASSPHRASE

# Kraken with custom settings
genebot add-crypto kraken --name kraken-eu --mode live \
  --api-key $KRAKEN_KEY --api-secret $KRAKEN_SECRET \
  --rate-limit 900 --timeout 45
```

#### Adding Forex Broker Accounts

```bash
# OANDA demo account
genebot add-forex oanda --name oanda-demo --mode demo \
  --api-key $OANDA_DEMO_KEY --account-id $OANDA_DEMO_ACCOUNT

# MetaTrader 5 demo
genebot add-forex mt5 --name mt5-demo --mode demo \
  --server "Demo-Server" --login 12345678 --password $MT5_PASSWORD

# Interactive Brokers paper trading
genebot add-forex ib --name ib-paper --mode demo \
  --host 127.0.0.1 --port 7497 --client-id 1
```

#### Account Management

```bash
# List all accounts with status
genebot list-accounts

# List only crypto accounts
genebot list-accounts --type crypto

# List only active accounts
genebot list-accounts --status active

# Validate all accounts
genebot validate-accounts

# Validate specific account with detailed output
genebot validate-accounts --account binance-test --detailed

# Edit account interactively
genebot edit-crypto binance-test --interactive

# Enable/disable accounts
genebot enable-account binance-test
genebot disable-account oanda-demo
```

### Bot Control Examples

#### Starting the Bot

```bash
# Start with all configured accounts and strategies
genebot start

# Start with specific strategy
genebot start --strategy arbitrage

# Start with specific accounts
genebot start --account binance-test --account oanda-demo

# Start in foreground for debugging
genebot start --foreground --verbose

# Start with custom configuration
genebot start --config config/custom_config.yaml

# Dry run to test configuration
genebot start --dry-run
```

#### Multi-Instance Management

```bash
# Start named instances for different strategies
genebot start-instance crypto-arb --strategy crypto_arbitrage \
  --account binance-test --account coinbase-test

genebot start-instance forex-trend --strategy trend_following \
  --account oanda-demo

# List all running instances
genebot list-instances

# Check specific instance status
genebot instance-status crypto-arb --detailed

# View instance logs
genebot instance-logs crypto-arb --lines 50 --follow

# Stop specific instance
genebot stop-instance crypto-arb

# Restart instance with new configuration
genebot restart-instance forex-trend --config config/forex_only.yaml
```

#### Bot Status and Control

```bash
# Basic status
genebot status

# Detailed status with metrics
genebot status --detailed

# Status in JSON format for scripts
genebot status --json

# Comprehensive status with resource usage
genebot comprehensive-status --detailed

# Stop bot gracefully
genebot stop

# Force stop if unresponsive
genebot stop --force --timeout 30

# Restart with new configuration
genebot restart --config config/updated_config.yaml
```

### Configuration Examples

#### Configuration Initialization

```bash
# Initialize with development template
genebot init-config --template development

# Initialize with production template
genebot init-config --template production

# Initialize minimal configuration
genebot init-config --template minimal

# Overwrite existing configuration
genebot init-config --template production --overwrite
```

#### Configuration Management

```bash
# Show configuration help
genebot config-help

# Show configuration examples
genebot config-help --examples

# Validate all configuration files
genebot validate-config

# Validate with detailed output
genebot validate-config --verbose

# Show configuration status
genebot config-status

# Backup configuration
genebot config-backup

# Restore from backup
genebot config-restore --timestamp 2024-01-15_14-30-00

# Migrate configuration to latest version
genebot config-migrate --version latest
```

#### System Validation

```bash
# Comprehensive system validation
genebot system-validate

# Detailed system validation
genebot system-validate --verbose

# Validate and fix issues
genebot system-validate --fix-issues

# Health check
genebot health-check

# Health check with automatic fixes
genebot health-check --fix
```

### Monitoring and Reporting Examples

#### Real-Time Monitoring

```bash
# Basic monitoring
genebot monitor

# Monitor with 10-second refresh
genebot monitor --refresh 10

# Monitor specific account
genebot monitor --account binance-test

# Monitor with alerts enabled
genebot monitor --alerts --refresh 5
```

#### Trading History

```bash
# Show last 20 trades
genebot trades

# Show last 50 trades
genebot trades --limit 50

# Show trades for specific account
genebot trades --account binance-test --limit 30

# Show trades from last 7 days
genebot trades --days 7

# Export trades to CSV
genebot trades --days 30 --format csv --output trades_january.csv
```

#### Report Generation

```bash
# Generate summary report
genebot report summary

# Generate detailed performance report
genebot report performance --days 30

# Generate compliance report
genebot report compliance --days 90 --format pdf --output compliance_q1.pdf

# Generate strategy-specific report
genebot report strategy --strategy arbitrage --days 14

# Generate P&L report with charts
genebot report pnl --days 30 --format html --charts --output pnl_report.html
```

#### Advanced Analytics

```bash
# Performance analytics
genebot analytics performance --days 30

# Risk analysis
genebot analytics risk --days 14 --format json --output risk_analysis.json

# Correlation analysis
genebot analytics correlation --days 60

# Attribution analysis
genebot analytics attribution --days 30 --format html --output attribution.html

# Portfolio optimization
genebot analytics optimization --days 90
```

#### Backtesting Analytics

```bash
# Analyze backtest results
genebot backtest-analytics results/backtest_2024_01.json

# Generate HTML report from backtest
genebot backtest-analytics results/strategy_test.json \
  --format html --output reports/backtest_analysis.html

# Generate PDF report
genebot backtest-analytics results/multi_strategy.json \
  --format pdf --output reports/backtest_report.pdf
```

### Utility Examples

#### Order Management

```bash
# Close all orders with confirmation
genebot close-all-orders

# Close orders for specific account
genebot close-all-orders --account binance-test

# Close orders with extended timeout
genebot close-all-orders --timeout 600

# Force close all orders
genebot close-all-orders --force
```

#### System Maintenance

```bash
# Backup all configurations
genebot backup-config

# Backup to specific directory
genebot backup-config --output backups/manual_backup_$(date +%Y%m%d)

# Reset system (with confirmation)
genebot reset

# Reset keeping configuration
genebot reset --keep-config --confirm

# Reset everything without confirmation
genebot reset --confirm
```

### Security Examples

#### Security Management

```bash
# Security scan
genebot security --scan

# Fix security issues
genebot security --fix

# Generate security audit
genebot security --audit --export security_audit_$(date +%Y%m%d).json

# Rotate API keys
genebot security --rotate-keys
```

### Error Handling Examples

#### Diagnostics and Recovery

```bash
# Run comprehensive diagnostics
genebot diagnostics --verbose

# Diagnose specific component
genebot diagnostics --component database

# Export diagnostic report
genebot diagnostics --export diagnostic_report.json

# Generate error report
genebot error-report --start-date $(date -d '7 days ago' +%Y-%m-%d)

# System recovery
genebot system-recovery --component all

# Recover from backup
genebot system-recovery --backup-date 2024-01-15
```

## Advanced Usage Patterns

### Scripting Examples

#### Daily Operations Script

```bash
#!/bin/bash
# daily_operations.sh

echo "Starting daily GeneBot operations..."

# Health check
if ! genebot health-check --quiet; then
    echo "Health check failed, attempting fixes..."
    genebot health-check --fix
fi

# Validate accounts
if ! genebot validate-accounts --quiet; then
    echo "Account validation failed, check configurations"
    exit 1
fi

# Start bot if not running
if ! genebot status --quiet; then
    echo "Starting trading bot..."
    genebot start --background
fi

# Generate daily report
genebot report summary --days 1 --format html \
  --output "reports/daily_$(date +%Y%m%d).html"

echo "Daily operations completed successfully"
```

#### Monitoring Script

```bash
#!/bin/bash
# monitor_bot.sh

# Continuous monitoring with alerts
while true; do
    # Check bot status
    if ! genebot status --quiet; then
        echo "$(date): Bot is not running, attempting restart..."
        genebot start --background
        
        # Send alert (customize as needed)
        echo "GeneBot restarted at $(date)" | mail -s "GeneBot Alert" admin@company.com
    fi
    
    # Check system health
    if ! genebot health-check --quiet; then
        echo "$(date): Health check failed"
        genebot diagnostics --component system --export "diagnostics_$(date +%Y%m%d_%H%M%S).json"
    fi
    
    # Wait 5 minutes
    sleep 300
done
```

#### Backup Script

```bash
#!/bin/bash
# backup_script.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configurations
genebot backup-config --output "$BACKUP_DIR"

# Export current status
genebot status --json > "$BACKUP_DIR/status.json"

# Export recent trades
genebot trades --days 7 --format json > "$BACKUP_DIR/recent_trades.json"

# Generate reports
genebot report summary --days 30 --format json > "$BACKUP_DIR/monthly_summary.json"

echo "Backup completed: $BACKUP_DIR"
```

### Integration Examples

#### Python Integration

```python
#!/usr/bin/env python3
# genebot_integration.py

import subprocess
import json
import sys

def run_genebot_command(command):
    """Run a GeneBot CLI command and return the result"""
    try:
        result = subprocess.run(
            ['genebot'] + command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None

def get_bot_status():
    """Get bot status as JSON"""
    output = run_genebot_command(['status', '--json'])
    if output:
        return json.loads(output)
    return None

def start_bot_if_needed():
    """Start bot if it's not running"""
    status = get_bot_status()
    if not status or not status.get('running', False):
        print("Starting bot...")
        run_genebot_command(['start', '--background'])
        return True
    return False

def generate_daily_report():
    """Generate and return daily report"""
    return run_genebot_command(['report', 'summary', '--days', '1', '--format', 'json'])

if __name__ == "__main__":
    # Check and start bot
    if start_bot_if_needed():
        print("Bot started successfully")
    
    # Get current status
    status = get_bot_status()
    if status:
        print(f"Bot uptime: {status.get('uptime', 'Unknown')}")
        print(f"Active accounts: {len(status.get('accounts', []))}")
    
    # Generate report
    report = generate_daily_report()
    if report:
        print("Daily report generated successfully")
```

#### Webhook Integration

```bash
#!/bin/bash
# webhook_handler.sh

# Handle webhook notifications
case "$1" in
    "start")
        genebot start --background
        ;;
    "stop")
        genebot stop --timeout 60
        ;;
    "status")
        genebot status --json
        ;;
    "report")
        genebot report summary --days 1 --format json
        ;;
    *)
        echo "Usage: $0 {start|stop|status|report}"
        exit 1
        ;;
esac
```

## Help System Features

### Interactive Help

The CLI includes an interactive help system:

```bash
# Launch interactive help
genebot help --interactive

# Navigate through topics:
# 1. Account Management
# 2. Bot Control
# 3. Configuration
# 4. Monitoring & Reports
# 5. Troubleshooting
# 6. Examples
```

### Context-Sensitive Help

```bash
# Get help for specific command
genebot add-crypto --help

# Show examples for command
genebot help add-crypto --examples

# Show configuration help
genebot config-help --section accounts
```

### Command Completion

```bash
# Install bash completion
genebot completion --install

# Generate completion script
genebot completion --generate --shell bash > /etc/bash_completion.d/genebot

# For zsh users
genebot completion --generate --shell zsh > ~/.zsh/completions/_genebot
```

This enhanced help system provides comprehensive examples and guidance for all CLI operations, making it easier for users to learn and use GeneBot effectively.
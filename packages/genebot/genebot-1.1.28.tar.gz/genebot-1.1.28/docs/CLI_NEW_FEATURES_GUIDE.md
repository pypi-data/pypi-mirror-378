# GeneBot CLI New Features and Workflows Guide

## Table of Contents

1. [Overview of New Features](#overview-of-new-features)
2. [Real Data Integration](#real-data-integration)
3. [Multi-Instance Management](#multi-instance-management)
4. [Advanced Monitoring](#advanced-monitoring)
5. [Enhanced Analytics](#enhanced-analytics)
6. [Security Features](#security-features)
7. [Configuration Management](#configuration-management)
8. [Error Handling and Recovery](#error-handling-and-recovery)
9. [Interactive Help System](#interactive-help-system)
10. [Workflow Examples](#workflow-examples)
11. [Best Practices](#best-practices)

## Overview of New Features

The refactored GeneBot CLI introduces numerous enhancements that transform it from a basic command-line tool into a comprehensive trading bot management platform.

### Key Improvements

- **Real Data Integration**: All commands now work with actual data instead of mock data
- **Multi-Instance Support**: Run multiple bot instances with different configurations
- **Advanced Monitoring**: Real-time monitoring with metrics and alerts
- **Enhanced Analytics**: Comprehensive performance and risk analysis
- **Security Enhancements**: Secure credential management and validation
- **Interactive Help**: Context-aware help system with examples
- **Process Management**: Robust bot lifecycle management with health monitoring
- **Configuration Templates**: Pre-built configurations for different use cases

## Real Data Integration

### Account Validation with Live API Testing

The new CLI performs actual API connectivity tests instead of basic configuration validation.

```bash
# Test real API connectivity
genebot validate-accounts --detailed

# Example output:
# ✅ binance-main: Connected successfully
#    - Balance: 1.5 BTC, 10.2 ETH, 5000 USDT
#    - Permissions: Spot Trading, Margin Trading
#    - Rate Limit: 1200/min (current: 45/min)
#
# ❌ coinbase-test: Connection failed
#    - Error: Invalid API credentials
#    - Suggestion: Check API key and secret in .env file
#    - Last successful connection: 2024-01-14 15:30:00
```

### Real-Time Trading Data

Access actual trading data from your database:

```bash
# View recent trades with real P&L
genebot trades --limit 10

# Example output:
# Recent Trades (Last 10)
# ┌─────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
# │ Timestamp           │ Pair     │ Side     │ Amount   │ Price    │ P&L      │
# ├─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
# │ 2024-01-15 10:30:15 │ BTC/USDT │ BUY      │ 0.1      │ 42,500   │ +125.50  │
# │ 2024-01-15 10:25:30 │ ETH/USDT │ SELL     │ 2.5      │ 2,650    │ +87.25   │
# └─────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
# 
# Total P&L (24h): +$1,247.85
# Win Rate: 68.5%
# Active Positions: 3
```

### Live Process Management

The CLI now manages actual bot processes with PID tracking:

```bash
# Start bot with real process management
genebot start --background

# Check actual process status
genebot status --detailed

# Example output:
# Bot Status: Running ✅
# ┌─────────────────┬─────────────────────────────────────┐
# │ Property        │ Value                               │
# ├─────────────────┼─────────────────────────────────────┤
# │ Process ID      │ 12345                               │
# │ Uptime          │ 2h 15m 30s                         │
# │ Memory Usage    │ 245.7 MB                           │
# │ CPU Usage       │ 3.2%                               │
# │ Active Accounts │ 3 (binance, coinbase, oanda)       │
# │ Active Orders   │ 7                                   │
# │ Last Activity   │ 2024-01-15 10:32:45                │
# └─────────────────┴─────────────────────────────────────┘
```

## Multi-Instance Management

### Running Multiple Bot Instances

Run different strategies or account groups simultaneously:

```bash
# Start crypto arbitrage instance
genebot start-instance crypto-arb \
  --strategy crypto_arbitrage \
  --account binance-main \
  --account coinbase-pro

# Start forex trend following instance
genebot start-instance forex-trend \
  --strategy trend_following \
  --account oanda-live \
  --account ib-paper

# Start conservative portfolio instance
genebot start-instance conservative \
  --strategy mean_reversion \
  --config config/conservative.yaml
```

### Instance Management

```bash
# List all running instances
genebot list-instances

# Example output:
# Running Bot Instances
# ┌─────────────────┬─────────┬──────────────────┬─────────────┬──────────────┐
# │ Instance        │ Status  │ Strategy         │ Accounts    │ Uptime       │
# ├─────────────────┼─────────┼──────────────────┼─────────────┼──────────────┤
# │ crypto-arb      │ Running │ crypto_arbitrage │ 2           │ 1h 45m       │
# │ forex-trend     │ Running │ trend_following  │ 2           │ 45m          │
# │ conservative    │ Stopped │ mean_reversion   │ 1           │ -            │
# └─────────────────┴─────────┴──────────────────┴─────────────┴──────────────┘

# Check specific instance status
genebot instance-status crypto-arb --detailed

# View instance logs
genebot instance-logs crypto-arb --follow

# Stop specific instance
genebot stop-instance forex-trend
```

### Instance-Specific Configuration

Each instance can have its own configuration:

```yaml
# config/crypto_arb.yaml
instance_name: "crypto-arb"
strategies:
  crypto_arbitrage:
    enabled: true
    min_profit_threshold: 0.005
    max_position_size: 1000
    
accounts:
  - binance-main
  - coinbase-pro
  
risk_management:
  max_daily_loss: 0.01
  position_size_limit: 0.05
```

## Advanced Monitoring

### Real-Time Monitoring Dashboard

```bash
# Launch real-time monitoring
genebot monitor --refresh 5

# Example output (updates every 5 seconds):
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           GeneBot Live Monitor                               ║
# ║                        Last Update: 2024-01-15 10:35:22                     ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║ System Status                                                                ║
# ║ • Bot Status: Running (3 instances)                                         ║
# ║ • Memory Usage: 512.3 MB / 2.0 GB (25.6%)                                  ║
# ║ • CPU Usage: 8.5%                                                           ║
# ║ • Network: Connected (latency: 45ms)                                        ║
# ║                                                                              ║
# ║ Trading Activity (Last 5 minutes)                                           ║
# ║ • Orders Placed: 12                                                         ║
# ║ • Orders Filled: 8                                                          ║
# ║ • P&L: +$127.45                                                             ║
# ║ • Volume: $45,230                                                           ║
# ║                                                                              ║
# ║ Account Status                                                               ║
# ║ • binance-main: ✅ Connected (Balance: $12,450)                             ║
# ║ • coinbase-pro: ✅ Connected (Balance: $8,750)                              ║
# ║ • oanda-live: ⚠️  High latency (Balance: $5,200)                            ║
# ║                                                                              ║
# ║ Active Strategies                                                            ║
# ║ • crypto_arbitrage: 🟢 Active (P&L: +$89.25)                               ║
# ║ • trend_following: 🟢 Active (P&L: +$38.20)                                ║
# ║ • mean_reversion: 🔴 Paused (Risk limit reached)                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
```

### Monitoring Specific Components

```bash
# Monitor specific account
genebot monitor --account binance-main --refresh 10

# Monitor with alerts
genebot monitor --alerts --refresh 5

# Monitor specific strategy
genebot monitor --strategy crypto_arbitrage
```

### Performance Metrics

```bash
# Get detailed performance metrics
genebot instance-metrics crypto-arb

# Example output:
# Performance Metrics - crypto-arb
# ┌─────────────────────┬─────────────┬─────────────┬─────────────┐
# │ Metric              │ 1H          │ 24H         │ 7D          │
# ├─────────────────────┼─────────────┼─────────────┼─────────────┤
# │ Total P&L           │ +$127.45    │ +$1,247.85  │ +$8,945.20  │
# │ Win Rate            │ 72.5%       │ 68.5%       │ 71.2%       │
# │ Sharpe Ratio        │ 2.15        │ 1.87        │ 2.03        │
# │ Max Drawdown        │ -$45.20     │ -$234.50    │ -$456.80    │
# │ Trades Executed     │ 23          │ 187         │ 1,245       │
# │ Average Trade Size  │ $1,250      │ $1,180      │ $1,205      │
# │ Risk-Adjusted ROI   │ 15.2%       │ 12.8%       │ 14.5%       │
# └─────────────────────┴─────────────┴─────────────┴─────────────┘
```

## Enhanced Analytics

### Performance Analytics

```bash
# Comprehensive performance analysis
genebot analytics performance --days 30

# Example output:
# Performance Analytics Report (30 Days)
# ═══════════════════════════════════════
# 
# Overall Performance
# • Total Return: +18.5%
# • Annualized Return: +67.2%
# • Sharpe Ratio: 2.15
# • Sortino Ratio: 3.28
# • Maximum Drawdown: -5.2%
# • Calmar Ratio: 12.9
# 
# Risk Metrics
# • Value at Risk (95%): -$234.50
# • Expected Shortfall: -$345.20
# • Beta (vs BTC): 0.65
# • Correlation (vs Market): 0.42
# 
# Trade Statistics
# • Total Trades: 1,247
# • Win Rate: 71.2%
# • Average Win: +$89.45
# • Average Loss: -$42.30
# • Profit Factor: 2.85
# • Largest Win: +$456.80
# • Largest Loss: -$123.45
```

### Risk Analysis

```bash
# Detailed risk analysis
genebot analytics risk --days 14

# Portfolio correlation analysis
genebot analytics correlation --days 60

# Strategy attribution analysis
genebot analytics attribution --days 30
```

### Custom Analytics

```bash
# Export analytics data for custom analysis
genebot analytics performance --days 90 \
  --format json --output analytics_q1.json

# Generate HTML report with charts
genebot analytics performance --days 30 \
  --format html --charts --output performance_report.html
```

## Security Features

### Security Scanning

```bash
# Comprehensive security scan
genebot security --scan

# Example output:
# Security Scan Results
# ═══════════════════════
# 
# ✅ Configuration Files
# • File permissions: Secure (600)
# • No plain-text credentials found
# • Environment variables properly used
# 
# ⚠️  API Keys
# • binance-main: Excessive permissions detected
#   - Recommendation: Disable withdrawal permissions
# • coinbase-pro: ✅ Properly configured
# 
# ✅ Network Security
# • All connections use HTTPS/TLS
# • Certificate validation enabled
# • No insecure protocols detected
# 
# 🔧 Recommendations
# 1. Rotate API keys older than 90 days
# 2. Enable 2FA on all exchange accounts
# 3. Review API key permissions quarterly
```

### Credential Management

```bash
# Rotate API keys
genebot security --rotate-keys

# Generate security audit report
genebot security --audit --export security_audit.json

# Fix detected security issues
genebot security --fix
```

### Secure Configuration

```bash
# Validate file permissions
genebot security --scan --component permissions

# Check for credential exposure
genebot security --scan --component credentials

# Audit access logs
genebot security --audit --component access
```

## Configuration Management

### Configuration Templates

```bash
# Initialize with different templates
genebot init-config --template production
genebot init-config --template development
genebot init-config --template minimal

# List available templates
genebot config-help --templates
```

### Configuration Validation

```bash
# Comprehensive configuration validation
genebot validate-config --strict

# Example output:
# Configuration Validation Results
# ══════════════════════════════════
# 
# ✅ accounts.yaml
# • Syntax: Valid YAML
# • Schema: Compliant
# • Accounts: 3 configured, 3 valid
# 
# ✅ trading_bot_config.yaml
# • Syntax: Valid YAML
# • Schema: Compliant
# • Strategies: 4 configured, 4 enabled
# 
# ⚠️  .env file
# • Missing: OANDA_ACCOUNT_ID
# • Recommendation: Add missing environment variable
# 
# 🔧 Suggestions
# 1. Add OANDA_ACCOUNT_ID to .env file
# 2. Consider enabling email notifications
# 3. Update risk limits for production use
```

### Configuration Migration

```bash
# Migrate configuration to latest version
genebot config-migrate --version latest

# Show migration plan without applying
genebot config-migrate --dry-run

# Migrate specific configuration file
genebot config-migrate --file accounts.yaml
```

### Backup and Restore

```bash
# Create configuration backup
genebot config-backup

# Restore from specific backup
genebot config-restore --timestamp 2024-01-15_14-30-00

# List available backups
genebot config-restore --list
```

## Error Handling and Recovery

### Comprehensive Diagnostics

```bash
# Run full system diagnostics
genebot diagnostics --verbose

# Example output:
# System Diagnostics Report
# ═══════════════════════════
# 
# 🔍 System Health
# • OS: macOS 14.2.1 (darwin)
# • Python: 3.11.5
# • Memory: 8.2 GB available
# • Disk Space: 125 GB free
# • Network: Connected (45ms latency)
# 
# 🔍 GeneBot Components
# • CLI Version: 1.1.15
# • Configuration: Valid
# • Database: Connected (trading_bot.db)
# • Log Files: Accessible
# 
# 🔍 External Services
# • Binance API: ✅ Connected (12ms)
# • Coinbase API: ✅ Connected (28ms)
# • OANDA API: ⚠️  Slow response (156ms)
# 
# 🔧 Recommendations
# 1. Consider upgrading OANDA connection
# 2. Archive old log files (>100MB detected)
# 3. Update Python to latest version
```

### Automatic Error Recovery

```bash
# Enable automatic error recovery
genebot start --auto-recover

# System recovery for specific components
genebot system-recovery --component database

# Full system recovery
genebot system-recovery --all
```

### Error Reporting

```bash
# Generate comprehensive error report
genebot error-report --days 7

# Export error analysis
genebot error-report --export error_analysis.json

# View error trends
genebot error-report --trends --days 30
```

## Interactive Help System

### Context-Aware Help

```bash
# Launch interactive help system
genebot help --interactive

# Interactive menu:
# ┌─────────────────────────────────────────┐
# │           GeneBot Help System           │
# ├─────────────────────────────────────────┤
# │ 1. Getting Started                      │
# │ 2. Account Management                   │
# │ 3. Bot Control & Monitoring             │
# │ 4. Configuration & Setup                │
# │ 5. Analytics & Reporting                │
# │ 6. Troubleshooting                      │
# │ 7. Advanced Features                    │
# │ 8. Examples & Tutorials                 │
# │ 9. Exit                                 │
# └─────────────────────────────────────────┘
# Select option (1-9):
```

### Command-Specific Examples

```bash
# Get examples for specific command
genebot help add-crypto --examples

# Show configuration examples
genebot config-help --examples --section accounts

# Interactive command builder
genebot help --build-command add-crypto
```

### Smart Suggestions

The CLI now provides intelligent suggestions based on context:

```bash
# When a command fails, get smart suggestions
genebot start
# Error: No accounts configured
# 
# 💡 Suggestions:
# 1. Add a crypto exchange: genebot add-crypto binance --mode demo
# 2. Add a forex broker: genebot add-forex oanda --mode demo
# 3. Initialize configuration: genebot init-config --template development
# 4. View setup guide: genebot help --interactive
```

## Workflow Examples

### Daily Trading Workflow

```bash
#!/bin/bash
# daily_trading_workflow.sh

echo "🚀 Starting daily GeneBot workflow..."

# 1. System health check
echo "📊 Checking system health..."
if ! genebot health-check --quiet; then
    echo "⚠️  Health issues detected, attempting fixes..."
    genebot health-check --fix
fi

# 2. Validate all accounts
echo "🔐 Validating account connections..."
if ! genebot validate-accounts --quiet; then
    echo "❌ Account validation failed"
    genebot validate-accounts --detailed
    exit 1
fi

# 3. Check if bot is running
echo "🤖 Checking bot status..."
if ! genebot status --quiet; then
    echo "🔄 Starting trading bot..."
    genebot start --background
    sleep 10  # Wait for startup
fi

# 4. Generate morning report
echo "📈 Generating daily report..."
genebot report summary --days 1 \
  --format html --charts \
  --output "reports/daily_$(date +%Y%m%d).html"

# 5. Start monitoring (optional)
if [[ "$1" == "--monitor" ]]; then
    echo "👀 Starting live monitoring..."
    genebot monitor --refresh 30
fi

echo "✅ Daily workflow completed successfully!"
```

### Strategy Development Workflow

```bash
#!/bin/bash
# strategy_development_workflow.sh

STRATEGY_NAME="$1"
if [[ -z "$STRATEGY_NAME" ]]; then
    echo "Usage: $0 <strategy_name>"
    exit 1
fi

echo "🧪 Strategy Development Workflow: $STRATEGY_NAME"

# 1. Create test configuration
echo "⚙️  Creating test configuration..."
genebot init-config --template development \
  --output "config/test_${STRATEGY_NAME}.yaml"

# 2. Add demo accounts for testing
echo "🔧 Setting up demo accounts..."
genebot add-crypto binance --name "binance-${STRATEGY_NAME}" \
  --mode demo --config "config/test_${STRATEGY_NAME}.yaml"

# 3. Start test instance
echo "🚀 Starting test instance..."
genebot start-instance "test-${STRATEGY_NAME}" \
  --config "config/test_${STRATEGY_NAME}.yaml" \
  --strategy "$STRATEGY_NAME"

# 4. Monitor for 1 hour
echo "📊 Monitoring test run for 1 hour..."
timeout 3600 genebot instance-logs "test-${STRATEGY_NAME}" --follow &
MONITOR_PID=$!

sleep 3600

# 5. Stop test and generate report
echo "🛑 Stopping test instance..."
genebot stop-instance "test-${STRATEGY_NAME}"

# 6. Generate test report
echo "📋 Generating test report..."
genebot analytics performance --days 1 \
  --format html --output "reports/test_${STRATEGY_NAME}_$(date +%Y%m%d).html"

echo "✅ Strategy test completed!"
```

### Production Deployment Workflow

```bash
#!/bin/bash
# production_deployment_workflow.sh

echo "🚀 Production Deployment Workflow"

# 1. Backup current configuration
echo "💾 Creating configuration backup..."
genebot config-backup --output "backups/pre_deployment_$(date +%Y%m%d_%H%M%S)"

# 2. Validate production configuration
echo "🔍 Validating production configuration..."
if ! genebot validate-config --strict; then
    echo "❌ Configuration validation failed"
    exit 1
fi

# 3. Security scan
echo "🔒 Running security scan..."
if ! genebot security --scan --quiet; then
    echo "⚠️  Security issues detected"
    genebot security --scan
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 4. Validate all accounts with live API
echo "🔐 Validating live account connections..."
if ! genebot validate-accounts --detailed; then
    echo "❌ Account validation failed"
    exit 1
fi

# 5. Stop existing bot instances
echo "🛑 Stopping existing instances..."
genebot stop --force --timeout 30

# 6. Start production instances
echo "🚀 Starting production instances..."

# Start main trading instance
genebot start-instance "production-main" \
  --config "config/production.yaml" \
  --strategy "multi_strategy"

# Start monitoring instance
genebot start-instance "production-monitor" \
  --config "config/monitoring.yaml" \
  --strategy "monitoring_only"

# 7. Verify deployment
echo "✅ Verifying deployment..."
sleep 30  # Wait for startup

if genebot status --detailed; then
    echo "🎉 Production deployment successful!"
    
    # Send notification (customize as needed)
    genebot report summary --days 1 --format json | \
      jq '.deployment_status = "successful"' > deployment_status.json
else
    echo "❌ Deployment verification failed"
    exit 1
fi
```

## Best Practices

### Security Best Practices

1. **Use Environment Variables for Credentials**
   ```bash
   # Store in .env file
   echo "BINANCE_API_KEY=your_key_here" >> .env
   echo "BINANCE_API_SECRET=your_secret_here" >> .env
   
   # Set proper permissions
   chmod 600 .env
   ```

2. **Regular Security Audits**
   ```bash
   # Weekly security scan
   genebot security --scan --audit
   
   # Monthly key rotation
   genebot security --rotate-keys
   ```

3. **Limit API Permissions**
   ```bash
   # Validate API permissions
   genebot validate-accounts --detailed
   
   # Check for excessive permissions
   genebot security --scan --component permissions
   ```

### Performance Best Practices

1. **Monitor Resource Usage**
   ```bash
   # Regular health checks
   genebot health-check
   
   # Monitor instance metrics
   genebot instance-metrics production-main
   ```

2. **Optimize Configuration**
   ```bash
   # Use appropriate rate limits
   genebot edit-crypto binance --field rate_limit --value 1000
   
   # Set reasonable timeouts
   genebot edit-crypto binance --field timeout --value 30
   ```

3. **Regular Maintenance**
   ```bash
   # Clean up old logs
   genebot reset --logs
   
   # Backup configurations
   genebot config-backup
   ```

### Operational Best Practices

1. **Use Configuration Templates**
   ```bash
   # Development environment
   genebot init-config --template development
   
   # Production environment
   genebot init-config --template production
   ```

2. **Implement Monitoring**
   ```bash
   # Set up continuous monitoring
   genebot monitor --refresh 60 --alerts
   
   # Generate regular reports
   genebot report summary --days 1 --format html
   ```

3. **Test Before Production**
   ```bash
   # Always test with demo accounts first
   genebot add-crypto binance --mode demo
   genebot validate-accounts --account binance-demo
   ```

4. **Use Multi-Instance Architecture**
   ```bash
   # Separate instances for different strategies
   genebot start-instance crypto-arb --strategy arbitrage
   genebot start-instance forex-trend --strategy trend_following
   ```

5. **Implement Error Recovery**
   ```bash
   # Enable automatic recovery
   genebot start --auto-recover
   
   # Regular diagnostics
   genebot diagnostics --verbose
   ```

The new GeneBot CLI provides a comprehensive platform for managing sophisticated trading operations. These features enable professional-grade trading bot management with enterprise-level reliability and security.
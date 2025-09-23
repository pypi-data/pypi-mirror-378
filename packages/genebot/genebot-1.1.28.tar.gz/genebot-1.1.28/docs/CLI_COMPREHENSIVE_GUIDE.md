# GeneBot CLI Comprehensive Guide v1.1.28

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Complete Command Reference](#complete-command-reference)
5. [Configuration Management](#configuration-management)
6. [Account Management](#account-management)
7. [Strategy Management](#strategy-management)
8. [Bot Process Management](#bot-process-management)
9. [Orchestrator System](#orchestrator-system)
10. [Monitoring and Analytics](#monitoring-and-analytics)
11. [Security Features](#security-features)
12. [Advanced Features](#advanced-features)
13. [Integration Guide](#integration-guide)
14. [Troubleshooting](#troubleshooting)

## Overview

The GeneBot CLI is a comprehensive command-line interface for managing your advanced multi-market trading bot. Version 1.1.28 represents the complete integration and finalization of all system components, providing:

- **Complete System Integration**: All components work seamlessly together with validated connections
- **Advanced Strategy Engine**: 20+ built-in strategies with machine learning and arbitrage capabilities
- **Multi-Market Excellence**: Full crypto and forex integration with cross-market arbitrage
- **Orchestrator System**: Advanced strategy orchestration with intelligent allocation management
- **Production Ready**: Comprehensive testing and validation for enterprise deployment

### Key Features

- **Multi-Market Trading**: Crypto exchanges and forex brokers with unified management
- **Advanced Strategies**: Technical analysis, machine learning, and arbitrage strategies
- **Strategy Orchestration**: Intelligent allocation and rebalancing across multiple strategies
- **Real-Time Monitoring**: Live trading activity with comprehensive dashboards
- **Risk Management**: Advanced position sizing, correlation analysis, and drawdown protection
- **Security & Compliance**: Secure credential handling, audit trails, and regulatory compliance
- **Performance Analytics**: Comprehensive backtesting and real-time performance analysis
- **Process Management**: Advanced bot lifecycle management with health monitoring

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Access to trading accounts (exchanges/brokers)

### Installation Steps

1. **Install GeneBot Package**
   ```bash
   pip install genebot
   ```

2. **Verify Installation**
   ```bash
   genebot --version
   ```

3. **Initialize Configuration**
   ```bash
   genebot init-config
   ```

4. **Set Up Command Completion (Optional)**
   ```bash
   genebot completion --install
   source ~/.bashrc  # or restart your shell
   ```

### Directory Structure

After initialization, GeneBot creates the following structure:

```
.
├── config/
│   ├── accounts.yaml           # Account configurations
│   ├── trading_bot_config.yaml # Main bot configuration
│   ├── compliance_config.yaml  # Compliance settings
│   └── monitoring_config.yaml  # Monitoring configuration
├── logs/
│   ├── cli.log                 # CLI operation logs
│   ├── trading.log             # Trading activity logs
│   └── errors/                 # Error logs
├── reports/                    # Generated reports
├── backups/                    # Configuration backups
└── .env                        # Environment variables
```

## Quick Start Guide

### 1. First-Time Setup

```bash
# Initialize configuration
genebot init-config

# Add your first crypto exchange (interactive)
genebot add-crypto

# Add a forex broker (interactive)
genebot add-forex

# Validate all accounts
genebot validate-accounts

# Start the trading bot
genebot start
```

### 2. Basic Operations

```bash
# Check bot status
genebot status

# Monitor live trading
genebot monitor

# View recent trades
genebot trades

# Generate performance report
genebot report --type performance

# Stop the bot
genebot stop
```

### 3. Account Management

```bash
# List all accounts
genebot list-accounts

# List available exchanges
genebot list-exchanges

# List available brokers
genebot list-brokers

# Enable/disable accounts
genebot enable-account binance crypto
genebot disable-account oanda forex
```

## Command Reference

### Global Options

All commands support these global options:

```bash
--verbose, -v          # Verbose output
--quiet, -q           # Quiet mode (minimal output)
--no-color            # Disable colored output
--config-path PATH    # Custom configuration directory
--log-level LEVEL     # Set logging level (DEBUG, INFO, WARNING, ERROR)
--dry-run             # Show what would be done without executing
--output-file FILE    # Save output to file
```

### Account Management Commands

#### `genebot add-crypto`
Add a cryptocurrency exchange account.

```bash
genebot add-crypto [OPTIONS]

Options:
  --name TEXT              Account name
  --exchange TEXT          Exchange type (binance, coinbase, kraken, etc.)
  --api-key TEXT          API key
  --api-secret TEXT       API secret
  --api-passphrase TEXT   API passphrase (Coinbase only)
  --sandbox               Use sandbox/testnet mode
  --enabled               Enable account immediately
  --force                 Overwrite existing account
  --rate-limit INTEGER    Rate limit per minute
  --timeout INTEGER       Request timeout in seconds
```

**Examples:**
```bash
# Interactive mode
genebot add-crypto

# Command line mode
genebot add-crypto --name binance-main --exchange binance \
  --api-key $BINANCE_KEY --api-secret $BINANCE_SECRET --enabled

# Sandbox account
genebot add-crypto --name binance-test --exchange binance \
  --api-key $BINANCE_TEST_KEY --api-secret $BINANCE_TEST_SECRET \
  --sandbox --enabled
```

#### `genebot add-forex`
Add a forex broker account.

```bash
genebot add-forex [OPTIONS]

Options:
  --name TEXT           Account name
  --broker TEXT         Broker type (oanda, mt5, interactive_brokers)
  --api-key TEXT        API key (OANDA)
  --account-id TEXT     Account ID (OANDA)
  --server TEXT         Server (MT5)
  --login TEXT          Login (MT5)
  --password TEXT       Password (MT5)
  --host TEXT           Host (Interactive Brokers)
  --port INTEGER        Port (Interactive Brokers)
  --client-id INTEGER   Client ID (Interactive Brokers)
  --sandbox             Use sandbox mode
  --enabled             Enable account immediately
  --force               Overwrite existing account
```

**Examples:**
```bash
# OANDA demo account
genebot add-forex --name oanda-demo --broker oanda \
  --api-key $OANDA_KEY --account-id $OANDA_ACCOUNT --sandbox

# MetaTrader 5
genebot add-forex --name mt5-demo --broker mt5 \
  --server Demo-Server --login 12345678 --password $MT5_PASSWORD
```

#### `genebot list-accounts`
Display all configured accounts.

```bash
genebot list-accounts [OPTIONS]

Options:
  --type TYPE          Filter by account type (crypto, forex)
  --status STATUS      Filter by status (enabled, disabled)
  --format FORMAT      Output format (table, json, yaml)
  --show-credentials   Show masked credentials (admin only)
```

#### `genebot validate-accounts`
Validate account configurations and test API connectivity.

```bash
genebot validate-accounts [OPTIONS]

Options:
  --account TEXT       Validate specific account
  --type TYPE          Validate accounts of specific type
  --fix-issues         Attempt to fix common issues
  --detailed           Show detailed validation results
```

#### `genebot edit-crypto` / `genebot edit-forex`
Edit existing account configurations.

```bash
genebot edit-crypto ACCOUNT_NAME [OPTIONS]
genebot edit-forex ACCOUNT_NAME [OPTIONS]

Options:
  --interactive        Use interactive editor
  --field FIELD        Edit specific field
  --value VALUE        New value for field
```

#### `genebot remove-account`
Remove an account configuration.

```bash
genebot remove-account ACCOUNT_NAME TYPE [OPTIONS]

Options:
  --force              Skip confirmation prompt
  --backup             Create backup before removal
```

#### `genebot enable-account` / `genebot disable-account`
Enable or disable accounts.

```bash
genebot enable-account ACCOUNT_NAME TYPE
genebot disable-account ACCOUNT_NAME TYPE [OPTIONS]

Options:
  --reason TEXT        Reason for disabling (logged)
```

### Bot Control Commands

#### `genebot start`
Start the trading bot.

```bash
genebot start [OPTIONS]

Options:
  --config FILE        Custom configuration file
  --strategy TEXT      Specific strategy to run
  --accounts TEXT      Comma-separated list of accounts to use
  --dry-run           Start in simulation mode
  --background        Run in background (daemon mode)
  --pid-file FILE     Custom PID file location
```

#### `genebot stop`
Stop the trading bot.

```bash
genebot stop [OPTIONS]

Options:
  --force              Force stop (SIGKILL)
  --timeout INTEGER    Graceful shutdown timeout (seconds)
  --save-state         Save current state before stopping
```

#### `genebot restart`
Restart the trading bot.

```bash
genebot restart [OPTIONS]

Options:
  --force              Force restart
  --config FILE        Use different configuration
  --wait-time INTEGER  Wait time between stop and start
```

#### `genebot status`
Show bot status and health information.

```bash
genebot status [OPTIONS]

Options:
  --detailed           Show detailed status information
  --json               Output in JSON format
  --watch              Continuously monitor status
  --refresh INTEGER    Refresh interval for watch mode
```

### Advanced Process Management

#### `genebot start-instance`
Start a named bot instance.

```bash
genebot start-instance INSTANCE_NAME [OPTIONS]

Options:
  --config FILE        Instance-specific configuration
  --strategy TEXT      Strategy for this instance
  --accounts TEXT      Accounts for this instance
```

#### `genebot list-instances`
List all running bot instances.

```bash
genebot list-instances [OPTIONS]

Options:
  --format FORMAT      Output format (table, json)
  --show-config        Show instance configurations
```

#### `genebot instance-status`
Show status of specific instance.

```bash
genebot instance-status INSTANCE_NAME [OPTIONS]

Options:
  --detailed           Detailed status information
  --metrics            Include performance metrics
```

#### `genebot instance-logs`
View logs for specific instance.

```bash
genebot instance-logs INSTANCE_NAME [OPTIONS]

Options:
  --lines INTEGER      Number of lines to show
  --follow             Follow log output
  --level LEVEL        Filter by log level
```

### Strategy Orchestration Commands

The orchestrator provides intelligent coordination of multiple trading strategies with automatic allocation management and advanced risk controls.

#### `genebot orchestrator-start` / `genebot orch-start`
Start the strategy orchestrator.

```bash
genebot orchestrator-start [OPTIONS]

Options:
  --config FILE        Orchestrator configuration file
  --daemon             Run in daemon mode
  --strategies TEXT    Specific strategies to enable (comma-separated)
```

**Examples:**
```bash
# Start with default configuration
genebot orchestrator-start

# Start with custom configuration in daemon mode
genebot orchestrator-start --config config/orchestrator_prod.yaml --daemon

# Start with specific strategies only
genebot orchestrator-start --strategies ma_short,rsi_oversold --daemon
```

#### `genebot orchestrator-stop` / `genebot orch-stop`
Stop the strategy orchestrator.

```bash
genebot orchestrator-stop [OPTIONS]

Options:
  --timeout INTEGER    Shutdown timeout in seconds (default: 60)
```

#### `genebot orchestrator-status` / `genebot orch-status`
Show orchestrator status and metrics.

```bash
genebot orchestrator-status [OPTIONS]

Options:
  --verbose            Show detailed status with strategy information
  --json               Output in JSON format
```

**Example output:**
```
=== Orchestrator Status ===
Status: running
Orchestrator ID: 140234567890
Start Time: 2024-01-15T10:30:00

Strategies:
  Active: 5
  Paused: 1
  Failed: 0
  Total: 6

Performance:
  Total Return: 12.45%
  Sharpe Ratio: 1.85
  Max Drawdown: 3.2%
  Win Rate: 68.5%

Risk:
  Current Drawdown: 1.1%
  Portfolio VaR: 2.8%
  Max Correlation: 0.65

Allocation:
  ma_short: 22.5%
  rsi_oversold: 18.3%
  mean_reversion: 15.7%
  momentum: 20.1%
  arbitrage: 23.4%
```

#### `genebot orchestrator-config` / `genebot orch-config`
Manage orchestrator configuration.

```bash
genebot orchestrator-config ACTION [OPTIONS]

Actions:
  show                 Show current configuration
  update               Update configuration parameters
  validate             Validate configuration file
  reload               Reload configuration without restart

Update Options:
  --allocation-method METHOD    Update allocation method (equal_weight, performance_based, risk_parity)
  --rebalance-frequency FREQ    Update rebalance frequency (daily, weekly, monthly)
  --max-drawdown FLOAT         Update maximum portfolio drawdown limit
```

**Examples:**
```bash
# Show current configuration
genebot orchestrator-config show

# Update allocation method
genebot orchestrator-config update --allocation-method performance_based

# Validate configuration file
genebot orchestrator-config validate --config config/orchestrator_config.yaml

# Reload configuration
genebot orchestrator-config reload
```

#### `genebot orchestrator-monitor` / `genebot orch-monitor`
Monitor orchestrator performance and metrics.

```bash
genebot orchestrator-monitor [OPTIONS]

Options:
  --hours INTEGER      Time range in hours for monitoring data (default: 24)
  --format FORMAT      Output format (table, json)
  --refresh INTEGER    Auto-refresh interval in seconds
```

**Examples:**
```bash
# Monitor last 24 hours
genebot orchestrator-monitor

# Monitor last week with JSON output
genebot orchestrator-monitor --hours 168 --format json

# Live monitoring with 30-second refresh
genebot orchestrator-monitor --refresh 30
```

#### `genebot orchestrator-intervention` / `genebot orch-intervention`
Perform manual interventions on the orchestrator.

```bash
genebot orchestrator-intervention ACTION [OPTIONS]

Actions:
  pause_strategy       Pause a specific strategy
  resume_strategy      Resume a paused strategy
  emergency_stop       Execute emergency stop across all strategies
  force_rebalance      Force immediate rebalancing
  adjust_allocation    Manually adjust allocation weights

Options:
  --strategy TEXT      Strategy name (required for pause/resume)
  --reason TEXT        Reason for intervention (for emergency stop)
  --allocation JSON    New allocation weights as JSON string
```

**Examples:**
```bash
# Pause a strategy
genebot orchestrator-intervention pause_strategy --strategy ma_short

# Resume a strategy
genebot orchestrator-intervention resume_strategy --strategy ma_short

# Emergency stop with reason
genebot orchestrator-intervention emergency_stop --reason "Market volatility spike"

# Force rebalancing
genebot orchestrator-intervention force_rebalance

# Adjust allocation weights
genebot orchestrator-intervention adjust_allocation \
  --allocation '{"ma_short": 0.20, "rsi_oversold": 0.25, "arbitrage": 0.30}'
```

#### `genebot orchestrator-api` / `genebot orch-api`
Manage orchestrator REST API server.

```bash
genebot orchestrator-api ACTION [OPTIONS]

Actions:
  start                Start API server
  stop                 Stop API server

Options:
  --host TEXT          API server host (default: 127.0.0.1)
  --port INTEGER       API server port (default: 8080)
```

**Examples:**
```bash
# Start API server on default host/port
genebot orchestrator-api start

# Start API server on all interfaces
genebot orchestrator-api start --host 0.0.0.0 --port 8080
```

#### `genebot orchestrator-migrate` / `genebot orch-migrate`
Migrate existing setup to orchestrator.

```bash
genebot orchestrator-migrate ACTION [OPTIONS]

Actions:
  analyze              Analyze existing setup for migration
  backup               Create backup of current configuration
  generate             Generate orchestrator configuration
  migrate              Perform complete migration
  validate             Validate orchestrator configuration
  guide                Show migration guide

Options:
  --output FILE        Output path for generated configuration
  --allocation-method METHOD    Allocation method (default: performance_based)
  --rebalance-frequency FREQ    Rebalancing frequency (default: daily)
  --max-drawdown FLOAT         Maximum portfolio drawdown (default: 0.10)
  --no-backup          Skip creating backup during migration
```

**Examples:**
```bash
# Analyze current setup
genebot orchestrator-migrate analyze

# Generate orchestrator configuration
genebot orchestrator-migrate generate --allocation-method performance_based

# Perform complete migration with backup
genebot orchestrator-migrate migrate

# Validate generated configuration
genebot orchestrator-migrate validate config/orchestrator_config.yaml

# Show migration guide
genebot orchestrator-migrate guide
```

### Configuration Commands

#### `genebot init-config`
Initialize configuration files.

```bash
genebot init-config [OPTIONS]

Options:
  --template TEXT      Configuration template to use
  --overwrite          Overwrite existing configurations
  --minimal            Create minimal configuration
  --interactive        Interactive configuration setup
```

#### `genebot config-help`
Show configuration help and examples.

```bash
genebot config-help [OPTIONS]

Options:
  --section TEXT       Show help for specific section
  --examples           Show configuration examples
  --validate           Validate current configuration
```

#### `genebot validate-config`
Validate configuration files.

```bash
genebot validate-config [OPTIONS]

Options:
  --file FILE          Validate specific file
  --fix                Attempt to fix issues
  --strict             Strict validation mode
```

#### `genebot system-validate`
Comprehensive system validation.

```bash
genebot system-validate [OPTIONS]

Options:
  --components TEXT    Validate specific components
  --fix-issues         Attempt to fix found issues
  --report FILE        Save validation report
```

### Monitoring and Reporting Commands

#### `genebot monitor`
Real-time monitoring of trading activity.

```bash
genebot monitor [OPTIONS]

Options:
  --accounts TEXT      Monitor specific accounts
  --strategies TEXT    Monitor specific strategies
  --refresh INTEGER    Refresh interval (seconds)
  --alerts             Show alerts and warnings
```

#### `genebot trades`
Display trading history.

```bash
genebot trades [OPTIONS]

Options:
  --limit INTEGER      Number of trades to show
  --account TEXT       Filter by account
  --strategy TEXT      Filter by strategy
  --start-date DATE    Start date (YYYY-MM-DD)
  --end-date DATE      End date (YYYY-MM-DD)
  --format FORMAT      Output format (table, json, csv)
  --export FILE        Export to file
```

#### `genebot report`
Generate comprehensive reports.

```bash
genebot report [OPTIONS]

Options:
  --type TYPE          Report type (summary, detailed, performance, compliance)
  --start-date DATE    Start date for report
  --end-date DATE      End date for report
  --accounts TEXT      Include specific accounts
  --strategies TEXT    Include specific strategies
  --format FORMAT      Output format (text, html, pdf)
  --output FILE        Save report to file
  --email TEXT         Email report to address
```

**Report Types:**
- `summary`: Overview of trading performance
- `detailed`: Detailed trade-by-trade analysis
- `performance`: Performance metrics and statistics
- `compliance`: Regulatory compliance report
- `risk`: Risk analysis and exposure report
- `arbitrage`: Cross-market arbitrage opportunities

#### `genebot analytics`
Advanced analytics and insights.

```bash
genebot analytics [OPTIONS]

Options:
  --type TYPE          Analysis type (performance, risk, correlation)
  --timeframe TEXT     Analysis timeframe (1d, 1w, 1m, 3m, 1y)
  --benchmark TEXT     Benchmark for comparison
  --export FILE        Export analysis results
```

#### `genebot close-all-orders`
Close all open orders across accounts.

```bash
genebot close-all-orders [OPTIONS]

Options:
  --accounts TEXT      Close orders for specific accounts
  --confirm            Skip confirmation prompt
  --dry-run           Show what would be closed
  --reason TEXT        Reason for closing orders
```

### Utility Commands

#### `genebot health-check`
Perform system health check.

```bash
genebot health-check [OPTIONS]

Options:
  --components TEXT    Check specific components
  --fix                Attempt to fix issues
  --report FILE        Save health report
```

#### `genebot backup-config`
Backup configuration files.

```bash
genebot backup-config [OPTIONS]

Options:
  --destination DIR    Backup destination directory
  --compress           Create compressed backup
  --encrypt            Encrypt backup (requires password)
```

#### `genebot reset`
Reset configuration or data.

```bash
genebot reset [OPTIONS]

Options:
  --config             Reset configuration files
  --data               Reset trading data
  --logs               Clear log files
  --all                Reset everything
  --confirm            Skip confirmation prompts
```

### Security Commands

#### `genebot security`
Security management and validation.

```bash
genebot security [OPTIONS]

Options:
  --scan               Scan for security issues
  --fix                Fix security issues
  --audit              Generate security audit report
  --rotate-keys        Rotate API keys
```

### Error Handling Commands

#### `genebot diagnostics`
Run system diagnostics.

```bash
genebot diagnostics [OPTIONS]

Options:
  --component TEXT     Diagnose specific component
  --verbose            Detailed diagnostic output
  --export FILE        Export diagnostic report
```

#### `genebot error-report`
Generate error reports.

```bash
genebot error-report [OPTIONS]

Options:
  --start-date DATE    Start date for error analysis
  --end-date DATE      End date for error analysis
  --severity LEVEL     Filter by error severity
  --export FILE        Export error report
```

#### `genebot system-recovery`
System recovery operations.

```bash
genebot system-recovery [OPTIONS]

Options:
  --component TEXT     Recover specific component
  --backup-date DATE   Restore from specific backup
  --force              Force recovery without confirmation
```

## Configuration Management

### Configuration Files

GeneBot uses several configuration files:

#### `config/accounts.yaml`
Account configurations for exchanges and brokers.

```yaml
crypto_exchanges:
  binance:
    name: binance
    exchange_type: binance
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: false
    enabled: true
    rate_limit: 1200
    timeout: 30
    
forex_brokers:
  oanda:
    name: oanda
    broker_type: oanda
    api_key: "${OANDA_API_KEY}"
    account_id: "${OANDA_ACCOUNT_ID}"
    sandbox: false
    enabled: true
    timeout: 30
```

#### `config/trading_bot_config.yaml`
Main trading bot configuration.

```yaml
trading:
  strategies:
    - name: "multi_market_arbitrage"
      enabled: true
      config:
        min_profit_threshold: 0.005
        max_position_size: 1000
        
risk_management:
  max_daily_loss: 0.02
  max_position_size: 0.1
  stop_loss_percentage: 0.05
  
monitoring:
  enable_alerts: true
  alert_channels: ["email", "webhook"]
  metrics_interval: 60
```

#### Environment Variables (`.env`)
Sensitive configuration stored in environment variables.

```bash
# Crypto Exchange API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Forex Broker API Keys
OANDA_API_KEY=your_oanda_api_key
OANDA_ACCOUNT_ID=your_oanda_account_id

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/genebot

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_URL=http://localhost:3000
```

### Configuration Templates

GeneBot provides several configuration templates:

```bash
# List available templates
genebot config-help --examples

# Initialize with specific template
genebot init-config --template development
genebot init-config --template production
genebot init-config --template minimal
```

### Configuration Validation

```bash
# Validate all configuration files
genebot validate-config

# Validate specific file
genebot validate-config --file config/accounts.yaml

# Strict validation with detailed output
genebot validate-config --strict --verbose
```

## Account Management

### Supported Exchanges and Brokers

#### Cryptocurrency Exchanges
- **Binance**: Spot and futures trading
- **Coinbase Pro**: Professional trading platform
- **Kraken**: European-focused exchange
- **KuCoin**: Global cryptocurrency exchange
- **Bybit**: Derivatives and spot trading

#### Forex Brokers
- **OANDA**: Retail forex broker with REST API
- **MetaTrader 5**: Popular trading platform
- **Interactive Brokers**: Professional trading platform

### Account Configuration Best Practices

1. **Use Environment Variables**
   ```bash
   # Store credentials in .env file
   echo "BINANCE_API_KEY=your_key" >> .env
   echo "BINANCE_API_SECRET=your_secret" >> .env
   ```

2. **Start with Sandbox Accounts**
   ```bash
   # Always test with sandbox first
   genebot add-crypto --name binance-test --exchange binance --sandbox
   ```

3. **Validate Before Trading**
   ```bash
   # Validate all accounts before starting
   genebot validate-accounts --detailed
   ```

4. **Regular Security Audits**
   ```bash
   # Run security scans regularly
   genebot security --scan --audit
   ```

### Account Validation Process

The CLI performs comprehensive account validation:

1. **Configuration Validation**
   - Required fields present
   - Correct data types
   - Valid exchange/broker types

2. **Credential Validation**
   - API key format validation
   - No placeholder values
   - Proper encoding

3. **Connectivity Testing**
   - API endpoint reachability
   - Authentication verification
   - Permission validation

4. **Feature Testing**
   - Account balance retrieval
   - Order placement capability
   - Market data access

## Bot Process Management

### Process Lifecycle

The CLI provides comprehensive process management:

1. **Starting the Bot**
   ```bash
   # Start with validation
   genebot start
   
   # Start specific strategy
   genebot start --strategy arbitrage
   
   # Start in background
   genebot start --background
   ```

2. **Monitoring Processes**
   ```bash
   # Check status
   genebot status --detailed
   
   # Monitor continuously
   genebot status --watch --refresh 5
   ```

3. **Managing Multiple Instances**
   ```bash
   # Start named instances
   genebot start-instance crypto-arb --strategy crypto_arbitrage
   genebot start-instance forex-trend --strategy forex_trend
   
   # List all instances
   genebot list-instances
   ```

4. **Graceful Shutdown**
   ```bash
   # Graceful stop
   genebot stop
   
   # Force stop if needed
   genebot stop --force
   ```

### Process Health Monitoring

```bash
# Health check
genebot health-check

# Detailed diagnostics
genebot diagnostics --verbose

# Monitor specific instance
genebot instance-status crypto-arb --metrics
```

### PID File Management

The CLI automatically manages PID files for process tracking:

- Main bot: `bot.pid`
- Named instances: `bot_<instance_name>.pid`
- Monitoring processes: `monitor_<type>.pid`

## Monitoring and Analytics

### Real-Time Monitoring

```bash
# Live trading monitor
genebot monitor --refresh 5

# Monitor specific accounts
genebot monitor --accounts binance,oanda

# Monitor with alerts
genebot monitor --alerts
```

### Trading Analytics

```bash
# Performance analysis
genebot analytics --type performance --timeframe 1m

# Risk analysis
genebot analytics --type risk --timeframe 1w

# Correlation analysis
genebot analytics --type correlation --timeframe 3m
```

### Report Generation

```bash
# Daily summary report
genebot report --type summary --start-date $(date +%Y-%m-%d)

# Monthly performance report
genebot report --type performance --start-date $(date -d '1 month ago' +%Y-%m-%d) \
  --format html --output reports/monthly_performance.html

# Compliance report for regulators
genebot report --type compliance --start-date 2024-01-01 --end-date 2024-12-31 \
  --format pdf --output reports/compliance_2024.pdf
```

### Backtesting Analytics

```bash
# Backtest specific strategy
genebot backtest-analytics --strategy arbitrage --start-date 2024-01-01 \
  --end-date 2024-12-31

# Compare multiple strategies
genebot backtest-analytics --strategies arbitrage,trend,mean_reversion \
  --benchmark SPY --export results/backtest_comparison.json
```

## Security Features

### Credential Security

1. **Environment Variable Storage**
   - All sensitive data stored in environment variables
   - No plain text credentials in configuration files
   - Automatic .env file loading

2. **Credential Validation**
   - Format validation for API keys
   - Detection of placeholder values
   - Encryption key validation

3. **Access Control**
   - File permission validation
   - Secure file creation (600 permissions)
   - User ownership verification

### Security Scanning

```bash
# Comprehensive security scan
genebot security --scan

# Fix security issues
genebot security --fix

# Generate security audit
genebot security --audit --export security_audit.json
```

### Key Rotation

```bash
# Rotate API keys
genebot security --rotate-keys

# Update specific account keys
genebot edit-crypto binance --field api_key --value $NEW_BINANCE_KEY
```

## Advanced Features

### Multi-Market Arbitrage

```bash
# Monitor arbitrage opportunities
genebot monitor --strategies arbitrage

# Generate arbitrage report
genebot report --type arbitrage --start-date $(date -d '7 days ago' +%Y-%m-%d)
```

### Cross-Market Analysis

```bash
# Analyze market correlations
genebot analytics --type correlation --markets crypto,forex

# Export correlation matrix
genebot analytics --type correlation --export correlation_matrix.csv
```

### Portfolio Management

```bash
# Portfolio status
genebot status --detailed --accounts all

# Portfolio rebalancing report
genebot report --type portfolio --accounts all
```

### Compliance Management

```bash
# Generate compliance report
genebot report --type compliance --start-date 2024-01-01

# Audit trail export
genebot report --type audit --format json --export audit_trail.json
```

## Integration Guide

### API Integration

The CLI can be integrated with external systems:

```python
# Python integration example
import subprocess
import json

def get_bot_status():
    result = subprocess.run(['genebot', 'status', '--json'], 
                          capture_output=True, text=True)
    return json.loads(result.stdout)

def start_trading_session():
    result = subprocess.run(['genebot', 'start', '--background'])
    return result.returncode == 0
```

### Webhook Integration

```bash
# Configure webhooks in monitoring config
genebot config-help --section monitoring

# Test webhook delivery
genebot monitor --alerts --webhook-test
```

### Database Integration

```bash
# Export trading data
genebot trades --format json --export trading_data.json

# Generate database report
genebot report --type database --export db_status.json
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Configuration Issues

**Problem**: "Configuration file not found"
```bash
# Solution: Initialize configuration
genebot init-config
```

**Problem**: "Invalid configuration format"
```bash
# Solution: Validate and fix configuration
genebot validate-config --fix
```

#### 2. Account Issues

**Problem**: "Account validation failed"
```bash
# Solution: Check account configuration
genebot validate-accounts --account binance --detailed

# Fix common issues
genebot validate-accounts --fix-issues
```

**Problem**: "API connection timeout"
```bash
# Solution: Check network and increase timeout
genebot edit-crypto binance --field timeout --value 60
```

#### 3. Process Issues

**Problem**: "Bot won't start"
```bash
# Solution: Check system status
genebot system-validate

# Check for existing processes
genebot status --detailed

# Force cleanup if needed
genebot stop --force
```

**Problem**: "Process not responding"
```bash
# Solution: Check process health
genebot diagnostics --component process

# Force restart if needed
genebot restart --force
```

#### 4. Performance Issues

**Problem**: "Slow CLI responses"
```bash
# Solution: Check system resources
genebot health-check --components system

# Clear logs if needed
genebot reset --logs
```

### Diagnostic Commands

```bash
# Comprehensive system check
genebot diagnostics --verbose

# Check specific components
genebot diagnostics --component database
genebot diagnostics --component network
genebot diagnostics --component accounts

# Generate diagnostic report
genebot diagnostics --export diagnostic_report.json
```

### Log Analysis

```bash
# View CLI logs
tail -f logs/cli.log

# View trading logs
tail -f logs/trading.log

# View error logs
genebot error-report --start-date $(date -d '1 day ago' +%Y-%m-%d)
```

### Recovery Procedures

```bash
# System recovery
genebot system-recovery --component all

# Configuration recovery
genebot system-recovery --component config --backup-date 2024-01-15

# Database recovery
genebot system-recovery --component database
```

### Getting Help

1. **Built-in Help System**
   ```bash
   # General help
   genebot --help
   
   # Command-specific help
   genebot start --help
   
   # Interactive help
   genebot help --interactive
   ```

2. **Configuration Help**
   ```bash
   # Configuration examples
   genebot config-help --examples
   
   # Section-specific help
   genebot config-help --section accounts
   ```

3. **System Validation**
   ```bash
   # Comprehensive validation
   genebot system-validate --verbose
   
   # Component-specific validation
   genebot system-validate --components accounts,config,database
   ```

4. **Error Reporting**
   ```bash
   # Generate error report
   genebot error-report --verbose --export error_analysis.json
   
   # System diagnostics
   genebot diagnostics --export system_diagnostics.json
   ```

The GeneBot CLI is designed to be self-documenting and provide helpful guidance for troubleshooting. Most commands include detailed help text and examples accessible through the `--help` option.

For complex issues, the diagnostic and error reporting commands provide comprehensive information for troubleshooting and support.
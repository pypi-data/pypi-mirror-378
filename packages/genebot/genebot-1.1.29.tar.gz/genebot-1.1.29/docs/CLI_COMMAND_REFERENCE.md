# GeneBot CLI Command Reference v1.1.28

## Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Setup & Configuration Commands](#setup--configuration-commands)
4. [Account Management Commands](#account-management-commands)
5. [Bot Control & Process Management](#bot-control--process-management)
6. [Strategy Management Commands](#strategy-management-commands)
7. [Orchestrator Management Commands](#orchestrator-management-commands)
8. [Monitoring & Analytics Commands](#monitoring--analytics-commands)
9. [Security Commands](#security-commands)
10. [Utility Commands](#utility-commands)
11. [Command Examples](#command-examples)

## Overview

The GeneBot CLI provides comprehensive command-line access to all trading bot functionality. All commands support consistent options and provide detailed help information.

### Getting Help

```bash
# General help
genebot --help

# Command-specific help
genebot <command> --help

# Configuration help
genebot config-help

# List all available commands
genebot --help | grep -A 100 "Available commands"
```

## Global Options

These options are available for all commands:

```bash
--config-path <path>           # Path to configuration directory (default: config)
--log-level <level>            # Set logging level (DEBUG, INFO, WARNING, ERROR)
--verbose, -v                  # Enable verbose output with detailed information
--quiet, -q                    # Suppress all output except errors
--no-color                     # Disable colored output
--output-file <file>           # Write output to file instead of stdout
--dry-run                      # Show what would be done without making changes
--force                        # Force operation without confirmation prompts
--auto-recover                 # Attempt automatic error recovery when possible
```

## Setup & Configuration Commands

### `genebot init-config`
Initialize configuration files and directory structure.

```bash
genebot init-config [options]

Options:
  --overwrite                  # Overwrite existing configuration files
  --template <name>            # Configuration template (minimal, development, production)

Examples:
  genebot init-config                           # Create default development config
  genebot init-config --template production     # Create production config
  genebot init-config --overwrite              # Overwrite existing files
```

### `genebot config-help`
Display comprehensive configuration setup guide.

```bash
genebot config-help

# Shows detailed information about:
# - Configuration file structure
# - Environment variables
# - Account setup
# - Strategy configuration
# - Risk management settings
```

### `genebot validate-config`
Validate configuration files for errors and consistency.

```bash
genebot validate-config [options]

Options:
  --verbose                    # Show detailed validation information

Examples:
  genebot validate-config                       # Basic validation
  genebot validate-config --verbose             # Detailed validation report
```

### `genebot config-status`
Show current configuration status and file information.

```bash
genebot config-status

# Displays:
# - Configuration file locations
# - File modification times
# - Configuration version
# - Validation status
```

### `genebot config-backup`
Create backup copies of configuration files.

```bash
genebot config-backup [options]

Options:
  --file <type>                # Specific file to backup (all, bot_config, accounts, env)

Examples:
  genebot config-backup                         # Backup all files
  genebot config-backup --file accounts         # Backup only accounts.yaml
```

### `genebot config-restore`
Restore configuration files from previously created backups.

```bash
genebot config-restore [options]

Options:
  --file <type>                # Specific file to restore
  --timestamp <time>           # Specific backup timestamp to restore from

Examples:
  genebot config-restore                        # Restore from most recent backup
  genebot config-restore --file accounts        # Restore only accounts.yaml
  genebot config-restore --timestamp 20240101_120000  # Restore specific backup
```

### `genebot config-migrate`
Migrate configuration files to newer format versions.

```bash
genebot config-migrate [options]

Options:
  --version <version>          # Target version to migrate to (default: latest)
  --dry-run                    # Show migration plan without applying changes

Examples:
  genebot config-migrate                        # Migrate to latest version
  genebot config-migrate --dry-run              # Preview migration changes
```

### `genebot system-validate`
Perform comprehensive validation of all system components.

```bash
genebot system-validate [options]

Options:
  --verbose                    # Show detailed validation information

# Validates:
# - Configuration files
# - Account connectivity
# - Strategy loading
# - System dependencies
# - File permissions
```

## Account Management Commands

### `genebot list-accounts` (alias: `list`)
List all configured trading accounts with their status.

```bash
genebot list-accounts [options]

Options:
  --type <type>                # Filter by type (crypto, forex, all)
  --status <status>            # Filter by status (active, inactive, disabled, all)

Examples:
  genebot list-accounts                         # List all accounts
  genebot list-accounts --type crypto          # List only crypto accounts
  genebot list-accounts --status active        # List only active accounts
```

### `genebot list-exchanges`
Show all supported cryptocurrency exchanges.

```bash
genebot list-exchanges

# Displays:
# - Exchange names
# - Supported features (spot, futures, sandbox)
# - Current status
# - API documentation links
```

### `genebot list-brokers`
Show all supported forex brokers.

```bash
genebot list-brokers

# Displays:
# - Broker names
# - Supported features (spot forex, CFDs, demo)
# - Current status
# - API documentation links
```

### `genebot add-crypto`
Add a new cryptocurrency exchange account.

```bash
genebot add-crypto <exchange> [options]

Arguments:
  <exchange>                   # Exchange name (binance, coinbase, kraken, etc.)

Options:
  --name <name>                # Custom account name (default: exchange-mode)
  --mode <mode>                # Account mode (demo, live)
  --enabled                    # Enable account immediately (default: true)

Examples:
  genebot add-crypto binance                    # Add Binance demo account
  genebot add-crypto binance --mode live        # Add Binance live account
  genebot add-crypto coinbase --name coinbase-main --mode demo
```

### `genebot add-forex`
Add a new forex broker account.

```bash
genebot add-forex <broker> [options]

Arguments:
  <broker>                     # Broker name (oanda, ib, mt5, etc.)

Options:
  --name <name>                # Custom account name (default: broker-mode)
  --mode <mode>                # Account mode (demo, live)
  --enabled                    # Enable account immediately (default: true)

Examples:
  genebot add-forex oanda                       # Add OANDA demo account
  genebot add-forex oanda --mode live           # Add OANDA live account
  genebot add-forex ib --name ib-paper --mode demo
```

### `genebot edit-crypto`
Edit an existing cryptocurrency exchange account.

```bash
genebot edit-crypto <name> [options]

Arguments:
  <name>                       # Account name to edit

Options:
  --interactive                # Use interactive editing mode

Examples:
  genebot edit-crypto binance-demo              # Edit account interactively
  genebot edit-crypto binance-demo --interactive
```

### `genebot edit-forex`
Edit an existing forex broker account.

```bash
genebot edit-forex <name> [options]

Arguments:
  <name>                       # Account name to edit

Options:
  --interactive                # Use interactive editing mode

Examples:
  genebot edit-forex oanda-demo                 # Edit account interactively
```

### `genebot remove-account`
Remove a specific trading account.

```bash
genebot remove-account <name> [options]

Arguments:
  <name>                       # Account name to remove

Options:
  --confirm                    # Skip confirmation prompt

Examples:
  genebot remove-account old-account            # Remove with confirmation
  genebot remove-account old-account --confirm  # Remove without confirmation
```

### `genebot enable-account`
Enable a disabled trading account.

```bash
genebot enable-account <name>

Arguments:
  <name>                       # Account name to enable

Examples:
  genebot enable-account binance-demo
```

### `genebot disable-account`
Disable an active trading account.

```bash
genebot disable-account <name>

Arguments:
  <name>                       # Account name to disable

Examples:
  genebot disable-account binance-demo
```

### `genebot validate-accounts` (alias: `validate`)
Test connectivity and validate all configured accounts.

```bash
genebot validate-accounts [options]

Options:
  --account <name>             # Validate specific account only
  --timeout <seconds>          # Connection timeout (default: 30)

Examples:
  genebot validate-accounts                     # Validate all accounts
  genebot validate-accounts --account binance-demo  # Validate specific account
  genebot validate-accounts --timeout 60       # Use longer timeout
```

## Bot Control & Process Management

### `genebot start`
Start the trading bot with all configured strategies.

```bash
genebot start [options]

Options:
  --config <file>              # Specific configuration file to use
  --strategy <name>            # Enable specific strategy only (repeatable)
  --account <name>             # Use specific account only (repeatable)
  --background                 # Run bot in background (default: true)
  --foreground                 # Run bot in foreground

Examples:
  genebot start                                 # Start with default config
  genebot start --foreground                   # Start in foreground
  genebot start --strategy RSIStrategy         # Start with specific strategy
  genebot start --account binance-demo         # Start with specific account
```

### `genebot stop`
Gracefully stop the trading bot and all strategies.

```bash
genebot stop [options]

Options:
  --timeout <seconds>          # Shutdown timeout (default: 60)
  --force                      # Force kill if graceful shutdown fails

Examples:
  genebot stop                                  # Graceful stop
  genebot stop --timeout 120                   # Longer timeout
  genebot stop --force                         # Force stop
```

### `genebot restart`
Stop and restart the trading bot.

```bash
genebot restart [options]

Options:
  --timeout <seconds>          # Shutdown timeout (default: 60)
  --config <file>              # Configuration file for restart
  --strategy <name>            # Enable specific strategy after restart
  --account <name>             # Use specific account after restart

Examples:
  genebot restart                               # Basic restart
  genebot restart --config new_config.yaml     # Restart with new config
```

### `genebot status`
Display current status of the trading bot and all components.

```bash
genebot status [options]

Options:
  --detailed                   # Show detailed status information
  --json                       # Output status in JSON format

Examples:
  genebot status                                # Basic status
  genebot status --detailed                    # Detailed status
  genebot status --json                        # JSON output
```

### Advanced Instance Management

### `genebot start-instance`
Start a named bot instance with unique configuration.

```bash
genebot start-instance <instance_name> [options]

Arguments:
  <instance_name>              # Unique name for this bot instance

Options:
  --config <file>              # Specific configuration file
  --strategy <name>            # Enable specific strategy (repeatable)
  --account <name>             # Use specific account (repeatable)
  --background                 # Run in background (default: true)
  --foreground                 # Run in foreground

Examples:
  genebot start-instance crypto-bot             # Start named instance
  genebot start-instance forex-bot --strategy ForexSessionStrategy
```

### `genebot stop-instance`
Stop a specific bot instance by name.

```bash
genebot stop-instance <instance_name> [options]

Arguments:
  <instance_name>              # Name of instance to stop

Options:
  --timeout <seconds>          # Shutdown timeout (default: 60)
  --force                      # Force kill the instance

Examples:
  genebot stop-instance crypto-bot              # Stop named instance
  genebot stop-instance forex-bot --force       # Force stop instance
```

### `genebot list-instances`
Show all bot instances and their status.

```bash
genebot list-instances [options]

Options:
  --json                       # Output in JSON format

Examples:
  genebot list-instances                        # List all instances
  genebot list-instances --json                 # JSON output
```

### `genebot instance-status`
Display detailed status of a named bot instance.

```bash
genebot instance-status <instance_name> [options]

Arguments:
  <instance_name>              # Name of the bot instance

Options:
  --detailed                   # Show detailed status information
  --json                       # Output in JSON format

Examples:
  genebot instance-status crypto-bot            # Basic instance status
  genebot instance-status crypto-bot --detailed # Detailed status
```

### `genebot instance-logs`
Display recent log entries for a named bot instance.

```bash
genebot instance-logs <instance_name> [options]

Arguments:
  <instance_name>              # Name of the bot instance

Options:
  --lines <number>             # Number of log lines to show (default: 100)
  --follow                     # Follow log output (like tail -f)

Examples:
  genebot instance-logs crypto-bot              # Show recent logs
  genebot instance-logs crypto-bot --lines 500  # Show more lines
  genebot instance-logs crypto-bot --follow     # Follow logs
```

### `genebot instance-metrics`
Show performance metrics for a bot instance.

```bash
genebot instance-metrics <instance_name> [options]

Arguments:
  <instance_name>              # Name of the bot instance

Options:
  --limit <number>             # Maximum metrics to show (default: 50)
  --json                       # Output in JSON format

Examples:
  genebot instance-metrics crypto-bot           # Show metrics
  genebot instance-metrics crypto-bot --json    # JSON output
```

### Process Monitoring

### `genebot start-monitoring`
Start continuous monitoring of all bot instances.

```bash
genebot start-monitoring [options]

Options:
  --interval <seconds>         # Monitoring interval (default: 60)

Examples:
  genebot start-monitoring                      # Start with default interval
  genebot start-monitoring --interval 30       # Monitor every 30 seconds
```

### `genebot stop-monitoring`
Stop continuous monitoring of bot instances.

```bash
genebot stop-monitoring

Examples:
  genebot stop-monitoring                       # Stop monitoring
```

## Strategy Management Commands

### `genebot list-strategies`
List all available trading strategies and their status.

```bash
genebot list-strategies [options]

Options:
  --status <status>            # Filter by status (active, inactive, all)

Examples:
  genebot list-strategies                       # List all strategies
  genebot list-strategies --status active      # List only active strategies
```

## Orchestrator Management Commands

### `genebot orchestrator-start` (alias: `orch-start`)
Start the strategy orchestrator system.

```bash
genebot orchestrator-start [options]

Options:
  --config <file>              # Orchestrator configuration file
  --daemon                     # Run in daemon mode
  --strategies <names>         # Specific strategies to enable

Examples:
  genebot orchestrator-start                    # Start with default config
  genebot orch-start --daemon                   # Start as daemon
  genebot orch-start --strategies RSIStrategy,MovingAverageStrategy
```

### `genebot orchestrator-stop` (alias: `orch-stop`)
Gracefully stop the running orchestrator.

```bash
genebot orchestrator-stop [options]

Options:
  --timeout <seconds>          # Shutdown timeout (default: 60)

Examples:
  genebot orchestrator-stop                     # Graceful stop
  genebot orch-stop --timeout 120              # Longer timeout
```

### `genebot orchestrator-status` (alias: `orch-status`)
Display current orchestrator status and metrics.

```bash
genebot orchestrator-status [options]

Options:
  --verbose                    # Show detailed status information
  --json                       # Output in JSON format

Examples:
  genebot orchestrator-status                   # Basic status
  genebot orch-status --verbose                # Detailed status
  genebot orch-status --json                   # JSON output
```

### `genebot orchestrator-config` (alias: `orch-config`)
View and manage orchestrator configuration.

```bash
genebot orchestrator-config <action> [options]

Arguments:
  <action>                     # Configuration action (show, update, validate, reload)

Options:
  --config <file>              # Configuration file path
  --allocation-method <method> # Update allocation method
  --rebalance-frequency <freq> # Update rebalance frequency
  --max-drawdown <value>       # Update maximum drawdown limit

Examples:
  genebot orchestrator-config show             # Show current config
  genebot orch-config update --allocation-method performance_based
  genebot orch-config validate                 # Validate config
```

### `genebot orchestrator-monitor` (alias: `orch-monitor`)
Display real-time orchestrator monitoring information.

```bash
genebot orchestrator-monitor [options]

Options:
  --hours <number>             # Time range in hours (default: 24)
  --format <format>            # Output format (table, json)
  --refresh <seconds>          # Auto-refresh interval

Examples:
  genebot orchestrator-monitor                 # Monitor last 24 hours
  genebot orch-monitor --hours 48              # Monitor last 48 hours
  genebot orch-monitor --refresh 10            # Auto-refresh every 10 seconds
```

### `genebot orchestrator-intervention` (alias: `orch-intervention`)
Perform manual interventions on the orchestrator.

```bash
genebot orchestrator-intervention <action> [options]

Arguments:
  <action>                     # Intervention action

Actions:
  pause_strategy               # Pause a specific strategy
  resume_strategy              # Resume a paused strategy
  emergency_stop               # Emergency stop all trading
  force_rebalance              # Force portfolio rebalancing
  adjust_allocation            # Manually adjust allocations

Options:
  --strategy <name>            # Strategy name (for pause/resume)
  --reason <text>              # Reason for intervention
  --allocation <json>          # New allocation weights (JSON format)

Examples:
  genebot orchestrator-intervention pause_strategy --strategy RSIStrategy
  genebot orch-intervention emergency_stop --reason "Market crash"
  genebot orch-intervention adjust_allocation --allocation '{"RSI": 0.6, "MA": 0.4}'
```

### `genebot orchestrator-api` (alias: `orch-api`)
Manage the orchestrator REST API server.

```bash
genebot orchestrator-api <action> [options]

Arguments:
  <action>                     # API server action (start, stop)

Options:
  --host <host>                # API server host (default: 127.0.0.1)
  --port <port>                # API server port (default: 8080)

Examples:
  genebot orchestrator-api start               # Start API server
  genebot orch-api start --port 8081           # Start on different port
  genebot orch-api stop                        # Stop API server
```

### `genebot orchestrator-migrate` (alias: `orch-migrate`)
Migrate existing setup to use orchestrator.

```bash
genebot orchestrator-migrate <action> [options]

Arguments:
  <action>                     # Migration action

Actions:
  analyze                      # Analyze current setup for migration
  backup                       # Backup current configuration
  generate                     # Generate orchestrator configuration
  migrate                      # Perform migration
  validate                     # Validate migrated setup
  guide                        # Show migration guide

Options:
  --output <path>              # Output path for generated config
  --allocation-method <method> # Allocation method (equal_weight, performance_based, risk_parity)
  --rebalance-frequency <freq> # Rebalancing frequency (daily, weekly, monthly)
  --max-drawdown <value>       # Maximum drawdown (default: 0.10)
  --no-backup                  # Skip backup creation

Examples:
  genebot orchestrator-migrate analyze         # Analyze current setup
  genebot orch-migrate generate --allocation-method performance_based
  genebot orch-migrate migrate --no-backup     # Migrate without backup
```

## Monitoring & Analytics Commands

### `genebot monitor`
Display live trading activity and bot status.

```bash
genebot monitor [options]

Options:
  --refresh <seconds>          # Refresh interval (default: 5)
  --account <name>             # Monitor specific account only

Examples:
  genebot monitor                               # Monitor with 5-second refresh
  genebot monitor --refresh 10                 # 10-second refresh
  genebot monitor --account binance-demo       # Monitor specific account
```

### `genebot trades`
Show recent trading activity and performance metrics.

```bash
genebot trades [options]

Options:
  --limit <number>             # Number of trades to show (default: 20)
  --account <name>             # Show trades for specific account
  --days <number>              # Show trades from last N days

Examples:
  genebot trades                                # Show last 20 trades
  genebot trades --limit 50                    # Show last 50 trades
  genebot trades --account binance-demo        # Trades for specific account
  genebot trades --days 7                      # Trades from last 7 days
```

### `genebot report`
Generate comprehensive trading report.

```bash
genebot report [options]

Options:
  --format <format>            # Report format (html, pdf, json)
  --period <period>            # Time period (1d, 7d, 30d, 90d)
  --output <file>              # Output file path

Examples:
  genebot report                                # Generate default report
  genebot report --format pdf --period 30d     # PDF report for 30 days
  genebot report --output monthly_report.html  # Save to specific file
```

### `genebot analytics`
Advanced analytics and performance analysis.

```bash
genebot analytics <type> [options]

Arguments:
  <type>                       # Analytics type

Types:
  performance                  # Strategy performance analysis
  risk                         # Risk analysis and metrics
  correlation                  # Correlation analysis
  attribution                  # Performance attribution
  optimization                 # Parameter optimization

Options:
  --strategy <name>            # Analyze specific strategy
  --period <period>            # Analysis period
  --format <format>            # Output format (table, json, csv)

Examples:
  genebot analytics performance --strategy RSIStrategy --period 30d
  genebot analytics risk --format json
  genebot analytics correlation --strategies RSI,MA
```

## Security Commands

### `genebot security`
Security management and validation.

```bash
genebot security <action> [options]

Arguments:
  <action>                     # Security action

Actions:
  validate-credentials         # Validate API credentials
  audit                        # Comprehensive security audit
  scan-config                  # Scan configuration for security issues
  check-permissions            # Check file and API permissions

Examples:
  genebot security validate-credentials        # Validate all credentials
  genebot security audit                       # Full security audit
  genebot security scan-config                 # Scan configuration files
```

## Utility Commands

### `genebot health-check`
Comprehensive system health check.

```bash
genebot health-check [options]

Options:
  --verbose                    # Show detailed health information

Examples:
  genebot health-check                          # Basic health check
  genebot health-check --verbose               # Detailed health report
```

### `genebot error-report`
Generate comprehensive error report.

```bash
genebot error-report [options]

Options:
  --verbose                    # Include detailed error information
  --output <file>              # Save report to file

Examples:
  genebot error-report                          # Generate error report
  genebot error-report --verbose --output error_report.txt
```

### `genebot completion`
Manage shell completion for the CLI.

```bash
genebot completion [options]

Options:
  --install                    # Install completion for current shell
  --generate                   # Generate completion script
  --shell <shell>              # Target shell (bash, zsh, fish)

Examples:
  genebot completion --install                  # Install completion
  genebot completion --generate --shell bash    # Generate bash completion
```

### `genebot reset`
Clean up all data and reset system to initial state.

```bash
genebot reset [options]

Options:
  --confirm                    # Skip confirmation prompt
  --keep-config                # Keep configuration files
  --keep-logs                  # Keep log files

Examples:
  genebot reset                                 # Reset with confirmation
  genebot reset --confirm --keep-config        # Reset but keep config
```

### Data Management

### `genebot data-export`
Export trading data and configuration.

```bash
genebot data-export [options]

Options:
  --format <format>            # Export format (json, csv, sql)
  --output <file>              # Output file path
  --type <type>                # Data type (trades, config, all)

Examples:
  genebot data-export --format json            # Export all data as JSON
  genebot data-export --type trades --format csv  # Export trades as CSV
```

### `genebot data-import`
Import trading data from backup.

```bash
genebot data-import [options]

Options:
  --file <file>                # Input file path
  --format <format>            # Input format (json, csv, sql)
  --merge                      # Merge with existing data

Examples:
  genebot data-import --file backup.json       # Import from JSON backup
  genebot data-import --file trades.csv --format csv --merge
```

### `genebot cleanup`
Clean up temporary files and logs.

```bash
genebot cleanup [options]

Options:
  --logs                       # Clean up log files
  --temp                       # Clean up temporary files
  --old-backups                # Remove old backup files
  --days <number>              # Keep files newer than N days

Examples:
  genebot cleanup                               # Clean up all temporary files
  genebot cleanup --logs --days 7              # Clean logs older than 7 days
```

## Command Examples

### Complete Setup Workflow

```bash
# 1. Initialize configuration
genebot init-config --template development

# 2. Add demo accounts
genebot add-crypto binance --mode demo
genebot add-forex oanda --mode demo

# 3. Validate setup
genebot validate-config
genebot validate-accounts

# 4. Start trading
genebot start

# 5. Monitor activity
genebot status
genebot monitor
```

### Production Deployment

```bash
# 1. Create production configuration
genebot init-config --template production

# 2. Add live accounts
genebot add-crypto binance --mode live --name binance-prod
genebot add-forex oanda --mode live --name oanda-prod

# 3. Comprehensive validation
genebot system-validate --verbose
genebot security audit

# 4. Backup configuration
genebot config-backup

# 5. Start with monitoring
genebot start --background
genebot start-monitoring
```

### Orchestrator Setup

```bash
# 1. Analyze current setup
genebot orchestrator-migrate analyze

# 2. Generate orchestrator configuration
genebot orchestrator-migrate generate --allocation-method performance_based

# 3. Validate orchestrator setup
genebot orchestrator-config validate

# 4. Start orchestrator
genebot orchestrator-start --daemon

# 5. Monitor orchestrator
genebot orchestrator-monitor --refresh 30
```

### Troubleshooting Workflow

```bash
# 1. Check system status
genebot status --detailed
genebot health-check --verbose

# 2. Validate configuration
genebot system-validate --verbose

# 3. Check logs
genebot instance-logs main --lines 200

# 4. Generate error report
genebot error-report --verbose

# 5. Security audit
genebot security audit
```

This comprehensive command reference covers all available GeneBot CLI commands with detailed options and examples. For additional help with any command, use the `--help` option or refer to the troubleshooting guide.
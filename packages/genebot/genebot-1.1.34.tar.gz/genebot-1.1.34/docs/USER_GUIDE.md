# Trading Bot User Guide

## Overview

This comprehensive user guide provides step-by-step instructions for operating and monitoring the Trading Bot Python system. Whether you're a beginner or experienced trader, this guide will help you effectively use the bot for automated trading.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Running the Bot](#running-the-bot)
4. [Strategy Orchestration](#strategy-orchestration)
5. [Monitoring and Alerts](#monitoring-and-alerts)
6. [Strategy Management](#strategy-management)
7. [Risk Management](#risk-management)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

Before using the trading bot, ensure you have:

- Python 3.9 or higher installed
- Exchange API keys (with appropriate permissions)
- Basic understanding of trading concepts
- Sufficient capital for trading (start small!)

### Initial Setup

1. **Clone and Install**
   ```bash
   git clone https://github.com/your-org/trading-bot-python.git
   cd trading-bot-python
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Configure Database**
   ```bash
   # For development (SQLite)
   export DATABASE_URL="sqlite:///trading_bot.db"
   
   # For production (PostgreSQL)
   export DATABASE_URL="postgresql://user:pass@localhost:5432/trading_bot"
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

### First Run (Paper Trading)

Always start with paper trading to familiarize yourself with the system:

```bash
# Set paper trading mode
export PAPER_TRADING=true

# Start the bot
python main.py
```

## Configuration

### Basic Configuration

The main configuration file is `config/trading_bot_config.yaml`. Key sections include:

#### Exchange Settings
```yaml
exchanges:
  binance:
    enabled: true
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true  # Start with testnet
```

#### Strategy Settings
```yaml
strategies:
  moving_average:
    enabled: true
    parameters:
      short_period: 10
      long_period: 20
    symbols:
      - "BTC/USDT"
    timeframes:
      - "1h"
```

#### Risk Management
```yaml
risk_management:
  global:
    max_portfolio_risk: 0.02  # 2% risk per trade
    max_daily_loss: 0.05      # 5% daily loss limit
```

### Environment-Specific Configurations

Use different configurations for different environments:

- `examples/configuration_examples/development_config.yaml` - For testing
- `examples/configuration_examples/production_config.yaml` - For live trading

## Running the Bot

### Command Line Interface

#### Basic Commands

```bash
# Start the bot
python main.py

# Start with specific config
python main.py --config config/my_config.yaml

# Start in paper trading mode
python main.py --paper-trading

# Start with specific log level
python main.py --log-level DEBUG

# Run backtest only
python main.py --backtest-only --start-date 2023-01-01 --end-date 2023-12-31
```

#### Advanced Options

```bash
# Start specific strategies only
python main.py --strategies moving_average,rsi_strategy

# Start with custom symbols
python main.py --symbols BTC/USDT,ETH/USDT

# Dry run (no actual trades)
python main.py --dry-run

# Enable profiling
python main.py --profile
```

### Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop the bot
docker-compose down
```

### Systemd Service (Linux)

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/trading-bot.service
[Unit]
Description=Trading Bot Python
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/opt/trading-bot
ExecStart=/opt/trading-bot/venv/bin/python main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/trading-bot

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```

## Strategy Orchestration

The Strategy Orchestration system provides intelligent coordination of multiple trading strategies, automatic allocation management, and advanced risk controls across your entire portfolio.

### Overview

The orchestrator acts as a meta-strategy that:
- Automatically discovers and manages all available strategies
- Intelligently allocates capital based on performance
- Provides portfolio-level risk management
- Optimizes strategy combinations for maximum returns
- Monitors and adjusts allocations in real-time

### Getting Started with Orchestration

#### 1. Migration from Existing Setup

If you have an existing genebot configuration, migrate to orchestrator:

```bash
# Analyze your current setup
genebot orchestrator-migrate analyze

# Create backup of current configuration
genebot orchestrator-migrate backup

# Generate orchestrator configuration
genebot orchestrator-migrate generate --allocation-method performance_based

# Perform complete migration
genebot orchestrator-migrate migrate
```

#### 2. Manual Configuration

Create an orchestrator configuration file:

```bash
# Generate template configuration
genebot config-help orchestrator > config/orchestrator_config.yaml
```

Edit the configuration to match your needs:

```yaml
orchestrator:
  allocation:
    method: "performance_based"  # equal_weight, performance_based, risk_parity
    rebalance_frequency: "daily"  # daily, weekly, monthly
    min_allocation: 0.01  # Minimum 1% allocation per strategy
    max_allocation: 0.25  # Maximum 25% allocation per strategy
  
  risk:
    max_portfolio_drawdown: 0.10  # Maximum 10% portfolio drawdown
    max_strategy_correlation: 0.80  # Maximum correlation between strategies
    position_size_limit: 0.05  # Maximum 5% position size
    stop_loss_threshold: 0.02  # 2% stop loss threshold
  
  strategies:
    - type: "MovingAverageStrategy"
      name: "ma_short"
      enabled: true
      allocation_weight: 1.0
      parameters:
        short_period: 10
        long_period: 20
    
    - type: "RSIStrategy"
      name: "rsi_oversold"
      enabled: true
      allocation_weight: 1.0
      parameters:
        period: 14
        oversold: 30
        overbought: 70
```

### Running the Orchestrator

#### Basic Commands

```bash
# Start orchestrator
genebot orchestrator-start

# Start with specific configuration
genebot orchestrator-start --config config/orchestrator_config.yaml

# Start in daemon mode
genebot orchestrator-start --daemon

# Check orchestrator status
genebot orchestrator-status

# Stop orchestrator
genebot orchestrator-stop
```

#### Advanced Operations

```bash
# Monitor orchestrator performance
genebot orchestrator-monitor --hours 24

# View detailed status with strategy information
genebot orchestrator-status --verbose

# Manual intervention - pause a strategy
genebot orchestrator-intervention pause_strategy --strategy ma_short

# Force rebalancing
genebot orchestrator-intervention force_rebalance

# Emergency stop all strategies
genebot orchestrator-intervention emergency_stop --reason "Market volatility"
```

### Configuration Management

#### Dynamic Configuration Updates

```bash
# Show current configuration
genebot orchestrator-config show

# Update allocation method
genebot orchestrator-config update --allocation-method risk_parity

# Update rebalancing frequency
genebot orchestrator-config update --rebalance-frequency weekly

# Validate configuration
genebot orchestrator-config validate

# Reload configuration without restart
genebot orchestrator-config reload
```

### Allocation Methods

#### 1. Equal Weight
- Allocates capital equally across all enabled strategies
- Simple and balanced approach
- Good for strategies with similar risk profiles

#### 2. Performance Based (Recommended)
- Allocates more capital to better-performing strategies
- Uses risk-adjusted returns (Sharpe ratio)
- Automatically adapts to changing market conditions

#### 3. Risk Parity
- Allocates capital based on risk contribution
- Strategies with lower volatility get higher allocation
- Focuses on risk-adjusted diversification

### Monitoring and Analytics

#### Real-time Monitoring

```bash
# Live monitoring dashboard
genebot orchestrator-monitor --refresh 30

# Performance attribution analysis
genebot orchestrator-monitor --format json | jq '.performance_metrics'

# Strategy correlation analysis
genebot orchestrator-status --verbose | grep -A 10 "correlation"
```

#### API Access

Start the orchestrator API server for programmatic access:

```bash
# Start API server
genebot orchestrator-api start --host 0.0.0.0 --port 8080

# Access metrics via HTTP
curl http://localhost:8080/api/v1/status
curl http://localhost:8080/api/v1/metrics
curl http://localhost:8080/api/v1/performance
```

### Best Practices

#### 1. Strategy Selection
- Use strategies with different market conditions preferences
- Ensure strategies have low correlation
- Include both trend-following and mean-reversion strategies
- Test strategies individually before orchestration

#### 2. Risk Management
- Set conservative drawdown limits initially
- Monitor correlation between strategies regularly
- Use position size limits to prevent concentration
- Implement emergency stop conditions

#### 3. Performance Optimization
- Allow sufficient time for performance evaluation (30+ days)
- Rebalance frequency should match strategy timeframes
- Monitor allocation changes and their impact
- Keep detailed logs for analysis

#### 4. Monitoring
- Check orchestrator status daily
- Review performance attribution weekly
- Analyze strategy correlations monthly
- Backup configurations before major changes

### Troubleshooting

#### Common Issues

1. **Orchestrator won't start**
   ```bash
   # Check configuration
   genebot orchestrator-config validate
   
   # Check logs
   tail -f logs/orchestrator.log
   ```

2. **Strategies not being allocated**
   ```bash
   # Check strategy status
   genebot orchestrator-status --verbose
   
   # Verify strategy configuration
   genebot list-strategies
   ```

3. **Poor performance**
   ```bash
   # Analyze performance attribution
   genebot orchestrator-monitor --hours 168  # 1 week
   
   # Check individual strategy performance
   genebot report strategy --days 30
   ```

#### Recovery Procedures

```bash
# Emergency stop all strategies
genebot orchestrator-intervention emergency_stop

# Restore from backup
genebot config-restore --timestamp <backup_timestamp>

# Reset to equal weight allocation
genebot orchestrator-config update --allocation-method equal_weight
```

## Monitoring and Alerts

### Web Dashboard

Access the monitoring dashboard at `http://localhost:8000` (or your configured port).

#### Key Metrics to Monitor

1. **Portfolio Performance**
   - Total P&L
   - Daily P&L
   - Win rate
   - Sharpe ratio

2. **Strategy Performance**
   - Signal frequency
   - Strategy accuracy
   - Individual strategy P&L

3. **Risk Metrics**
   - Current drawdown
   - Position sizes
   - Risk exposure

4. **System Health**
   - Exchange connectivity
   - Data feed status
   - Error rates

### Grafana Dashboards

If using Grafana (recommended for production):

1. **Access Grafana**: `http://localhost:3000`
2. **Default credentials**: admin/admin
3. **Import dashboards** from `deployment/grafana/dashboards/`

#### Key Dashboards

- **Trading Bot Overview**: High-level performance metrics
- **Strategy Analysis**: Detailed strategy performance
- **Risk Monitoring**: Risk metrics and alerts
- **System Health**: Technical system metrics

### Alert Configuration

#### Email Alerts

Configure SMTP settings in your environment:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

#### Slack Alerts

Set up Slack webhook:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

#### Alert Rules

Common alert configurations:

```yaml
alerting:
  rules:
    - name: "high_loss"
      condition: "daily_pnl < -0.03"
      severity: "critical"
      message: "Daily loss exceeds 3%"
      
    - name: "strategy_failure"
      condition: "strategy_errors > 5"
      severity: "warning"
      message: "Strategy generating errors"
```

### Log Monitoring

#### Log Locations

- **Application logs**: `logs/trading_bot.log`
- **Error logs**: `logs/errors.log`
- **Trade logs**: `logs/trades.log`
- **Orchestration logs**: `logs/orchestration.log`
- **Strategy logs**: `logs/strategies/`
- **Performance logs**: `logs/performance.log`

#### Log Analysis

```bash
# View recent logs
tail -f logs/trading_bot.log

# Search for errors
grep "ERROR" logs/trading_bot.log

# View trade history
grep "TRADE_EXECUTED" logs/trades.log | jq '.'

# Monitor specific strategy
grep "moving_average" logs/trading_bot.log

# Monitor orchestration decisions
tail -f logs/orchestration.log | grep "ALLOCATION_CHANGE"

# View strategy performance logs
tail -f logs/performance.log | grep "STRATEGY_PERFORMANCE"

# Monitor risk management actions
grep "RISK_LIMIT" logs/trading_bot.log
```

### Orchestration Monitoring

#### Real-time Orchestration Metrics

```bash
# View current orchestration status
genebot orchestration status

# Monitor allocation changes in real-time
genebot orchestration monitor --follow

# View strategy health dashboard
genebot orchestration health

# Check risk metrics
genebot orchestration risk-status
```

#### Orchestration Dashboard

The orchestration system provides additional dashboard views:

1. **Strategy Allocation View**: Real-time allocation across all strategies
2. **Performance Attribution**: Contribution of each strategy to overall performance
3. **Risk Heatmap**: Risk exposure across strategies and correlations
4. **Rebalancing History**: Timeline of allocation changes and triggers

Access at: `http://localhost:8000/orchestration/dashboard`

#### Orchestration Alerts

Configure orchestration-specific alerts:

```yaml
orchestration_alerts:
  allocation_change:
    threshold: 0.05  # Alert if allocation changes by more than 5%
    
  strategy_failure:
    consecutive_failures: 3  # Alert after 3 consecutive strategy failures
    
  correlation_spike:
    threshold: 0.85  # Alert if strategy correlation exceeds 85%
    
  performance_degradation:
    threshold: -0.10  # Alert if orchestration performance drops 10%
    lookback_days: 7
```

## Strategy Management

### Available Strategies

Genebot includes a comprehensive suite of trading strategies across multiple categories:

#### Technical Analysis Strategies

1. **Moving Average Strategy** (`MovingAverageStrategy`)
   - Simple moving average crossover strategy
   - Parameters: `short_period`, `long_period`
   - Best for: Trending markets

2. **RSI Strategy** (`RSIStrategy`)
   - Relative Strength Index based strategy
   - Parameters: `period`, `oversold`, `overbought`
   - Best for: Mean reversion in ranging markets

3. **Mean Reversion Strategy** (`MeanReversionStrategy`)
   - Advanced mean reversion with multiple indicators
   - Parameters: `lookback_period`, `std_dev_threshold`
   - Best for: Sideways markets with clear support/resistance

4. **Multi-Indicator Strategy** (`MultiIndicatorStrategy`)
   - Combines multiple technical indicators
   - Parameters: `indicators`, `weights`, `threshold`
   - Best for: High-probability signal generation

5. **Advanced Momentum Strategy** (`AdvancedMomentumStrategy`)
   - Sophisticated momentum detection
   - Parameters: `momentum_period`, `confirmation_period`
   - Best for: Strong trending markets

6. **ATR Volatility Strategy** (`ATRVolatilityStrategy`)
   - Average True Range based volatility strategy
   - Parameters: `atr_period`, `volatility_threshold`
   - Best for: Volatile market conditions

#### Machine Learning Strategies

7. **ML Pattern Strategy** (`MLPatternStrategy`)
   - Machine learning pattern recognition
   - Parameters: `model_type`, `training_period`, `features`
   - Best for: Complex pattern detection

#### Forex-Specific Strategies

8. **Forex Carry Trade Strategy** (`ForexCarryTradeStrategy`)
   - Interest rate differential trading
   - Parameters: `interest_rate_threshold`, `currency_pairs`
   - Best for: Long-term forex positions

9. **Forex Session Strategy** (`ForexSessionStrategy`)
   - Trading based on forex market sessions
   - Parameters: `session_times`, `volatility_filter`
   - Best for: Session-based forex trading

10. **Forex News Strategy** (`ForexNewsStrategy`)
    - News-based trading strategy
    - Parameters: `news_sources`, `impact_threshold`
    - Best for: Event-driven forex trading

#### Cross-Market Arbitrage Strategies

11. **Cross Market Arbitrage Strategy** (`CrossMarketArbitrageStrategy`)
    - Base class for arbitrage strategies
    - Parameters: `price_threshold`, `execution_speed`
    - Best for: Multi-exchange arbitrage

12. **Triangular Arbitrage Strategy** (`TriangularArbitrageStrategy`)
    - Three-currency arbitrage opportunities
    - Parameters: `currency_triplets`, `min_profit_threshold`
    - Best for: Forex triangular arbitrage

13. **Crypto Forex Arbitrage Strategy** (`CryptoForexArbitrageStrategy`)
    - Arbitrage between crypto and forex markets
    - Parameters: `crypto_pairs`, `forex_pairs`, `spread_threshold`
    - Best for: Cross-market arbitrage opportunities

### Strategy Orchestration System

Genebot features an advanced **Unified Strategy Orchestration System** that intelligently coordinates all available strategies:

#### Key Features

- **Automatic Strategy Discovery**: Automatically detects and registers all available strategies
- **Intelligent Allocation**: Dynamically allocates capital based on strategy performance
- **Risk Management**: Portfolio-level risk controls across all strategies
- **Performance Optimization**: Continuously optimizes strategy combinations
- **Market Adaptation**: Adjusts strategy selection based on market conditions

#### Orchestration Configuration

```yaml
orchestrator:
  enabled: true
  allocation:
    method: "performance_based"  # Options: equal_weight, performance_based, risk_parity
    rebalance_frequency: "daily"
    min_allocation: 0.01
    max_allocation: 0.25
    
  risk:
    max_portfolio_drawdown: 0.10
    max_strategy_correlation: 0.80
    position_size_limit: 0.05
    
  strategies:
    # Technical Analysis Strategies
    - type: "MovingAverageStrategy"
      name: "ma_short_term"
      enabled: true
      allocation_weight: 1.0
      parameters:
        short_period: 10
        long_period: 20
        
    - type: "RSIStrategy"
      name: "rsi_oversold"
      enabled: true
      allocation_weight: 1.0
      parameters:
        period: 14
        oversold: 30
        overbought: 70
        
    - type: "MeanReversionStrategy"
      name: "mean_reversion"
      enabled: true
      allocation_weight: 1.0
      parameters:
        lookback_period: 20
        std_dev_threshold: 2.0
        
    # Advanced Strategies
    - type: "MultiIndicatorStrategy"
      name: "multi_indicator"
      enabled: true
      allocation_weight: 1.5
      parameters:
        indicators: ["rsi", "macd", "bollinger"]
        weights: [0.4, 0.4, 0.2]
        
    - type: "AdvancedMomentumStrategy"
      name: "momentum"
      enabled: true
      allocation_weight: 1.2
      parameters:
        momentum_period: 14
        confirmation_period: 3
        
    - type: "ATRVolatilityStrategy"
      name: "volatility"
      enabled: true
      allocation_weight: 1.0
      parameters:
        atr_period: 14
        volatility_threshold: 0.02
        
    # ML Strategy
    - type: "MLPatternStrategy"
      name: "ml_patterns"
      enabled: true
      allocation_weight: 1.3
      parameters:
        model_type: "random_forest"
        training_period: 1000
        
    # Forex Strategies (if trading forex)
    - type: "ForexCarryTradeStrategy"
      name: "carry_trade"
      enabled: true
      allocation_weight: 1.0
      parameters:
        interest_rate_threshold: 0.02
        
    - type: "ForexSessionStrategy"
      name: "session_trading"
      enabled: true
      allocation_weight: 1.0
      parameters:
        preferred_sessions: ["london", "new_york"]
        
    # Arbitrage Strategies
    - type: "TriangularArbitrageStrategy"
      name: "triangular_arb"
      enabled: true
      allocation_weight: 0.8
      parameters:
        min_profit_threshold: 0.001
        
    - type: "CryptoForexArbitrageStrategy"
      name: "crypto_forex_arb"
      enabled: true
      allocation_weight: 0.8
      parameters:
        spread_threshold: 0.005
```

#### Running with Orchestration

```bash
# Start with orchestration enabled
python main.py --orchestration

# Start with specific orchestration config
python main.py --orchestration-config config/orchestration_config.yaml

# Monitor orchestration performance
python scripts/monitor_orchestration.py
```

### Enabling/Disabling Strategies

#### Via Configuration File

```yaml
strategies:
  moving_average:
    enabled: false  # Disable strategy
    
# Or with orchestration
orchestrator:
  strategies:
    - type: "MovingAverageStrategy"
      enabled: false  # Disable in orchestration
```

#### Via CLI Commands

```bash
# Disable strategy
genebot strategy disable moving_average

# Enable strategy
genebot strategy enable moving_average

# List all strategies
genebot strategy list

# Show strategy status
genebot strategy status moving_average

# Update strategy parameters
genebot strategy update moving_average --parameters '{"short_period": 12}'
```

#### Via API (if enabled)

```bash
# Disable strategy
curl -X POST http://localhost:8000/api/strategies/moving_average/disable

# Enable strategy
curl -X POST http://localhost:8000/api/strategies/moving_average/enable

# Update parameters
curl -X PUT http://localhost:8000/api/strategies/moving_average/parameters \
  -H "Content-Type: application/json" \
  -d '{"short_period": 12, "long_period": 24}'

# Get orchestration status
curl http://localhost:8000/api/orchestration/status

# Update orchestration allocation
curl -X PUT http://localhost:8000/api/orchestration/allocation \
  -H "Content-Type: application/json" \
  -d '{"moving_average": 0.15, "rsi_strategy": 0.20}'
```

### Strategy Performance Analysis

#### Viewing Strategy Metrics

```bash
# Get individual strategy performance
genebot strategy analyze moving_average --days 30

# Compare multiple strategies
genebot strategy compare moving_average rsi_strategy mean_reversion --days 30

# Get orchestration performance
genebot orchestration analyze --days 30

# View strategy allocation history
genebot orchestration allocation-history --days 7

# Get performance attribution
genebot orchestration attribution --days 30
```

#### Advanced Analytics

```bash
# Strategy correlation analysis
genebot analytics correlation --strategies all --days 30

# Risk attribution analysis
genebot analytics risk-attribution --days 30

# Performance decomposition
genebot analytics decompose-performance --days 30

# Strategy efficiency metrics
genebot analytics efficiency --strategies all
```

#### Backtesting Strategies

```bash
# Backtest single strategy
genebot backtest strategy moving_average \
  --symbol BTC/USDT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Backtest multiple strategies
genebot backtest strategies moving_average,rsi_strategy,mean_reversion \
  --symbols BTC/USDT,ETH/USDT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Backtest orchestration system
genebot backtest orchestration \
  --config config/orchestration_config.yaml \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Optimize orchestration parameters
genebot optimize orchestration \
  --parameter-ranges config/optimization_ranges.yaml \
  --start-date 2023-01-01 \
  --end-date 2023-12-31
```

#### Strategy Selection and Optimization

```bash
# Auto-select best performing strategies
genebot orchestration auto-select --lookback-days 90 --max-strategies 5

# Optimize allocation weights
genebot orchestration optimize-allocation --method sharpe_ratio --days 60

# Rebalance based on recent performance
genebot orchestration rebalance --trigger performance_degradation

# Test strategy combinations
genebot orchestration test-combination \
  --strategies moving_average,rsi_strategy,multi_indicator \
  --allocation equal_weight \
  --days 30
```

### Adding New Strategies

1. **Create strategy file** in `src/strategies/`
2. **Inherit from BaseStrategy**
3. **Register strategy** in configuration
4. **Test thoroughly** before live trading

Example:
```python
from src.strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def analyze(self, data):
        # Your strategy logic here
        pass
```

## Risk Management

### Position Sizing

The bot automatically calculates position sizes based on your risk settings:

```yaml
risk_management:
  global:
    max_portfolio_risk: 0.02  # 2% of portfolio at risk per trade
    position_sizing_method: "fixed_fractional"
```

### Stop Loss Management

Configure automatic stop losses:

```yaml
risk_management:
  stop_loss:
    enabled: true
    default_percentage: 0.05  # 5% stop loss
    trailing_stop: true
    trailing_percentage: 0.03  # 3% trailing stop
```

### Portfolio Limits

Set overall portfolio limits:

```yaml
risk_management:
  position_limits:
    max_position_size: 0.1    # 10% max per position
    max_positions: 5          # Maximum 5 open positions
    max_daily_loss: 0.05      # 5% daily loss limit
```

### Emergency Stop

#### Manual Emergency Stop

```bash
# Stop all trading immediately
python scripts/emergency_stop.py

# Close all positions
python scripts/close_all_positions.py
```

#### Automatic Circuit Breakers

The bot includes automatic circuit breakers:

- **Daily loss limit**: Stops trading if daily loss exceeds threshold
- **Drawdown limit**: Stops trading if drawdown exceeds threshold
- **Error threshold**: Stops trading if too many errors occur

## Troubleshooting

### Common Issues

#### 1. Bot Won't Start

**Symptoms**: Bot exits immediately or shows connection errors

**Solutions**:
```bash
# Check configuration
python -c "from config.manager import ConfigManager; ConfigManager().validate()"

# Test database connection
python -c "from src.database import test_connection; test_connection()"

# Verify API keys
python scripts/test_exchange_connection.py
```

#### 2. No Trading Signals

**Symptoms**: Bot runs but doesn't generate any trades

**Solutions**:
- Check strategy parameters (may be too restrictive)
- Verify market data is being received
- Review strategy logs for errors
- Test strategy with historical data

```bash
# Test strategy with recent data
python scripts/test_strategy.py --strategy moving_average --symbol BTC/USDT
```

#### 3. Exchange Connection Issues

**Symptoms**: API errors, connection timeouts

**Solutions**:
- Verify API keys and permissions
- Check exchange status
- Review rate limiting settings
- Test with different exchange endpoints

```bash
# Test exchange connectivity
python scripts/test_exchange.py --exchange binance
```

#### 4. High Memory Usage

**Symptoms**: Bot consumes excessive memory

**Solutions**:
- Reduce data retention period
- Limit number of symbols/timeframes
- Enable data compression
- Restart bot periodically

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Start with debug logging
python main.py --log-level DEBUG

# Enable profiling
python main.py --profile

# Memory tracking
python main.py --track-memory
```

### Health Checks

The bot provides health check endpoints:

```bash
# Check overall health
curl http://localhost:8001/health

# Check specific components
curl http://localhost:8001/health/database
curl http://localhost:8001/health/exchanges
curl http://localhost:8001/health/strategies
```

## Best Practices

### Security

1. **API Key Security**
   - Use environment variables for API keys
   - Enable IP restrictions on exchange accounts
   - Use read-only keys for monitoring
   - Rotate keys regularly

2. **System Security**
   - Run bot with limited user privileges
   - Use firewall to restrict network access
   - Keep system and dependencies updated
   - Monitor for unauthorized access

### Risk Management

1. **Start Small**
   - Begin with paper trading
   - Use small position sizes initially
   - Gradually increase exposure as confidence grows

2. **Diversification**
   - Don't put all capital in one strategy
   - Trade multiple uncorrelated assets
   - Use different timeframes

3. **Monitoring**
   - Check bot performance daily
   - Set up comprehensive alerts
   - Review and adjust strategies regularly

### Performance Optimization

1. **Resource Management**
   - Monitor CPU and memory usage
   - Optimize database queries
   - Use appropriate data retention periods

2. **Strategy Optimization**
   - Regularly backtest strategies
   - Monitor strategy performance metrics
   - Disable underperforming strategies

3. **Data Management**
   - Ensure reliable data feeds
   - Implement data validation
   - Have backup data sources

### Maintenance

1. **Regular Tasks**
   - Review logs weekly
   - Update dependencies monthly
   - Backup configuration and data
   - Test disaster recovery procedures

2. **Performance Review**
   - Monthly strategy performance review
   - Quarterly risk assessment
   - Annual system architecture review

### Documentation

1. **Keep Records**
   - Document configuration changes
   - Maintain trading journal
   - Record system modifications

2. **Version Control**
   - Use git for code changes
   - Tag releases
   - Maintain changelog

## Support and Community

### Getting Help

1. **Documentation**: Check this guide and API documentation
2. **Logs**: Review application logs for error details
3. **GitHub Issues**: Report bugs and feature requests
4. **Community**: Join discussions and share experiences

### Contributing

1. **Bug Reports**: Use GitHub issues with detailed information
2. **Feature Requests**: Describe use cases and benefits
3. **Code Contributions**: Follow contribution guidelines
4. **Documentation**: Help improve guides and examples

---

**Disclaimer**: Trading involves risk of loss. This bot is provided as-is without warranty. Always test thoroughly before live trading and never risk more than you can afford to lose.
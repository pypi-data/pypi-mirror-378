# GeneBot Comprehensive Configuration Guide v1.1.28

This guide covers all configuration options available in GeneBot v1.1.28, including all supported strategies, exchanges, brokers, and the new orchestrator system.

> **📖 New in v1.1.28+**: GeneBot now uses a unified configuration system with intelligent discovery and automatic CLI integration. See the [Unified Configuration Guide](UNIFIED_CONFIGURATION_GUIDE.md) for details on the new system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Files Overview](#configuration-files-overview)
3. [Environment Variables](#environment-variables)
4. [Supported Exchanges and Brokers](#supported-exchanges-and-brokers)
5. [Available Strategies](#available-strategies)
6. [Orchestrator Configuration](#orchestrator-configuration)
7. [Multi-Market Configuration](#multi-market-configuration)
8. [Configuration Templates](#configuration-templates)
9. [Validation and Migration](#validation-and-migration)
10. [Best Practices](#best-practices)
11. [Additional Resources](#additional-resources)

## Quick Start

> **🚀 Unified Configuration System**: GeneBot v1.1.28+ uses an intelligent configuration discovery system. The bot automatically finds and uses configuration files created by the CLI.

### 1. Initialize Configuration

```bash
# Create default configuration files (automatically discovered by bot)
genebot init-config

# Create production configuration
genebot init-config --template production

# Overwrite existing files
genebot init-config --overwrite
```

### 2. Configure Environment Variables

Edit the `.env` file with your API credentials:

```bash
# Crypto Exchange API Keys
BINANCE_API_KEY=your_actual_binance_api_key
BINANCE_API_SECRET=your_actual_binance_api_secret
BINANCE_SANDBOX=true

# Forex Broker Credentials  
OANDA_API_KEY=your_actual_oanda_api_key
OANDA_ACCOUNT_ID=your_actual_oanda_account_id
OANDA_ENVIRONMENT=practice
```

### 3. Validate Configuration

```bash
# Validate all configuration files
genebot validate

# Check configuration status and discovery
genebot config-status --verbose

# Start bot (automatically uses discovered configuration)
genebot start
```

## Configuration Files Overview

GeneBot uses several configuration files that are automatically discovered by the unified configuration system:

### Primary Configuration Files (Auto-discovered)
- **`config/trading_bot_config.yaml`** - Main bot configuration (CLI-generated)
- **`config/accounts.yaml`** - Exchange and broker account configurations (CLI-generated)
- **`.env`** - Environment variables and API credentials (CLI-generated)

### Optional Configuration Files
- **`config/multi_market_config.yaml`** - Multi-market specific settings (optional)
- **`config/orchestrator_config.yaml`** - Strategy orchestration settings (optional)
- **`config/logging_config.yaml`** - Logging configuration
- **`config/monitoring_config.yaml`** - Monitoring and alerting configuration

### Configuration Discovery Order
The unified system searches for configuration files in this order:
1. **CLI-generated paths** (highest priority) - `config/` directory
2. **Environment variable overrides** - `GENEBOT_CONFIG_FILE`, etc.
3. **Current directory** - `./trading_bot_config.yaml`, etc.
4. **Default locations** - `~/.genebot/config/`, etc.

> **💡 Tip**: Use `genebot config-status` to see which configuration files are being used.

## Environment Variables

### Application Settings
```bash
GENEBOT_ENV=development          # development, staging, production
DEBUG=true                       # Enable debug mode
DRY_RUN=true                    # Paper trading mode
APP_NAME=GeneBot                # Application name
APP_VERSION=1.1.28              # Version
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Crypto Exchange API Credentials

#### Binance
```bash
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BINANCE_SANDBOX=true
```

#### Coinbase Pro
```bash
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_api_secret_here
COINBASE_PASSPHRASE=your_coinbase_passphrase_here
COINBASE_SANDBOX=true
```

#### Kraken
```bash
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_API_SECRET=your_kraken_api_secret_here
```

#### KuCoin
```bash
KUCOIN_API_KEY=your_kucoin_api_key_here
KUCOIN_API_SECRET=your_kucoin_api_secret_here
KUCOIN_PASSPHRASE=your_kucoin_passphrase_here
KUCOIN_SANDBOX=true
```

#### Bybit
```bash
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
BYBIT_SANDBOX=true
```

### Forex Broker Credentials

#### OANDA
```bash
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_ENVIRONMENT=practice      # practice or live
```

#### MetaTrader 5
```bash
MT5_LOGIN=your_mt5_login_here
MT5_PASSWORD=your_mt5_password_here
MT5_SERVER=your_mt5_server_here
MT5_PATH=/Applications/MetaTrader 5/terminal64.exe
```

#### Interactive Brokers
```bash
IB_HOST=127.0.0.1
IB_PORT=7497                    # 7497 for paper, 7496 for live
IB_CLIENT_ID=1
```

#### Alpaca
```bash
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_API_SECRET=your_alpaca_api_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

#### FXCM
```bash
FXCM_API_KEY=your_fxcm_api_key_here
FXCM_ACCESS_TOKEN=your_fxcm_access_token_here
FXCM_SERVER=demo               # demo or real
```

## Supported Exchanges and Brokers

### Crypto Exchanges

| Exchange | Sandbox | Supported Symbols | Fee Structure |
|----------|---------|-------------------|---------------|
| **Binance** | ✅ | BTC/USDT, ETH/USDT, ADA/USDT, DOT/USDT, LTC/USDT, BNB/USDT, SOL/USDT, MATIC/USDT | 0.1% maker/taker |
| **Coinbase Pro** | ✅ | BTC/USD, ETH/USD, ADA/USD, DOT/USD, LTC/USD | 0.5% maker/taker |
| **Kraken** | ❌ | BTC/USD, ETH/USD, ADA/USD, DOT/USD, LTC/USD | 0.16% maker, 0.26% taker |
| **KuCoin** | ✅ | BTC/USDT, ETH/USDT, ADA/USDT, DOT/USDT, LTC/USDT | 0.1% maker/taker |
| **Bybit** | ✅ | BTC/USDT, ETH/USDT, ADA/USDT, DOT/USDT, SOL/USDT | 0.1% maker/taker |

### Forex Brokers

| Broker | Sandbox | Supported Pairs | Leverage |
|--------|---------|-----------------|----------|
| **OANDA** | ✅ | EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD | 50:1 |
| **MetaTrader 5** | ✅ | EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD | 100:1 |
| **Interactive Brokers** | ✅ | EUR.USD, GBP.USD, USD.JPY, USD.CHF, AUD.USD, USD.CAD, NZD.USD | Variable |
| **Alpaca** | ✅ | EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD | Variable |
| **FXCM** | ✅ | EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD | Variable |

## Available Strategies

### Technical Analysis Strategies

#### 1. RSI Strategy (`rsi`)
**Description**: Trades based on RSI overbought/oversold conditions

**Parameters**:
- `rsi_period`: RSI calculation period (default: 14)
- `oversold_threshold`: Buy signal threshold (default: 30)
- `overbought_threshold`: Sell signal threshold (default: 70)
- `min_confidence`: Minimum signal confidence (default: 0.7)

**Markets**: Crypto, Forex

#### 2. Moving Average Strategy (`moving_average`)
**Description**: Simple moving average crossover strategy

**Parameters**:
- `short_window`: Short-term MA period (default: 10)
- `long_window`: Long-term MA period (default: 30)
- `min_confidence`: Minimum signal confidence (default: 0.7)

**Markets**: Crypto, Forex

#### 3. Mean Reversion Strategy (`mean_reversion`)
**Description**: Trades when price deviates significantly from mean

**Parameters**:
- `lookback_period`: Historical data period (default: 20)
- `std_dev_multiplier`: Standard deviation multiplier (default: 2.0)
- `min_confidence`: Minimum signal confidence (default: 0.75)
- `reversion_threshold`: Price deviation threshold (default: 0.02)

**Markets**: Crypto, Forex

#### 4. Multi-Indicator Strategy (`multi_indicator`)
**Description**: Combines MA, RSI, MACD, and Bollinger Bands

**Parameters**:
- `ma_fast`: Fast moving average (default: 10)
- `ma_slow`: Slow moving average (default: 20)
- `rsi_period`: RSI period (default: 14)
- `rsi_oversold`: RSI oversold level (default: 30)
- `rsi_overbought`: RSI overbought level (default: 70)
- `macd_fast`: MACD fast EMA (default: 12)
- `macd_slow`: MACD slow EMA (default: 26)
- `macd_signal`: MACD signal line (default: 9)
- `bollinger_period`: Bollinger bands period (default: 20)
- `bollinger_std`: Bollinger bands std dev (default: 2.0)
- `min_confidence`: Minimum signal confidence (default: 0.85)

**Markets**: Crypto, Forex

#### 5. ATR Volatility Strategy (`atr_volatility`)
**Description**: Trades based on volatility breakouts using ATR

**Parameters**:
- `atr_period`: ATR calculation period (default: 14)
- `atr_multiplier`: ATR multiplier for signals (default: 2.0)
- `volatility_threshold`: Minimum volatility threshold (default: 0.02)
- `min_confidence`: Minimum signal confidence (default: 0.8)
- `breakout_confirmation`: Require breakout confirmation (default: true)

**Markets**: Crypto, Forex

#### 6. Advanced Momentum Strategy (`advanced_momentum`)
**Description**: Advanced momentum strategy with volume confirmation

**Parameters**:
- `momentum_period`: Momentum calculation period (default: 20)
- `rsi_period`: RSI period for confirmation (default: 14)
- `volume_threshold`: Volume spike threshold (default: 1.5)
- `price_change_threshold`: Minimum price change (default: 0.03)
- `min_confidence`: Minimum signal confidence (default: 0.8)
- `trend_confirmation`: Require trend confirmation (default: true)

**Markets**: Crypto, Forex

#### 7. ML Pattern Strategy (`ml_pattern`)
**Description**: Uses machine learning to identify chart patterns

**Parameters**:
- `pattern_lookback`: Historical pattern lookback (default: 50)
- `confidence_threshold`: ML model confidence threshold (default: 0.85)
- `feature_count`: Number of features to use (default: 20)
- `model_retrain_interval`: Retrain interval in hours (default: 168)
- `pattern_types`: Pattern types to detect (default: ["head_shoulders", "double_top", "triangle", "flag"])
- `min_pattern_strength`: Minimum pattern strength (default: 0.7)

**Markets**: Crypto, Forex

### Forex-Specific Strategies

#### 8. Forex Session Strategy (`forex_session`)
**Description**: Trades during high-volume forex session overlaps

**Parameters**:
- `session_overlap_only`: Trade only during overlaps (default: true)
- `min_volatility_threshold`: Minimum volatility in pips (default: 0.0015)
- `momentum_period`: Momentum calculation period (default: 20)
- `atr_period`: ATR period (default: 14)
- `atr_multiplier`: ATR multiplier (default: 2.0)
- `rsi_period`: RSI period (default: 14)
- `rsi_oversold`: RSI oversold level (default: 30)
- `rsi_overbought`: RSI overbought level (default: 70)
- `preferred_sessions`: Preferred sessions (default: ["london", "new_york"])
- `min_overlap_minutes`: Minimum overlap duration (default: 60)

**Markets**: Forex only

#### 9. Forex Carry Trade Strategy (`forex_carry_trade`)
**Description**: Profits from interest rate differentials

**Parameters**:
- `min_interest_differential`: Minimum interest rate difference (default: 0.02)
- `trend_confirmation_period`: Trend confirmation period (default: 20)
- `volatility_threshold`: Maximum volatility threshold (default: 0.01)
- `correlation_threshold`: Correlation threshold (default: 0.7)
- `swap_positive_only`: Only positive swap trades (default: true)
- `max_drawdown_threshold`: Maximum drawdown allowed (default: 0.05)

**Markets**: Forex only

#### 10. Forex News Strategy (`forex_news`)
**Description**: Trades on high-impact news events

**Parameters**:
- `news_impact_threshold`: Minimum news impact level (default: "high")
- `pre_news_minutes`: Minutes before news to prepare (default: 15)
- `post_news_minutes`: Minutes after news to trade (default: 60)
- `volatility_multiplier`: Expected volatility increase (default: 2.0)
- `news_sources`: News sources (default: ["forex_factory", "economic_calendar"])
- `currency_focus`: Currency focus (default: ["USD", "EUR", "GBP", "JPY"])

**Markets**: Forex only

### Arbitrage Strategies

#### 11. Cross-Market Arbitrage Strategy (`cross_market_arbitrage`)
**Description**: Arbitrage opportunities between crypto and forex markets

**Parameters**:
- `min_arbitrage_opportunity`: Minimum profit opportunity (default: 0.001)
- `max_execution_time`: Maximum execution time in seconds (default: 30)
- `correlation_threshold`: Correlation threshold (default: 0.7)
- `min_confidence`: Minimum signal confidence (default: 0.90)
- `slippage_tolerance`: Maximum slippage tolerance (default: 0.0005)
- `transaction_cost_estimate`: Estimated transaction costs (default: 0.002)

**Markets**: Crypto, Forex

#### 12. Crypto-Forex Arbitrage Strategy (`crypto_forex_arbitrage`)
**Description**: Specialized crypto-forex arbitrage

**Parameters**:
- `min_spread_threshold`: Minimum spread for opportunity (default: 0.002)
- `max_position_hold_time`: Maximum hold time in seconds (default: 300)
- `correlation_window`: Correlation calculation window (default: 100)
- `volatility_adjustment`: Adjust for volatility (default: true)
- `hedge_ratio`: Hedge ratio between markets (default: 1.0)

**Markets**: Crypto, Forex

#### 13. Triangular Arbitrage Strategy (`triangular_arbitrage`)
**Description**: Three-way arbitrage within crypto markets

**Parameters**:
- `min_profit_threshold`: Minimum profit threshold (default: 0.001)
- `max_execution_time`: Maximum execution time in seconds (default: 10)
- `transaction_cost_estimate`: Estimated transaction costs (default: 0.001)
- `slippage_buffer`: Slippage buffer (default: 0.0005)
- `currency_triangles`: Currency triangles to monitor

**Markets**: Crypto only

### Market-Agnostic Strategies

#### 14. Market Agnostic Strategy (`market_agnostic`)
**Description**: Unified strategy that works across all markets

**Parameters**:
- `universal_indicators`: Universal indicators (default: ["rsi", "ma", "volume"])
- `market_correlation_threshold`: Market correlation threshold (default: 0.5)
- `cross_market_confirmation`: Cross-market confirmation (default: true)
- `adaptive_parameters`: Adaptive parameters (default: true)
- `market_weights`: Market weights (crypto: 0.6, forex: 0.4)

**Markets**: Crypto, Forex

#### 15. Market Specific Strategy (`market_specific`)
**Description**: Adapts strategy based on specific market characteristics

**Parameters**:
- `crypto_specific`: Crypto-specific settings
- `forex_specific`: Forex-specific settings
- `market_detection_threshold`: Market detection threshold (default: 0.8)

**Markets**: Crypto, Forex

## Configuration Templates

### Available Templates

1. **Development Template** (`development`)
   - Safe defaults for testing
   - Sandbox/testnet enabled
   - Conservative risk settings
   - Debug logging enabled

2. **Production Template** (`production`)
   - Optimized for live trading
   - Sandbox disabled
   - Standard risk settings
   - Info-level logging

3. **Multi-Market Template** (`multi_market`)
   - Full multi-market configuration
   - All strategies documented
   - Both crypto and forex support

### Using Templates

```bash
# Initialize with development template (default)
genebot init-config

# Initialize with production template
genebot init-config --template production

# Initialize with multi-market template
genebot init-config --template multi_market
```

## Validation and Migration

### Configuration Validation

```bash
# Validate all configuration files
genebot validate

# Validate with verbose output
genebot validate --verbose

# Check configuration status
genebot config-status
```

### Configuration Migration

```bash
# Migrate configuration to latest version
genebot migrate-config

# Backup configuration before changes
genebot config-backup

# Restore from backup
genebot config-restore --timestamp 2024-01-01_12-00-00
```

## Best Practices

### Security
1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Enable IP whitelisting** where supported
4. **Use read-only API keys** for validation when possible
5. **Regularly rotate API keys**

### Configuration Management
1. **Start with sandbox/testnet** accounts
2. **Validate configuration** before live trading
3. **Create backups** before making changes
4. **Use version control** for configuration files (excluding .env)
5. **Test with small amounts** first

### Strategy Selection
1. **Start with simple strategies** (RSI, Moving Average)
2. **Test thoroughly** in paper trading mode
3. **Monitor correlation** between strategies
4. **Adjust risk parameters** based on your risk tolerance
5. **Regularly review performance** and disable underperforming strategies

### Risk Management
1. **Set appropriate position sizes** (typically 1-5% per trade)
2. **Use stop losses** and take profits
3. **Monitor drawdown** regularly
4. **Diversify across markets** and strategies
5. **Never risk more than you can afford to lose**

### Performance Monitoring
1. **Track strategy performance** individually
2. **Monitor system resources** during operation
3. **Review logs** regularly for errors
4. **Set up alerts** for critical issues
5. **Analyze correlation** between positions

## Troubleshooting

### Common Issues

1. **Configuration validation errors**
   - Check YAML syntax
   - Verify required fields are present
   - Ensure strategy types are valid

2. **API connection failures**
   - Verify API credentials
   - Check network connectivity
   - Confirm API key permissions

3. **Strategy loading errors**
   - Check strategy type spelling
   - Verify parameter ranges
   - Ensure required parameters are provided

### Getting Help

```bash
# Show configuration help
genebot config-help

# List available strategies
genebot list-strategies

# Show CLI help
genebot --help

# Show command-specific help
genebot init-config --help
```

For additional support, refer to the troubleshooting guides in the `docs/` directory or check the project repository for updates.

## Additional Resources

### Configuration System Documentation

- **[Unified Configuration Guide](UNIFIED_CONFIGURATION_GUIDE.md)** - Complete guide to the new unified configuration system
- **[Configuration Migration Guide](CONFIGURATION_MIGRATION_GUIDE.md)** - Step-by-step migration from hardcoded configurations
- **[Configuration Troubleshooting Guide](CONFIGURATION_TROUBLESHOOTING_GUIDE.md)** - Detailed troubleshooting for configuration issues

### Related Documentation

- **[CLI User Guide](CLI_USER_GUIDE.md)** - Complete CLI command reference
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment configuration
- **[Logging Architecture Guide](LOGGING_ARCHITECTURE_GUIDE.md)** - Logging system configuration

### Quick Reference Commands

```bash
# Configuration Management
genebot init-config                    # Initialize configuration
genebot config-status                  # Check configuration status
genebot validate                       # Validate configuration
genebot migrate-config                 # Migrate from old system

# Troubleshooting
genebot config-status --verbose        # Detailed configuration info
genebot validate --verbose             # Detailed validation errors
genebot config-status --show-discovery # Show discovery process
genebot config-dump --sanitize         # Export configuration (safe)
```

### Migration Support

If you're upgrading from an older version of GeneBot:

1. **Backup your current configuration** before upgrading
2. **Follow the [Migration Guide](CONFIGURATION_MIGRATION_GUIDE.md)** for step-by-step instructions
3. **Use the troubleshooting guide** if you encounter issues
4. **Test thoroughly** in development before deploying to production

The unified configuration system provides better reliability, easier management, and improved integration between CLI and bot runtime.
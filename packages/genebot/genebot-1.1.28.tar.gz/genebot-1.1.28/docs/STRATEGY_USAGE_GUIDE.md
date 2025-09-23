# GeneBot Strategy Usage Guide v1.1.28

## Table of Contents

1. [Overview](#overview)
2. [Available Strategies](#available-strategies)
3. [Strategy Configuration](#strategy-configuration)
4. [Strategy Categories](#strategy-categories)
5. [Usage Examples](#usage-examples)
6. [Performance Optimization](#performance-optimization)
7. [Risk Management](#risk-management)
8. [Multi-Market Strategies](#multi-market-strategies)
9. [Custom Strategy Development](#custom-strategy-development)
10. [Troubleshooting](#troubleshooting)

## Overview

GeneBot v1.1.28 includes a comprehensive strategy engine with 20+ built-in trading strategies covering technical analysis, machine learning, arbitrage, and multi-market trading. This guide provides detailed information on how to use, configure, and optimize these strategies.

### Strategy Engine Features

- **Dynamic Strategy Loading**: Automatic discovery and registration of strategies
- **Multi-Market Support**: Strategies that work across crypto and forex markets
- **Real-Time Performance Monitoring**: Live tracking of strategy performance
- **Risk Management Integration**: Built-in risk controls for each strategy
- **Backtesting Support**: Historical validation of strategy performance
- **Parameter Optimization**: Automated parameter tuning capabilities

## Available Strategies

### Technical Analysis Strategies

#### 1. RSI Mean Reversion Strategy
**File**: `src/strategies/rsi_strategy.py`
**Markets**: Crypto, Forex
**Description**: Uses RSI indicator to identify overbought/oversold conditions for mean reversion trades.

**Parameters**:
- `rsi_period`: RSI calculation period (default: 14)
- `oversold_threshold`: RSI level for buy signals (default: 30)
- `overbought_threshold`: RSI level for sell signals (default: 70)
- `position_size`: Position size as percentage of portfolio (default: 0.05)

#### 2. Moving Average Crossover Strategy
**File**: `src/strategies/moving_average_strategy.py`
**Markets**: Crypto, Forex
**Description**: Generates signals based on fast and slow moving average crossovers.

**Parameters**:
- `fast_ma`: Fast moving average period (default: 10)
- `slow_ma`: Slow moving average period (default: 20)
- `position_size`: Position size as percentage of portfolio (default: 0.03)

#### 3. Multi-Indicator Strategy
**File**: `src/strategies/multi_indicator_strategy.py`
**Markets**: Crypto, Forex
**Description**: Combines RSI, MACD, and Bollinger Bands for comprehensive signal generation.

**Parameters**:
- `rsi_period`: RSI period (default: 14)
- `macd_fast`: MACD fast EMA period (default: 12)
- `macd_slow`: MACD slow EMA period (default: 26)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Bollinger Bands standard deviation (default: 2)

#### 4. ATR Volatility Strategy
**File**: `src/strategies/atr_volatility_strategy.py`
**Markets**: Crypto, Forex
**Description**: Uses Average True Range (ATR) to adjust position sizes based on volatility.

**Parameters**:
- `atr_period`: ATR calculation period (default: 14)
- `volatility_multiplier`: Multiplier for volatility-based sizing (default: 2.0)
- `base_position_size`: Base position size (default: 0.02)

#### 5. Advanced Momentum Strategy
**File**: `src/strategies/advanced_momentum_strategy.py`
**Markets**: Crypto, Forex
**Description**: Advanced momentum strategy using multiple timeframes and momentum indicators.

**Parameters**:
- `momentum_period`: Momentum calculation period (default: 20)
- `rsi_period`: RSI period for momentum confirmation (default: 14)
- `volume_threshold`: Minimum volume threshold (default: 1.5)

### Machine Learning Strategies

#### 6. ML Pattern Recognition Strategy
**File**: `src/strategies/ml_pattern_strategy.py`
**Markets**: Crypto
**Description**: Uses machine learning to identify price patterns and predict future movements.

**Parameters**:
- `lookback_period`: Historical data lookback period (default: 50)
- `prediction_horizon`: Prediction time horizon (default: 5)
- `confidence_threshold`: Minimum confidence for trades (default: 0.7)
- `model_type`: ML model type (default: "random_forest")

### Arbitrage Strategies

#### 7. Cross-Market Arbitrage Strategy
**File**: `src/strategies/cross_market_arbitrage_strategy.py`
**Markets**: Crypto, Forex
**Description**: Exploits price differences between different markets or exchanges.

**Parameters**:
- `min_spread`: Minimum spread required for arbitrage (default: 0.005)
- `max_position_size`: Maximum position size (default: 0.1)
- `execution_timeout`: Order execution timeout (default: 30)

#### 8. Crypto-Forex Arbitrage Strategy
**File**: `src/strategies/crypto_forex_arbitrage_strategy.py`
**Markets**: Crypto, Forex
**Description**: Arbitrage opportunities between cryptocurrency and forex markets.

**Parameters**:
- `currency_pairs`: Supported currency pairs
- `min_profit_threshold`: Minimum profit threshold (default: 0.003)
- `max_exposure`: Maximum exposure per trade (default: 0.08)

#### 9. Triangular Arbitrage Strategy
**File**: `src/strategies/triangular_arbitrage_strategy.py`
**Markets**: Crypto
**Description**: Exploits price discrepancies in triangular currency relationships.

**Parameters**:
- `min_profit`: Minimum profit threshold (default: 0.003)
- `max_slippage`: Maximum acceptable slippage (default: 0.001)
- `execution_speed`: Execution speed priority (default: "fast")

### Forex-Specific Strategies

#### 10. Forex Session Strategy
**File**: `src/strategies/forex_session_strategy.py`
**Markets**: Forex
**Description**: Trades based on forex market session characteristics and volatility patterns.

**Parameters**:
- `session`: Trading session (london, new_york, tokyo, sydney)
- `volatility_threshold`: Minimum volatility for trades (default: 0.5)
- `session_overlap`: Trade during session overlaps (default: true)

#### 11. Forex Carry Trade Strategy
**File**: `src/strategies/forex_carry_trade_strategy.py`
**Markets**: Forex
**Description**: Exploits interest rate differentials between currency pairs.

**Parameters**:
- `min_interest_diff`: Minimum interest rate difference (default: 0.02)
- `rollover_threshold`: Minimum rollover credit (default: 0.5)
- `max_drawdown`: Maximum acceptable drawdown (default: 0.05)

#### 12. Forex News Strategy
**File**: `src/strategies/forex_news_strategy.py`
**Markets**: Forex
**Description**: Trades based on economic news events and their market impact.

**Parameters**:
- `news_impact_threshold`: Minimum news impact level (default: "medium")
- `pre_news_buffer`: Time buffer before news (default: 300)
- `post_news_buffer`: Time buffer after news (default: 600)

#### 13. Forex Technical Indicators Strategy
**File**: `src/strategies/forex_technical_indicators.py`
**Markets**: Forex
**Description**: Forex-optimized technical indicators with currency-specific parameters.

**Parameters**:
- `major_pairs_only`: Trade major pairs only (default: true)
- `spread_threshold`: Maximum spread threshold (default: 3)
- `volatility_filter`: Enable volatility filtering (default: true)

### Multi-Market Strategies

#### 14. Market Agnostic Strategy
**File**: `src/strategies/market_agnostic_strategy.py`
**Markets**: Crypto, Forex
**Description**: Universal strategy that adapts to different market characteristics.

**Parameters**:
- `adaptation_period`: Market adaptation period (default: 30)
- `market_regime_detection`: Enable regime detection (default: true)
- `cross_asset_correlation`: Consider cross-asset correlations (default: true)

#### 15. Market Specific Strategy
**File**: `src/strategies/market_specific_strategy.py`
**Markets**: Crypto, Forex
**Description**: Optimized strategies for specific market types with tailored parameters.

**Parameters**:
- `market_type`: Target market type (crypto, forex)
- `optimization_method`: Parameter optimization method (default: "genetic")
- `reoptimization_frequency`: How often to reoptimize (default: "weekly")

#### 16. Multi-Market Strategy Engine
**File**: `src/strategies/multi_market_strategy_engine.py`
**Markets**: Crypto, Forex
**Description**: Coordinates multiple strategies across different markets.

**Parameters**:
- `max_strategies`: Maximum concurrent strategies (default: 5)
- `allocation_method`: Strategy allocation method (default: "performance_based")
- `rebalance_frequency`: Rebalancing frequency (default: "daily")

## Strategy Configuration

### Basic Configuration Format

```yaml
strategies:
  - name: "Strategy_Name"
    type: "StrategyClassName"
    enabled: true
    markets: ["crypto", "forex"]
    parameters:
      parameter1: value1
      parameter2: value2
    risk_limits:
      max_position_size: 0.05
      stop_loss: 0.02
      take_profit: 0.04
```

### Advanced Configuration Example

```yaml
strategies:
  - name: "Advanced_RSI_Strategy"
    type: "RSIStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      rsi_period: 21
      oversold_threshold: 25
      overbought_threshold: 75
      position_size: 0.03
      confirmation_required: true
      volume_filter: true
    risk_limits:
      max_position_size: 0.05
      stop_loss: 0.02
      take_profit: 0.06
      max_drawdown: 0.10
    schedule:
      active_hours: "09:00-17:00"
      timezone: "UTC"
      trading_days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
```

## Strategy Categories

### 1. Trend Following Strategies
- Moving Average Crossover
- Advanced Momentum Strategy
- Multi-Indicator Strategy (trend component)

**Best for**: Trending markets, longer timeframes
**Risk**: Whipsaws in sideways markets

### 2. Mean Reversion Strategies
- RSI Mean Reversion
- Multi-Indicator Strategy (mean reversion component)

**Best for**: Range-bound markets, shorter timeframes
**Risk**: Trend continuation against position

### 3. Volatility-Based Strategies
- ATR Volatility Strategy
- Forex Session Strategy

**Best for**: Volatile market conditions
**Risk**: Low volatility periods

### 4. Arbitrage Strategies
- Cross-Market Arbitrage
- Triangular Arbitrage
- Crypto-Forex Arbitrage

**Best for**: Market inefficiencies, high-frequency trading
**Risk**: Execution delays, slippage

### 5. Machine Learning Strategies
- ML Pattern Recognition

**Best for**: Complex pattern recognition, adaptive trading
**Risk**: Overfitting, model degradation

## Usage Examples

### Example 1: Basic RSI Strategy Setup

```bash
# 1. Configure strategy in config/trading_bot_config.yaml
nano config/trading_bot_config.yaml

# Add RSI strategy configuration:
strategies:
  - name: "My_RSI_Strategy"
    type: "RSIStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      rsi_period: 14
      oversold_threshold: 30
      overbought_threshold: 70
      position_size: 0.05

# 2. Validate configuration
genebot validate-config

# 3. Start bot with strategy
genebot start
```

### Example 2: Multi-Strategy Portfolio

```yaml
strategies:
  # Trend following component
  - name: "Trend_Following"
    type: "MovingAverageStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      fast_ma: 10
      slow_ma: 20
      position_size: 0.02
      
  # Mean reversion component
  - name: "Mean_Reversion"
    type: "RSIStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      rsi_period: 14
      oversold_threshold: 30
      overbought_threshold: 70
      position_size: 0.02
      
  # Arbitrage component
  - name: "Arbitrage"
    type: "CrossMarketArbitrageStrategy"
    enabled: true
    markets: ["crypto", "forex"]
    parameters:
      min_spread: 0.005
      max_position_size: 0.03
```

### Example 3: Forex-Specific Setup

```yaml
strategies:
  - name: "London_Session_Trading"
    type: "ForexSessionStrategy"
    enabled: true
    markets: ["forex"]
    parameters:
      session: "london"
      volatility_threshold: 0.5
      currency_pairs: ["EUR/USD", "GBP/USD", "USD/JPY"]
      
  - name: "Carry_Trade"
    type: "ForexCarryTradeStrategy"
    enabled: true
    markets: ["forex"]
    parameters:
      min_interest_diff: 0.02
      currency_pairs: ["AUD/JPY", "NZD/JPY", "EUR/TRY"]
```

## Performance Optimization

### 1. Parameter Optimization

```bash
# Use built-in parameter optimization
genebot analytics optimization --strategy RSIStrategy --period 30days

# Manual backtesting for parameter tuning
genebot backtest --strategy RSIStrategy --parameters '{"rsi_period": [10,14,21], "oversold_threshold": [25,30,35]}'
```

### 2. Strategy Selection

```bash
# Analyze strategy performance
genebot analytics performance --strategy all --period 30days

# Compare strategies
genebot analytics correlation --strategies RSIStrategy,MovingAverageStrategy
```

### 3. Risk-Adjusted Returns

```yaml
# Configure risk-adjusted position sizing
strategies:
  - name: "Risk_Adjusted_RSI"
    type: "RSIStrategy"
    enabled: true
    parameters:
      position_sizing_method: "volatility_adjusted"
      base_position_size: 0.02
      volatility_lookback: 20
      max_position_size: 0.08
```

## Risk Management

### Strategy-Level Risk Controls

```yaml
strategies:
  - name: "Controlled_Strategy"
    type: "RSIStrategy"
    enabled: true
    risk_limits:
      max_position_size: 0.05        # Maximum 5% position size
      stop_loss: 0.02                # 2% stop loss
      take_profit: 0.04              # 4% take profit
      max_drawdown: 0.10             # Stop if 10% drawdown
      max_daily_trades: 5            # Maximum 5 trades per day
      max_consecutive_losses: 3      # Stop after 3 consecutive losses
      correlation_limit: 0.7         # Maximum correlation with other positions
```

### Portfolio-Level Risk Management

```yaml
risk_management:
  global_limits:
    max_portfolio_risk: 0.02         # 2% portfolio risk per trade
    max_total_exposure: 0.8          # Maximum 80% portfolio exposure
    max_drawdown: 0.15               # Stop all trading at 15% drawdown
    max_correlation: 0.7             # Maximum position correlation
  
  position_sizing:
    method: "kelly_criterion"        # Position sizing method
    max_kelly_fraction: 0.25         # Maximum Kelly fraction
    min_position_size: 0.01          # Minimum position size
    max_position_size: 0.10          # Maximum position size
```

## Multi-Market Strategies

### Cross-Market Configuration

```yaml
multi_market:
  enabled: true
  cross_market_arbitrage: true
  correlation_threshold: 0.8
  max_exposure_per_market: 0.6
  
strategies:
  - name: "Cross_Market_Strategy"
    type: "CrossMarketArbitrageStrategy"
    enabled: true
    markets: ["crypto", "forex"]
    parameters:
      crypto_exchanges: ["binance", "coinbase"]
      forex_brokers: ["oanda", "ib"]
      min_spread: 0.005
      execution_timeout: 30
```

### Market Correlation Analysis

```bash
# Analyze cross-market correlations
genebot analytics correlation --markets crypto,forex --period 30days

# Monitor cross-market exposure
genebot monitor --cross-market
```

## Custom Strategy Development

### 1. Create Strategy Class

```python
# File: src/strategies/my_custom_strategy.py
from .base_strategy import BaseStrategy, StrategyConfig

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.setup_parameters()
    
    def setup_parameters(self):
        self.period = self.config.parameters.get('period', 20)
        self.threshold = self.config.parameters.get('threshold', 0.02)
    
    def generate_signals(self, data):
        # Implement your signal generation logic
        pass
    
    def validate_parameters(self) -> bool:
        # Validate strategy parameters
        return True
```

### 2. Register Strategy

```python
# The strategy will be automatically discovered and registered
# when placed in the src/strategies/ directory
```

### 3. Configure Strategy

```yaml
strategies:
  - name: "My_Custom_Strategy"
    type: "MyCustomStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      period: 20
      threshold: 0.02
```

## Troubleshooting

### Common Strategy Issues

#### Strategy Not Loading
```bash
# Check strategy registration
genebot list-strategies

# Validate strategy configuration
genebot validate-config

# Check logs for errors
tail -f logs/genebot.log | grep -i strategy
```

#### Strategy Not Generating Signals
```bash
# Check strategy status
genebot status --detailed

# Monitor strategy in real-time
genebot monitor --strategy MyStrategy

# Check market data availability
genebot validate-accounts
```

#### Poor Strategy Performance
```bash
# Analyze strategy performance
genebot analytics performance --strategy MyStrategy

# Compare with benchmark
genebot analytics attribution --strategy MyStrategy

# Optimize parameters
genebot analytics optimization --strategy MyStrategy
```

### Performance Issues

#### High CPU Usage
- Reduce number of active strategies
- Increase signal generation intervals
- Optimize strategy algorithms

#### Memory Issues
- Limit historical data retention
- Reduce strategy lookback periods
- Implement data cleanup routines

#### Slow Execution
- Optimize order execution logic
- Use faster data feeds
- Implement parallel processing

### Configuration Issues

#### Invalid Parameters
```bash
# Validate strategy parameters
genebot validate-config --verbose

# Check parameter ranges and types
genebot config-help
```

#### Strategy Conflicts
```bash
# Check for conflicting strategies
genebot analytics correlation --strategies all

# Monitor position overlaps
genebot monitor --positions
```

For additional support, refer to the main troubleshooting guide or contact support.
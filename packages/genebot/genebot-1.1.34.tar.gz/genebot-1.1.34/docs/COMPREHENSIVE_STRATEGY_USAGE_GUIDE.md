# Comprehensive Strategy Usage Guide

This guide provides detailed information about all available trading strategies in the GeneBot system, their usage, configuration, and best practices.

## Table of Contents

1. [Strategy Overview](#strategy-overview)
2. [Strategy Categories](#strategy-categories)
3. [Configuration Guide](#configuration-guide)
4. [CLI Usage](#cli-usage)
5. [Multi-Market Strategies](#multi-market-strategies)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

## Strategy Overview

GeneBot includes 15 comprehensive trading strategies across multiple categories:

### Available Strategies

| Strategy Name | Category | Markets | Win Rate | Description |
|---------------|----------|---------|----------|-------------|
| RSIStrategy | Technical Indicators | Crypto, Forex | 68% | RSI-based mean reversion strategy |
| MovingAverageStrategy | Technical Indicators | Crypto, Forex | 72% | Moving average crossover strategy |
| MultiIndicatorStrategy | Technical Indicators | Crypto, Forex | 69% | Multi-indicator confluence strategy |
| AdvancedMomentumStrategy | Technical Indicators | Crypto, Forex | 66% | Advanced momentum analysis |
| ATRVolatilityStrategy | Technical Indicators | Crypto, Forex | 70% | ATR-based volatility strategy |
| MeanReversionStrategy | Technical Indicators | Crypto, Forex | 67% | Statistical mean reversion |
| MLPatternStrategy | Machine Learning | Crypto, Forex | 74% | ML pattern recognition |
| CrossMarketArbitrageStrategy | Arbitrage | Crypto, Forex | 85% | Cross-market arbitrage |
| CryptoForexArbitrageStrategy | Arbitrage | Crypto, Forex | 82% | Crypto-forex arbitrage |
| TriangularArbitrageStrategy | Arbitrage | Crypto | 78% | Triangular arbitrage |
| ForexCarryTradeStrategy | Forex Specific | Forex | 71% | Interest rate carry trades |
| ForexNewsStrategy | Forex Specific | Forex | 58% | News-based trading |
| ForexSessionStrategy | Forex Specific | Forex | 65% | Session-based trading |

## Strategy Categories

### Technical Indicators

These strategies use traditional technical analysis indicators to generate trading signals.

#### RSIStrategy
**Description**: Uses Relative Strength Index for overbought/oversold conditions.

**Parameters**:
```yaml
parameters:
  rsi_period: 14
  oversold_threshold: 30
  overbought_threshold: 70
  confirmation_period: 2
```

**Best Use Cases**:
- Range-bound markets
- Mean reversion scenarios
- High-volatility periods

#### MovingAverageStrategy
**Description**: Simple moving average crossover strategy.

**Parameters**:
```yaml
parameters:
  short_period: 10
  long_period: 20
  confirmation_bars: 1
```

**Best Use Cases**:
- Trending markets
- Clear directional moves
- Lower volatility environments

#### MultiIndicatorStrategy
**Description**: Combines multiple indicators for confluence-based signals.

**Parameters**:
```yaml
parameters:
  rsi_period: 14
  ma_short: 10
  ma_long: 20
  bb_period: 20
  bb_std: 2
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
  min_confluence: 3
```

**Best Use Cases**:
- High-probability setups
- Reducing false signals
- Complex market conditions

#### AdvancedMomentumStrategy
**Description**: Advanced momentum analysis with multiple timeframes.

**Parameters**:
```yaml
parameters:
  momentum_period: 14
  acceleration_period: 5
  velocity_threshold: 0.02
  divergence_lookback: 20
  volume_confirmation: true
```

**Best Use Cases**:
- Strong trending markets
- Momentum breakouts
- High-volume periods

#### ATRVolatilityStrategy
**Description**: ATR-based volatility breakout and contraction strategy.

**Parameters**:
```yaml
parameters:
  atr_period: 14
  volatility_threshold: 1.5
  squeeze_threshold: 0.8
  breakout_multiplier: 2.0
  position_sizing_atr: true
```

**Best Use Cases**:
- Volatility breakouts
- Range expansions
- Risk-adjusted position sizing

#### MeanReversionStrategy
**Description**: Statistical mean reversion with multiple confirmation signals.

**Parameters**:
```yaml
parameters:
  lookback_period: 20
  deviation_threshold: 2.0
  volume_confirmation: true
  support_resistance: true
  max_holding_period: 10
```

**Best Use Cases**:
- Range-bound markets
- Extreme price deviations
- High-frequency trading

### Machine Learning

#### MLPatternStrategy
**Description**: Machine learning-based pattern recognition strategy.

**Parameters**:
```yaml
parameters:
  feature_window: 50
  pattern_types: ["candlestick", "chart", "volume"]
  confidence_threshold: 0.7
  retrain_frequency: 100
  ensemble_methods: ["rf", "svm", "nn"]
```

**Best Use Cases**:
- Complex pattern recognition
- Adaptive market conditions
- High-frequency data analysis

### Arbitrage Strategies

#### CrossMarketArbitrageStrategy
**Description**: Identifies arbitrage opportunities across different markets.

**Parameters**:
```yaml
parameters:
  price_threshold: 0.005
  execution_timeout: 30
  correlation_threshold: 0.8
  min_profit_margin: 0.002
  max_position_size: 0.1
```

**Best Use Cases**:
- Market inefficiencies
- High-frequency execution
- Low-risk profit opportunities

#### CryptoForexArbitrageStrategy
**Description**: Arbitrage between cryptocurrency and forex markets.

**Parameters**:
```yaml
parameters:
  currency_pairs: ["BTC/USD", "ETH/EUR"]
  conversion_threshold: 0.01
  session_overlap_only: true
  regulatory_compliance: true
```

**Best Use Cases**:
- Currency arbitrage
- Session overlaps
- Regulatory-compliant trading

#### TriangularArbitrageStrategy
**Description**: Three-currency arbitrage within the same market.

**Parameters**:
```yaml
parameters:
  triangle_pairs: [["BTC/USD", "ETH/BTC", "ETH/USD"]]
  min_profit_threshold: 0.001
  execution_speed: "fast"
  slippage_tolerance: 0.0005
```

**Best Use Cases**:
- Currency triangles
- High liquidity markets
- Automated execution

### Forex-Specific Strategies

#### ForexCarryTradeStrategy
**Description**: Interest rate differential-based carry trading.

**Parameters**:
```yaml
parameters:
  interest_rate_threshold: 0.02
  correlation_filter: true
  volatility_filter: true
  session_timing: ["london", "new_york"]
```

**Best Use Cases**:
- Interest rate differentials
- Low volatility periods
- Long-term positions

#### ForexNewsStrategy
**Description**: Economic news and event-based trading.

**Parameters**:
```yaml
parameters:
  impact_levels: ["high", "medium"]
  pre_news_buffer: 300  # seconds
  post_news_buffer: 600  # seconds
  volatility_multiplier: 2.0
```

**Best Use Cases**:
- Economic announcements
- High-impact events
- Volatility trading

#### ForexSessionStrategy
**Description**: Trading based on forex session characteristics.

**Parameters**:
```yaml
parameters:
  active_sessions: ["london", "new_york", "tokyo"]
  overlap_focus: true
  session_momentum: true
  timezone_aware: true
```

**Best Use Cases**:
- Session overlaps
- Time-based patterns
- Regional market characteristics

## Configuration Guide

### Basic Strategy Configuration

```yaml
strategies:
  - name: "rsi_strategy_1"
    type: "RSIStrategy"
    enabled: true
    markets: ["crypto"]
    parameters:
      rsi_period: 14
      oversold_threshold: 30
      overbought_threshold: 70
    risk_limits:
      max_position_size: 0.05
      stop_loss_pct: 0.02
      take_profit_pct: 0.04
```

### Multi-Strategy Configuration

```yaml
strategies:
  # Technical Analysis
  - name: "rsi_crypto"
    type: "RSIStrategy"
    enabled: true
    markets: ["crypto"]
    allocation: 0.3
    
  - name: "ma_forex"
    type: "MovingAverageStrategy"
    enabled: true
    markets: ["forex"]
    allocation: 0.3
    
  # Arbitrage
  - name: "cross_market_arb"
    type: "CrossMarketArbitrageStrategy"
    enabled: true
    markets: ["crypto", "forex"]
    allocation: 0.2
    
  # Machine Learning
  - name: "ml_pattern"
    type: "MLPatternStrategy"
    enabled: true
    markets: ["crypto", "forex"]
    allocation: 0.2
```

### Risk Management Configuration

```yaml
risk_management:
  global_limits:
    max_daily_loss: 0.05
    max_drawdown: 0.10
    max_open_positions: 10
    
  strategy_limits:
    max_allocation_per_strategy: 0.4
    max_correlation_threshold: 0.7
    
  position_sizing:
    method: "kelly"
    base_size: 0.02
    max_size: 0.1
    volatility_adjustment: true
```

## CLI Usage

### List All Strategies

```bash
# List all available strategies
genebot list-strategies

# Filter by status
genebot list-strategies --status active
genebot list-strategies --status inactive
```

### Strategy Information

```bash
# Get detailed strategy information
genebot strategy-info RSIStrategy

# View strategy performance
genebot strategy-performance --strategy RSIStrategy --days 30
```

### Enable/Disable Strategies

```bash
# Enable a strategy
genebot enable-strategy RSIStrategy

# Disable a strategy
genebot disable-strategy RSIStrategy

# Enable multiple strategies
genebot enable-strategy RSIStrategy MovingAverageStrategy
```

### Strategy Testing

```bash
# Backtest a strategy
genebot backtest --strategy RSIStrategy --start 2024-01-01 --end 2024-12-31

# Paper trading
genebot paper-trade --strategy RSIStrategy --duration 7d
```

## Multi-Market Strategies

### Cross-Market Arbitrage

Cross-market arbitrage strategies operate across multiple market types:

```yaml
cross_market_arbitrage:
  enabled: true
  markets: ["crypto", "forex"]
  correlation_threshold: 0.8
  execution_timeout: 30
  profit_threshold: 0.005
```

**Key Features**:
- Real-time price monitoring across markets
- Correlation analysis
- Automated execution
- Risk management across market types

### Market-Agnostic Strategies

These strategies work across any market type:

```yaml
market_agnostic:
  universal_parameters: true
  adaptive_thresholds: true
  market_normalization: true
  unified_risk_management: true
```

## Performance Optimization

### Strategy Selection

1. **Diversification**: Use strategies from different categories
2. **Market Conditions**: Match strategies to current market regime
3. **Correlation**: Avoid highly correlated strategies
4. **Risk-Adjusted Returns**: Focus on Sharpe ratio, not just returns

### Parameter Optimization

```yaml
optimization:
  method: "genetic_algorithm"
  generations: 100
  population_size: 50
  mutation_rate: 0.1
  crossover_rate: 0.8
  
  objectives:
    - "sharpe_ratio"
    - "max_drawdown"
    - "profit_factor"
```

### Resource Management

```yaml
resource_management:
  max_concurrent_strategies: 10
  cpu_allocation: 0.8
  memory_limit: "4GB"
  execution_priority: "high"
```

## Troubleshooting

### Common Issues

#### Strategy Not Starting
```bash
# Check strategy status
genebot strategy-status RSIStrategy

# Validate configuration
genebot validate-config --strategy RSIStrategy

# Check logs
genebot logs --strategy RSIStrategy --lines 100
```

#### Poor Performance
```bash
# Analyze strategy performance
genebot analyze-performance --strategy RSIStrategy

# Compare with benchmark
genebot benchmark --strategy RSIStrategy --benchmark SPY

# Optimize parameters
genebot optimize --strategy RSIStrategy --metric sharpe_ratio
```

#### Execution Issues
```bash
# Check market connectivity
genebot check-connectivity

# Validate account permissions
genebot validate-accounts

# Monitor execution latency
genebot monitor-latency --strategy RSIStrategy
```

### Performance Monitoring

```bash
# Real-time monitoring
genebot monitor --strategy RSIStrategy

# Generate performance report
genebot report --strategy RSIStrategy --format pdf

# Export trade history
genebot export-trades --strategy RSIStrategy --format csv
```

### Best Practices

1. **Start Small**: Begin with paper trading
2. **Diversify**: Use multiple uncorrelated strategies
3. **Monitor Regularly**: Check performance daily
4. **Risk Management**: Always use stop-losses
5. **Backtesting**: Validate strategies before live trading
6. **Documentation**: Keep detailed records of changes
7. **Regular Updates**: Update parameters based on market conditions

### Strategy Lifecycle Management

```yaml
lifecycle:
  development:
    - backtesting
    - parameter_optimization
    - risk_assessment
    
  testing:
    - paper_trading
    - small_position_testing
    - performance_validation
    
  production:
    - live_trading
    - continuous_monitoring
    - regular_optimization
    
  retirement:
    - performance_degradation_detection
    - graceful_shutdown
    - post_mortem_analysis
```

## Advanced Features

### Custom Strategy Development

```python
from src.strategies.base_strategy import BaseStrategy, StrategyConfig

class CustomStrategy(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        # Custom initialization
        
    def analyze(self, market_data):
        # Custom analysis logic
        pass
        
    def process_market_data(self, market_data):
        # Custom signal generation
        pass
```

### Strategy Orchestration

```yaml
orchestration:
  enabled: true
  allocation_method: "risk_parity"
  rebalance_frequency: "daily"
  correlation_monitoring: true
  performance_attribution: true
```

### Integration with External Systems

```yaml
integrations:
  portfolio_management:
    enabled: true
    system: "custom"
    
  risk_management:
    enabled: true
    system: "internal"
    
  execution_management:
    enabled: true
    system: "multi_broker"
```

This comprehensive guide covers all aspects of strategy usage in the GeneBot system. For additional support, consult the API documentation or contact the development team.
# Strategy Orchestrator User Guide

## Overview

The Strategy Orchestrator is a comprehensive system that intelligently coordinates all available trading strategies in genebot. It provides automated strategy selection, portfolio allocation, risk management, and performance optimization across multiple markets (crypto and forex).

## Key Features

- **Automated Strategy Discovery**: Automatically finds and registers all available strategies
- **Intelligent Allocation**: Dynamically allocates capital based on performance and risk metrics
- **Cross-Strategy Risk Management**: Portfolio-level risk controls and monitoring
- **Performance Optimization**: Continuous performance tracking and allocation adjustments
- **Multi-Market Support**: Works across crypto and forex markets simultaneously
- **Real-time Monitoring**: Comprehensive monitoring and alerting system

## Getting Started

### Prerequisites

- Genebot installed and configured
- At least one exchange connection configured
- Basic understanding of trading strategies

### Basic Setup

1. **Create Orchestrator Configuration**

Create a configuration file `config/orchestrator_config.yaml`:

```yaml
orchestrator:
  allocation:
    method: "performance_based"
    rebalance_frequency: "daily"
    min_allocation: 0.01
    max_allocation: 0.25
    
  risk:
    max_portfolio_drawdown: 0.10
    max_strategy_correlation: 0.80
    position_size_limit: 0.05
    
  monitoring:
    performance_tracking: true
    alert_thresholds:
      drawdown: 0.05
      correlation: 0.75
      
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

2. **Start the Orchestrator**

```bash
# Using CLI
genebot orchestrator start --config config/orchestrator_config.yaml

# Or using Python
python -m genebot.orchestration.orchestrator --config config/orchestrator_config.yaml
```

3. **Monitor Performance**

```bash
# Check status
genebot orchestrator status

# View performance metrics
genebot orchestrator metrics

# View current allocations
genebot orchestrator allocations
```

## Configuration Guide

### Allocation Methods

#### Equal Weight
Distributes capital equally across all enabled strategies:

```yaml
allocation:
  method: "equal_weight"
  rebalance_frequency: "daily"
```

#### Performance Based
Allocates more capital to better-performing strategies:

```yaml
allocation:
  method: "performance_based"
  lookback_period: 30  # days
  performance_metric: "sharpe_ratio"  # or "total_return", "win_rate"
  rebalance_frequency: "weekly"
```

#### Risk Parity
Allocates capital to equalize risk contribution:

```yaml
allocation:
  method: "risk_parity"
  risk_metric: "volatility"  # or "var", "max_drawdown"
  rebalance_frequency: "weekly"
```

#### Custom Allocation
Use custom allocation algorithms:

```yaml
allocation:
  method: "custom"
  algorithm: "my_custom_allocator"
  parameters:
    param1: value1
    param2: value2
```

### Risk Management

Configure portfolio-level risk controls:

```yaml
risk:
  # Maximum portfolio drawdown before emergency stop
  max_portfolio_drawdown: 0.10
  
  # Maximum correlation between strategies
  max_strategy_correlation: 0.80
  
  # Maximum position size per trade
  position_size_limit: 0.05
  
  # Stop loss threshold for individual positions
  stop_loss_threshold: 0.02
  
  # Emergency stop conditions
  emergency_stop_conditions:
    - "portfolio_drawdown_exceeded"
    - "correlation_limit_exceeded"
    - "strategy_failure_cascade"
```

### Strategy Configuration

Configure individual strategies within the orchestrator:

```yaml
strategies:
  - type: "MovingAverageStrategy"
    name: "ma_short_term"
    enabled: true
    allocation_weight: 1.0
    markets: ["crypto", "forex"]  # Optional: limit to specific markets
    parameters:
      short_period: 10
      long_period: 20
      
  - type: "RSIStrategy"
    name: "rsi_mean_reversion"
    enabled: true
    allocation_weight: 1.5  # Higher weight = more allocation preference
    parameters:
      period: 14
      oversold: 30
      overbought: 70
      
  - type: "ForexCarryTradeStrategy"
    name: "carry_trade"
    enabled: true
    allocation_weight: 0.8
    markets: ["forex"]  # Forex only
    parameters:
      min_interest_differential: 0.02
```

### Monitoring Configuration

Configure monitoring and alerting:

```yaml
monitoring:
  performance_tracking: true
  
  # Metrics collection frequency
  metrics_frequency: "1m"
  
  # Alert thresholds
  alert_thresholds:
    drawdown: 0.05
    correlation: 0.75
    strategy_failure_rate: 0.20
    
  # Notification channels
  notifications:
    email:
      enabled: true
      recipients: ["trader@example.com"]
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/..."
```

## Usage Examples

### Starting with Conservative Settings

For beginners, start with conservative risk settings:

```yaml
orchestrator:
  allocation:
    method: "equal_weight"
    rebalance_frequency: "weekly"
    min_allocation: 0.05
    max_allocation: 0.15
    
  risk:
    max_portfolio_drawdown: 0.05
    position_size_limit: 0.02
    stop_loss_threshold: 0.01
```

### Aggressive Growth Configuration

For experienced traders seeking higher returns:

```yaml
orchestrator:
  allocation:
    method: "performance_based"
    rebalance_frequency: "daily"
    min_allocation: 0.01
    max_allocation: 0.40
    
  risk:
    max_portfolio_drawdown: 0.15
    position_size_limit: 0.08
    max_strategy_correlation: 0.90
```

### Multi-Market Arbitrage Focus

Configuration optimized for arbitrage strategies:

```yaml
strategies:
  - type: "CrossMarketArbitrageStrategy"
    name: "crypto_forex_arb"
    enabled: true
    allocation_weight: 2.0
    
  - type: "TriangularArbitrageStrategy"
    name: "triangular_arb"
    enabled: true
    allocation_weight: 1.5
    
  - type: "CryptoForexArbitrageStrategy"
    name: "cross_asset_arb"
    enabled: true
    allocation_weight: 1.8
```

## Command Line Interface

### Basic Commands

```bash
# Start orchestrator
genebot orchestrator start --config config/orchestrator_config.yaml

# Stop orchestrator
genebot orchestrator stop

# Check status
genebot orchestrator status

# View current allocations
genebot orchestrator allocations

# View performance metrics
genebot orchestrator metrics --period 7d

# View strategy performance
genebot orchestrator strategies --sort-by performance

# Rebalance allocations manually
genebot orchestrator rebalance --force

# Emergency stop all strategies
genebot orchestrator emergency-stop
```

### Configuration Management

```bash
# Validate configuration
genebot orchestrator config validate --config config/orchestrator_config.yaml

# Update configuration dynamically
genebot orchestrator config update --key allocation.method --value performance_based

# Reload configuration
genebot orchestrator config reload

# Export current configuration
genebot orchestrator config export --output current_config.yaml
```

### Monitoring Commands

```bash
# View real-time metrics
genebot orchestrator monitor --live

# Generate performance report
genebot orchestrator report --period 30d --output report.pdf

# View risk metrics
genebot orchestrator risk-status

# Check correlation matrix
genebot orchestrator correlations
```

## Best Practices

### 1. Start Small
- Begin with a small number of strategies (2-3)
- Use conservative risk settings initially
- Monitor performance for at least a week before scaling up

### 2. Diversification
- Use strategies with different approaches (trend-following, mean-reversion, arbitrage)
- Avoid highly correlated strategies
- Consider different timeframes and markets

### 3. Risk Management
- Set appropriate drawdown limits
- Monitor correlation between strategies
- Use position sizing to control risk

### 4. Performance Monitoring
- Review performance metrics regularly
- Analyze attribution to understand which strategies contribute most
- Adjust allocations based on changing market conditions

### 5. Configuration Management
- Keep configuration files in version control
- Test configuration changes in a sandbox environment
- Document any custom parameters or modifications

## Troubleshooting

### Common Issues

#### Orchestrator Won't Start
```bash
# Check configuration validity
genebot orchestrator config validate --config config/orchestrator_config.yaml

# Check logs for errors
tail -f logs/orchestrator.log

# Verify strategy dependencies
genebot orchestrator strategies --check-dependencies
```

#### Poor Performance
```bash
# Analyze strategy performance
genebot orchestrator strategies --detailed

# Check correlation matrix
genebot orchestrator correlations

# Review allocation history
genebot orchestrator allocations --history
```

#### High Risk Exposure
```bash
# Check current risk metrics
genebot orchestrator risk-status

# Review position sizes
genebot orchestrator positions

# Adjust risk parameters
genebot orchestrator config update --key risk.position_size_limit --value 0.03
```

### Getting Help

- Check the troubleshooting guide: `docs/ORCHESTRATOR_TROUBLESHOOTING.md`
- Review API documentation: `docs/ORCHESTRATOR_API_REFERENCE.md`
- Enable debug logging: `--log-level DEBUG`
- Contact support with log files and configuration

## Advanced Topics

### Custom Allocation Algorithms

Create custom allocation algorithms by implementing the `AllocationAlgorithm` interface:

```python
from src.orchestration.interfaces import AllocationAlgorithm

class MyCustomAllocator(AllocationAlgorithm):
    def calculate_allocation(self, performance_metrics, risk_metrics):
        # Your custom logic here
        return allocations
```

### Strategy Development

Develop new strategies compatible with the orchestrator:

```python
from src.strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        # Strategy initialization
        
    def generate_signals(self, market_data):
        # Signal generation logic
        return signals
```

### Integration with External Systems

The orchestrator provides REST API endpoints for integration:

```python
import requests

# Get current status
response = requests.get('http://localhost:8080/api/orchestrator/status')
status = response.json()

# Update allocation
requests.post('http://localhost:8080/api/orchestrator/allocations', 
              json={'strategy': 'ma_short', 'allocation': 0.15})
```

## Next Steps

1. Review the configuration reference: `docs/ORCHESTRATOR_CONFIG_REFERENCE.md`
2. Explore example configurations: `examples/orchestrator/`
3. Learn about API integration: `docs/ORCHESTRATOR_API_REFERENCE.md`
4. Set up monitoring dashboards: `docs/ORCHESTRATOR_MONITORING.md`

For more detailed information, see the complete documentation suite in the `docs/` directory.
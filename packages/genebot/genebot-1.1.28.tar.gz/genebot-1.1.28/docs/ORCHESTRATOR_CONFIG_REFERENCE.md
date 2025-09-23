# Strategy Orchestrator Configuration Reference

## Overview

This document provides a comprehensive reference for all configuration options available in the Strategy Orchestrator system. The configuration is structured in YAML format and supports dynamic updates for most parameters.

## Configuration Structure

```yaml
orchestrator:
  allocation:
    # Allocation management settings
  risk:
    # Risk management settings
  monitoring:
    # Monitoring and alerting settings
  strategies:
    # Individual strategy configurations
  optimization:
    # Performance optimization settings
  logging:
    # Logging configuration
  api:
    # API server settings
```

## Allocation Configuration

### Basic Settings

```yaml
allocation:
  # Allocation method: equal_weight, performance_based, risk_parity, custom
  method: "performance_based"
  
  # Rebalancing frequency: daily, weekly, monthly, custom
  rebalance_frequency: "daily"
  
  # Minimum allocation per strategy (0.0 - 1.0)
  min_allocation: 0.01
  
  # Maximum allocation per strategy (0.0 - 1.0)
  max_allocation: 0.25
  
  # Allocation constraints per strategy type
  allocation_constraints:
    MovingAverageStrategy:
      min: 0.05
      max: 0.20
    RSIStrategy:
      min: 0.02
      max: 0.15
```

### Performance-Based Allocation

```yaml
allocation:
  method: "performance_based"
  
  # Performance-based specific settings
  performance_based:
    # Lookback period for performance calculation (days)
    lookback_period: 30
    
    # Performance metric: sharpe_ratio, total_return, win_rate, profit_factor
    performance_metric: "sharpe_ratio"
    
    # Minimum performance threshold for allocation
    min_performance_threshold: 0.0
    
    # Performance decay factor (0.0 - 1.0)
    decay_factor: 0.95
    
    # Smoothing factor for allocation changes (0.0 - 1.0)
    smoothing_factor: 0.8
```

### Risk Parity Allocation

```yaml
allocation:
  method: "risk_parity"
  
  # Risk parity specific settings
  risk_parity:
    # Risk metric: volatility, var, max_drawdown, beta
    risk_metric: "volatility"
    
    # Lookback period for risk calculation (days)
    lookback_period: 60
    
    # Target risk contribution per strategy
    target_risk_contribution: "equal"  # or "custom"
    
    # Custom risk contributions (if target_risk_contribution: custom)
    custom_risk_contributions:
      MovingAverageStrategy: 0.3
      RSIStrategy: 0.2
      ArbitrageStrategy: 0.5
```

### Custom Allocation

```yaml
allocation:
  method: "custom"
  
  # Custom allocation settings
  custom:
    # Custom algorithm class name
    algorithm: "MyCustomAllocator"
    
    # Algorithm-specific parameters
    parameters:
      param1: value1
      param2: value2
      
    # Module path for custom algorithm
    module_path: "custom.allocators"
```

## Risk Management Configuration

### Portfolio Risk Limits

```yaml
risk:
  # Maximum portfolio drawdown before emergency stop (0.0 - 1.0)
  max_portfolio_drawdown: 0.10
  
  # Maximum correlation between strategies (0.0 - 1.0)
  max_strategy_correlation: 0.80
  
  # Maximum position size per trade (0.0 - 1.0)
  position_size_limit: 0.05
  
  # Stop loss threshold for individual positions (0.0 - 1.0)
  stop_loss_threshold: 0.02
  
  # Maximum number of concurrent positions
  max_concurrent_positions: 10
  
  # Maximum exposure per market (0.0 - 1.0)
  max_market_exposure:
    crypto: 0.60
    forex: 0.40
```

### Risk Monitoring

```yaml
risk:
  # Risk monitoring settings
  monitoring:
    # Correlation calculation period (days)
    correlation_period: 30
    
    # Drawdown calculation method: peak_to_trough, rolling_window
    drawdown_method: "peak_to_trough"
    
    # Risk metrics update frequency (seconds)
    update_frequency: 60
    
    # Enable real-time risk monitoring
    real_time_monitoring: true
```

### Emergency Stop Conditions

```yaml
risk:
  # Emergency stop conditions
  emergency_stop_conditions:
    - "portfolio_drawdown_exceeded"
    - "correlation_limit_exceeded"
    - "strategy_failure_cascade"
    - "market_volatility_spike"
    
  # Emergency stop settings
  emergency_stop:
    # Automatic recovery after emergency stop
    auto_recovery: false
    
    # Recovery delay (minutes)
    recovery_delay: 30
    
    # Recovery conditions
    recovery_conditions:
      - "drawdown_below_threshold"
      - "manual_approval"
```

## Strategy Configuration

### Individual Strategy Settings

```yaml
strategies:
  - type: "MovingAverageStrategy"
    name: "ma_short_term"
    enabled: true
    
    # Allocation weight (relative to other strategies)
    allocation_weight: 1.0
    
    # Markets this strategy can trade
    markets: ["crypto", "forex"]
    
    # Strategy-specific parameters
    parameters:
      short_period: 10
      long_period: 20
      signal_threshold: 0.01
      
    # Strategy-specific risk limits
    risk_limits:
      max_position_size: 0.03
      stop_loss: 0.015
      take_profit: 0.025
      
    # Performance requirements
    performance_requirements:
      min_sharpe_ratio: 0.5
      min_win_rate: 0.45
      max_drawdown: 0.08
```

### Strategy Groups

```yaml
strategy_groups:
  trend_following:
    strategies:
      - "ma_short_term"
      - "momentum_strategy"
    max_group_allocation: 0.40
    
  mean_reversion:
    strategies:
      - "rsi_strategy"
      - "bollinger_bands"
    max_group_allocation: 0.30
    
  arbitrage:
    strategies:
      - "cross_market_arb"
      - "triangular_arb"
    max_group_allocation: 0.30
```

## Monitoring Configuration

### Performance Monitoring

```yaml
monitoring:
  # Enable performance tracking
  performance_tracking: true
  
  # Metrics collection frequency
  metrics_frequency: "1m"  # 1m, 5m, 15m, 1h
  
  # Performance metrics to track
  tracked_metrics:
    - "total_return"
    - "sharpe_ratio"
    - "max_drawdown"
    - "win_rate"
    - "profit_factor"
    - "volatility"
    
  # Historical data retention (days)
  data_retention: 365
```

### Alert Configuration

```yaml
monitoring:
  # Alert thresholds
  alert_thresholds:
    # Portfolio drawdown alert threshold
    drawdown: 0.05
    
    # Strategy correlation alert threshold
    correlation: 0.75
    
    # Strategy failure rate alert threshold
    strategy_failure_rate: 0.20
    
    # Performance degradation threshold
    performance_degradation: 0.30
    
    # Position size alert threshold
    position_size: 0.08
```

### Notification Channels

```yaml
monitoring:
  notifications:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "alerts@example.com"
      password: "${EMAIL_PASSWORD}"
      recipients:
        - "trader@example.com"
        - "risk@example.com"
        
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channel: "#trading-alerts"
      
    discord:
      enabled: false
      webhook_url: "${DISCORD_WEBHOOK_URL}"
      
    webhook:
      enabled: true
      url: "https://api.example.com/alerts"
      headers:
        Authorization: "Bearer ${API_TOKEN}"
```

## Optimization Configuration

### Performance Optimization

```yaml
optimization:
  # Optimization frequency: daily, weekly, monthly
  optimization_frequency: "weekly"
  
  # Lookback period for optimization (days)
  lookback_period: 30
  
  # Optimization method: sharpe_ratio, total_return, risk_adjusted_return
  optimization_method: "sharpe_ratio"
  
  # Minimum performance threshold for strategy inclusion
  min_performance_threshold: 0.0
  
  # Strategy selection criteria
  selection_criteria:
    min_trades: 10
    min_win_rate: 0.40
    max_drawdown: 0.15
```

### Parameter Optimization

```yaml
optimization:
  parameter_optimization:
    # Enable parameter optimization
    enabled: true
    
    # Optimization algorithm: genetic, grid_search, bayesian
    algorithm: "bayesian"
    
    # Optimization frequency
    frequency: "monthly"
    
    # Parameters to optimize
    parameters:
      MovingAverageStrategy:
        short_period: [5, 10, 15, 20]
        long_period: [20, 30, 40, 50]
      RSIStrategy:
        period: [10, 14, 18, 22]
        oversold: [25, 30, 35]
        overbought: [65, 70, 75]
```

## Logging Configuration

```yaml
logging:
  # Log level: DEBUG, INFO, WARNING, ERROR
  level: "INFO"
  
  # Log format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # Log file settings
  file:
    enabled: true
    path: "logs/orchestrator.log"
    max_size: "100MB"
    backup_count: 5
    
  # Console logging
  console:
    enabled: true
    level: "INFO"
    
  # Structured logging
  structured:
    enabled: true
    format: "json"
    
  # Audit logging
  audit:
    enabled: true
    path: "logs/orchestrator_audit.log"
    include_decisions: true
    include_allocations: true
    include_risk_events: true
```

## API Configuration

```yaml
api:
  # Enable REST API server
  enabled: true
  
  # API server host and port
  host: "0.0.0.0"
  port: 8080
  
  # API authentication
  authentication:
    enabled: true
    method: "bearer_token"  # bearer_token, api_key, basic_auth
    token: "${API_TOKEN}"
    
  # CORS settings
  cors:
    enabled: true
    origins: ["http://localhost:3000"]
    
  # Rate limiting
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    
  # API documentation
  docs:
    enabled: true
    path: "/docs"
```

## Environment Variables

The configuration supports environment variable substitution using `${VARIABLE_NAME}` syntax:

```yaml
# Example environment variables
EMAIL_PASSWORD: "your_email_password"
SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/..."
API_TOKEN: "your_api_token"
DATABASE_URL: "postgresql://user:pass@localhost/db"
```

## Configuration Validation

### Schema Validation

The orchestrator validates configuration against a JSON schema. Common validation errors:

- Invalid allocation method
- Risk limits outside valid ranges (0.0 - 1.0)
- Missing required strategy parameters
- Invalid frequency specifications
- Malformed notification settings

### Runtime Validation

Additional validation occurs at runtime:

- Strategy class availability
- Exchange connectivity
- Market data availability
- Performance metric calculations

## Dynamic Configuration Updates

Most configuration parameters can be updated without restarting the orchestrator:

```bash
# Update allocation method
genebot orchestrator config update --key allocation.method --value risk_parity

# Update risk limit
genebot orchestrator config update --key risk.max_portfolio_drawdown --value 0.08

# Enable/disable strategy
genebot orchestrator config update --key strategies.ma_short_term.enabled --value false

# Reload entire configuration
genebot orchestrator config reload --config new_config.yaml
```

## Configuration Templates

### Conservative Template

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

### Aggressive Template

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

### Arbitrage-Focused Template

```yaml
orchestrator:
  allocation:
    method: "risk_parity"
    rebalance_frequency: "daily"
  strategies:
    - type: "CrossMarketArbitrageStrategy"
      allocation_weight: 2.0
    - type: "TriangularArbitrageStrategy"
      allocation_weight: 1.5
```

## Best Practices

1. **Start with Templates**: Use provided templates as starting points
2. **Validate Configuration**: Always validate before deploying
3. **Use Environment Variables**: Keep sensitive data in environment variables
4. **Monitor Changes**: Track configuration changes in version control
5. **Test in Sandbox**: Test configuration changes in a sandbox environment
6. **Document Customizations**: Document any custom parameters or modifications

## Troubleshooting

### Common Configuration Issues

1. **Invalid YAML Syntax**: Use a YAML validator
2. **Missing Environment Variables**: Check all `${VARIABLE}` references
3. **Invalid Parameter Ranges**: Ensure values are within valid ranges
4. **Strategy Not Found**: Verify strategy class names and availability
5. **Network Configuration**: Check API host/port settings

### Configuration Debugging

```bash
# Validate configuration
genebot orchestrator config validate --config config.yaml --verbose

# Show resolved configuration (with environment variables)
genebot orchestrator config show --resolved

# Test configuration without starting
genebot orchestrator config test --config config.yaml
```

For more information, see the troubleshooting guide: `docs/ORCHESTRATOR_TROUBLESHOOTING.md`
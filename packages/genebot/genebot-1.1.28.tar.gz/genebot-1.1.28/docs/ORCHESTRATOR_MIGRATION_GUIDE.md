# Orchestrator Migration Guide

## Overview

This comprehensive guide helps you migrate your existing genebot setup to use the unified strategy orchestration system. The orchestrator provides intelligent strategy coordination, automatic allocation management, and advanced risk controls across your entire portfolio.

## Benefits of Migration

### Performance Benefits
- **Intelligent Allocation**: Automatically allocate capital across strategies based on performance
- **Risk-Adjusted Returns**: Use Sharpe ratio and other metrics for optimal allocation
- **Dynamic Rebalancing**: Continuously optimize strategy weights based on market conditions
- **Performance Attribution**: Understand which strategies contribute most to returns

### Risk Management Benefits
- **Portfolio-Level Controls**: Risk management across all strategies, not just individual ones
- **Correlation Monitoring**: Prevent over-concentration in correlated strategies
- **Emergency Procedures**: Automatic emergency stops and risk limit enforcement
- **Drawdown Protection**: Portfolio-wide drawdown limits and monitoring

### Operational Benefits
- **Unified Monitoring**: Single dashboard for all strategies and performance metrics
- **Automated Management**: Reduce manual intervention and optimization tasks
- **Comprehensive Logging**: Detailed audit trails for all orchestration decisions
- **API Access**: Programmatic access to orchestrator metrics and controls

## Pre-Migration Assessment

### 1. Analyze Current Setup

Run the analysis tool to understand your current configuration:

```bash
genebot orchestrator-migrate analyze
```

This will show:
- Current strategies and their configuration
- Exchange setup and connectivity
- Risk management settings
- Migration recommendations and warnings

### 2. Review Migration Readiness

**Migration is recommended if you have:**
- Multiple trading strategies configured
- Multiple exchanges or markets
- Complex risk management requirements
- Need for performance optimization
- Desire for unified monitoring

**Migration may not be needed if you have:**
- Single strategy with simple requirements
- Very specific custom strategy logic
- Extremely low-latency requirements
- Regulatory constraints requiring isolated strategies

### 3. Plan Migration Timeline

**Recommended timeline:**
- **Week 1**: Analysis and planning
- **Week 2**: Configuration generation and testing
- **Week 3**: Dry-run testing and validation
- **Week 4**: Production migration and monitoring

## Migration Process

### Step 1: Backup Current Configuration

Create a complete backup of your existing setup:

```bash
# Create timestamped backup
genebot orchestrator-migrate backup

# Manual backup (alternative)
genebot config-backup --file all
```

The backup includes:
- All configuration files
- Environment variables
- Account configurations
- Strategy parameters
- Risk settings

### Step 2: Generate Orchestrator Configuration

Generate an orchestrator configuration based on your existing setup:

```bash
# Basic generation with performance-based allocation
genebot orchestrator-migrate generate

# Advanced generation with custom parameters
genebot orchestrator-migrate generate \
  --allocation-method risk_parity \
  --rebalance-frequency weekly \
  --max-drawdown 0.08 \
  --output config/orchestrator_config.yaml
```

**Allocation Methods:**
- `equal_weight`: Equal allocation across all strategies
- `performance_based`: Allocation based on risk-adjusted returns (recommended)
- `risk_parity`: Allocation based on risk contribution

### Step 3: Review and Customize Configuration

Edit the generated configuration to match your specific needs:

```yaml
orchestrator:
  allocation:
    method: "performance_based"
    rebalance_frequency: "daily"
    min_allocation: 0.01  # Minimum 1% per strategy
    max_allocation: 0.25  # Maximum 25% per strategy
    allocation_constraints:
      # Custom constraints per strategy
      high_risk_strategies: 0.15  # Max 15% for high-risk strategies
  
  risk:
    max_portfolio_drawdown: 0.10
    max_strategy_correlation: 0.80
    position_size_limit: 0.05
    stop_loss_threshold: 0.02
    emergency_stop_conditions:
      - "max_drawdown_exceeded"
      - "correlation_too_high"
      - "strategy_failure_cascade"
  
  monitoring:
    performance_tracking: true
    alert_thresholds:
      drawdown: 0.05  # Alert at 5% drawdown
      correlation: 0.75  # Alert when correlation exceeds 75%
      underperformance: -0.10  # Alert on 10% underperformance
    notification_channels: ["console", "email"]
  
  strategies:
    - type: "MovingAverageStrategy"
      name: "ma_short"
      enabled: true
      allocation_weight: 1.0
      parameters:
        short_period: 10
        long_period: 20
      symbols: ["BTC/USDT", "ETH/USDT"]
      timeframe: "1h"
    
    - type: "RSIStrategy"
      name: "rsi_oversold"
      enabled: true
      allocation_weight: 1.0
      parameters:
        period: 14
        oversold: 30
        overbought: 70
      symbols: ["BTC/USDT", "ETH/USDT"]
      timeframe: "4h"
```

### Step 4: Validate Configuration

Validate the generated configuration:

```bash
# Validate orchestrator configuration
genebot orchestrator-config validate --config config/orchestrator_config.yaml

# Check for common issues
genebot orchestrator-migrate validate config/orchestrator_config.yaml
```

Common validation issues:
- Missing required strategy parameters
- Invalid allocation constraints
- Incompatible risk settings
- Strategy type mismatches

### Step 5: Dry-Run Testing

Test the orchestrator configuration without live trading:

```bash
# Start orchestrator in dry-run mode
genebot orchestrator-start \
  --config config/orchestrator_config.yaml \
  --daemon \
  --dry-run

# Monitor dry-run performance
genebot orchestrator-monitor --hours 24

# Check strategy allocation
genebot orchestrator-status --verbose
```

**Dry-run testing checklist:**
- [ ] All strategies load correctly
- [ ] Allocation weights are reasonable
- [ ] Risk limits are enforced
- [ ] Monitoring data is collected
- [ ] No critical errors in logs

### Step 6: Production Migration

Perform the complete migration:

```bash
# Stop existing bot
genebot stop

# Perform migration (includes backup)
genebot orchestrator-migrate migrate \
  --allocation-method performance_based \
  --rebalance-frequency daily \
  --max-drawdown 0.10

# Start orchestrator
genebot orchestrator-start --daemon

# Verify operation
genebot orchestrator-status
```

### Step 7: Post-Migration Monitoring

Monitor the orchestrator closely after migration:

```bash
# Real-time monitoring
genebot orchestrator-monitor --refresh 30

# Daily status checks
genebot orchestrator-status --verbose

# Weekly performance review
genebot orchestrator-monitor --hours 168 --format json > weekly_report.json
```

## Configuration Mapping

### Strategy Migration

| Original Config | Orchestrator Config | Notes |
|----------------|-------------------|-------|
| `strategies.moving_average` | `orchestrator.strategies[].type: "MovingAverageStrategy"` | Type name standardized |
| `strategies.*.enabled` | `orchestrator.strategies[].enabled` | Direct mapping |
| `strategies.*.parameters` | `orchestrator.strategies[].parameters` | Direct mapping |
| `strategies.*.symbols` | `orchestrator.strategies[].symbols` | Direct mapping |
| `strategies.*.max_positions` | Handled by orchestrator allocation | Replaced by allocation system |

### Risk Management Migration

| Original Config | Orchestrator Config | Notes |
|----------------|-------------------|-------|
| `risk.max_position_size` | `orchestrator.risk.position_size_limit` | Portfolio-level limit |
| `risk.max_drawdown` | `orchestrator.risk.max_portfolio_drawdown` | Portfolio-level drawdown |
| `risk.stop_loss_percentage` | `orchestrator.risk.stop_loss_threshold` | Applied across strategies |
| `risk.max_open_positions` | Managed by allocation system | Dynamic based on allocation |

### Exchange Configuration

Exchange configurations remain unchanged and are used by all strategies in the orchestrator.

## Advanced Migration Scenarios

### Scenario 1: Multiple Bot Instances

If you're running multiple bot instances:

```bash
# Migrate each instance separately
for instance in bot1 bot2 bot3; do
  genebot orchestrator-migrate analyze --config config/${instance}_config.yaml
  genebot orchestrator-migrate generate --config config/${instance}_config.yaml --output config/orchestrator_${instance}.yaml
done

# Or combine into single orchestrator
genebot orchestrator-migrate merge-configs \
  config/bot1_config.yaml \
  config/bot2_config.yaml \
  config/bot3_config.yaml \
  --output config/unified_orchestrator.yaml
```

### Scenario 2: Custom Strategy Classes

For custom strategy implementations:

```python
# Ensure your custom strategies inherit from BaseStrategy
from src.strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        # Your initialization code
    
    def generate_signals(self, market_data):
        # Your signal generation logic
        pass
    
    # Implement required methods
    def get_strategy_info(self):
        return {
            'name': 'MyCustomStrategy',
            'version': '1.0.0',
            'description': 'My custom trading strategy'
        }
```

Update orchestrator configuration:

```yaml
orchestrator:
  strategies:
    - type: "MyCustomStrategy"
      name: "my_custom"
      enabled: true
      allocation_weight: 1.0
      parameters:
        # Your custom parameters
        custom_param1: value1
        custom_param2: value2
```

### Scenario 3: Gradual Migration

For gradual migration with minimal disruption:

```bash
# Phase 1: Run orchestrator alongside existing bot
genebot start --config config/original_config.yaml &
genebot orchestrator-start --config config/orchestrator_config.yaml --daemon

# Phase 2: Gradually move strategies to orchestrator
genebot orchestrator-config update --enable-strategy ma_short
genebot config update --disable-strategy moving_average

# Phase 3: Complete migration
genebot stop  # Stop original bot
# Orchestrator continues running
```

## Troubleshooting Migration Issues

### Common Issues and Solutions

#### 1. Strategy Loading Errors

**Problem**: Strategies fail to load in orchestrator

**Solution**:
```bash
# Check strategy registry
genebot list-strategies

# Verify strategy class names
genebot orchestrator-config validate --verbose

# Check import paths
python -c "from src.strategies.moving_average_strategy import MovingAverageStrategy; print('OK')"
```

#### 2. Allocation Issues

**Problem**: Strategies not receiving expected allocation

**Solution**:
```bash
# Check allocation constraints
genebot orchestrator-status --verbose

# Review allocation method
genebot orchestrator-config show | grep -A 5 allocation

# Force rebalancing
genebot orchestrator-intervention force_rebalance
```

#### 3. Performance Degradation

**Problem**: Performance worse than individual strategies

**Solution**:
```bash
# Analyze performance attribution
genebot orchestrator-monitor --hours 168

# Check strategy correlations
genebot orchestrator-status --verbose | grep correlation

# Adjust allocation method
genebot orchestrator-config update --allocation-method equal_weight
```

#### 4. Risk Limit Violations

**Problem**: Risk limits too restrictive or not working

**Solution**:
```bash
# Review current risk settings
genebot orchestrator-config show | grep -A 10 risk

# Adjust risk limits
genebot orchestrator-config update --max-drawdown 0.15

# Check risk violation logs
tail -f logs/orchestrator.log | grep -i risk
```

### Recovery Procedures

#### Rollback to Original Configuration

If migration fails or performance is unsatisfactory:

```bash
# Stop orchestrator
genebot orchestrator-stop

# Restore original configuration
genebot config-restore --timestamp <backup_timestamp>

# Start original bot
genebot start
```

#### Partial Rollback

Keep some strategies in orchestrator, others in original bot:

```bash
# Disable problematic strategies in orchestrator
genebot orchestrator-config update --disable-strategy problematic_strategy

# Enable them in original configuration
genebot config update --enable-strategy problematic_strategy

# Run both systems
genebot start --strategies problematic_strategy &
genebot orchestrator-start --daemon
```

## Post-Migration Optimization

### Performance Tuning

#### 1. Allocation Optimization

```bash
# Monitor allocation effectiveness
genebot orchestrator-monitor --hours 168 --format json | jq '.allocation_metrics'

# Experiment with different methods
genebot orchestrator-config update --allocation-method risk_parity
# Monitor for 1-2 weeks, then compare

# Fine-tune allocation constraints
genebot orchestrator-config update --min-allocation 0.02 --max-allocation 0.20
```

#### 2. Risk Management Tuning

```bash
# Analyze risk metrics
genebot orchestrator-status --verbose | grep -A 20 "risk_metrics"

# Adjust based on performance
genebot orchestrator-config update --max-drawdown 0.12  # If too conservative
genebot orchestrator-config update --max-correlation 0.75  # If too restrictive
```

#### 3. Rebalancing Frequency

```bash
# Test different frequencies
genebot orchestrator-config update --rebalance-frequency weekly
# Monitor for impact on performance and transaction costs

# Daily for volatile markets, weekly for stable markets
```

### Monitoring Setup

#### 1. Automated Monitoring

```bash
# Set up cron job for daily reports
echo "0 9 * * * genebot orchestrator-monitor --hours 24 --format json > /var/log/orchestrator/daily_$(date +\%Y\%m\%d).json" | crontab -
```

#### 2. Alert Configuration

```yaml
orchestrator:
  monitoring:
    alert_thresholds:
      drawdown: 0.03  # Alert at 3% drawdown
      correlation: 0.70  # Alert when correlation exceeds 70%
      underperformance: -0.05  # Alert on 5% underperformance
    notification_channels: ["email", "slack"]
```

#### 3. Performance Dashboards

Set up Grafana dashboards for orchestrator metrics:

```bash
# Import orchestrator dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @deployment/grafana/dashboards/orchestrator-overview.json
```

## Best Practices

### 1. Strategy Selection
- Include strategies with different market condition preferences
- Ensure low correlation between strategies
- Mix trend-following and mean-reversion approaches
- Test strategies individually before orchestration

### 2. Risk Management
- Start with conservative drawdown limits
- Monitor strategy correlations regularly
- Use position size limits to prevent concentration
- Implement multiple emergency stop conditions

### 3. Performance Monitoring
- Allow 30+ days for meaningful performance evaluation
- Compare orchestrator performance to individual strategies
- Monitor allocation changes and their impact
- Keep detailed logs for analysis

### 4. Configuration Management
- Version control all configuration changes
- Test configuration changes in dry-run mode
- Document the reasoning behind parameter choices
- Regular backup of configurations and performance data

## Support and Resources

### Documentation
- [Orchestrator User Guide](ORCHESTRATOR_USER_GUIDE.md)
- [Orchestrator API Reference](ORCHESTRATOR_API_REFERENCE.md)
- [Orchestrator Configuration Reference](ORCHESTRATOR_CONFIG_REFERENCE.md)
- [Troubleshooting Guide](ORCHESTRATOR_TROUBLESHOOTING.md)

### Command Reference
```bash
# Migration commands
genebot orchestrator-migrate --help

# Configuration commands
genebot orchestrator-config --help

# Monitoring commands
genebot orchestrator-monitor --help

# Control commands
genebot orchestrator-start --help
genebot orchestrator-stop --help
genebot orchestrator-status --help
```

### Getting Help

1. **Check logs**: `tail -f logs/orchestrator.log`
2. **Validate configuration**: `genebot orchestrator-config validate`
3. **Review status**: `genebot orchestrator-status --verbose`
4. **Check documentation**: Review relevant guide sections
5. **Community support**: Check GitHub issues and discussions

## Migration Checklist

### Pre-Migration
- [ ] Current setup analyzed and documented
- [ ] Migration timeline planned
- [ ] Backup created and verified
- [ ] Orchestrator configuration generated
- [ ] Configuration validated and customized
- [ ] Dry-run testing completed successfully

### Migration
- [ ] Original bot stopped gracefully
- [ ] Orchestrator started with correct configuration
- [ ] All strategies loaded successfully
- [ ] Initial allocation applied correctly
- [ ] Monitoring systems active

### Post-Migration
- [ ] Performance monitoring active
- [ ] Daily status checks scheduled
- [ ] Alert thresholds configured
- [ ] Documentation updated
- [ ] Team trained on new commands
- [ ] Rollback procedure tested

### Ongoing
- [ ] Weekly performance reviews
- [ ] Monthly configuration optimization
- [ ] Quarterly strategy evaluation
- [ ] Regular backup verification
- [ ] Continuous monitoring of correlations and risk metrics

---

*This migration guide is designed to ensure a smooth transition to the orchestrator system. Take your time with each step and don't hesitate to rollback if issues arise. The orchestrator is designed to improve performance and reduce risk, but proper migration and monitoring are essential for success.*
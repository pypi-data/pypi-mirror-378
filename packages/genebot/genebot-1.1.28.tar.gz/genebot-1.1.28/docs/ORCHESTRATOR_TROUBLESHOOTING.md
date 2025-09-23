# Strategy Orchestrator Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when using the Strategy Orchestrator. It covers startup problems, performance issues, configuration errors, and operational challenges.

## Quick Diagnostics

### Health Check Commands

```bash
# Check orchestrator status
genebot orchestrator status

# Validate configuration
genebot orchestrator config validate --config config/orchestrator_config.yaml

# Check strategy dependencies
genebot orchestrator strategies --check-dependencies

# View recent logs
tail -f logs/orchestrator.log

# Run system diagnostics
genebot orchestrator diagnostics --full
```

### Log Locations

- **Main Log**: `logs/orchestrator.log`
- **Error Log**: `logs/orchestrator_error.log`
- **Audit Log**: `logs/orchestrator_audit.log`
- **Performance Log**: `logs/orchestrator_performance.log`
- **Strategy Logs**: `logs/strategies/`

## Common Issues and Solutions

### Startup Issues

#### Issue: Orchestrator Won't Start

**Symptoms:**
- Command hangs or fails immediately
- Error message: "Failed to initialize orchestrator"
- No log entries created

**Diagnosis:**
```bash
# Check configuration validity
genebot orchestrator config validate --config config/orchestrator_config.yaml --verbose

# Check for port conflicts
netstat -an | grep 8080

# Verify file permissions
ls -la config/orchestrator_config.yaml
ls -la logs/
```

**Solutions:**

1. **Configuration Issues:**
```bash
# Fix YAML syntax errors
python -c "import yaml; yaml.safe_load(open('config/orchestrator_config.yaml'))"

# Check for missing environment variables
grep -o '\${[^}]*}' config/orchestrator_config.yaml
```

2. **Port Conflicts:**
```yaml
# Change API port in configuration
api:
  port: 8081  # Use different port
```

3. **Permission Issues:**
```bash
# Fix log directory permissions
chmod 755 logs/
chmod 644 logs/*.log

# Fix config file permissions
chmod 644 config/orchestrator_config.yaml
```

#### Issue: Strategy Loading Failures

**Symptoms:**
- "Strategy not found" errors
- Some strategies missing from active list
- Import errors in logs

**Diagnosis:**
```bash
# List available strategies
genebot strategies list --all

# Check strategy imports
python -c "from src.strategies.moving_average_strategy import MovingAverageStrategy"

# Verify strategy registry
genebot orchestrator strategies --check-registry
```

**Solutions:**

1. **Missing Strategy Classes:**
```bash
# Ensure strategy files exist
ls -la src/strategies/

# Check for syntax errors in strategy files
python -m py_compile src/strategies/moving_average_strategy.py
```

2. **Import Path Issues:**
```python
# Add to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

3. **Strategy Configuration:**
```yaml
strategies:
  - type: "MovingAverageStrategy"  # Exact class name
    name: "ma_short"
    enabled: true
    # ... parameters
```

### Configuration Issues

#### Issue: Invalid Configuration Parameters

**Symptoms:**
- Validation errors on startup
- "Invalid parameter" messages
- Configuration not applied

**Common Validation Errors:**

1. **Invalid Allocation Method:**
```yaml
# Wrong
allocation:
  method: "invalid_method"

# Correct
allocation:
  method: "performance_based"  # or equal_weight, risk_parity, custom
```

2. **Out of Range Values:**
```yaml
# Wrong
risk:
  max_portfolio_drawdown: 1.5  # > 1.0

# Correct
risk:
  max_portfolio_drawdown: 0.10  # 0.0 - 1.0
```

3. **Missing Required Parameters:**
```yaml
# Wrong
strategies:
  - type: "MovingAverageStrategy"
    name: "ma_short"
    # Missing parameters

# Correct
strategies:
  - type: "MovingAverageStrategy"
    name: "ma_short"
    enabled: true
    parameters:
      short_period: 10
      long_period: 20
```

#### Issue: Environment Variable Substitution

**Symptoms:**
- Variables not replaced: `${API_TOKEN}` appears literally
- Authentication failures
- Missing configuration values

**Solutions:**

1. **Set Environment Variables:**
```bash
export API_TOKEN="your_token_here"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
```

2. **Use .env File:**
```bash
# Create .env file
echo "API_TOKEN=your_token_here" >> .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/..." >> .env

# Load environment variables
source .env
```

3. **Verify Variable Substitution:**
```bash
# Check resolved configuration
genebot orchestrator config show --resolved
```

### Performance Issues

#### Issue: Poor Strategy Performance

**Symptoms:**
- Low returns compared to individual strategies
- High correlation between strategies
- Frequent rebalancing

**Diagnosis:**
```bash
# Check strategy performance
genebot orchestrator strategies --detailed --sort-by performance

# View correlation matrix
genebot orchestrator correlations

# Check allocation history
genebot orchestrator allocations --history --period 30d
```

**Solutions:**

1. **Strategy Selection:**
```bash
# Disable underperforming strategies
genebot orchestrator config update --key strategies.poor_strategy.enabled --value false

# Adjust allocation weights
genebot orchestrator config update --key strategies.good_strategy.allocation_weight --value 1.5
```

2. **Reduce Correlation:**
```yaml
# Add correlation limits
risk:
  max_strategy_correlation: 0.60  # Lower threshold

# Use different strategy types
strategies:
  - type: "MovingAverageStrategy"    # Trend following
  - type: "RSIStrategy"             # Mean reversion
  - type: "ArbitrageStrategy"       # Market neutral
```

3. **Optimize Rebalancing:**
```yaml
allocation:
  rebalance_frequency: "weekly"     # Less frequent
  smoothing_factor: 0.9            # Smoother changes
```

#### Issue: High Drawdown

**Symptoms:**
- Portfolio drawdown exceeding limits
- Risk alerts triggered frequently
- Emergency stops activated

**Diagnosis:**
```bash
# Check risk status
genebot orchestrator risk-status

# View drawdown history
genebot orchestrator performance --metric drawdown --period 90d

# Check position sizes
genebot orchestrator positions --summary
```

**Solutions:**

1. **Tighten Risk Controls:**
```yaml
risk:
  max_portfolio_drawdown: 0.05     # Stricter limit
  position_size_limit: 0.02        # Smaller positions
  stop_loss_threshold: 0.01        # Tighter stops
```

2. **Adjust Allocation:**
```yaml
allocation:
  method: "risk_parity"            # Risk-based allocation
  max_allocation: 0.15             # Lower maximum
```

3. **Add Defensive Strategies:**
```yaml
strategies:
  - type: "DefensiveStrategy"
    name: "defensive"
    enabled: true
    allocation_weight: 0.5
```

### Operational Issues

#### Issue: Strategies Not Executing Trades

**Symptoms:**
- No trades generated despite signals
- "Insufficient funds" errors
- Position limits reached

**Diagnosis:**
```bash
# Check account balance
genebot account balance

# View strategy signals
genebot orchestrator signals --recent

# Check position limits
genebot orchestrator positions --limits
```

**Solutions:**

1. **Funding Issues:**
```bash
# Check available capital
genebot orchestrator capital --available

# Adjust allocation if needed
genebot orchestrator config update --key allocation.max_allocation --value 0.20
```

2. **Position Limits:**
```yaml
risk:
  max_concurrent_positions: 20     # Increase limit
  position_size_limit: 0.08        # Allow larger positions
```

3. **Signal Validation:**
```bash
# Check signal generation
genebot orchestrator strategies --signals --strategy ma_short

# Verify market data
genebot market-data status
```

#### Issue: Frequent Rebalancing

**Symptoms:**
- Allocations changing too often
- High transaction costs
- Unstable performance

**Solutions:**

1. **Adjust Rebalancing Settings:**
```yaml
allocation:
  rebalance_frequency: "weekly"    # Less frequent
  smoothing_factor: 0.8           # Smoother changes
  min_allocation_change: 0.02     # Minimum change threshold
```

2. **Add Rebalancing Constraints:**
```yaml
allocation:
  rebalancing_constraints:
    max_turnover: 0.20             # Maximum portfolio turnover
    min_time_between: "24h"        # Minimum time between rebalances
```

### Monitoring and Alerting Issues

#### Issue: Missing Alerts

**Symptoms:**
- No notifications received
- Alert conditions not triggering
- Monitoring dashboard empty

**Diagnosis:**
```bash
# Check alert configuration
genebot orchestrator config show --section monitoring

# Test notification channels
genebot orchestrator alerts test --channel email

# Check alert history
genebot orchestrator alerts --history
```

**Solutions:**

1. **Email Configuration:**
```yaml
monitoring:
  notifications:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "alerts@example.com"
      password: "${EMAIL_PASSWORD}"
      recipients: ["trader@example.com"]
```

2. **Slack Configuration:**
```yaml
monitoring:
  notifications:
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channel: "#trading-alerts"
```

3. **Alert Thresholds:**
```yaml
monitoring:
  alert_thresholds:
    drawdown: 0.03                 # Lower threshold
    performance_degradation: 0.20  # More sensitive
```

#### Issue: Performance Monitoring Problems

**Symptoms:**
- Metrics not updating
- Dashboard showing stale data
- Performance calculations incorrect

**Solutions:**

1. **Check Metrics Collection:**
```bash
# Verify metrics service
genebot orchestrator metrics --test

# Check data pipeline
genebot orchestrator diagnostics --metrics
```

2. **Database Issues:**
```bash
# Check database connection
genebot orchestrator db-status

# Repair metrics database
genebot orchestrator db-repair --metrics
```

## Advanced Troubleshooting

### Debug Mode

Enable debug logging for detailed troubleshooting:

```yaml
logging:
  level: "DEBUG"
  console:
    enabled: true
    level: "DEBUG"
```

Or via command line:
```bash
genebot orchestrator start --log-level DEBUG
```

### Memory and Performance Issues

#### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep orchestrator

# Monitor memory over time
top -p $(pgrep -f orchestrator)
```

**Solutions:**

1. **Reduce Data Retention:**
```yaml
monitoring:
  data_retention: 30              # Reduce from 365 days
  metrics_frequency: "5m"         # Less frequent collection
```

2. **Optimize Strategy Count:**
```bash
# Disable unused strategies
genebot orchestrator strategies --disable-unused
```

#### Slow Performance

**Diagnosis:**
```bash
# Profile performance
genebot orchestrator profile --duration 60s

# Check database performance
genebot orchestrator db-stats
```

**Solutions:**

1. **Database Optimization:**
```bash
# Optimize database
genebot orchestrator db-optimize

# Add indexes
genebot orchestrator db-index --create
```

2. **Reduce Computation:**
```yaml
allocation:
  rebalance_frequency: "daily"    # Less frequent
optimization:
  optimization_frequency: "weekly" # Less frequent
```

### Network and Connectivity Issues

#### Exchange Connection Problems

**Symptoms:**
- "Connection failed" errors
- Stale market data
- Order execution failures

**Diagnosis:**
```bash
# Test exchange connections
genebot exchanges test-connection --all

# Check network connectivity
ping api.binance.com
```

**Solutions:**

1. **Connection Settings:**
```yaml
exchanges:
  binance:
    timeout: 30                   # Increase timeout
    retry_attempts: 5             # More retries
    rate_limit_buffer: 0.1        # Add buffer
```

2. **Failover Configuration:**
```yaml
exchanges:
  primary: "binance"
  fallback: ["coinbase", "kraken"]
  auto_failover: true
```

### Data Issues

#### Missing Market Data

**Symptoms:**
- Strategies not generating signals
- "No data available" errors
- Stale price information

**Solutions:**

1. **Check Data Sources:**
```bash
# Verify data feeds
genebot market-data status --all

# Test data retrieval
genebot market-data test --symbol BTC/USD
```

2. **Data Backup Sources:**
```yaml
data:
  sources:
    primary: "binance"
    backup: ["coinbase", "kraken"]
  fallback_enabled: true
```

## Recovery Procedures

### Emergency Recovery

If the orchestrator is in an unstable state:

1. **Emergency Stop:**
```bash
genebot orchestrator emergency-stop --close-positions
```

2. **Safe Mode Start:**
```bash
genebot orchestrator start --safe-mode --config config/minimal_config.yaml
```

3. **Position Review:**
```bash
genebot positions list --all
genebot positions close --strategy failed_strategy
```

### Configuration Recovery

If configuration is corrupted:

1. **Restore from Backup:**
```bash
cp config/backups/orchestrator_config_backup.yaml config/orchestrator_config.yaml
```

2. **Reset to Defaults:**
```bash
genebot orchestrator config reset --template conservative
```

3. **Validate and Start:**
```bash
genebot orchestrator config validate
genebot orchestrator start
```

### Data Recovery

If performance data is lost:

1. **Rebuild Metrics:**
```bash
genebot orchestrator rebuild-metrics --from-trades
```

2. **Restore from Backup:**
```bash
genebot orchestrator restore-data --backup-file metrics_backup.sql
```

## Getting Help

### Log Collection

When reporting issues, collect relevant logs:

```bash
# Create support bundle
genebot orchestrator support-bundle --output support_bundle.zip

# Or collect manually
tar -czf logs_bundle.tar.gz logs/ config/ 
```

### Diagnostic Information

Include this information when seeking help:

```bash
# System information
genebot orchestrator system-info

# Configuration summary
genebot orchestrator config summary

# Recent error logs
tail -100 logs/orchestrator_error.log
```

### Contact Information

- **Documentation**: Check the user guide and API reference
- **GitHub Issues**: Report bugs and feature requests
- **Community Forum**: Ask questions and share experiences
- **Support Email**: For critical production issues

## Prevention Best Practices

1. **Regular Monitoring**: Set up comprehensive monitoring and alerting
2. **Configuration Backups**: Regularly backup configuration files
3. **Testing**: Test configuration changes in a sandbox environment
4. **Updates**: Keep the orchestrator and strategies updated
5. **Documentation**: Document any customizations or special configurations

For more detailed information on specific topics, refer to:
- User Guide: `docs/ORCHESTRATOR_USER_GUIDE.md`
- Configuration Reference: `docs/ORCHESTRATOR_CONFIG_REFERENCE.md`
- API Reference: `docs/ORCHESTRATOR_API_REFERENCE.md`
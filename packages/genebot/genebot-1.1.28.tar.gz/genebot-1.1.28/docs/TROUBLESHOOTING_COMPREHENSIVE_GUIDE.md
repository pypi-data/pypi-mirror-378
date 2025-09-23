# GeneBot Comprehensive Troubleshooting Guide v1.1.28

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Configuration Problems](#configuration-problems)
4. [Account and API Issues](#account-and-api-issues)
5. [Strategy Issues](#strategy-issues)
6. [Orchestrator Problems](#orchestrator-problems)
7. [Performance Issues](#performance-issues)
8. [Security and Permissions](#security-and-permissions)
9. [Multi-Market Issues](#multi-market-issues)
10. [Advanced Troubleshooting](#advanced-troubleshooting)
11. [Emergency Procedures](#emergency-procedures)
12. [Getting Help](#getting-help)

## Quick Diagnostics

### First Steps for Any Issue

```bash
# 1. Check system status
genebot status --detailed

# 2. Validate configuration
genebot validate-config

# 3. Check system health
genebot health-check

# 4. Review recent logs
tail -f logs/genebot.log

# 5. Generate error report
genebot error-report
```

### System Information Commands

```bash
# Check version
genebot --version

# List all accounts
genebot list-accounts

# List all strategies
genebot list-strategies

# Check configuration status
genebot config-status

# Security audit
genebot security audit
```

## Common Issues

### Issue: "No accounts configured yet"

**Symptoms**: Bot won't start, error message about missing accounts

**Solutions**:
```bash
# Check if accounts exist
genebot list-accounts

# If no accounts, initialize and add demo accounts
genebot init-config
genebot add-crypto binance --mode demo
genebot add-forex oanda --mode demo

# Validate accounts
genebot validate-accounts
```

**Root Causes**:
- Fresh installation without account setup
- Corrupted accounts.yaml file
- Incorrect configuration path

### Issue: "API credentials invalid" or "Authentication failed"

**Symptoms**: Account validation fails, trading operations rejected

**Solutions**:
```bash
# Check environment variables
cat .env | grep -E "(API_KEY|API_SECRET)"

# Validate specific account
genebot validate-accounts --account account_name

# Security credential check
genebot security validate-credentials

# Re-add account with correct credentials
genebot remove-account old_account
genebot add-crypto binance --mode demo
```

**Root Causes**:
- Incorrect API keys or secrets
- API keys lack required permissions
- IP address not whitelisted
- Using production keys with sandbox mode
- Expired or suspended API keys

### Issue: "Strategy not found" or "Strategy failed to load"

**Symptoms**: Strategy errors in logs, strategies not executing

**Solutions**:
```bash
# List available strategies
genebot list-strategies

# Check strategy configuration
genebot validate-config --verbose

# Verify strategy name in config
nano config/trading_bot_config.yaml

# Check strategy file exists
ls -la src/strategies/
```

**Root Causes**:
- Typo in strategy name or type
- Strategy file missing or corrupted
- Import errors in strategy code
- Invalid strategy parameters

### Issue: "Permission denied" or "Access denied"

**Symptoms**: File access errors, API permission errors

**Solutions**:
```bash
# Check file permissions
ls -la config/
chmod 600 .env
chmod 644 config/*.yaml

# Check API permissions
genebot security check-permissions

# Fix ownership issues
sudo chown -R $USER:$USER .
```

**Root Causes**:
- Incorrect file permissions
- API key permissions insufficient
- User account issues
- SELinux or AppArmor restrictions

### Issue: Bot won't start or crashes immediately

**Symptoms**: Bot exits immediately, process doesn't stay running

**Solutions**:
```bash
# Comprehensive validation
genebot system-validate --verbose

# Check for port conflicts
netstat -tulpn | grep :8080

# Run in foreground for debugging
genebot start --foreground --log-level DEBUG

# Check system resources
df -h  # Disk space
free -h  # Memory
```

**Root Causes**:
- Configuration errors
- Port conflicts
- Insufficient system resources
- Missing dependencies
- Database connection issues

## Configuration Problems

### Invalid Configuration Files

**Symptoms**: Validation errors, YAML parsing errors

**Solutions**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/trading_bot_config.yaml'))"

# Use configuration backup
genebot config-restore

# Reset to default configuration
genebot init-config --overwrite --template development
```

### Configuration Migration Issues

**Symptoms**: Old configuration format, migration errors

**Solutions**:
```bash
# Check current configuration version
genebot config-status

# Backup before migration
genebot config-backup

# Migrate configuration
genebot config-migrate --version latest

# Validate after migration
genebot validate-config
```

### Environment Variable Issues

**Symptoms**: API credentials not found, environment errors

**Solutions**:
```bash
# Check environment variables are loaded
env | grep -E "(BINANCE|OANDA|COINBASE)"

# Reload environment
source .env

# Check .env file format
cat -A .env  # Shows hidden characters

# Fix common .env issues
sed -i 's/\r$//' .env  # Remove Windows line endings
```

## Account and API Issues

### Exchange/Broker Connectivity

**Symptoms**: Connection timeouts, API errors

**Solutions**:
```bash
# Test connectivity
genebot validate-accounts --timeout 60

# Check exchange status
curl -s https://api.binance.com/api/v3/ping

# Test with different timeout
genebot validate-accounts --account binance-demo --timeout 120
```

### API Rate Limiting

**Symptoms**: Rate limit errors, temporary bans

**Solutions**:
```bash
# Check API usage
genebot analytics api-usage

# Reduce request frequency
# Edit config/trading_bot_config.yaml:
# api_settings:
#   request_delay: 1000  # milliseconds
#   max_requests_per_minute: 100

# Use different API keys
genebot add-crypto binance --name binance-backup
```

### Sandbox vs Live Mode Issues

**Symptoms**: Orders not executing, balance errors

**Solutions**:
```bash
# Check account mode
genebot list-accounts

# Verify environment settings
grep SANDBOX .env

# Switch to correct mode
genebot edit-crypto binance-demo
# Set sandbox: true for demo, false for live
```

## Strategy Issues

### Strategy Not Executing Trades

**Symptoms**: Strategy running but no trades generated

**Solutions**:
```bash
# Monitor strategy in real-time
genebot monitor --strategy RSIStrategy

# Check strategy parameters
genebot analytics performance --strategy RSIStrategy

# Verify market conditions
genebot trades --limit 10

# Check risk limits
# Review risk_management section in config
```

**Root Causes**:
- Market conditions don't meet strategy criteria
- Risk limits preventing trades
- Insufficient account balance
- Strategy parameters too restrictive

### Poor Strategy Performance

**Symptoms**: Consistent losses, low win rate

**Solutions**:
```bash
# Analyze strategy performance
genebot analytics performance --strategy MyStrategy --period 30days

# Compare with benchmark
genebot analytics attribution --strategy MyStrategy

# Optimize parameters
genebot analytics optimization --strategy MyStrategy

# Backtest with different parameters
genebot backtest --strategy MyStrategy --period 90days
```

### Strategy Parameter Errors

**Symptoms**: Invalid parameter errors, strategy won't load

**Solutions**:
```bash
# Validate strategy configuration
genebot validate-config --verbose

# Check parameter ranges
# Review strategy documentation
genebot config-help

# Reset to default parameters
# Copy from config/templates/
```

## Orchestrator Problems

### Orchestrator Won't Start

**Symptoms**: Orchestrator startup failures, allocation errors

**Solutions**:
```bash
# Check orchestrator configuration
genebot orchestrator-config validate

# Validate strategy allocations
# Ensure allocations sum to 1.0 or less

# Check orchestrator status
genebot orchestrator-status --verbose

# Start with minimal configuration
genebot orchestrator-migrate generate --allocation-method equal_weight
```

### Allocation Issues

**Symptoms**: Incorrect strategy allocations, rebalancing errors

**Solutions**:
```bash
# Check current allocations
genebot orchestrator-monitor --format json

# Force rebalancing
genebot orchestrator-intervention force_rebalance

# Adjust allocations manually
genebot orchestrator-intervention adjust_allocation --allocation '{"strategy1": 0.5, "strategy2": 0.5}'

# Reset to equal weights
genebot orchestrator-config update --allocation-method equal_weight
```

### Performance Monitoring Issues

**Symptoms**: Missing performance data, monitoring errors

**Solutions**:
```bash
# Check monitoring configuration
cat config/monitoring_config.yaml

# Restart monitoring
genebot stop-monitoring
genebot start-monitoring

# Check Prometheus/Grafana connectivity
curl -s http://localhost:9090/metrics
```

## Performance Issues

### High CPU Usage

**Symptoms**: System slowdown, high CPU utilization

**Solutions**:
```bash
# Check process usage
genebot instance-metrics main

# Reduce strategy frequency
# Edit strategy parameters to reduce calculation frequency

# Limit concurrent strategies
# Reduce number of active strategies

# Optimize system settings
# Increase monitoring intervals
```

### Memory Issues

**Symptoms**: Out of memory errors, system crashes

**Solutions**:
```bash
# Check memory usage
free -h
genebot instance-metrics main --json

# Clean up logs
genebot cleanup

# Reduce data retention
# Edit config/logging_config.yaml:
# retention_days: 7

# Restart bot instances
genebot restart
```

### Slow Order Execution

**Symptoms**: Delayed order fills, execution timeouts

**Solutions**:
```bash
# Check network latency
ping api.binance.com

# Optimize order settings
# Edit strategy parameters:
# execution_timeout: 10  # seconds
# order_type: "market"   # faster than limit orders

# Use faster exchanges
# Switch to exchanges with better API performance
```

## Security and Permissions

### Credential Security Issues

**Symptoms**: Security warnings, credential exposure

**Solutions**:
```bash
# Security audit
genebot security audit

# Check file permissions
ls -la .env config/

# Secure sensitive files
chmod 600 .env
chmod 600 config/accounts.yaml

# Rotate API keys
# Generate new keys on exchanges
# Update .env file
# Test with new credentials
```

### Access Control Issues

**Symptoms**: Permission denied errors, access restrictions

**Solutions**:
```bash
# Check user permissions
id
groups

# Fix ownership
sudo chown -R $USER:$USER .

# Check SELinux/AppArmor
getenforce  # SELinux
aa-status   # AppArmor
```

## Multi-Market Issues

### Cross-Market Arbitrage Problems

**Symptoms**: Arbitrage opportunities not detected, execution failures

**Solutions**:
```bash
# Check multi-market configuration
grep -A 10 "multi_market:" config/trading_bot_config.yaml

# Validate all market accounts
genebot validate-accounts

# Check market data synchronization
genebot monitor --cross-market

# Verify arbitrage parameters
# min_spread should be realistic (0.005 = 0.5%)
# execution_timeout should be sufficient
```

### Market Correlation Issues

**Symptoms**: High correlation warnings, risk limit violations

**Solutions**:
```bash
# Analyze correlations
genebot analytics correlation --markets crypto,forex

# Adjust correlation limits
# Edit config/trading_bot_config.yaml:
# multi_market:
#   correlation_threshold: 0.9  # Allow higher correlation

# Diversify across markets
# Add more uncorrelated assets
```

## Advanced Troubleshooting

### Debug Mode

```bash
# Enable comprehensive debugging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debug logging
genebot start --log-level DEBUG --foreground

# Monitor debug logs
tail -f logs/genebot.log | grep DEBUG
```

### Database Issues

```bash
# Check database connectivity
python -c "from src.database import get_connection; print(get_connection())"

# Reset database
genebot reset --database-only

# Backup/restore database
genebot data-export --format sql
genebot data-import --file backup.sql
```

### Network Diagnostics

```bash
# Test exchange connectivity
curl -s https://api.binance.com/api/v3/time
curl -s https://api-fxtrade.oanda.com/v3/accounts

# Check DNS resolution
nslookup api.binance.com

# Test with different network
# Try mobile hotspot or VPN
```

### Process Management

```bash
# Check running processes
ps aux | grep genebot

# Kill stuck processes
pkill -f genebot

# Check process limits
ulimit -a

# Monitor system resources
top -p $(pgrep -f genebot)
```

## Emergency Procedures

### Emergency Stop All Trading

```bash
# Immediate stop
genebot stop --force

# Emergency orchestrator stop
genebot orchestrator-intervention emergency_stop --reason "Emergency stop"

# Stop all instances
genebot list-instances
genebot stop-instance instance1
genebot stop-instance instance2
```

### Close All Positions

```bash
# CAUTION: This closes all open positions
genebot close-all-orders --confirm

# Check positions before closing
genebot trades --limit 50
```

### System Recovery

```bash
# 1. Stop all processes
genebot stop --force
genebot stop-monitoring

# 2. Backup current state
genebot config-backup
genebot data-export

# 3. Validate system
genebot system-validate

# 4. Restore from backup if needed
genebot config-restore --timestamp latest

# 5. Restart with validation
genebot validate-config
genebot start
```

### Data Recovery

```bash
# Export all data
genebot data-export --format json --output backup_$(date +%Y%m%d).json

# Import from backup
genebot data-import --file backup_20240101.json

# Verify data integrity
genebot system-validate --verbose
```

## Getting Help

### Self-Help Resources

```bash
# Built-in help
genebot --help
genebot config-help

# Command-specific help
genebot start --help
genebot orchestrator-config --help

# Generate comprehensive report
genebot error-report --verbose
```

### Log Analysis

```bash
# View recent errors
grep -i error logs/genebot.log | tail -20

# Search for specific issues
grep -i "api" logs/genebot.log
grep -i "strategy" logs/genebot.log
grep -i "orchestrator" logs/genebot.log

# Monitor live logs
tail -f logs/genebot.log | grep -E "(ERROR|WARNING)"
```

### System Information for Support

```bash
# Collect system information
echo "GeneBot Version: $(genebot --version)"
echo "Python Version: $(python --version)"
echo "OS: $(uname -a)"
echo "Disk Space: $(df -h .)"
echo "Memory: $(free -h)"

# Configuration summary
genebot config-status
genebot list-accounts
genebot list-strategies
```

### Contact Information

- **GitHub Issues**: [Report bugs and request features](https://github.com/genebot/genebot/issues)
- **Documentation**: [Complete documentation](https://docs.genebot.ai)
- **Community**: [Discord server](https://discord.gg/genebot)
- **Email Support**: support@genebot.ai

### Before Contacting Support

1. **Try the quick diagnostics** at the top of this guide
2. **Generate an error report**: `genebot error-report`
3. **Check recent logs**: `tail -100 logs/genebot.log`
4. **Validate configuration**: `genebot system-validate --verbose`
5. **Document the issue**: Steps to reproduce, error messages, system info

This comprehensive troubleshooting guide should help resolve most issues you encounter with GeneBot. If you continue to experience problems, don't hesitate to reach out for support with the information gathered from these diagnostic steps.
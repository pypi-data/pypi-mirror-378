# GeneBot CLI Troubleshooting Guide

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Configuration Problems](#configuration-problems)
4. [Account Issues](#account-issues)
5. [Process Management Issues](#process-management-issues)
6. [Network and Connectivity Issues](#network-and-connectivity-issues)
7. [Performance Issues](#performance-issues)
8. [Security Issues](#security-issues)
9. [Database Issues](#database-issues)
10. [Error Code Reference](#error-code-reference)
11. [Advanced Troubleshooting](#advanced-troubleshooting)
12. [Getting Support](#getting-support)

## Quick Diagnostics

When experiencing issues, start with these quick diagnostic commands:

```bash
# Comprehensive system check
genebot system-validate --verbose

# Check CLI health
genebot health-check

# Run diagnostics
genebot diagnostics --verbose

# Check bot status
genebot status --detailed
```

### Emergency Commands

If the CLI is completely unresponsive:

```bash
# Force stop all processes
genebot stop --force

# Reset to clean state
genebot reset --all --confirm

# Reinitialize configuration
genebot init-config --overwrite
```

## Common Issues

### 1. "Command not found: genebot"

**Symptoms:**
- `bash: genebot: command not found`
- CLI not accessible from command line

**Causes:**
- GeneBot not installed
- Installation path not in PATH
- Virtual environment not activated

**Solutions:**

```bash
# Check if GeneBot is installed
pip list | grep genebot

# Install if missing
pip install genebot

# Check installation path
which genebot

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(python -m site --user-base)/bin"

# Activate virtual environment if using one
source venv/bin/activate
```

### 2. "Permission denied" Errors

**Symptoms:**
- Cannot read/write configuration files
- Cannot create PID files
- Cannot access log directories

**Causes:**
- Incorrect file permissions
- Wrong file ownership
- SELinux/AppArmor restrictions

**Solutions:**

```bash
# Fix configuration file permissions
chmod 600 config/accounts.yaml
chmod 600 .env
chmod 755 config/
chmod 755 logs/

# Fix ownership (replace 'user' with your username)
chown -R user:user config/
chown -R user:user logs/

# Check current permissions
ls -la config/
ls -la logs/

# Create missing directories
mkdir -p logs/errors
mkdir -p reports
mkdir -p backups
```

### 3. "Configuration file not found"

**Symptoms:**
- CLI cannot find configuration files
- "No such file or directory" errors

**Causes:**
- Configuration not initialized
- Wrong working directory
- Incorrect configuration path

**Solutions:**

```bash
# Initialize configuration
genebot init-config

# Check current directory
pwd
ls -la config/

# Use custom configuration path
genebot --config-path /path/to/config status

# Set environment variable
export GENEBOT_CONFIG_PATH=/path/to/config
```

### 4. "Invalid configuration format"

**Symptoms:**
- YAML parsing errors
- Configuration validation failures
- Malformed configuration messages

**Causes:**
- Syntax errors in YAML files
- Missing required fields
- Incorrect data types

**Solutions:**

```bash
# Validate configuration syntax
genebot validate-config --strict

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/accounts.yaml'))"

# Fix common issues automatically
genebot validate-config --fix

# Regenerate configuration from template
genebot init-config --template minimal --overwrite

# View configuration help
genebot config-help --examples
```

## Configuration Problems

### Missing Required Fields

**Error:** "Missing required field: api_key"

**Solution:**
```bash
# Check account configuration
genebot validate-accounts --account binance --detailed

# Edit account to add missing fields
genebot edit-crypto binance --interactive

# Or add field directly
genebot edit-crypto binance --field api_key --value $BINANCE_API_KEY
```

### Environment Variable Issues

**Error:** "Environment variable not found: BINANCE_API_KEY"

**Solution:**
```bash
# Check environment variables
env | grep -E "BINANCE|OANDA|GENEBOT"

# Load from .env file
source .env

# Set missing variables
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"

# Verify .env file format
cat .env | grep -v "^#" | grep "="
```

### Configuration Validation Failures

**Error:** "Configuration validation failed"

**Solution:**
```bash
# Run detailed validation
genebot validate-config --strict --verbose

# Check specific configuration file
genebot validate-config --file config/accounts.yaml

# View validation errors
genebot validate-config 2>&1 | grep -i error

# Fix issues automatically
genebot validate-config --fix

# Restore from backup if needed
genebot config-restore --backup-date $(date -d '1 day ago' +%Y-%m-%d)
```

## Account Issues

### Account Validation Failures

**Error:** "Account validation failed: Connection timeout"

**Diagnosis:**
```bash
# Test specific account
genebot validate-accounts --account binance --detailed

# Check network connectivity
ping api.binance.com
curl -I https://api.binance.com/api/v3/ping

# Test with verbose output
genebot validate-accounts --verbose
```

**Solutions:**
```bash
# Increase timeout
genebot edit-crypto binance --field timeout --value 60

# Check API credentials
genebot validate-accounts --account binance --fix-issues

# Test in sandbox mode first
genebot edit-crypto binance --field sandbox --value true

# Check rate limits
genebot edit-crypto binance --field rate_limit --value 600
```

### API Authentication Errors

**Error:** "Invalid API credentials"

**Diagnosis:**
```bash
# Check credential format
genebot list-accounts --show-credentials

# Verify environment variables
echo $BINANCE_API_KEY | wc -c  # Should be 64 characters
echo $BINANCE_API_SECRET | wc -c  # Should be 64 characters
```

**Solutions:**
```bash
# Update credentials
genebot edit-crypto binance --field api_key --value $NEW_BINANCE_KEY
genebot edit-crypto binance --field api_secret --value $NEW_BINANCE_SECRET

# Test credentials manually
curl -H "X-MBX-APIKEY: $BINANCE_API_KEY" https://api.binance.com/api/v3/account

# Regenerate API keys on exchange
# Then update in GeneBot
genebot remove-account binance crypto
genebot add-crypto --name binance --exchange binance --api-key $NEW_KEY
```

### Exchange-Specific Issues

#### Binance Issues

**Error:** "Binance API error: -1021 Timestamp outside of recv window"

**Solution:**
```bash
# Sync system time
sudo ntpdate -s time.nist.gov

# Check system time
date

# Adjust recv window (if supported)
genebot edit-crypto binance --field recv_window --value 10000
```

#### Coinbase Issues

**Error:** "Coinbase API error: Invalid passphrase"

**Solution:**
```bash
# Ensure passphrase is set
genebot edit-crypto coinbase --field api_passphrase --value $COINBASE_PASSPHRASE

# Verify all three credentials are set
genebot validate-accounts --account coinbase --detailed
```

#### OANDA Issues

**Error:** "OANDA API error: Insufficient authorization"

**Solution:**
```bash
# Check account ID format
genebot edit-forex oanda --field account_id --value "101-001-12345678-001"

# Verify API token permissions
curl -H "Authorization: Bearer $OANDA_API_KEY" \
  https://api-fxpractice.oanda.com/v3/accounts
```

## Process Management Issues

### Bot Won't Start

**Error:** "Failed to start trading bot"

**Diagnosis:**
```bash
# Check system status
genebot system-validate

# Check for existing processes
genebot status --detailed
ps aux | grep -i genebot

# Check PID files
ls -la *.pid

# Check logs
tail -f logs/cli.log
tail -f logs/trading.log
```

**Solutions:**
```bash
# Clean up stale processes
genebot stop --force
rm -f *.pid

# Check configuration
genebot validate-config
genebot validate-accounts

# Start with verbose output
genebot start --verbose

# Start in dry-run mode first
genebot start --dry-run

# Check system resources
genebot health-check --components system
```

### Process Becomes Unresponsive

**Symptoms:**
- Bot status shows running but no activity
- Commands hang or timeout
- High CPU/memory usage

**Diagnosis:**
```bash
# Check process status
genebot instance-status --metrics

# Check system resources
top -p $(cat bot.pid)
htop

# Check logs for errors
tail -f logs/errors/*.log
```

**Solutions:**
```bash
# Graceful restart
genebot restart

# Force restart if needed
genebot restart --force

# Check for memory leaks
genebot diagnostics --component memory

# Restart with resource limits
ulimit -m 1048576  # 1GB memory limit
genebot start
```

### Multiple Instance Conflicts

**Error:** "Instance already running"

**Diagnosis:**
```bash
# List all instances
genebot list-instances

# Check PID files
ls -la *_*.pid

# Check process tree
pstree -p $(cat bot.pid)
```

**Solutions:**
```bash
# Stop specific instance
genebot stop-instance crypto-arb

# Stop all instances
genebot stop --force

# Clean up PID files
rm -f bot_*.pid

# Start with unique instance names
genebot start-instance crypto-main --strategy arbitrage
genebot start-instance forex-trend --strategy trend_following
```

## Network and Connectivity Issues

### Connection Timeouts

**Error:** "Connection timeout to exchange API"

**Diagnosis:**
```bash
# Test network connectivity
ping api.binance.com
traceroute api.binance.com

# Test HTTPS connectivity
curl -I https://api.binance.com/api/v3/ping

# Check DNS resolution
nslookup api.binance.com
```

**Solutions:**
```bash
# Increase timeout values
genebot edit-crypto binance --field timeout --value 60

# Use different DNS servers
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Check firewall settings
sudo ufw status
sudo iptables -L

# Test with proxy if needed
export https_proxy=http://proxy.company.com:8080
genebot validate-accounts
```

### SSL/TLS Issues

**Error:** "SSL certificate verification failed"

**Diagnosis:**
```bash
# Test SSL connection
openssl s_client -connect api.binance.com:443

# Check certificate validity
curl -vI https://api.binance.com/api/v3/ping
```

**Solutions:**
```bash
# Update CA certificates
sudo apt-get update && sudo apt-get install ca-certificates

# For macOS
brew install ca-certificates

# Temporarily disable SSL verification (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

### Rate Limiting Issues

**Error:** "Rate limit exceeded"

**Diagnosis:**
```bash
# Check current rate limits
genebot list-accounts --show-credentials

# Monitor API usage
genebot monitor --accounts binance --refresh 5
```

**Solutions:**
```bash
# Reduce rate limits
genebot edit-crypto binance --field rate_limit --value 600

# Add delays between requests
genebot edit-crypto binance --field request_delay --value 1000

# Use multiple API keys if available
genebot add-crypto --name binance-backup --exchange binance \
  --api-key $BINANCE_BACKUP_KEY --api-secret $BINANCE_BACKUP_SECRET
```

## Performance Issues

### Slow CLI Response

**Symptoms:**
- Commands take long time to execute
- CLI appears to hang
- High CPU usage

**Diagnosis:**
```bash
# Check system resources
genebot health-check --components system

# Profile CLI performance
time genebot status

# Check database performance
genebot diagnostics --component database
```

**Solutions:**
```bash
# Clear log files
genebot reset --logs

# Optimize database
genebot diagnostics --component database --fix

# Increase system resources
# Add more RAM or CPU if running in VM

# Use quiet mode for scripts
genebot status --quiet

# Disable verbose logging
export GENEBOT_LOG_LEVEL=WARNING
```

### Memory Issues

**Error:** "Out of memory" or system becomes slow

**Diagnosis:**
```bash
# Check memory usage
free -h
genebot instance-status --metrics

# Check for memory leaks
ps aux --sort=-%mem | head -10
```

**Solutions:**
```bash
# Restart bot to free memory
genebot restart

# Set memory limits
ulimit -v 2097152  # 2GB virtual memory limit

# Clear caches
genebot reset --logs
sudo sync && sudo sysctl vm.drop_caches=3

# Monitor memory usage
genebot monitor --refresh 30 --metrics
```

### Database Performance Issues

**Symptoms:**
- Slow report generation
- Database connection timeouts
- High disk I/O

**Diagnosis:**
```bash
# Check database status
genebot diagnostics --component database

# Check disk space
df -h

# Check database size
du -sh *.db
```

**Solutions:**
```bash
# Optimize database
genebot diagnostics --component database --fix

# Clean old data
genebot reset --data --confirm

# Vacuum database (SQLite)
sqlite3 trading_bot.db "VACUUM;"

# Add database indexes (if supported)
genebot diagnostics --component database --optimize
```

## Security Issues

### Credential Exposure

**Warning:** "Credentials may be exposed in logs"

**Diagnosis:**
```bash
# Scan for exposed credentials
genebot security --scan

# Check log files
grep -r "api_key\|api_secret" logs/

# Check configuration files
genebot security --audit
```

**Solutions:**
```bash
# Fix credential exposure
genebot security --fix

# Rotate exposed credentials
genebot security --rotate-keys

# Clean logs
genebot reset --logs

# Update file permissions
chmod 600 config/accounts.yaml
chmod 600 .env
```

### File Permission Issues

**Error:** "Insecure file permissions detected"

**Diagnosis:**
```bash
# Check file permissions
ls -la config/
ls -la .env

# Run security scan
genebot security --scan
```

**Solutions:**
```bash
# Fix permissions automatically
genebot security --fix

# Manual permission fixes
chmod 600 config/accounts.yaml
chmod 600 .env
chmod 700 config/
chmod 755 logs/

# Set secure umask
umask 077
```

### API Key Security

**Warning:** "API keys have excessive permissions"

**Diagnosis:**
```bash
# Check API key permissions
genebot validate-accounts --detailed

# Test API key capabilities
curl -H "X-MBX-APIKEY: $BINANCE_API_KEY" \
  https://api.binance.com/api/v3/account
```

**Solutions:**
```bash
# Create new API keys with limited permissions
# On exchange: Enable only "Read Info" and "Spot & Margin Trading"
# Disable "Enable Withdrawals" and "Enable Futures"

# Update API keys in GeneBot
genebot edit-crypto binance --field api_key --value $NEW_LIMITED_KEY

# Verify permissions
genebot validate-accounts --account binance --detailed
```

## Database Issues

### Database Connection Errors

**Error:** "Unable to connect to database"

**Diagnosis:**
```bash
# Check database file
ls -la *.db

# Test database connection
sqlite3 trading_bot.db ".tables"

# Check database permissions
ls -la trading_bot.db
```

**Solutions:**
```bash
# Create database if missing
genebot init-config --database

# Fix database permissions
chmod 644 trading_bot.db

# Repair database
sqlite3 trading_bot.db ".recover" > recovered.sql
sqlite3 new_trading_bot.db < recovered.sql
mv new_trading_bot.db trading_bot.db

# Reset database if corrupted
genebot reset --data --confirm
```

### Database Corruption

**Error:** "Database is corrupted" or "Database disk image is malformed"

**Diagnosis:**
```bash
# Check database integrity
sqlite3 trading_bot.db "PRAGMA integrity_check;"

# Check disk space
df -h .

# Check for file system errors
fsck /dev/sda1  # Replace with your disk
```

**Solutions:**
```bash
# Backup current database
cp trading_bot.db trading_bot.db.backup

# Try to recover
sqlite3 trading_bot.db ".recover" > recovered.sql
sqlite3 new_trading_bot.db < recovered.sql

# If recovery fails, restore from backup
genebot config-restore --component database --backup-date $(date -d '1 day ago' +%Y-%m-%d)

# If no backup, reinitialize
mv trading_bot.db trading_bot.db.corrupted
genebot init-config --database
```

## Error Code Reference

### CLI Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 1 | General CLI error | Check command syntax and options |
| 2 | Configuration error | Validate and fix configuration |
| 3 | Account validation error | Check account credentials and connectivity |
| 4 | Process management error | Check system resources and permissions |
| 5 | Network connectivity error | Check network and firewall settings |
| 6 | Database error | Check database file and permissions |
| 7 | Security error | Fix file permissions and credential issues |
| 8 | Resource error | Check system resources (memory, disk) |
| 130 | User interruption (Ctrl+C) | Normal interruption, no action needed |

### Exchange Error Codes

#### Binance Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| -1021 | Timestamp outside recv window | Sync system time |
| -1022 | Invalid signature | Check API secret |
| -2010 | Account has insufficient balance | Add funds or reduce position size |
| -1003 | Too many requests | Reduce rate limit |

#### OANDA Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 401 | Unauthorized | Check API key and account ID |
| 403 | Forbidden | Check API key permissions |
| 404 | Not found | Check account ID format |
| 429 | Rate limit exceeded | Reduce request frequency |

## Advanced Troubleshooting

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Set debug log level
export GENEBOT_LOG_LEVEL=DEBUG

# Run command with verbose output
genebot --verbose status

# Enable debug logging for specific components
export GENEBOT_DEBUG_COMPONENTS="accounts,process,database"
```

### Log Analysis

Analyze logs for patterns and issues:

```bash
# View recent errors
tail -100 logs/cli.log | grep -i error

# Count error types
grep -i error logs/cli.log | sort | uniq -c | sort -nr

# Find performance issues
grep -i "slow\|timeout\|delay" logs/cli.log

# Analyze database queries
grep -i "sql\|query" logs/cli.log
```

### Network Debugging

Debug network connectivity issues:

```bash
# Trace network calls
strace -e trace=network genebot validate-accounts

# Monitor network traffic
sudo tcpdump -i any host api.binance.com

# Test with different network settings
export https_proxy=http://proxy:8080
export no_proxy=localhost,127.0.0.1
```

### System Resource Monitoring

Monitor system resources during CLI operations:

```bash
# Monitor in real-time
watch -n 1 'genebot status --json | jq .system_resources'

# Log resource usage
while true; do
  echo "$(date): $(genebot health-check --json | jq .resources)" >> resource_usage.log
  sleep 60
done
```

### Configuration Debugging

Debug configuration issues:

```bash
# Dump effective configuration
genebot config-help --dump-config

# Validate configuration step by step
genebot validate-config --component accounts
genebot validate-config --component strategies
genebot validate-config --component risk_management

# Test configuration parsing
python -c "
import yaml
with open('config/accounts.yaml') as f:
    config = yaml.safe_load(f)
    print(yaml.dump(config, indent=2))
"
```

## Getting Support

### Self-Help Resources

1. **Built-in Help**
   ```bash
   genebot --help
   genebot COMMAND --help
   genebot help --interactive
   ```

2. **System Information**
   ```bash
   genebot diagnostics --export system_info.json
   genebot system-validate --report system_report.txt
   ```

3. **Error Reports**
   ```bash
   genebot error-report --export error_analysis.json
   genebot diagnostics --verbose --export full_diagnostics.json
   ```

### Preparing Support Requests

When requesting support, include:

1. **System Information**
   ```bash
   genebot --version
   python --version
   uname -a
   ```

2. **Error Details**
   ```bash
   # Full command that failed
   genebot command --verbose 2>&1 | tee error_output.txt
   
   # Recent logs
   tail -100 logs/cli.log > recent_logs.txt
   ```

3. **Configuration (sanitized)**
   ```bash
   # Remove sensitive data before sharing
   genebot config-help --dump-config --sanitize > config_dump.yaml
   ```

4. **Diagnostic Report**
   ```bash
   genebot diagnostics --export diagnostics.json
   ```

### Emergency Recovery

If the CLI is completely broken:

```bash
# Emergency reset (will lose configuration)
rm -rf config/ logs/ *.pid *.db
genebot init-config

# Restore from backup if available
cp -r backups/latest/* ./

# Manual process cleanup
pkill -f genebot
pkill -f trading_bot
rm -f *.pid
```

### Community Resources

- Check documentation: `docs/`
- Review examples: `examples/`
- Check test cases: `tests/`
- Review configuration templates: `config/templates/`

Remember to sanitize any configuration files or logs before sharing them, removing API keys, account IDs, and other sensitive information.
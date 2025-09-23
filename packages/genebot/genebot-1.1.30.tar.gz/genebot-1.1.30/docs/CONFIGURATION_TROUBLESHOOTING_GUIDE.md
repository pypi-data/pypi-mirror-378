# Configuration Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve configuration issues with the GeneBot unified configuration system. It covers common problems, diagnostic steps, and solutions for configuration-related issues.

## Quick Diagnostic Commands

Before diving into specific issues, run these commands to get an overview of your configuration status:

```bash
# Check overall configuration status
genebot config-status --verbose

# Validate all configuration
genebot validate --verbose

# Test configuration discovery
genebot config-status --show-discovery

# Check environment variables
genebot config-status --show-env
```

## Common Issues and Solutions

### 1. Configuration Files Not Found

#### Symptoms
```
Error: No configuration files found
Error: Could not locate trading_bot_config.yaml
Warning: Using default configuration values
```

#### Diagnosis
```bash
# Check what files exist
ls -la config/
ls -la .env
ls -la trading_bot_config.yaml

# Check configuration discovery
genebot config-status --show-discovery
```

#### Solutions

**Solution 1: Initialize Configuration**
```bash
# Create configuration files using CLI
genebot init-config

# Verify files were created
genebot config-status
```

**Solution 2: Check File Locations**
```bash
# Ensure files are in expected locations
mkdir -p config
mv your_config.yaml config/trading_bot_config.yaml
mv your_accounts.yaml config/accounts.yaml
```

**Solution 3: Use Environment Variables**
```bash
# Override configuration file locations
export GENEBOT_CONFIG_FILE="/path/to/your/config.yaml"
export GENEBOT_ACCOUNTS_FILE="/path/to/your/accounts.yaml"

# Test override
genebot config-status
```

### 2. Configuration Validation Errors

#### Symptoms
```
Error: Configuration validation failed
Error: Invalid value for 'max_portfolio_risk'
Error: Missing required field 'api_key'
```

#### Diagnosis
```bash
# Get detailed validation errors
genebot validate --verbose

# Check specific configuration sections
genebot validate --section strategies
genebot validate --section risk_management
```

#### Solutions

**Solution 1: Fix Validation Errors**
```bash
# Use template to see correct format
genebot init-config --template development --show-only

# Compare with your configuration
diff config/trading_bot_config.yaml <(genebot init-config --template development --show-only)
```

**Solution 2: Check Required Fields**
```yaml
# Ensure all required fields are present
# config/trading_bot_config.yaml
version: "1.1.28"  # Required
app:
  name: "GeneBot"  # Required
  environment: "development"  # Required

strategies:
  # At least one strategy required
  rsi:
    enabled: true
    parameters:
      period: 14  # Required for RSI strategy
```

**Solution 3: Validate Data Types**
```yaml
# Ensure correct data types
risk_management:
  max_portfolio_risk: 0.02  # Float, not string
  max_positions: 10         # Integer, not string
  enabled: true             # Boolean, not string
```

### 3. Environment Variables Not Loading

#### Symptoms
```
Error: Environment variable 'BINANCE_API_KEY' not found
Warning: Using placeholder values for API keys
Error: Database connection failed - check DATABASE_URL
```

#### Diagnosis
```bash
# Check if .env file exists and is readable
ls -la .env
cat .env

# Check environment variable loading
genebot config-status --show-env

# Test specific environment variables
echo $BINANCE_API_KEY
echo $DATABASE_URL
```

#### Solutions

**Solution 1: Create or Fix .env File**
```bash
# Create .env file if missing
genebot init-config --env-only

# Check .env file format
cat > .env << EOF
# API Keys
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_api_secret_here

# Database
DATABASE_URL=sqlite:///trading_bot.db

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
```

**Solution 2: Check File Permissions**
```bash
# Ensure .env file is readable
chmod 600 .env
ls -la .env
```

**Solution 3: Verify Environment Variable Format**
```bash
# Correct format in .env
VARIABLE_NAME=value_without_quotes

# Incorrect formats to avoid:
# VARIABLE_NAME="value_with_quotes"  # Remove quotes
# VARIABLE_NAME = value              # Remove spaces around =
# export VARIABLE_NAME=value         # Remove export
```

### 4. Configuration Precedence Issues

#### Symptoms
```
Warning: Configuration value overridden by environment variable
Error: Conflicting configuration values found
Info: Using value from CLI-generated config instead of user config
```

#### Diagnosis
```bash
# Check configuration precedence
genebot config-status --show-precedence

# Identify configuration conflicts
genebot config-status --show-conflicts

# See all configuration sources
genebot config-status --show-sources
```

#### Solutions

**Solution 1: Understand Precedence Order**
```
1. Environment Variables (highest priority)
2. CLI-Generated Files
3. User-Specified Files
4. Default Values (lowest priority)
```

**Solution 2: Resolve Conflicts**
```bash
# Remove duplicate configuration from lower priority sources
# Or use environment variables to override specific values

# Example: Override log level temporarily
export GENEBOT_LOG_LEVEL=DEBUG
genebot start
```

**Solution 3: Clean Up Configuration Sources**
```bash
# Remove unused configuration files
rm old_config.yaml
rm ~/.genebot/config/old_config.yaml

# Verify only intended sources remain
genebot config-status --show-sources
```

### 5. API Key and Authentication Issues

#### Symptoms
```
Error: Exchange authentication failed
Error: Invalid API key format
Error: API key permissions insufficient
```

#### Diagnosis
```bash
# Check API key configuration
genebot validate --section exchanges

# Test API key format
genebot config-status --check-api-keys

# Test exchange connections
genebot test-connection --exchange binance
```

#### Solutions

**Solution 1: Verify API Key Format**
```bash
# Check .env file for correct API key format
cat .env | grep API_KEY

# Ensure no extra spaces or characters
BINANCE_API_KEY=your_64_character_api_key_here
BINANCE_API_SECRET=your_64_character_api_secret_here
```

**Solution 2: Check API Key Permissions**
```bash
# Ensure API keys have required permissions:
# - Read account information
# - Read market data
# - Place orders (if not in dry-run mode)

# Test with exchange directly
genebot test-exchange --exchange binance --dry-run
```

**Solution 3: Verify Sandbox Settings**
```yaml
# For testing, ensure sandbox is enabled
exchanges:
  binance:
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true  # Use testnet for development
```

### 6. Database Connection Issues

#### Symptoms
```
Error: Could not connect to database
Error: Database URL format invalid
Error: Permission denied for database
```

#### Diagnosis
```bash
# Check database configuration
genebot config-status --section database

# Test database connection
genebot test-database

# Check database URL format
echo $DATABASE_URL
```

#### Solutions

**Solution 1: Fix Database URL Format**
```bash
# SQLite (recommended for development)
DATABASE_URL=sqlite:///trading_bot.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/trading_bot

# MySQL
DATABASE_URL=mysql://username:password@localhost:3306/trading_bot
```

**Solution 2: Create Database**
```bash
# For SQLite (automatic)
# Database file will be created automatically

# For PostgreSQL
createdb trading_bot

# For MySQL
mysql -u root -p -e "CREATE DATABASE trading_bot;"
```

**Solution 3: Check Database Permissions**
```bash
# Ensure database user has required permissions
# For PostgreSQL:
psql -c "GRANT ALL PRIVILEGES ON DATABASE trading_bot TO your_user;"

# For MySQL:
mysql -u root -p -e "GRANT ALL PRIVILEGES ON trading_bot.* TO 'your_user'@'localhost';"
```

### 7. Strategy Configuration Issues

#### Symptoms
```
Error: Unknown strategy type 'invalid_strategy'
Error: Missing required parameter for strategy
Warning: Strategy disabled due to configuration error
```

#### Diagnosis
```bash
# List available strategies
genebot list-strategies

# Validate strategy configuration
genebot validate --section strategies

# Check specific strategy
genebot validate --strategy rsi
```

#### Solutions

**Solution 1: Use Valid Strategy Names**
```bash
# Check available strategies
genebot list-strategies

# Use exact strategy names in configuration
strategies:
  rsi:  # Correct
    enabled: true
  # rsi_strategy:  # Incorrect - use 'rsi'
```

**Solution 2: Provide Required Parameters**
```yaml
# Each strategy has required parameters
strategies:
  rsi:
    enabled: true
    parameters:
      period: 14          # Required
      oversold: 30        # Required
      overbought: 70      # Required
    symbols:
      - "BTC/USDT"        # Required
```

**Solution 3: Check Parameter Ranges**
```yaml
# Ensure parameters are within valid ranges
strategies:
  rsi:
    parameters:
      period: 14          # Must be > 0
      oversold: 30        # Must be 0-100
      overbought: 70      # Must be 0-100, > oversold
```

### 8. Logging Configuration Issues

#### Symptoms
```
Error: Could not create log file
Warning: Log level not recognized
Error: Log rotation failed
```

#### Diagnosis
```bash
# Check logging configuration
genebot config-status --section logging

# Test log file creation
touch logs/test.log
ls -la logs/

# Check log levels
genebot config-status --show-log-config
```

#### Solutions

**Solution 1: Create Log Directory**
```bash
# Ensure log directory exists
mkdir -p logs
chmod 755 logs
```

**Solution 2: Fix Log Level**
```bash
# Use valid log levels
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Or in configuration
app:
  log_level: "INFO"
```

**Solution 3: Check Log File Permissions**
```bash
# Ensure log files are writable
chmod 644 logs/*.log
chown $USER:$USER logs/
```

## Advanced Troubleshooting

### Debug Mode

Enable debug mode for detailed troubleshooting information:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export GENEBOT_DEBUG=true

# Run with debug output
genebot config-status --debug
genebot validate --debug
```

### Configuration Dump

Get complete configuration dump for analysis:

```bash
# Dump all configuration (sanitized)
genebot config-dump --sanitize

# Dump specific section
genebot config-dump --section strategies

# Dump with source information
genebot config-dump --show-sources
```

### Manual Configuration Testing

Test configuration loading manually:

```python
# test_config.py
from config.unified_loader import UnifiedConfigLoader
from config.enhanced_manager import EnhancedConfigManager

def test_config_loading():
    try:
        # Test unified loader
        loader = UnifiedConfigLoader()
        config = loader.load_configuration()
        print("✅ Configuration loaded successfully")
        
        # Test enhanced manager
        manager = EnhancedConfigManager()
        config = manager.load_with_discovery()
        print("✅ Enhanced manager working")
        
        # Test validation
        status = loader.get_configuration_status()
        if status.validation_status.is_valid:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            for error in status.validation_status.errors:
                print(f"   - {error}")
                
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_config_loading()
```

```bash
# Run manual test
python test_config.py
```

## Diagnostic Scripts

### Configuration Health Check

```bash
#!/bin/bash
# config_health_check.sh

echo "GeneBot Configuration Health Check"
echo "=================================="

# Check configuration files exist
echo "1. Checking configuration files..."
if [ -f "config/trading_bot_config.yaml" ]; then
    echo "   ✅ Main config found"
else
    echo "   ❌ Main config missing"
fi

if [ -f "config/accounts.yaml" ]; then
    echo "   ✅ Accounts config found"
else
    echo "   ❌ Accounts config missing"
fi

if [ -f ".env" ]; then
    echo "   ✅ Environment file found"
else
    echo "   ❌ Environment file missing"
fi

# Check configuration status
echo "2. Checking configuration status..."
if genebot config-status > /dev/null 2>&1; then
    echo "   ✅ Configuration status OK"
else
    echo "   ❌ Configuration status failed"
fi

# Check validation
echo "3. Checking configuration validation..."
if genebot validate > /dev/null 2>&1; then
    echo "   ✅ Configuration validation passed"
else
    echo "   ❌ Configuration validation failed"
fi

# Check API keys
echo "4. Checking API keys..."
if [ -n "$BINANCE_API_KEY" ]; then
    echo "   ✅ Binance API key set"
else
    echo "   ⚠️  Binance API key not set"
fi

echo "Health check complete!"
```

### Environment Variables Check

```bash
#!/bin/bash
# check_env_vars.sh

echo "Environment Variables Check"
echo "=========================="

# Required environment variables
REQUIRED_VARS=(
    "BINANCE_API_KEY"
    "BINANCE_API_SECRET"
    "DATABASE_URL"
)

# Optional environment variables
OPTIONAL_VARS=(
    "LOG_LEVEL"
    "ENVIRONMENT"
    "GENEBOT_CONFIG_FILE"
    "GENEBOT_ACCOUNTS_FILE"
)

echo "Required variables:"
for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo "   ✅ $var is set"
    else
        echo "   ❌ $var is missing"
    fi
done

echo "Optional variables:"
for var in "${OPTIONAL_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo "   ✅ $var = ${!var}"
    else
        echo "   ⚠️  $var not set (using default)"
    fi
done
```

## Getting Additional Help

### Log Analysis

Check log files for configuration-related errors:

```bash
# Check main log file
tail -f logs/genebot.log | grep -i config

# Check error log
tail -f logs/errors.log | grep -i config

# Search for specific errors
grep -r "configuration" logs/
```

### Community Support

1. **Check Documentation**: Review all configuration guides
2. **Search Issues**: Look for similar problems in project issues
3. **Create Issue**: Report new problems with:
   - Configuration files (sanitized)
   - Error messages
   - Steps to reproduce
   - System information

### Professional Support

For production environments or complex issues:

1. **Configuration Review**: Professional review of configuration setup
2. **Custom Solutions**: Tailored configuration for specific requirements
3. **Training**: Team training on configuration management

## Prevention Best Practices

### 1. Regular Configuration Validation

```bash
# Add to cron job or CI/CD pipeline
0 */6 * * * /usr/local/bin/genebot validate --quiet || echo "Configuration validation failed" | mail -s "GeneBot Config Alert" admin@example.com
```

### 2. Configuration Monitoring

```bash
# Monitor configuration file changes
inotifywait -m config/ -e modify,create,delete --format '%w%f %e' | while read file event; do
    echo "Configuration file $file was $event"
    genebot validate --quiet || echo "Configuration validation failed after $event on $file"
done
```

### 3. Backup Strategy

```bash
# Daily configuration backup
#!/bin/bash
BACKUP_DIR="backups/config_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r config/ "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || true
echo "Configuration backed up to $BACKUP_DIR"
```

This troubleshooting guide should help you resolve most configuration issues. Remember to always validate your configuration after making changes and keep backups of working configurations.
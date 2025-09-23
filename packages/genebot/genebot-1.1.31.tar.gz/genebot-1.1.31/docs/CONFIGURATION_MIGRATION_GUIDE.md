# Configuration Migration Guide

## Overview

This guide helps you migrate from hardcoded configuration paths to the new unified configuration system introduced in GeneBot v1.1.28+. The unified system provides automatic configuration discovery, better error handling, and consistency between CLI and bot runtime.

## Migration Scenarios

### Scenario 1: Hardcoded Configuration Paths in main.py

**Before (Deprecated):**
```python
# main.py - Old approach
import yaml

# Hardcoded configuration paths
CONFIG_FILE = "config/multi_market_config.yaml"
ACCOUNTS_FILE = "config/accounts.yaml"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    config = load_config()
    # Start bot with config
```

**After (Recommended):**
```python
# main.py - New approach
from config.unified_loader import UnifiedConfigLoader
from config.enhanced_manager import EnhancedConfigManager

def main():
    # Use unified configuration loading
    config_manager = EnhancedConfigManager()
    config = config_manager.load_with_discovery()
    
    # Configuration is automatically discovered and validated
    print(f"Using configuration from: {config_manager.get_active_sources()}")
    
    # Start bot with discovered configuration
    start_bot(config)

if __name__ == "__main__":
    main()
```

### Scenario 2: Custom Configuration Loading Logic

**Before (Deprecated):**
```python
# Custom configuration loading
import os
import yaml
from pathlib import Path

def find_config():
    # Manual configuration discovery
    possible_paths = [
        "config/trading_bot_config.yaml",
        "trading_bot_config.yaml",
        os.path.expanduser("~/.genebot/config.yaml")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError("No configuration file found")

def load_config():
    config_path = find_config()
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

**After (Recommended):**
```python
# Use unified configuration system
from config.unified_loader import UnifiedConfigLoader

def load_config():
    loader = UnifiedConfigLoader()
    
    # Automatic discovery with intelligent precedence
    config = loader.load_configuration()
    
    # Get discovery information
    status = loader.get_configuration_status()
    print(f"Configuration loaded from: {status.active_sources}")
    
    return config
```

### Scenario 3: Environment-Specific Configuration

**Before (Deprecated):**
```python
# Manual environment handling
import os

def get_config_file():
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        return 'config/production_config.yaml'
    elif env == 'staging':
        return 'config/staging_config.yaml'
    else:
        return 'config/development_config.yaml'

config_file = get_config_file()
```

**After (Recommended):**
```python
# Environment variables automatically handled
from config.unified_loader import UnifiedConfigLoader

# Set environment variable to override config file
# export GENEBOT_CONFIG_FILE="config/production_config.yaml"

loader = UnifiedConfigLoader()
config = loader.load_configuration()

# Environment variables are automatically applied as overrides
```

## Step-by-Step Migration Process

### Step 1: Backup Existing Configuration

```bash
# Create backup of current configuration
mkdir -p backups/config_backup_$(date +%Y%m%d_%H%M%S)
cp -r config/ backups/config_backup_$(date +%Y%m%d_%H%M%S)/
cp .env backups/config_backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
```

### Step 2: Initialize Unified Configuration

```bash
# Initialize configuration using CLI (recommended)
genebot init-config

# Or migrate existing configuration
genebot migrate-config --from-hardcoded
```

### Step 3: Update Code to Use Unified System

Replace hardcoded configuration loading with unified system:

```python
# Replace this pattern
with open('hardcoded/path/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# With this pattern
from config.enhanced_manager import EnhancedConfigManager
config_manager = EnhancedConfigManager()
config = config_manager.load_with_discovery()
```

### Step 4: Validate Migration

```bash
# Validate new configuration
genebot validate

# Check configuration status
genebot config-status --verbose

# Test bot startup
genebot start --dry-run
```

### Step 5: Remove Deprecated Code

After successful migration, remove deprecated configuration loading code:

```python
# Remove these deprecated patterns:
# - Hardcoded file paths
# - Manual configuration discovery logic
# - Custom YAML loading code
# - Environment-specific file selection logic
```

## Common Migration Patterns

### Pattern 1: Replace Direct YAML Loading

```python
# Before
import yaml
with open('config/some_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# After
from config.unified_loader import UnifiedConfigLoader
loader = UnifiedConfigLoader()
config = loader.load_configuration()
```

### Pattern 2: Replace Configuration Path Constants

```python
# Before
CONFIG_PATH = "config/trading_bot_config.yaml"
ACCOUNTS_PATH = "config/accounts.yaml"

# After - No constants needed, paths are discovered automatically
from config.enhanced_manager import EnhancedConfigManager
config_manager = EnhancedConfigManager()
```

### Pattern 3: Replace Manual Environment Variable Handling

```python
# Before
import os
config_file = os.getenv('CONFIG_FILE', 'default_config.yaml')

# After - Environment variables handled automatically
# Just set GENEBOT_CONFIG_FILE environment variable
from config.unified_loader import UnifiedConfigLoader
loader = UnifiedConfigLoader()  # Automatically handles env vars
```

### Pattern 4: Replace Custom Validation Logic

```python
# Before
def validate_config(config):
    if 'strategies' not in config:
        raise ValueError("Missing strategies section")
    # Custom validation logic...

# After - Use built-in validation
from config.enhanced_manager import EnhancedConfigManager
config_manager = EnhancedConfigManager()
config = config_manager.load_with_discovery()  # Automatically validated
```

## Configuration File Migration

### Migrating Configuration File Locations

If your configuration files are in non-standard locations:

```bash
# Option 1: Move files to standard locations
mkdir -p config
mv your_custom_config.yaml config/trading_bot_config.yaml
mv your_accounts_config.yaml config/accounts.yaml

# Option 2: Use environment variables to specify custom locations
export GENEBOT_CONFIG_FILE="/path/to/your/custom_config.yaml"
export GENEBOT_ACCOUNTS_FILE="/path/to/your/accounts_config.yaml"
```

### Migrating Configuration Content

The unified system expects specific configuration file structures:

```yaml
# config/trading_bot_config.yaml - Main configuration
version: "1.1.28"
app:
  name: "GeneBot"
  environment: "development"

strategies:
  # Strategy configurations

risk_management:
  # Risk management settings

# ... other sections
```

```yaml
# config/accounts.yaml - Account configurations
exchanges:
  binance:
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true

brokers:
  oanda:
    api_key: "${OANDA_API_KEY}"
    account_id: "${OANDA_ACCOUNT_ID}"
    environment: "practice"
```

## Handling Migration Issues

### Issue 1: Configuration Not Found

**Problem:** Bot can't find configuration files after migration.

**Solution:**
```bash
# Check configuration discovery
genebot config-status --verbose

# Verify files are in correct locations
ls -la config/
ls -la .env

# Re-initialize if needed
genebot init-config --overwrite
```

### Issue 2: Configuration Validation Errors

**Problem:** Configuration fails validation after migration.

**Solution:**
```bash
# Get detailed validation errors
genebot validate --verbose

# Check for missing required fields
genebot config-status --check-required

# Use template to fix structure
genebot init-config --template development --merge
```

### Issue 3: Environment Variables Not Working

**Problem:** Environment variable overrides not being applied.

**Solution:**
```bash
# Check environment variable loading
genebot config-status --show-env

# Verify .env file format
cat .env

# Test environment variable override
export GENEBOT_LOG_LEVEL=DEBUG
genebot config-status
```

### Issue 4: Multiple Configuration Sources Conflict

**Problem:** Configuration values from different sources are conflicting.

**Solution:**
```bash
# Check configuration precedence
genebot config-status --show-precedence

# Identify conflicting sources
genebot config-status --show-conflicts

# Resolve conflicts by removing duplicate configurations
```

## Testing Your Migration

### 1. Automated Migration Test

```bash
#!/bin/bash
# migration_test.sh

echo "Testing configuration migration..."

# Test configuration discovery
echo "1. Testing configuration discovery..."
genebot config-status || exit 1

# Test configuration validation
echo "2. Testing configuration validation..."
genebot validate || exit 1

# Test bot startup (dry run)
echo "3. Testing bot startup..."
genebot start --dry-run || exit 1

# Test CLI commands
echo "4. Testing CLI commands..."
genebot list-strategies || exit 1

echo "Migration test completed successfully!"
```

### 2. Manual Migration Verification

```bash
# 1. Verify configuration files are discovered
genebot config-status

# 2. Check that all required configuration is present
genebot validate --verbose

# 3. Test that environment variables work
export GENEBOT_LOG_LEVEL=DEBUG
genebot config-status | grep "DEBUG"

# 4. Test bot startup
python main.py --dry-run

# 5. Test CLI integration
genebot start --dry-run
```

## Rollback Procedure

If migration fails, you can rollback to the previous configuration:

```bash
# 1. Stop the bot
genebot stop

# 2. Restore from backup
BACKUP_DIR="backups/config_backup_YYYYMMDD_HHMMSS"
cp -r $BACKUP_DIR/config/ ./
cp $BACKUP_DIR/.env ./ 2>/dev/null || true

# 3. Revert code changes
git checkout HEAD -- main.py  # If using git

# 4. Test rollback
python main.py --dry-run
```

## Post-Migration Best Practices

### 1. Use CLI for Configuration Management

```bash
# Always use CLI for configuration changes
genebot config-update --strategy rsi --parameter period=21
genebot validate
```

### 2. Monitor Configuration Status

```bash
# Add to monitoring scripts
genebot config-status --format json | jq '.validation_status'
```

### 3. Keep Configuration in Version Control

```bash
# Add configuration files to git (excluding .env)
git add config/
echo ".env" >> .gitignore
git commit -m "Migrate to unified configuration system"
```

### 4. Document Custom Configuration

If you use custom configuration locations or overrides, document them:

```bash
# Create documentation
cat > CONFIG_SETUP.md << EOF
# Configuration Setup

## Environment Variables
- GENEBOT_CONFIG_FILE: Custom config file location
- GENEBOT_LOG_LEVEL: Override log level

## Custom Settings
- Production uses config/production_config.yaml
- Staging uses environment variable overrides
EOF
```

## Getting Help

If you encounter issues during migration:

1. **Check the logs**: Look for configuration-related error messages
2. **Use verbose mode**: Run commands with `--verbose` for detailed output
3. **Validate step by step**: Test each part of the configuration separately
4. **Consult troubleshooting guide**: See [Configuration Troubleshooting Guide](CONFIGURATION_TROUBLESHOOTING_GUIDE.md)
5. **Create an issue**: Report migration problems with detailed error messages

## Migration Checklist

- [ ] Backup existing configuration
- [ ] Initialize unified configuration with `genebot init-config`
- [ ] Update code to use `UnifiedConfigLoader` or `EnhancedConfigManager`
- [ ] Remove hardcoded configuration paths
- [ ] Test configuration discovery with `genebot config-status`
- [ ] Validate configuration with `genebot validate`
- [ ] Test bot startup with `genebot start --dry-run`
- [ ] Test CLI commands work correctly
- [ ] Update documentation and deployment scripts
- [ ] Remove deprecated configuration loading code
- [ ] Commit changes to version control

The unified configuration system provides a more robust, maintainable, and user-friendly approach to configuration management. Following this migration guide ensures a smooth transition while maintaining all existing functionality.
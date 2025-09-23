# GeneBot Unified Configuration System Guide

## Overview

GeneBot v1.1.28+ introduces a unified configuration system that eliminates hardcoded configuration paths and provides intelligent configuration discovery. This system ensures consistency between CLI commands and bot runtime, making configuration management seamless and reliable.

## Key Features

- **Intelligent Configuration Discovery**: Automatically finds configuration files in standard locations
- **Unified Loading System**: Same configuration loading mechanism for CLI and bot runtime
- **Configuration Precedence**: Clear hierarchy for configuration sources
- **Status Reporting**: Visibility into which configuration files are being used
- **Migration Support**: Smooth transition from hardcoded configurations

## Configuration Discovery Process

The unified configuration system searches for configuration files in the following order:

### 1. CLI-Generated Paths (Highest Priority)
- `config/trading_bot_config.yaml` - Main bot configuration
- `config/accounts.yaml` - Exchange and broker accounts
- `.env` - Environment variables and API keys

### 2. Environment Variable Overrides
- `GENEBOT_CONFIG_FILE` - Override main config file path
- `GENEBOT_ACCOUNTS_FILE` - Override accounts config file path
- `GENEBOT_ENV_FILE` - Override environment file path

### 3. Current Directory
- `./trading_bot_config.yaml`
- `./accounts.yaml`
- `./.env`

### 4. Default Locations (Lowest Priority)
- `~/.genebot/config/trading_bot_config.yaml`
- `~/.genebot/config/accounts.yaml`
- `~/.genebot/.env`

## Configuration Precedence

When multiple configuration sources are found, they are merged with the following precedence (highest to lowest):

1. **Environment Variables** - Direct environment variable overrides
2. **CLI-Generated Files** - Files created by `genebot init-config`
3. **User-Specified Files** - Files specified via environment variables
4. **Default Configuration** - Built-in default values

## Getting Started

### 1. Initialize Configuration

The recommended way to set up configuration is using the CLI:

```bash
# Create default configuration files
genebot init-config

# Create production configuration
genebot init-config --template production

# Overwrite existing files
genebot init-config --overwrite
```

This creates configuration files in the standard CLI-generated locations that will be automatically discovered by the bot.

### 2. Verify Configuration Discovery

Check which configuration files the system will use:

```bash
# Show configuration status
genebot config-status

# Validate configuration
genebot validate

# Show configuration discovery details
genebot config-status --verbose
```

### 3. Start the Bot

The bot will automatically use the discovered configuration:

```bash
# Start with discovered configuration
genebot start

# Or using the main script
python main.py
```

## Configuration Status and Reporting

### Configuration Status Command

```bash
# Basic status
genebot config-status

# Detailed status with discovery information
genebot config-status --verbose

# JSON output for scripting
genebot config-status --format json
```

Example output:
```
Configuration Status Report
==========================

✅ Main Configuration: config/trading_bot_config.yaml
   Source: CLI-generated
   Last Modified: 2024-01-15 10:30:00
   Status: Valid

✅ Accounts Configuration: config/accounts.yaml
   Source: CLI-generated
   Last Modified: 2024-01-15 10:30:00
   Status: Valid

✅ Environment File: .env
   Source: CLI-generated
   Last Modified: 2024-01-15 10:30:00
   Status: Valid

Configuration Sources:
- CLI-generated files: 3 found
- Environment overrides: 0 active
- User-specified files: 0 found
- Default locations: 0 used

Validation: ✅ All configurations valid
```

### Bot Startup Logging

When the bot starts, it logs which configuration files are being used:

```
2024-01-15 10:35:00 [INFO] Configuration Discovery: Found 3 configuration sources
2024-01-15 10:35:00 [INFO] Main Config: config/trading_bot_config.yaml (CLI-generated)
2024-01-15 10:35:00 [INFO] Accounts Config: config/accounts.yaml (CLI-generated)
2024-01-15 10:35:00 [INFO] Environment File: .env (CLI-generated)
2024-01-15 10:35:00 [INFO] Configuration validation: PASSED
2024-01-15 10:35:00 [INFO] Bot starting with unified configuration system
```

## Environment Variable Overrides

You can override configuration file locations using environment variables:

```bash
# Override main configuration file
export GENEBOT_CONFIG_FILE="/path/to/custom/config.yaml"

# Override accounts configuration
export GENEBOT_ACCOUNTS_FILE="/path/to/custom/accounts.yaml"

# Override environment file
export GENEBOT_ENV_FILE="/path/to/custom/.env"

# Start bot with overrides
genebot start
```

## Configuration Validation

The unified system uses the same validation rules as the CLI:

```bash
# Validate all configuration
genebot validate

# Validate with detailed output
genebot validate --verbose

# Validate specific configuration file
genebot validate --config config/trading_bot_config.yaml
```

## Hot Configuration Reloading

The unified system supports hot reloading of configuration changes:

```python
# Enable hot reload in your bot configuration
config:
  hot_reload:
    enabled: true
    check_interval: 60  # Check every 60 seconds
    auto_restart_strategies: true
```

When configuration files change:
1. System detects the change
2. Validates new configuration
3. Applies changes without full restart (where possible)
4. Logs configuration updates

## Advanced Usage

### Custom Configuration Locations

You can specify custom configuration locations programmatically:

```python
from config.unified_loader import UnifiedConfigLoader

# Create loader with custom search paths
loader = UnifiedConfigLoader(search_paths=[
    "/custom/config/path",
    "/another/config/location"
])

# Load configuration
config = loader.load_configuration()

# Get configuration status
status = loader.get_configuration_status()
```

### Configuration Merging

When multiple configuration sources are found, they are intelligently merged:

```python
# Example: CLI config has basic settings
# config/trading_bot_config.yaml
strategies:
  rsi:
    enabled: true
    period: 14

# Environment variables provide overrides
export GENEBOT_STRATEGY_RSI_PERIOD=21

# Final merged configuration
strategies:
  rsi:
    enabled: true
    period: 21  # Overridden by environment variable
```

### Configuration Validation Hooks

You can add custom validation hooks:

```python
from config.unified_loader import UnifiedConfigLoader

def custom_validator(config):
    """Custom configuration validation"""
    if config.get('risk_management', {}).get('max_risk', 0) > 0.1:
        raise ValueError("Maximum risk cannot exceed 10%")
    return True

loader = UnifiedConfigLoader()
loader.add_validator(custom_validator)
```

## Integration with Existing Code

### Updating Bot Code

If you have existing bot code that uses hardcoded configuration paths, update it to use the unified loader:

```python
# Old approach (deprecated)
import yaml
with open('config/multi_market_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# New approach (recommended)
from config.unified_loader import UnifiedConfigLoader

loader = UnifiedConfigLoader()
config = loader.load_configuration()
```

### CLI Integration

The CLI automatically uses the unified configuration system:

```python
# CLI commands automatically discover configuration
from genebot.cli.utils.config_manager import ConfigManager

config_manager = ConfigManager()
# Automatically uses unified discovery
config = config_manager.load_config()
```

## Best Practices

### 1. Use CLI for Configuration Management

Always use the CLI for creating and managing configuration:

```bash
# Create initial configuration
genebot init-config

# Update configuration
genebot config-update

# Validate changes
genebot validate
```

### 2. Keep Configuration in Standard Locations

Place configuration files in CLI-generated locations for automatic discovery:
- `config/trading_bot_config.yaml`
- `config/accounts.yaml`
- `.env`

### 3. Use Environment Variables for Overrides

Use environment variables for temporary overrides or environment-specific settings:

```bash
# Temporary override for testing
export GENEBOT_CONFIG_FILE="test_config.yaml"
genebot start

# Production environment override
export GENEBOT_LOG_LEVEL="WARNING"
```

### 4. Validate Configuration Regularly

Always validate configuration after changes:

```bash
# After making changes
genebot validate

# Before starting bot
genebot config-status
```

### 5. Monitor Configuration Status

Regularly check configuration status to ensure everything is working correctly:

```bash
# Daily configuration check
genebot config-status --verbose

# Include in monitoring scripts
genebot config-status --format json | jq '.validation_status'
```

## Troubleshooting

See the [Configuration Troubleshooting Guide](CONFIGURATION_TROUBLESHOOTING_GUIDE.md) for detailed troubleshooting information.

## Migration Guide

See the [Configuration Migration Guide](CONFIGURATION_MIGRATION_GUIDE.md) for detailed migration instructions from older configuration systems.
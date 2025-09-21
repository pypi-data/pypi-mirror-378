# GeneBot CLI Migration Guide

## Overview

This guide helps you migrate from the old GeneBot CLI implementation to the new refactored version. The new CLI provides enhanced functionality, better error handling, real data integration, and improved user experience.

## Table of Contents

1. [What's Changed](#whats-changed)
2. [Breaking Changes](#breaking-changes)
3. [Migration Steps](#migration-steps)
4. [Command Mapping](#command-mapping)
5. [Configuration Migration](#configuration-migration)
6. [Feature Comparison](#feature-comparison)
7. [Troubleshooting Migration Issues](#troubleshooting-migration-issues)
8. [Rollback Procedures](#rollback-procedures)

## What's Changed

### Major Improvements

1. **Real Data Integration**
   - All commands now work with actual configuration files, databases, and live processes
   - No more mock data - everything connects to real systems
   - Actual API connectivity testing for account validation

2. **Modular Architecture**
   - Commands organized into logical modules
   - Shared utilities for consistent behavior
   - Better code organization and maintainability

3. **Enhanced Error Handling**
   - Consistent error messages with actionable guidance
   - Specific troubleshooting suggestions
   - Comprehensive error recovery procedures

4. **Process Management**
   - Real bot process lifecycle management
   - PID file tracking and health monitoring
   - Graceful shutdown and restart capabilities

5. **Security Enhancements**
   - Secure credential handling
   - File permission validation
   - Security scanning and audit capabilities

6. **Advanced Features**
   - Multi-instance support
   - Real-time monitoring
   - Comprehensive analytics and reporting
   - Interactive help system

### New Command Structure

The CLI now uses a more organized command structure:

```
Old CLI (genebot/cli.py)     →     New CLI (genebot/cli/*)
├── Monolithic file          →     ├── main.py (entry point)
├── Mock data                →     ├── commands/ (command modules)
├── Basic error handling     →     ├── utils/ (shared utilities)
└── Limited functionality    →     └── Enhanced features
```

## Breaking Changes

### 1. Entry Point Changes

**Old Way:**
```bash
python genebot/cli.py command
python scripts/trading_bot_cli.py command
```

**New Way:**
```bash
genebot command
# or if installed in development mode:
python -m genebot.cli command
```

### 2. Command Name Changes

Some commands have been renamed for consistency:

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `list` | `list-accounts` | More explicit naming |
| `validate` | `validate-accounts` | More explicit naming |
| `full-status` | `comprehensive-status` | Clearer naming |

### 3. Option Changes

Some command options have changed:

| Old Option | New Option | Notes |
|------------|------------|-------|
| `--type` (for accounts) | `--exchange` / `--broker` | More specific |
| `--sandbox-mode` | `--sandbox` | Shorter option |
| `--output-format` | `--format` | Shorter option |

### 4. Configuration File Changes

**Old Structure:**
```yaml
# Single accounts.yaml with mixed structure
accounts:
  crypto:
    - name: binance
      type: crypto
  forex:
    - name: oanda
      type: forex
```

**New Structure:**
```yaml
# Organized by account type
crypto_exchanges:
  binance:
    name: binance
    exchange_type: binance
    # ... other fields

forex_brokers:
  oanda:
    name: oanda
    broker_type: oanda
    # ... other fields
```

### 5. Environment Variable Changes

**Old Variables:**
```bash
TRADING_BOT_CONFIG_PATH=/path/to/config
TRADING_BOT_LOG_LEVEL=INFO
```

**New Variables:**
```bash
GENEBOT_CONFIG_PATH=/path/to/config
GENEBOT_LOG_LEVEL=INFO
```

## Migration Steps

### Step 1: Backup Current Configuration

```bash
# Create backup directory
mkdir -p backups/pre-migration-$(date +%Y%m%d)

# Backup existing configuration
cp -r config/ backups/pre-migration-$(date +%Y%m%d)/
cp .env backups/pre-migration-$(date +%Y%m%d)/ 2>/dev/null || true

# Backup any custom scripts
cp scripts/trading_bot_cli.py backups/pre-migration-$(date +%Y%m%d)/ 2>/dev/null || true
```

### Step 2: Install New CLI

```bash
# If using pip installation
pip install --upgrade genebot

# If using development installation
pip install -e .

# Verify installation
genebot --version
```

### Step 3: Migrate Configuration

#### Automatic Migration

The new CLI includes automatic migration tools:

```bash
# Run configuration migration
genebot config-migrate --from-old-format

# Validate migrated configuration
genebot validate-config --strict
```

#### Manual Migration

If automatic migration fails, migrate manually:

1. **Create new configuration structure:**
   ```bash
   genebot init-config --template minimal
   ```

2. **Migrate account configurations:**
   ```bash
   # For each old account, add using new CLI
   genebot add-crypto --name binance --exchange binance \
     --api-key $BINANCE_KEY --api-secret $BINANCE_SECRET
   
   genebot add-forex --name oanda --broker oanda \
     --api-key $OANDA_KEY --account-id $OANDA_ACCOUNT
   ```

3. **Update environment variables:**
   ```bash
   # Update .env file with new variable names
   sed -i 's/TRADING_BOT_/GENEBOT_/g' .env
   ```

### Step 4: Validate Migration

```bash
# Comprehensive system validation
genebot system-validate --verbose

# Validate all accounts
genebot validate-accounts --detailed

# Test basic functionality
genebot status
genebot list-accounts
```

### Step 5: Update Scripts and Automation

Update any scripts or automation that use the old CLI:

**Old Script:**
```bash
#!/bin/bash
python scripts/trading_bot_cli.py validate
python scripts/trading_bot_cli.py start
```

**New Script:**
```bash
#!/bin/bash
genebot validate-accounts
genebot start
```

### Step 6: Test New Features

```bash
# Test new monitoring features
genebot monitor --refresh 10

# Test new reporting features
genebot report --type performance

# Test new analytics features
genebot analytics --type risk
```

## Command Mapping

### Account Management Commands

| Old Command | New Command | Changes |
|-------------|-------------|---------|
| `python scripts/trading_bot_cli.py add-crypto` | `genebot add-crypto` | Entry point change |
| `python scripts/trading_bot_cli.py add-forex` | `genebot add-forex` | Entry point change |
| `python scripts/trading_bot_cli.py list` | `genebot list-accounts` | Command name change |
| `python scripts/trading_bot_cli.py validate` | `genebot validate-accounts` | Command name change |
| `python scripts/trading_bot_cli.py remove-account` | `genebot remove-account` | Entry point change |
| `python scripts/trading_bot_cli.py enable-account` | `genebot enable-account` | Entry point change |
| `python scripts/trading_bot_cli.py disable-account` | `genebot disable-account` | Entry point change |

### Bot Control Commands

| Old Command | New Command | Changes |
|-------------|-------------|---------|
| `python scripts/trading_bot_cli.py start` | `genebot start` | Entry point change, real process management |
| `python scripts/trading_bot_cli.py stop` | `genebot stop` | Entry point change, graceful shutdown |
| `python scripts/trading_bot_cli.py status` | `genebot status` | Entry point change, real status checking |
| N/A | `genebot restart` | New command |
| N/A | `genebot start-instance` | New multi-instance support |
| N/A | `genebot list-instances` | New multi-instance support |

### Monitoring and Reporting Commands

| Old Command | New Command | Changes |
|-------------|-------------|---------|
| `python scripts/trading_bot_cli.py report` | `genebot report` | Entry point change, real data |
| N/A | `genebot monitor` | New real-time monitoring |
| N/A | `genebot trades` | New trade history display |
| N/A | `genebot analytics` | New analytics features |
| N/A | `genebot close-all-orders` | New order management |

### Configuration Commands

| Old Command | New Command | Changes |
|-------------|-------------|---------|
| N/A | `genebot init-config` | New configuration initialization |
| N/A | `genebot config-help` | New configuration help |
| N/A | `genebot validate-config` | New configuration validation |
| N/A | `genebot system-validate` | New system validation |

## Configuration Migration

### Account Configuration Migration

**Old Format (config/accounts.yaml):**
```yaml
accounts:
  crypto:
    - name: binance
      type: crypto
      exchange_type: binance
      api_key: "key"
      api_secret: "secret"
      sandbox: true
      enabled: true
  forex:
    - name: oanda
      type: forex
      broker_type: oanda
      api_key: "key"
      account_id: "account"
      sandbox: true
      enabled: true
```

**New Format (config/accounts.yaml):**
```yaml
crypto_exchanges:
  binance:
    name: binance
    exchange_type: binance
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true
    enabled: true
    rate_limit: 1200
    timeout: 30

forex_brokers:
  oanda:
    name: oanda
    broker_type: oanda
    api_key: "${OANDA_API_KEY}"
    account_id: "${OANDA_ACCOUNT_ID}"
    sandbox: true
    enabled: true
    timeout: 30
```

### Environment Variable Migration

**Old .env:**
```bash
TRADING_BOT_CONFIG_PATH=/path/to/config
TRADING_BOT_LOG_LEVEL=INFO
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

**New .env:**
```bash
GENEBOT_CONFIG_PATH=/path/to/config
GENEBOT_LOG_LEVEL=INFO
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

### Migration Script

Use this script to automate configuration migration:

```bash
#!/bin/bash
# migrate_config.sh

echo "Starting GeneBot CLI configuration migration..."

# Backup existing configuration
BACKUP_DIR="backups/migration-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r config/ "$BACKUP_DIR/" 2>/dev/null || true
cp .env "$BACKUP_DIR/" 2>/dev/null || true

echo "Configuration backed up to $BACKUP_DIR"

# Run automatic migration
echo "Running automatic configuration migration..."
genebot config-migrate --from-old-format

# Update environment variables
if [ -f .env ]; then
    echo "Updating environment variables..."
    sed -i.bak 's/TRADING_BOT_/GENEBOT_/g' .env
fi

# Validate migrated configuration
echo "Validating migrated configuration..."
if genebot validate-config --strict; then
    echo "✅ Configuration migration successful!"
else
    echo "❌ Configuration migration failed. Check errors above."
    echo "Original configuration backed up to $BACKUP_DIR"
    exit 1
fi

# Validate accounts
echo "Validating account configurations..."
if genebot validate-accounts; then
    echo "✅ Account validation successful!"
else
    echo "⚠️  Some account validations failed. Check configurations."
fi

echo "Migration complete! Run 'genebot system-validate' for full system check."
```

## Feature Comparison

### Old CLI Features

| Feature | Status | Notes |
|---------|--------|-------|
| Add crypto accounts | ✅ Migrated | Same functionality, better validation |
| Add forex accounts | ✅ Migrated | Same functionality, better validation |
| List accounts | ✅ Migrated | Enhanced display format |
| Validate accounts | ✅ Enhanced | Now tests real API connectivity |
| Start/stop bot | ✅ Enhanced | Real process management |
| Generate reports | ✅ Enhanced | Real data, more formats |
| Basic error handling | ✅ Enhanced | Comprehensive error handling |

### New CLI Features

| Feature | Description |
|---------|-------------|
| Real-time monitoring | Live trading activity monitoring |
| Multi-instance support | Run multiple bot instances |
| Advanced analytics | Performance, risk, correlation analysis |
| Security scanning | Credential and configuration security |
| Interactive help | Enhanced help system with examples |
| Configuration templates | Pre-built configuration templates |
| System diagnostics | Comprehensive system health checks |
| Backup/restore | Configuration backup and restore |
| Process health monitoring | Real-time process status and metrics |
| Cross-market analysis | Multi-market trading insights |

## Troubleshooting Migration Issues

### Common Migration Problems

#### 1. Configuration Format Errors

**Problem:** "Invalid configuration format after migration"

**Solution:**
```bash
# Restore from backup and try manual migration
cp backups/pre-migration-*/config/accounts.yaml config/
genebot init-config --template minimal
# Manually add accounts using genebot add-crypto/add-forex
```

#### 2. Environment Variable Issues

**Problem:** "Environment variables not found"

**Solution:**
```bash
# Check environment variable names
grep -E "TRADING_BOT_|GENEBOT_" .env

# Update variable names
sed -i 's/TRADING_BOT_/GENEBOT_/g' .env

# Reload environment
source .env
```

#### 3. Account Validation Failures

**Problem:** "Account validation fails after migration"

**Solution:**
```bash
# Check account configuration
genebot validate-accounts --account binance --detailed

# Fix common issues
genebot validate-accounts --fix-issues

# Re-add account if needed
genebot remove-account binance crypto
genebot add-crypto --name binance --exchange binance
```

#### 4. Process Management Issues

**Problem:** "Bot won't start with new CLI"

**Solution:**
```bash
# Check system status
genebot system-validate

# Clean up old processes
pkill -f trading_bot
rm -f *.pid

# Try starting again
genebot start --verbose
```

#### 5. Permission Issues

**Problem:** "Permission denied errors"

**Solution:**
```bash
# Fix file permissions
chmod 600 config/accounts.yaml
chmod 600 .env
chmod 755 logs/

# Check directory ownership
ls -la config/
```

### Migration Validation Checklist

Use this checklist to ensure successful migration:

- [ ] Configuration files migrated successfully
- [ ] Environment variables updated
- [ ] All accounts validate successfully
- [ ] Bot starts and stops correctly
- [ ] Real-time monitoring works
- [ ] Reports generate with real data
- [ ] No permission issues
- [ ] All custom scripts updated
- [ ] Backup created and verified

### Getting Help During Migration

1. **Run System Validation**
   ```bash
   genebot system-validate --verbose
   ```

2. **Check Migration Status**
   ```bash
   genebot config-migrate --status
   ```

3. **Generate Diagnostic Report**
   ```bash
   genebot diagnostics --export migration_diagnostics.json
   ```

4. **View Migration Logs**
   ```bash
   tail -f logs/cli.log
   ```

## Rollback Procedures

If migration fails or causes issues, you can rollback:

### Quick Rollback

```bash
# Restore configuration from backup
BACKUP_DIR="backups/pre-migration-$(date +%Y%m%d)"
cp -r "$BACKUP_DIR/config/" ./
cp "$BACKUP_DIR/.env" ./ 2>/dev/null || true

# Use old CLI temporarily
python scripts/trading_bot_cli.py status
```

### Complete Rollback

```bash
#!/bin/bash
# rollback.sh

echo "Rolling back GeneBot CLI migration..."

# Find latest backup
BACKUP_DIR=$(ls -1d backups/pre-migration-* | tail -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "No backup found for rollback!"
    exit 1
fi

echo "Restoring from backup: $BACKUP_DIR"

# Restore configuration
cp -r "$BACKUP_DIR/config/" ./
cp "$BACKUP_DIR/.env" ./ 2>/dev/null || true

# Restore old CLI if available
if [ -f "$BACKUP_DIR/trading_bot_cli.py" ]; then
    cp "$BACKUP_DIR/trading_bot_cli.py" scripts/
fi

echo "Rollback complete. You can now use the old CLI:"
echo "python scripts/trading_bot_cli.py --help"
```

### Partial Rollback

You can also rollback specific components:

```bash
# Rollback only configuration
cp backups/pre-migration-*/config/accounts.yaml config/

# Rollback only environment variables
cp backups/pre-migration-*/.env ./

# Use old CLI for specific commands
python scripts/trading_bot_cli.py validate
```

## Post-Migration Best Practices

### 1. Regular Validation

```bash
# Daily system validation
genebot system-validate

# Weekly account validation
genebot validate-accounts --detailed
```

### 2. Monitor New Features

```bash
# Use real-time monitoring
genebot monitor --refresh 30

# Generate regular reports
genebot report --type performance --start-date $(date -d '7 days ago' +%Y-%m-%d)
```

### 3. Security Maintenance

```bash
# Regular security scans
genebot security --scan

# Rotate credentials periodically
genebot security --rotate-keys
```

### 4. Backup Automation

```bash
# Automated daily backups
echo "0 2 * * * genebot backup-config --destination backups/daily" | crontab -
```

### 5. Update Documentation

Update any internal documentation or runbooks to reflect the new CLI commands and procedures.

## Conclusion

The new GeneBot CLI provides significant improvements in functionality, reliability, and user experience. While migration requires some effort, the enhanced features and real data integration make it worthwhile.

Key benefits after migration:
- Real data integration instead of mock data
- Better error handling and troubleshooting
- Enhanced security and credential management
- Advanced monitoring and analytics
- Multi-instance support
- Comprehensive system validation

If you encounter issues during migration, use the troubleshooting section and rollback procedures as needed. The new CLI is designed to be more robust and user-friendly than the previous version.
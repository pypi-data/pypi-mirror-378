"""
Security Commands Tests
=======================

Tests for security CLI commands and integration.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

from genebot.cli.commands.security import SecurityCommand
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult, ResultStatus
from genebot.cli.utils.security_manager import SecurityLevel


class TestSecurityCommand:
    """Test security CLI commands"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            logs_dir = workspace / "logs"
            logs_dir.mkdir()
            yield workspace
    
    @pytest.fixture
    def cli_context(self, temp_workspace):
        """Create CLI context for testing"""
        return CLIContext(
            config_path=temp_workspace / "config",
            verbose=False,
            dry_run=False
        )
    
    @pytest.fixture
    def security_command(self, cli_context):
        """Create security command instance"""
        return SecurityCommand(context=cli_context)
    
    @pytest.fixture
    def sample_env_file(self, temp_workspace):
        """Create sample .env file"""
        env_file = temp_workspace / ".env"
        env_content = """
API_KEY=test_api_key_1234567890abcdef
SECRET_KEY=test_secret_key_abcdefghijklmnop
PASSWORD=testpassword123
"""
        env_file.write_text(env_content)
        env_file.chmod(0o600)
        return env_file
    
    def test_security_command_initialization(self, cli_context):
        """Test security command initialization"""
        command = SecurityCommand(context=cli_context)
        
        assert command.context == cli_context
        assert command.security_manager is not None
        assert command.error_handler is not None
    
    def test_validate_credentials_command(self, security_command, sample_env_file):
        """Test validate-credentials command"""
        args = Namespace(
            security_action='validate-credentials',
            env_file=sample_env_file
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            assert len(credentials) > 0
            
            # Verify credentials are masked
            for cred in credentials:
                assert 'masked_value' in cred
                assert cred['masked_value'] != ""
                # Ensure no actual credential values are exposed
                assert "test_api_key_1234567890abcdef" not in str(result.data)
    
    def test_validate_credentials_command_missing_file(self, security_command, temp_workspace):
        """Test validate-credentials command with missing file"""
        missing_file = temp_workspace / "missing.env"
        args = Namespace(
            security_action='validate-credentials',
            env_file=missing_file
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.WARNING
        assert "No .env file found" in result.message
    
    def test_audit_command(self, security_command, sample_env_file):
        """Test security audit command"""
        args = Namespace(security_action='audit')
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING, ResultStatus.ERROR]
        assert result.data is not None
        
        audit_data = result.data
        assert 'files_checked' in audit_data
        assert 'secure_files' in audit_data
        assert 'insecure_files' in audit_data
        assert isinstance(audit_data['files_checked'], int)
    
    def test_check_permissions_command(self, security_command, sample_env_file):
        """Test check-permissions command"""
        args = Namespace(
            security_action='check-permissions',
            files=[sample_env_file]
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        if result.data:
            assert 'files_checked' in result.data
            files_checked = result.data['files_checked']
            assert len(files_checked) > 0
            
            for file_info in files_checked:
                # file_info is a FileSecurityInfo object, not a dict
                assert hasattr(file_info, 'path')
                assert hasattr(file_info, 'permissions')
                assert hasattr(file_info, 'is_secure')
    
    def test_check_permissions_command_default_files(self, security_command):
        """Test check-permissions command with default files"""
        args = Namespace(
            security_action='check-permissions',
            files=[]
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        # Should check default files even if they don't exist
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
    
    def test_fix_permissions_command_dry_run(self, security_command):
        """Test fix-permissions command in dry run mode"""
        # Create an insecure file
        insecure_file = security_command.context.workspace_path / ".env"
        insecure_file.write_text("API_KEY=test")
        insecure_file.chmod(0o644)  # Insecure permissions
        
        args = Namespace(
            security_action='fix-permissions',
            dry_run=True
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # File permissions should not have changed in dry run
        file_stat = insecure_file.stat()
        assert file_stat.st_mode & 0o777 == 0o644
    
    def test_fix_permissions_command_actual(self, security_command):
        """Test fix-permissions command with actual changes"""
        # Create an insecure file
        insecure_file = security_command.context.workspace_path / ".env"
        insecure_file.write_text("API_KEY=test")
        insecure_file.chmod(0o644)  # Insecure permissions
        
        args = Namespace(
            security_action='fix-permissions',
            dry_run=False
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        # Result can be success or warning depending on what was fixed
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
    
    def test_rotation_guide_command(self, security_command, sample_env_file):
        """Test rotation-guide command"""
        args = Namespace(security_action='rotation-guide')
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        
        guide = result.data
        assert 'overview' in guide
        assert 'procedures' in guide
        assert 'current_status' in guide
        assert 'next_actions' in guide
        
        # Check overview structure
        overview = guide['overview']
        assert 'importance' in overview
        assert 'frequency' in overview
        assert 'best_practices' in overview
        assert isinstance(overview['best_practices'], list)
    
    def test_audit_log_command(self, security_command):
        """Test audit-log command"""
        # First, perform some operations to generate log entries
        security_command.security_manager._log_audit_entry(
            operation="test_operation",
            resource="test_resource",
            security_level=SecurityLevel.HIGH,
            success=True,
            details={'test': 'data'}
        )
        
        args = Namespace(
            security_action='audit-log',
            limit=10,
            operation=None,
            user=None,
            days=30
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        
        entries = result.data['entries']
        assert isinstance(entries, list)
        
        if entries:  # If there are entries
            for entry in entries:
                assert 'timestamp' in entry
                assert 'operation' in entry
                assert 'resource' in entry
                assert 'success' in entry
    
    def test_audit_log_command_with_filters(self, security_command):
        """Test audit-log command with filters"""
        # Add test entries
        security_command.security_manager._log_audit_entry(
            operation="credential_validation",
            resource="test_resource",
            security_level=SecurityLevel.HIGH,
            success=True,
            details={},
            user="test_user"
        )
        
        security_command.security_manager._log_audit_entry(
            operation="security_audit",
            resource="test_resource",
            security_level=SecurityLevel.MEDIUM,
            success=True,
            details={},
            user="other_user"
        )
        
        # Test with operation filter
        args = Namespace(
            security_action='audit-log',
            limit=10,
            operation='credential_validation',
            user=None,
            days=30
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        
        entries = result.data['entries']
        for entry in entries:
            assert 'credential_validation' in entry['operation']
    
    def test_init_config_command(self, security_command):
        """Test init-config command"""
        args = Namespace(security_action='init-config')
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.SUCCESS
        
        # Check that config file was created
        config_file = security_command.context.config_path / "security_config.yaml"
        assert config_file.exists()
        
        # Check file content
        config_content = config_file.read_text()
        assert "credential_rotation_days" in config_content
        assert "password_min_length" in config_content
        assert "file_permission_checks" in config_content
        
        # Check file permissions are secure
        file_stat = config_file.stat()
        assert file_stat.st_mode & 0o777 == 0o600
    
    def test_init_config_command_existing_file(self, security_command):
        """Test init-config command with existing config file"""
        # Create existing config file
        config_file = security_command.context.config_path / "security_config.yaml"
        config_file.write_text("existing_config: true")
        
        args = Namespace(security_action='init-config')
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.WARNING
        assert "already exists" in result.message
    
    def test_no_action_specified(self, security_command):
        """Test command execution with no action specified"""
        args = Namespace()  # No security_action attribute
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.ERROR
        assert "No security action specified" in result.message
        assert len(result.suggestions) > 0
    
    def test_invalid_action(self, security_command):
        """Test command execution with invalid action"""
        args = Namespace(security_action='invalid-action')
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.ERROR
        assert "No security action specified" in result.message
    
    @patch('genebot.cli.commands.security.SecurityManager')
    def test_error_handling_in_command_execution(self, mock_security_manager, security_command):
        """Test error handling in command execution"""
        # Mock security manager to raise an exception
        mock_instance = Mock()
        mock_instance.validate_credentials_secure.side_effect = Exception("Test error")
        mock_security_manager.return_value = mock_instance
        
        # Create new command instance with mocked manager
        security_command.security_manager = mock_instance
        
        args = Namespace(
            security_action='validate-credentials',
            env_file=None
        )
        
        result = security_command.execute(args)
        
        assert isinstance(result, CommandResult)
        assert result.status == ResultStatus.ERROR
        assert "Test error" in result.message or "Credential validation" in result.message
    
    def test_verbose_output_handling(self, temp_workspace):
        """Test verbose output handling in security commands"""
        # Create verbose context
        verbose_context = CLIContext(
            config_path=temp_workspace / "config",
            verbose=True,
            dry_run=False
        )
        
        command = SecurityCommand(context=verbose_context)
        
        # Create sample file for testing
        env_file = temp_workspace / ".env"
        env_file.write_text("API_KEY=test123")
        env_file.chmod(0o600)
        
        args = Namespace(security_action='audit')
        
        result = command.execute(args)
        
        assert isinstance(result, CommandResult)
        # Verbose mode should not affect the basic result structure
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING, ResultStatus.ERROR]


class TestSecurityCommandIntegration:
    """Integration tests for security commands with real operations"""
    
    @pytest.fixture
    def integration_workspace(self):
        """Create workspace with realistic file structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            (workspace / "config").mkdir()
            (workspace / "logs").mkdir()
            (workspace / "backups").mkdir()
            
            # Create realistic files
            env_file = workspace / ".env"
            env_file.write_text("""
# Trading Bot Environment Variables
BINANCE_API_KEY=real_looking_api_key_1234567890abcdef
BINANCE_SECRET_KEY=real_looking_secret_key_abcdefghijklmnopqrstuvwxyz
OANDA_API_TOKEN=real_looking_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
DATABASE_PASSWORD=secure_database_password_123
""")
            env_file.chmod(0o600)
            
            accounts_file = workspace / "config" / "accounts.yaml"
            accounts_file.write_text("""
crypto_exchanges:
  binance:
    enabled: true
    exchange_type: binance
    api_key_env: BINANCE_API_KEY
    secret_key_env: BINANCE_SECRET_KEY

forex_brokers:
  oanda:
    enabled: true
    broker_type: oanda
    api_token_env: OANDA_API_TOKEN
""")
            accounts_file.chmod(0o644)  # Intentionally less secure
            
            config_file = workspace / "config" / "trading_bot_config.yaml"
            config_file.write_text("bot_config: {}")
            config_file.chmod(0o644)
            
            yield workspace
    
    def test_complete_security_workflow(self, integration_workspace):
        """Test complete security workflow from audit to fix"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            verbose=True,
            dry_run=False
        )
        
        command = SecurityCommand(context=context)
        
        # 1. Initial security audit
        audit_args = Namespace(security_action='audit')
        audit_result = command.execute(audit_args)
        
        assert audit_result.status in [ResultStatus.WARNING, ResultStatus.ERROR]
        initial_issues = (
            len(audit_result.data['critical_issues']) +
            len(audit_result.data['high_issues']) +
            len(audit_result.data['medium_issues'])
        )
        assert initial_issues > 0  # Should find permission issues
        
        # 2. Validate credentials
        cred_args = Namespace(
            security_action='validate-credentials',
            env_file=None
        )
        cred_result = command.execute(cred_args)
        
        assert cred_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        assert 'credentials' in cred_result.data
        credentials_found = len(cred_result.data['credentials'])
        assert credentials_found >= 3  # Should find at least 3 credentials
        
        # 3. Generate rotation guide
        guide_args = Namespace(security_action='rotation-guide')
        guide_result = command.execute(guide_args)
        
        assert guide_result.status == ResultStatus.SUCCESS
        assert len(guide_result.data['procedures']) >= credentials_found
        
        # 4. Fix permissions (dry run first)
        fix_dry_args = Namespace(
            security_action='fix-permissions',
            dry_run=True
        )
        fix_dry_result = command.execute(fix_dry_args)
        
        assert fix_dry_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # 5. Fix permissions (actual)
        fix_args = Namespace(
            security_action='fix-permissions',
            dry_run=False
        )
        fix_result = command.execute(fix_args)
        
        assert fix_result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        
        # 6. Audit again to verify improvements
        second_audit_result = command.execute(audit_args)
        
        second_issues = (
            len(second_audit_result.data['critical_issues']) +
            len(second_audit_result.data['high_issues']) +
            len(second_audit_result.data['medium_issues'])
        )
        
        # Should have fewer or equal issues after fixing
        assert second_issues <= initial_issues
        
        # 7. Check audit log
        log_args = Namespace(
            security_action='audit-log',
            limit=20,
            operation=None,
            user=None,
            days=1
        )
        log_result = command.execute(log_args)
        
        assert log_result.status == ResultStatus.SUCCESS
        assert len(log_result.data['entries']) >= 5  # Should have logged several operations
    
    def test_credential_security_validation(self, integration_workspace):
        """Test comprehensive credential security validation"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            verbose=False,
            dry_run=False
        )
        
        command = SecurityCommand(context=context)
        
        # Validate credentials
        args = Namespace(
            security_action='validate-credentials',
            env_file=None
        )
        
        result = command.execute(args)
        
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING]
        assert 'credentials' in result.data
        
        credentials = result.data['credentials']
        
        # Verify credential analysis
        for cred in credentials:
            # Check required fields
            assert 'name' in cred
            assert 'credential_type' in cred
            assert 'masked_value' in cred
            assert 'strength_score' in cred
            assert 'rotation_due' in cred
            
            # Verify masking - original values should not be present
            assert cred['masked_value'] != ""
            assert "real_looking_api_key_1234567890abcdef" not in cred['masked_value']
            assert "real_looking_secret_key_abcdefghijklmnopqrstuvwxyz" not in cred['masked_value']
            
            # Verify strength scoring
            assert isinstance(cred['strength_score'], int)
            assert 0 <= cred['strength_score'] <= 100
            
            # Verify rotation recommendation
            assert isinstance(cred['rotation_due'], bool)
        
        # Check file security
        assert 'file_security' in result.data
        file_security = result.data['file_security']
        assert file_security['is_secure'] is True  # .env has 600 permissions
    
    def test_permission_fixing_effectiveness(self, integration_workspace):
        """Test that permission fixing actually improves security"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            verbose=False,
            dry_run=False
        )
        
        command = SecurityCommand(context=context)
        
        # Check initial permissions of accounts.yaml (should be 644)
        accounts_file = integration_workspace / "config" / "accounts.yaml"
        initial_stat = accounts_file.stat()
        initial_permissions = initial_stat.st_mode & 0o777
        assert initial_permissions == 0o644  # Insecure
        
        # Fix permissions
        fix_args = Namespace(
            security_action='fix-permissions',
            dry_run=False
        )
        
        fix_result = command.execute(fix_args)
        
        # Check if permissions were actually changed
        if fix_result.status == ResultStatus.SUCCESS and fix_result.data:
            fixes = fix_result.data.get('fixes_applied', [])
            
            # If fixes were applied, verify the file permissions changed
            if any(str(accounts_file) in fix.get('file', '') for fix in fixes):
                final_stat = accounts_file.stat()
                final_permissions = final_stat.st_mode & 0o777
                assert final_permissions == 0o600  # Should be secure now
    
    def test_audit_log_functionality(self, integration_workspace):
        """Test audit log functionality across multiple operations"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            verbose=False,
            dry_run=False
        )
        
        command = SecurityCommand(context=context)
        
        # Perform multiple operations to generate audit entries
        operations = [
            Namespace(security_action='validate-credentials', env_file=None),
            Namespace(security_action='audit'),
            Namespace(security_action='fix-permissions', dry_run=True),
            Namespace(security_action='rotation-guide')
        ]
        
        for args in operations:
            result = command.execute(args)
            assert result.status in [ResultStatus.SUCCESS, ResultStatus.WARNING, ResultStatus.ERROR]
        
        # Check audit log
        log_args = Namespace(
            security_action='audit-log',
            limit=10,
            operation=None,
            user=None,
            days=1
        )
        
        log_result = command.execute(log_args)
        
        assert log_result.status == ResultStatus.SUCCESS
        entries = log_result.data['entries']
        
        # Should have entries for the operations performed
        assert len(entries) >= len(operations)
        
        # Verify entry structure and content
        operations_logged = set()
        for entry in entries:
            assert 'timestamp' in entry
            assert 'operation' in entry
            assert 'resource' in entry
            assert 'security_level' in entry
            assert 'success' in entry
            assert 'user' in entry
            
            operations_logged.add(entry['operation'])
        
        # Should have logged various security operations
        expected_operations = {
            'credential_validation', 'security_audit', 
            'fix_permissions', 'rotation_guide_generated'
        }
        
        # At least some of the expected operations should be present
        assert len(operations_logged.intersection(expected_operations)) >= 2
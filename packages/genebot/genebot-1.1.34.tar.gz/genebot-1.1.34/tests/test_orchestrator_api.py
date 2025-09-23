"""
Tests for Orchestrator API
==========================

Unit tests for the orchestrator REST API server and client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# Test imports
try:
    from src.orchestration.api_server import OrchestratorAPIServer
    from src.orchestration.api_client import OrchestratorAPIClient, create_client
    API_COMPONENTS_AVAILABLE = True
except ImportError:
    API_COMPONENTS_AVAILABLE = False


@unittest.skipUnless(API_COMPONENTS_AVAILABLE, "API components not available")
class TestOrchestratorAPIServer(unittest.TestCase):
    """Test cases for OrchestratorAPIServer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock FastAPI availability
        with patch('src.orchestration.api_server.FASTAPI_AVAILABLE', True):
            with patch('src.orchestration.api_server.FastAPI'):
                self.api_server = OrchestratorAPIServer(host="127.0.0.1", port=8080)
    
    def test_server_initialization(self):
        """Test API server initialization"""
        self.assertEqual(self.api_server.host, "127.0.0.1")
        self.assertEqual(self.api_server.port, 8080)
        self.assertIsNone(self.api_server._orchestrator)
        self.assertIsNone(self.api_server._config_manager)
    
    @patch('src.orchestration.api_server.yaml.safe_load')
    @patch('builtins.open')
    def test_load_orchestrator_config(self, mock_open, mock_yaml_load):
        """Test configuration loading"""
        # Mock configuration data
        mock_config_data = {
            'orchestrator': {
                'allocation': {'method': 'equal_weight'},
                'risk': {'max_portfolio_drawdown': 0.2},
                'monitoring': {'enabled': True}
            }
        }
        mock_yaml_load.return_value = mock_config_data
        
        # Mock OrchestratorConfig
        with patch('src.orchestration.api_server.OrchestratorConfig') as mock_config_class:
            mock_config = Mock()
            mock_config_class.from_dict.return_value = mock_config
            
            # Test loading config
            result = self.api_server._load_orchestrator_config('test_config.yaml')
            
            self.assertIsNotNone(result)
            mock_open.assert_called_once_with('test_config.yaml', 'r')
            mock_config_class.from_dict.assert_called_once_with(mock_config_data['orchestrator'])
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        volatility = self.api_server._calculate_volatility(returns)
        
        self.assertIsInstance(volatility, float)
        self.assertGreater(volatility, 0)
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = [0.01, 0.02, 0.03, 0.01, 0.02]
        sharpe = self.api_server._calculate_sharpe_ratio(returns)
        
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, 0)
    
    def test_calculate_max_drawdown(self):
        """Test maximum drawdown calculation"""
        returns = [0.01, -0.05, 0.02, -0.03, 0.04]
        max_dd = self.api_server._calculate_max_drawdown(returns)
        
        self.assertIsInstance(max_dd, float)
        self.assertGreaterEqual(max_dd, 0)


@unittest.skipUnless(API_COMPONENTS_AVAILABLE, "API components not available")
class TestOrchestratorAPIClient(unittest.TestCase):
    """Test cases for OrchestratorAPIClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('src.orchestration.api_client.REQUESTS_AVAILABLE', True):
            with patch('src.orchestration.api_client.requests.Session'):
                self.api_client = OrchestratorAPIClient(base_url="http://127.0.0.1:8080")
    
    def test_client_initialization(self):
        """Test API client initialization"""
        self.assertEqual(self.api_client.base_url, "http://127.0.0.1:8080")
        self.assertEqual(self.api_client.timeout, 30)
    
    @patch('src.orchestration.api_client.requests.Session')
    def test_make_request_success(self, mock_session_class):
        """Test successful API request"""
        # Mock session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'success': True, 'data': {'test': 'value'}}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client and make request
        with patch('src.orchestration.api_client.REQUESTS_AVAILABLE', True):
            client = OrchestratorAPIClient()
            client.session = mock_session
            
            result = client._make_request('GET', '/test')
            
            self.assertEqual(result, {'success': True, 'data': {'test': 'value'}})
            mock_session.request.assert_called_once()
    
    def test_health_check(self):
        """Test health check method"""
        with patch.object(self.api_client, '_make_request') as mock_request:
            mock_request.return_value = {'status': 'healthy'}
            
            result = self.api_client.health_check()
            
            self.assertEqual(result, {'status': 'healthy'})
            mock_request.assert_called_once_with('GET', '/health')
    
    def test_start_orchestrator(self):
        """Test start orchestrator method"""
        with patch.object(self.api_client, '_make_request') as mock_request:
            mock_request.return_value = {'success': True, 'message': 'Started'}
            
            result = self.api_client.start_orchestrator(
                config_path='test_config.yaml',
                daemon_mode=True,
                strategies=['strategy1', 'strategy2']
            )
            
            self.assertEqual(result, {'success': True, 'message': 'Started'})
            mock_request.assert_called_once_with(
                'POST', 
                '/orchestrator/start',
                json={
                    'config_path': 'test_config.yaml',
                    'daemon_mode': True,
                    'strategies': ['strategy1', 'strategy2']
                }
            )
    
    def test_get_orchestrator_status(self):
        """Test get orchestrator status method"""
        with patch.object(self.api_client, '_make_request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'data': {'status': 'running', 'strategies': {'active': 3}}
            }
            
            result = self.api_client.get_orchestrator_status(verbose=True)
            
            self.assertEqual(result['success'], True)
            self.assertEqual(result['data']['status'], 'running')
            mock_request.assert_called_once_with(
                'GET', 
                '/orchestrator/status',
                params={'verbose': True}
            )
    
    def test_pause_strategy(self):
        """Test pause strategy method"""
        with patch.object(self.api_client, '_make_request') as mock_request:
            mock_request.return_value = {'success': True, 'data': {'action': 'paused'}}
            
            result = self.api_client.pause_strategy('test_strategy')
            
            self.assertEqual(result, {'success': True, 'data': {'action': 'paused'}})
            mock_request.assert_called_once_with(
                'POST',
                '/orchestrator/intervention',
                json={'action': 'pause_strategy', 'strategy': 'test_strategy'}
            )
    
    def test_is_running(self):
        """Test is_running convenience method"""
        with patch.object(self.api_client, 'get_orchestrator_status') as mock_status:
            # Test running case
            mock_status.return_value = {'data': {'status': 'running'}}
            self.assertTrue(self.api_client.is_running())
            
            # Test not running case
            mock_status.return_value = {'data': {'status': 'stopped'}}
            self.assertFalse(self.api_client.is_running())
            
            # Test error case
            mock_status.side_effect = Exception("Connection error")
            self.assertFalse(self.api_client.is_running())
    
    def test_get_strategy_list(self):
        """Test get strategy list convenience method"""
        with patch.object(self.api_client, 'get_orchestrator_status') as mock_status:
            # Test successful case
            mock_status.return_value = {
                'data': {
                    'strategy_details': {
                        'strategy1': {'state': 'active'},
                        'strategy2': {'state': 'paused'}
                    }
                }
            }
            
            result = self.api_client.get_strategy_list()
            self.assertEqual(set(result), {'strategy1', 'strategy2'})
            
            # Test error case
            mock_status.side_effect = Exception("Error")
            result = self.api_client.get_strategy_list()
            self.assertEqual(result, [])


class TestAPIUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    @unittest.skipUnless(API_COMPONENTS_AVAILABLE, "API components not available")
    def test_create_client(self):
        """Test create_client utility function"""
        with patch('src.orchestration.api_client.REQUESTS_AVAILABLE', True):
            with patch('src.orchestration.api_client.requests.Session'):
                client = create_client(base_url="http://test:9000", timeout=60)
                
                self.assertIsInstance(client, OrchestratorAPIClient)
                self.assertEqual(client.base_url, "http://test:9000")
                self.assertEqual(client.timeout, 60)


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API components"""
    
    @unittest.skipUnless(API_COMPONENTS_AVAILABLE, "API components not available")
    def test_api_server_client_compatibility(self):
        """Test that API server and client are compatible"""
        # This test verifies that the API endpoints defined in the server
        # match the methods available in the client
        
        with patch('src.orchestration.api_server.FASTAPI_AVAILABLE', True):
            with patch('src.orchestration.api_server.FastAPI'):
                server = OrchestratorAPIServer()
        
        with patch('src.orchestration.api_client.REQUESTS_AVAILABLE', True):
            with patch('src.orchestration.api_client.requests.Session'):
                client = OrchestratorAPIClient()
        
        # Check that client has methods for all major API operations
        client_methods = [
            'health_check',
            'start_orchestrator',
            'stop_orchestrator',
            'get_orchestrator_status',
            'get_config',
            'update_config',
            'reload_config',
            'get_metrics',
            'get_performance_analytics',
            'pause_strategy',
            'resume_strategy',
            'emergency_stop',
            'force_rebalance',
            'adjust_allocation',
            'get_performance_report',
            'get_audit_report'
        ]
        
        for method_name in client_methods:
            self.assertTrue(hasattr(client, method_name), 
                          f"Client missing method: {method_name}")
            self.assertTrue(callable(getattr(client, method_name)),
                          f"Client method not callable: {method_name}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
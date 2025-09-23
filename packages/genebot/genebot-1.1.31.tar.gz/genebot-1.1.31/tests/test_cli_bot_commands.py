"""
Tests for CLI Bot Commands
==========================

Tests for the bot control commands that use the ProcessManager.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace
import pytest

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from genebot.cli.commands.bot import StartBotCommand, StopBotCommand, RestartBotCommand, StatusCommand
from genebot.cli.context import CLIContext
from genebot.cli.utils.logger import CLILogger
from genebot.cli.utils.error_handler import CLIErrorHandler
from genebot.cli.utils.process_manager import BotStatus, ProcessError


class TestBotCommands:
    """Test cases for bot control commands"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main.py for validation
        main_py = self.temp_dir / "main.py"
        main_py.write_text("print('Mock bot')")
        
        # Create context
        self.context = CLIContext(
            config_path=self.config_dir,
            log_level='INFO',
            dry_run=False,
            verbose=False
        )
        
        # Create logger and error handler
        self.logger = CLILogger('test', 'INFO', None, False)
        self.error_handler = CLIErrorHandler(False)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_status_command_bot_not_running(self):
        """Test status command when bot is not running"""
        cmd = StatusCommand(self.context, self.logger, self.error_handler)
        args = Namespace(detailed=False, json=False)
        
        result = cmd.execute(args)
        
        assert result.success
        assert "Status information displayed" in result.message
        assert result.data['bot_running'] is False
    
    def test_status_command_json_output(self):
        """Test status command with JSON output"""
        cmd = StatusCommand(self.context, self.logger, self.error_handler)
        args = Namespace(detailed=False, json=True)
        
        with patch('builtins.print') as mock_print:
            result = cmd.execute(args)
        
        assert result.success
        assert "JSON format" in result.message
        mock_print.assert_called_once()
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.get_bot_status')
    def test_status_command_bot_running(self, mock_get_status):
        """Test status command when bot is running"""
        from datetime import datetime, timedelta
        
        # Mock running bot status
        mock_status = BotStatus(
            running=True,
            pid=12345,
            uptime=timedelta(hours=2, minutes=15),
            memory_usage=256.0,
            cpu_usage=5.2
        )
        mock_get_status.return_value = mock_status
        
        cmd = StatusCommand(self.context, self.logger, self.error_handler)
        args = Namespace(detailed=False, json=False)
        
        result = cmd.execute(args)
        
        assert result.success
        assert result.data['bot_running'] is True
        assert result.data['pid'] == 12345
        assert "2h 15m" in result.data['uptime']
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.start_bot')
    def test_start_command_success(self, mock_start_bot):
        """Test successful bot start"""
        # Mock successful start
        mock_status = BotStatus(
            running=True,
            pid=12345,
            memory_usage=100.0,
            cpu_usage=2.5
        )
        mock_start_bot.return_value = mock_status
        
        cmd = StartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            config=None,
            strategy=None,
            account=None,
            background=True,
            foreground=False
        )
        
        result = cmd.execute(args)
        
        assert result.success
        assert "started successfully" in result.message
        assert result.data['pid'] == 12345
        mock_start_bot.assert_called_once()
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.start_bot')
    def test_start_command_with_options(self, mock_start_bot):
        """Test bot start with configuration options"""
        mock_status = BotStatus(running=True, pid=12345)
        mock_start_bot.return_value = mock_status
        
        cmd = StartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            config='test.yaml',
            strategy=['rsi', 'ma'],
            account=['binance'],
            background=True,
            foreground=False
        )
        
        result = cmd.execute(args)
        
        assert result.success
        mock_start_bot.assert_called_once_with(
            config_file='test.yaml',
            strategies=['rsi', 'ma'],
            accounts=['binance'],
            background=True
        )
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.start_bot')
    def test_start_command_foreground_override(self, mock_start_bot):
        """Test that foreground flag overrides background"""
        mock_status = BotStatus(running=True, pid=12345)
        mock_start_bot.return_value = mock_status
        
        cmd = StartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            config=None,
            strategy=None,
            account=None,
            background=True,
            foreground=True  # This should override background
        )
        
        result = cmd.execute(args)
        
        assert result.success
        mock_start_bot.assert_called_once_with(
            config_file=None,
            strategies=None,
            accounts=None,
            background=False  # Should be False due to foreground=True
        )
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.start_bot')
    def test_start_command_process_error(self, mock_start_bot):
        """Test start command with process error"""
        mock_start_bot.side_effect = ProcessError(
            "Bot is already running",
            suggestions=["Use 'genebot stop' first"]
        )
        
        cmd = StartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            config=None,
            strategy=None,
            account=None,
            background=True,
            foreground=False
        )
        
        result = cmd.execute(args)
        
        assert not result.success
        assert "Bot is already running" in result.message
        assert "Use 'genebot stop' first" in result.suggestions
    
    def test_start_command_missing_main_py(self):
        """Test start command when main.py is missing"""
        # Remove main.py
        (self.temp_dir / "main.py").unlink()
        
        cmd = StartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            config=None,
            strategy=None,
            account=None,
            background=True,
            foreground=False
        )
        
        result = cmd.execute(args)
        
        assert not result.success
        assert "main.py not found" in result.message
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.stop_bot')
    @patch('genebot.cli.utils.process_manager.ProcessManager.get_bot_status')
    def test_stop_command_success(self, mock_get_status, mock_stop_bot):
        """Test successful bot stop"""
        # Mock running bot
        mock_get_status.return_value = BotStatus(running=True, pid=12345)
        mock_stop_bot.return_value = BotStatus(running=False)
        
        cmd = StopBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(timeout=60, force=False)
        
        result = cmd.execute(args)
        
        assert result.success
        assert "stopped successfully" in result.message
        mock_stop_bot.assert_called_once_with(timeout=60, force=False)
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.get_bot_status')
    def test_stop_command_not_running(self, mock_get_status):
        """Test stop command when bot is not running"""
        mock_get_status.return_value = BotStatus(running=False)
        
        cmd = StopBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(timeout=60, force=False)
        
        result = cmd.execute(args)
        
        assert result.success
        assert "not running" in result.message
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.stop_bot')
    @patch('genebot.cli.utils.process_manager.ProcessManager.get_bot_status')
    def test_stop_command_force(self, mock_get_status, mock_stop_bot):
        """Test force stop command"""
        mock_get_status.return_value = BotStatus(running=True, pid=12345)
        mock_stop_bot.return_value = BotStatus(running=False)
        
        cmd = StopBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(timeout=30, force=True)
        
        result = cmd.execute(args)
        
        assert result.success
        mock_stop_bot.assert_called_once_with(timeout=30, force=True)
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.restart_bot')
    def test_restart_command_success(self, mock_restart_bot):
        """Test successful bot restart"""
        mock_status = BotStatus(running=True, pid=54321)
        mock_restart_bot.return_value = mock_status
        
        cmd = RestartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(
            timeout=60,
            config='test.yaml',
            strategy=['rsi'],
            account=['binance']
        )
        
        result = cmd.execute(args)
        
        assert result.success
        assert "restarted successfully" in result.message
        assert result.data['pid'] == 54321
        mock_restart_bot.assert_called_once_with(
            timeout=60,
            config_file='test.yaml',
            strategies=['rsi'],
            accounts=['binance']
        )
    
    @patch('genebot.cli.utils.process_manager.ProcessManager.restart_bot')
    def test_restart_command_failure(self, mock_restart_bot):
        """Test restart command failure"""
        mock_restart_bot.side_effect = ProcessError(
            "Failed to restart bot",
            suggestions=["Check system resources"]
        )
        
        cmd = RestartBotCommand(self.context, self.logger, self.error_handler)
        args = Namespace(timeout=60, config=None, strategy=None, account=None)
        
        result = cmd.execute(args)
        
        assert not result.success
        assert "Failed to restart bot" in result.message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"""
Tests for CLI Process Manager
============================

Tests for the ProcessManager class that handles bot process lifecycle management.
"""

import os
import sys
import time
import json
import signal
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
import pytest
import psutil

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from genebot.cli.utils.process_manager import (
    ProcessManager, ProcessInfo, BotStatus, ProcessError, 
    ProcessState, ProcessMetrics, RecoveryConfig, BotInstance
)


class TestProcessManager:
    """Test cases for ProcessManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.process_manager = ProcessManager(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "logs").mkdir(exist_ok=True)
        
        # Create a mock main.py
        main_py = self.temp_dir / "main.py"
        main_py.write_text("""
import time
import sys
import signal

def signal_handler(signum, frame):
    print("Received signal, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("Mock bot started")
while True:
    time.sleep(1)
""")
    
    def teardown_method(self):
        """Cleanup test environment"""
        # Clean up any running processes
        try:
            if self.process_manager.pid_file.exists():
                pid_info = self.process_manager._read_pid_file()
                if pid_info and pid_info.get('pid'):
                    try:
                        process = psutil.Process(pid_info['pid'])
                        process.terminate()
                        process.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        pass
        except Exception:
            pass
        
        # Remove temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test ProcessManager initialization"""
        pm = ProcessManager(self.temp_dir)
        
        assert pm.workspace_path == self.temp_dir
        assert pm.pid_dir == self.temp_dir / "logs"
        assert pm.pid_file == self.temp_dir / "logs" / "genebot.pid"
        assert pm.log_dir == self.temp_dir / "logs"
        
        # Check directories are created
        assert pm.pid_dir.exists()
        assert pm.log_dir.exists()
    
    def test_build_start_command(self):
        """Test command building for bot start"""
        # Basic command
        cmd = self.process_manager._build_start_command()
        assert cmd == [sys.executable, "main.py"]
        
        # With config file
        cmd = self.process_manager._build_start_command(config_file="test.yaml")
        assert cmd == [sys.executable, "main.py", "--config", "test.yaml"]
        
        # With strategies
        cmd = self.process_manager._build_start_command(strategies=["rsi", "ma"])
        assert cmd == [sys.executable, "main.py", "--strategies", "rsi", "ma"]
        
        # With accounts
        cmd = self.process_manager._build_start_command(accounts=["binance", "oanda"])
        assert cmd == [sys.executable, "main.py", "--accounts", "binance", "oanda"]
        
        # With all options
        cmd = self.process_manager._build_start_command(
            config_file="test.yaml",
            strategies=["rsi"],
            accounts=["binance"]
        )
        expected = [sys.executable, "main.py", "--config", "test.yaml", "--strategies", "rsi", "--accounts", "binance"]
        assert cmd == expected
    
    def test_create_and_read_pid_file(self):
        """Test PID file creation and reading"""
        pid = 12345
        command = [sys.executable, "main.py"]
        log_file = self.temp_dir / "test.log"
        
        # Create PID file
        self.process_manager._create_pid_file(pid, command, log_file)
        
        assert self.process_manager.pid_file.exists()
        
        # Read PID file
        pid_info = self.process_manager._read_pid_file()
        
        assert pid_info is not None
        assert pid_info['pid'] == pid
        assert pid_info['command'] == command
        assert pid_info['log_file'] == str(log_file)
        assert 'start_time' in pid_info
        assert pid_info['workspace'] == str(self.temp_dir)
    
    def test_cleanup_pid_file(self):
        """Test PID file cleanup"""
        # Create a PID file
        self.process_manager.pid_file.write_text('{"pid": 12345}')
        assert self.process_manager.pid_file.exists()
        
        # Cleanup
        self.process_manager._cleanup_pid_file()
        assert not self.process_manager.pid_file.exists()
    
    @patch('psutil.Process')
    def test_get_process_info_success(self, mock_process_class):
        """Test getting process information successfully"""
        # Mock process
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process.name.return_value = "python"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.return_value = 5.2
        mock_process.memory_info.return_value = Mock(rss=256 * 1024 * 1024)  # 256 MB
        mock_process.memory_percent.return_value = 10.5
        mock_process.create_time.return_value = time.time() - 3600  # 1 hour ago
        mock_process.cmdline.return_value = [sys.executable, "main.py"]
        
        mock_process_class.return_value = mock_process
        
        # Get process info
        info = self.process_manager._get_process_info(12345)
        
        assert info is not None
        assert info.pid == 12345
        assert info.name == "python"
        assert info.status == "running"
        assert info.cpu_percent == 5.2
        assert info.memory_mb == 256.0
        assert info.memory_percent == 10.5
        assert info.command_line == [sys.executable, "main.py"]
        assert isinstance(info.uptime, timedelta)
    
    @patch('psutil.Process')
    def test_get_process_info_no_such_process(self, mock_process_class):
        """Test getting process info when process doesn't exist"""
        mock_process_class.side_effect = psutil.NoSuchProcess(12345)
        
        info = self.process_manager._get_process_info(12345)
        assert info is None
    
    @patch('psutil.Process')
    def test_get_process_info_access_denied(self, mock_process_class):
        """Test getting process info with access denied"""
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process.name.return_value = "python"
        mock_process.status.return_value = "running"
        mock_process.cpu_percent.side_effect = psutil.AccessDenied()
        mock_process.memory_info.side_effect = psutil.AccessDenied()
        mock_process.memory_percent.side_effect = psutil.AccessDenied()
        mock_process.create_time.return_value = time.time()
        mock_process.cmdline.side_effect = psutil.AccessDenied()
        
        mock_process_class.return_value = mock_process
        
        info = self.process_manager._get_process_info(12345)
        
        assert info is not None
        assert info.cpu_percent == 0.0
        assert info.memory_mb == 0.0
        assert info.memory_percent == 0.0
        assert info.command_line == []
    
    def test_get_bot_status_no_pid_file(self):
        """Test getting bot status when no PID file exists"""
        status = self.process_manager.get_bot_status()
        
        assert not status.running
        assert status.pid is None
        assert status.uptime is None
        assert status.error_message is None
    
    def test_get_bot_status_invalid_pid_file(self):
        """Test getting bot status with invalid PID file"""
        # Create invalid PID file
        self.process_manager.pid_file.write_text("invalid json")
        
        status = self.process_manager.get_bot_status()
        assert not status.running
    
    @patch('genebot.cli.utils.process_manager.ProcessManager._get_process_info')
    def test_get_bot_status_process_not_running(self, mock_get_process_info):
        """Test getting bot status when process is not running"""
        # Create PID file
        pid_info = {
            'pid': 12345,
            'command': [sys.executable, "main.py"],
            'start_time': datetime.now().isoformat()
        }
        with open(self.process_manager.pid_file, 'w') as f:
            json.dump(pid_info, f)
        
        # Mock process not found
        mock_get_process_info.return_value = None
        
        status = self.process_manager.get_bot_status()
        
        assert not status.running
        assert not self.process_manager.pid_file.exists()  # Should be cleaned up
    
    @patch('genebot.cli.utils.process_manager.ProcessManager._get_process_info')
    def test_get_bot_status_running(self, mock_get_process_info):
        """Test getting bot status when bot is running"""
        # Create PID file
        pid_info = {
            'pid': 12345,
            'command': [sys.executable, "main.py"],
            'start_time': datetime.now().isoformat()
        }
        with open(self.process_manager.pid_file, 'w') as f:
            json.dump(pid_info, f)
        
        # Mock process info
        create_time = datetime.now() - timedelta(hours=1)
        mock_process_info = ProcessInfo(
            pid=12345,
            name="python",
            status="running",
            cpu_percent=5.2,
            memory_percent=10.5,
            memory_mb=256.0,
            create_time=create_time,
            uptime=timedelta(hours=1),
            command_line=[sys.executable, "main.py"]
        )
        mock_get_process_info.return_value = mock_process_info
        
        status = self.process_manager.get_bot_status()
        
        assert status.running
        assert status.pid == 12345
        assert status.memory_usage == 256.0
        assert status.cpu_usage == 5.2
        assert status.process_info == mock_process_info
        assert isinstance(status.uptime, timedelta)
    
    def test_monitor_health(self):
        """Test health monitoring"""
        with patch.object(self.process_manager, 'get_bot_status') as mock_status:
            mock_bot_status = BotStatus(
                running=True,
                pid=12345,
                uptime=timedelta(hours=1),
                memory_usage=256.0,
                cpu_usage=5.2
            )
            mock_status.return_value = mock_bot_status
            
            health = self.process_manager.monitor_health()
            
            assert 'timestamp' in health
            assert health['running'] is True
            assert health['healthy'] is True
            assert health['pid'] == 12345
            assert health['memory_mb'] == 256.0
            assert health['cpu_percent'] == 5.2
            assert health['uptime_seconds'] == 3600.0
    
    @patch('subprocess.Popen')
    def test_start_bot_success(self, mock_popen):
        """Test successful bot start"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            mock_process_info = ProcessInfo(
                pid=12345,
                name="python",
                status="running",
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_mb=100.0,
                create_time=datetime.now(),
                uptime=timedelta(seconds=0),
                command_line=[sys.executable, "main.py"]
            )
            mock_get_info.return_value = mock_process_info
            
            status = self.process_manager.start_bot()
            
            assert status.running
            assert status.pid == 12345
            assert self.process_manager.pid_file.exists()
    
    def test_start_bot_already_running(self):
        """Test starting bot when already running"""
        # Create a running default instance
        from genebot.cli.utils.process_manager import BotInstance, ProcessState
        instance = BotInstance(name="default")
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["default"] = instance
        
        with pytest.raises(ProcessError) as exc_info:
            self.process_manager.start_bot()
        
        assert "already running" in str(exc_info.value)
    
    @patch('subprocess.Popen')
    def test_start_bot_process_fails(self, mock_popen):
        """Test bot start when process fails immediately"""
        # Mock process that fails immediately
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = 1  # Exit code 1
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        with pytest.raises(ProcessError) as exc_info:
            self.process_manager.start_bot()
        
        assert "terminated immediately" in str(exc_info.value)
    
    def test_stop_bot_success(self):
        """Test successful bot stop"""
        # Create a running default instance
        from genebot.cli.utils.process_manager import BotInstance, ProcessState
        instance = BotInstance(name="default", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["default"] = instance
        
        with patch.object(self.process_manager, 'stop_bot_instance') as mock_stop_instance:
            mock_stop_instance.return_value = BotStatus(running=False)
            
            status = self.process_manager.stop_bot()
            
            assert not status.running
            mock_stop_instance.assert_called_once_with("default", timeout=60, force=False)
    
    def test_stop_bot_not_running(self):
        """Test stopping bot when not running"""
        with patch.object(self.process_manager, 'get_bot_status') as mock_status:
            mock_status.return_value = BotStatus(running=False)
            
            status = self.process_manager.stop_bot()
            assert not status.running
    
    def test_stop_bot_force_kill(self):
        """Test force killing bot"""
        # Create a running default instance
        from genebot.cli.utils.process_manager import BotInstance, ProcessState
        instance = BotInstance(name="default", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["default"] = instance
        
        with patch.object(self.process_manager, 'stop_bot_instance') as mock_stop_instance:
            mock_stop_instance.return_value = BotStatus(running=False)
            
            status = self.process_manager.stop_bot(force=True)
            
            assert not status.running
            mock_stop_instance.assert_called_once_with("default", timeout=60, force=True)
    
    def test_stop_bot_timeout_then_kill(self):
        """Test bot stop with timeout then force kill"""
        # Create a running default instance
        from genebot.cli.utils.process_manager import BotInstance, ProcessState
        instance = BotInstance(name="default", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["default"] = instance
        
        with patch.object(self.process_manager, 'stop_bot_instance') as mock_stop_instance:
            mock_stop_instance.return_value = BotStatus(running=False)
            
            status = self.process_manager.stop_bot(timeout=5)
            
            assert not status.running
            mock_stop_instance.assert_called_once_with("default", timeout=5, force=False)
    
    def test_restart_bot(self):
        """Test bot restart"""
        # Create a default instance first
        from genebot.cli.utils.process_manager import BotInstance
        instance = BotInstance(name="default")
        self.process_manager.instances["default"] = instance
        
        with patch.object(self.process_manager, 'restart_bot_instance') as mock_restart_instance:
            mock_restart_instance.return_value = BotStatus(running=True, pid=12345)
            
            status = self.process_manager.restart_bot()
            
            mock_restart_instance.assert_called_once_with("default", timeout=60)
            assert status.running
            assert status.pid == 12345


class TestProcessManagerIntegration:
    """Integration tests for ProcessManager with real processes"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.process_manager = ProcessManager(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "logs").mkdir(exist_ok=True)
        
        # Create a simple test script that can be controlled
        self.test_script = self.temp_dir / "test_bot.py"
        self.test_script.write_text("""
import time
import sys
import signal
import os

# Create a simple signal handler
def signal_handler(signum, frame):
    print(f"Received signal {signum}")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Write PID to a file for verification
with open('test_bot.pid', 'w') as f:
    f.write(str(os.getpid()))

print("Test bot started")
sys.stdout.flush()

# Run for a while
for i in range(100):
    time.sleep(0.1)
    if i % 10 == 0:
        print(f"Tick {i}")
        sys.stdout.flush()
""")
    
    def teardown_method(self):
        """Cleanup test environment"""
        # Clean up any running processes
        try:
            if self.process_manager.pid_file.exists():
                pid_info = self.process_manager._read_pid_file()
                if pid_info and pid_info.get('pid'):
                    try:
                        process = psutil.Process(pid_info['pid'])
                        process.terminate()
                        process.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        pass
        except Exception:
            pass
        
        # Remove temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.integration
    def test_real_process_lifecycle(self):
        """Test complete process lifecycle with real process"""
        # Override the command to use our test script
        original_build_command = self.process_manager._build_start_command
        
        def mock_build_command(*args, **kwargs):
            return [sys.executable, str(self.test_script)]
        
        self.process_manager._build_start_command = mock_build_command
        
        try:
            # Start the process
            status = self.process_manager.start_bot(background=True)
            
            assert status.running
            assert status.pid is not None
            
            # Wait a moment for process to initialize
            time.sleep(0.5)
            
            # Check status
            current_status = self.process_manager.get_bot_status()
            assert current_status.running
            assert current_status.pid == status.pid
            
            # Verify process is actually running
            process = psutil.Process(status.pid)
            assert process.is_running()
            
            # Stop the process
            stop_status = self.process_manager.stop_bot(timeout=5)
            assert not stop_status.running
            
            # Verify process is stopped
            time.sleep(0.1)
            final_status = self.process_manager.get_bot_status()
            assert not final_status.running
            
        finally:
            # Ensure cleanup
            try:
                if status.pid:
                    process = psutil.Process(status.pid)
                    if process.is_running():
                        process.terminate()
                        process.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass


class TestAdvancedProcessManager:
    """Test cases for advanced ProcessManager features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.process_manager = ProcessManager(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "logs").mkdir(exist_ok=True)
        (self.temp_dir / "logs" / "instances").mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        # Stop monitoring
        self.process_manager.stop_monitoring()
        
        # Clean up instances
        for instance_name in list(self.process_manager.instances.keys()):
            try:
                self.process_manager.stop_bot_instance(instance_name, force=True)
            except Exception:
                pass
        
        # Remove temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_recovery_config(self):
        """Test recovery configuration"""
        from genebot.cli.utils.process_manager import RecoveryConfig
        
        config = RecoveryConfig(
            enabled=True,
            max_restarts=3,
            restart_delay=10,
            memory_threshold_mb=500.0,
            cpu_threshold_percent=80.0
        )
        
        self.process_manager.configure_recovery(config)
        
        assert self.process_manager.recovery_config.enabled is True
        assert self.process_manager.recovery_config.max_restarts == 3
        assert self.process_manager.recovery_config.restart_delay == 10
        assert self.process_manager.recovery_config.memory_threshold_mb == 500.0
        assert self.process_manager.recovery_config.cpu_threshold_percent == 80.0
    
    def test_recovery_callbacks(self):
        """Test recovery callback system"""
        callback_calls = []
        
        def test_callback(instance_name: str, status):
            callback_calls.append((instance_name, status))
        
        self.process_manager.add_recovery_callback(test_callback)
        
        assert len(self.process_manager.recovery_callbacks) == 1
        
        # Simulate callback
        from genebot.cli.utils.process_manager import BotStatus
        test_status = BotStatus(running=False)
        self.process_manager.recovery_callbacks[0]("test", test_status)
        
        assert len(callback_calls) == 1
        assert callback_calls[0][0] == "test"
    
    @patch('subprocess.Popen')
    def test_start_bot_instance(self, mock_popen):
        """Test starting a named bot instance"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            from genebot.cli.utils.process_manager import ProcessInfo
            mock_process_info = ProcessInfo(
                pid=12345,
                name="python",
                status="running",
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_mb=100.0,
                create_time=datetime.now(),
                uptime=timedelta(seconds=0),
                command_line=[sys.executable, "main.py"]
            )
            mock_get_info.return_value = mock_process_info
            
            status = self.process_manager.start_bot_instance(
                "test_instance",
                config_file="test.yaml",
                strategies=["rsi"],
                accounts=["binance"]
            )
            
            assert status.running
            assert status.pid == 12345
            assert "test_instance" in self.process_manager.instances
            
            instance = self.process_manager.instances["test_instance"]
            assert instance.name == "test_instance"
            assert instance.config_file == "test.yaml"
            assert instance.strategies == ["rsi"]
            assert instance.accounts == ["binance"]
    
    def test_start_instance_already_running(self):
        """Test starting instance when already running"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState
        
        # Create running instance
        instance = BotInstance(name="test_instance")
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["test_instance"] = instance
        
        with pytest.raises(ProcessError) as exc_info:
            self.process_manager.start_bot_instance("test_instance")
        
        assert "already running" in str(exc_info.value)
    
    def test_stop_bot_instance(self):
        """Test stopping a bot instance"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState
        
        # Create running instance
        instance = BotInstance(name="test_instance", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["test_instance"] = instance
        
        with patch('psutil.Process') as mock_process_class:
            mock_process = Mock()
            mock_process.terminate.return_value = None
            mock_process.wait.return_value = None
            mock_process_class.return_value = mock_process
            
            status = self.process_manager.stop_bot_instance("test_instance")
            
            assert not status.running
            assert status.state == ProcessState.STOPPED
            mock_process.terminate.assert_called_once()
    
    def test_stop_instance_not_found(self):
        """Test stopping non-existent instance"""
        with pytest.raises(ProcessError) as exc_info:
            self.process_manager.stop_bot_instance("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    def test_restart_bot_instance(self):
        """Test restarting a bot instance"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState
        
        # Create instance
        instance = BotInstance(
            name="test_instance",
            config_file="test.yaml",
            strategies=["rsi"],
            accounts=["binance"]
        )
        self.process_manager.instances["test_instance"] = instance
        
        with patch.object(self.process_manager, 'stop_bot_instance') as mock_stop:
            with patch.object(self.process_manager, 'start_bot_instance') as mock_start:
                mock_stop.return_value = BotStatus(running=False)
                mock_start.return_value = BotStatus(running=True, pid=12345)
                
                status = self.process_manager.restart_bot_instance("test_instance")
                
                mock_stop.assert_called_once_with("test_instance", timeout=60)
                mock_start.assert_called_once()
                assert status.running
    
    def test_list_instances(self):
        """Test listing bot instances"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus
        
        # Create test instances
        instance1 = BotInstance(name="instance1")
        instance1.status = BotStatus(running=True, pid=12345)
        
        instance2 = BotInstance(name="instance2")
        instance2.status = BotStatus(running=False)
        
        self.process_manager.instances["instance1"] = instance1
        self.process_manager.instances["instance2"] = instance2
        
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            # Mock process info for running instance
            mock_get_info.return_value = Mock()
            
            instances = self.process_manager.list_instances()
            
            assert len(instances) == 2
            assert "instance1" in instances
            assert "instance2" in instances
    
    def test_get_instance_status(self):
        """Test getting instance status"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus
        
        instance = BotInstance(name="test_instance", pid=12345)
        instance.status = BotStatus(running=True, pid=12345)
        self.process_manager.instances["test_instance"] = instance
        
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            from genebot.cli.utils.process_manager import ProcessInfo
            mock_process_info = ProcessInfo(
                pid=12345,
                name="python",
                status="running",
                cpu_percent=5.0,
                memory_percent=10.0,
                memory_mb=256.0,
                create_time=datetime.now(),
                uptime=timedelta(hours=1),
                command_line=[sys.executable, "main.py"]
            )
            mock_get_info.return_value = mock_process_info
            
            status = self.process_manager.get_instance_status("test_instance")
            
            assert status.running
            assert status.pid == 12345
            assert status.memory_usage == 256.0
            assert status.cpu_usage == 5.0
    
    def test_get_instance_status_not_found(self):
        """Test getting status of non-existent instance"""
        with pytest.raises(ProcessError) as exc_info:
            self.process_manager.get_instance_status("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    def test_get_instance_metrics(self):
        """Test getting instance metrics"""
        from genebot.cli.utils.process_manager import BotInstance, ProcessMetrics
        from collections import deque
        
        instance = BotInstance(name="test_instance")
        
        # Add some test metrics
        metrics = [
            ProcessMetrics(
                timestamp=datetime.now() - timedelta(minutes=i),
                cpu_percent=float(i),
                memory_mb=100.0 + i,
                memory_percent=10.0 + i,
                threads=5,
                open_files=10,
                connections=2
            )
            for i in range(10)
        ]
        instance.metrics_history = deque(metrics, maxlen=100)
        
        self.process_manager.instances["test_instance"] = instance
        
        # Get all metrics
        result = self.process_manager.get_instance_metrics("test_instance")
        assert len(result) == 10
        
        # Get limited metrics
        result = self.process_manager.get_instance_metrics("test_instance", limit=5)
        assert len(result) == 5
    
    def test_get_instance_logs(self):
        """Test getting instance logs"""
        from genebot.cli.utils.process_manager import BotInstance
        
        # Create test log file
        log_file = self.temp_dir / "test_instance.log"
        log_content = "\n".join([f"Log line {i}" for i in range(20)])
        log_file.write_text(log_content)
        
        instance = BotInstance(name="test_instance", log_file=log_file)
        self.process_manager.instances["test_instance"] = instance
        
        # Get all logs
        logs = self.process_manager.get_instance_logs("test_instance")
        assert len(logs) == 20
        assert logs[0] == "Log line 0"
        assert logs[-1] == "Log line 19"
        
        # Get limited logs
        logs = self.process_manager.get_instance_logs("test_instance", lines=5)
        assert len(logs) == 5
        assert logs[0] == "Log line 15"  # Last 5 lines
        assert logs[-1] == "Log line 19"
    
    def test_monitoring_lifecycle(self):
        """Test monitoring start/stop lifecycle"""
        assert not self.process_manager.monitoring_active
        
        # Start monitoring
        self.process_manager.start_monitoring(interval=1)
        assert self.process_manager.monitoring_active
        assert self.process_manager.monitoring_thread is not None
        
        # Try to start again (should warn)
        self.process_manager.start_monitoring(interval=1)
        
        # Stop monitoring
        self.process_manager.stop_monitoring()
        assert not self.process_manager.monitoring_active
    
    def test_check_instance_health(self):
        """Test instance health checking"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState, ProcessInfo
        
        instance = BotInstance(name="test_instance", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["test_instance"] = instance
        
        # Test healthy process
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            mock_process_info = ProcessInfo(
                pid=12345,
                name="python",
                status="running",
                cpu_percent=50.0,  # Below threshold
                memory_percent=10.0,
                memory_mb=500.0,  # Below threshold
                create_time=datetime.now(),
                uptime=timedelta(hours=1),
                command_line=[sys.executable, "main.py"],
                threads=5,
                open_files=10,
                connections=2
            )
            mock_get_info.return_value = mock_process_info
            
            self.process_manager._check_instance_health("test_instance", instance)
            
            # Should have added metrics
            assert len(instance.metrics_history) == 1
            assert instance.status.memory_usage == 500.0
            assert instance.status.cpu_usage == 50.0
    
    def test_check_instance_health_crashed(self):
        """Test health checking for crashed process"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState, RecoveryConfig
        
        # Configure recovery
        self.process_manager.recovery_config = RecoveryConfig(
            enabled=True,
            auto_restart_on_crash=True,
            max_restarts=1,
            restart_delay=1
        )
        
        instance = BotInstance(name="test_instance", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["test_instance"] = instance
        
        # Mock crashed process (returns None)
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            with patch.object(self.process_manager, '_attempt_recovery') as mock_recovery:
                mock_get_info.return_value = None
                
                self.process_manager._check_instance_health("test_instance", instance)
                
                assert instance.status.state == ProcessState.CRASHED
                assert not instance.status.running
                mock_recovery.assert_called_once()
    
    def test_attempt_recovery_disabled(self):
        """Test recovery when disabled"""
        from genebot.cli.utils.process_manager import BotInstance, RecoveryConfig
        
        # Disable recovery
        self.process_manager.recovery_config = RecoveryConfig(enabled=False)
        
        instance = BotInstance(name="test_instance")
        
        # Should return early
        self.process_manager._attempt_recovery("test_instance", instance)
        # No assertions needed, just shouldn't crash
    
    def test_attempt_recovery_max_restarts(self):
        """Test recovery with max restarts exceeded"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, RecoveryConfig
        
        self.process_manager.recovery_config = RecoveryConfig(
            enabled=True,
            max_restarts=2
        )
        
        instance = BotInstance(name="test_instance")
        instance.status = BotStatus(running=False, restart_count=3)  # Exceeds max
        
        # Should return early
        self.process_manager._attempt_recovery("test_instance", instance)
        # No assertions needed, just shouldn't crash
    
    def test_attempt_recovery_delay(self):
        """Test recovery with restart delay"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, RecoveryConfig
        
        self.process_manager.recovery_config = RecoveryConfig(
            enabled=True,
            restart_delay=60  # 1 minute
        )
        
        instance = BotInstance(name="test_instance")
        instance.status = BotStatus(
            running=False,
            restart_count=0,
            last_restart=datetime.now() - timedelta(seconds=30)  # Too recent
        )
        
        # Should return early due to delay
        self.process_manager._attempt_recovery("test_instance", instance)
        # No assertions needed, just shouldn't crash
    
    def test_create_instance_pid_file(self):
        """Test creating instance PID file"""
        from genebot.cli.utils.process_manager import BotInstance
        
        instance = BotInstance(
            name="test_instance",
            pid=12345,
            config_file="test.yaml",
            strategies=["rsi"],
            accounts=["binance"]
        )
        instance.pid_file = self.temp_dir / "test_instance.pid"
        instance.log_file = self.temp_dir / "test_instance.log"
        
        cmd = [sys.executable, "main.py"]
        
        self.process_manager._create_instance_pid_file("test_instance", instance, cmd)
        
        assert instance.pid_file.exists()
        
        # Read and verify content
        with open(instance.pid_file, 'r') as f:
            pid_data = json.load(f)
        
        assert pid_data['instance_name'] == "test_instance"
        assert pid_data['pid'] == 12345
        assert pid_data['command'] == cmd
        assert pid_data['config_file'] == "test.yaml"
        assert pid_data['strategies'] == ["rsi"]
        assert pid_data['accounts'] == ["binance"]
    
    def test_load_instances(self):
        """Test loading instances from PID files"""
        # Create test PID file
        pid_file = self.process_manager.instances_dir / "test_instance.pid"
        pid_data = {
            'instance_name': 'test_instance',
            'pid': 12345,
            'command': [sys.executable, 'main.py'],
            'config_file': 'test.yaml',
            'strategies': ['rsi'],
            'accounts': ['binance'],
            'log_file': str(self.temp_dir / 'test.log')
        }
        
        with open(pid_file, 'w') as f:
            json.dump(pid_data, f)
        
        # Mock process not running
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            mock_get_info.return_value = None
            
            # Clear instances and reload
            self.process_manager.instances.clear()
            self.process_manager._load_instances()
            
            # Should have loaded instance but marked as stopped
            assert "test_instance" in self.process_manager.instances
            instance = self.process_manager.instances["test_instance"]
            assert instance.name == "test_instance"
            assert not instance.status.running
            assert instance.config_file == "test.yaml"
            assert instance.strategies == ["rsi"]
            assert instance.accounts == ["binance"]
            
            # PID file should be cleaned up
            assert not pid_file.exists()


class TestProcessManagerRecovery:
    """Test cases for process recovery functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.process_manager = ProcessManager(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "logs").mkdir(exist_ok=True)
        (self.temp_dir / "logs" / "instances").mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        self.process_manager.stop_monitoring()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_recovery_with_callback(self):
        """Test recovery with callback notification"""
        from genebot.cli.utils.process_manager import BotInstance, BotStatus, ProcessState, RecoveryConfig
        
        callback_calls = []
        
        def recovery_callback(instance_name: str, status: BotStatus):
            callback_calls.append((instance_name, status.state))
        
        self.process_manager.add_recovery_callback(recovery_callback)
        self.process_manager.recovery_config = RecoveryConfig(
            enabled=True,
            cpu_threshold_percent=50.0,
            memory_threshold_mb=200.0
        )
        
        instance = BotInstance(name="test_instance", pid=12345)
        instance.status = BotStatus(running=True, pid=12345, state=ProcessState.RUNNING)
        self.process_manager.instances["test_instance"] = instance
        
        # Simulate high resource usage
        with patch.object(self.process_manager, '_get_process_info') as mock_get_info:
            from genebot.cli.utils.process_manager import ProcessInfo
            mock_process_info = ProcessInfo(
                pid=12345,
                name="python",
                status="running",
                cpu_percent=80.0,  # Above threshold
                memory_percent=20.0,
                memory_mb=300.0,  # Above threshold
                create_time=datetime.now(),
                uptime=timedelta(hours=1),
                command_line=[sys.executable, "main.py"],
                threads=5,
                open_files=10,
                connections=2
            )
            mock_get_info.return_value = mock_process_info
            
            self.process_manager._check_instance_health("test_instance", instance)
            
            # Should have called callback
            assert len(callback_calls) == 1
            assert callback_calls[0][0] == "test_instance"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"""
Bot Control Commands
===================

Commands for controlling the trading bot lifecycle.
"""

from argparse import Namespace
from typing import Dict, Any, Optional
from datetime import timedelta
from pathlib import Path
import json

from ..result import CommandResult
from .base import BaseCommand
from ..utils.process_manager import ProcessManager, ProcessError


class StartBotCommand(BaseCommand):
    """Start the trading bot"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute start bot command"""
        config_file = getattr(args, 'config', None)
        strategies = getattr(args, 'strategy', None)
        accounts = getattr(args, 'account', None)
        background = getattr(args, 'background', True)
        foreground = getattr(args, 'foreground', False)
        
        # Handle foreground override
        if foreground:
            background = False
        
        self.logger.section("Starting GeneBot Trading Engine")
        
        try:
            # Initialize process manager
            process_manager = ProcessManager(self.context.workspace_path)
            
            if config_file:
                self.logger.info(f"Using configuration file: {config_file}")
            
            if strategies:
                self.logger.info(f"Enabled strategies: {', '.join(strategies)}")
            
            if accounts:
                self.logger.info(f"Using accounts: {', '.join(accounts)}")
            
            # Validate system configuration
            self.logger.progress("Validating system configuration...")
            self._validate_system_config()
            
            # Start bot process
            self.logger.progress("Starting bot processes...")
            
            status = process_manager.start_bot(
                config_file=config_file,
                strategies=strategies,
                accounts=accounts,
                background=background
            )
            
            if status.running:
                self.logger.success(f"GeneBot trading engine started successfully! (PID: {status.pid})")
                
                # Show initial status
                if status.process_info:
                    self.logger.info(f"Memory usage: {status.memory_usage:.1f} MB")
                    self.logger.info(f"CPU usage: {status.cpu_usage:.1f}%")
                
                return CommandResult.success(
                    f"Trading bot started successfully with PID {status.pid}",
                    data={
                        'pid': status.pid,
                        'memory_usage': status.memory_usage,
                        'cpu_usage': status.cpu_usage
                    },
                    suggestions=[
                        "Monitor status with 'genebot status'",
                        "View live activity with 'genebot monitor'",
                        "Check trades with 'genebot trades'",
                        f"View logs in logs/ directory"
                    ]
                )
            else:
                return CommandResult.error(
                    "Failed to start trading bot",
                    suggestions=["Check logs for error details", "Verify configuration"]
                )
                
        except ProcessError as e:
            self.logger.error(f"Process error: {e.message}")
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return CommandResult.error(
                f"Failed to start bot: {str(e)}",
                suggestions=[
                    "Check system resources",
                    "Verify Python installation",
                    "Check workspace permissions"
                ]
            )
    
    def _auto_detect_workspace(self) -> bool:
        """
        Auto-detect workspace by looking for main.py in parent directories.
        Updates context.workspace_path if found.
        
        Returns:
            bool: True if workspace was found and updated, False otherwise
        """
        current_path = Path.cwd()
        max_depth = 5  # Limit search to avoid infinite loops
        
        for i in range(max_depth):
            main_py = current_path / "main.py"
            if main_py.exists():
                # Found main.py, check if it looks like a GeneBot main.py
                try:
                    content = main_py.read_text()
                    if "trading" in content.lower() and ("genebot" in content.lower() or "bot" in content.lower()):
                        # Update the context to use this as workspace
                        self.context.config_path = current_path / "config"
                        self.logger.info(f"Auto-detected workspace: {current_path}")
                        return True
                except Exception:
                    pass  # Continue searching if we can't read the file
            
            # Move to parent directory
            parent = current_path.parent
            if parent == current_path:  # Reached filesystem root
                break
            current_path = parent
        
        return False
    
    def _validate_system_config(self) -> None:
        """Validate system configuration before starting"""
        # Check if main.py exists in current workspace
        main_py = self.context.workspace_path / "main.py"
        if not main_py.exists():
            # Try to auto-detect workspace by looking for main.py in parent directories
            workspace_found = self._auto_detect_workspace()
            if not workspace_found:
                # Provide more specific guidance based on the situation
                current_dir = Path.cwd()
                config_dir = current_dir / "config"
                
                # Check if this looks like a real workspace or just auto-created config
                has_real_config = False
                if config_dir.exists():
                    # Check if config directory has actual configuration files
                    config_files = [
                        config_dir / "trading_bot_config.yaml",
                        config_dir / "accounts.yaml"
                    ]
                    has_real_config = any(f.exists() for f in config_files)
                
                if has_real_config:
                    # Config directory exists with real files but no main.py - likely a partial setup
                    suggestions = [
                        "This appears to be a GeneBot workspace but main.py is missing",
                        "Download or create main.py in this directory",
                        "Ensure you have the complete GeneBot project files",
                        "Check if main.py was accidentally deleted or moved"
                    ]
                else:
                    # No real config files - likely running from wrong location
                    suggestions = [
                        "Navigate to your GeneBot project directory (where main.py is located)",
                        "If you don't have a project yet, run 'genebot init-config' to create one",
                        "Use --config-path to specify the correct config directory path",
                        "Ensure you're in a directory containing both main.py and config/ folder"
                    ]
                
                raise ProcessError(
                    "main.py not found in workspace",
                    suggestions=suggestions
                )
        
        # Check if config directory exists
        config_dir = self.context.workspace_path / "config"
        if not config_dir.exists():
            self.logger.warning("Config directory not found, bot may use defaults")
        
        # Check if logs directory is writable
        logs_dir = self.context.workspace_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        try:
            test_file = logs_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise ProcessError(
                f"Cannot write to logs directory: {str(e)}",
                suggestions=[
                    "Check directory permissions",
                    "Ensure sufficient disk space",
                    "Create logs directory manually"
                ]
            )


class StopBotCommand(BaseCommand):
    """Stop the trading bot"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute stop bot command"""
        timeout = getattr(args, 'timeout', 60)
        force = getattr(args, 'force', False)
        
        self.logger.section("Stopping GeneBot Trading Engine")
        self.logger.info(f"Shutdown timeout: {timeout} seconds")
        
        if force:
            self.logger.warning("Force stop requested - bot will be killed immediately")
        
        try:
            # Initialize process manager
            process_manager = ProcessManager(self.context.workspace_path)
            
            # Check current status
            current_status = process_manager.get_bot_status()
            if not current_status.running:
                self.logger.info("Bot is not currently running")
                return CommandResult.success("Bot was not running")
            
            self.logger.info(f"Stopping bot process (PID: {current_status.pid})")
            
            # Stop the bot
            if force:
                self.logger.progress("Force killing bot process...")
            else:
                self.logger.progress("Sending shutdown signal...")
                self.logger.progress("Waiting for graceful shutdown...")
            
            status = process_manager.stop_bot(timeout=timeout, force=force)
            
            if not status.running:
                self.logger.progress("Cleaning up resources...")
                self.logger.success("GeneBot trading engine stopped successfully!")
                
                return CommandResult.success(
                    "Trading bot stopped successfully",
                    suggestions=[
                        "Use 'genebot start' to restart the bot",
                        "Check logs for any shutdown messages"
                    ]
                )
            else:
                return CommandResult.error(
                    "Failed to stop trading bot",
                    suggestions=[
                        "Try using --force flag",
                        "Check if process is hung",
                        "Manually kill process if necessary"
                    ]
                )
                
        except ProcessError as e:
            self.logger.error(f"Process error: {e.message}")
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return CommandResult.error(
                f"Failed to stop bot: {str(e)}",
                suggestions=[
                    "Try force stop with --force",
                    "Check system permissions",
                    "Manually terminate process"
                ]
            )


class RestartBotCommand(BaseCommand):
    """Restart the trading bot"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute restart bot command"""
        timeout = getattr(args, 'timeout', 60)
        config_file = getattr(args, 'config', None)
        strategies = getattr(args, 'strategy', None)
        accounts = getattr(args, 'account', None)
        
        self.logger.section("Restarting GeneBot Trading Engine")
        
        try:
            # Initialize process manager
            process_manager = ProcessManager(self.context.workspace_path)
            
            self.logger.progress("Stopping bot...")
            
            # Restart the bot
            status = process_manager.restart_bot(
                timeout=timeout,
                config_file=config_file,
                strategies=strategies,
                accounts=accounts
            )
            
            if status.running:
                self.logger.progress("Starting bot...")
                self.logger.success(f"GeneBot trading engine restarted successfully! (PID: {status.pid})")
                
                return CommandResult.success(
                    f"Trading bot restarted successfully with PID {status.pid}",
                    data={
                        'pid': status.pid,
                        'memory_usage': status.memory_usage,
                        'cpu_usage': status.cpu_usage
                    },
                    suggestions=[
                        "Monitor status with 'genebot status'",
                        "Check logs for startup messages"
                    ]
                )
            else:
                return CommandResult.error(
                    "Failed to restart trading bot",
                    suggestions=[
                        "Try stopping and starting manually",
                        "Check system resources",
                        "Verify configuration"
                    ]
                )
                
        except ProcessError as e:
            self.logger.error(f"Process error: {e.message}")
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return CommandResult.error(
                f"Failed to restart bot: {str(e)}",
                suggestions=[
                    "Try manual stop and start",
                    "Check system resources",
                    "Verify configuration files"
                ]
            )


class StatusCommand(BaseCommand):
    """Show bot status"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute status command"""
        detailed = getattr(args, 'detailed', False)
        json_output = getattr(args, 'json', False)
        
        self.logger.section("GeneBot Status")
        
        try:
            # Initialize process manager
            process_manager = ProcessManager(self.context.workspace_path)
            
            # Get bot status
            bot_status = process_manager.get_bot_status()
            
            # Get health information
            health_info = process_manager.monitor_health()
            
            # Prepare status data
            status_data = {
                'bot_running': bot_status.running,
                'pid': bot_status.pid,
                'uptime': self._format_uptime(bot_status.uptime) if bot_status.uptime else None,
                'memory_usage': f"{bot_status.memory_usage:.1f} MB" if bot_status.memory_usage else None,
                'cpu_usage': f"{bot_status.cpu_usage:.1f}%" if bot_status.cpu_usage else None,
                'error_message': bot_status.error_message,
                'last_check': health_info['timestamp'],
                'healthy': health_info['healthy']
            }
            
            # Add detailed information if requested
            if detailed and bot_status.process_info:
                status_data.update({
                    'process_name': bot_status.process_info.name,
                    'process_status': bot_status.process_info.status,
                    'memory_percent': f"{bot_status.process_info.memory_percent:.1f}%",
                    'command_line': ' '.join(bot_status.process_info.command_line),
                    'create_time': bot_status.process_info.create_time.isoformat()
                })
            
            if json_output:
                print(json.dumps(status_data, indent=2, default=str))
                return CommandResult.success("Status displayed in JSON format")
            
            # Display formatted status
            self._display_status(status_data, detailed, bot_status)
            
            return CommandResult.success(
                "Status information displayed",
                data=status_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {str(e)}")
            return CommandResult.error(
                f"Failed to get bot status: {str(e)}",
                suggestions=[
                    "Check if bot process exists",
                    "Verify PID file integrity",
                    "Check system permissions"
                ]
            )
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """Format uptime as human-readable string"""
        total_seconds = int(uptime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _display_status(self, status: Dict[str, Any], detailed: bool, bot_status) -> None:
        """Display status information in formatted output"""
        
        # Bot status
        if status['bot_running']:
            bot_status_text = "🟢 Running"
            if not status['healthy']:
                bot_status_text += " (Unhealthy)"
        else:
            bot_status_text = "🔴 Stopped"
        
        self.logger.list_item(f"Bot Status: {bot_status_text}", "info")
        
        if status['error_message']:
            self.logger.list_item(f"Error: {status['error_message']}", "error")
        
        if status['bot_running']:
            self.logger.list_item(f"Process ID: {status['pid']}", "info")
            if status['uptime']:
                self.logger.list_item(f"Uptime: {status['uptime']}", "info")
            
            if status['memory_usage']:
                self.logger.list_item(f"Memory Usage: {status['memory_usage']}", "info")
            if status['cpu_usage']:
                self.logger.list_item(f"CPU Usage: {status['cpu_usage']}", "info")
        
        # Show last check time
        self.logger.list_item(f"Last Check: {status['last_check']}", "info")
        
        if detailed and status['bot_running']:
            self.logger.subsection("Detailed Process Information")
            
            if 'process_name' in status:
                self.logger.list_item(f"Process Name: {status['process_name']}", "info")
            if 'process_status' in status:
                self.logger.list_item(f"Process Status: {status['process_status']}", "info")
            if 'memory_percent' in status:
                self.logger.list_item(f"Memory Percent: {status['memory_percent']}", "info")
            if 'command_line' in status:
                self.logger.list_item(f"Command: {status['command_line']}", "info")
            if 'create_time' in status:
                self.logger.list_item(f"Started: {status['create_time']}", "info")


class StartInstanceCommand(BaseCommand):
    """Start a named bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute start instance command"""
        instance_name = args.instance_name
        config_file = getattr(args, 'config', None)
        strategies = getattr(args, 'strategy', None)
        accounts = getattr(args, 'account', None)
        background = getattr(args, 'background', True)
        foreground = getattr(args, 'foreground', False)
        
        if foreground:
            background = False
        
        self.logger.section(f"Starting Bot Instance: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            
            status = process_manager.start_bot_instance(
                instance_name,
                config_file=config_file,
                strategies=strategies,
                accounts=accounts,
                background=background
            )
            
            if status.running:
                self.logger.success(f"Instance '{instance_name}' started successfully! (PID: {status.pid})")
                
                return CommandResult.success(
                    f"Bot instance '{instance_name}' started with PID {status.pid}",
                    data={'instance_name': instance_name, 'pid': status.pid},
                    suggestions=[
                        f"Monitor with 'genebot instance-status {instance_name}'",
                        "List all instances with 'genebot list-instances'"
                    ]
                )
            else:
                return CommandResult.error(f"Failed to start instance '{instance_name}'")
                
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to start instance: {str(e)}")


class StopInstanceCommand(BaseCommand):
    """Stop a named bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute stop instance command"""
        instance_name = args.instance_name
        timeout = getattr(args, 'timeout', 60)
        force = getattr(args, 'force', False)
        
        self.logger.section(f"Stopping Bot Instance: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            
            status = process_manager.stop_bot_instance(
                instance_name,
                timeout=timeout,
                force=force
            )
            
            if not status.running:
                self.logger.success(f"Instance '{instance_name}' stopped successfully!")
                
                return CommandResult.success(
                    f"Bot instance '{instance_name}' stopped successfully",
                    suggestions=[f"Restart with 'genebot start-instance {instance_name}'"]
                )
            else:
                return CommandResult.error(f"Failed to stop instance '{instance_name}'")
                
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to stop instance: {str(e)}")


class RestartInstanceCommand(BaseCommand):
    """Restart a named bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute restart instance command"""
        instance_name = args.instance_name
        timeout = getattr(args, 'timeout', 60)
        
        self.logger.section(f"Restarting Bot Instance: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            
            status = process_manager.restart_bot_instance(instance_name, timeout=timeout)
            
            if status.running:
                self.logger.success(f"Instance '{instance_name}' restarted successfully! (PID: {status.pid})")
                
                return CommandResult.success(
                    f"Bot instance '{instance_name}' restarted with PID {status.pid}",
                    data={'instance_name': instance_name, 'pid': status.pid}
                )
            else:
                return CommandResult.error(f"Failed to restart instance '{instance_name}'")
                
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to restart instance: {str(e)}")


class ListInstancesCommand(BaseCommand):
    """List all bot instances"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute list instances command"""
        json_output = getattr(args, 'json', False)
        
        self.logger.section("Bot Instances")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            instances = process_manager.list_instances()
            
            if not instances:
                self.logger.info("No bot instances found")
                return CommandResult.success("No instances found")
            
            if json_output:
                instance_data = {}
                for name, instance in instances.items():
                    instance_data[name] = {
                        'name': instance.name,
                        'pid': instance.pid,
                        'running': instance.status.running,
                        'state': instance.status.state.value,
                        'config_file': instance.config_file,
                        'strategies': instance.strategies,
                        'accounts': instance.accounts,
                        'restart_count': instance.status.restart_count
                    }
                print(json.dumps(instance_data, indent=2))
                return CommandResult.success("Instances listed in JSON format")
            
            # Display formatted list
            for name, instance in instances.items():
                status_icon = "🟢" if instance.status.running else "🔴"
                state_text = instance.status.state.value.title()
                
                self.logger.list_item(f"{status_icon} {name} ({state_text})", "info")
                
                if instance.pid:
                    self.logger.list_item(f"  PID: {instance.pid}", "info", indent=1)
                
                if instance.config_file:
                    self.logger.list_item(f"  Config: {instance.config_file}", "info", indent=1)
                
                if instance.strategies:
                    self.logger.list_item(f"  Strategies: {', '.join(instance.strategies)}", "info", indent=1)
                
                if instance.accounts:
                    self.logger.list_item(f"  Accounts: {', '.join(instance.accounts)}", "info", indent=1)
                
                if instance.status.restart_count > 0:
                    self.logger.list_item(f"  Restarts: {instance.status.restart_count}", "info", indent=1)
            
            return CommandResult.success(
                f"Found {len(instances)} bot instances",
                data={'instance_count': len(instances)}
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to list instances: {str(e)}")


class InstanceStatusCommand(BaseCommand):
    """Show status of a specific bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute instance status command"""
        instance_name = args.instance_name
        detailed = getattr(args, 'detailed', False)
        json_output = getattr(args, 'json', False)
        
        self.logger.section(f"Instance Status: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            status = process_manager.get_instance_status(instance_name)
            
            status_data = {
                'instance_name': instance_name,
                'running': status.running,
                'state': status.state.value,
                'pid': status.pid,
                'uptime': self._format_uptime(status.uptime) if status.uptime else None,
                'memory_usage': f"{status.memory_usage:.1f} MB" if status.memory_usage else None,
                'cpu_usage': f"{status.cpu_usage:.1f}%" if status.cpu_usage else None,
                'restart_count': status.restart_count,
                'last_restart': status.last_restart.isoformat() if status.last_restart else None,
                'error_message': status.error_message
            }
            
            if json_output:
                print(json.dumps(status_data, indent=2, default=str))
                return CommandResult.success("Instance status displayed in JSON format")
            
            # Display formatted status
            state_icon = "🟢" if status.running else "🔴"
            self.logger.list_item(f"Status: {state_icon} {status.state.value.title()}", "info")
            
            if status.pid:
                self.logger.list_item(f"Process ID: {status.pid}", "info")
            
            if status.uptime:
                self.logger.list_item(f"Uptime: {self._format_uptime(status.uptime)}", "info")
            
            if status.memory_usage:
                self.logger.list_item(f"Memory Usage: {status.memory_usage:.1f} MB", "info")
            
            if status.cpu_usage:
                self.logger.list_item(f"CPU Usage: {status.cpu_usage:.1f}%", "info")
            
            if status.restart_count > 0:
                self.logger.list_item(f"Restart Count: {status.restart_count}", "info")
            
            if status.last_restart:
                self.logger.list_item(f"Last Restart: {status.last_restart}", "info")
            
            if status.error_message:
                self.logger.list_item(f"Error: {status.error_message}", "error")
            
            return CommandResult.success("Instance status displayed", data=status_data)
            
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to get instance status: {str(e)}")
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """Format uptime as human-readable string"""
        total_seconds = int(uptime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class InstanceLogsCommand(BaseCommand):
    """Show logs for a specific bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute instance logs command"""
        instance_name = args.instance_name
        lines = getattr(args, 'lines', 100)
        follow = getattr(args, 'follow', False)
        
        self.logger.section(f"Instance Logs: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            
            if follow:
                self.logger.info("Following logs (Ctrl+C to stop)...")
                # TODO: Implement log following
                return CommandResult.error("Log following not yet implemented")
            
            logs = process_manager.get_instance_logs(instance_name, lines=lines)
            
            if not logs:
                self.logger.info("No logs found for this instance")
                return CommandResult.success("No logs available")
            
            self.logger.info(f"Showing last {len(logs)} lines:")
            for line in logs:
                print(line)
            
            return CommandResult.success(f"Displayed {len(logs)} log lines")
            
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to get instance logs: {str(e)}")


class StartMonitoringCommand(BaseCommand):
    """Start process monitoring"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute start monitoring command"""
        interval = getattr(args, 'interval', 60)
        
        self.logger.section("Starting Process Monitoring")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            process_manager.start_monitoring(interval=interval)
            
            self.logger.success(f"Process monitoring started with {interval}s interval")
            
            return CommandResult.success(
                f"Process monitoring started with {interval}s interval",
                suggestions=[
                    "Stop monitoring with 'genebot stop-monitoring'",
                    "Check instance status with 'genebot list-instances'"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to start monitoring: {str(e)}")


class StopMonitoringCommand(BaseCommand):
    """Stop process monitoring"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute stop monitoring command"""
        self.logger.section("Stopping Process Monitoring")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            process_manager.stop_monitoring()
            
            self.logger.success("Process monitoring stopped")
            
            return CommandResult.success("Process monitoring stopped")
            
        except Exception as e:
            return CommandResult.error(f"Failed to stop monitoring: {str(e)}")


class InstanceMetricsCommand(BaseCommand):
    """Show performance metrics for a bot instance"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute instance metrics command"""
        instance_name = args.instance_name
        limit = getattr(args, 'limit', 50)
        json_output = getattr(args, 'json', False)
        
        self.logger.section(f"Instance Metrics: {instance_name}")
        
        try:
            process_manager = ProcessManager(self.context.workspace_path)
            metrics = process_manager.get_instance_metrics(instance_name, limit=limit)
            
            if not metrics:
                self.logger.info("No metrics available for this instance")
                return CommandResult.success("No metrics available")
            
            if json_output:
                metrics_data = []
                for metric in metrics:
                    metrics_data.append({
                        'timestamp': metric.timestamp.isoformat(),
                        'cpu_percent': metric.cpu_percent,
                        'memory_mb': metric.memory_mb,
                        'memory_percent': metric.memory_percent,
                        'threads': metric.threads,
                        'open_files': metric.open_files,
                        'connections': metric.connections
                    })
                print(json.dumps(metrics_data, indent=2))
                return CommandResult.success("Metrics displayed in JSON format")
            
            # Display formatted metrics
            self.logger.info(f"Showing last {len(metrics)} metrics:")
            
            for metric in metrics[-10:]:  # Show last 10 for readability
                timestamp = metric.timestamp.strftime("%H:%M:%S")
                self.logger.list_item(
                    f"{timestamp}: CPU {metric.cpu_percent:.1f}%, "
                    f"Memory {metric.memory_mb:.1f}MB ({metric.memory_percent:.1f}%), "
                    f"Threads {metric.threads}",
                    "info"
                )
            
            # Show summary statistics
            if len(metrics) > 1:
                avg_cpu = sum(m.cpu_percent for m in metrics) / len(metrics)
                avg_memory = sum(m.memory_mb for m in metrics) / len(metrics)
                max_memory = max(m.memory_mb for m in metrics)
                
                self.logger.subsection("Summary Statistics")
                self.logger.list_item(f"Average CPU: {avg_cpu:.1f}%", "info")
                self.logger.list_item(f"Average Memory: {avg_memory:.1f}MB", "info")
                self.logger.list_item(f"Peak Memory: {max_memory:.1f}MB", "info")
            
            return CommandResult.success(f"Displayed {len(metrics)} metrics")
            
        except ProcessError as e:
            return CommandResult.error(e.message, suggestions=e.suggestions)
        except Exception as e:
            return CommandResult.error(f"Failed to get instance metrics: {str(e)}")
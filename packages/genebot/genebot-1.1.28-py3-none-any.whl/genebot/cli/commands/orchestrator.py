"""
Orchestrator CLI Commands
========================

CLI commands for managing the strategy orchestrator.
"""

import asyncio
import json
import yaml
from typing import Dict, Any, Optional
from argparse import Namespace
from datetime import datetime, timedelta

from ..context import CLIContext
from ..result import CommandResult
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler
from .base import BaseCommand
import logging

class SimpleBaseCommand:
    """Simple base command for testing"""
    
    def __init__(self):
        self.context = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.error_handler = None
    
    def validate_args(self, args):
        """Validate command arguments"""
        from genebot.cli.result import CommandResult
        return CommandResult.success("Arguments validated")
    
    def execute(self, args):
        """Execute command"""
        from genebot.cli.result import CommandResult
        return CommandResult.success("Command executed")


# Import orchestrator components
try:
    import sys
    from pathlib import Path
    # Add src directory to path for orchestration imports
    src_path = Path(__file__).parent.parent.parent.parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from src.orchestration.orchestrator import StrategyOrchestrator
    from src.orchestration.config import OrchestratorConfig
    from src.orchestration.allocation import AllocationManager
    from src.orchestration.risk import OrchestratorRiskManager
    from src.orchestration.performance import PerformanceMonitor
    from src.orchestration.config_manager import ConfigurationManager
    from src.orchestration.monitoring import OrchestratorMonitoring
    from src.orchestration.manual_intervention import ManualInterventionManager
except ImportError as e:
    # Handle missing orchestration components gracefully
    StrategyOrchestrator = None
    OrchestratorConfig = None
    import_error = str(e)


class StartOrchestratorCommand(BaseCommand):
    """Start the strategy orchestrator"""
    
    def validate_args(self, args: Namespace) -> CommandResult:
        """Validate start orchestrator arguments"""
        if StrategyOrchestrator is None:
            return CommandResult.error(
                "Orchestrator components not available",
                details=[f"Import error: {import_error}"]
            )
        
        # Validate config file exists if specified
        if hasattr(args, 'config') and args.config:
            try:
                with open(args.config, 'r') as f:
                    yaml.safe_load(f)
            except FileNotFoundError:
                return CommandResult.error(f"Configuration file not found: {args.config}")
            except yaml.YAMLError as e:
                return CommandResult.error(f"Invalid YAML configuration: {e}")
        
        return CommandResult.success("Arguments validated")
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute start orchestrator command"""
        try:
            # Load configuration
            config_path = getattr(args, 'config', 'config/templates/orchestrator_config_template.yaml')
            config = self._load_orchestrator_config(config_path)
            
            if not config:
                return CommandResult.error("Failed to load orchestrator configuration")
            
            # Initialize orchestrator components
            allocation_manager = AllocationManager(config.allocation)
            risk_manager = OrchestratorRiskManager(config.risk)
            performance_monitor = PerformanceMonitor(config.monitoring)
            
            # Create orchestrator instance
            orchestrator = StrategyOrchestrator(
                config=config,
                allocation_manager=allocation_manager,
                risk_manager=risk_manager,
                performance_monitor=performance_monitor
            )
            
            # Start orchestrator
            self.logger.info("Starting strategy orchestrator...")
            
            # Run orchestrator in background if daemon mode
            if getattr(args, 'daemon', False):
                return self._start_daemon_mode(orchestrator, args)
            else:
                return self._start_interactive_mode(orchestrator, args)
                
        except Exception as e:
            return CommandResult.error(f"Failed to start orchestrator: {e}")
    
    def _load_orchestrator_config(self, config_path: str) -> Optional[OrchestratorConfig]:
        """Load orchestrator configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return OrchestratorConfig.from_dict(config_data.get('orchestrator', config_data))
        except Exception as e:
            self.logger.error(f"Failed to load config from {config_path}: {e}")
            return None
    
    def _start_daemon_mode(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Start orchestrator in daemon mode"""
        try:
            # Save orchestrator instance reference for other commands
            self.context.set_orchestrator_instance(orchestrator)
            
            # Start orchestrator
            orchestrator.start()
            
            return CommandResult.success(
                "Strategy orchestrator started in daemon mode",
                data={
                    'orchestrator_id': id(orchestrator),
                    'start_time': datetime.now().isoformat(),
                    'mode': 'daemon',
                    'strategies_count': len(orchestrator.active_strategies)
                }
            )
        except Exception as e:
            return CommandResult.error(f"Failed to start daemon mode: {e}")
    
    def _start_interactive_mode(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Start orchestrator in interactive mode"""
        try:
            # Save orchestrator instance reference
            self.context.set_orchestrator_instance(orchestrator)
            
            # Start orchestrator
            orchestrator.start()
            
            self.logger.info("Orchestrator started in interactive mode. Press Ctrl+C to stop.")
            
            # Run until interrupted
            try:
                while orchestrator.is_running:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Stopping orchestrator...")
                orchestrator.stop()
            
            return CommandResult.success(
                "Strategy orchestrator stopped",
                data={
                    'orchestrator_id': id(orchestrator),
                    'stop_time': datetime.now().isoformat(),
                    'mode': 'interactive'
                }
            )
        except Exception as e:
            return CommandResult.error(f"Failed to run interactive mode: {e}")


class StopOrchestratorCommand(BaseCommand):
    """Stop the strategy orchestrator"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute stop orchestrator command"""
        try:
            # Get orchestrator instance from context
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.error("No running orchestrator found")
            
            if not orchestrator.is_running:
                return CommandResult.warning("Orchestrator is not running")
            
            # Stop orchestrator gracefully
            self.logger.info("Stopping strategy orchestrator...")
            orchestrator.stop()
            
            # Clear instance from context
            self.context.clear_orchestrator_instance()
            
            return CommandResult.success(
                "Strategy orchestrator stopped successfully",
                data={
                    'stop_time': datetime.now().isoformat(),
                    'graceful_shutdown': True
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to stop orchestrator: {e}")


class OrchestratorStatusCommand(BaseCommand):
    """Get orchestrator status and metrics"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute orchestrator status command"""
        try:
            # Get orchestrator instance
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.warning(
                    "No orchestrator instance found",
                    data={'status': 'not_running'}
                )
            
            # Collect status information
            status_data = {
                'status': 'running' if orchestrator.is_running else 'stopped',
                'orchestrator_id': id(orchestrator),
                'start_time': getattr(orchestrator, 'start_time', None),
                'strategies': {
                    'active': len([s for s, state in orchestrator.strategy_states.items() if state == 'active']),
                    'paused': len([s for s, state in orchestrator.strategy_states.items() if state == 'paused']),
                    'failed': len([s for s, state in orchestrator.strategy_states.items() if state == 'failed']),
                    'total': len(orchestrator.active_strategies)
                },
                'performance': self._get_performance_summary(orchestrator),
                'risk': self._get_risk_summary(orchestrator),
                'allocation': self._get_allocation_summary(orchestrator)
            }
            
            # Add detailed information if verbose
            if getattr(args, 'verbose', False):
                status_data.update({
                    'strategy_details': self._get_strategy_details(orchestrator),
                    'recent_signals': self._get_recent_signals(orchestrator),
                    'metrics': orchestrator.orchestration_metrics
                })
            
            return CommandResult.success(
                f"Orchestrator status: {status_data['status']}",
                data=status_data
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to get orchestrator status: {e}")
    
    def _get_performance_summary(self, orchestrator: StrategyOrchestrator) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            performance_metrics = orchestrator.performance_monitor.collect_performance_metrics()
            
            return {
                'total_return': performance_metrics.get('portfolio', {}).get('total_return', 0.0),
                'sharpe_ratio': performance_metrics.get('portfolio', {}).get('sharpe_ratio', 0.0),
                'max_drawdown': performance_metrics.get('portfolio', {}).get('max_drawdown', 0.0),
                'win_rate': performance_metrics.get('portfolio', {}).get('win_rate', 0.0)
            }
        except Exception:
            return {'status': 'unavailable'}
    
    def _get_risk_summary(self, orchestrator: StrategyOrchestrator) -> Dict[str, Any]:
        """Get risk summary"""
        try:
            risk_metrics = orchestrator.risk_manager.get_risk_metrics()
            
            return {
                'current_drawdown': risk_metrics.get('current_drawdown', 0.0),
                'portfolio_var': risk_metrics.get('portfolio_var', 0.0),
                'correlation_risk': risk_metrics.get('max_correlation', 0.0),
                'position_concentration': risk_metrics.get('position_concentration', 0.0)
            }
        except Exception:
            return {'status': 'unavailable'}
    
    def _get_allocation_summary(self, orchestrator: StrategyOrchestrator) -> Dict[str, Any]:
        """Get allocation summary"""
        try:
            return {
                'strategy_weights': orchestrator.strategy_weights.copy(),
                'last_rebalance': orchestrator.last_rebalance.isoformat() if orchestrator.last_rebalance else None,
                'rebalance_frequency': orchestrator.config.allocation.rebalance_frequency
            }
        except Exception:
            return {'status': 'unavailable'}
    
    def _get_strategy_details(self, orchestrator: StrategyOrchestrator) -> Dict[str, Any]:
        """Get detailed strategy information"""
        try:
            details = {}
            for name, strategy in orchestrator.active_strategies.items():
                details[name] = {
                    'type': strategy.__class__.__name__,
                    'state': orchestrator.strategy_states.get(name, 'unknown'),
                    'weight': orchestrator.strategy_weights.get(name, 0.0),
                    'recent_returns': orchestrator.strategy_returns.get(name, [])[-5:]  # Last 5 returns
                }
            return details
        except Exception:
            return {'status': 'unavailable'}
    
    def _get_recent_signals(self, orchestrator: StrategyOrchestrator) -> Dict[str, Any]:
        """Get recent signals information"""
        try:
            # This would need to be implemented in the orchestrator
            return {
                'signals_today': getattr(orchestrator, 'signals_today', 0),
                'last_signal_time': getattr(orchestrator, 'last_signal_time', None)
            }
        except Exception:
            return {'status': 'unavailable'}


class OrchestratorConfigCommand(BaseCommand):
    """Manage orchestrator configuration"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute orchestrator config command"""
        try:
            action = getattr(args, 'action', 'show')
            
            if action == 'show':
                return self._show_config(args)
            elif action == 'update':
                return self._update_config(args)
            elif action == 'validate':
                return self._validate_config(args)
            elif action == 'reload':
                return self._reload_config(args)
            else:
                return CommandResult.error(f"Unknown config action: {action}")
                
        except Exception as e:
            return CommandResult.error(f"Failed to manage orchestrator config: {e}")
    
    def _show_config(self, args: Namespace) -> CommandResult:
        """Show current orchestrator configuration"""
        try:
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                # Load config from file
                config_path = getattr(args, 'config', None)
                if not config_path:
                    config_path = 'config/templates/orchestrator_config_template.yaml'
                
                # Check if file exists
                import os
                if not os.path.exists(config_path):
                    # Try alternative paths
                    alternative_paths = [
                        'config/templates/development_orchestrator_config.yaml',
                        'config/templates/production_orchestrator_config.yaml',
                        'config/templates/minimal_orchestrator_config.yaml'
                    ]
                    
                    for alt_path in alternative_paths:
                        if os.path.exists(alt_path):
                            config_path = alt_path
                            break
                    else:
                        return CommandResult.error(
                            f"No orchestrator configuration found. Available templates: {', '.join(alternative_paths)}"
                        )
                
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
            else:
                config_data = orchestrator.config.to_dict()
            
            return CommandResult.success(
                "Orchestrator configuration",
                data=config_data
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to show config: {e}")
    
    def _update_config(self, args: Namespace) -> CommandResult:
        """Update orchestrator configuration"""
        try:
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.error("No running orchestrator found")
            
            # Get configuration manager
            config_manager = ConfigurationManager(orchestrator.config)
            
            # Parse update parameters
            updates = {}
            if hasattr(args, 'allocation_method'):
                updates['allocation.method'] = args.allocation_method
            if hasattr(args, 'rebalance_frequency'):
                updates['allocation.rebalance_frequency'] = args.rebalance_frequency
            if hasattr(args, 'max_drawdown'):
                updates['risk.max_portfolio_drawdown'] = args.max_drawdown
            
            # Apply updates
            for key, value in updates.items():
                config_manager.update_config_value(key, value)
            
            return CommandResult.success(
                f"Updated {len(updates)} configuration parameters",
                data={'updates': updates}
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to update config: {e}")
    
    def _validate_config(self, args: Namespace) -> CommandResult:
        """Validate orchestrator configuration"""
        try:
            config_path = getattr(args, 'config', 'config/templates/orchestrator_config_template.yaml')
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Validate configuration
            try:
                config = OrchestratorConfig.from_dict(config_data.get('orchestrator', config_data))
                validation_errors = config.validate()
                
                if validation_errors:
                    return CommandResult.error(
                        "Configuration validation failed",
                        details=validation_errors
                    )
                else:
                    return CommandResult.success(
                        "Configuration is valid",
                        data={'config_path': config_path}
                    )
                    
            except Exception as e:
                return CommandResult.error(f"Configuration validation error: {e}")
                
        except Exception as e:
            return CommandResult.error(f"Failed to validate config: {e}")
    
    def _reload_config(self, args: Namespace) -> CommandResult:
        """Reload orchestrator configuration"""
        try:
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.error("No running orchestrator found")
            
            config_path = getattr(args, 'config', 'config/templates/orchestrator_config_template.yaml')
            
            # Load new configuration
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            new_config = OrchestratorConfig.from_dict(config_data.get('orchestrator', config_data))
            
            # Apply configuration
            orchestrator.update_config(new_config)
            
            return CommandResult.success(
                "Configuration reloaded successfully",
                data={
                    'config_path': config_path,
                    'reload_time': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to reload config: {e}")


class OrchestratorMonitorCommand(BaseCommand):
    """Monitor orchestrator performance and metrics"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute orchestrator monitor command"""
        try:
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.error("No running orchestrator found")
            
            # Get monitoring data
            monitoring_data = self._collect_monitoring_data(orchestrator, args)
            
            # Format output based on requested format
            output_format = getattr(args, 'format', 'table')
            
            if output_format == 'json':
                return CommandResult.success(
                    "Orchestrator monitoring data",
                    data=monitoring_data
                )
            else:
                return self._format_monitoring_output(monitoring_data)
                
        except Exception as e:
            return CommandResult.error(f"Failed to monitor orchestrator: {e}")
    
    def _collect_monitoring_data(self, orchestrator: StrategyOrchestrator, args: Namespace) -> Dict[str, Any]:
        """Collect comprehensive monitoring data"""
        try:
            # Get time range
            hours = getattr(args, 'hours', 24)
            since = datetime.now() - timedelta(hours=hours)
            
            monitoring_data = {
                'timestamp': datetime.now().isoformat(),
                'time_range_hours': hours,
                'orchestrator_metrics': orchestrator.orchestration_metrics.copy(),
                'performance_metrics': orchestrator.performance_monitor.collect_performance_metrics(),
                'risk_metrics': orchestrator.risk_manager.get_risk_metrics(),
                'allocation_metrics': {
                    'current_weights': orchestrator.strategy_weights.copy(),
                    'last_rebalance': orchestrator.last_rebalance.isoformat() if orchestrator.last_rebalance else None
                },
                'strategy_status': {
                    name: {
                        'state': orchestrator.strategy_states.get(name, 'unknown'),
                        'weight': orchestrator.strategy_weights.get(name, 0.0),
                        'recent_performance': orchestrator.strategy_returns.get(name, [])[-10:]
                    }
                    for name in orchestrator.active_strategies.keys()
                }
            }
            
            return monitoring_data
            
        except Exception as e:
            self.logger.error(f"Error collecting monitoring data: {e}")
            return {'error': str(e)}
    
    def _format_monitoring_output(self, data: Dict[str, Any]) -> CommandResult:
        """Format monitoring data for table output"""
        try:
            # Create formatted output
            output_lines = [
                "=== Orchestrator Monitoring Report ===",
                f"Timestamp: {data.get('timestamp', 'N/A')}",
                f"Time Range: {data.get('time_range_hours', 'N/A')} hours",
                "",
                "=== Performance Metrics ===",
            ]
            
            # Add performance data
            perf_data = data.get('performance_metrics', {})
            if isinstance(perf_data, dict) and 'portfolio' in perf_data:
                portfolio_perf = perf_data['portfolio']
                output_lines.extend([
                    f"Total Return: {portfolio_perf.get('total_return', 0.0):.2%}",
                    f"Sharpe Ratio: {portfolio_perf.get('sharpe_ratio', 0.0):.2f}",
                    f"Max Drawdown: {portfolio_perf.get('max_drawdown', 0.0):.2%}",
                    f"Win Rate: {portfolio_perf.get('win_rate', 0.0):.2%}",
                ])
            
            # Add risk data
            output_lines.append("\n=== Risk Metrics ===")
            risk_data = data.get('risk_metrics', {})
            if isinstance(risk_data, dict):
                output_lines.extend([
                    f"Current Drawdown: {risk_data.get('current_drawdown', 0.0):.2%}",
                    f"Portfolio VaR: {risk_data.get('portfolio_var', 0.0):.2%}",
                    f"Max Correlation: {risk_data.get('max_correlation', 0.0):.2f}",
                ])
            
            # Add strategy status
            output_lines.append("\n=== Strategy Status ===")
            strategy_data = data.get('strategy_status', {})
            for name, info in strategy_data.items():
                output_lines.append(f"{name}: {info.get('state', 'unknown')} (weight: {info.get('weight', 0.0):.1%})")
            
            formatted_output = "\n".join(output_lines)
            
            return CommandResult.success(
                "Orchestrator monitoring report",
                message=formatted_output,
                data=data
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to format monitoring output: {e}")


class OrchestratorAPICommand(BaseCommand):
    """Start/stop orchestrator API server"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute API server command"""
        try:
            action = getattr(args, 'action', 'start')
            
            if action == 'start':
                return self._start_api_server(args)
            elif action == 'stop':
                return self._stop_api_server(args)
            else:
                return CommandResult.error(f"Unknown API action: {action}")
                
        except Exception as e:
            return CommandResult.error(f"Failed to manage API server: {e}")
    
    def _start_api_server(self, args: Namespace) -> CommandResult:
        """Start the API server"""
        try:
            # Import API server
            try:
                from ...orchestration.api_server import OrchestratorAPIServer
            except ImportError as e:
                return CommandResult.error(
                    "API server dependencies not available",
                    details=[
                        f"Import error: {e}",
                        "Install FastAPI dependencies: pip install fastapi uvicorn"
                    ]
                )
            
            host = getattr(args, 'host', '127.0.0.1')
            port = getattr(args, 'port', 8080)
            
            # Create and start API server
            api_server = OrchestratorAPIServer(host=host, port=port)
            
            self.logger.info(f"Starting Orchestrator API server on {host}:{port}")
            
            # Run server (this will block)
            api_server.run()
            
            return CommandResult.success(
                "API server started successfully",
                data={
                    'host': host,
                    'port': port,
                    'start_time': datetime.now().isoformat()
                }
            )
            
        except KeyboardInterrupt:
            return CommandResult.success("API server stopped by user")
        except Exception as e:
            return CommandResult.error(f"Failed to start API server: {e}")
    
    def _stop_api_server(self, args: Namespace) -> CommandResult:
        """Stop the API server"""
        # This would require process management to stop a running server
        return CommandResult.warning(
            "API server stop not implemented",
            details=["Use Ctrl+C to stop the running server"]
        )


class OrchestratorInterventionCommand(BaseCommand):
    """Manual intervention commands for orchestrator"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute manual intervention command"""
        try:
            orchestrator = self.context.get_orchestrator_instance()
            
            if not orchestrator:
                return CommandResult.error("No running orchestrator found")
            
            action = getattr(args, 'action', None)
            
            if action == 'pause_strategy':
                return self._pause_strategy(orchestrator, args)
            elif action == 'resume_strategy':
                return self._resume_strategy(orchestrator, args)
            elif action == 'emergency_stop':
                return self._emergency_stop(orchestrator, args)
            elif action == 'force_rebalance':
                return self._force_rebalance(orchestrator, args)
            elif action == 'adjust_allocation':
                return self._adjust_allocation(orchestrator, args)
            else:
                return CommandResult.error(f"Unknown intervention action: {action}")
                
        except Exception as e:
            return CommandResult.error(f"Failed to execute intervention: {e}")
    
    def _pause_strategy(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Pause a specific strategy"""
        try:
            strategy_name = getattr(args, 'strategy', None)
            if not strategy_name:
                return CommandResult.error("Strategy name required for pause action")
            
            if strategy_name not in orchestrator.active_strategies:
                return CommandResult.error(f"Strategy not found: {strategy_name}")
            
            # Pause strategy
            orchestrator.strategy_states[strategy_name] = 'paused'
            
            # Redistribute allocation
            orchestrator.allocation_manager.redistribute_allocation_on_strategy_pause(strategy_name)
            
            return CommandResult.success(
                f"Strategy '{strategy_name}' paused successfully",
                data={
                    'strategy': strategy_name,
                    'action': 'paused',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to pause strategy: {e}")
    
    def _resume_strategy(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Resume a paused strategy"""
        try:
            strategy_name = getattr(args, 'strategy', None)
            if not strategy_name:
                return CommandResult.error("Strategy name required for resume action")
            
            if strategy_name not in orchestrator.active_strategies:
                return CommandResult.error(f"Strategy not found: {strategy_name}")
            
            # Resume strategy
            orchestrator.strategy_states[strategy_name] = 'active'
            
            # Rebalance allocation
            orchestrator.allocation_manager.rebalance_allocations()
            
            return CommandResult.success(
                f"Strategy '{strategy_name}' resumed successfully",
                data={
                    'strategy': strategy_name,
                    'action': 'resumed',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to resume strategy: {e}")
    
    def _emergency_stop(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Execute emergency stop"""
        try:
            reason = getattr(args, 'reason', 'Manual emergency stop')
            
            # Confirm action
            if not self.confirm_action(f"Execute emergency stop? Reason: {reason}"):
                return CommandResult.warning("Emergency stop cancelled")
            
            # Execute emergency stop
            orchestrator.risk_manager.trigger_emergency_stop(reason)
            
            return CommandResult.success(
                "Emergency stop executed",
                data={
                    'action': 'emergency_stop',
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to execute emergency stop: {e}")
    
    def _force_rebalance(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Force allocation rebalancing"""
        try:
            # Confirm action
            if not self.confirm_action("Force allocation rebalancing?"):
                return CommandResult.warning("Rebalancing cancelled")
            
            # Force rebalance
            old_allocations = orchestrator.strategy_weights.copy()
            new_allocations = orchestrator.allocation_manager.rebalance_allocations()
            
            return CommandResult.success(
                "Allocation rebalancing completed",
                data={
                    'action': 'force_rebalance',
                    'old_allocations': old_allocations,
                    'new_allocations': new_allocations,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to force rebalance: {e}")
    
    def _adjust_allocation(self, orchestrator: StrategyOrchestrator, args: Namespace) -> CommandResult:
        """Manually adjust strategy allocation"""
        try:
            strategy_name = getattr(args, 'strategy', None)
            new_weight = getattr(args, 'weight', None)
            
            if not strategy_name or new_weight is None:
                return CommandResult.error("Strategy name and weight required for allocation adjustment")
            
            if strategy_name not in orchestrator.active_strategies:
                return CommandResult.error(f"Strategy not found: {strategy_name}")
            
            # Validate weight
            try:
                new_weight = float(new_weight)
                if not 0.0 <= new_weight <= 1.0:
                    return CommandResult.error("Weight must be between 0.0 and 1.0")
            except ValueError:
                return CommandResult.error("Invalid weight value")
            
            # Adjust allocation
            old_weight = orchestrator.strategy_weights.get(strategy_name, 0.0)
            orchestrator.strategy_weights[strategy_name] = new_weight
            
            # Normalize other weights if needed
            orchestrator.allocation_manager.normalize_allocations()
            
            return CommandResult.success(
                f"Allocation adjusted for '{strategy_name}'",
                data={
                    'strategy': strategy_name,
                    'old_weight': old_weight,
                    'new_weight': new_weight,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to adjust allocation: {e}")
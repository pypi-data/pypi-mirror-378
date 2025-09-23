"""
Command Router
==============

Routes CLI commands to appropriate handlers.
"""

from typing import Dict, Type
from argparse import Namespace

from ..context import CLIContext
from ..result import CommandResult
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler, CLIException
from .base import BaseCommand

# Import command classes (will be created in subsequent files)
from .account import (
    ListAccountsCommand, ListExchangesCommand, ListBrokersCommand,
    AddCryptoCommand, AddForexCommand, EditCryptoCommand, EditForexCommand,
    RemoveAccountCommand, EnableAccountCommand, DisableAccountCommand,
    ValidateAccountsCommand
)
from .bot import (
    StartBotCommand, StopBotCommand, RestartBotCommand, StatusCommand,
    StartInstanceCommand, StopInstanceCommand, RestartInstanceCommand,
    ListInstancesCommand, InstanceStatusCommand, InstanceLogsCommand,
    StartMonitoringCommand, StopMonitoringCommand, InstanceMetricsCommand
)
from .config import (
    InitConfigCommand, ConfigHelpCommand, ListStrategiesCommand,
    ValidateConfigCommand, ConfigStatusCommand, ConfigBackupCommand,
    ConfigRestoreCommand, ConfigMigrateCommand, SystemValidateCommand
)
from .monitoring import (
    MonitorCommand, TradesCommand, ReportCommand, CloseOrdersCommand,
    ComprehensiveStatusCommand
)
from .analytics import (
    AnalyticsCommand, BacktestAnalyticsCommand
)
from .utility import (
    HealthCheckCommand, BackupConfigCommand, ResetCommand
)
from .error_report import (
    ErrorReportCommand, SystemRecoveryCommand, DiagnosticsCommand
)
from .security import SecurityCommand
from .completion import CompletionCommand
from .orchestrator import (
    StartOrchestratorCommand, StopOrchestratorCommand, OrchestratorStatusCommand,
    OrchestratorConfigCommand, OrchestratorMonitorCommand, OrchestratorInterventionCommand,
    OrchestratorAPICommand
)
from .orchestrator_migration import OrchestratorMigrationCommand
from .performance import (
    ProfileStartupCommand, MonitorPerformanceCommand, OptimizeSystemCommand,
    ValidatePerformanceCommand, BenchmarkOperationCommand, PerformanceStatusCommand
)


class CommandRouter:
    """Routes commands to appropriate handlers"""
    
    def __init__(self, context: CLIContext, logger: CLILogger, error_handler: CLIErrorHandler):
        self.context = context
        self.logger = logger
        self.error_handler = error_handler
        
        # Command mapping
        self.commands: Dict[str, Type[BaseCommand]] = {
            # Account management commands
            'list-accounts': ListAccountsCommand,
            'list': ListAccountsCommand,  # Alias
            'list-exchanges': ListExchangesCommand,
            'list-brokers': ListBrokersCommand,
            'add-crypto': AddCryptoCommand,
            'add-forex': AddForexCommand,
            'edit-crypto': EditCryptoCommand,
            'edit-forex': EditForexCommand,
            'remove-account': RemoveAccountCommand,
            'enable-account': EnableAccountCommand,
            'disable-account': DisableAccountCommand,
            'validate-accounts': ValidateAccountsCommand,
            'validate': ValidateAccountsCommand,  # Alias
            
            # Bot control commands
            'start': StartBotCommand,
            'stop': StopBotCommand,
            'restart': RestartBotCommand,
            'status': StatusCommand,
            
            # Advanced process management commands
            'start-instance': StartInstanceCommand,
            'stop-instance': StopInstanceCommand,
            'restart-instance': RestartInstanceCommand,
            'list-instances': ListInstancesCommand,
            'instance-status': InstanceStatusCommand,
            'instance-logs': InstanceLogsCommand,
            'start-monitoring': StartMonitoringCommand,
            'stop-monitoring': StopMonitoringCommand,
            'instance-metrics': InstanceMetricsCommand,
            
            # Configuration commands
            'init-config': InitConfigCommand,
            'config-help': ConfigHelpCommand,
            'list-strategies': ListStrategiesCommand,
            'validate-config': ValidateConfigCommand,
            'config-status': ConfigStatusCommand,
            'config-backup': ConfigBackupCommand,
            'config-restore': ConfigRestoreCommand,
            'config-migrate': ConfigMigrateCommand,
            'system-validate': SystemValidateCommand,
            
            # Monitoring and reporting commands
            'monitor': MonitorCommand,
            'trades': TradesCommand,
            'report': ReportCommand,
            'analytics': AnalyticsCommand,
            'backtest-analytics': BacktestAnalyticsCommand,
            'close-all-orders': CloseOrdersCommand,
            'comprehensive-status': ComprehensiveStatusCommand,
            'full-status': ComprehensiveStatusCommand,  # Alias
            
            # Utility commands
            'health-check': HealthCheckCommand,
            'backup-config': BackupConfigCommand,
            'reset': ResetCommand,
            
            # Error reporting and recovery commands
            'error-report': ErrorReportCommand,
            'system-recovery': SystemRecoveryCommand,
            'diagnostics': DiagnosticsCommand,
            
            # Completion command
            'completion': CompletionCommand,
            
            # Orchestrator commands
            'orchestrator-start': StartOrchestratorCommand,
            'orchestrator-stop': StopOrchestratorCommand,
            'orchestrator-status': OrchestratorStatusCommand,
            'orchestrator-config': OrchestratorConfigCommand,
            'orchestrator-monitor': OrchestratorMonitorCommand,
            'orchestrator-intervention': OrchestratorInterventionCommand,
            'orchestrator-api': OrchestratorAPICommand,
            
            # Orchestrator aliases
            'orch-start': StartOrchestratorCommand,
            'orch-stop': StopOrchestratorCommand,
            'orch-status': OrchestratorStatusCommand,
            'orch-config': OrchestratorConfigCommand,
            'orch-monitor': OrchestratorMonitorCommand,
            'orch-intervention': OrchestratorInterventionCommand,
            'orch-api': OrchestratorAPICommand,
            
            # Migration commands
            'orchestrator-migrate': OrchestratorMigrationCommand,
            'orch-migrate': OrchestratorMigrationCommand,
            
            # Performance commands
            'profile-startup': ProfileStartupCommand,
            'monitor-performance': MonitorPerformanceCommand,
            'optimize-system': OptimizeSystemCommand,
            'validate-performance': ValidatePerformanceCommand,
            'benchmark': BenchmarkOperationCommand,
            'performance-status': PerformanceStatusCommand,
            'perf-status': PerformanceStatusCommand,  # Alias
        }
    
    def route_command(self, command_name: str, args: Namespace) -> CommandResult:
        """Route command to appropriate handler"""
        
        if command_name not in self.commands:
            available_commands = sorted(self.commands.keys())
            return CommandResult.error(
                f"Unknown command: {command_name}",
                suggestions=[
                    f"Available commands: {', '.join(available_commands)}",
                    "Use 'genebot --help' to see all available commands",
                    f"Did you mean one of: {self._suggest_similar_commands(command_name)}"
                ]
            )
        
        # Get command class and instantiate
        command_class = self.commands[command_name]
        
        try:
            command_instance = command_class(self.context, self.logger, self.error_handler)
        except Exception as e:
            return self.error_handler.handle_exception(
                e, f"Failed to initialize command '{command_name}'"
            )
        
        # Execute command
        self.logger.debug(f"Executing command: {command_name}")
        return command_instance.run(args)
    
    def _suggest_similar_commands(self, command_name: str, max_suggestions: int = 3) -> str:
        """Suggest similar command names using simple string matching"""
        suggestions = []
        
        for cmd in self.commands.keys():
            # Simple similarity check
            if command_name in cmd or cmd in command_name:
                suggestions.append(cmd)
            elif self._levenshtein_distance(command_name, cmd) <= 2:
                suggestions.append(cmd)
        
        # Sort by similarity (shorter distance first)
        suggestions.sort(key=lambda x: self._levenshtein_distance(command_name, x))
        
        return ', '.join(suggestions[:max_suggestions]) if suggestions else "none"
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_available_commands(self) -> Dict[str, Type[BaseCommand]]:
        """Get all available commands"""
        return self.commands.copy()
    
    def add_command(self, name: str, command_class: Type[BaseCommand]) -> None:
        """Add a new command to the router"""
        self.commands[name] = command_class
    
    def remove_command(self, name: str) -> bool:
        """Remove a command from the router"""
        if name in self.commands:
            del self.commands[name]
            return True
        return False
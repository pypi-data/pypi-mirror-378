"""
Enhanced Argument Parser
=======================

Enhanced argument parsing with validation and comprehensive help text.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from .utils.validator import CLIValidator
from .utils.error_handler import CLIException


class EnhancedArgumentParser(argparse.ArgumentParser):
    """Enhanced argument parser with validation and better error handling"""
    
    def __init__(self, *args, **kwargs):
        # Set default formatter for better help display
        if 'formatter_class' not in kwargs:
            kwargs['formatter_class'] = argparse.RawDescriptionHelpFormatter
        
        super().__init__(*args, **kwargs)
        self.validator = CLIValidator()
    
    def error(self, message):
        """Override error method to provide better error messages"""
        # Extract command from sys.argv if available
        command = sys.argv[1] if len(sys.argv) > 1 else "genebot"
        
        suggestions = [
            f"Run 'genebot {command} --help' for usage information",
            "Check command syntax and required arguments",
            "Use 'genebot --help' to see all available commands"
        ]
        
        raise CLIException(
            f"Command line error: {message}",
            suggestions=suggestions,
            error_code="INVALID_ARGUMENTS"
        )
    
    def add_common_arguments(self) -> None:
        """Add common arguments used across commands"""
        self.add_argument(
            '--config-path',
            type=Path,
            default=Path('config'),
            help='Path to configuration directory (default: config)'
        )
        
        self.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )
        
        self.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output with detailed information'
        )
        
        self.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress all output except errors'
        )
        
        self.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
        
        self.add_argument(
            '--output-file',
            type=Path,
            help='Write output to file instead of stdout'
        )
        
        self.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
        self.add_argument(
            '--force',
            action='store_true',
            help='Force operation without confirmation prompts'
        )
        
        self.add_argument(
            '--auto-recover',
            action='store_true',
            help='Attempt automatic error recovery when possible'
        )


def create_main_parser() -> EnhancedArgumentParser:
    """Create the main argument parser for GeneBot CLI"""
    
    parser = EnhancedArgumentParser(
        prog='genebot',
        description='GeneBot - Advanced Multi-Market Trading Bot',
        epilog="""
Examples:
  genebot --version                    Show version information
  genebot config-help                  Show configuration guide
  genebot init-config                  Initialize configuration files
  genebot validate-config              Validate configuration files
  genebot config-status                Show configuration status
  genebot config-backup                Backup configuration files
  genebot add-crypto binance --mode demo  Add Binance crypto account
  genebot add-forex oanda --mode demo     Add OANDA forex account
  genebot validate                     Validate configuration
  genebot list-strategies              List all active trading strategies
  genebot start                        Start the trading bot
  genebot status                       Check bot status
  genebot monitor                      Real-time trading monitor
  genebot trades                       Show recent trades and P&L
  genebot close-all-orders             Close all open orders safely
  genebot stop                         Stop the trading bot

For more information, visit: https://github.com/genebot/genebot
        """
    )
    
    # Version argument
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='GeneBot 1.1.29 - Advanced Multi-Market Trading Bot'
    )
    
    # Add common arguments
    parser.add_common_arguments()
    
    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Account management commands
    _add_account_commands(subparsers)
    
    # Bot control commands  
    _add_bot_commands(subparsers)
    
    # Configuration commands
    _add_config_commands(subparsers)
    
    # Monitoring and reporting commands
    _add_monitoring_commands(subparsers)
    
    # Utility commands
    _add_utility_commands(subparsers)
    
    # Error handling and recovery commands
    _add_error_handling_commands(subparsers)
    
    # Orchestrator commands
    _add_orchestrator_commands(subparsers)
    
    return parser


def _add_orchestrator_commands(subparsers) -> None:
    """Add orchestrator management commands"""
    
    # Start orchestrator command
    start_orch_parser = subparsers.add_parser(
        'orchestrator-start',
        aliases=['orch-start'],
        help='Start the strategy orchestrator',
        description='Start the unified strategy orchestration system'
    )
    start_orch_parser.add_argument(
        '--config',
        help='Orchestrator configuration file path'
    )
    start_orch_parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run orchestrator in daemon mode'
    )
    start_orch_parser.add_argument(
        '--strategies',
        nargs='+',
        help='Specific strategies to enable (default: all configured)'
    )
    
    # Stop orchestrator command
    stop_orch_parser = subparsers.add_parser(
        'orchestrator-stop',
        aliases=['orch-stop'],
        help='Stop the strategy orchestrator',
        description='Gracefully stop the running orchestrator'
    )
    stop_orch_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Shutdown timeout in seconds (default: 60)'
    )
    
    # Orchestrator status command
    status_orch_parser = subparsers.add_parser(
        'orchestrator-status',
        aliases=['orch-status'],
        help='Show orchestrator status',
        description='Display current orchestrator status and metrics'
    )
    status_orch_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed status information'
    )
    status_orch_parser.add_argument(
        '--json',
        action='store_true',
        help='Output status in JSON format'
    )
    
    # Orchestrator configuration command
    config_orch_parser = subparsers.add_parser(
        'orchestrator-config',
        aliases=['orch-config'],
        help='Manage orchestrator configuration',
        description='View and manage orchestrator configuration'
    )
    config_orch_parser.add_argument(
        'action',
        choices=['show', 'update', 'validate', 'reload'],
        help='Configuration action to perform'
    )
    config_orch_parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    config_orch_parser.add_argument(
        '--allocation-method',
        choices=['equal_weight', 'performance_based', 'risk_parity', 'custom'],
        help='Update allocation method'
    )
    config_orch_parser.add_argument(
        '--rebalance-frequency',
        choices=['daily', 'weekly', 'monthly'],
        help='Update rebalance frequency'
    )
    config_orch_parser.add_argument(
        '--max-drawdown',
        type=float,
        help='Update maximum portfolio drawdown limit'
    )
    
    # Orchestrator monitoring command
    monitor_orch_parser = subparsers.add_parser(
        'orchestrator-monitor',
        aliases=['orch-monitor'],
        help='Monitor orchestrator performance',
        description='Display real-time orchestrator monitoring information'
    )
    monitor_orch_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Time range in hours for monitoring data (default: 24)'
    )
    monitor_orch_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    monitor_orch_parser.add_argument(
        '--refresh',
        type=int,
        help='Auto-refresh interval in seconds'
    )
    
    # Manual intervention command
    intervention_parser = subparsers.add_parser(
        'orchestrator-intervention',
        aliases=['orch-intervention'],
        help='Manual orchestrator interventions',
        description='Perform manual interventions on the orchestrator'
    )
    intervention_parser.add_argument(
        'action',
        choices=['pause_strategy', 'resume_strategy', 'emergency_stop', 'force_rebalance', 'adjust_allocation'],
        help='Intervention action to perform'
    )
    intervention_parser.add_argument(
        '--strategy',
        help='Strategy name (required for pause/resume actions)'
    )
    intervention_parser.add_argument(
        '--reason',
        help='Reason for intervention (for emergency stop)'
    )
    intervention_parser.add_argument(
        '--allocation',
        help='New allocation weights as JSON string (for adjust_allocation)'
    )
    
    # API server command
    api_orch_parser = subparsers.add_parser(
        'orchestrator-api',
        aliases=['orch-api'],
        help='Manage orchestrator API server',
        description='Start or stop the orchestrator REST API server'
    )
    api_orch_parser.add_argument(
        'action',
        choices=['start', 'stop'],
        help='API server action'
    )
    api_orch_parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='API server host (default: 127.0.0.1)'
    )
    api_orch_parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='API server port (default: 8080)'
    )
    
    # Migration command
    migrate_orch_parser = subparsers.add_parser(
        'orchestrator-migrate',
        aliases=['orch-migrate'],
        help='Migrate existing setup to orchestrator',
        description='Migrate existing genebot configuration to use orchestrator'
    )
    migrate_orch_parser.add_argument(
        'action',
        choices=['analyze', 'backup', 'generate', 'migrate', 'validate', 'guide'],
        help='Migration action to perform'
    )
    migrate_orch_parser.add_argument(
        '--output',
        help='Output path for generated configuration'
    )
    migrate_orch_parser.add_argument(
        '--allocation-method',
        choices=['equal_weight', 'performance_based', 'risk_parity'],
        default='performance_based',
        help='Allocation method for orchestrator (default: performance_based)'
    )
    migrate_orch_parser.add_argument(
        '--rebalance-frequency',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Rebalancing frequency (default: daily)'
    )
    migrate_orch_parser.add_argument(
        '--max-drawdown',
        type=float,
        default=0.10,
        help='Maximum portfolio drawdown (default: 0.10)'
    )
    migrate_orch_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup during migration'
    )


def _add_account_commands(subparsers) -> None:
    """Add account management commands"""
    
    # List commands
    list_parser = subparsers.add_parser(
        'list-accounts',
        aliases=['list'],
        help='List all configured accounts',
        description='Display all configured trading accounts with their status'
    )
    list_parser.add_argument(
        '--type',
        choices=['crypto', 'forex', 'all'],
        default='all',
        help='Filter accounts by type (default: all)'
    )
    list_parser.add_argument(
        '--status',
        choices=['active', 'inactive', 'disabled', 'all'],
        default='all',
        help='Filter accounts by status (default: all)'
    )
    
    # List exchanges/brokers
    subparsers.add_parser(
        'list-exchanges',
        help='List available crypto exchanges',
        description='Show all supported cryptocurrency exchanges'
    )
    
    subparsers.add_parser(
        'list-brokers', 
        help='List available forex brokers',
        description='Show all supported forex brokers'
    )
    
    # Add account commands
    add_crypto_parser = subparsers.add_parser(
        'add-crypto',
        help='Add crypto exchange account',
        description='Add a new cryptocurrency exchange account configuration'
    )
    add_crypto_parser.add_argument(
        'exchange',
        help='Exchange name (e.g., binance, coinbase, kraken)'
    )
    add_crypto_parser.add_argument(
        '--name',
        help='Custom account name (default: exchange-mode)'
    )
    add_crypto_parser.add_argument(
        '--mode',
        choices=['demo', 'live'],
        default='demo',
        help='Account mode (default: demo)'
    )
    add_crypto_parser.add_argument(
        '--enabled',
        action='store_true',
        default=True,
        help='Enable account immediately (default: true)'
    )
    
    add_forex_parser = subparsers.add_parser(
        'add-forex',
        help='Add forex broker account',
        description='Add a new forex broker account configuration'
    )
    add_forex_parser.add_argument(
        'broker',
        help='Broker name (e.g., oanda, ib, mt5)'
    )
    add_forex_parser.add_argument(
        '--name',
        help='Custom account name (default: broker-mode)'
    )
    add_forex_parser.add_argument(
        '--mode',
        choices=['demo', 'live'],
        default='demo',
        help='Account mode (default: demo)'
    )
    add_forex_parser.add_argument(
        '--enabled',
        action='store_true',
        default=True,
        help='Enable account immediately (default: true)'
    )
    
    # Edit account commands
    edit_crypto_parser = subparsers.add_parser(
        'edit-crypto',
        help='Edit crypto exchange account',
        description='Edit an existing cryptocurrency exchange account'
    )
    edit_crypto_parser.add_argument(
        'name',
        help='Account name to edit'
    )
    edit_crypto_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Use interactive editing mode'
    )
    
    edit_forex_parser = subparsers.add_parser(
        'edit-forex',
        help='Edit forex broker account',
        description='Edit an existing forex broker account'
    )
    edit_forex_parser.add_argument(
        'name',
        help='Account name to edit'
    )
    edit_forex_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Use interactive editing mode'
    )
    
    # Remove account commands
    remove_parser = subparsers.add_parser(
        'remove-account',
        help='Remove an account',
        description='Remove a specific trading account'
    )
    remove_parser.add_argument(
        'name',
        help='Account name to remove'
    )
    remove_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    # Account control commands
    enable_parser = subparsers.add_parser(
        'enable-account',
        help='Enable an account',
        description='Enable a disabled trading account'
    )
    enable_parser.add_argument(
        'name',
        help='Account name to enable'
    )
    
    disable_parser = subparsers.add_parser(
        'disable-account',
        help='Disable an account',
        description='Disable an active trading account'
    )
    disable_parser.add_argument(
        'name',
        help='Account name to disable'
    )
    
    # Validation commands
    validate_parser = subparsers.add_parser(
        'validate-accounts',
        aliases=['validate'],
        help='Validate all accounts',
        description='Test connectivity and validate all configured accounts'
    )
    validate_parser.add_argument(
        '--account',
        help='Validate specific account only'
    )
    validate_parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Connection timeout in seconds (default: 30)'
    )


def _add_bot_commands(subparsers) -> None:
    """Add bot control commands"""
    
    # Start command
    start_parser = subparsers.add_parser(
        'start',
        help='Start the trading bot',
        description='Start the GeneBot trading engine with all configured strategies'
    )
    start_parser.add_argument(
        '--config',
        help='Specific configuration file to use'
    )
    start_parser.add_argument(
        '--strategy',
        action='append',
        help='Enable specific strategy only (can be used multiple times)'
    )
    start_parser.add_argument(
        '--account',
        action='append',
        help='Use specific account only (can be used multiple times)'
    )
    start_parser.add_argument(
        '--background',
        action='store_true',
        default=True,
        help='Run bot in background (default: true)'
    )
    start_parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run bot in foreground (overrides --background)'
    )
    
    # Stop command
    stop_parser = subparsers.add_parser(
        'stop',
        help='Stop the trading bot',
        description='Gracefully stop the trading bot and all strategies'
    )
    stop_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Shutdown timeout in seconds (default: 60)'
    )
    stop_parser.add_argument(
        '--force',
        action='store_true',
        help='Force kill the bot process if graceful shutdown fails'
    )
    
    # Restart command
    restart_parser = subparsers.add_parser(
        'restart',
        help='Restart the trading bot',
        description='Stop and restart the trading bot'
    )
    restart_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Shutdown timeout in seconds (default: 60)'
    )
    restart_parser.add_argument(
        '--config',
        help='Specific configuration file to use after restart'
    )
    restart_parser.add_argument(
        '--strategy',
        action='append',
        help='Enable specific strategy only after restart (can be used multiple times)'
    )
    restart_parser.add_argument(
        '--account',
        action='append',
        help='Use specific account only after restart (can be used multiple times)'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show bot status',
        description='Display current status of the trading bot and all components'
    )
    status_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed status information'
    )
    status_parser.add_argument(
        '--json',
        action='store_true',
        help='Output status in JSON format'
    )
    
    # Advanced process management commands
    
    # Start instance command
    start_instance_parser = subparsers.add_parser(
        'start-instance',
        help='Start a named bot instance',
        description='Start a specific bot instance with a unique name'
    )
    start_instance_parser.add_argument(
        'instance_name',
        help='Unique name for this bot instance'
    )
    start_instance_parser.add_argument(
        '--config',
        help='Specific configuration file to use'
    )
    start_instance_parser.add_argument(
        '--strategy',
        action='append',
        help='Enable specific strategy only (can be used multiple times)'
    )
    start_instance_parser.add_argument(
        '--account',
        action='append',
        help='Use specific account only (can be used multiple times)'
    )
    start_instance_parser.add_argument(
        '--background',
        action='store_true',
        default=True,
        help='Run bot in background (default: true)'
    )
    start_instance_parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run bot in foreground (overrides --background)'
    )
    
    # Stop instance command
    stop_instance_parser = subparsers.add_parser(
        'stop-instance',
        help='Stop a named bot instance',
        description='Stop a specific bot instance by name'
    )
    stop_instance_parser.add_argument(
        'instance_name',
        help='Name of the bot instance to stop'
    )
    stop_instance_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Shutdown timeout in seconds (default: 60)'
    )
    stop_instance_parser.add_argument(
        '--force',
        action='store_true',
        help='Force kill the instance process'
    )
    
    # Restart instance command
    restart_instance_parser = subparsers.add_parser(
        'restart-instance',
        help='Restart a named bot instance',
        description='Restart a specific bot instance by name'
    )
    restart_instance_parser.add_argument(
        'instance_name',
        help='Name of the bot instance to restart'
    )
    restart_instance_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Shutdown timeout in seconds (default: 60)'
    )
    
    # List instances command
    list_instances_parser = subparsers.add_parser(
        'list-instances',
        help='List all bot instances',
        description='Show all bot instances and their status'
    )
    list_instances_parser.add_argument(
        '--json',
        action='store_true',
        help='Output instances in JSON format'
    )
    
    # Instance status command
    instance_status_parser = subparsers.add_parser(
        'instance-status',
        help='Show status of a specific bot instance',
        description='Display detailed status of a named bot instance'
    )
    instance_status_parser.add_argument(
        'instance_name',
        help='Name of the bot instance'
    )
    instance_status_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed status information'
    )
    instance_status_parser.add_argument(
        '--json',
        action='store_true',
        help='Output status in JSON format'
    )
    
    # Instance logs command
    instance_logs_parser = subparsers.add_parser(
        'instance-logs',
        help='Show logs for a specific bot instance',
        description='Display recent log entries for a named bot instance'
    )
    instance_logs_parser.add_argument(
        'instance_name',
        help='Name of the bot instance'
    )
    instance_logs_parser.add_argument(
        '--lines',
        type=int,
        default=100,
        help='Number of log lines to show (default: 100)'
    )
    instance_logs_parser.add_argument(
        '--follow',
        action='store_true',
        help='Follow log output (like tail -f)'
    )
    
    # Start monitoring command
    start_monitoring_parser = subparsers.add_parser(
        'start-monitoring',
        help='Start process monitoring',
        description='Start continuous monitoring of all bot instances'
    )
    start_monitoring_parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitoring interval in seconds (default: 60)'
    )
    
    # Stop monitoring command
    subparsers.add_parser(
        'stop-monitoring',
        help='Stop process monitoring',
        description='Stop continuous monitoring of bot instances'
    )
    
    # Instance metrics command
    instance_metrics_parser = subparsers.add_parser(
        'instance-metrics',
        help='Show performance metrics for a bot instance',
        description='Display performance metrics and statistics for a named bot instance'
    )
    instance_metrics_parser.add_argument(
        'instance_name',
        help='Name of the bot instance'
    )
    instance_metrics_parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of metrics to show (default: 50)'
    )
    instance_metrics_parser.add_argument(
        '--json',
        action='store_true',
        help='Output metrics in JSON format'
    )


def _add_config_commands(subparsers) -> None:
    """Add configuration commands"""
    
    # Initialize configuration
    init_parser = subparsers.add_parser(
        'init-config',
        help='Initialize configuration files',
        description='Create default configuration files and directory structure'
    )
    init_parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing configuration files'
    )
    init_parser.add_argument(
        '--template',
        choices=['minimal', 'development', 'production'],
        default='development',
        help='Configuration template to use (default: development)'
    )
    
    # Configuration help
    subparsers.add_parser(
        'config-help',
        help='Show configuration guide',
        description='Display comprehensive configuration setup guide'
    )
    
    # List strategies
    strategies_parser = subparsers.add_parser(
        'list-strategies',
        help='List all active trading strategies',
        description='Display all configured trading strategies and their status'
    )
    strategies_parser.add_argument(
        '--status',
        choices=['active', 'inactive', 'all'],
        default='all',
        help='Filter strategies by status (default: all)'
    )
    
    # Validate configuration
    validate_parser = subparsers.add_parser(
        'validate-config',
        help='Validate configuration files',
        description='Check configuration files for errors and consistency'
    )
    validate_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed validation information'
    )
    
    # Configuration status
    subparsers.add_parser(
        'config-status',
        help='Show configuration status',
        description='Display current configuration status and file information'
    )
    
    # Configuration backup
    backup_parser = subparsers.add_parser(
        'config-backup',
        help='Backup configuration files',
        description='Create backup copies of configuration files'
    )
    backup_parser.add_argument(
        '--file',
        choices=['all', 'bot_config', 'accounts', 'env'],
        default='all',
        help='Specific file to backup (default: all)'
    )
    
    # Configuration restore
    restore_parser = subparsers.add_parser(
        'config-restore',
        help='Restore configuration files from backup',
        description='Restore configuration files from previously created backups'
    )
    restore_parser.add_argument(
        '--file',
        choices=['bot_config', 'accounts', 'env'],
        help='Specific file to restore (if not specified, uses most recent backup)'
    )
    restore_parser.add_argument(
        '--timestamp',
        help='Specific backup timestamp to restore from'
    )
    
    # Configuration migration
    migrate_parser = subparsers.add_parser(
        'config-migrate',
        help='Migrate configuration files to newer versions',
        description='Migrate configuration files to newer format versions'
    )
    migrate_parser.add_argument(
        '--version',
        default='latest',
        help='Target version to migrate to (default: latest)'
    )
    migrate_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show migration plan without applying changes'
    )
    
    # System validation
    system_validate_parser = subparsers.add_parser(
        'system-validate',
        help='Comprehensive system validation',
        description='Perform comprehensive validation of all system components'
    )
    system_validate_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed validation information'
    )


def _add_monitoring_commands(subparsers) -> None:
    """Add monitoring and reporting commands"""
    
    # Monitor command
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Real-time trading monitor',
        description='Display live trading activity and bot status'
    )
    monitor_parser.add_argument(
        '--refresh',
        type=int,
        default=5,
        help='Refresh interval in seconds (default: 5)'
    )
    monitor_parser.add_argument(
        '--account',
        help='Monitor specific account only'
    )
    
    # Trades command
    trades_parser = subparsers.add_parser(
        'trades',
        help='Show recent trades and P&L',
        description='Display recent trading activity and performance metrics'
    )
    trades_parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Number of trades to show (default: 20)'
    )
    trades_parser.add_argument(
        '--account',
        help='Show trades for specific account only'
    )
    trades_parser.add_argument(
        '--days',
        type=int,
        help='Show trades from last N days'
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        'report',
        help='Generate trading reports',
        description='Generate comprehensive trading performance reports'
    )
    report_parser.add_argument(
        'type',
        nargs='?',
        default='summary',
        choices=['summary', 'detailed', 'performance', 'compliance', 'strategy', 'pnl'],
        help='Report type (default: summary)'
    )
    report_parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )
    report_parser.add_argument(
        '--format',
        choices=['text', 'json', 'csv', 'html', 'pdf'],
        default='text',
        help='Output format (default: text)'
    )
    report_parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    report_parser.add_argument(
        '--charts',
        action='store_true',
        help='Include performance charts in HTML/PDF reports'
    )
    
    # Analytics command
    analytics_parser = subparsers.add_parser(
        'analytics',
        help='Advanced trading analytics',
        description='Run advanced analytics and performance analysis'
    )
    analytics_parser.add_argument(
        'type',
        choices=['performance', 'risk', 'correlation', 'attribution', 'optimization'],
        help='Analytics type to run'
    )
    analytics_parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    analytics_parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )
    analytics_parser.add_argument(
        '--format',
        choices=['text', 'json', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Backtest analytics command
    backtest_analytics_parser = subparsers.add_parser(
        'backtest-analytics',
        help='Generate analytics from backtesting results',
        description='Analyze backtesting results and generate comprehensive reports'
    )
    backtest_analytics_parser.add_argument(
        'file',
        help='Path to backtest results file'
    )
    backtest_analytics_parser.add_argument(
        '--output',
        help='Output file path for analytics report'
    )
    backtest_analytics_parser.add_argument(
        '--format',
        choices=['html', 'json', 'pdf'],
        default='html',
        help='Output format (default: html)'
    )
    
    # Close orders command
    close_orders_parser = subparsers.add_parser(
        'close-all-orders',
        help='Close all open orders safely',
        description='Safely close all open orders across all accounts'
    )
    close_orders_parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout in seconds (default: 300)'
    )
    close_orders_parser.add_argument(
        '--account',
        help='Close orders for specific account only'
    )
    
    # Comprehensive status command
    comprehensive_status_parser = subparsers.add_parser(
        'comprehensive-status',
        aliases=['full-status'],
        help='Show comprehensive bot status with resource usage',
        description='Display comprehensive bot status including process monitoring, resource usage, and health metrics'
    )
    comprehensive_status_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed status information including account connectivity'
    )
    comprehensive_status_parser.add_argument(
        '--json',
        action='store_true',
        help='Output status in JSON format'
    )


def _add_utility_commands(subparsers) -> None:
    """Add utility commands"""
    
    # Enhanced help command
    help_parser = subparsers.add_parser(
        'help',
        help='Show help information',
        description='Display help information for commands and topics'
    )
    help_parser.add_argument(
        'topic',
        nargs='?',
        help='Specific command or topic to get help for'
    )
    help_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Launch interactive help system'
    )
    help_parser.add_argument(
        '--examples',
        action='store_true',
        help='Show examples for the specified command'
    )
    
    # Command completion
    completion_parser = subparsers.add_parser(
        'completion',
        help='Command completion utilities',
        description='Install and manage command completion for bash/zsh'
    )
    completion_parser.add_argument(
        '--install',
        action='store_true',
        help='Install bash completion script'
    )
    completion_parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate completion script to stdout'
    )
    completion_parser.add_argument(
        '--shell',
        choices=['bash', 'zsh'],
        default='bash',
        help='Target shell for completion (default: bash)'
    )
    
    # Health check
    health_parser = subparsers.add_parser(
        'health-check',
        help='System health check',
        description='Perform comprehensive system health and readiness check'
    )
    health_parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix detected issues automatically'
    )
    
    # Backup configuration
    backup_parser = subparsers.add_parser(
        'backup-config',
        help='Backup configurations',
        description='Create backup of all configuration files'
    )
    backup_parser.add_argument(
        '--output',
        help='Backup output directory (default: backups/)'
    )
    
    # Reset system
    reset_parser = subparsers.add_parser(
        'reset',
        help='Reset system by cleaning up all data',
        description='Clean up all data and reset system to initial state'
    )
    reset_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    reset_parser.add_argument(
        '--keep-config',
        action='store_true',
        help='Keep configuration files'
    )


def _add_error_handling_commands(subparsers) -> None:
    """Add error handling and recovery commands"""
    
    # Error report command
    error_report_parser = subparsers.add_parser(
        'error-report',
        help='Generate comprehensive error report',
        description='Generate a detailed error report for troubleshooting and support'
    )
    error_report_parser.add_argument(
        '--output',
        help='Output file path (default: logs/errors/error_report_<timestamp>.json)'
    )
    error_report_parser.add_argument(
        '--include-recovery',
        action='store_true',
        help='Include system recovery diagnostics in the report'
    )
    error_report_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Include detailed system information and diagnostics'
    )
    
    # System recovery command
    system_recovery_parser = subparsers.add_parser(
        'system-recovery',
        help='Run comprehensive system recovery',
        description='Perform comprehensive system diagnostics and attempt automatic recovery'
    )
    system_recovery_parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically attempt to fix detected issues'
    )
    system_recovery_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    system_recovery_parser.add_argument(
        '--save-report',
        action='store_true',
        default=True,
        help='Save recovery report to file (default: true)'
    )
    
    # Diagnostics command
    diagnostics_parser = subparsers.add_parser(
        'diagnostics',
        help='Run system diagnostics',
        description='Run system diagnostics without attempting recovery'
    )
    diagnostics_parser.add_argument(
        '--network',
        action='store_true',
        default=True,
        help='Include network connectivity checks (default: true)'
    )
    diagnostics_parser.add_argument(
        '--dependencies',
        action='store_true',
        default=True,
        help='Include dependency checks (default: true)'
    )
    diagnostics_parser.add_argument(
        '--config',
        action='store_true',
        default=True,
        help='Include configuration validation (default: true)'
    )


def _add_orchestrator_commands(subparsers) -> None:
    """Add orchestrator management commands"""
    
    # Start orchestrator command
    start_orch_parser = subparsers.add_parser(
        'orchestrator-start',
        aliases=['orch-start'],
        help='Start the strategy orchestrator',
        description='Start the unified strategy orchestration system'
    )
    start_orch_parser.add_argument(
        '--config',
        help='Path to orchestrator configuration file'
    )
    start_orch_parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run orchestrator in daemon mode'
    )
    start_orch_parser.add_argument(
        '--strategies',
        nargs='*',
        help='Specific strategies to enable (default: all configured)'
    )
    
    # Stop orchestrator command
    stop_orch_parser = subparsers.add_parser(
        'orchestrator-stop',
        aliases=['orch-stop'],
        help='Stop the strategy orchestrator',
        description='Stop the running strategy orchestrator gracefully'
    )
    stop_orch_parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout for graceful shutdown in seconds (default: 30)'
    )
    
    # Orchestrator status command
    status_orch_parser = subparsers.add_parser(
        'orchestrator-status',
        aliases=['orch-status'],
        help='Get orchestrator status and metrics',
        description='Display current status and performance metrics of the orchestrator'
    )
    status_orch_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed status information'
    )
    status_orch_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    
    # Orchestrator configuration command
    config_orch_parser = subparsers.add_parser(
        'orchestrator-config',
        aliases=['orch-config'],
        help='Manage orchestrator configuration',
        description='View and manage orchestrator configuration settings'
    )
    config_orch_parser.add_argument(
        'action',
        choices=['show', 'update', 'validate', 'reload'],
        help='Configuration action to perform'
    )
    config_orch_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    config_orch_parser.add_argument(
        '--allocation-method',
        choices=['equal_weight', 'performance_based', 'risk_parity', 'custom'],
        help='Update allocation method'
    )
    config_orch_parser.add_argument(
        '--rebalance-frequency',
        choices=['daily', 'weekly', 'monthly'],
        help='Update rebalancing frequency'
    )
    config_orch_parser.add_argument(
        '--max-drawdown',
        type=float,
        help='Update maximum portfolio drawdown limit'
    )
    
    # Orchestrator monitoring command
    monitor_orch_parser = subparsers.add_parser(
        'orchestrator-monitor',
        aliases=['orch-monitor'],
        help='Monitor orchestrator performance and metrics',
        description='Real-time monitoring of orchestrator performance and strategy metrics'
    )
    monitor_orch_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Time range for monitoring data in hours (default: 24)'
    )
    monitor_orch_parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    monitor_orch_parser.add_argument(
        '--refresh',
        type=int,
        help='Auto-refresh interval in seconds (for continuous monitoring)'
    )
    
    # Manual intervention command
    intervention_parser = subparsers.add_parser(
        'orchestrator-intervention',
        aliases=['orch-intervention'],
        help='Manual intervention commands for orchestrator',
        description='Execute manual interventions on the running orchestrator'
    )
    intervention_parser.add_argument(
        'action',
        choices=['pause_strategy', 'resume_strategy', 'emergency_stop', 'force_rebalance', 'adjust_allocation'],
        help='Intervention action to perform'
    )
    intervention_parser.add_argument(
        '--strategy',
        help='Strategy name (required for strategy-specific actions)'
    )
    intervention_parser.add_argument(
        '--weight',
        type=float,
        help='New allocation weight (for adjust_allocation action)'
    )
    intervention_parser.add_argument(
        '--reason',
        help='Reason for intervention (for emergency_stop action)'
    )
    intervention_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    # API server command
    api_parser = subparsers.add_parser(
        'orchestrator-api',
        aliases=['orch-api'],
        help='Start/stop orchestrator API server',
        description='Manage the orchestrator REST API server'
    )
    api_parser.add_argument(
        'action',
        choices=['start', 'stop'],
        default='start',
        help='API server action (default: start)'
    )
    api_parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='API server host (default: 127.0.0.1)'
    )
    api_parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='API server port (default: 8080)'
    )
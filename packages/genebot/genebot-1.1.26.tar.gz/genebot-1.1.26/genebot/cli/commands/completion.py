"""
Completion Command
==================

Command completion utilities for bash/zsh shells.
"""

from argparse import Namespace
from pathlib import Path
import os

from ..result import CommandResult
from .base import BaseCommand


class CompletionCommand(BaseCommand):
    """Command completion utilities"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute completion command"""
        install = getattr(args, 'install', False)
        generate = getattr(args, 'generate', False)
        shell = getattr(args, 'shell', 'bash')
        
        self.logger.section("Command Completion")
        
        if install:
            return self._install_completion(shell)
        elif generate:
            return self._generate_completion(shell)
        else:
            return CommandResult.error(
                "No action specified",
                suggestions=[
                    "Use --install to install completion",
                    "Use --generate to generate completion script",
                    "Run 'genebot completion --help' for more options"
                ]
            )
    
    def _install_completion(self, shell: str) -> CommandResult:
        """Install completion script"""
        try:
            completion_script = self._get_completion_script(shell)
            
            if shell == 'bash':
                completion_dir = Path.home() / '.bash_completion.d'
                completion_dir.mkdir(exist_ok=True)
                completion_file = completion_dir / 'genebot'
            elif shell == 'zsh':
                completion_dir = Path.home() / '.zsh' / 'completions'
                completion_dir.mkdir(parents=True, exist_ok=True)
                completion_file = completion_dir / '_genebot'
            else:
                return CommandResult.error(f"Unsupported shell: {shell}")
            
            with open(completion_file, 'w') as f:
                f.write(completion_script)
            
            self.logger.success(f"Completion script installed: {completion_file}")
            
            if shell == 'bash':
                self.logger.info("Add this to your ~/.bashrc:")
                self.logger.info(f"source {completion_file}")
            elif shell == 'zsh':
                self.logger.info("Add this to your ~/.zshrc:")
                self.logger.info(f"fpath=({completion_dir} $fpath)")
                self.logger.info("autoload -U compinit && compinit")
            
            return CommandResult.success("Completion script installed successfully")
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to install completion: {e}",
                suggestions=[
                    "Check file permissions",
                    "Ensure shell configuration directory exists",
                    "Try running with --generate to test script generation"
                ]
            )
    
    def _generate_completion(self, shell: str) -> CommandResult:
        """Generate completion script to stdout"""
        try:
            completion_script = self._get_completion_script(shell)
            print(completion_script)
            return CommandResult.success("Completion script generated")
            
        except Exception as e:
            return CommandResult.error(f"Failed to generate completion: {e}")
    
    def _get_completion_script(self, shell: str) -> str:
        """Get completion script for specified shell"""
        if shell == 'bash':
            return self._get_bash_completion()
        elif shell == 'zsh':
            return self._get_zsh_completion()
        else:
            raise ValueError(f"Unsupported shell: {shell}")
    
    def _get_bash_completion(self) -> str:
        """Generate bash completion script"""
        commands = [
            'list-accounts', 'list', 'list-exchanges', 'list-brokers',
            'add-crypto', 'add-forex', 'edit-crypto', 'edit-forex',
            'remove-account', 'enable-account', 'disable-account',
            'validate-accounts', 'validate', 'start', 'stop', 'restart',
            'status', 'start-instance', 'stop-instance', 'restart-instance',
            'list-instances', 'instance-status', 'instance-logs',
            'start-monitoring', 'stop-monitoring', 'instance-metrics',
            'init-config', 'config-help', 'list-strategies', 'validate-config',
            'config-status', 'config-backup', 'config-restore', 'config-migrate',
            'system-validate', 'monitor', 'trades', 'report', 'analytics',
            'backtest-analytics', 'close-all-orders', 'comprehensive-status',
            'full-status', 'health-check', 'backup-config', 'reset',
            'error-report', 'system-recovery', 'diagnostics', 'completion'
        ]
        
        return f"""#!/bin/bash
# GeneBot bash completion script

_genebot_completion() {{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    
    # Main commands
    opts="{' '.join(commands)}"
    
    # Global options
    global_opts="--help --version --config-path --log-level --verbose --quiet --no-color --output-file --dry-run --force --auto-recover"
    
    case "${{prev}}" in
        genebot)
            COMPREPLY=( $(compgen -W "${{opts}} ${{global_opts}}" -- ${{cur}}) )
            return 0
            ;;
        --log-level)
            COMPREPLY=( $(compgen -W "DEBUG INFO WARNING ERROR" -- ${{cur}}) )
            return 0
            ;;
        --shell)
            COMPREPLY=( $(compgen -W "bash zsh" -- ${{cur}}) )
            return 0
            ;;
        *)
            COMPREPLY=( $(compgen -W "${{global_opts}}" -- ${{cur}}) )
            return 0
            ;;
    esac
}}

complete -F _genebot_completion genebot
"""
    
    def _get_zsh_completion(self) -> str:
        """Generate zsh completion script"""
        return """#compdef genebot

# GeneBot zsh completion script

_genebot() {
    local context state line
    typeset -A opt_args
    
    _arguments -C \\
        '(--help -h)'{--help,-h}'[Show help message]' \\
        '(--version -V)'{--version,-V}'[Show version]' \\
        '--config-path[Configuration directory path]:path:_directories' \\
        '--log-level[Logging level]:(DEBUG INFO WARNING ERROR)' \\
        '(--verbose -v)'{--verbose,-v}'[Enable verbose output]' \\
        '(--quiet -q)'{--quiet,-q}'[Suppress output except errors]' \\
        '--no-color[Disable colored output]' \\
        '--output-file[Output file path]:file:_files' \\
        '--dry-run[Show what would be done]' \\
        '--force[Force operation without confirmation]' \\
        '--auto-recover[Attempt automatic error recovery]' \\
        '1: :_genebot_commands' \\
        '*:: :->args'
    
    case $state in
        args)
            case $words[1] in
                add-crypto|add-forex)
                    _arguments \\
                        '--name[Custom account name]:name:' \\
                        '--mode[Account mode]:(demo live)' \\
                        '--enabled[Enable account immediately]'
                    ;;
                analytics)
                    _arguments \\
                        '--days[Number of days to analyze]:days:' \\
                        '--output[Output file path]:file:_files' \\
                        '--format[Output format]:(text json html)'
                    ;;
                report)
                    _arguments \\
                        '--output[Output file path]:file:_files' \\
                        '--format[Output format]:(text json csv html pdf)' \\
                        '--days[Number of days to analyze]:days:' \\
                        '--charts[Include performance charts]'
                    ;;
                completion)
                    _arguments \\
                        '--install[Install completion script]' \\
                        '--generate[Generate completion script]' \\
                        '--shell[Target shell]:(bash zsh)'
                    ;;
            esac
            ;;
    esac
}

_genebot_commands() {
    local commands
    commands=(
        'list-accounts:List all configured accounts'
        'list:List all configured accounts (alias)'
        'list-exchanges:List available crypto exchanges'
        'list-brokers:List available forex brokers'
        'add-crypto:Add crypto exchange account'
        'add-forex:Add forex broker account'
        'edit-crypto:Edit crypto exchange account'
        'edit-forex:Edit forex broker account'
        'remove-account:Remove an account'
        'enable-account:Enable an account'
        'disable-account:Disable an account'
        'validate-accounts:Validate all accounts'
        'validate:Validate all accounts (alias)'
        'start:Start the trading bot'
        'stop:Stop the trading bot'
        'restart:Restart the trading bot'
        'status:Show bot status'
        'start-instance:Start a named bot instance'
        'stop-instance:Stop a named bot instance'
        'restart-instance:Restart a named bot instance'
        'list-instances:List all bot instances'
        'instance-status:Show status of a specific bot instance'
        'instance-logs:Show logs for a specific bot instance'
        'start-monitoring:Start process monitoring'
        'stop-monitoring:Stop process monitoring'
        'instance-metrics:Show performance metrics for a bot instance'
        'init-config:Initialize configuration files'
        'config-help:Show configuration guide'
        'list-strategies:List all active trading strategies'
        'validate-config:Validate configuration files'
        'config-status:Show configuration status'
        'config-backup:Backup configuration files'
        'config-restore:Restore configuration files from backup'
        'config-migrate:Migrate configuration files to newer versions'
        'system-validate:Comprehensive system validation'
        'monitor:Real-time trading monitor'
        'trades:Show recent trades and P&L'
        'report:Generate trading reports'
        'analytics:Advanced trading analytics'
        'backtest-analytics:Generate analytics from backtesting results'
        'close-all-orders:Close all open orders safely'
        'comprehensive-status:Show comprehensive bot status'
        'full-status:Show comprehensive bot status (alias)'
        'health-check:System health check'
        'backup-config:Backup configurations'
        'reset:Reset system by cleaning up all data'
        'error-report:Generate comprehensive error report'
        'system-recovery:Run comprehensive system recovery'
        'diagnostics:Run system diagnostics'
        'completion:Command completion utilities'
    )
    
    _describe 'commands' commands
}

_genebot "$@"
"""
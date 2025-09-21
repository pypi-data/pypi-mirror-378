"""
CLI Command Completion and Help
===============================

Enhanced command completion, help system, and interactive guidance for better user experience.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import argparse
import textwrap

from .formatting import ColorFormatter, Icons
from .output_manager import OutputManager, OutputMode


class CommandCompletion:
    """Command completion utilities"""
    
    def __init__(self):
        self.commands = {}
        self.subcommands = {}
        self.options = {}
    
    def register_command(self, command: str, subcommands: List[str] = None, 
                        options: List[str] = None, description: str = "") -> None:
        """Register a command for completion"""
        self.commands[command] = {
            'description': description,
            'subcommands': subcommands or [],
            'options': options or []
        }
        
        if subcommands:
            self.subcommands[command] = subcommands
        
        if options:
            self.options[command] = options
    
    def get_completions(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Get completions for the given text"""
        words = line.split()
        
        if not words:
            return list(self.commands.keys())
        
        # Complete main command
        if len(words) == 1 and not line.endswith(' '):
            return [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        
        # Complete subcommand or options
        if len(words) >= 1:
            main_command = words[0]
            
            if main_command in self.commands:
                cmd_info = self.commands[main_command]
                
                # If we're completing after the main command
                if len(words) == 2 and not line.endswith(' '):
                    # Complete subcommands and options
                    completions = []
                    completions.extend([sub for sub in cmd_info['subcommands'] if sub.startswith(text)])
                    completions.extend([opt for opt in cmd_info['options'] if opt.startswith(text)])
                    return completions
                
                # If we have a subcommand, complete its options
                elif len(words) >= 2:
                    subcommand = words[1]
                    if subcommand in cmd_info['subcommands']:
                        # Return options for this subcommand
                        return [opt for opt in cmd_info['options'] if opt.startswith(text)]
        
        return []
    
    def generate_bash_completion(self) -> str:
        """Generate bash completion script"""
        script_lines = [
            "#!/bin/bash",
            "",
            "_genebot_completion() {",
            "    local cur prev opts",
            "    COMPREPLY=()",
            "    cur=\"${COMP_WORDS[COMP_CWORD]}\"",
            "    prev=\"${COMP_WORDS[COMP_CWORD-1]}\"",
            "",
            "    # Main commands",
            f"    local commands=\"{' '.join(self.commands.keys())}\"",
            "",
            "    if [[ ${COMP_CWORD} == 1 ]]; then",
            "        COMPREPLY=($(compgen -W \"${commands}\" -- ${cur}))",
            "        return 0",
            "    fi",
            "",
            "    # Subcommands and options",
            "    case \"${COMP_WORDS[1]}\" in"
        ]
        
        for command, info in self.commands.items():
            if info['subcommands'] or info['options']:
                subcommands = ' '.join(info['subcommands'])
                options = ' '.join(info['options'])
                all_completions = f"{subcommands} {options}".strip()
                
                script_lines.extend([
                    f"        {command})",
                    f"            COMPREPLY=($(compgen -W \"{all_completions}\" -- ${{cur}}))",
                    "            return 0",
                    "            ;;"
                ])
        
        script_lines.extend([
            "    esac",
            "}",
            "",
            "complete -F _genebot_completion genebot"
        ])
        
        return '\n'.join(script_lines)
    
    def install_bash_completion(self, install_path: Path = None) -> bool:
        """Install bash completion script"""
        if install_path is None:
            # Try common completion directories
            completion_dirs = [
                Path.home() / '.bash_completion.d',
                Path('/usr/local/etc/bash_completion.d'),
                Path('/etc/bash_completion.d')
            ]
            
            for dir_path in completion_dirs:
                if dir_path.exists() and os.access(dir_path, os.W_OK):
                    install_path = dir_path / 'genebot'
                    break
            else:
                # Fallback to user directory
                install_path = Path.home() / '.bash_completion.d' / 'genebot'
                install_path.parent.mkdir(exist_ok=True)
        
        try:
            completion_script = self.generate_bash_completion()
            install_path.write_text(completion_script)
            return True
        except Exception:
            return False


class HelpFormatter:
    """Enhanced help formatter with colors and better layout"""
    
    def __init__(self, use_colors: bool = None):
        self.formatter = ColorFormatter(use_colors)
        self.output = OutputManager(OutputMode.NORMAL, use_colors)
    
    def format_command_help(self, command: str, description: str, usage: str,
                           options: List[Dict[str, str]] = None,
                           examples: List[Dict[str, str]] = None,
                           see_also: List[str] = None) -> str:
        """Format comprehensive command help"""
        lines = []
        
        # Header
        from .formatting import Color
        lines.append(self.formatter.colorize(f"COMMAND: {command}", Color.BOLD))
        lines.append("")
        
        # Description
        if description:
            lines.append(self.formatter.colorize("DESCRIPTION:", Color.BOLD))
            wrapped_desc = textwrap.fill(description, width=70, initial_indent="    ", subsequent_indent="    ")
            lines.append(wrapped_desc)
            lines.append("")
        
        # Usage
        lines.append(self.formatter.colorize("USAGE:", Color.BOLD))
        lines.append(f"    {self.formatter.code(usage)}")
        lines.append("")
        
        # Options
        if options:
            lines.append(self.formatter.colorize("OPTIONS:", Color.BOLD))
            for option in options:
                option_line = f"    {self.formatter.code(option['flag'])}"
                if 'short' in option:
                    option_line += f", {self.formatter.code(option['short'])}"
                lines.append(option_line)
                
                if 'description' in option:
                    desc_wrapped = textwrap.fill(
                        option['description'], 
                        width=60, 
                        initial_indent="        ", 
                        subsequent_indent="        "
                    )
                    lines.append(desc_wrapped)
                
                if 'default' in option:
                    lines.append(f"        Default: {option['default']}")
                
                lines.append("")
        
        # Examples
        if examples:
            lines.append(self.formatter.colorize("EXAMPLES:", Color.BOLD))
            for example in examples:
                if 'description' in example:
                    lines.append(f"    {example['description']}:")
                lines.append(f"    {self.formatter.code(example['command'])}")
                lines.append("")
        
        # See also
        if see_also:
            lines.append(self.formatter.colorize("SEE ALSO:", Color.BOLD))
            see_also_line = "    " + ", ".join(self.formatter.code(cmd) for cmd in see_also)
            lines.append(see_also_line)
            lines.append("")
        
        return '\n'.join(lines)
    
    def format_command_list(self, commands: Dict[str, Dict[str, Any]], 
                           title: str = "Available Commands") -> str:
        """Format a list of commands with descriptions"""
        lines = []
        
        from .formatting import Color
        lines.append(self.formatter.colorize(title.upper(), Color.BOLD))
        lines.append("=" * len(title))
        lines.append("")
        
        # Group commands by category if available
        categories = {}
        for cmd, info in commands.items():
            category = info.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append((cmd, info))
        
        for category, cmd_list in categories.items():
            if len(categories) > 1:
                lines.append(self.formatter.colorize(f"{category}:", Color.CYAN))
                lines.append("")
            
            # Find max command length for alignment
            max_cmd_len = max(len(cmd) for cmd, _ in cmd_list)
            
            for cmd, info in sorted(cmd_list):
                cmd_formatted = self.formatter.code(cmd.ljust(max_cmd_len))
                description = info.get('description', 'No description available')
                
                # Wrap long descriptions
                if len(description) > 50:
                    description = description[:47] + "..."
                
                lines.append(f"  {cmd_formatted}  {description}")
            
            lines.append("")
        
        return '\n'.join(lines)


class InteractiveHelp:
    """Interactive help system with guided assistance"""
    
    def __init__(self, use_colors: bool = None):
        self.formatter = ColorFormatter(use_colors)
        self.output = OutputManager(OutputMode.NORMAL, use_colors)
        self.help_formatter = HelpFormatter(use_colors)
        
        # Help topics and their handlers
        self.help_topics = {
            'getting-started': self._help_getting_started,
            'configuration': self._help_configuration,
            'accounts': self._help_accounts,
            'trading': self._help_trading,
            'monitoring': self._help_monitoring,
            'troubleshooting': self._help_troubleshooting,
            'examples': self._help_examples
        }
    
    def show_interactive_help(self) -> None:
        """Show interactive help menu"""
        self.output.print_header("GeneBot Interactive Help", "Get help with any aspect of GeneBot")
        
        topics = list(self.help_topics.keys())
        topic_descriptions = {
            'getting-started': 'First steps with GeneBot',
            'configuration': 'Setting up configuration files',
            'accounts': 'Managing trading accounts',
            'trading': 'Starting and managing trading bots',
            'monitoring': 'Monitoring bot performance',
            'troubleshooting': 'Common issues and solutions',
            'examples': 'Example commands and workflows'
        }
        
        while True:
            self.output.print_section("Help Topics")
            
            options = []
            for topic in topics:
                description = topic_descriptions.get(topic, topic.replace('-', ' ').title())
                options.append(f"{topic.replace('-', ' ').title()} - {description}")
            
            options.append("Exit Help")
            
            choice = self.output.select_option("Select a help topic:", options)
            
            if choice == len(options) - 1:  # Exit
                break
            
            topic = topics[choice]
            self.help_topics[topic]()
            
            if not self.output.confirm("Would you like to see another help topic?", default=True):
                break
        
        self.output.success("Thanks for using GeneBot help!")
    
    def _help_getting_started(self) -> None:
        """Getting started help"""
        self.output.print_header("Getting Started with GeneBot")
        
        steps = [
            {
                'title': 'Initialize Configuration',
                'command': 'genebot init-config',
                'description': 'Create initial configuration files and directory structure'
            },
            {
                'title': 'Add Trading Accounts',
                'command': 'genebot add-crypto --exchange binance',
                'description': 'Add your first crypto exchange account'
            },
            {
                'title': 'Validate Setup',
                'command': 'genebot validate',
                'description': 'Check that everything is configured correctly'
            },
            {
                'title': 'Start Trading',
                'command': 'genebot start',
                'description': 'Start the trading bot with your configuration'
            },
            {
                'title': 'Monitor Performance',
                'command': 'genebot status',
                'description': 'Check bot status and performance'
            }
        ]
        
        for i, step in enumerate(steps, 1):
            self.output.print_subsection(f"Step {i}: {step['title']}")
            self.output.info(step['description'])
            self.output.info(f"Command: {self.formatter.code(step['command'])}")
            print()
    
    def _help_configuration(self) -> None:
        """Configuration help"""
        self.output.print_header("Configuration Guide")
        
        config_files = [
            {
                'file': 'config/accounts.yaml',
                'description': 'Trading account configurations',
                'example': 'genebot add-crypto --exchange binance'
            },
            {
                'file': 'config/trading_bot_config.yaml',
                'description': 'Bot behavior and strategy settings',
                'example': 'genebot config set strategy.type momentum'
            },
            {
                'file': '.env',
                'description': 'API keys and sensitive credentials',
                'example': 'Edit manually with your API keys'
            }
        ]
        
        for config in config_files:
            self.output.print_subsection(config['file'])
            self.output.info(config['description'])
            self.output.info(f"Setup: {self.formatter.code(config['example'])}")
            print()
    
    def _help_accounts(self) -> None:
        """Account management help"""
        self.output.print_header("Account Management")
        
        commands = [
            ('genebot list-accounts', 'Show all configured accounts'),
            ('genebot add-crypto --exchange binance', 'Add crypto exchange account'),
            ('genebot add-forex --broker oanda', 'Add forex broker account'),
            ('genebot validate-accounts', 'Test account connectivity'),
            ('genebot enable-account myaccount', 'Enable an account'),
            ('genebot disable-account myaccount', 'Disable an account')
        ]
        
        for command, description in commands:
            self.output.info(f"{self.formatter.code(command)}")
            self.output.verbose(f"  {description}")
            print()
    
    def _help_trading(self) -> None:
        """Trading help"""
        self.output.print_header("Trading Operations")
        
        sections = {
            'Bot Control': [
                ('genebot start', 'Start the trading bot'),
                ('genebot stop', 'Stop the trading bot'),
                ('genebot restart', 'Restart the trading bot'),
                ('genebot status', 'Check bot status')
            ],
            'Trading Data': [
                ('genebot trades', 'View recent trades'),
                ('genebot positions', 'View current positions'),
                ('genebot balance', 'Check account balances'),
                ('genebot close-all-orders', 'Close all open orders')
            ]
        }
        
        for section, commands in sections.items():
            self.output.print_subsection(section)
            for command, description in commands:
                self.output.info(f"{self.formatter.code(command)} - {description}")
            print()
    
    def _help_monitoring(self) -> None:
        """Monitoring help"""
        self.output.print_header("Monitoring and Analytics")
        
        commands = [
            ('genebot monitor', 'Real-time monitoring dashboard'),
            ('genebot report --type performance', 'Generate performance report'),
            ('genebot report --type trades', 'Generate trade analysis'),
            ('genebot logs --tail', 'View live log output'),
            ('genebot metrics', 'Show key performance metrics')
        ]
        
        for command, description in commands:
            self.output.info(f"{self.formatter.code(command)}")
            self.output.verbose(f"  {description}")
            print()
    
    def _help_troubleshooting(self) -> None:
        """Troubleshooting help"""
        self.output.print_header("Troubleshooting Guide")
        
        issues = [
            {
                'problem': 'Bot won\'t start',
                'solutions': [
                    'Check configuration with: genebot validate',
                    'Verify account credentials: genebot validate-accounts',
                    'Check logs: genebot logs --errors'
                ]
            },
            {
                'problem': 'API connection errors',
                'solutions': [
                    'Verify API keys in .env file',
                    'Check network connectivity',
                    'Ensure API permissions are correct'
                ]
            },
            {
                'problem': 'No trades being executed',
                'solutions': [
                    'Check strategy configuration',
                    'Verify account has sufficient balance',
                    'Review risk management settings'
                ]
            }
        ]
        
        for issue in issues:
            self.output.print_subsection(f"Problem: {issue['problem']}")
            self.output.info("Solutions:")
            for solution in issue['solutions']:
                self.output.info(f"  • {solution}")
            print()
    
    def _help_examples(self) -> None:
        """Examples help"""
        self.output.print_header("Example Workflows")
        
        workflows = [
            {
                'name': 'Complete Setup',
                'steps': [
                    'genebot init-config',
                    'genebot add-crypto --exchange binance',
                    'genebot validate',
                    'genebot start'
                ]
            },
            {
                'name': 'Daily Monitoring',
                'steps': [
                    'genebot status',
                    'genebot trades --today',
                    'genebot balance',
                    'genebot report --type daily'
                ]
            },
            {
                'name': 'Emergency Stop',
                'steps': [
                    'genebot close-all-orders',
                    'genebot stop',
                    'genebot report --type emergency'
                ]
            }
        ]
        
        for workflow in workflows:
            self.output.print_subsection(workflow['name'])
            for step in workflow['steps']:
                self.output.info(f"  {self.formatter.code(step)}")
            print()


def setup_command_completion() -> CommandCompletion:
    """Set up command completion with all available commands"""
    completion = CommandCompletion()
    
    # Register main commands
    completion.register_command('init-config', 
        description='Initialize configuration files',
        options=['--force', '--template', '--help'])
    
    completion.register_command('add-crypto',
        description='Add cryptocurrency exchange account',
        options=['--exchange', '--name', '--testnet', '--help'])
    
    completion.register_command('add-forex',
        description='Add forex broker account', 
        options=['--broker', '--name', '--demo', '--help'])
    
    completion.register_command('list-accounts',
        description='List all configured accounts',
        options=['--format', '--status', '--help'])
    
    completion.register_command('validate-accounts',
        description='Validate account connectivity',
        options=['--account', '--timeout', '--help'])
    
    completion.register_command('start',
        description='Start the trading bot',
        options=['--config', '--strategy', '--dry-run', '--help'])
    
    completion.register_command('stop',
        description='Stop the trading bot',
        options=['--force', '--timeout', '--help'])
    
    completion.register_command('status',
        description='Show bot status',
        options=['--detailed', '--json', '--help'])
    
    completion.register_command('monitor',
        description='Real-time monitoring',
        options=['--refresh', '--accounts', '--help'])
    
    completion.register_command('trades',
        description='Show trade history',
        options=['--limit', '--account', '--format', '--help'])
    
    completion.register_command('report',
        subcommands=['performance', 'trades', 'risk', 'compliance'],
        options=['--type', '--period', '--format', '--output', '--help'])
    
    completion.register_command('validate',
        description='Validate configuration',
        options=['--fix', '--verbose', '--help'])
    
    completion.register_command('help',
        subcommands=list(completion.commands.keys()) + ['topics', 'interactive'],
        description='Show help information')
    
    return completion
"""
CLI Output Management
====================

Enhanced output management with support for different verbosity levels,
quiet mode, and consistent formatting across all CLI commands.
"""

import sys
import os
from typing import Optional, Dict, Any, List, Union, TextIO
from pathlib import Path
from datetime import datetime
from enum import Enum

from .formatting import ColorFormatter, ProgressIndicator, ProgressBar, Table, InteractivePrompt, Banner, Icons
from ..result import CommandResult, ResultStatus


class OutputMode(Enum):
    """Output verbosity modes"""
    QUIET = "quiet"      # Only errors and critical messages
    NORMAL = "normal"    # Standard output
    VERBOSE = "verbose"  # Detailed output with debug info
    DEBUG = "debug"      # Full debug output


class OutputManager:
    """Centralized output management for CLI operations"""
    
    def __init__(self, mode: OutputMode = OutputMode.NORMAL, use_colors: bool = None, 
                 output_file: Optional[Path] = None):
        self.mode = mode
        self.formatter = ColorFormatter(use_colors)
        self.prompt = InteractivePrompt(use_colors)
        self.banner = Banner(use_colors)
        self.output_file = output_file
        self._file_handle: Optional[TextIO] = None
        
        # Open output file if specified
        if self.output_file:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(self.output_file, 'a', encoding='utf-8')
    
    def __del__(self):
        """Clean up file handle"""
        if self._file_handle:
            self._file_handle.close()
    
    def _should_output(self, level: str) -> bool:
        """Check if message should be output based on current mode"""
        level_hierarchy = {
            'error': 0,
            'warning': 1,
            'info': 2,
            'success': 2,
            'debug': 3,
            'verbose': 3
        }
        
        mode_thresholds = {
            OutputMode.QUIET: 0,
            OutputMode.NORMAL: 2,
            OutputMode.VERBOSE: 3,
            OutputMode.DEBUG: 3
        }
        
        message_level = level_hierarchy.get(level, 2)
        threshold = mode_thresholds.get(self.mode, 2)
        
        return message_level <= threshold
    
    def _write(self, message: str, file: TextIO = None) -> None:
        """Write message to output"""
        if file is None:
            file = sys.stdout
        
        print(message, file=file)
        
        # Also write to file if configured
        if self._file_handle:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._file_handle.write(f"[{timestamp}] {message}\n")
            self._file_handle.flush()
    
    def success(self, message: str) -> None:
        """Output success message"""
        if self._should_output('success'):
            formatted = self.formatter.success(message)
            self._write(formatted)
    
    def error(self, message: str) -> None:
        """Output error message"""
        if self._should_output('error'):
            formatted = self.formatter.error(message)
            self._write(formatted, sys.stderr)
    
    def warning(self, message: str) -> None:
        """Output warning message"""
        if self._should_output('warning'):
            formatted = self.formatter.warning(message)
            self._write(formatted)
    
    def info(self, message: str) -> None:
        """Output info message"""
        if self._should_output('info'):
            formatted = self.formatter.info(message)
            self._write(formatted)
    
    def debug(self, message: str) -> None:
        """Output debug message"""
        if self._should_output('debug'):
            formatted = self.formatter.dim(f"🔍 DEBUG: {message}")
            self._write(formatted)
    
    def verbose(self, message: str) -> None:
        """Output verbose message"""
        if self._should_output('verbose'):
            formatted = self.formatter.dim(f"📝 {message}")
            self._write(formatted)
    
    def print_result(self, result: CommandResult) -> None:
        """Print a command result with appropriate formatting"""
        if result.success:
            if result.status == ResultStatus.WARNING:
                self.warning(result.message)
            elif result.status == ResultStatus.INFO:
                self.info(result.message)
            else:
                self.success(result.message)
        else:
            self.error(result.message)
        
        # Print suggestions if available
        if result.suggestions and self.mode != OutputMode.QUIET:
            self.print_suggestions(result.suggestions)
        
        # Print data if available and in verbose mode
        if result.data and self.mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            self.print_data(result.data)
    
    def print_suggestions(self, suggestions: List[str]) -> None:
        """Print suggestions with proper formatting"""
        if not suggestions or self.mode == OutputMode.QUIET:
            return
        
        self.info("💡 Suggestions:")
        for suggestion in suggestions:
            suggestion_text = f"  • {suggestion}"
            if self.formatter.use_colors:
                suggestion_text = self.formatter.dim(suggestion_text)
            self._write(suggestion_text)
    
    def print_data(self, data: Dict[str, Any], title: str = "Additional Information") -> None:
        """Print structured data"""
        if self.mode == OutputMode.QUIET:
            return
        
        self.info(f"📊 {title}:")
        self._print_dict(data, indent=2)
    
    def _print_dict(self, data: Dict[str, Any], indent: int = 0) -> None:
        """Recursively print dictionary data"""
        for key, value in data.items():
            prefix = " " * indent
            
            if isinstance(value, dict):
                self._write(f"{prefix}{key}:")
                self._print_dict(value, indent + 2)
            elif isinstance(value, list):
                self._write(f"{prefix}{key}:")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._write(f"{prefix}  [{i}]:")
                        self._print_dict(item, indent + 4)
                    else:
                        self._write(f"{prefix}  • {item}")
            else:
                formatted_value = str(value)
                if self.formatter.use_colors:
                    formatted_value = self.formatter.dim(formatted_value)
                self._write(f"{prefix}{key}: {formatted_value}")
    
    def print_table(self, data: List[Dict[str, Any]], columns: List[str], 
                   title: str = None, formatters: Dict[str, callable] = None) -> None:
        """Print data as a formatted table"""
        if self.mode == OutputMode.QUIET or not data:
            return
        
        if title:
            self.info(f"📋 {title}")
        
        # Create table columns
        from .formatting import TableColumn
        table_columns = []
        for col in columns:
            formatter = formatters.get(col) if formatters else None
            table_columns.append(TableColumn(
                header=col.replace('_', ' ').title(),
                width=15,
                formatter=formatter
            ))
        
        # Create and populate table
        table = Table(table_columns, self.formatter.use_colors)
        for row in data:
            values = [row.get(col, '') for col in columns]
            table.add_row(*values)
        
        table.print()
    
    def print_list(self, items: List[str], title: str = None, 
                  status_map: Dict[str, str] = None) -> None:
        """Print a formatted list"""
        if self.mode == OutputMode.QUIET or not items:
            return
        
        if title:
            self.info(f"📋 {title}")
        
        for item in items:
            status = status_map.get(item, 'info') if status_map else 'info'
            
            if status == 'success':
                icon = Icons.SUCCESS
                color = self.formatter.colorize
            elif status == 'error':
                icon = Icons.ERROR
                color = self.formatter.colorize
            elif status == 'warning':
                icon = Icons.WARNING
                color = self.formatter.colorize
            else:
                icon = '•'
                color = lambda x, c: x
            
            formatted_item = f"  {icon} {item}"
            self._write(formatted_item)
    
    def print_header(self, title: str, subtitle: str = "") -> None:
        """Print a formatted header"""
        if self.mode != OutputMode.QUIET:
            self.banner.print_header(title, subtitle)
    
    def print_section(self, title: str) -> None:
        """Print a section header"""
        if self.mode not in (OutputMode.QUIET,):
            self.banner.print_section(title)
    
    def print_subsection(self, title: str) -> None:
        """Print a subsection header"""
        if self.mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            self.banner.print_subsection(title)
    
    def create_progress_indicator(self, message: str = "Processing") -> ProgressIndicator:
        """Create a progress indicator"""
        if self.mode == OutputMode.QUIET:
            # Return a no-op progress indicator for quiet mode
            return NoOpProgressIndicator()
        return ProgressIndicator(message, self.formatter.use_colors)
    
    def create_progress_bar(self, total: int, message: str = "Progress") -> ProgressBar:
        """Create a progress bar"""
        if self.mode == OutputMode.QUIET:
            # Return a no-op progress bar for quiet mode
            return NoOpProgressBar(total)
        return ProgressBar(total, message, use_colors=self.formatter.use_colors)
    
    def confirm(self, message: str, default: bool = False, 
               dangerous: bool = False) -> bool:
        """Ask for user confirmation"""
        if dangerous and not self._confirm_dangerous_operation(message):
            return False
        
        return self.prompt.confirm(message, default)
    
    def _confirm_dangerous_operation(self, message: str) -> bool:
        """Special confirmation for dangerous operations"""
        self.warning("⚠️  DANGEROUS OPERATION")
        self.warning("This action cannot be undone and may cause data loss.")
        
        # First confirmation
        if not self.prompt.confirm("Are you sure you want to continue?", default=False):
            return False
        
        # Second confirmation with typing requirement
        confirmation_text = "DELETE"
        typed_confirmation = self.prompt.input_text(
            f"Type '{confirmation_text}' to confirm this dangerous operation",
            required=True
        )
        
        if typed_confirmation != confirmation_text:
            self.error("Confirmation text does not match. Operation cancelled.")
            return False
        
        return True
    
    def select_option(self, message: str, options: List[str], default: int = 0) -> int:
        """Select from a list of options"""
        return self.prompt.select(message, options, default)
    
    def input_text(self, message: str, default: str = "", required: bool = False,
                  validator: callable = None) -> str:
        """Get text input from user"""
        return self.prompt.input_text(message, default, required, validator)
    
    def input_password(self, message: str, required: bool = True) -> str:
        """Get password input from user"""
        return self.prompt.input_password(message, required)
    
    def print_command_help(self, command: str, description: str, 
                          usage: str, examples: List[str] = None) -> None:
        """Print formatted command help"""
        if self.mode == OutputMode.QUIET:
            return
        
        self.print_header(f"Command: {command}", description)
        
        self.print_section("Usage")
        self._write(f"  {usage}")
        
        if examples:
            self.print_section("Examples")
            for example in examples:
                self._write(f"  {self.formatter.code(example)}")
    
    def print_status_summary(self, status_data: Dict[str, Any]) -> None:
        """Print a formatted status summary"""
        if self.mode == OutputMode.QUIET:
            return
        
        self.print_section("System Status")
        
        # Overall status
        overall_status = status_data.get('overall_status', 'unknown')
        if overall_status == 'healthy':
            self.success(f"System Status: {overall_status.upper()}")
        elif overall_status == 'warning':
            self.warning(f"System Status: {overall_status.upper()}")
        else:
            self.error(f"System Status: {overall_status.upper()}")
        
        # Component statuses
        components = status_data.get('components', {})
        if components:
            self.print_subsection("Component Status")
            for component, status in components.items():
                status_icon = {
                    'healthy': Icons.SUCCESS,
                    'warning': Icons.WARNING,
                    'error': Icons.ERROR,
                    'unknown': Icons.QUESTION
                }.get(status, Icons.QUESTION)
                
                self._write(f"  {status_icon} {component}: {status}")
        
        # Metrics
        metrics = status_data.get('metrics', {})
        if metrics and self.mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            self.print_subsection("Metrics")
            for metric, value in metrics.items():
                self._write(f"  📊 {metric}: {value}")


class NoOpProgressIndicator:
    """No-operation progress indicator for quiet mode"""
    
    def start(self): pass
    def stop(self, success_message=None, error_message=None): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass


class NoOpProgressBar:
    """No-operation progress bar for quiet mode"""
    
    def __init__(self, total: int):
        self.total = total
        self.current = 0
    
    def update(self, increment: int = 1, message: str = None): 
        self.current = min(self.current + increment, self.total)
    
    def set_progress(self, current: int, message: str = None):
        self.current = min(max(current, 0), self.total)
    
    def finish(self, message: str = "Complete"): pass


def create_output_manager(verbose: bool = False, quiet: bool = False, 
                         use_colors: bool = None, output_file: str = None) -> OutputManager:
    """Create an output manager with appropriate settings"""
    if quiet:
        mode = OutputMode.QUIET
    elif verbose:
        mode = OutputMode.VERBOSE
    else:
        mode = OutputMode.NORMAL
    
    output_path = Path(output_file) if output_file else None
    
    return OutputManager(mode, use_colors, output_path)
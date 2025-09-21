"""
Enhanced CLI Logging Utilities
=============================

Comprehensive logging for CLI operations with centralized system integration.
This module provides user-friendly console output while maintaining structured
logging for analysis and debugging.
"""

import logging
import sys
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

# Import centralized logging system
from ...logging.factory import get_cli_logger as get_centralized_cli_logger, CLILogger as BaseCLILogger
from ...logging.context import LogContext, cli_context, set_context, context_scope


class EnhancedCLILogger:
    """
    Enhanced CLI logger with full centralized system integration.
    
    This logger provides:
    - User-friendly console output formatting
    - CLI-specific context and command tracking
    - Integration with centralized logging system
    - Command execution monitoring
    - Progress tracking and reporting
    - Structured logging for analysis
    """
    
    def __init__(self, name: str = "genebot.cli", level: str = "INFO", 
                 log_file: Optional[Path] = None, verbose: bool = False):
        # Use centralized CLI logger
        self.centralized_logger = get_centralized_cli_logger(verbose=verbose)
        self.verbose = verbose
        
        # Keep reference to underlying logger for compatibility
        self.logger = self.centralized_logger.logger
        
        # CLI-specific tracking
        self._current_command: Optional[str] = None
        self._command_start_time: Optional[datetime] = None
        self._command_context: Optional[LogContext] = None
        self._session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._command_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with CLI context"""
        if self.verbose:
            context = self._get_current_context()
            self.centralized_logger.debug(f"🔍 {message}", context=context, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.info(f"ℹ️  {message}", context=context, **kwargs)
    
    def success(self, message: str, **kwargs) -> None:
        """Log success message with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.info(f"✅ {message}", context=context, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.warning(f"⚠️  {message}", context=context, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.error(f"❌ {message}", context=context, **kwargs)
    
    def progress(self, message: str, current: Optional[int] = None, 
                total: Optional[int] = None, **kwargs) -> None:
        """Log progress message with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.progress(f"🔄 {message}", current=current, 
                                       total=total, context=context, **kwargs)
    
    def step(self, step_num: int, total_steps: int, message: str, **kwargs) -> None:
        """Log step progress with CLI context"""
        context = self._get_current_context()
        self.centralized_logger.progress(
            f"📋 Step {step_num}/{total_steps}: {message}", 
            current=step_num, total=total_steps, context=context, **kwargs
        )
    
    def section(self, title: str) -> None:
        """Log section header"""
        separator = "=" * len(title)
        self.centralized_logger.info(f"\n{title}")
        self.centralized_logger.info(separator)
    
    def subsection(self, title: str) -> None:
        """Log subsection header"""
        self.centralized_logger.info(f"\n📌 {title}")
        self.centralized_logger.info("-" * (len(title) + 3))
    
    def _get_current_context(self) -> Optional[LogContext]:
        """Get current CLI context"""
        if self._command_context:
            return self._command_context
        return cli_context("cli", "general")
    
    def command_start(self, command: str, subcommand: str = None, 
                     command_args: Dict[str, Any] = None, **kwargs) -> None:
        """Log command start with enhanced tracking"""
        with self._lock:
            self._current_command = command
            self._command_start_time = datetime.utcnow()
            
            # Create command-specific context
            operation = f"{command}.{subcommand}" if subcommand else command
            self._command_context = cli_context(command, subcommand or "main")
        
        # Set context for the thread
        set_context(self._command_context)
        
        # Log command start
        self.centralized_logger.command_start(
            command=operation, 
            command_args=command_args,
            context=self._command_context,
            session_id=self._session_id,
            **kwargs
        )
    
    def command_end(self, command: str = None, success: bool = True, 
                   result: str = None, error: str = None, **kwargs) -> None:
        """Log command completion with enhanced tracking"""
        cmd = command or self._current_command
        
        if not cmd:
            self.warning("command_end called without active command")
            return
        
        # Calculate execution time
        execution_time = None
        if self._command_start_time:
            execution_time = (datetime.utcnow() - self._command_start_time).total_seconds()
        
        # Log command completion
        if success:
            self.centralized_logger.command_success(
                command=cmd, 
                result=result,
                context=self._command_context,
                execution_time_s=execution_time,
                session_id=self._session_id,
                **kwargs
            )
        else:
            self.centralized_logger.command_error(
                command=cmd, 
                error=error or "Command failed",
                context=self._command_context,
                execution_time_s=execution_time,
                session_id=self._session_id,
                **kwargs
            )
        
        # Store command history
        with self._lock:
            command_record = {
                'command': cmd,
                'start_time': self._command_start_time.isoformat() if self._command_start_time else None,
                'end_time': datetime.utcnow().isoformat(),
                'execution_time_s': execution_time,
                'success': success,
                'result': result,
                'error': error,
                'session_id': self._session_id
            }
            self._command_history.append(command_record)
            
            # Reset current command tracking
            self._current_command = None
            self._command_start_time = None
            self._command_context = None
    
    def list_item(self, item: str, status: str = "info") -> None:
        """Log list item with status"""
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "•",
            "active": "🟢",
            "inactive": "🔴",
            "disabled": "⏸️"
        }
        icon = icons.get(status, "•")
        self.centralized_logger.info(f"  {icon} {item}")
    
    def command_success(self, command: str, message: str = None, **kwargs) -> None:
        """Log command success - compatibility method"""
        self.command_end(command=command, success=True, result=message, **kwargs)
    
    def command_error(self, command: str, error: str = None, **kwargs) -> None:
        """Log command error - compatibility method"""
        self.command_end(command=command, success=False, error=error, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception - compatibility method"""
        context = self._get_current_context()
        self.centralized_logger.error(f"💥 {message}", context=context, **kwargs)
    
    def table_header(self, headers: list) -> None:
        """Log table header"""
        header_line = " | ".join(f"{h:^15}" for h in headers)
        separator = "-" * len(header_line)
        self.centralized_logger.info(f"\n{header_line}")
        self.centralized_logger.info(separator)
    
    def table_row(self, values: list) -> None:
        """Log table row"""
        row_line = " | ".join(f"{str(v):^15}" for v in values)
        self.centralized_logger.info(row_line)
    
    def banner(self, text: str, char: str = "=") -> None:
        """Log banner text"""
        width = max(60, len(text) + 4)
        border = char * width
        padded_text = f"{text:^{width-2}}"
        
        self.centralized_logger.info(f"\n{border}")
        self.centralized_logger.info(f"{char}{padded_text}{char}")
        self.centralized_logger.info(f"{border}\n")
    
    def json_data(self, data: dict, title: str = "Data") -> None:
        """Log JSON data in readable format"""
        import json
        self.centralized_logger.info(f"\n📊 {title}:")
        formatted_json = json.dumps(data, indent=2, default=str)
        for line in formatted_json.split('\n'):
            self.centralized_logger.info(f"  {line}")
    
    @contextmanager
    def command_context(self, command: str, subcommand: str = None, **kwargs):
        """
        Context manager for command execution with automatic logging.
        
        Args:
            command: Main command name
            subcommand: Subcommand name
            **kwargs: Additional context data
            
        Usage:
            with cli_logger.command_context("bot", "start"):
                # Command implementation
                pass
        """
        self.command_start(command, subcommand, **kwargs)
        try:
            yield
            self.command_end(success=True)
        except Exception as e:
            self.command_end(success=False, error=str(e))
            raise
    
    def user_input_prompt(self, prompt: str, **kwargs) -> None:
        """Log user input prompt"""
        context = self._get_current_context()
        self.centralized_logger.info(f"❓ {prompt}", context=context, **kwargs)
    
    def user_response(self, response: str, **kwargs) -> None:
        """Log user response"""
        context = self._get_current_context()
        self.centralized_logger.info(f"💬 User: {response}", context=context, **kwargs)
    
    def validation_error(self, field: str, value: str, reason: str, **kwargs) -> None:
        """Log validation error in CLI context"""
        context = self._get_current_context()
        self.centralized_logger.error(
            f"❌ Validation Error: {field}='{value}' - {reason}",
            context=context,
            **kwargs
        )
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent command execution history.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of command execution records
        """
        with self._lock:
            return self._command_history[-limit:] if self._command_history else []
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current CLI session.
        
        Returns:
            Dictionary containing session summary
        """
        with self._lock:
            total_commands = len(self._command_history)
            successful_commands = sum(1 for cmd in self._command_history if cmd['success'])
            failed_commands = total_commands - successful_commands
            
            # Calculate average execution time
            execution_times = [
                cmd['execution_time_s'] for cmd in self._command_history 
                if cmd['execution_time_s'] is not None
            ]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                'session_id': self._session_id,
                'total_commands': total_commands,
                'successful_commands': successful_commands,
                'failed_commands': failed_commands,
                'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
                'average_execution_time_s': avg_execution_time,
                'current_command': self._current_command,
                'session_start': self._command_history[0]['start_time'] if self._command_history else None
            }
    
    def clear_history(self) -> None:
        """Clear command history (useful for testing)"""
        with self._lock:
            self._command_history.clear()
    
    @classmethod
    def create_cli_logger(cls, verbose: bool = False, log_file: Optional[str] = None) -> 'EnhancedCLILogger':
        """
        Create a standard CLI logger using centralized system.
        
        Note: log_file parameter is ignored as file output is handled
        by the centralized logging configuration.
        """
        return cls(
            name="genebot.cli",
            level="DEBUG" if verbose else "INFO",
            verbose=verbose
        )


# Maintain backward compatibility
CLILogger = EnhancedCLILogger
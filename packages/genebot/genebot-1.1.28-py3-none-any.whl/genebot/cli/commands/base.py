"""
Base Command Class
==================

Base class for all CLI commands with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from argparse import Namespace

from ..context import CLIContext
from ..result import CommandResult
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler


class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    def __init__(self, context: CLIContext, logger: CLILogger, error_handler: CLIErrorHandler, 
                 output_manager=None):
        self.context = context
        self.logger = logger
        self.error_handler = error_handler
        self.output = output_manager
    
    @abstractmethod
    def execute(self, args: Namespace) -> CommandResult:
        """Execute the command with given arguments"""
        pass
    
    def validate_args(self, args: Namespace) -> CommandResult:
        """Validate command arguments (override in subclasses if needed)"""
        return CommandResult.success("Arguments validated")
    
    def pre_execute(self, args: Namespace) -> CommandResult:
        """Pre-execution hook (override in subclasses if needed)"""
        return CommandResult.success("Pre-execution completed")
    
    def post_execute(self, args: Namespace, result: CommandResult) -> CommandResult:
        """Post-execution hook (override in subclasses if needed)"""
        return result
    
    def run(self, args: Namespace) -> CommandResult:
        """Main execution flow with hooks and comprehensive error handling"""
        auto_recover = getattr(args, 'auto_recover', False)
        
        try:
            # Validate arguments
            validation_result = self.validate_args(args)
            if not validation_result.success:
                return validation_result
            
            # Pre-execution
            pre_result = self.pre_execute(args)
            if not pre_result.success:
                return pre_result
            
            # Main execution with error wrapping
            result = self.error_handler.wrap_command_execution(self.execute, args)
            
            # Post-execution
            final_result = self.post_execute(args, result)
            
            return final_result
            
        except Exception as e:
            return self.error_handler.handle_exception(
                e, 
                context=f"Command: {self.__class__.__name__}",
                auto_recover=auto_recover
            )
    
    def handle_validation_errors(self, errors: list, context: str = "") -> CommandResult:
        """Handle validation errors using the error handler"""
        auto_recover = getattr(self.context, 'auto_recover', False)
        return self.error_handler.handle_validation_errors(
            errors, 
            context=context or f"Validation in {self.__class__.__name__}",
            auto_recover=auto_recover
        )
    
    def safe_execute(self, operation, *args, **kwargs):
        """Safely execute an operation with error handling"""
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            return self.error_handler.handle_exception(
                e, 
                context=f"Operation: {operation.__name__ if hasattr(operation, '__name__') else str(operation)}"
            )
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation"""
        if self.context.force:
            return True
        
        suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{message}{suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    def show_progress(self, current: int, total: int, message: str = "") -> None:
        """Show progress indicator"""
        if self.context.verbose:
            percentage = (current / total) * 100 if total > 0 else 0
            bar_length = 30
            filled_length = int(bar_length * current // total) if total > 0 else 0
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            progress_msg = f"Progress: |{bar}| {percentage:.1f}% ({current}/{total})"
            if message:
                progress_msg += f" - {message}"
            
            print(f"\r{progress_msg}", end='', flush=True)
            
            if current >= total:
                print()  # New line when complete
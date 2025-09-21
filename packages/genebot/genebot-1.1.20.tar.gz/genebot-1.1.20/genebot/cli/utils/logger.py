"""
CLI Logging Utilities
====================

Enhanced logging for CLI operations with proper formatting and levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class CLILogger:
    """Enhanced logger for CLI operations"""
    
    def __init__(self, name: str = "genebot.cli", level: str = "INFO", 
                 log_file: Optional[Path] = None, verbose: bool = False):
        self.logger = logging.getLogger(name)
        self.verbose = verbose
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        if self.verbose:
            self.logger.debug(f"🔍 {message}")
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(f"ℹ️  {message}")
    
    def success(self, message: str) -> None:
        """Log success message"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(f"⚠️  {message}")
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(f"❌ {message}")
    
    def progress(self, message: str) -> None:
        """Log progress message"""
        self.logger.info(f"🔄 {message}")
    
    def step(self, step_num: int, total_steps: int, message: str) -> None:
        """Log step progress"""
        self.logger.info(f"📋 Step {step_num}/{total_steps}: {message}")
    
    def section(self, title: str) -> None:
        """Log section header"""
        separator = "=" * len(title)
        self.logger.info(f"\n{title}")
        self.logger.info(separator)
    
    def subsection(self, title: str) -> None:
        """Log subsection header"""
        self.logger.info(f"\n📌 {title}")
        self.logger.info("-" * (len(title) + 3))
    
    def command_start(self, command: str) -> None:
        """Log command start"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logger.info(f"🚀 [{timestamp}] Starting command: {command}")
    
    def command_end(self, command: str, success: bool = True) -> None:
        """Log command completion"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ Completed" if success else "❌ Failed"
        self.logger.info(f"{status} [{timestamp}] Command: {command}")
    
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
        self.logger.info(f"  {icon} {item}")
    
    def table_header(self, headers: list) -> None:
        """Log table header"""
        header_line = " | ".join(f"{h:^15}" for h in headers)
        separator = "-" * len(header_line)
        self.logger.info(f"\n{header_line}")
        self.logger.info(separator)
    
    def table_row(self, values: list) -> None:
        """Log table row"""
        row_line = " | ".join(f"{str(v):^15}" for v in values)
        self.logger.info(row_line)
    
    def banner(self, text: str, char: str = "=") -> None:
        """Log banner text"""
        width = max(60, len(text) + 4)
        border = char * width
        padded_text = f"{text:^{width-2}}"
        
        self.logger.info(f"\n{border}")
        self.logger.info(f"{char}{padded_text}{char}")
        self.logger.info(f"{border}\n")
    
    def json_data(self, data: dict, title: str = "Data") -> None:
        """Log JSON data in readable format"""
        import json
        self.logger.info(f"\n📊 {title}:")
        formatted_json = json.dumps(data, indent=2, default=str)
        for line in formatted_json.split('\n'):
            self.logger.info(f"  {line}")
    
    @classmethod
    def create_cli_logger(cls, verbose: bool = False, log_file: Optional[str] = None) -> 'CLILogger':
        """Create a standard CLI logger"""
        level = "DEBUG" if verbose else "INFO"
        log_path = Path(log_file) if log_file else None
        
        return cls(
            name="genebot.cli",
            level=level,
            log_file=log_path,
            verbose=verbose
        )
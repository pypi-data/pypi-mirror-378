"""
Command Result Management
========================

Standardized result handling for CLI commands.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class ResultStatus(Enum):
    """Command result status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CommandResult:
    """Standardized command result"""
    
    def __init__(self, success: bool, message: str, 
                 status: ResultStatus = ResultStatus.SUCCESS,
                 data: Optional[Dict[str, Any]] = None,
                 suggestions: List[str] = None,
                 error_code: Optional[str] = None):
        self.success = success
        self.message = message
        self.status = status
        self.data = data
        self.suggestions = suggestions or []
        self.error_code = error_code
        
        # Set status based on success if not explicitly provided
        if self.status == ResultStatus.SUCCESS and not self.success:
            self.status = ResultStatus.ERROR
    

    
    @classmethod
    def success(cls, message: str, data: Optional[Dict[str, Any]] = None, 
                suggestions: List[str] = None) -> 'CommandResult':
        """Create a successful result"""
        return cls(
            success=True,
            message=message,
            status=ResultStatus.SUCCESS,
            data=data,
            suggestions=suggestions or []
        )
    
    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None,
              suggestions: List[str] = None) -> 'CommandResult':
        """Create an error result"""
        return cls(
            success=False,
            message=message,
            status=ResultStatus.ERROR,
            error_code=error_code,
            suggestions=suggestions or []
        )
    
    @classmethod
    def warning(cls, message: str, data: Optional[Dict[str, Any]] = None,
                suggestions: List[str] = None) -> 'CommandResult':
        """Create a warning result"""
        return cls(
            success=True,
            message=message,
            status=ResultStatus.WARNING,
            data=data,
            suggestions=suggestions or []
        )
    
    @classmethod
    def info(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create an info result"""
        return cls(
            success=True,
            message=message,
            status=ResultStatus.INFO,
            data=data
        )
    
    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion to the result"""
        self.suggestions.append(suggestion)
    
    def add_data(self, key: str, value: Any) -> None:
        """Add data to the result"""
        if self.data is None:
            self.data = {}
        self.data[key] = value
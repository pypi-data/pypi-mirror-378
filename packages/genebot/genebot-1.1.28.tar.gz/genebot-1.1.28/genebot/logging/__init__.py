"""
Centralized logging system for GeneBot trading bot.

This module provides a unified logging infrastructure that consolidates
all logging configurations and eliminates duplicate handlers.
"""

from .config import LoggingConfig
from .context import LogContext
from .factory import (
    LoggerFactory,
    setup_global_config,
    get_logger,
    get_trade_logger,
    get_cli_logger,
    get_performance_logger,
    get_error_logger,
    get_enhanced_trade_logger,
    get_enhanced_performance_logger,
    get_enhanced_error_logger,
    get_enhanced_cli_logger,
    get_logging_performance_metrics,
    reset_logging_performance_metrics,
    create_lazy_string,
    create_lazy_format,
    get_log_directory_status,
    cleanup_old_log_files
)
from .formatters import StructuredJSONFormatter, SimpleFormatter

__all__ = [
    'LoggingConfig',
    'LogContext', 
    'LoggerFactory',
    'StructuredJSONFormatter',
    'SimpleFormatter',
    'setup_global_config',
    'get_logger',
    'get_trade_logger',
    'get_cli_logger',
    'get_performance_logger',
    'get_error_logger',
    'get_enhanced_trade_logger',
    'get_enhanced_performance_logger',
    'get_enhanced_error_logger',
    'get_enhanced_cli_logger',
    'get_logging_performance_metrics',
    'reset_logging_performance_metrics',
    'create_lazy_string',
    'create_lazy_format',
    'get_log_directory_status',
    'cleanup_old_log_files'
]
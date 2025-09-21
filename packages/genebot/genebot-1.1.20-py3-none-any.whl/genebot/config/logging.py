"""
Minimal logging utilities for GeneBot CLI
"""

import logging
import sys
from typing import Optional


class LogContext:
    """Minimal log context"""
    
    def __init__(self, **kwargs):
        self.context = kwargs
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def get_logger(name: str = "genebot") -> logging.Logger:
    """Get logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set up basic logging if not already configured
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
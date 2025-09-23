"""
GeneBot CLI Package
==================

Modular command-line interface for the GeneBot trading bot.
"""

from .main import main
from .context import CLIContext
from .result import CommandResult

__all__ = ['main', 'CLIContext', 'CommandResult']
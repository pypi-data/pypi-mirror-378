#!/usr/bin/env python3
"""
GeneBot CLI - Command Line Interface
===================================

Main entry point for the GeneBot trading bot CLI application.
This file now delegates to the new modular CLI implementation.
"""

import sys

# Import the new modular CLI
try:
    from genebot.cli.main import main
except ImportError:
    # Fallback for development/testing
    from .main import main


def main_legacy():
    """Legacy main function - now delegates to new modular CLI"""
    return main()


if __name__ == '__main__':
    sys.exit(main())
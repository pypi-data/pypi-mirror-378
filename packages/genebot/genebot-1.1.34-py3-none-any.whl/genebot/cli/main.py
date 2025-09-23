"""
Main CLI Entry Point
===================

Main entry point for the modular GeneBot CLI application.
"""

import sys
from pathlib import Path

from .parser import create_main_parser
from .context import CLIContext
from .result import CommandResult
from .utils.error_handler import CLIErrorHandler, CLIException
from .utils.output_manager import create_output_manager, OutputMode
from .utils.completion import setup_command_completion, InteractiveHelp
from .commands import CommandRouter

# Import centralized logging system
from ..logging.factory import setup_global_config
from ..logging.config import get_default_config
from ..logging.context import LogContext, cli_context, set_context


def print_banner():
    """Print the GeneBot banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ███████╗███╗   ██╗███████╗██████╗  ██████╗ ████████╗║
    ║  ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝║
    ║  ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝██║   ██║   ██║   ║
    ║  ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║   ██║   ║
    ║  ╚██████╔╝███████╗██║ ╚████║███████╗██████╔╝╚██████╔╝   ██║   ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═════╝  ╚═════╝    ╚═╝   ║
    ║                                                               ║
    ║              Advanced Multi-Market Trading Bot               ║
    ║                        Version 1.1.31                        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🚀 Welcome to GeneBot - Your Advanced Trading Companion
    
    Features:
    • Multi-Market Trading (Crypto + Forex)
    • Advanced Strategy Engine
    • Real-Time Risk Management
    • Comprehensive API Validation
    • Cross-Market Arbitrage
    • Portfolio Management
    • Backtesting & Analytics
    • Compliance & Audit Trails
    
    """
    print(banner)


def main() -> int:
    """Main entry point for GeneBot CLI"""
    
    # Create parser and parse arguments
    parser = create_main_parser()
    
    # If no arguments provided, show banner and help
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        return 0
    
    try:
        args = parser.parse_args()
    except CLIException as e:
        error_handler = CLIErrorHandler()
        result = CommandResult.error(e.message, suggestions=e.suggestions)
        error_handler.exit_with_error(result)
    except SystemExit as e:
        # Handle argparse's sys.exit calls
        return e.code
    
    # Create CLI context from arguments
    try:
        context = CLIContext.from_args(args)
    except Exception as e:
        error_handler = CLIErrorHandler()
        result = error_handler.handle_exception(e, "Failed to initialize CLI context")
        error_handler.exit_with_error(result)
    
    # Create enhanced output manager
    output = create_output_manager(
        verbose=context.verbose,
        quiet=getattr(args, 'quiet', False),
        use_colors=not getattr(args, 'no_color', False),
        output_file=getattr(args, 'output_file', None)
    )
    
    # Setup centralized logging if not already configured
    try:
        config = get_default_config()
        config.enable_cli_logging = True
        setup_global_config(config)
    except Exception:
        pass  # Logging may already be configured
    
    # Create enhanced CLI logger
    from .utils.logger import EnhancedCLILogger
    logger = EnhancedCLILogger.create_cli_logger(verbose=context.verbose)
    
    # Create error handler
    error_handler = CLIErrorHandler(verbose=context.verbose)
    
    # Handle special commands
    if hasattr(args, 'command'):
        # Interactive help
        if args.command == 'help' and getattr(args, 'interactive', False):
            help_system = InteractiveHelp(use_colors=not getattr(args, 'no_color', False))
            help_system.show_interactive_help()
            return 0
        
        # Command completion setup
        if args.command == 'completion' and getattr(args, 'install', False):
            completion = setup_command_completion()
            if completion.install_bash_completion():
                output.success("Bash completion installed successfully")
                output.info("Restart your shell or run: source ~/.bashrc")
            else:
                output.error("Failed to install bash completion")
                return 1
            return 0
    
    # Create command router
    try:
        router = CommandRouter(context, logger, error_handler)
    except Exception as e:
        result = error_handler.handle_exception(e, "Failed to initialize command router")
        error_handler.exit_with_error(result)
    
    # Execute command
    try:
        # Set CLI context for logging
        command_context = cli_context(args.command or "help")
        set_context(command_context)
        
        logger.command_start(args.command or "help")
        
        if not args.command:
            print_banner()
            parser.print_help()
            return 0
        
        # Route and execute command
        result = router.route_command(args.command, args)
        
        # Handle result with enhanced output
        if result.success:
            logger.command_success(args.command or "help", str(result.message) if result.message else None)
            output.print_result(result)
            return 0
        else:
            logger.command_error(args.command or "help", str(result.message) if result.message else "Unknown error")
            output.print_result(result)
            return 1
    
    except CLIException as e:
        result = CommandResult.error(
            e.message,
            error_code=e.error_code,
            suggestions=e.suggestions
        )
        logger.command_error(args.command or "unknown", e.message)
        output.print_result(result)
        return 1
    
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        output.warning("Operation cancelled by user")
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        result = error_handler.handle_exception(e, f"Unexpected error in command '{args.command}'")
        logger.exception(f"Unexpected error in command '{args.command}'")
        output.print_result(result)
        return 1


if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
CLI UX Improvements Demo
=======================

Demonstration of the enhanced CLI user experience features including:
- Progress indicators for long-running operations
- Colored output and better formatting
- Interactive prompts for dangerous operations
- Enhanced help system and command completion
- Verbose and quiet modes
"""

import time
import sys
from pathlib import Path

# Add the project root to the path so we can import genebot modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from genebot.cli.utils.formatting import (
    ColorFormatter, ProgressIndicator, ProgressBar, Table, InteractivePrompt,
    Banner, TableColumn, Icons
)
from genebot.cli.utils.output_manager import OutputManager, OutputMode
from genebot.cli.utils.completion import setup_command_completion, InteractiveHelp
from genebot.cli.result import CommandResult


def demo_colored_output():
    """Demonstrate colored output and formatting"""
    print("\n" + "="*60)
    print("🎨 COLORED OUTPUT AND FORMATTING DEMO")
    print("="*60)
    
    formatter = ColorFormatter(use_colors=True)
    
    print("\n📋 Status Messages:")
    print(formatter.success("✅ Trading bot started successfully"))
    print(formatter.error("❌ Failed to connect to exchange API"))
    print(formatter.warning("⚠️  High volatility detected in market"))
    print(formatter.info("ℹ️  Processing 1,234 trades for analysis"))
    
    print("\n📋 Text Formatting:")
    print(f"Normal text vs {formatter.highlight('highlighted text')}")
    print(f"Regular text vs {formatter.dim('dimmed text')}")
    print(f"Command example: {formatter.code('genebot start --config my-config.yaml')}")
    
    print("\n📋 Without Colors (for comparison):")
    formatter_no_color = ColorFormatter(use_colors=False)
    print(formatter_no_color.success("Trading bot started successfully"))
    print(formatter_no_color.error("Failed to connect to exchange API"))


def demo_progress_indicators():
    """Demonstrate progress indicators"""
    print("\n" + "="*60)
    print("⏳ PROGRESS INDICATORS DEMO")
    print("="*60)
    
    print("\n📋 Spinner Progress Indicator:")
    with ProgressIndicator("Validating account credentials", use_colors=True) as progress:
        time.sleep(2)  # Simulate work
    
    print("\n📋 Progress Bar:")
    progress_bar = ProgressBar(100, "Processing trades", use_colors=True)
    
    for i in range(0, 101, 10):
        progress_bar.set_progress(i, f"Processing trade {i}/100")
        time.sleep(0.1)  # Simulate work
    
    print("\n📋 Step-by-step Progress:")
    steps = [
        "Connecting to exchange APIs",
        "Downloading market data", 
        "Analyzing trading patterns",
        "Generating recommendations",
        "Saving results"
    ]
    
    for i, step in enumerate(steps, 1):
        with ProgressIndicator(step, use_colors=True) as progress:
            time.sleep(0.5)  # Simulate work
        print(f"✅ Step {i}/{len(steps)} completed")


def demo_interactive_prompts():
    """Demonstrate interactive prompts"""
    print("\n" + "="*60)
    print("💬 INTERACTIVE PROMPTS DEMO")
    print("="*60)
    
    prompt = InteractivePrompt(use_colors=True)
    
    print("\n📋 Confirmation Prompts:")
    print("(Demo mode - simulating user responses)")
    
    # Simulate responses for demo
    import unittest.mock
    
    with unittest.mock.patch('builtins.input', return_value='y'):
        result = prompt.confirm("Start the trading bot?", default=False)
        print(f"User confirmed: {result}")
    
    with unittest.mock.patch('builtins.input', return_value='n'):
        result = prompt.confirm("Delete all trading data?", default=False)
        print(f"User declined: {result}")
    
    print("\n📋 Option Selection:")
    options = ["Conservative Strategy", "Aggressive Strategy", "Balanced Strategy"]
    
    with unittest.mock.patch('builtins.input', return_value='2'):
        choice = prompt.select("Choose trading strategy:", options)
        print(f"User selected: {options[choice]}")
    
    print("\n📋 Text Input with Validation:")
    
    def email_validator(text):
        return "@" in text and "." in text
    
    with unittest.mock.patch('builtins.input', return_value='trader@example.com'):
        email = prompt.input_text("Enter your email:", validator=email_validator)
        print(f"Valid email entered: {email}")


def demo_table_formatting():
    """Demonstrate table formatting"""
    print("\n" + "="*60)
    print("📊 TABLE FORMATTING DEMO")
    print("="*60)
    
    # Account status table
    columns = [
        TableColumn("Account Name", 20),
        TableColumn("Exchange", 12),
        TableColumn("Status", 10),
        TableColumn("Balance", 15, align='right'),
        TableColumn("P&L", 12, align='right')
    ]
    
    def currency_formatter(value):
        return f"${float(value):,.2f}"
    
    def pnl_formatter(value):
        val = float(value)
        sign = "+" if val >= 0 else ""
        return f"{sign}${val:,.2f}"
    
    columns[3].formatter = currency_formatter
    columns[4].formatter = pnl_formatter
    
    table = Table(columns, use_colors=True)
    table.add_row("Binance Main", "Binance", "Active", "12500.75", "1250.30")
    table.add_row("Coinbase Pro", "Coinbase", "Active", "8750.25", "-125.50")
    table.add_row("Demo Account", "Kraken", "Inactive", "1000.00", "0.00")
    table.add_row("Forex OANDA", "OANDA", "Active", "5000.00", "75.25")
    
    print("\n📋 Trading Accounts Overview:")
    table.print()
    
    # Performance metrics table
    perf_columns = [
        TableColumn("Metric", 20),
        TableColumn("Value", 15, align='right'),
        TableColumn("Change", 12, align='right')
    ]
    
    perf_table = Table(perf_columns, use_colors=True)
    perf_table.add_row("Total Portfolio", "$26,251.00", "+4.2%")
    perf_table.add_row("Daily P&L", "+$1,199.55", "+4.8%")
    perf_table.add_row("Win Rate", "68.5%", "+2.1%")
    perf_table.add_row("Sharpe Ratio", "1.85", "+0.15")
    
    print("\n📋 Performance Metrics:")
    perf_table.print()


def demo_output_modes():
    """Demonstrate different output modes"""
    print("\n" + "="*60)
    print("🔊 OUTPUT MODES DEMO")
    print("="*60)
    
    # Create sample result
    result = CommandResult.success(
        "Trading bot started successfully",
        data={"accounts": 4, "strategies": 3, "uptime": "2h 15m"},
        suggestions=["Monitor performance with 'genebot status'", "View trades with 'genebot trades'"]
    )
    
    print("\n📋 Normal Mode:")
    normal_output = OutputManager(OutputMode.NORMAL, use_colors=True)
    normal_output.print_result(result)
    
    print("\n📋 Verbose Mode:")
    verbose_output = OutputManager(OutputMode.VERBOSE, use_colors=True)
    verbose_output.print_result(result)
    
    print("\n📋 Quiet Mode (errors only):")
    quiet_output = OutputManager(OutputMode.QUIET, use_colors=True)
    quiet_output.print_result(result)  # This won't show much
    
    # Show an error in quiet mode
    error_result = CommandResult.error("Connection failed")
    quiet_output.print_result(error_result)


def demo_enhanced_help():
    """Demonstrate enhanced help system"""
    print("\n" + "="*60)
    print("❓ ENHANCED HELP SYSTEM DEMO")
    print("="*60)
    
    print("\n📋 Command Completion Setup:")
    completion = setup_command_completion()
    
    # Show some completion examples
    print("Available main commands:")
    for cmd in sorted(completion.commands.keys())[:10]:  # Show first 10
        desc = completion.commands[cmd].get('description', 'No description')
        print(f"  • {cmd:<20} - {desc}")
    
    print("\n📋 Bash Completion Script (first few lines):")
    script = completion.generate_bash_completion()
    lines = script.split('\n')[:10]
    for line in lines:
        print(f"  {line}")
    print("  ... (truncated)")
    
    print("\n📋 Interactive Help Topics:")
    help_system = InteractiveHelp(use_colors=True)
    print("Available help topics:")
    for topic in help_system.help_topics.keys():
        print(f"  • {topic.replace('-', ' ').title()}")


def demo_banner_and_headers():
    """Demonstrate banner and header formatting"""
    print("\n" + "="*60)
    print("🎯 BANNER AND HEADERS DEMO")
    print("="*60)
    
    banner = Banner(use_colors=True)
    
    banner.print_header("GeneBot Trading System", "Advanced Multi-Market Trading Platform")
    
    banner.print_section("Account Management")
    print("  • Add and configure trading accounts")
    print("  • Validate API connectivity")
    print("  • Monitor account status")
    
    banner.print_subsection("Crypto Exchanges")
    print("    - Binance, Coinbase, Kraken, etc.")
    
    banner.print_subsection("Forex Brokers")
    print("    - OANDA, Interactive Brokers, MT5")
    
    banner.print_section("Trading Operations")
    print("  • Start/stop trading bots")
    print("  • Monitor real-time performance")
    print("  • Generate detailed reports")


def main():
    """Run all UX improvement demos"""
    print("🚀 GeneBot CLI User Experience Improvements Demo")
    print("=" * 80)
    print("This demo showcases the enhanced CLI features that improve")
    print("user experience, readability, and interaction quality.")
    print("=" * 80)
    
    try:
        demo_banner_and_headers()
        demo_colored_output()
        demo_progress_indicators()
        demo_table_formatting()
        demo_interactive_prompts()
        demo_output_modes()
        demo_enhanced_help()
        
        print("\n" + "="*80)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("All UX improvements are working correctly.")
        print("The CLI now provides:")
        print("  ✅ Colored output for better readability")
        print("  ✅ Progress indicators for long operations")
        print("  ✅ Interactive prompts for safety")
        print("  ✅ Enhanced table formatting")
        print("  ✅ Multiple output modes (quiet/verbose)")
        print("  ✅ Improved help and completion system")
        print("  ✅ Professional banners and headers")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
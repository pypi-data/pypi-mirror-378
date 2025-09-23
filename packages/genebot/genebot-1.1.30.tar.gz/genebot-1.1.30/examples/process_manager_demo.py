#!/usr/bin/env python3
"""
Process Manager Demo
===================

Demonstration of the ProcessManager functionality for bot lifecycle management.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from genebot.cli.utils.process_manager import ProcessManager, ProcessError


def main():
    """Demonstrate ProcessManager functionality"""
    print("🤖 ProcessManager Demo")
    print("=" * 50)
    
    # Initialize ProcessManager
    workspace = Path.cwd()
    pm = ProcessManager(workspace)
    
    print(f"📁 Workspace: {workspace}")
    print(f"📄 PID file: {pm.pid_file}")
    print(f"📋 Log directory: {pm.log_dir}")
    print()
    
    # Check initial status
    print("1️⃣  Checking initial bot status...")
    status = pm.get_bot_status()
    print(f"   Running: {status.running}")
    if status.error_message:
        print(f"   Error: {status.error_message}")
    print()
    
    # Monitor health
    print("2️⃣  Monitoring system health...")
    health = pm.monitor_health()
    print(f"   Timestamp: {health['timestamp']}")
    print(f"   Healthy: {health['healthy']}")
    print(f"   Running: {health['running']}")
    print()
    
    # Demonstrate command building
    print("3️⃣  Building start commands...")
    
    basic_cmd = pm._build_start_command()
    print(f"   Basic: {' '.join(basic_cmd)}")
    
    config_cmd = pm._build_start_command(config_file="config/bot.yaml")
    print(f"   With config: {' '.join(config_cmd)}")
    
    full_cmd = pm._build_start_command(
        config_file="config/bot.yaml",
        strategies=["rsi", "ma"],
        accounts=["binance", "oanda"]
    )
    print(f"   Full options: {' '.join(full_cmd)}")
    print()
    
    # Test PID file operations
    print("4️⃣  Testing PID file operations...")
    
    # Create a test PID file
    test_pid = 99999
    test_cmd = ["python", "main.py"]
    test_log = pm.log_dir / "test.log"
    
    try:
        pm._create_pid_file(test_pid, test_cmd, test_log)
        print(f"   ✅ Created PID file for PID {test_pid}")
        
        # Read it back
        pid_info = pm._read_pid_file()
        if pid_info:
            print(f"   ✅ Read PID file: PID={pid_info['pid']}, CMD={pid_info['command']}")
        
        # Cleanup
        pm._cleanup_pid_file()
        print(f"   ✅ Cleaned up PID file")
        
    except Exception as e:
        print(f"   ❌ PID file operations failed: {e}")
    
    print()
    
    # Demonstrate error handling
    print("5️⃣  Testing error handling...")
    
    try:
        # Try to start when main.py doesn't exist (should fail gracefully)
        if not (workspace / "main.py").exists():
            print("   ℹ️  main.py not found - this will demonstrate error handling")
            status = pm.start_bot()
        else:
            print("   ℹ️  main.py exists - skipping error demo to avoid starting actual bot")
    
    except ProcessError as e:
        print(f"   ✅ Caught ProcessError: {e.message}")
        if e.suggestions:
            print(f"   💡 Suggestions: {', '.join(e.suggestions)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print()
    
    # Show final status
    print("6️⃣  Final status check...")
    final_status = pm.get_bot_status()
    print(f"   Running: {final_status.running}")
    if final_status.pid:
        print(f"   PID: {final_status.pid}")
    if final_status.uptime:
        print(f"   Uptime: {final_status.uptime}")
    
    print()
    print("✅ ProcessManager demo completed!")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
GeneBot CLI Validation Script
============================

Comprehensive validation of CLI commands after package installation.
Tests all CLI functionality to ensure it works correctly.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CLITestResult:
    """Result of a CLI command test"""
    command: str
    success: bool
    message: str
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class CLIValidationReport:
    """Complete CLI validation report"""
    timestamp: str
    version: str
    overall_success: bool
    results: List[CLITestResult]
    summary: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CLIValidator:
    """Comprehensive CLI validator"""
    
    def __init__(self, python_exe: str = None):
        self.python_exe = python_exe or sys.executable
        self.results: List[CLITestResult] = []
        
    def add_result(self, command: str, success: bool, message: str, 
                   output: str = None, error: str = None, execution_time: float = None):
        """Add a CLI test result"""
        result = CLITestResult(
            command=command,
            success=success,
            message=message,
            output=output,
            error=error,
            execution_time=execution_time
        )
        self.results.append(result)
        
        # Log result
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"{command}: {message}")
    
    def run_cli_command(self, args: List[str], timeout: int = 30) -> Tuple[bool, str, str, float]:
        """Run a CLI command and return success, stdout, stderr, execution_time"""
        import time
        
        start_time = time.time()
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "genebot.cli"] + args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            execution_time = time.time() - start_time
            
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr,
                execution_time
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return False, "", f"Command timed out after {timeout}s", execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            return False, "", str(e), execution_time
    
    def test_help_command(self) -> bool:
        """Test help command"""
        logger.info("Testing help command...")
        
        success, output, error, exec_time = self.run_cli_command(["--help"])
        
        if not success:
            self.add_result(
                "genebot --help",
                False,
                f"Help command failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check if help output contains expected content
        expected_content = [
            "GeneBot",
            "usage:",
            "commands:",
            "init-config",
            "start",
            "stop"
        ]
        
        missing_content = []
        output_lower = output.lower()
        for content in expected_content:
            if content.lower() not in output_lower:
                missing_content.append(content)
        
        if missing_content:
            self.add_result(
                "genebot --help",
                False,
                f"Help output missing expected content: {', '.join(missing_content)}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot --help",
            True,
            f"Help command works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_version_command(self) -> bool:
        """Test version command"""
        logger.info("Testing version command...")
        
        success, output, error, exec_time = self.run_cli_command(["--version"])
        
        if not success:
            self.add_result(
                "genebot --version",
                False,
                f"Version command failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check if version output contains version number
        if not output.strip() or "version" not in output.lower():
            self.add_result(
                "genebot --version",
                False,
                f"Version output doesn't contain version info: {output}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot --version",
            True,
            f"Version command works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_init_config_help(self) -> bool:
        """Test init-config help"""
        logger.info("Testing init-config help...")
        
        success, output, error, exec_time = self.run_cli_command(["init-config", "--help"])
        
        if not success:
            self.add_result(
                "genebot init-config --help",
                False,
                f"Init-config help failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check for expected help content
        expected_content = ["init-config", "configuration", "template"]
        missing_content = []
        output_lower = output.lower()
        
        for content in expected_content:
            if content.lower() not in output_lower:
                missing_content.append(content)
        
        if missing_content:
            self.add_result(
                "genebot init-config --help",
                False,
                f"Init-config help missing content: {', '.join(missing_content)}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot init-config --help",
            True,
            f"Init-config help works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_init_config_dry_run(self) -> bool:
        """Test init-config with dry run"""
        logger.info("Testing init-config dry run...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                success, output, error, exec_time = self.run_cli_command([
                    "init-config", "--dry-run", "--template", "development"
                ])
                
                if not success:
                    self.add_result(
                        "genebot init-config --dry-run",
                        False,
                        f"Init-config dry run failed: {error}",
                        output, error, exec_time
                    )
                    return False
                
                # Check output mentions what would be created
                if "would create" not in output.lower() and "dry run" not in output.lower():
                    self.add_result(
                        "genebot init-config --dry-run",
                        False,
                        f"Dry run output doesn't indicate simulation: {output}",
                        output, error, exec_time
                    )
                    return False
                
                self.add_result(
                    "genebot init-config --dry-run",
                    True,
                    f"Init-config dry run works correctly (executed in {exec_time:.2f}s)",
                    output, error, exec_time
                )
                return True
                
            finally:
                os.chdir(original_cwd)
    
    def test_start_help(self) -> bool:
        """Test start command help"""
        logger.info("Testing start command help...")
        
        success, output, error, exec_time = self.run_cli_command(["start", "--help"])
        
        if not success:
            self.add_result(
                "genebot start --help",
                False,
                f"Start help failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check for expected help content
        expected_content = ["start", "trading", "bot"]
        missing_content = []
        output_lower = output.lower()
        
        for content in expected_content:
            if content.lower() not in output_lower:
                missing_content.append(content)
        
        if missing_content:
            self.add_result(
                "genebot start --help",
                False,
                f"Start help missing content: {', '.join(missing_content)}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot start --help",
            True,
            f"Start help works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_stop_help(self) -> bool:
        """Test stop command help"""
        logger.info("Testing stop command help...")
        
        success, output, error, exec_time = self.run_cli_command(["stop", "--help"])
        
        if not success:
            self.add_result(
                "genebot stop --help",
                False,
                f"Stop help failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check for expected help content
        expected_content = ["stop", "trading", "bot"]
        missing_content = []
        output_lower = output.lower()
        
        for content in expected_content:
            if content.lower() not in output_lower:
                missing_content.append(content)
        
        if missing_content:
            self.add_result(
                "genebot stop --help",
                False,
                f"Stop help missing content: {', '.join(missing_content)}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot stop --help",
            True,
            f"Stop help works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_status_help(self) -> bool:
        """Test status command help"""
        logger.info("Testing status command help...")
        
        success, output, error, exec_time = self.run_cli_command(["status", "--help"])
        
        if not success:
            self.add_result(
                "genebot status --help",
                False,
                f"Status help failed: {error}",
                output, error, exec_time
            )
            return False
        
        # Check for expected help content
        expected_content = ["status", "bot"]
        missing_content = []
        output_lower = output.lower()
        
        for content in expected_content:
            if content.lower() not in output_lower:
                missing_content.append(content)
        
        if missing_content:
            self.add_result(
                "genebot status --help",
                False,
                f"Status help missing content: {', '.join(missing_content)}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot status --help",
            True,
            f"Status help works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_account_commands(self) -> bool:
        """Test account management commands"""
        logger.info("Testing account commands...")
        
        # Test account list help
        success, output, error, exec_time = self.run_cli_command(["account", "list", "--help"])
        
        if not success:
            self.add_result(
                "genebot account list --help",
                False,
                f"Account list help failed: {error}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot account list --help",
            True,
            f"Account commands work correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_config_commands(self) -> bool:
        """Test config management commands"""
        logger.info("Testing config commands...")
        
        # Test config validate help
        success, output, error, exec_time = self.run_cli_command(["config", "validate", "--help"])
        
        if not success:
            self.add_result(
                "genebot config validate --help",
                False,
                f"Config validate help failed: {error}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot config validate --help",
            True,
            f"Config commands work correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_strategy_commands(self) -> bool:
        """Test strategy management commands"""
        logger.info("Testing strategy commands...")
        
        # Test strategy list help
        success, output, error, exec_time = self.run_cli_command(["strategy", "list", "--help"])
        
        if not success:
            # Strategy commands might not be implemented yet, so this is a soft failure
            self.add_result(
                "genebot strategy list --help",
                False,
                f"Strategy list help failed (may not be implemented): {error}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot strategy list --help",
            True,
            f"Strategy commands work correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_orchestrator_commands(self) -> bool:
        """Test orchestrator commands"""
        logger.info("Testing orchestrator commands...")
        
        # Test orchestrator help
        success, output, error, exec_time = self.run_cli_command(["orchestrator", "--help"])
        
        if not success:
            # Orchestrator commands might not be fully implemented
            self.add_result(
                "genebot orchestrator --help",
                False,
                f"Orchestrator help failed (may not be implemented): {error}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot orchestrator --help",
            True,
            f"Orchestrator commands work correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def test_error_handling(self) -> bool:
        """Test CLI error handling"""
        logger.info("Testing CLI error handling...")
        
        # Test invalid command
        success, output, error, exec_time = self.run_cli_command(["invalid-command"])
        
        # This should fail, but gracefully
        if success:
            self.add_result(
                "genebot invalid-command",
                False,
                "Invalid command should have failed but didn't",
                output, error, exec_time
            )
            return False
        
        # Check that error message is helpful
        if not error and not output:
            self.add_result(
                "genebot invalid-command",
                False,
                "No error message provided for invalid command",
                output, error, exec_time
            )
            return False
        
        error_text = (error + output).lower()
        if "invalid" not in error_text and "unknown" not in error_text and "not found" not in error_text:
            self.add_result(
                "genebot invalid-command",
                False,
                f"Error message not helpful for invalid command: {error_text}",
                output, error, exec_time
            )
            return False
        
        self.add_result(
            "genebot invalid-command",
            True,
            f"Error handling works correctly (executed in {exec_time:.2f}s)",
            output, error, exec_time
        )
        return True
    
    def run_all_tests(self) -> CLIValidationReport:
        """Run all CLI validation tests"""
        logger.info("Starting comprehensive CLI validation...")
        
        # Clear previous results
        self.results = []
        
        # Define test functions
        tests = [
            ("Help Command", self.test_help_command),
            ("Version Command", self.test_version_command),
            ("Init-Config Help", self.test_init_config_help),
            ("Init-Config Dry Run", self.test_init_config_dry_run),
            ("Start Help", self.test_start_help),
            ("Stop Help", self.test_stop_help),
            ("Status Help", self.test_status_help),
            ("Account Commands", self.test_account_commands),
            ("Config Commands", self.test_config_commands),
            ("Strategy Commands", self.test_strategy_commands),
            ("Orchestrator Commands", self.test_orchestrator_commands),
            ("Error Handling", self.test_error_handling)
        ]
        
        success_count = 0
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                if test_func():
                    success_count += 1
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                self.add_result(
                    test_name,
                    False,
                    f"Test failed with exception: {e}"
                )
        
        # Create summary
        total_count = len(self.results)
        failed_count = total_count - success_count
        overall_success = failed_count == 0
        
        summary = {
            "total": total_count,
            "passed": success_count,
            "failed": failed_count,
            "success_rate": (success_count / total_count * 100) if total_count > 0 else 0
        }
        
        # Get version (try to extract from version command)
        version = "unknown"
        try:
            success, output, _, _ = self.run_cli_command(["--version"])
            if success and output:
                # Extract version from output
                import re
                version_match = re.search(r'(\d+\.\d+\.\d+)', output)
                if version_match:
                    version = version_match.group(1)
        except Exception:
            pass
        
        report = CLIValidationReport(
            timestamp=datetime.now().isoformat(),
            version=version,
            overall_success=overall_success,
            results=self.results,
            summary=summary
        )
        
        logger.info(f"CLI validation complete: {success_count}/{total_count} tests passed")
        return report


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GeneBot CLI Validation")
    parser.add_argument("--python", help="Python executable to use for testing")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output report in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run validation
    validator = CLIValidator(python_exe=args.python)
    report = validator.run_all_tests()
    
    # Output report
    if args.json:
        report_data = report.to_dict()
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"JSON report saved to: {args.output}")
        else:
            print(json.dumps(report_data, indent=2))
    else:
        # Text report
        print("\n" + "="*60)
        print(f"GeneBot CLI Validation Report")
        print(f"Version: {report.version}")
        print(f"Timestamp: {report.timestamp}")
        print("="*60)
        
        print(f"\nSummary:")
        print(f"  Total tests: {report.summary['total']}")
        print(f"  Passed: {report.summary['passed']}")
        print(f"  Failed: {report.summary['failed']}")
        print(f"  Success rate: {report.summary['success_rate']:.1f}%")
        
        print(f"\nOverall result: {'✅ PASS' if report.overall_success else '❌ FAIL'}")
        
        if not report.overall_success:
            print(f"\nFailed tests:")
            for result in report.results:
                if not result.success:
                    print(f"  ❌ {result.command}: {result.message}")
        
        print(f"\nDetailed results:")
        for result in report.results:
            status = "✅" if result.success else "❌"
            exec_time = f" ({result.execution_time:.2f}s)" if result.execution_time else ""
            print(f"  {status} {result.command}: {result.message}{exec_time}")
        
        if args.output:
            # Save text report
            with open(args.output, 'w') as f:
                f.write(f"GeneBot CLI Validation Report\n")
                f.write(f"Version: {report.version}\n")
                f.write(f"Timestamp: {report.timestamp}\n")
                f.write(f"Overall Success: {report.overall_success}\n\n")
                
                f.write(f"Summary:\n")
                f.write(f"  Total: {report.summary['total']}\n")
                f.write(f"  Passed: {report.summary['passed']}\n")
                f.write(f"  Failed: {report.summary['failed']}\n")
                f.write(f"  Success Rate: {report.summary['success_rate']:.1f}%\n\n")
                
                f.write(f"Detailed Results:\n")
                for result in report.results:
                    status = "PASS" if result.success else "FAIL"
                    exec_time = f" ({result.execution_time:.2f}s)" if result.execution_time else ""
                    f.write(f"  [{status}] {result.command}: {result.message}{exec_time}\n")
            
            print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report.overall_success else 1)


if __name__ == "__main__":
    main()
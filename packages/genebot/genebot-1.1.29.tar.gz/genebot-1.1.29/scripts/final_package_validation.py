#!/usr/bin/env python3
"""
Final Package Validation Script
===============================

Comprehensive final validation of the GeneBot package for publication.
This script performs all necessary checks to ensure the package is ready.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinalPackageValidator:
    """Final comprehensive package validator"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = {}
        
    def log_result(self, test_name: str, success: bool, message: str):
        """Log a test result"""
        self.results[test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        level = logging.INFO if success else logging.ERROR
        status = "✅ PASS" if success else "❌ FAIL"
        logger.log(level, f"{status} {test_name}: {message}")
    
    def test_package_build(self) -> bool:
        """Test that package can be built"""
        logger.info("Testing package build...")
        
        try:
            # Clean previous builds
            for pattern in ["dist", "build", "*.egg-info"]:
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            
            # Build package
            result = subprocess.run([
                sys.executable, "-m", "build", "--wheel", "--sdist"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.log_result("Package Build", False, f"Build failed: {result.stderr}")
                return False
            
            # Check output files
            dist_dir = self.project_root / "dist"
            if not dist_dir.exists():
                self.log_result("Package Build", False, "No dist directory created")
                return False
            
            dist_files = list(dist_dir.glob("*"))
            if not dist_files:
                self.log_result("Package Build", False, "No distribution files created")
                return False
            
            # Check for both wheel and source dist
            has_wheel = any(f.suffix == ".whl" for f in dist_files)
            has_sdist = any(f.name.endswith(".tar.gz") for f in dist_files)
            
            if not has_wheel or not has_sdist:
                self.log_result("Package Build", False, f"Missing distribution types (wheel: {has_wheel}, sdist: {has_sdist})")
                return False
            
            self.log_result("Package Build", True, f"Successfully built {len(dist_files)} distribution files")
            return True
            
        except Exception as e:
            self.log_result("Package Build", False, f"Build test failed: {e}")
            return False
    
    def test_package_metadata(self) -> bool:
        """Test package metadata using twine check"""
        logger.info("Testing package metadata...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "twine", "check", "dist/*"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.log_result("Package Metadata", False, f"Metadata validation failed: {result.stderr}")
                return False
            
            self.log_result("Package Metadata", True, "Package metadata is valid")
            return True
            
        except FileNotFoundError:
            # Try to install twine
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "twine"], 
                             check=True, capture_output=True)
                return self.test_package_metadata()  # Retry
            except Exception:
                self.log_result("Package Metadata", False, "Could not install twine for validation")
                return False
        except Exception as e:
            self.log_result("Package Metadata", False, f"Metadata test failed: {e}")
            return False
    
    def test_installation_in_clean_env(self) -> bool:
        """Test installation in a clean virtual environment"""
        logger.info("Testing installation in clean environment...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.log_result("Clean Installation", False, "No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create virtual environment
                venv_path = temp_path / "test_venv"
                result = subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    self.log_result("Clean Installation", False, f"Failed to create venv: {result.stderr}")
                    return False
                
                # Get python executable in venv
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                    pip_exe = venv_path / "bin" / "pip"
                
                # Install the package
                result = subprocess.run([
                    str(pip_exe), "install", str(wheel_file)
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    self.log_result("Clean Installation", False, f"Installation failed: {result.stderr}")
                    return False
                
                # Test import
                result = subprocess.run([
                    str(python_exe), "-c", "import genebot; print('Import successful')"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log_result("Clean Installation", False, f"Import failed: {result.stderr}")
                    return False
                
                self.log_result("Clean Installation", True, "Package installs and imports successfully")
                return True
                
        except Exception as e:
            self.log_result("Clean Installation", False, f"Installation test failed: {e}")
            return False
    
    def test_cli_functionality(self) -> bool:
        """Test CLI functionality after installation"""
        logger.info("Testing CLI functionality...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.log_result("CLI Functionality", False, "No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create virtual environment
                venv_path = temp_path / "test_venv"
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True, timeout=120)
                
                # Get python executable in venv
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                    pip_exe = venv_path / "bin" / "pip"
                
                # Install the package
                subprocess.run([
                    str(pip_exe), "install", str(wheel_file)
                ], check=True, capture_output=True, timeout=300)
                
                # Test CLI help
                result = subprocess.run([
                    str(python_exe), "-m", "genebot.cli", "--help"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log_result("CLI Functionality", False, f"CLI help failed: {result.stderr}")
                    return False
                
                # Check help output contains expected content
                help_output = result.stdout.lower()
                expected_content = ["genebot", "usage", "commands"]
                missing_content = [content for content in expected_content if content not in help_output]
                
                if missing_content:
                    self.log_result("CLI Functionality", False, f"Help missing content: {missing_content}")
                    return False
                
                # Test version command
                result = subprocess.run([
                    str(python_exe), "-m", "genebot.cli", "--version"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log_result("CLI Functionality", False, f"Version command failed: {result.stderr}")
                    return False
                
                # Check version output
                version_output = result.stdout.strip()
                if not version_output or "genebot" not in version_output.lower():
                    self.log_result("CLI Functionality", False, f"Invalid version output: {version_output}")
                    return False
                
                self.log_result("CLI Functionality", True, f"CLI works correctly, version: {version_output}")
                return True
                
        except Exception as e:
            self.log_result("CLI Functionality", False, f"CLI test failed: {e}")
            return False
    
    def test_entry_points(self) -> bool:
        """Test that entry points work correctly"""
        logger.info("Testing entry points...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.log_result("Entry Points", False, "No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create virtual environment
                venv_path = temp_path / "test_venv"
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True, timeout=120)
                
                # Get executables
                if sys.platform == "win32":
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                    genebot_exe = venv_path / "Scripts" / "genebot.exe"
                else:
                    pip_exe = venv_path / "bin" / "pip"
                    genebot_exe = venv_path / "bin" / "genebot"
                
                # Install the package
                subprocess.run([
                    str(pip_exe), "install", str(wheel_file)
                ], check=True, capture_output=True, timeout=300)
                
                # Test genebot entry point
                if genebot_exe.exists():
                    result = subprocess.run([
                        str(genebot_exe), "--version"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode != 0:
                        self.log_result("Entry Points", False, f"Entry point failed: {result.stderr}")
                        return False
                    
                    self.log_result("Entry Points", True, "Entry points work correctly")
                    return True
                else:
                    self.log_result("Entry Points", False, "Entry point executable not created")
                    return False
                
        except Exception as e:
            self.log_result("Entry Points", False, f"Entry point test failed: {e}")
            return False
    
    def test_uninstallation(self) -> bool:
        """Test package uninstallation"""
        logger.info("Testing package uninstallation...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.log_result("Uninstallation", False, "No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create virtual environment
                venv_path = temp_path / "test_venv"
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True, timeout=120)
                
                # Get executables
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                    pip_exe = venv_path / "bin" / "pip"
                
                # Install the package
                subprocess.run([
                    str(pip_exe), "install", str(wheel_file)
                ], check=True, capture_output=True, timeout=300)
                
                # Verify installation
                result = subprocess.run([
                    str(pip_exe), "show", "genebot"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.log_result("Uninstallation", False, "Package not properly installed")
                    return False
                
                # Uninstall package
                result = subprocess.run([
                    str(pip_exe), "uninstall", "genebot", "-y"
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    self.log_result("Uninstallation", False, f"Uninstallation failed: {result.stderr}")
                    return False
                
                # Verify uninstallation
                result = subprocess.run([
                    str(pip_exe), "show", "genebot"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_result("Uninstallation", False, "Package still installed after uninstallation")
                    return False
                
                # Test that import fails
                result = subprocess.run([
                    str(python_exe), "-c", "import genebot"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_result("Uninstallation", False, "Package still importable after uninstallation")
                    return False
                
                self.log_result("Uninstallation", True, "Package uninstalls cleanly")
                return True
                
        except Exception as e:
            self.log_result("Uninstallation", False, f"Uninstallation test failed: {e}")
            return False
    
    def test_package_contents(self) -> bool:
        """Test package contents are correct"""
        logger.info("Testing package contents...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.log_result("Package Contents", False, "No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            # Check wheel contents using zipfile
            import zipfile
            
            with zipfile.ZipFile(wheel_file, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Check for essential files
                essential_files = [
                    "genebot/__init__.py",
                    "genebot/cli/__init__.py",
                    "genebot/cli/main.py",
                    "genebot/config/__init__.py",
                    "genebot/strategies/__init__.py"
                ]
                
                missing_files = []
                for file_path in essential_files:
                    if not any(f.endswith(file_path) for f in file_list):
                        missing_files.append(file_path)
                
                if missing_files:
                    self.log_result("Package Contents", False, f"Missing essential files: {missing_files}")
                    return False
                
                # Check for metadata files
                metadata_files = [f for f in file_list if f.endswith('.dist-info/METADATA')]
                if not metadata_files:
                    self.log_result("Package Contents", False, "No metadata file found")
                    return False
                
                self.log_result("Package Contents", True, f"Package contains {len(file_list)} files with all essentials")
                return True
                
        except Exception as e:
            self.log_result("Package Contents", False, f"Contents test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info("Starting final package validation...")
        
        tests = [
            ("Package Build", self.test_package_build),
            ("Package Metadata", self.test_package_metadata),
            ("Package Contents", self.test_package_contents),
            ("Clean Installation", self.test_installation_in_clean_env),
            ("CLI Functionality", self.test_cli_functionality),
            ("Entry Points", self.test_entry_points),
            ("Uninstallation", self.test_uninstallation)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Test failed with exception: {e}")
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        overall_success = failed_tests == 0
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.results
        }
        
        # Log summary
        if overall_success:
            logger.info("🎉 All validation tests passed! Package is ready for publication.")
        else:
            logger.error(f"❌ {failed_tests} tests failed. Package needs fixes before publication.")
            
            # Log failed tests
            for test_name, result in self.results.items():
                if not result['success']:
                    logger.error(f"  ❌ {test_name}: {result['message']}")
        
        logger.info(f"Final validation complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return summary


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Final GeneBot Package Validation")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output report in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run validation
    validator = FinalPackageValidator()
    report = validator.run_all_tests()
    
    # Output report
    if args.json:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"JSON report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2))
    else:
        # Text report
        print("\n" + "="*60)
        print(f"GeneBot Final Package Validation Report")
        print(f"Timestamp: {report['timestamp']}")
        print("="*60)
        
        print(f"\nSummary:")
        print(f"  Total tests: {report['total_tests']}")
        print(f"  Passed: {report['passed_tests']}")
        print(f"  Failed: {report['failed_tests']}")
        print(f"  Success rate: {report['success_rate']:.1f}%")
        
        if report['overall_success']:
            print(f"\n🎉 Overall result: READY FOR PUBLICATION")
        else:
            print(f"\n❌ Overall result: NOT READY - FIXES NEEDED")
        
        print(f"\nDetailed results:")
        for test_name, result in report['results'].items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {status} {test_name}: {result['message']}")
        
        if args.output:
            # Save text report
            with open(args.output, 'w') as f:
                f.write(f"GeneBot Final Package Validation Report\n")
                f.write(f"Timestamp: {report['timestamp']}\n")
                f.write(f"Overall Success: {report['overall_success']}\n\n")
                
                f.write(f"Summary:\n")
                f.write(f"  Total: {report['total_tests']}\n")
                f.write(f"  Passed: {report['passed_tests']}\n")
                f.write(f"  Failed: {report['failed_tests']}\n")
                f.write(f"  Success Rate: {report['success_rate']:.1f}%\n\n")
                
                f.write(f"Detailed Results:\n")
                for test_name, result in report['results'].items():
                    status = "PASS" if result['success'] else "FAIL"
                    f.write(f"  [{status}] {test_name}: {result['message']}\n")
            
            print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_success'] else 1)


if __name__ == "__main__":
    main()
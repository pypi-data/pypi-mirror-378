#!/usr/bin/env python3
"""
GeneBot Package Preparation Script
=================================

Comprehensive script for final package preparation and validation.
This script handles all aspects of package preparation before publication.
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


class PackagePreparator:
    """Comprehensive package preparation manager"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.version = self._get_version()
        
    def _get_version(self) -> str:
        """Get current version from pyproject.toml"""
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
                return config.get("project", {}).get("version", "unknown")
        except Exception:
            return "unknown"
    
    def clean_build_artifacts(self) -> bool:
        """Clean all build artifacts"""
        logger.info("Cleaning build artifacts...")
        
        try:
            # Patterns to clean
            patterns = [
                "dist",
                "build", 
                "*.egg-info",
                "__pycache__",
                "*.pyc",
                "*.pyo",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                ".coverage"
            ]
            
            cleaned_items = []
            
            for pattern in patterns:
                for path in self.project_root.rglob(pattern):
                    try:
                        if path.is_dir():
                            shutil.rmtree(path)
                            cleaned_items.append(f"dir: {path}")
                        else:
                            path.unlink()
                            cleaned_items.append(f"file: {path}")
                    except Exception as e:
                        logger.warning(f"Could not clean {path}: {e}")
            
            logger.info(f"Cleaned {len(cleaned_items)} items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean build artifacts: {e}")
            return False
    
    def update_version_references(self) -> bool:
        """Update version references across the codebase"""
        logger.info(f"Updating version references to {self.version}...")
        
        try:
            # Files that may contain version references
            version_files = [
                "genebot/__init__.py",
                "genebot/cli/main.py",
                "README_GENEBOT.md",
                "docs/README.md"
            ]
            
            updated_files = []
            
            for file_path in version_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    continue
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update version patterns
                    import re
                    
                    # Pattern for __version__ = "x.x.x"
                    version_pattern = r'__version__\s*=\s*["\'][\d\.]+["\']'
                    if re.search(version_pattern, content):
                        content = re.sub(version_pattern, f'__version__ = "{self.version}"', content)
                        updated_files.append(file_path)
                    
                    # Pattern for Version x.x.x in banner/text
                    banner_pattern = r'Version\s+[\d\.]+'
                    if re.search(banner_pattern, content):
                        content = re.sub(banner_pattern, f'Version {self.version}', content)
                        updated_files.append(file_path)
                    
                    # Write back if changed
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as e:
                    logger.warning(f"Could not update version in {file_path}: {e}")
            
            logger.info(f"Updated version references in {len(set(updated_files))} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update version references: {e}")
            return False
    
    def validate_package_metadata(self) -> bool:
        """Validate package metadata is complete"""
        logger.info("Validating package metadata...")
        
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            logger.error(f"Cannot read pyproject.toml: {e}")
            return False
        
        project = config.get("project", {})
        
        # Required fields
        required_fields = {
            "name": "Package name",
            "version": "Version number", 
            "description": "Package description",
            "authors": "Author information",
            "license": "License information",
            "readme": "README file reference",
            "dependencies": "Dependencies list",
            "scripts": "CLI entry points"
        }
        
        missing_fields = []
        for field, description in required_fields.items():
            if field not in project or not project[field]:
                missing_fields.append(f"{field} ({description})")
        
        if missing_fields:
            logger.error(f"Missing required metadata: {', '.join(missing_fields)}")
            return False
        
        # Validate README file exists
        readme_config = project.get("readme", {})
        if isinstance(readme_config, dict):
            readme_file = readme_config.get("file")
            if readme_file and not (self.project_root / readme_file).exists():
                logger.error(f"README file not found: {readme_file}")
                return False
        
        logger.info("Package metadata validation passed")
        return True
    
    def build_package(self) -> bool:
        """Build the package"""
        logger.info("Building package...")
        
        try:
            # Install build dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", 
                "build", "wheel", "setuptools"
            ], check=True, capture_output=True)
            
            # Build package
            result = subprocess.run([
                sys.executable, "-m", "build", "--wheel", "--sdist"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Package build failed: {result.stderr}")
                return False
            
            # Check output
            dist_dir = self.project_root / "dist"
            if not dist_dir.exists():
                logger.error("No dist directory created")
                return False
            
            dist_files = list(dist_dir.glob("*"))
            if not dist_files:
                logger.error("No distribution files created")
                return False
            
            # Verify we have both wheel and source dist
            has_wheel = any(f.suffix == ".whl" for f in dist_files)
            has_sdist = any(f.name.endswith(".tar.gz") for f in dist_files)
            
            if not has_wheel:
                logger.error("No wheel file created")
                return False
            
            if not has_sdist:
                logger.error("No source distribution created")
                return False
            
            logger.info(f"Package built successfully: {len(dist_files)} files created")
            for f in dist_files:
                logger.info(f"  - {f.name}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Package build timed out")
            return False
        except Exception as e:
            logger.error(f"Package build failed: {e}")
            return False
    
    def validate_package_contents(self) -> bool:
        """Validate package contents using twine"""
        logger.info("Validating package contents...")
        
        try:
            # Install twine if needed
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "twine"
            ], check=True, capture_output=True)
            
            # Check package
            result = subprocess.run([
                sys.executable, "-m", "twine", "check", "dist/*"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Package validation failed: {result.stderr}")
                return False
            
            logger.info("Package contents validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Package validation failed: {e}")
            return False
    
    def test_installation(self) -> bool:
        """Test package installation in clean environment"""
        logger.info("Testing package installation...")
        
        try:
            # Find wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                logger.error("No wheel file found for installation test")
                return False
            
            wheel_file = wheel_files[0]
            
            # Test in temporary environment
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
                
                # Install package
                subprocess.run([
                    str(pip_exe), "install", str(wheel_file)
                ], check=True, capture_output=True, timeout=300)
                
                # Test import
                result = subprocess.run([
                    str(python_exe), "-c", 
                    "import genebot; import genebot.cli; print('Import successful')"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.error(f"Import test failed: {result.stderr}")
                    return False
                
                # Test CLI
                result = subprocess.run([
                    str(python_exe), "-m", "genebot.cli", "--help"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.error(f"CLI test failed: {result.stderr}")
                    return False
                
                # Check CLI output contains expected commands
                help_output = result.stdout
                expected_commands = ["init-config", "start", "stop"]
                missing_commands = [cmd for cmd in expected_commands if cmd not in help_output]
                
                if missing_commands:
                    logger.error(f"CLI missing expected commands: {missing_commands}")
                    return False
                
                logger.info("Installation test passed")
                return True
                
        except Exception as e:
            logger.error(f"Installation test failed: {e}")
            return False
    
    def test_uninstallation(self) -> bool:
        """Test package uninstallation and cleanup"""
        logger.info("Testing package uninstallation...")
        
        try:
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
                
                # Install package
                dist_dir = self.project_root / "dist"
                wheel_files = list(dist_dir.glob("*.whl"))
                if not wheel_files:
                    logger.error("No wheel file found")
                    return False
                
                subprocess.run([
                    str(pip_exe), "install", str(wheel_files[0])
                ], check=True, capture_output=True, timeout=300)
                
                # Verify installation
                result = subprocess.run([
                    str(pip_exe), "show", "genebot"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error("Package not properly installed")
                    return False
                
                # Uninstall package
                subprocess.run([
                    str(pip_exe), "uninstall", "genebot", "-y"
                ], check=True, capture_output=True, timeout=120)
                
                # Verify uninstallation
                result = subprocess.run([
                    str(pip_exe), "show", "genebot"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.error("Package not properly uninstalled")
                    return False
                
                # Test that import fails
                result = subprocess.run([
                    str(python_exe), "-c", "import genebot"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.error("Package still importable after uninstallation")
                    return False
                
                logger.info("Uninstallation test passed")
                return True
                
        except Exception as e:
            logger.error(f"Uninstallation test failed: {e}")
            return False
    
    def prepare_package_description(self) -> bool:
        """Prepare and validate package description"""
        logger.info("Preparing package description...")
        
        try:
            # Check README file
            readme_path = self.project_root / "README_GENEBOT.md"
            if not readme_path.exists():
                logger.error("README_GENEBOT.md not found")
                return False
            
            # Read and validate README
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Check README has essential sections
            required_sections = [
                "# GeneBot",
                "## Features",
                "## Installation", 
                "## Quick Start",
                "## Configuration"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in readme_content:
                    missing_sections.append(section)
            
            if missing_sections:
                logger.error(f"README missing sections: {missing_sections}")
                return False
            
            # Validate pyproject.toml references README correctly
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
            
            readme_config = config.get("project", {}).get("readme", {})
            if isinstance(readme_config, dict):
                readme_file = readme_config.get("file")
                if readme_file != "README_GENEBOT.md":
                    logger.error(f"pyproject.toml references wrong README: {readme_file}")
                    return False
            
            logger.info("Package description validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Package description preparation failed: {e}")
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive test suite"""
        logger.info("Running comprehensive test suite...")
        
        try:
            # Install test dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade",
                "pytest", "pytest-cov", "pytest-asyncio"
            ], check=True, capture_output=True)
            
            # Run tests
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", 
                "--tb=short", "--maxfail=5"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Test suite failed: {result.stdout}\n{result.stderr}")
                return False
            
            logger.info("Test suite passed")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Test suite timed out")
            return False
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            return False
    
    def generate_preparation_report(self, results: Dict[str, bool]) -> Dict[str, Any]:
        """Generate comprehensive preparation report"""
        
        passed_checks = sum(1 for success in results.values() if success)
        total_checks = len(results)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "overall_success": all(results.values()),
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "success_rate": success_rate
            },
            "detailed_results": results,
            "package_info": {
                "name": "genebot",
                "version": self.version,
                "build_timestamp": datetime.now().isoformat()
            }
        }
        
        return report
    
    def prepare_package(self) -> Dict[str, Any]:
        """Run complete package preparation process"""
        logger.info(f"Starting comprehensive package preparation for version {self.version}...")
        
        # Define preparation steps
        steps = [
            ("Clean Build Artifacts", self.clean_build_artifacts),
            ("Update Version References", self.update_version_references),
            ("Validate Package Metadata", self.validate_package_metadata),
            ("Prepare Package Description", self.prepare_package_description),
            ("Run Comprehensive Tests", self.run_comprehensive_tests),
            ("Build Package", self.build_package),
            ("Validate Package Contents", self.validate_package_contents),
            ("Test Installation", self.test_installation),
            ("Test Uninstallation", self.test_uninstallation)
        ]
        
        results = {}
        
        # Execute each step
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            try:
                success = step_func()
                results[step_name] = success
                
                if success:
                    logger.info(f"✅ {step_name} - PASSED")
                else:
                    logger.error(f"❌ {step_name} - FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {step_name} - FAILED with exception: {e}")
                results[step_name] = False
        
        # Generate report
        report = self.generate_preparation_report(results)
        
        # Log summary
        if report["overall_success"]:
            logger.info("🎉 Package preparation completed successfully!")
            logger.info("Package is ready for publication")
        else:
            logger.error("❌ Package preparation failed")
            failed_steps = [step for step, success in results.items() if not success]
            logger.error(f"Failed steps: {', '.join(failed_steps)}")
        
        return report


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GeneBot Package Preparation")
    parser.add_argument("--output", "-o", help="Output file for preparation report")
    parser.add_argument("--json", action="store_true", help="Output report in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run preparation
    preparator = PackagePreparator()
    report = preparator.prepare_package()
    
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
        print(f"GeneBot Package Preparation Report")
        print(f"Version: {report['version']}")
        print(f"Timestamp: {report['timestamp']}")
        print("="*60)
        
        print(f"\nSummary:")
        summary = report['summary']
        print(f"  Total checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed_checks']}")
        print(f"  Failed: {summary['failed_checks']}")
        print(f"  Success rate: {summary['success_rate']:.1f}%")
        
        print(f"\nOverall result: {'✅ READY FOR PUBLICATION' if report['overall_success'] else '❌ NOT READY'}")
        
        print(f"\nDetailed results:")
        for step, success in report['detailed_results'].items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {step}")
        
        if args.output:
            # Save text report
            with open(args.output, 'w') as f:
                f.write(f"GeneBot Package Preparation Report\n")
                f.write(f"Version: {report['version']}\n")
                f.write(f"Timestamp: {report['timestamp']}\n")
                f.write(f"Overall Success: {report['overall_success']}\n\n")
                
                f.write(f"Summary:\n")
                f.write(f"  Total: {summary['total_checks']}\n")
                f.write(f"  Passed: {summary['passed_checks']}\n")
                f.write(f"  Failed: {summary['failed_checks']}\n")
                f.write(f"  Success Rate: {summary['success_rate']:.1f}%\n\n")
                
                f.write(f"Detailed Results:\n")
                for step, success in report['detailed_results'].items():
                    status = "PASS" if success else "FAIL"
                    f.write(f"  [{status}] {step}\n")
            
            print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_success'] else 1)


if __name__ == "__main__":
    main()
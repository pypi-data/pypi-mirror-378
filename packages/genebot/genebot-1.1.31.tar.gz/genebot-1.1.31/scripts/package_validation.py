#!/usr/bin/env python3
"""
GeneBot Package Validation Script
=================================

Comprehensive validation script for final package preparation.
This script validates all aspects of the package before publication.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
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
class ValidationResult:
    """Result of a validation check"""
    name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


@dataclass
class PackageValidationReport:
    """Complete package validation report"""
    timestamp: str
    version: str
    overall_success: bool
    results: List[ValidationResult]
    summary: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PackageValidator:
    """Comprehensive package validator"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results: List[ValidationResult] = []
        
    def add_result(self, name: str, success: bool, message: str, 
                   details: Dict[str, Any] = None, suggestions: List[str] = None):
        """Add a validation result"""
        result = ValidationResult(
            name=name,
            success=success,
            message=message,
            details=details or {},
            suggestions=suggestions or []
        )
        self.results.append(result)
        
        # Log result
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"{name}: {message}")
        
    def validate_project_structure(self) -> bool:
        """Validate project structure"""
        logger.info("Validating project structure...")
        
        required_files = [
            "pyproject.toml",
            "README_GENEBOT.md",
            "genebot/__init__.py",
            "genebot/cli/__init__.py",
            "genebot/cli/main.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.add_result(
                "Project Structure",
                False,
                f"Missing required files: {', '.join(missing_files)}",
                {"missing_files": missing_files},
                ["Ensure all required files are present before packaging"]
            )
            return False
        
        self.add_result(
            "Project Structure",
            True,
            "All required files are present"
        )
        return True
    
    def validate_pyproject_toml(self) -> bool:
        """Validate pyproject.toml configuration"""
        logger.info("Validating pyproject.toml...")
        
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            self.add_result(
                "pyproject.toml",
                False,
                f"Failed to parse pyproject.toml: {e}",
                suggestions=["Fix syntax errors in pyproject.toml"]
            )
            return False
        
        # Check required sections
        required_sections = ["build-system", "project"]
        missing_sections = [s for s in required_sections if s not in config]
        
        if missing_sections:
            self.add_result(
                "pyproject.toml",
                False,
                f"Missing required sections: {', '.join(missing_sections)}",
                {"missing_sections": missing_sections}
            )
            return False
        
        # Check project metadata
        project = config.get("project", {})
        required_fields = ["name", "version", "description", "authors"]
        missing_fields = [f for f in required_fields if f not in project]
        
        if missing_fields:
            self.add_result(
                "pyproject.toml",
                False,
                f"Missing required project fields: {', '.join(missing_fields)}",
                {"missing_fields": missing_fields}
            )
            return False
        
        # Validate version format
        version = project.get("version", "")
        if not version or not self._is_valid_version(version):
            self.add_result(
                "pyproject.toml",
                False,
                f"Invalid version format: {version}",
                suggestions=["Use semantic versioning (e.g., 1.2.3)"]
            )
            return False
        
        self.add_result(
            "pyproject.toml",
            True,
            f"Configuration is valid (version: {version})",
            {"version": version}
        )
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate package dependencies"""
        logger.info("Validating dependencies...")
        
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            self.add_result(
                "Dependencies",
                False,
                f"Cannot read pyproject.toml: {e}"
            )
            return False
        
        dependencies = config.get("project", {}).get("dependencies", [])
        
        # Check for critical dependencies
        critical_deps = ["ccxt", "pandas", "numpy", "pydantic", "click"]
        missing_critical = []
        
        for dep in critical_deps:
            if not any(dep in d for d in dependencies):
                missing_critical.append(dep)
        
        if missing_critical:
            self.add_result(
                "Dependencies",
                False,
                f"Missing critical dependencies: {', '.join(missing_critical)}",
                {"missing_critical": missing_critical}
            )
            return False
        
        self.add_result(
            "Dependencies",
            True,
            f"All critical dependencies present ({len(dependencies)} total)",
            {"total_dependencies": len(dependencies)}
        )
        return True
    
    def validate_entry_points(self) -> bool:
        """Validate CLI entry points"""
        logger.info("Validating entry points...")
        
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            self.add_result(
                "Entry Points",
                False,
                f"Cannot read pyproject.toml: {e}"
            )
            return False
        
        scripts = config.get("project", {}).get("scripts", {})
        
        if "genebot" not in scripts:
            self.add_result(
                "Entry Points",
                False,
                "Missing 'genebot' CLI entry point",
                suggestions=["Add 'genebot = \"genebot.cli:main\"' to [project.scripts]"]
            )
            return False
        
        # Validate entry point path
        entry_point = scripts["genebot"]
        if "genebot.cli" not in entry_point:
            self.add_result(
                "Entry Points",
                False,
                f"Invalid entry point path: {entry_point}",
                suggestions=["Entry point should reference genebot.cli module"]
            )
            return False
        
        self.add_result(
            "Entry Points",
            True,
            f"CLI entry point configured: {entry_point}"
        )
        return True
    
    def validate_imports(self) -> bool:
        """Validate that all imports work correctly"""
        logger.info("Validating imports...")
        
        # Test critical imports
        critical_modules = [
            "genebot",
            "genebot.cli",
            "genebot.cli.main",
            "genebot.config",
            "genebot.strategies",
            "genebot.models"
        ]
        
        failed_imports = []
        
        for module in critical_modules:
            try:
                spec = importlib.util.find_spec(module)
                if spec is None:
                    failed_imports.append(f"{module} (not found)")
                else:
                    # Try to actually import
                    importlib.import_module(module)
            except Exception as e:
                failed_imports.append(f"{module} ({str(e)})")
        
        if failed_imports:
            self.add_result(
                "Imports",
                False,
                f"Failed imports: {', '.join(failed_imports)}",
                {"failed_imports": failed_imports},
                ["Fix import errors before packaging"]
            )
            return False
        
        self.add_result(
            "Imports",
            True,
            f"All critical modules importable ({len(critical_modules)} tested)"
        )
        return True
    
    def validate_cli_functionality(self) -> bool:
        """Validate CLI functionality"""
        logger.info("Validating CLI functionality...")
        
        try:
            # Test CLI help command
            result = subprocess.run(
                [sys.executable, "-m", "genebot.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                self.add_result(
                    "CLI Functionality",
                    False,
                    f"CLI help command failed: {result.stderr}",
                    {"returncode": result.returncode, "stderr": result.stderr}
                )
                return False
            
            # Check if help output contains expected content
            help_output = result.stdout
            expected_commands = ["init-config", "start", "stop", "status"]
            missing_commands = [cmd for cmd in expected_commands if cmd not in help_output]
            
            if missing_commands:
                self.add_result(
                    "CLI Functionality",
                    False,
                    f"Missing CLI commands in help: {', '.join(missing_commands)}",
                    {"missing_commands": missing_commands}
                )
                return False
            
            self.add_result(
                "CLI Functionality",
                True,
                "CLI help command works and shows expected commands"
            )
            return True
            
        except subprocess.TimeoutExpired:
            self.add_result(
                "CLI Functionality",
                False,
                "CLI help command timed out",
                suggestions=["Check for infinite loops or blocking operations in CLI"]
            )
            return False
        except Exception as e:
            self.add_result(
                "CLI Functionality",
                False,
                f"CLI test failed: {e}"
            )
            return False
    
    def validate_package_build(self) -> bool:
        """Validate package can be built"""
        logger.info("Validating package build...")
        
        # Create temporary directory for build test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Copy project to temp directory
                project_copy = temp_path / "genebot_build_test"
                shutil.copytree(self.project_root, project_copy, 
                              ignore=shutil.ignore_patterns('dist', 'build', '*.egg-info', '__pycache__'))
                
                # Try to build package
                result = subprocess.run(
                    [sys.executable, "-m", "build", "--wheel", "--sdist"],
                    capture_output=True,
                    text=True,
                    cwd=project_copy,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.add_result(
                        "Package Build",
                        False,
                        f"Package build failed: {result.stderr}",
                        {"returncode": result.returncode, "stderr": result.stderr}
                    )
                    return False
                
                # Check if dist files were created
                dist_dir = project_copy / "dist"
                if not dist_dir.exists():
                    self.add_result(
                        "Package Build",
                        False,
                        "No dist directory created during build"
                    )
                    return False
                
                dist_files = list(dist_dir.glob("*"))
                if not dist_files:
                    self.add_result(
                        "Package Build",
                        False,
                        "No distribution files created"
                    )
                    return False
                
                # Check for both wheel and source distribution
                has_wheel = any(f.suffix == ".whl" for f in dist_files)
                has_sdist = any(f.suffix == ".gz" for f in dist_files)
                
                if not has_wheel or not has_sdist:
                    self.add_result(
                        "Package Build",
                        False,
                        f"Missing distribution types (wheel: {has_wheel}, sdist: {has_sdist})",
                        {"has_wheel": has_wheel, "has_sdist": has_sdist}
                    )
                    return False
                
                self.add_result(
                    "Package Build",
                    True,
                    f"Package built successfully ({len(dist_files)} files created)",
                    {"dist_files": [f.name for f in dist_files]}
                )
                return True
                
            except subprocess.TimeoutExpired:
                self.add_result(
                    "Package Build",
                    False,
                    "Package build timed out"
                )
                return False
            except Exception as e:
                self.add_result(
                    "Package Build",
                    False,
                    f"Package build test failed: {e}"
                )
                return False
    
    def validate_installation_test(self) -> bool:
        """Test package installation in clean environment"""
        logger.info("Testing package installation...")
        
        # First build the package
        try:
            # Clean previous builds
            for pattern in ["dist", "build", "*.egg-info"]:
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            
            # Build package
            result = subprocess.run(
                [sys.executable, "-m", "build", "--wheel"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if result.returncode != 0:
                self.add_result(
                    "Installation Test",
                    False,
                    f"Failed to build package for installation test: {result.stderr}"
                )
                return False
            
            # Find the wheel file
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            
            if not wheel_files:
                self.add_result(
                    "Installation Test",
                    False,
                    "No wheel file found for installation test"
                )
                return False
            
            wheel_file = wheel_files[0]
            
            # Test installation in temporary environment
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create virtual environment
                venv_path = temp_path / "test_venv"
                result = subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_path)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    self.add_result(
                        "Installation Test",
                        False,
                        f"Failed to create test virtual environment: {result.stderr}"
                    )
                    return False
                
                # Get python executable in venv
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                    pip_exe = venv_path / "Scripts" / "pip.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                    pip_exe = venv_path / "bin" / "pip"
                
                # Install the package
                result = subprocess.run(
                    [str(pip_exe), "install", str(wheel_file)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    self.add_result(
                        "Installation Test",
                        False,
                        f"Package installation failed: {result.stderr}",
                        {"stderr": result.stderr}
                    )
                    return False
                
                # Test that CLI is accessible
                result = subprocess.run(
                    [str(python_exe), "-c", "import genebot.cli; print('Import successful')"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.add_result(
                        "Installation Test",
                        False,
                        f"Package import failed after installation: {result.stderr}"
                    )
                    return False
                
                # Test CLI command
                result = subprocess.run(
                    [str(python_exe), "-m", "genebot.cli", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.add_result(
                        "Installation Test",
                        False,
                        f"CLI command failed after installation: {result.stderr}"
                    )
                    return False
                
                self.add_result(
                    "Installation Test",
                    True,
                    "Package installs and CLI works correctly",
                    {"wheel_file": wheel_file.name}
                )
                return True
                
        except Exception as e:
            self.add_result(
                "Installation Test",
                False,
                f"Installation test failed: {e}"
            )
            return False
    
    def validate_metadata(self) -> bool:
        """Validate package metadata"""
        logger.info("Validating package metadata...")
        
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            self.add_result(
                "Metadata",
                False,
                f"Cannot read pyproject.toml: {e}"
            )
            return False
        
        project = config.get("project", {})
        
        # Check metadata completeness
        metadata_fields = {
            "name": project.get("name"),
            "version": project.get("version"),
            "description": project.get("description"),
            "authors": project.get("authors"),
            "license": project.get("license"),
            "readme": project.get("readme"),
            "keywords": project.get("keywords"),
            "classifiers": project.get("classifiers")
        }
        
        missing_metadata = [k for k, v in metadata_fields.items() if not v]
        
        if missing_metadata:
            self.add_result(
                "Metadata",
                False,
                f"Missing metadata fields: {', '.join(missing_metadata)}",
                {"missing_metadata": missing_metadata}
            )
            return False
        
        # Validate README file exists
        readme_config = project.get("readme", {})
        if isinstance(readme_config, dict):
            readme_file = readme_config.get("file")
            if readme_file and not (self.project_root / readme_file).exists():
                self.add_result(
                    "Metadata",
                    False,
                    f"README file not found: {readme_file}"
                )
                return False
        
        self.add_result(
            "Metadata",
            True,
            "All required metadata fields are present and valid"
        )
        return True
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        import re
        pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?(?:\+[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$'
        return bool(re.match(pattern, version))
    
    def run_all_validations(self) -> PackageValidationReport:
        """Run all validation checks"""
        logger.info("Starting comprehensive package validation...")
        
        # Clear previous results
        self.results = []
        
        # Run all validations
        validations = [
            self.validate_project_structure,
            self.validate_pyproject_toml,
            self.validate_dependencies,
            self.validate_entry_points,
            self.validate_metadata,
            self.validate_imports,
            self.validate_cli_functionality,
            self.validate_package_build,
            self.validate_installation_test
        ]
        
        success_count = 0
        for validation in validations:
            try:
                if validation():
                    success_count += 1
            except Exception as e:
                logger.error(f"Validation {validation.__name__} failed with exception: {e}")
                self.add_result(
                    validation.__name__,
                    False,
                    f"Validation failed with exception: {e}"
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
        
        # Get version
        version = "unknown"
        try:
            import tomllib
            with open(self.project_root / "pyproject.toml", "rb") as f:
                config = tomllib.load(f)
                version = config.get("project", {}).get("version", "unknown")
        except Exception:
            pass
        
        report = PackageValidationReport(
            timestamp=datetime.now().isoformat(),
            version=version,
            overall_success=overall_success,
            results=self.results,
            summary=summary
        )
        
        logger.info(f"Validation complete: {success_count}/{total_count} checks passed")
        return report


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GeneBot Package Validation")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output report in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run validation
    validator = PackageValidator()
    report = validator.run_all_validations()
    
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
        print(f"GeneBot Package Validation Report")
        print(f"Version: {report.version}")
        print(f"Timestamp: {report.timestamp}")
        print("="*60)
        
        print(f"\nSummary:")
        print(f"  Total checks: {report.summary['total']}")
        print(f"  Passed: {report.summary['passed']}")
        print(f"  Failed: {report.summary['failed']}")
        print(f"  Success rate: {report.summary['success_rate']:.1f}%")
        
        print(f"\nOverall result: {'✅ PASS' if report.overall_success else '❌ FAIL'}")
        
        if not report.overall_success:
            print(f"\nFailed checks:")
            for result in report.results:
                if not result.success:
                    print(f"  ❌ {result.name}: {result.message}")
                    if result.suggestions:
                        for suggestion in result.suggestions:
                            print(f"     💡 {suggestion}")
        
        print(f"\nDetailed results:")
        for result in report.results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.name}: {result.message}")
        
        if args.output:
            # Save text report
            with open(args.output, 'w') as f:
                f.write(f"GeneBot Package Validation Report\n")
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
                    f.write(f"  [{status}] {result.name}: {result.message}\n")
                    if result.suggestions:
                        for suggestion in result.suggestions:
                            f.write(f"    Suggestion: {suggestion}\n")
            
            print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report.overall_success else 1)


if __name__ == "__main__":
    main()
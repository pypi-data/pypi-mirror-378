"""
Logging configuration validation tools.

This module provides comprehensive validation for logging configurations,
including schema validation, performance testing, and compatibility checks.
"""

import os
import json
import yaml
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from .config import LoggingConfig
from .factory import setup_global_config, get_logger


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    config_path: Optional[Path]
    config: LoggingConfig
    results: List[ValidationResult]
    overall_status: str  # passed, failed, warnings
    validation_time: datetime
    
    @property
    def errors(self) -> List[ValidationResult]:
        """Get all error results."""
        return [r for r in self.results if r.severity == "error" and not r.passed]
    
    @property
    def warnings(self) -> List[ValidationResult]:
        """Get all warning results."""
        return [r for r in self.results if r.severity == "warning" and not r.passed]
    
    @property
    def passed_checks(self) -> List[ValidationResult]:
        """Get all passed checks."""
        return [r for r in self.results if r.passed]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'config_path': str(self.config_path) if self.config_path else None,
            'config': self.config.to_dict(),
            'overall_status': self.overall_status,
            'validation_time': self.validation_time.isoformat(),
            'summary': {
                'total_checks': len(self.results),
                'passed': len(self.passed_checks),
                'errors': len(self.errors),
                'warnings': len(self.warnings)
            },
            'results': [
                {
                    'check_name': r.check_name,
                    'passed': r.passed,
                    'message': r.message,
                    'severity': r.severity,
                    'details': r.details
                }
                for r in self.results
            ]
        }
    
    def save_to_file(self, output_path: Path) -> None:
        """Save validation report to file."""
        report_data = self.to_dict()
        
        with open(output_path, 'w') as f:
            if output_path.suffix.lower() == '.json':
                json.dump(report_data, f, indent=2, default=str)
            else:
                yaml.dump(report_data, f, default_flow_style=False, indent=2)


class ConfigurationValidator:
    """Comprehensive logging configuration validator."""
    
    def __init__(self):
        """Initialize validator."""
        self.checks = [
            self._validate_basic_config,
            self._validate_file_permissions,
            self._validate_directory_structure,
            self._validate_log_levels,
            self._validate_file_sizes,
            self._validate_rotation_settings,
            self._validate_performance_settings,
            self._validate_security_settings,
            self._validate_environment_compatibility,
            self._validate_external_dependencies
        ]
    
    def validate(self, config: LoggingConfig, config_path: Optional[Path] = None) -> ValidationReport:
        """
        Perform comprehensive validation of logging configuration.
        
        Args:
            config: LoggingConfig to validate
            config_path: Optional path to config file
            
        Returns:
            ValidationReport with all validation results
        """
        results = []
        
        # Run all validation checks
        for check in self.checks:
            try:
                result = check(config)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    check_name=check.__name__,
                    passed=False,
                    message=f"Validation check failed: {e}",
                    severity="error"
                ))
        
        # Determine overall status
        errors = [r for r in results if r.severity == "error" and not r.passed]
        warnings = [r for r in results if r.severity == "warning" and not r.passed]
        
        if errors:
            overall_status = "failed"
        elif warnings:
            overall_status = "warnings"
        else:
            overall_status = "passed"
        
        return ValidationReport(
            config_path=config_path,
            config=config,
            results=results,
            overall_status=overall_status,
            validation_time=datetime.now()
        )
    
    def _validate_basic_config(self, config: LoggingConfig) -> ValidationResult:
        """Validate basic configuration structure."""
        try:
            # Test that config can be created and accessed
            _ = config.level
            _ = config.format_type
            _ = config.log_directory
            
            return ValidationResult(
                check_name="basic_config",
                passed=True,
                message="Basic configuration structure is valid",
                severity="error"
            )
        except Exception as e:
            return ValidationResult(
                check_name="basic_config",
                passed=False,
                message=f"Basic configuration validation failed: {e}",
                severity="error"
            )
    
    def _validate_file_permissions(self, config: LoggingConfig) -> ValidationResult:
        """Validate file and directory permissions."""
        if not config.file_output:
            return ValidationResult(
                check_name="file_permissions",
                passed=True,
                message="File output disabled, skipping permission check",
                severity="info"
            )
        
        try:
            # Test directory creation and file writing
            test_dir = config.log_directory / "test_permissions"
            test_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = test_dir / "test.log"
            test_file.write_text("test")
            
            # Check if file is readable
            content = test_file.read_text()
            
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
            
            return ValidationResult(
                check_name="file_permissions",
                passed=True,
                message="File permissions are correct",
                severity="error"
            )
            
        except PermissionError as e:
            return ValidationResult(
                check_name="file_permissions",
                passed=False,
                message=f"Permission denied: {e}",
                severity="error"
            )
        except Exception as e:
            return ValidationResult(
                check_name="file_permissions",
                passed=False,
                message=f"File permission check failed: {e}",
                severity="error"
            )
    
    def _validate_directory_structure(self, config: LoggingConfig) -> ValidationResult:
        """Validate log directory structure."""
        if not config.file_output:
            return ValidationResult(
                check_name="directory_structure",
                passed=True,
                message="File output disabled, skipping directory check",
                severity="info"
            )
        
        try:
            # Check if log directory can be created
            config.log_directory.mkdir(parents=True, exist_ok=True)
            
            # Check if directory is writable
            if not os.access(config.log_directory, os.W_OK):
                return ValidationResult(
                    check_name="directory_structure",
                    passed=False,
                    message=f"Log directory is not writable: {config.log_directory}",
                    severity="error"
                )
            
            # Check available disk space
            stat = os.statvfs(config.log_directory)
            free_space_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
            
            if free_space_mb < config.min_free_space_mb:
                return ValidationResult(
                    check_name="directory_structure",
                    passed=False,
                    message=f"Insufficient disk space: {free_space_mb:.1f}MB available, {config.min_free_space_mb}MB required",
                    severity="warning"
                )
            
            return ValidationResult(
                check_name="directory_structure",
                passed=True,
                message=f"Directory structure is valid, {free_space_mb:.1f}MB available",
                severity="info",
                details={"free_space_mb": free_space_mb}
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="directory_structure",
                passed=False,
                message=f"Directory structure validation failed: {e}",
                severity="error"
            )
    
    def _validate_log_levels(self, config: LoggingConfig) -> ValidationResult:
        """Validate log level configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if config.level not in valid_levels:
            return ValidationResult(
                check_name="log_levels",
                passed=False,
                message=f"Invalid log level: {config.level}. Must be one of: {', '.join(valid_levels)}",
                severity="error"
            )
        
        if config.external_lib_level not in valid_levels:
            return ValidationResult(
                check_name="log_levels",
                passed=False,
                message=f"Invalid external library log level: {config.external_lib_level}",
                severity="error"
            )
        
        # Check for potentially problematic level combinations
        level_values = {
            "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50
        }
        
        main_level_value = level_values[config.level]
        ext_level_value = level_values[config.external_lib_level]
        
        if ext_level_value < main_level_value:
            return ValidationResult(
                check_name="log_levels",
                passed=True,
                message="External library log level is lower than main level, may produce noise",
                severity="warning",
                details={
                    "main_level": config.level,
                    "external_level": config.external_lib_level
                }
            )
        
        return ValidationResult(
            check_name="log_levels",
            passed=True,
            message="Log levels are valid",
            severity="info"
        )
    
    def _validate_file_sizes(self, config: LoggingConfig) -> ValidationResult:
        """Validate file size configuration."""
        if not config.file_output:
            return ValidationResult(
                check_name="file_sizes",
                passed=True,
                message="File output disabled, skipping size check",
                severity="info"
            )
        
        # Check maximum file size
        min_size = 1024 * 1024  # 1MB
        max_size = 1024 * 1024 * 1024  # 1GB
        
        if config.max_file_size < min_size:
            return ValidationResult(
                check_name="file_sizes",
                passed=False,
                message=f"Max file size too small: {config.max_file_size} bytes (minimum: {min_size} bytes)",
                severity="warning"
            )
        
        if config.max_file_size > max_size:
            return ValidationResult(
                check_name="file_sizes",
                passed=False,
                message=f"Max file size very large: {config.max_file_size} bytes (may impact performance)",
                severity="warning"
            )
        
        return ValidationResult(
            check_name="file_sizes",
            passed=True,
            message=f"File size configuration is reasonable: {config.max_file_size / (1024*1024):.1f}MB",
            severity="info"
        )
    
    def _validate_rotation_settings(self, config: LoggingConfig) -> ValidationResult:
        """Validate log rotation settings."""
        if not config.file_output:
            return ValidationResult(
                check_name="rotation_settings",
                passed=True,
                message="File output disabled, skipping rotation check",
                severity="info"
            )
        
        # Check backup count
        if config.backup_count < 1:
            return ValidationResult(
                check_name="rotation_settings",
                passed=False,
                message="Backup count should be at least 1 to prevent log loss",
                severity="warning"
            )
        
        if config.backup_count > 100:
            return ValidationResult(
                check_name="rotation_settings",
                passed=False,
                message=f"Backup count very high: {config.backup_count} (may consume excessive disk space)",
                severity="warning"
            )
        
        # Estimate total disk usage
        total_size_mb = (config.max_file_size * (config.backup_count + 1)) / (1024 * 1024)
        
        return ValidationResult(
            check_name="rotation_settings",
            passed=True,
            message=f"Rotation settings valid, estimated max disk usage: {total_size_mb:.1f}MB per log type",
            severity="info",
            details={"estimated_max_disk_usage_mb": total_size_mb}
        )
    
    def _validate_performance_settings(self, config: LoggingConfig) -> ValidationResult:
        """Validate performance-related settings."""
        issues = []
        
        # Check async logging settings
        if config.enable_async_logging:
            if config.log_buffer_size < 100:
                issues.append("Async buffer size very small, may impact performance")
            
            if config.async_queue_size < config.log_buffer_size * 10:
                issues.append("Async queue size may be too small for buffer size")
            
            if config.async_flush_interval > 10.0:
                issues.append("Async flush interval very long, may delay log writes")
        
        # Check buffer sizes
        if config.log_buffer_size > 10000:
            issues.append("Log buffer size very large, may consume excessive memory")
        
        if issues:
            return ValidationResult(
                check_name="performance_settings",
                passed=False,
                message=f"Performance configuration issues: {'; '.join(issues)}",
                severity="warning",
                details={"issues": issues}
            )
        
        return ValidationResult(
            check_name="performance_settings",
            passed=True,
            message="Performance settings are optimal",
            severity="info"
        )
    
    def _validate_security_settings(self, config: LoggingConfig) -> ValidationResult:
        """Validate security-related settings."""
        recommendations = []
        
        if not config.mask_sensitive_data:
            recommendations.append("Consider enabling sensitive data masking for production")
        
        if config.file_output:
            # Check log directory permissions
            try:
                stat_info = config.log_directory.stat()
                # Check if directory is world-readable (may be security issue)
                if stat_info.st_mode & 0o004:
                    recommendations.append("Log directory is world-readable, consider restricting permissions")
            except Exception:
                pass  # Directory might not exist yet
        
        if recommendations:
            return ValidationResult(
                check_name="security_settings",
                passed=True,
                message=f"Security recommendations: {'; '.join(recommendations)}",
                severity="warning",
                details={"recommendations": recommendations}
            )
        
        return ValidationResult(
            check_name="security_settings",
            passed=True,
            message="Security settings are appropriate",
            severity="info"
        )
    
    def _validate_environment_compatibility(self, config: LoggingConfig) -> ValidationResult:
        """Validate environment-specific compatibility."""
        current_env = os.getenv('ENVIRONMENT', 'development')
        
        # Check if configuration matches environment expectations
        if current_env == 'production':
            if config.level == 'DEBUG':
                return ValidationResult(
                    check_name="environment_compatibility",
                    passed=False,
                    message="DEBUG level logging in production may impact performance",
                    severity="warning"
                )
            
            if config.console_output and not config.file_output:
                return ValidationResult(
                    check_name="environment_compatibility",
                    passed=False,
                    message="Console-only logging in production is not recommended",
                    severity="warning"
                )
        
        elif current_env == 'testing':
            if config.file_output:
                return ValidationResult(
                    check_name="environment_compatibility",
                    passed=True,
                    message="File output in testing environment may interfere with test isolation",
                    severity="warning"
                )
        
        return ValidationResult(
            check_name="environment_compatibility",
            passed=True,
            message=f"Configuration compatible with {current_env} environment",
            severity="info"
        )
    
    def _validate_external_dependencies(self, config: LoggingConfig) -> ValidationResult:
        """Validate external dependencies and imports."""
        missing_deps = []
        
        try:
            import yaml
        except ImportError:
            missing_deps.append("PyYAML (required for YAML config files)")
        
        if config.enable_async_logging:
            try:
                import asyncio
            except ImportError:
                missing_deps.append("asyncio (required for async logging)")
        
        if missing_deps:
            return ValidationResult(
                check_name="external_dependencies",
                passed=False,
                message=f"Missing dependencies: {', '.join(missing_deps)}",
                severity="error",
                details={"missing_dependencies": missing_deps}
            )
        
        return ValidationResult(
            check_name="external_dependencies",
            passed=True,
            message="All required dependencies are available",
            severity="info"
        )


class FunctionalityTester:
    """Tests actual logging functionality with configuration."""
    
    def __init__(self, config: LoggingConfig):
        """
        Initialize functionality tester.
        
        Args:
            config: LoggingConfig to test
        """
        self.config = config
        self.test_results = []
    
    def run_all_tests(self) -> List[ValidationResult]:
        """
        Run all functionality tests.
        
        Returns:
            List of ValidationResult for each test
        """
        tests = [
            self._test_basic_logging,
            self._test_specialized_loggers,
            self._test_context_logging,
            self._test_error_logging,
            self._test_file_output,
            self._test_log_rotation,
            self._test_performance_logging
        ]
        
        results = []
        
        # Setup logging with test config
        try:
            setup_global_config(self.config)
        except Exception as e:
            results.append(ValidationResult(
                check_name="setup_logging",
                passed=False,
                message=f"Failed to setup logging: {e}",
                severity="error"
            ))
            return results
        
        # Run tests
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    check_name=test.__name__,
                    passed=False,
                    message=f"Test failed with exception: {e}",
                    severity="error"
                ))
        
        return results
    
    def _test_basic_logging(self) -> ValidationResult:
        """Test basic logging functionality."""
        try:
            logger = get_logger("test.basic")
            
            # Test all log levels
            logger.debug("Test debug message")
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            logger.critical("Test critical message")
            
            return ValidationResult(
                check_name="basic_logging",
                passed=True,
                message="Basic logging functionality works",
                severity="info"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="basic_logging",
                passed=False,
                message=f"Basic logging test failed: {e}",
                severity="error"
            )
    
    def _test_specialized_loggers(self) -> ValidationResult:
        """Test specialized logger functionality."""
        try:
            from .factory import get_trade_logger, get_performance_logger, get_error_logger
            
            # Test trade logger
            trade_logger = get_trade_logger()
            trade_logger.info("Test trade message")
            
            # Test performance logger
            perf_logger = get_performance_logger()
            perf_logger.info("Test performance message")
            
            # Test error logger
            error_logger = get_error_logger()
            error_logger.error("Test error message")
            
            return ValidationResult(
                check_name="specialized_loggers",
                passed=True,
                message="Specialized loggers work correctly",
                severity="info"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="specialized_loggers",
                passed=False,
                message=f"Specialized logger test failed: {e}",
                severity="error"
            )
    
    def _test_context_logging(self) -> ValidationResult:
        """Test context-aware logging."""
        try:
            from .context import LogContext
            
            context = LogContext(
                component="test",
                operation="validation",
                symbol="BTCUSDT"
            )
            
            logger = get_logger("test.context", context)
            logger.info("Test context message")
            
            return ValidationResult(
                check_name="context_logging",
                passed=True,
                message="Context logging works correctly",
                severity="info"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="context_logging",
                passed=False,
                message=f"Context logging test failed: {e}",
                severity="error"
            )
    
    def _test_error_logging(self) -> ValidationResult:
        """Test error and exception logging."""
        try:
            logger = get_logger("test.error")
            
            # Test exception logging
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Test exception logging")
            
            return ValidationResult(
                check_name="error_logging",
                passed=True,
                message="Error logging works correctly",
                severity="info"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="error_logging",
                passed=False,
                message=f"Error logging test failed: {e}",
                severity="error"
            )
    
    def _test_file_output(self) -> ValidationResult:
        """Test file output functionality."""
        if not self.config.file_output:
            return ValidationResult(
                check_name="file_output",
                passed=True,
                message="File output disabled, skipping test",
                severity="info"
            )
        
        try:
            logger = get_logger("test.file")
            logger.info("Test file output message")
            
            # Check if log file was created
            log_files = list(self.config.log_directory.glob("*.log"))
            
            if not log_files:
                return ValidationResult(
                    check_name="file_output",
                    passed=False,
                    message="No log files created",
                    severity="error"
                )
            
            return ValidationResult(
                check_name="file_output",
                passed=True,
                message=f"File output works, created {len(log_files)} log files",
                severity="info",
                details={"log_files": [str(f) for f in log_files]}
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="file_output",
                passed=False,
                message=f"File output test failed: {e}",
                severity="error"
            )
    
    def _test_log_rotation(self) -> ValidationResult:
        """Test log rotation functionality."""
        if not self.config.file_output:
            return ValidationResult(
                check_name="log_rotation",
                passed=True,
                message="File output disabled, skipping rotation test",
                severity="info"
            )
        
        # This is a basic test - full rotation testing would require generating large amounts of log data
        return ValidationResult(
            check_name="log_rotation",
            passed=True,
            message="Log rotation configuration appears valid (full test requires large log generation)",
            severity="info"
        )
    
    def _test_performance_logging(self) -> ValidationResult:
        """Test performance logging functionality."""
        if not self.config.enable_performance_logging:
            return ValidationResult(
                check_name="performance_logging",
                passed=True,
                message="Performance logging disabled, skipping test",
                severity="info"
            )
        
        try:
            from .performance_logger import PerformanceLogger
            
            perf_logger = PerformanceLogger()
            
            # Test performance measurement
            with perf_logger.measure_time("test_operation"):
                import time
                time.sleep(0.01)  # Small delay for measurement
            
            return ValidationResult(
                check_name="performance_logging",
                passed=True,
                message="Performance logging works correctly",
                severity="info"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="performance_logging",
                passed=False,
                message=f"Performance logging test failed: {e}",
                severity="error"
            )


def validate_configuration_file(config_path: Path, run_functionality_tests: bool = False) -> ValidationReport:
    """
    Validate a logging configuration file.
    
    Args:
        config_path: Path to configuration file
        run_functionality_tests: Whether to run functionality tests
        
    Returns:
        ValidationReport with validation results
    """
    try:
        config = LoggingConfig.from_file(config_path)
    except Exception as e:
        # Create minimal report for file loading failure
        return ValidationReport(
            config_path=config_path,
            config=LoggingConfig(),  # Default config for report structure
            results=[ValidationResult(
                check_name="load_config",
                passed=False,
                message=f"Failed to load configuration file: {e}",
                severity="error"
            )],
            overall_status="failed",
            validation_time=datetime.now()
        )
    
    # Run configuration validation
    validator = ConfigurationValidator()
    report = validator.validate(config, config_path)
    
    # Run functionality tests if requested
    if run_functionality_tests:
        tester = FunctionalityTester(config)
        functionality_results = tester.run_all_tests()
        report.results.extend(functionality_results)
        
        # Update overall status if functionality tests failed
        func_errors = [r for r in functionality_results if r.severity == "error" and not r.passed]
        if func_errors and report.overall_status != "failed":
            report.overall_status = "failed"
    
    return report
"""
Utility Commands
===============

Utility commands for system maintenance and health checks.
"""

from argparse import Namespace
from pathlib import Path
from typing import List, Dict, Any
import shutil
import os
from datetime import datetime

from ..result import CommandResult
from .base import BaseCommand


class HealthCheckCommand(BaseCommand):
    """System health check"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute health check command"""
        fix_issues = getattr(args, 'fix', False)
        
        self.logger.section("System Health Check")
        
        if fix_issues:
            self.logger.info("Auto-fix mode enabled")
        
        # Run health checks
        issues = []
        checks_passed = 0
        total_checks = 0
        
        # Check configuration files
        config_issues = self._check_configuration_files(fix_issues)
        issues.extend(config_issues)
        total_checks += 3
        checks_passed += (3 - len(config_issues))
        
        # Check directories
        dir_issues = self._check_directories(fix_issues)
        issues.extend(dir_issues)
        total_checks += 3
        checks_passed += (3 - len(dir_issues))
        
        # Check dependencies
        dep_issues = self._check_dependencies()
        issues.extend(dep_issues)
        total_checks += 2
        checks_passed += (2 - len(dep_issues))
        
        # Check permissions
        perm_issues = self._check_permissions()
        issues.extend(perm_issues)
        total_checks += 2
        checks_passed += (2 - len(perm_issues))
        
        # Display results
        self._display_health_results(checks_passed, total_checks, issues)
        
        if issues:
            return CommandResult.warning(
                f"Health check completed: {checks_passed}/{total_checks} checks passed",
                suggestions=[
                    "Fix the issues listed above",
                    "Run with --fix to attempt automatic fixes",
                    "Use 'genebot init-config' to recreate missing files"
                ]
            )
        
        return CommandResult.success(
            f"All {total_checks} health checks passed successfully"
        )
    
    def _check_configuration_files(self, fix_issues: bool) -> List[str]:
        """Check configuration files"""
        issues = []
        
        required_files = [
            ('.env', 'Environment variables file'),
            ('config/accounts.yaml', 'Account configuration'),
            ('config/trading_bot_config.yaml', 'Bot configuration')
        ]
        
        for file_path, description in required_files:
            path = Path(file_path)
            if not path.exists():
                issues.append(f"Missing {description}: {file_path}")
                if fix_issues:
                    self.logger.progress(f"Creating {file_path}...")
                    # TODO: Create default file
            else:
                self.logger.list_item(f"{description}: ✅", "success")
        
        return issues
    
    def _check_directories(self, fix_issues: bool) -> List[str]:
        """Check required directories"""
        issues = []
        
        required_dirs = [
            ('logs', 'Log files directory'),
            ('reports', 'Reports directory'),
            ('backups', 'Backups directory')
        ]
        
        for dir_path, description in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                issues.append(f"Missing {description}: {dir_path}")
                if fix_issues:
                    self.logger.progress(f"Creating directory {dir_path}...")
                    path.mkdir(parents=True, exist_ok=True)
            else:
                self.logger.list_item(f"{description}: ✅", "success")
        
        return issues
    
    def _check_dependencies(self) -> List[str]:
        """Check Python dependencies"""
        issues = []
        
        try:
            import yaml
            self.logger.list_item("PyYAML dependency: ✅", "success")
        except ImportError:
            issues.append("Missing required dependency: PyYAML")
        
        try:
            import ccxt
            self.logger.list_item("CCXT dependency: ✅", "success")
        except ImportError:
            issues.append("Missing required dependency: CCXT")
        
        return issues
    
    def _check_permissions(self) -> List[str]:
        """Check file permissions"""
        issues = []
        
        # Check config directory permissions
        config_dir = Path('config')
        if config_dir.exists():
            if not config_dir.is_dir():
                issues.append("config path exists but is not a directory")
            elif not os.access(config_dir, os.W_OK):
                issues.append("config directory is not writable")
            else:
                self.logger.list_item("Config directory permissions: ✅", "success")
        
        # Check logs directory permissions
        logs_dir = Path('logs')
        if logs_dir.exists():
            if not os.access(logs_dir, os.W_OK):
                issues.append("logs directory is not writable")
            else:
                self.logger.list_item("Logs directory permissions: ✅", "success")
        
        return issues
    
    def _display_health_results(self, passed: int, total: int, issues: List[str]) -> None:
        """Display health check results"""
        self.logger.subsection("Health Check Results")
        
        percentage = (passed / total * 100) if total > 0 else 0
        status_icon = "✅" if percentage == 100 else "⚠️" if percentage >= 70 else "❌"
        
        self.logger.info(f"{status_icon} Overall Health: {passed}/{total} checks passed ({percentage:.1f}%)")
        
        if issues:
            self.logger.subsection("Issues Found")
            for issue in issues:
                self.logger.list_item(issue, "error")


class BackupConfigCommand(BaseCommand):
    """Backup configurations"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute backup config command"""
        output_dir = getattr(args, 'output', None)
        
        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"backups/config_backup_{timestamp}"
        
        output_path = Path(output_dir)
        
        self.logger.section("Configuration Backup")
        self.logger.info(f"Backup destination: {output_path}")
        
        # Create backup directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Files to backup
        backup_files = [
            '.env',
            'config/accounts.yaml',
            'config/trading_bot_config.yaml',
            'config/compliance_config.yaml',
            'config/monitoring_config.yaml'
        ]
        
        backed_up = []
        skipped = []
        
        for file_path in backup_files:
            source = Path(file_path)
            if source.exists():
                dest = output_path / source.name
                try:
                    shutil.copy2(source, dest)
                    backed_up.append(file_path)
                    self.logger.list_item(f"Backed up: {file_path}", "success")
                except Exception as e:
                    self.logger.list_item(f"Failed to backup {file_path}: {str(e)}", "error")
            else:
                skipped.append(file_path)
                self.logger.list_item(f"Skipped (not found): {file_path}", "warning")
        
        # Create backup manifest
        manifest = {
            'backup_date': datetime.now().isoformat(),
            'backed_up_files': backed_up,
            'skipped_files': skipped,
            'total_files': len(backed_up)
        }
        
        manifest_file = output_path / 'backup_manifest.json'
        import json
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self.logger.success(f"Backup completed: {len(backed_up)} files backed up")
        
        return CommandResult.success(
            f"Configuration backup created at {output_path}",
            data=manifest
        )


class ResetCommand(BaseCommand):
    """Reset system by cleaning up all data"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute reset command"""
        confirm = getattr(args, 'confirm', False)
        keep_config = getattr(args, 'keep_config', False)
        
        self.logger.section("System Reset")
        
        if keep_config:
            self.logger.info("Configuration files will be preserved")
        else:
            self.logger.warning("This will remove ALL configuration and data files")
        
        if not confirm:
            warning_msg = "Reset system and remove all data"
            if keep_config:
                warning_msg = "Reset system (keeping configuration files)"
            
            if not self.confirm_action(warning_msg + "?", default=False):
                return CommandResult.info("System reset cancelled by user")
        
        # Items to clean up
        cleanup_items = []
        
        # Data directories
        data_dirs = ['logs', 'reports', 'backups']
        if not keep_config:
            data_dirs.append('config')
        
        # Files to remove
        files_to_remove = []
        if not keep_config:
            files_to_remove.extend(['.env', 'genebot.db'])
        
        # Clean up directories
        for dir_name in data_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    cleanup_items.append(f"Removed directory: {dir_name}")
                    self.logger.list_item(f"Removed: {dir_name}/", "success")
                except Exception as e:
                    self.logger.list_item(f"Failed to remove {dir_name}: {str(e)}", "error")
        
        # Clean up files
        for file_name in files_to_remove:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    file_path.unlink()
                    cleanup_items.append(f"Removed file: {file_name}")
                    self.logger.list_item(f"Removed: {file_name}", "success")
                except Exception as e:
                    self.logger.list_item(f"Failed to remove {file_name}: {str(e)}", "error")
        
        if cleanup_items:
            self.logger.success(f"System reset completed: {len(cleanup_items)} items removed")
            
            suggestions = ["Run 'genebot init-config' to set up the system again"]
            if keep_config:
                suggestions.append("Configuration files were preserved")
            
            return CommandResult.success(
                "System reset completed successfully",
                suggestions=suggestions
            )
        else:
            return CommandResult.info("No files or directories found to clean up")
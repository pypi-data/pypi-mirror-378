"""
Security Commands
=================

CLI commands for security management, credential validation, and audit operations.
"""

import argparse
from pathlib import Path
from typing import Optional

from ..result import CommandResult
from ..context import CLIContext
from .base import BaseCommand
from ..utils.security_manager import SecurityManager
from ..utils.error_handler import CLIErrorHandler


class SecurityCommand(BaseCommand):
    """Security management commands"""
    
    def __init__(self, context: CLIContext, logger=None, error_handler=None, output_manager=None):
        # Create default logger and error handler if not provided
        if logger is None:
            from ..utils.logger import CLILogger
            logger = CLILogger(context.log_level)
        
        if error_handler is None:
            error_handler = CLIErrorHandler(
                verbose=context.verbose,
                workspace_path=context.workspace_path
            )
        
        super().__init__(context, logger, error_handler, output_manager)
        self.security_manager = SecurityManager(
            workspace_path=context.workspace_path,
            config_path=context.config_path
        )
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup security command parser"""
        subparsers = parser.add_subparsers(dest='security_action', help='Security actions')
        
        # Validate credentials command
        validate_parser = subparsers.add_parser(
            'validate-credentials',
            help='Validate credentials without exposing sensitive data'
        )
        validate_parser.add_argument(
            '--env-file',
            type=Path,
            help='Path to environment file (default: .env)'
        )
        
        # Audit command
        audit_parser = subparsers.add_parser(
            'audit',
            help='Perform comprehensive security audit'
        )
        
        # Fix permissions command
        fix_parser = subparsers.add_parser(
            'fix-permissions',
            help='Fix insecure file permissions'
        )
        fix_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes'
        )
        
        # Check permissions command
        check_parser = subparsers.add_parser(
            'check-permissions',
            help='Check file permissions for security issues'
        )
        check_parser.add_argument(
            'files',
            nargs='*',
            type=Path,
            help='Specific files to check (default: check important files)'
        )
        
        # Rotation guide command
        rotation_parser = subparsers.add_parser(
            'rotation-guide',
            help='Generate credential rotation guidance'
        )
        
        # Audit log command
        log_parser = subparsers.add_parser(
            'audit-log',
            help='View security audit log'
        )
        log_parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of entries to show (default: 50)'
        )
        log_parser.add_argument(
            '--operation',
            help='Filter by operation type'
        )
        log_parser.add_argument(
            '--user',
            help='Filter by user'
        )
        log_parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back (default: 30)'
        )
        
        # Generate security config command
        config_parser = subparsers.add_parser(
            'init-config',
            help='Generate security configuration template'
        )
    
    def execute(self, args: argparse.Namespace) -> CommandResult:
        """Execute security command"""
        try:
            action = getattr(args, 'security_action', None)
            
            if action == 'validate-credentials':
                return self._validate_credentials(args)
            elif action == 'audit':
                return self._audit_security(args)
            elif action == 'fix-permissions':
                return self._fix_permissions(args)
            elif action == 'check-permissions':
                return self._check_permissions(args)
            elif action == 'rotation-guide':
                return self._rotation_guide(args)
            elif action == 'audit-log':
                return self._audit_log(args)
            elif action == 'init-config':
                return self._init_security_config(args)
            else:
                return CommandResult.error(
                    message="No security action specified",
                    suggestions=[
                        "Use 'genebot security validate-credentials' to check credentials",
                        "Use 'genebot security audit' for comprehensive security audit",
                        "Use 'genebot security --help' to see all available actions"
                    ]
                )
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Security command execution")
    
    def _validate_credentials(self, args: argparse.Namespace) -> CommandResult:
        """Validate credentials securely"""
        try:
            env_file = args.env_file if hasattr(args, 'env_file') and args.env_file else None
            result = self.security_manager.validate_credentials_secure(env_file)
            
            # Add formatted output for credentials
            if result.data and 'credentials' in result.data:
                credentials = result.data['credentials']
                
                if credentials:
                    if self.output:
                        self.output.print_section("Credential Validation Results")
                    
                    for cred in credentials:
                        status_icon = "✅" if cred['strength_score'] >= 60 else "⚠️" if cred['strength_score'] >= 40 else "❌"
                        rotation_icon = "🔄" if cred['rotation_due'] else "✓"
                        
                        if self.output:
                            self.output.print_item(
                                f"{status_icon} {cred['name']}",
                                f"Type: {cred['credential_type']}, "
                                f"Strength: {cred['strength_score']}/100, "
                                f"Value: {cred['masked_value']}, "
                                f"Rotation: {rotation_icon}"
                            )
                    
                    # Show file security status
                    if 'file_security' in result.data:
                        file_sec = result.data['file_security']
                        security_icon = "🔒" if file_sec['is_secure'] else "🔓"
                        if self.output:
                            self.output.print_item(
                                f"{security_icon} File Security",
                                f"Permissions: {oct(file_sec['permissions'])}, "
                                f"Secure: {'Yes' if file_sec['is_secure'] else 'No'}"
                            )
            
            return result
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Credential validation")
    
    def _audit_security(self, args: argparse.Namespace) -> CommandResult:
        """Perform security audit"""
        try:
            result = self.security_manager.audit_workspace_security()
            
            # Add formatted output for audit results
            if result.data and self.output:
                audit_data = result.data
                
                self.output.print_section("Security Audit Results")
                
                # Summary
                self.output.print_item(
                    "Files Checked",
                    f"{audit_data['files_checked']} total, "
                    f"{audit_data['secure_files']} secure, "
                    f"{audit_data['insecure_files']} insecure"
                )
                
                # Issues by severity
                for level, issues in [
                    ('Critical', audit_data['critical_issues']),
                    ('High', audit_data['high_issues']),
                    ('Medium', audit_data['medium_issues']),
                    ('Low', audit_data['low_issues'])
                ]:
                    if issues:
                        icon = "🚨" if level == 'Critical' else "⚠️" if level in ['High', 'Medium'] else "ℹ️"
                        self.output.print_item(
                            f"{icon} {level} Issues",
                            f"{len(issues)} found"
                        )
                        
                        if self.context.verbose:
                            for issue in issues[:3]:  # Show first 3 issues
                                if 'file' in issue:
                                    self.output.print_subitem(
                                        issue['file'],
                                        f"Permissions: {issue.get('permissions', 'unknown')}"
                                    )
                                elif 'directory' in issue:
                                    self.output.print_subitem(
                                        issue['directory'],
                                        issue.get('issue', 'Permission issue')
                                    )
            
            return result
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Security audit")
    
    def _fix_permissions(self, args: argparse.Namespace) -> CommandResult:
        """Fix file permissions"""
        try:
            dry_run = getattr(args, 'dry_run', False)
            result = self.security_manager.fix_file_permissions(dry_run=dry_run)
            
            # Add formatted output for fixes
            if result.data and 'fixes_applied' in result.data and self.output:
                fixes = result.data['fixes_applied']
                
                if fixes:
                    action = "Would fix" if dry_run else "Fixed"
                    self.output.print_section(f"{action} File Permissions")
                    
                    for fix in fixes:
                        icon = "🔧" if not dry_run else "👁️"
                        self.output.print_item(
                            f"{icon} {fix['file']}",
                            f"{fix['old_permissions']} → {fix['new_permissions']} ({fix['level']} priority)"
                        )
                
                if 'fixes_failed' in result.data and result.data['fixes_failed']:
                    failed = result.data['fixes_failed']
                    self.output.print_section("Failed Fixes")
                    
                    for fail in failed:
                        self.output.print_item(
                            f"❌ {fail['file']}",
                            f"Error: {fail['error']}"
                        )
            
            return result
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Permission fix")
    
    def _check_permissions(self, args: argparse.Namespace) -> CommandResult:
        """Check file permissions"""
        try:
            files_to_check = getattr(args, 'files', [])
            
            if not files_to_check:
                # Check default important files
                files_to_check = [
                    self.context.workspace_path / ".env",
                    self.context.config_path / "accounts.yaml",
                    self.context.config_path / "trading_bot_config.yaml"
                ]
            
            results = []
            issues_found = 0
            
            if self.output:
                self.output.print_section("File Permission Check")
            
            for file_path in files_to_check:
                if isinstance(file_path, str):
                    file_path = Path(file_path)
                
                file_security = self.security_manager.check_file_permissions(file_path)
                results.append(file_security)
                
                if not file_security.is_secure:
                    issues_found += 1
                
                # Display result
                if self.output:
                    icon = "🔒" if file_security.is_secure else "🔓"
                    status = "Secure" if file_security.is_secure else "Insecure"
                    
                    self.output.print_item(
                        f"{icon} {file_path.name}",
                        f"Permissions: {oct(file_security.permissions)}, Status: {status}"
                    )
                    
                    if not file_security.is_secure and file_security.recommendations:
                        for rec in file_security.recommendations[:2]:  # Show first 2 recommendations
                            self.output.print_subitem("Fix", rec)
            
            # Summary
            if issues_found == 0:
                return CommandResult.success(
                    message=f"All {len(results)} file(s) have secure permissions",
                    data={'files_checked': results}
                )
            else:
                return CommandResult.warning(
                    message=f"Found permission issues in {issues_found} of {len(results)} file(s)",
                    suggestions=[
                        "Use 'genebot security fix-permissions' to auto-fix issues",
                        "Review and manually fix permission issues",
                        "Run 'genebot security audit' for comprehensive analysis"
                    ],
                    data={'files_checked': results, 'issues_found': issues_found}
                )
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Permission check")
    
    def _rotation_guide(self, args: argparse.Namespace) -> CommandResult:
        """Generate credential rotation guide"""
        try:
            result = self.security_manager.generate_credential_rotation_guide()
            
            # Add formatted output for rotation guide
            if result.data and self.output:
                guide = result.data
                
                self.output.print_section("Credential Rotation Guide")
                
                # Overview
                if 'overview' in guide:
                    overview = guide['overview']
                    self.output.print_item(
                        "Rotation Frequency",
                        overview.get('frequency', 'Every 90 days')
                    )
                    self.output.print_item(
                        "Importance",
                        overview.get('importance', 'Reduces security risks')
                    )
                
                # Current status
                if 'current_status' in guide and guide['current_status']:
                    self.output.print_section("Current Credential Status")
                    
                    for cred_name, status in guide['current_status'].items():
                        rotation_icon = "🔄" if status['rotation_due'] else "✓"
                        strength_icon = "💪" if status['strength'] >= 80 else "⚠️" if status['strength'] >= 60 else "❌"
                        
                        self.output.print_item(
                            f"{rotation_icon} {strength_icon} {cred_name}",
                            f"Type: {status['type']}, "
                            f"Strength: {status['strength']}/100, "
                            f"Value: {status['masked_value']}"
                        )
                
                # Next actions
                if 'next_actions' in guide and guide['next_actions']:
                    self.output.print_section("Recommended Actions")
                    
                    for action in guide['next_actions']:
                        priority_icon = "🚨" if action['priority'] == 'HIGH' else "⚠️" if action['priority'] == 'MEDIUM' else "ℹ️"
                        
                        self.output.print_item(
                            f"{priority_icon} {action['credential']}",
                            f"Priority: {action['priority']}, Reason: {action['reason']}"
                        )
                        self.output.print_subitem("Action", action['action'])
                
                # Show procedures in verbose mode
                if self.context.verbose and 'procedures' in guide:
                    self.output.print_section("Rotation Procedures")
                    
                    for cred_name, procedure in guide['procedures'].items():
                        self.output.print_item(f"📋 {cred_name}", "Rotation Steps:")
                        
                        for step in procedure.get('steps', [])[:3]:  # Show first 3 steps
                            self.output.print_subitem("Step", step)
                        
                        if len(procedure.get('steps', [])) > 3:
                            self.output.print_subitem("...", f"and {len(procedure['steps']) - 3} more steps")
            
            return result
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Rotation guide generation")
    
    def _audit_log(self, args: argparse.Namespace) -> CommandResult:
        """View security audit log"""
        try:
            limit = getattr(args, 'limit', 50)
            operation_filter = getattr(args, 'operation', None)
            user_filter = getattr(args, 'user', None)
            days_back = getattr(args, 'days', 30)
            
            result = self.security_manager.get_audit_log(
                limit=limit,
                operation_filter=operation_filter,
                user_filter=user_filter,
                days_back=days_back
            )
            
            # Add formatted output for audit log
            if result.data and 'entries' in result.data and self.output:
                entries = result.data['entries']
                
                if entries:
                    self.output.print_section(f"Security Audit Log ({len(entries)} entries)")
                    
                    for entry in entries:
                        # Parse timestamp
                        timestamp = entry['timestamp'][:19].replace('T', ' ')  # Format: YYYY-MM-DD HH:MM:SS
                        
                        # Status icon
                        status_icon = "✅" if entry['success'] else "❌"
                        
                        # Security level icon
                        level_icons = {
                            'critical': '🚨',
                            'high': '⚠️',
                            'medium': '🔶',
                            'low': 'ℹ️'
                        }
                        level_icon = level_icons.get(entry['security_level'], 'ℹ️')
                        
                        self.output.print_item(
                            f"{status_icon} {level_icon} {entry['operation']}",
                            f"User: {entry['user']}, Resource: {entry['resource']}, Time: {timestamp}"
                        )
                        
                        # Show details in verbose mode
                        if self.context.verbose and entry.get('details'):
                            details = entry['details']
                            for key, value in list(details.items())[:2]:  # Show first 2 details
                                self.output.print_subitem(key.title(), str(value))
                else:
                    self.output.print_info("No audit log entries found for the specified criteria")
            
            return result
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Audit log retrieval")
    
    def _init_security_config(self, args: argparse.Namespace) -> CommandResult:
        """Initialize security configuration"""
        try:
            config_file = self.context.config_path / "security_config.yaml"
            
            if config_file.exists():
                return CommandResult.warning(
                    message="Security configuration already exists",
                    suggestions=[
                        f"Edit existing config at {config_file}",
                        "Use --force to overwrite existing configuration",
                        "Backup existing configuration before overwriting"
                    ]
                )
            
            # Create security configuration template
            config_template = """# Security Configuration
# This file contains security settings for the GeneBot CLI

# Credential rotation settings
credential_rotation_days: 90  # Days between required credential rotations

# Password requirements
password_min_length: 12
password_require_special: true
password_require_numbers: true
password_require_uppercase: true

# File permission settings
file_permission_checks: true
secure_file_permissions: 0o600  # Octal notation for file permissions
secure_dir_permissions: 0o700   # Octal notation for directory permissions

# Audit settings
audit_retention_days: 365  # Days to retain audit logs

# Allowed credential sources
allowed_credential_sources:
  - ".env"
  - "accounts.yaml"

# Credential strength requirements
credential_strength_requirements:
  api_key:
    min_length: 20
    entropy_bits: 128
  secret_key:
    min_length: 32
    entropy_bits: 256
  password:
    min_length: 12
    entropy_bits: 60

# Security monitoring
monitor_file_changes: true
alert_on_permission_changes: true
log_credential_access: true
"""
            
            # Ensure config directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            config_file.write_text(config_template)
            
            # Set secure permissions on the config file
            config_file.chmod(0o600)
            
            return CommandResult.success(
                message=f"Security configuration created at {config_file}",
                suggestions=[
                    "Review and customize security settings",
                    "Run 'genebot security audit' to check current security status",
                    "Set up regular security audits and credential rotation"
                ]
            )
        
        except Exception as e:
            return self.error_handler.handle_exception(e, "Security config initialization")
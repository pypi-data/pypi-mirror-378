"""
Error Reporting Commands
=======================

Commands for generating error reports and running system diagnostics.
"""

from argparse import Namespace
from pathlib import Path
import json

from ..result import CommandResult
from .base import BaseCommand
from ..utils.error_recovery import ComprehensiveRecoveryManager


class ErrorReportCommand(BaseCommand):
    """Generate comprehensive error report"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute error report generation"""
        include_recovery = getattr(args, 'include_recovery', False)
        output_file = getattr(args, 'output', None)
        verbose_report = getattr(args, 'verbose', False)
        
        self.logger.section("Generating Error Report")
        
        try:
            # Create error report from error handler
            error_report = self.error_handler.create_error_report(include_history=True)
            
            # Add system diagnostics if requested
            if include_recovery or verbose_report:
                self.logger.progress("Running system diagnostics...")
                recovery_manager = ComprehensiveRecoveryManager(self.context.workspace_path)
                recovery_results = recovery_manager.run_full_system_recovery()
                error_report['system_recovery'] = recovery_results
            
            # Determine output file
            if output_file:
                report_path = Path(output_file)
            else:
                report_path = self.error_handler.save_error_report()
            
            # Save report
            if output_file:
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w') as f:
                    json.dump(error_report, f, indent=2, default=str)
            
            # Display summary
            self._display_report_summary(error_report)
            
            return CommandResult.success(
                f"Error report generated successfully: {report_path}",
                data={
                    'report_path': str(report_path),
                    'error_count': len(error_report.get('error_history', [])),
                    'system_health': self._assess_system_health(error_report)
                },
                suggestions=[
                    f"Review the detailed report at {report_path}",
                    "Share this report when seeking technical support",
                    "Use 'genebot system-recovery' to attempt automatic fixes"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to generate error report: {str(e)}",
                suggestions=[
                    "Check disk space and file permissions",
                    "Try specifying a different output location",
                    "Run with --verbose for more details"
                ]
            )
    
    def _display_report_summary(self, report: dict) -> None:
        """Display a summary of the error report"""
        self.logger.subsection("Error Report Summary")
        
        # Basic information
        self.logger.list_item(f"Workspace: {report.get('workspace_path', 'Unknown')}", "info")
        self.logger.list_item(f"Generated: {report.get('timestamp', 'Unknown')}", "info")
        
        # Error history
        error_history = report.get('error_history', [])
        if error_history:
            self.logger.list_item(f"Recent Errors: {len(error_history)}", "warning")
            
            # Show most recent errors
            recent_errors = error_history[-3:] if len(error_history) > 3 else error_history
            for error in recent_errors:
                self.logger.list_item(f"  • {error.get('error_type', 'Unknown')}: {error.get('message', 'No message')[:50]}...", "error")
        else:
            self.logger.list_item("Recent Errors: None", "success")
        
        # System recovery information
        if 'system_recovery' in report:
            recovery = report['system_recovery']
            success_rate = recovery.get('success_rate', 0) * 100
            
            if success_rate >= 80:
                status_icon = "🟢"
                status_text = "Good"
            elif success_rate >= 60:
                status_icon = "🟡"
                status_text = "Fair"
            else:
                status_icon = "🔴"
                status_text = "Poor"
            
            self.logger.list_item(f"System Health: {status_icon} {status_text} ({success_rate:.1f}%)", "info")
    
    def _assess_system_health(self, report: dict) -> str:
        """Assess overall system health from report"""
        if 'system_recovery' not in report:
            return "unknown"
        
        success_rate = report['system_recovery'].get('success_rate', 0)
        
        if success_rate >= 0.8:
            return "good"
        elif success_rate >= 0.6:
            return "fair"
        else:
            return "poor"


class SystemRecoveryCommand(BaseCommand):
    """Run comprehensive system recovery"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute system recovery"""
        auto_fix = getattr(args, 'auto_fix', False)
        dry_run = getattr(args, 'dry_run', False)
        save_report = getattr(args, 'save_report', True)
        
        self.logger.section("System Recovery")
        
        if dry_run:
            self.logger.info("Running in dry-run mode - no changes will be made")
        
        try:
            recovery_manager = ComprehensiveRecoveryManager(self.context.workspace_path)
            
            self.logger.progress("Running comprehensive system diagnostics...")
            recovery_results = recovery_manager.run_full_system_recovery()
            
            # Display results
            self._display_recovery_results(recovery_results)
            
            # Save report if requested
            report_path = None
            if save_report:
                self.logger.progress("Saving recovery report...")
                report_path = recovery_manager.save_recovery_report(recovery_results)
            
            # Determine overall result
            overall_success = recovery_results.get('overall_success', False)
            success_rate = recovery_results.get('success_rate', 0) * 100
            
            if overall_success:
                return CommandResult.success(
                    f"System recovery completed successfully (Success rate: {success_rate:.1f}%)",
                    data={
                        'recovery_results': recovery_results,
                        'report_path': str(report_path) if report_path else None
                    },
                    suggestions=[
                        "System appears to be healthy",
                        f"Review detailed report at {report_path}" if report_path else None
                    ]
                )
            else:
                failed_procedures = self._get_failed_procedures(recovery_results)
                
                return CommandResult.warning(
                    f"System recovery completed with issues (Success rate: {success_rate:.1f}%)",
                    data={
                        'recovery_results': recovery_results,
                        'failed_procedures': failed_procedures,
                        'report_path': str(report_path) if report_path else None
                    },
                    suggestions=[
                        "Review failed procedures and address manually",
                        "Check system resources and permissions",
                        f"Review detailed report at {report_path}" if report_path else None,
                        "Consider running individual recovery commands"
                    ]
                )
                
        except Exception as e:
            return CommandResult.error(
                f"System recovery failed: {str(e)}",
                suggestions=[
                    "Check system permissions and resources",
                    "Try running individual diagnostic commands",
                    "Review logs for detailed error information"
                ]
            )
    
    def _display_recovery_results(self, results: dict) -> None:
        """Display recovery results in a formatted way"""
        self.logger.subsection("Recovery Results")
        
        procedures = results.get('procedures', {})
        
        # System diagnostics
        if 'system_diagnostics' in procedures:
            self.logger.info("System Diagnostics:")
            diagnostics = procedures['system_diagnostics']
            
            for check_name, check_result in diagnostics.items():
                if isinstance(check_result, dict) and 'success' in check_result:
                    icon = "✅" if check_result['success'] else "❌"
                    message = check_result.get('message', check_name)
                    self.logger.list_item(f"{icon} {check_name}: {message}", "info")
        
        # Process recovery
        if 'process_recovery' in procedures:
            self.logger.info("Process Recovery:")
            process_recovery = procedures['process_recovery']
            
            for proc_name, proc_result in process_recovery.items():
                if isinstance(proc_result, dict) and 'success' in proc_result:
                    icon = "✅" if proc_result['success'] else "❌"
                    message = proc_result.get('message', proc_name)
                    self.logger.list_item(f"{icon} {proc_name}: {message}", "info")
        
        # Configuration recovery
        if 'configuration_recovery' in procedures:
            self.logger.info("Configuration Recovery:")
            config_recovery = procedures['configuration_recovery']
            
            for config_name, config_checks in config_recovery.items():
                self.logger.list_item(f"Configuration: {config_name}", "info")
                for check_name, check_result in config_checks.items():
                    if isinstance(check_result, dict) and 'success' in check_result:
                        icon = "✅" if check_result['success'] else "❌"
                        message = check_result.get('message', check_name)
                        self.logger.list_item(f"  {icon} {check_name}: {message}", "info")
        
        # Dependency recovery
        if 'dependency_recovery' in procedures:
            self.logger.info("Dependency Recovery:")
            dep_recovery = procedures['dependency_recovery']
            
            for dep_name, dep_result in dep_recovery.items():
                if isinstance(dep_result, dict) and 'success' in dep_result:
                    icon = "✅" if dep_result['success'] else "❌"
                    message = dep_result.get('message', dep_name)
                    self.logger.list_item(f"{icon} {dep_name}: {message}", "info")
        
        # Overall summary
        success_rate = results.get('success_rate', 0) * 100
        overall_success = results.get('overall_success', False)
        
        if overall_success:
            self.logger.success(f"Overall Status: ✅ Healthy (Success rate: {success_rate:.1f}%)")
        else:
            self.logger.warning(f"Overall Status: ⚠️  Issues detected (Success rate: {success_rate:.1f}%)")
    
    def _get_failed_procedures(self, results: dict) -> list:
        """Extract failed procedures from recovery results"""
        failed = []
        procedures = results.get('procedures', {})
        
        for category_name, category in procedures.items():
            if isinstance(category, dict):
                for proc_name, proc_result in category.items():
                    if isinstance(proc_result, dict):
                        if 'success' in proc_result and not proc_result['success']:
                            failed.append(f"{category_name}.{proc_name}")
                        else:
                            # Check nested procedures
                            for sub_name, sub_result in proc_result.items():
                                if isinstance(sub_result, dict) and 'success' in sub_result and not sub_result['success']:
                                    failed.append(f"{category_name}.{proc_name}.{sub_name}")
        
        return failed


class DiagnosticsCommand(BaseCommand):
    """Run system diagnostics without recovery"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute system diagnostics"""
        check_network = getattr(args, 'network', True)
        check_dependencies = getattr(args, 'dependencies', True)
        check_config = getattr(args, 'config', True)
        
        self.logger.section("System Diagnostics")
        
        try:
            from ..utils.error_recovery import SystemDiagnostics
            
            diagnostics = SystemDiagnostics(self.context.workspace_path)
            results = {}
            
            # Basic system checks
            self.logger.progress("Checking system resources...")
            results['disk_space'] = diagnostics.check_disk_space()
            results['memory_usage'] = diagnostics.check_memory_usage()
            results['python_environment'] = diagnostics.check_python_environment()
            
            # Network checks
            if check_network:
                self.logger.progress("Checking network connectivity...")
                results['network_connectivity'] = diagnostics.check_network_connectivity()
                results['ssl_certificates'] = diagnostics.check_ssl_certificates()
            
            # Display results
            self._display_diagnostic_results(results)
            
            # Assess overall health
            all_successful = all(
                result.get('success', False) 
                for result in results.values() 
                if isinstance(result, dict)
            )
            
            if all_successful:
                return CommandResult.success(
                    "All diagnostic checks passed",
                    data={'diagnostic_results': results}
                )
            else:
                failed_checks = [
                    name for name, result in results.items()
                    if isinstance(result, dict) and not result.get('success', False)
                ]
                
                return CommandResult.warning(
                    f"Some diagnostic checks failed: {', '.join(failed_checks)}",
                    data={'diagnostic_results': results, 'failed_checks': failed_checks},
                    suggestions=[
                        "Run 'genebot system-recovery' to attempt automatic fixes",
                        "Check system resources and network connectivity",
                        "Review failed checks for specific issues"
                    ]
                )
                
        except Exception as e:
            return CommandResult.error(
                f"Diagnostics failed: {str(e)}",
                suggestions=[
                    "Check system permissions",
                    "Ensure required dependencies are installed",
                    "Try running with --verbose for more details"
                ]
            )
    
    def _display_diagnostic_results(self, results: dict) -> None:
        """Display diagnostic results"""
        self.logger.subsection("Diagnostic Results")
        
        for check_name, result in results.items():
            if isinstance(result, dict):
                success = result.get('success', False)
                message = result.get('message', check_name)
                
                icon = "✅" if success else "❌"
                self.logger.list_item(f"{icon} {check_name}: {message}", "info")
                
                # Show additional details for failed checks
                if not success and 'error' in result:
                    self.logger.list_item(f"  Error: {result['error']}", "error")
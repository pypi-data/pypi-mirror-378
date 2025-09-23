"""
Error Recovery Procedures
========================

Comprehensive error recovery procedures for common CLI failure scenarios.
"""

import os
import sys
import shutil
import subprocess
import socket
import ssl
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml
import json
import logging
from datetime import datetime

from .config_manager import ConfigurationManager
from .file_manager import FileManager


class SystemDiagnostics:
    """System diagnostics and health checks"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger(__name__)
    
    def check_disk_space(self, min_free_gb: float = 1.0) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            statvfs = os.statvfs(self.workspace_path)
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            free_gb = free_bytes / (1024**3)
            
            return {
                'success': True,
                'free_gb': free_gb,
                'sufficient': free_gb >= min_free_gb,
                'message': f"Available disk space: {free_gb:.2f} GB"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check disk space: {e}"
            }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                'success': True,
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'percent_used': memory.percent,
                'sufficient': memory.percent < 90,
                'message': f"Memory usage: {memory.percent:.1f}% ({memory.available / (1024**3):.2f} GB available)"
            }
        except ImportError:
            return {
                'success': False,
                'error': 'psutil not available',
                'message': 'Cannot check memory usage - psutil not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check memory usage: {e}"
            }
    
    def check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment and dependencies"""
        try:
            python_version = sys.version_info
            executable = sys.executable
            
            # Check if we're in a virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            # Check pip availability
            try:
                import pip
                pip_available = True
            except ImportError:
                pip_available = False
            
            return {
                'success': True,
                'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                'executable': executable,
                'in_virtual_env': in_venv,
                'pip_available': pip_available,
                'message': f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ({'venv' if in_venv else 'system'})"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check Python environment: {e}"
            }
    
    def check_network_connectivity(self, hosts: List[str] = None) -> Dict[str, Any]:
        """Check network connectivity to various hosts"""
        if hosts is None:
            hosts = [
                ('google.com', 80),
                ('api.binance.com', 443),
                ('api.oanda.com', 443),
                ('8.8.8.8', 53)  # Google DNS
            ]
        
        results = {}
        successful_connections = 0
        total_hosts = len(hosts)
        
        for host_info in hosts:
            if isinstance(host_info, tuple):
                host, port = host_info
            else:
                host, port = host_info, 80
            
            try:
                socket.create_connection((host, port), timeout=5)
                results[host] = {'success': True, 'message': f"Connected to {host}:{port}"}
                successful_connections += 1
            except Exception as e:
                results[host] = {'success': False, 'error': str(e), 'message': f"Failed to connect to {host}:{port}"}
        
        # Consider it successful if at least half the connections work
        overall_success = successful_connections >= (total_hosts // 2)
        
        return {
            'success': overall_success,
            'results': results,
            'successful_connections': successful_connections,
            'total_hosts': total_hosts,
            'message': f"Network connectivity: {successful_connections}/{total_hosts} hosts reachable"
        }
    
    def check_ssl_certificates(self, hosts: List[str] = None) -> Dict[str, Any]:
        """Check SSL certificate validity for HTTPS endpoints"""
        if hosts is None:
            hosts = ['api.binance.com', 'api.oanda.com', 'api.kraken.com']
        
        results = {}
        successful_checks = 0
        total_hosts = len(hosts)
        
        for host in hosts:
            try:
                context = ssl.create_default_context()
                # Reduce timeout to avoid hanging
                with socket.create_connection((host, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        results[host] = {
                            'success': True,
                            'subject': dict(x[0] for x in cert['subject']),
                            'issuer': dict(x[0] for x in cert['issuer']),
                            'message': f"SSL certificate valid for {host}"
                        }
                        successful_checks += 1
            except Exception as e:
                results[host] = {
                    'success': False,
                    'error': str(e),
                    'message': f"SSL certificate issue for {host}: {str(e)[:100]}..."
                }
        
        # Consider it successful if at least one SSL check passes
        overall_success = successful_checks > 0
        
        return {
            'success': overall_success,
            'results': results,
            'successful_checks': successful_checks,
            'total_hosts': total_hosts,
            'message': f"SSL certificates: {successful_checks}/{total_hosts} hosts verified"
        }


class ConfigurationRecovery:
    """Configuration file recovery and repair"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.config_manager = ConfigurationManager()
        self.file_manager = FileManager()
        self.logger = logging.getLogger(__name__)
    
    def repair_corrupted_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Attempt to repair corrupted YAML files"""
        try:
            # Try to load the file
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            
            return {
                'success': True,
                'message': f"YAML file {file_path} is valid"
            }
        except yaml.YAMLError as e:
            # Attempt basic repairs
            try:
                content = file_path.read_text()
                
                # Common fixes
                fixes_applied = []
                
                # Fix common indentation issues
                lines = content.split('\n')
                fixed_lines = []
                for line in lines:
                    # Convert tabs to spaces
                    if '\t' in line:
                        line = line.replace('\t', '  ')
                        fixes_applied.append("Converted tabs to spaces")
                    
                    # Fix trailing spaces
                    if line.rstrip() != line:
                        line = line.rstrip()
                        fixes_applied.append("Removed trailing spaces")
                    
                    fixed_lines.append(line)
                
                # Try to parse the fixed content
                fixed_content = '\n'.join(fixed_lines)
                yaml.safe_load(fixed_content)
                
                # If successful, save the fixed version
                backup_path = self.file_manager.create_backup(file_path)
                file_path.write_text(fixed_content)
                
                return {
                    'success': True,
                    'fixes_applied': fixes_applied,
                    'backup_path': str(backup_path),
                    'message': f"Repaired YAML file {file_path}"
                }
            except Exception as repair_error:
                return {
                    'success': False,
                    'error': str(repair_error),
                    'original_error': str(e),
                    'message': f"Failed to repair YAML file {file_path}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check YAML file {file_path}"
            }
    
    def restore_default_config(self, config_type: str) -> Dict[str, Any]:
        """Restore default configuration for a specific type"""
        try:
            if config_type == 'accounts':
                return self._restore_accounts_config()
            elif config_type == 'trading_bot':
                return self._restore_trading_bot_config()
            elif config_type == 'monitoring':
                return self._restore_monitoring_config()
            else:
                return {
                    'success': False,
                    'error': f"Unknown config type: {config_type}",
                    'message': f"Cannot restore config for unknown type: {config_type}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to restore {config_type} configuration: {e}"
            }
    
    def _restore_accounts_config(self) -> Dict[str, Any]:
        """Restore default accounts configuration"""
        config_path = self.workspace_path / "config" / "accounts.yaml"
        
        default_config = {
            'accounts': {
                'crypto': {},
                'forex': {}
            },
            'settings': {
                'default_timeout': 30,
                'max_retries': 3,
                'rate_limit_delay': 1.0
            }
        }
        
        # Create backup if file exists
        if config_path.exists():
            backup_path = self.file_manager.create_backup(config_path)
        else:
            backup_path = None
        
        # Write default configuration
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        return {
            'success': True,
            'config_path': str(config_path),
            'backup_path': str(backup_path) if backup_path else None,
            'message': f"Restored default accounts configuration to {config_path}"
        }
    
    def _restore_trading_bot_config(self) -> Dict[str, Any]:
        """Restore default trading bot configuration"""
        config_path = self.workspace_path / "config" / "trading_bot_config.yaml"
        
        default_config = {
            'bot': {
                'name': 'GeneBot',
                'version': '1.1.28',
                'log_level': 'INFO'
            },
            'trading': {
                'enabled': True,
                'paper_trading': True,
                'max_positions': 5,
                'position_size': 0.1
            },
            'risk_management': {
                'max_drawdown': 0.1,
                'stop_loss': 0.02,
                'take_profit': 0.04
            },
            'strategies': {
                'enabled': ['moving_average'],
                'parameters': {
                    'moving_average': {
                        'short_period': 10,
                        'long_period': 20
                    }
                }
            }
        }
        
        # Create backup if file exists
        if config_path.exists():
            backup_path = self.file_manager.create_backup(config_path)
        else:
            backup_path = None
        
        # Write default configuration
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        return {
            'success': True,
            'config_path': str(config_path),
            'backup_path': str(backup_path) if backup_path else None,
            'message': f"Restored default trading bot configuration to {config_path}"
        }
    
    def _restore_monitoring_config(self) -> Dict[str, Any]:
        """Restore default monitoring configuration"""
        config_path = self.workspace_path / "config" / "monitoring_config.yaml"
        
        default_config = {
            'monitoring': {
                'enabled': True,
                'update_interval': 60,
                'metrics_retention_days': 30
            },
            'alerts': {
                'enabled': False,
                'email_notifications': False,
                'slack_notifications': False
            },
            'logging': {
                'level': 'INFO',
                'file_rotation': True,
                'max_file_size': '10MB',
                'backup_count': 5
            }
        }
        
        # Create backup if file exists
        if config_path.exists():
            backup_path = self.file_manager.create_backup(config_path)
        else:
            backup_path = None
        
        # Write default configuration
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        return {
            'success': True,
            'config_path': str(config_path),
            'backup_path': str(backup_path) if backup_path else None,
            'message': f"Restored default monitoring configuration to {config_path}"
        }
    
    def validate_and_fix_config_schema(self, config_path: Path) -> Dict[str, Any]:
        """Validate configuration schema and attempt fixes"""
        try:
            # Load configuration
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Validate using config manager
            validation_result = self.config_manager.validate_config_file(config_path)
            
            if validation_result['valid']:
                return {
                    'success': True,
                    'message': f"Configuration {config_path} is valid"
                }
            
            # Attempt to fix common schema issues
            fixes_applied = []
            
            # Add missing required sections
            if config_path.name == 'accounts.yaml':
                if 'accounts' not in config_data:
                    config_data['accounts'] = {'crypto': {}, 'forex': {}}
                    fixes_applied.append("Added missing 'accounts' section")
                
                if 'settings' not in config_data:
                    config_data['settings'] = {
                        'default_timeout': 30,
                        'max_retries': 3
                    }
                    fixes_applied.append("Added missing 'settings' section")
            
            # Save fixed configuration
            if fixes_applied:
                backup_path = self.file_manager.create_backup(config_path)
                with open(config_path, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                
                return {
                    'success': True,
                    'fixes_applied': fixes_applied,
                    'backup_path': str(backup_path),
                    'message': f"Fixed configuration schema for {config_path}"
                }
            
            return {
                'success': False,
                'validation_errors': validation_result.get('errors', []),
                'message': f"Configuration {config_path} has schema errors that cannot be auto-fixed"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to validate/fix configuration {config_path}: {e}"
            }


class ProcessRecovery:
    """Process management and recovery"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger(__name__)
    
    def cleanup_zombie_processes(self) -> Dict[str, Any]:
        """Clean up zombie or orphaned processes"""
        try:
            import psutil
            
            cleaned_processes = []
            current_pid = os.getpid()
            
            # Look for processes that might be related to genebot
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue
                    
                    cmdline = proc.info['cmdline'] or []
                    cmdline_str = ' '.join(cmdline).lower()
                    
                    # Check if it's a genebot process
                    if any(keyword in cmdline_str for keyword in ['genebot', 'trading_bot', 'main.py']):
                        # Check if it's a zombie or orphaned process
                        if proc.status() in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                            proc.terminate()
                            cleaned_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'status': 'terminated'
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'success': True,
                'cleaned_processes': cleaned_processes,
                'message': f"Cleaned up {len(cleaned_processes)} zombie processes"
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'psutil not available',
                'message': 'Cannot clean up processes - psutil not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to clean up processes: {e}"
            }
    
    def repair_pid_files(self) -> Dict[str, Any]:
        """Repair or remove invalid PID files"""
        try:
            pid_files = list(self.workspace_path.glob("*.pid"))
            repaired_files = []
            removed_files = []
            
            for pid_file in pid_files:
                try:
                    pid_str = pid_file.read_text().strip()
                    pid = int(pid_str)
                    
                    # Check if process exists
                    try:
                        os.kill(pid, 0)  # Signal 0 just checks existence
                        # Process exists, PID file is valid
                        continue
                    except OSError:
                        # Process doesn't exist, remove PID file
                        pid_file.unlink()
                        removed_files.append({
                            'file': str(pid_file),
                            'pid': pid,
                            'reason': 'Process not found'
                        })
                
                except (ValueError, FileNotFoundError):
                    # Invalid PID file content
                    pid_file.unlink()
                    removed_files.append({
                        'file': str(pid_file),
                        'pid': None,
                        'reason': 'Invalid PID format'
                    })
            
            return {
                'success': True,
                'repaired_files': repaired_files,
                'removed_files': removed_files,
                'message': f"Repaired PID files: {len(repaired_files)} fixed, {len(removed_files)} removed"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to repair PID files: {e}"
            }


class DependencyRecovery:
    """Dependency management and recovery"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger(__name__)
    
    def check_and_install_dependencies(self) -> Dict[str, Any]:
        """Check and attempt to install missing dependencies"""
        try:
            requirements_file = self.workspace_path / "requirements.txt"
            
            if not requirements_file.exists():
                return {
                    'success': False,
                    'error': 'requirements.txt not found',
                    'message': 'Cannot check dependencies - requirements.txt not found'
                }
            
            # Read requirements
            requirements = []
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        requirements.append(line)
            
            # Check each requirement
            missing_deps = []
            installed_deps = []
            
            for req in requirements:
                try:
                    import pkg_resources
                    pkg_resources.require(req)
                    installed_deps.append(req)
                except Exception:
                    missing_deps.append(req)
            
            if not missing_deps:
                return {
                    'success': True,
                    'installed_dependencies': installed_deps,
                    'message': f"All {len(installed_deps)} dependencies are installed"
                }
            
            # Attempt to install missing dependencies
            install_results = []
            for dep in missing_deps:
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', dep],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        install_results.append({
                            'dependency': dep,
                            'success': True,
                            'message': f"Successfully installed {dep}"
                        })
                    else:
                        install_results.append({
                            'dependency': dep,
                            'success': False,
                            'error': result.stderr,
                            'message': f"Failed to install {dep}"
                        })
                
                except subprocess.TimeoutExpired:
                    install_results.append({
                        'dependency': dep,
                        'success': False,
                        'error': 'Installation timeout',
                        'message': f"Installation of {dep} timed out"
                    })
                except Exception as e:
                    install_results.append({
                        'dependency': dep,
                        'success': False,
                        'error': str(e),
                        'message': f"Failed to install {dep}: {e}"
                    })
            
            successful_installs = [r for r in install_results if r['success']]
            failed_installs = [r for r in install_results if not r['success']]
            
            return {
                'success': len(failed_installs) == 0,
                'missing_dependencies': missing_deps,
                'install_results': install_results,
                'successful_installs': len(successful_installs),
                'failed_installs': len(failed_installs),
                'message': f"Dependency installation: {len(successful_installs)} successful, {len(failed_installs)} failed"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check/install dependencies: {e}"
            }
    
    def verify_python_version(self, min_version: Tuple[int, int] = (3, 8)) -> Dict[str, Any]:
        """Verify Python version meets requirements"""
        try:
            current_version = sys.version_info[:2]
            
            if current_version >= min_version:
                return {
                    'success': True,
                    'current_version': f"{current_version[0]}.{current_version[1]}",
                    'required_version': f"{min_version[0]}.{min_version[1]}",
                    'message': f"Python version {current_version[0]}.{current_version[1]} meets requirements"
                }
            else:
                return {
                    'success': False,
                    'current_version': f"{current_version[0]}.{current_version[1]}",
                    'required_version': f"{min_version[0]}.{min_version[1]}",
                    'message': f"Python version {current_version[0]}.{current_version[1]} is below required {min_version[0]}.{min_version[1]}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to check Python version: {e}"
            }


class ComprehensiveRecoveryManager:
    """Comprehensive recovery manager that coordinates all recovery procedures"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.diagnostics = SystemDiagnostics(workspace_path)
        self.config_recovery = ConfigurationRecovery(workspace_path)
        self.process_recovery = ProcessRecovery(workspace_path)
        self.dependency_recovery = DependencyRecovery(workspace_path)
        self.logger = logging.getLogger(__name__)
    
    def run_full_system_recovery(self) -> Dict[str, Any]:
        """Run comprehensive system recovery"""
        recovery_results = {
            'timestamp': datetime.now().isoformat(),
            'workspace_path': str(self.workspace_path),
            'procedures': {}
        }
        
        # System diagnostics
        recovery_results['procedures']['system_diagnostics'] = {
            'disk_space': self.diagnostics.check_disk_space(),
            'memory_usage': self.diagnostics.check_memory_usage(),
            'python_environment': self.diagnostics.check_python_environment(),
            'network_connectivity': self.diagnostics.check_network_connectivity(),
            'ssl_certificates': self.diagnostics.check_ssl_certificates()
        }
        
        # Process recovery
        recovery_results['procedures']['process_recovery'] = {
            'cleanup_zombies': self.process_recovery.cleanup_zombie_processes(),
            'repair_pid_files': self.process_recovery.repair_pid_files()
        }
        
        # Configuration recovery
        config_files = [
            'accounts.yaml',
            'trading_bot_config.yaml',
            'monitoring_config.yaml'
        ]
        
        recovery_results['procedures']['configuration_recovery'] = {}
        for config_file in config_files:
            config_path = self.workspace_path / 'config' / config_file
            if config_path.exists():
                recovery_results['procedures']['configuration_recovery'][config_file] = {
                    'yaml_repair': self.config_recovery.repair_corrupted_yaml(config_path),
                    'schema_validation': self.config_recovery.validate_and_fix_config_schema(config_path)
                }
        
        # Dependency recovery
        recovery_results['procedures']['dependency_recovery'] = {
            'python_version': self.dependency_recovery.verify_python_version(),
            'dependencies': self.dependency_recovery.check_and_install_dependencies()
        }
        
        # Calculate overall success
        all_procedures = []
        for category in recovery_results['procedures'].values():
            if isinstance(category, dict):
                for procedure in category.values():
                    if isinstance(procedure, dict) and 'success' in procedure:
                        all_procedures.append(procedure['success'])
                    elif isinstance(procedure, dict):
                        # Nested procedures
                        for sub_procedure in procedure.values():
                            if isinstance(sub_procedure, dict) and 'success' in sub_procedure:
                                all_procedures.append(sub_procedure['success'])
        
        recovery_results['overall_success'] = all(all_procedures) if all_procedures else False
        recovery_results['success_rate'] = sum(all_procedures) / len(all_procedures) if all_procedures else 0
        
        return recovery_results
    
    def save_recovery_report(self, recovery_results: Dict[str, Any]) -> Path:
        """Save recovery report to file"""
        reports_dir = self.workspace_path / "logs" / "recovery"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"recovery_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(recovery_results, f, indent=2, default=str)
        
        return report_path
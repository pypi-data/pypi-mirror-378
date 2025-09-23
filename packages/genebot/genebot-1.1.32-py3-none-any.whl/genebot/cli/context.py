"""
CLI Context Management
=====================

Shared context for CLI operations with configuration and state management.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import os


@dataclass
class CLIContext:
    """Shared context for CLI operations"""
    config_path: Path
    log_level: str = "INFO"
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    force: bool = False
    auto_recover: bool = False
    no_color: bool = False
    output_file: Optional[Path] = None
    
    def __post_init__(self):
        """Initialize context after creation"""
        # Ensure config path is absolute
        if not self.config_path.is_absolute():
            self.config_path = Path.cwd() / self.config_path
        
        # Create config directory if it doesn't exist
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize orchestrator instance storage
        self._orchestrator_instance = None
    
    @classmethod
    def from_args(cls, args) -> 'CLIContext':
        """Create context from parsed command line arguments"""
        config_path = getattr(args, 'config_path', None)
        if config_path is None:
            config_path = Path(os.getenv('GENEBOT_CONFIG_PATH', 'config'))
        
        output_file = getattr(args, 'output_file', None)
        if output_file:
            output_file = Path(output_file)
        
        return cls(
            config_path=Path(config_path),
            log_level=getattr(args, 'log_level', 'INFO'),
            dry_run=getattr(args, 'dry_run', False),
            verbose=getattr(args, 'verbose', False),
            quiet=getattr(args, 'quiet', False),
            force=getattr(args, 'force', False),
            auto_recover=getattr(args, 'auto_recover', False),
            no_color=getattr(args, 'no_color', False),
            output_file=output_file
        )
    
    @property
    def workspace_path(self) -> Path:
        """Path to workspace directory (parent of config)"""
        return self.config_path.parent
    
    @property
    def accounts_file(self) -> Path:
        """Path to accounts configuration file"""
        return self.config_path / 'accounts.yaml'
    
    @property
    def bot_config_file(self) -> Path:
        """Path to bot configuration file"""
        return self.config_path / 'trading_bot_config.yaml'
    
    @property
    def env_file(self) -> Path:
        """Path to environment file"""
        return Path('.env')
    
    @property
    def workspace_path(self) -> Path:
        """Path to workspace directory (parent of config)"""
        return self.config_path.parent
    
    def get_config_files(self) -> Dict[str, Path]:
        """Get all configuration file paths"""
        return {
            'accounts': self.accounts_file,
            'bot_config': self.bot_config_file,
            'env': self.env_file
        }
    
    def set_orchestrator_instance(self, orchestrator) -> None:
        """Set the orchestrator instance"""
        self._orchestrator_instance = orchestrator
    
    def get_orchestrator_instance(self):
        """Get the orchestrator instance"""
        return self._orchestrator_instance
    
    def clear_orchestrator_instance(self) -> None:
        """Clear the orchestrator instance"""
        self._orchestrator_instance = None
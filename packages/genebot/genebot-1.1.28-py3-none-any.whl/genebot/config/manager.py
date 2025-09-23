"""
Minimal configuration manager for GeneBot CLI
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigurationError(Exception):
    """Configuration error exception"""
    pass


class ConfigManager:
    """Minimal config manager for CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/trading_bot_config.yaml"
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
        except Exception as e:
            # Don't fail if config doesn't exist, just use empty config
            self.config = {}
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration"""
        self.config.update(updates)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value


def get_config_manager() -> ConfigManager:
    """Get config manager instance"""
    return ConfigManager()
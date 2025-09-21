"""
Minimal configuration models for GeneBot CLI
"""

from typing import Dict, Any, Optional


class TradingBotConfig:
    """Minimal trading bot configuration model"""
    
    def __init__(self, **kwargs):
        """Initialize config with provided values"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingBotConfig':
        """Create from dictionary"""
        return cls(**data)
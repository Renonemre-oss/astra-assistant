#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Configuration Schema
Validated configuration using Pydantic for type safety and validation.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OllamaConfig(BaseModel):
    """Ollama configuration."""
    model: str = Field(default="gemma3n:e4b", description="Ollama model name")
    url: str = Field(default="http://localhost:11434/api/generate", description="Ollama API URL")
    timeout: int = Field(default=120, ge=10, le=600, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum number of retries")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class ConversationConfig(BaseModel):
    """Conversation configuration."""
    history_size: int = Field(default=3, ge=1, le=100, description="Number of messages to keep in history")
    
    @validator('history_size')
    def validate_history_size(cls, v):
        """Ensure history size is reasonable."""
        if v > 50:
            import warnings
            warnings.warn("Large history size may impact performance")
        return v


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""
    model: str = Field(default="tts_models/pt/cv/vits", description="TTS model to use")
    temp_audio_dir: Optional[Path] = Field(default=None, description="Directory for temporary audio files")
    
    @validator('temp_audio_dir', pre=True)
    def set_temp_audio_dir(cls, v, values):
        """Set default temp audio directory if not provided."""
        if v is None:
            return Path("audio")
        return Path(v) if not isinstance(v, Path) else v


class DatabaseConfig(BaseModel):
    """Database configuration."""
    type: str = Field(default="sqlite", description="Database type")
    path: Optional[Path] = Field(default=None, description="Database file path (for SQLite)")
    check_same_thread: bool = Field(default=False, description="SQLite check_same_thread parameter")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Database timeout")
    foreign_keys: bool = Field(default=True, description="Enable foreign keys")
    
    @validator('path', pre=True)
    def set_db_path(cls, v, values):
        """Set default database path if not provided."""
        if v is None:
            return Path("ASTRA_assistant.db")
        return Path(v) if not isinstance(v, Path) else v


class PersonalityConfig(BaseModel):
    """Personality configuration."""
    default: str = Field(default="neutra", description="Default personality")
    available: List[str] = Field(
        default=["neutra", "amigável", "formal", "casual"],
        description="Available personalities"
    )
    
    @validator('default')
    def validate_default(cls, v, values):
        """Ensure default personality exists in available list."""
        available = values.get('available', [])
        if available and v not in available:
            raise ValueError(f"Default personality '{v}' not in available list")
        return v


class AstraConfig(BaseModel):
    """Main ASTRA configuration."""
    # Core settings
    version: str = Field(default="2.0.0", description="ASTRA version")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    
    # Component configurations
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    personality: PersonalityConfig = Field(default_factory=PersonalityConfig)
    
    # Paths
    data_dir: Path = Field(default=Path("data"), description="Data directory")
    logs_dir: Path = Field(default=Path("logs"), description="Logs directory")
    neural_dir: Path = Field(default=Path("neural_models"), description="Neural models directory")
    
    # Features toggles
    enable_voice: bool = Field(default=True, description="Enable voice features")
    enable_companion: bool = Field(default=True, description="Enable companion engine")
    enable_memory: bool = Field(default=True, description="Enable memory system")
    enable_personality: bool = Field(default=True, description="Enable personality system")
    enable_opinion: bool = Field(default=True, description="Enable opinion system")
    enable_api_hub: bool = Field(default=True, description="Enable API integration hub")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "allow"  # Allow extra fields for flexibility
    
    @validator('data_dir', 'logs_dir', 'neural_dir')
    def ensure_directory_exists(cls, v: Path) -> Path:
        """Create directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convert to legacy CONFIG format for compatibility."""
        return {
            "ollama_model": self.ollama.model,
            "ollama_url": self.ollama.url,
            "conversation_history_size": self.conversation.history_size,
            "max_retries": self.ollama.max_retries,
            "request_timeout": self.ollama.timeout,
            "tts_model": self.tts.model,
            "temp_audio_file": self.tts.temp_audio_dir / "resposta_temp.wav",
            "lembretes_file": self.data_dir / "lembretes.txt",
            "history_file": self.data_dir / "conversation_history.json",
            "facts_file": self.data_dir / "personal_facts.json",
            "log_file": self.logs_dir / "ASTRA_assistant.log",
            "model_file": self.neural_dir / "modelo.pkl",
            "intents_file": self.neural_dir / "dados" / "intents.json",
        }


def load_config_from_yaml(config_path: Optional[Path] = None) -> AstraConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Validated AstraConfig instance
    """
    import yaml
    from pathlib import Path
    
    if config_path is None:
        config_path = Path(__file__).parent / "astra_config.yaml"
    
    if not config_path.exists():
        # Return default configuration
        return AstraConfig()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return AstraConfig(**config_data)
    except Exception as e:
        import logging
        logging.error(f"Failed to load config from {config_path}: {e}")
        logging.warning("Using default configuration")
        return AstraConfig()


def save_config_to_yaml(config: AstraConfig, config_path: Optional[Path] = None):
    """
    Save configuration to YAML file.
    
    Args:
        config: AstraConfig instance
        config_path: Path to save configuration (optional)
    """
    import yaml
    from pathlib import Path
    
    if config_path is None:
        config_path = Path(__file__).parent / "astra_config.yaml"
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config.dict(exclude_none=True),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
    except Exception as e:
        import logging
        logging.error(f"Failed to save config to {config_path}: {e}")


# Global configuration instance
_config_instance: Optional[AstraConfig] = None


def get_config() -> AstraConfig:
    """
    Get global configuration instance (singleton pattern).
    
    Returns:
        AstraConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config_from_yaml()
    return _config_instance


def reload_config(config_path: Optional[Path] = None):
    """
    Reload configuration from file.
    
    Args:
        config_path: Path to configuration file (optional)
    """
    global _config_instance
    _config_instance = load_config_from_yaml(config_path)


if __name__ == "__main__":
    # Test configuration
    config = AstraConfig()
    print("✅ Default configuration loaded successfully")
    print(f"📊 Config: {config.dict()}")
    
    # Test validation
    try:
        invalid_config = AstraConfig(conversation={"history_size": 200})
        print("⚠️ Large history size warning should appear")
    except Exception as e:
        print(f"❌ Validation error: {e}")

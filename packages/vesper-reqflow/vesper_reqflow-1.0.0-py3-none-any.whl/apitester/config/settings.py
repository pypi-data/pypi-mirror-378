"""Configuration management for Agentic API Tester."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import json
import yaml


@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    username: Optional[str] = None
    password: Optional[str] = None
    database: int = 0
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class CacheConfig:
    """Response caching configuration."""
    enabled: bool = True
    default_ttl: int = 300  # 5 minutes
    max_size: int = 1000  # Maximum number of cached responses


@dataclass
class HistoryConfig:
    """Request history configuration."""
    enabled: bool = True
    max_entries: int = 100
    auto_cleanup: bool = True


@dataclass
class OutputConfig:
    """Output formatting configuration."""
    color_enabled: bool = True
    pretty_print: bool = True
    table_max_width: int = 120
    json_indent: int = 2
    show_headers: bool = True
    show_timing: bool = True


@dataclass
class AIConfig:
    """AI assistant configuration."""
    enabled: bool = False
    provider: str = "openai"  # openai, anthropic
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.1


@dataclass
class AppConfig:
    """Main application configuration."""
    redis: RedisConfig = field(default_factory=RedisConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    
    # Global settings
    verbose: bool = False
    debug: bool = False
    config_file: Optional[str] = None
    current_environment: str = "default"
    default_headers: Dict[str, str] = field(default_factory=dict)
    
    # HTTP client settings
    timeout: float = 30.0
    max_redirects: int = 10
    verify_ssl: bool = True


class ConfigManager:
    """Manages application configuration from multiple sources."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.config = AppConfig()
        self._load_configuration()
    
    def _get_default_config_file(self) -> str:
        """Get the default configuration file path."""
        home_dir = Path.home()
        config_dir = home_dir / ".config" / "apitester"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _load_configuration(self) -> None:
        """Load configuration from environment variables and config file."""
        # Load environment variables from .env file
        load_dotenv()
        
        # Load from config file if it exists
        if os.path.exists(self.config_file):
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self) -> None:
        """Load configuration from YAML or JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if data:
                self._update_config_from_dict(data)
        except Exception as e:
            # If config file is corrupted, use defaults and log warning
            print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Redis configuration
        if os.getenv("REDIS_HOST"):
            self.config.redis.host = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            self.config.redis.port = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_USERNAME"):
            self.config.redis.username = os.getenv("REDIS_USERNAME")
        if os.getenv("REDIS_PASSWORD"):
            self.config.redis.password = os.getenv("REDIS_PASSWORD")
        if os.getenv("REDIS_DB"):
            self.config.redis.database = int(os.getenv("REDIS_DB"))
        if os.getenv("REDIS_DATABASE"):
            self.config.redis.database = int(os.getenv("REDIS_DATABASE"))
        
        # AI configuration
        if os.getenv("AI_ENABLED"):
            self.config.ai.enabled = os.getenv("AI_ENABLED").lower() == "true"
        if os.getenv("AI_PROVIDER"):
            self.config.ai.provider = os.getenv("AI_PROVIDER")
        if os.getenv("AI_API_KEY"):
            self.config.ai.api_key = os.getenv("AI_API_KEY")
        if os.getenv("OPENAI_API_KEY"):
            self.config.ai.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY") and self.config.ai.provider == "anthropic":
            self.config.ai.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Cache configuration
        if os.getenv("CACHE_ENABLED"):
            self.config.cache.enabled = os.getenv("CACHE_ENABLED").lower() == "true"
        if os.getenv("CACHE_TTL"):
            self.config.cache.default_ttl = int(os.getenv("CACHE_TTL"))
        
        # History configuration
        if os.getenv("HISTORY_MAX_ENTRIES"):
            self.config.history.max_entries = int(os.getenv("HISTORY_MAX_ENTRIES"))
        
        # Output configuration
        if os.getenv("COLOR_ENABLED"):
            self.config.output.color_enabled = os.getenv("COLOR_ENABLED").lower() == "true"
        
        # Global settings
        if os.getenv("VERBOSE"):
            self.config.verbose = os.getenv("VERBOSE").lower() == "true"
        if os.getenv("DEBUG"):
            self.config.debug = os.getenv("DEBUG").lower() == "true"
    
    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary data."""
        if "redis" in data:
            redis_data = data["redis"]
            if "host" in redis_data:
                self.config.redis.host = redis_data["host"]
            if "port" in redis_data:
                self.config.redis.port = redis_data["port"]
            if "password" in redis_data:
                self.config.redis.password = redis_data["password"]
            if "database" in redis_data:
                self.config.redis.database = redis_data["database"]
        
        if "cache" in data:
            cache_data = data["cache"]
            if "enabled" in cache_data:
                self.config.cache.enabled = cache_data["enabled"]
            if "default_ttl" in cache_data:
                self.config.cache.default_ttl = cache_data["default_ttl"]
            if "max_size" in cache_data:
                self.config.cache.max_size = cache_data["max_size"]
        
        if "history" in data:
            history_data = data["history"]
            if "enabled" in history_data:
                self.config.history.enabled = history_data["enabled"]
            if "max_entries" in history_data:
                self.config.history.max_entries = history_data["max_entries"]
        
        if "output" in data:
            output_data = data["output"]
            if "color_enabled" in output_data:
                self.config.output.color_enabled = output_data["color_enabled"]
            if "pretty_print" in output_data:
                self.config.output.pretty_print = output_data["pretty_print"]
            if "json_indent" in output_data:
                self.config.output.json_indent = output_data["json_indent"]
        
        if "ai" in data:
            ai_data = data["ai"]
            if "enabled" in ai_data:
                self.config.ai.enabled = ai_data["enabled"]
            if "provider" in ai_data:
                self.config.ai.provider = ai_data["provider"]
            if "model" in ai_data:
                self.config.ai.model = ai_data["model"]
        
        if "default_headers" in data:
            self.config.default_headers = data["default_headers"]
        
        if "current_environment" in data:
            self.config.current_environment = data["current_environment"]
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_data = {
            "redis": {
                "host": self.config.redis.host,
                "port": self.config.redis.port,
                "database": self.config.redis.database,
            },
            "cache": {
                "enabled": self.config.cache.enabled,
                "default_ttl": self.config.cache.default_ttl,
                "max_size": self.config.cache.max_size,
            },
            "history": {
                "enabled": self.config.history.enabled,
                "max_entries": self.config.history.max_entries,
            },
            "output": {
                "color_enabled": self.config.output.color_enabled,
                "pretty_print": self.config.output.pretty_print,
                "json_indent": self.config.output.json_indent,
                "show_headers": self.config.output.show_headers,
                "show_timing": self.config.output.show_timing,
            },
            "ai": {
                "enabled": self.config.ai.enabled,
                "provider": self.config.ai.provider,
                "model": self.config.ai.model,
            },
            "default_headers": self.config.default_headers,
            "current_environment": self.config.current_environment,
        }
        
        # Don't save sensitive information like passwords and API keys
        if self.config.redis.password:
            config_data["redis"]["password"] = "***"
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None or config_file:
        _config_manager = ConfigManager(config_file)
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().get_config()
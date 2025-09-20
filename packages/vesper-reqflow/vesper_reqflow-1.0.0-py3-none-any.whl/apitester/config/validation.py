"""Configuration validation and migration utilities."""

import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import yaml
import json
from dataclasses import asdict

from .settings import AppConfig, RedisConfig, CacheConfig, HistoryConfig, OutputConfig, AIConfig


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigMigrationError(Exception):
    """Raised when configuration migration fails."""
    pass


class ConfigValidator:
    """Validates configuration settings."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_config(self, config: AppConfig) -> Tuple[bool, List[str], List[str]]:
        """Validate complete configuration."""
        self.errors = []
        self.warnings = []
        
        self._validate_redis_config(config.redis)
        self._validate_cache_config(config.cache)
        self._validate_history_config(config.history)
        self._validate_output_config(config.output)
        self._validate_ai_config(config.ai)
        self._validate_global_settings(config)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_redis_config(self, redis: RedisConfig) -> None:
        """Validate Redis configuration."""
        if not redis.host:
            self.errors.append("Redis host cannot be empty")
        
        if not isinstance(redis.port, int) or redis.port < 1 or redis.port > 65535:
            self.errors.append("Redis port must be between 1 and 65535")
        
        if not isinstance(redis.database, int) or redis.database < 0 or redis.database > 15:
            self.errors.append("Redis database must be between 0 and 15")
        
        if redis.socket_timeout <= 0:
            self.errors.append("Redis socket timeout must be positive")
        
        if redis.socket_connect_timeout <= 0:
            self.errors.append("Redis socket connect timeout must be positive")
        
        if redis.health_check_interval <= 0:
            self.errors.append("Redis health check interval must be positive")
    
    def _validate_cache_config(self, cache: CacheConfig) -> None:
        """Validate cache configuration."""
        if cache.default_ttl <= 0:
            self.errors.append("Cache default TTL must be positive")
        
        if cache.max_size <= 0:
            self.errors.append("Cache max size must be positive")
        
        if cache.default_ttl > 86400:  # 24 hours
            self.warnings.append("Cache TTL is very long (>24 hours)")
        
        if cache.max_size > 100000:
            self.warnings.append("Cache max size is very large (>100,000 entries)")
    
    def _validate_history_config(self, history: HistoryConfig) -> None:
        """Validate history configuration."""
        if history.max_entries <= 0:
            self.errors.append("History max entries must be positive")
        
        if history.max_entries > 1000000:
            self.warnings.append("History max entries is very large (>1,000,000)")
    
    def _validate_output_config(self, output: OutputConfig) -> None:
        """Validate output configuration."""
        if output.table_max_width <= 0:
            self.errors.append("Table max width must be positive")
        
        if output.json_indent < 0:
            self.errors.append("JSON indent cannot be negative")
        
        if output.table_max_width < 40:
            self.warnings.append("Table max width is very small (<40 characters)")
        
        if output.json_indent > 8:
            self.warnings.append("JSON indent is very large (>8 spaces)")
    
    def _validate_ai_config(self, ai: AIConfig) -> None:
        """Validate AI configuration."""
        if ai.enabled:
            if not ai.provider:
                self.errors.append("AI provider must be specified when AI is enabled")
            elif ai.provider not in ["openai", "anthropic", "gemini"]:
                self.errors.append("AI provider must be one of: openai, anthropic, gemini")
            
            if not ai.api_key:
                self.warnings.append("AI is enabled but no API key is configured")
            
            if not ai.model:
                self.errors.append("AI model must be specified when AI is enabled")
        
        if ai.max_tokens <= 0:
            self.errors.append("AI max tokens must be positive")
        
        if ai.temperature < 0 or ai.temperature > 2:
            self.errors.append("AI temperature must be between 0 and 2")
        
        if ai.max_tokens > 4000:
            self.warnings.append("AI max tokens is very large (>4000)")
    
    def _validate_global_settings(self, config: AppConfig) -> None:
        """Validate global settings."""
        if config.timeout <= 0:
            self.errors.append("Timeout must be positive")
        
        if config.max_redirects < 0:
            self.errors.append("Max redirects cannot be negative")
        
        if not config.current_environment:
            self.errors.append("Current environment cannot be empty")
        
        if config.timeout > 300:  # 5 minutes
            self.warnings.append("Timeout is very long (>5 minutes)")
        
        if config.max_redirects > 20:
            self.warnings.append("Max redirects is very high (>20)")


class ConfigMigrator:
    """Handles configuration migration between versions."""
    
    CURRENT_VERSION = "1.0"
    
    def __init__(self):
        self.migrations = {
            "0.1": self._migrate_from_0_1,
            "0.2": self._migrate_from_0_2,
            "0.9": self._migrate_from_0_9,
        }
    
    def migrate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to current version."""
        version = config_data.get("version", "0.1")
        
        if version == self.CURRENT_VERSION:
            return config_data
        
        # Apply migrations in order
        for migration_version in sorted(self.migrations.keys()):
            if self._version_less_than(version, migration_version):
                config_data = self.migrations[migration_version](config_data)
                config_data["version"] = migration_version
        
        # Set to current version
        config_data["version"] = self.CURRENT_VERSION
        return config_data
    
    def _version_less_than(self, version1: str, version2: str) -> bool:
        """Compare version strings."""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad with zeros if needed
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        return v1_parts < v2_parts
    
    def _migrate_from_0_1(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.1."""
        # Add new cache configuration
        if "cache" not in config_data:
            config_data["cache"] = {
                "enabled": True,
                "default_ttl": 300,
                "max_size": 1000
            }
        
        # Rename old settings
        if "redis_host" in config_data:
            if "redis" not in config_data:
                config_data["redis"] = {}
            config_data["redis"]["host"] = config_data.pop("redis_host")
        
        if "redis_port" in config_data:
            if "redis" not in config_data:
                config_data["redis"] = {}
            config_data["redis"]["port"] = config_data.pop("redis_port")
        
        return config_data
    
    def _migrate_from_0_2(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.2."""
        # Add AI configuration
        if "ai" not in config_data:
            config_data["ai"] = {
                "enabled": False,
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
        
        # Update output configuration
        if "output" in config_data:
            output = config_data["output"]
            if "show_headers" not in output:
                output["show_headers"] = True
            if "show_timing" not in output:
                output["show_timing"] = True
        
        return config_data
    
    def _migrate_from_0_9(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.9."""
        # Add Gemini support to AI configuration
        if "ai" in config_data:
            ai_config = config_data["ai"]
            if ai_config.get("provider") == "google":
                ai_config["provider"] = "gemini"
        
        # Add new security settings
        if "security" not in config_data:
            config_data["security"] = {
                "mask_sensitive_headers": True,
                "mask_sensitive_params": True
            }
        
        return config_data


class ConfigManager:
    """Enhanced configuration manager with validation and migration."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.validator = ConfigValidator()
        self.migrator = ConfigMigrator()
        self.config_file = config_file or self._get_default_config_file()
        self.config_data: Dict[str, Any] = {}
        self._load_configuration()
    
    def _get_default_config_file(self) -> str:
        """Get the default configuration file path."""
        home_dir = Path.home()
        config_dir = home_dir / ".config" / "apitester"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _load_configuration(self) -> None:
        """Load and validate configuration."""
        # Load default configuration
        self._load_defaults()
        
        # Load from config file if it exists
        if os.path.exists(self.config_file):
            self._load_from_file()
        
        # Migrate configuration if needed
        self.config_data = self.migrator.migrate_config(self.config_data)
        
        # Validate configuration
        config = self._dict_to_config(self.config_data)
        is_valid, errors, warnings = self.validator.validate_config(config)
        
        if not is_valid:
            raise ConfigValidationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        if warnings:
            for warning in warnings:
                print(f"Configuration warning: {warning}")
    
    def _load_defaults(self) -> None:
        """Load default configuration."""
        defaults_file = Path(__file__).parent / "defaults.yaml"
        try:
            with open(defaults_file, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load default configuration: {e}")
            self.config_data = {}
    
    def _load_from_file(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith(('.yaml', '.yml')):
                    file_data = yaml.safe_load(f) or {}
                else:
                    file_data = json.load(f)
            
            # Merge with defaults (file data takes precedence)
            self._deep_merge(self.config_data, file_data)
            
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig object."""
        # Extract nested configurations
        redis_data = data.get("redis", {})
        cache_data = data.get("cache", {})
        history_data = data.get("history", {})
        output_data = data.get("output", {})
        ai_data = data.get("ai", {})
        app_data = data.get("app", {})
        
        return AppConfig(
            redis=RedisConfig(
                host=redis_data.get("host", "localhost"),
                port=redis_data.get("port", 6379),
                password=redis_data.get("password"),
                database=redis_data.get("database", 0),
                socket_timeout=redis_data.get("socket_timeout", 5.0),
                socket_connect_timeout=redis_data.get("socket_connect_timeout", 5.0),
                retry_on_timeout=redis_data.get("retry_on_timeout", True),
                health_check_interval=redis_data.get("health_check_interval", 30)
            ),
            cache=CacheConfig(
                enabled=cache_data.get("enabled", True),
                default_ttl=cache_data.get("default_ttl", 300),
                max_size=cache_data.get("max_size", 1000)
            ),
            history=HistoryConfig(
                enabled=history_data.get("enabled", True),
                max_entries=history_data.get("max_entries", 10000),
                auto_cleanup=history_data.get("auto_cleanup", True)
            ),
            output=OutputConfig(
                color_enabled=output_data.get("color_enabled", True),
                pretty_print=output_data.get("pretty_print", True),
                table_max_width=output_data.get("table_max_width", 120),
                json_indent=output_data.get("json_indent", 2),
                show_headers=output_data.get("show_headers", True),
                show_timing=output_data.get("show_timing", True)
            ),
            ai=AIConfig(
                enabled=ai_data.get("enabled", False),
                provider=ai_data.get("provider", "openai"),
                api_key=ai_data.get("api_key"),
                model=ai_data.get("model", "gpt-3.5-turbo"),
                max_tokens=ai_data.get("max_tokens", 1000),
                temperature=ai_data.get("temperature", 0.1)
            ),
            verbose=app_data.get("verbose", False),
            debug=app_data.get("debug", False),
            current_environment=data.get("current_environment", "default"),
            default_headers=data.get("default_headers", {}),
            timeout=app_data.get("timeout", 30.0),
            max_redirects=app_data.get("max_redirects", 10),
            verify_ssl=app_data.get("verify_ssl", True)
        )
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self._dict_to_config(self.config_data)
    
    def save_config(self, config: AppConfig) -> None:
        """Save configuration to file."""
        # Convert config to dictionary
        config_dict = asdict(config)
        
        # Remove sensitive information
        if config_dict.get("redis", {}).get("password"):
            config_dict["redis"]["password"] = None
        if config_dict.get("ai", {}).get("api_key"):
            config_dict["ai"]["api_key"] = None
        
        # Add version
        config_dict["version"] = self.migrator.CURRENT_VERSION
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigValidationError(f"Could not save configuration: {e}")
    
    def validate_current_config(self) -> Tuple[bool, List[str], List[str]]:
        """Validate the current configuration."""
        config = self.get_config()
        return self.validator.validate_config(config)
    
    def create_sample_config(self, output_file: str) -> None:
        """Create a sample configuration file."""
        defaults_file = Path(__file__).parent / "defaults.yaml"
        try:
            with open(defaults_file, 'r') as src:
                content = src.read()
            
            with open(output_file, 'w') as dst:
                dst.write("# Sample configuration for Agentic API Tester CLI\n")
                dst.write("# Copy this file to ~/.config/apitester/config.yaml and customize\n\n")
                dst.write(content)
                
        except Exception as e:
            raise ConfigValidationError(f"Could not create sample configuration: {e}")


def validate_config_file(config_file: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a configuration file."""
    try:
        manager = ConfigManager(config_file)
        return manager.validate_current_config()
    except Exception as e:
        return False, [str(e)], []


def migrate_config_file(config_file: str, backup: bool = True) -> None:
    """Migrate a configuration file to the current version."""
    if backup:
        backup_file = f"{config_file}.backup"
        import shutil
        shutil.copy2(config_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    try:
        manager = ConfigManager(config_file)
        config = manager.get_config()
        manager.save_config(config)
        print(f"Successfully migrated configuration: {config_file}")
    except Exception as e:
        raise ConfigMigrationError(f"Migration failed: {e}")


def create_default_config(output_file: str) -> None:
    """Create a default configuration file."""
    manager = ConfigManager()
    manager.create_sample_config(output_file)
    print(f"Created default configuration: {output_file}")
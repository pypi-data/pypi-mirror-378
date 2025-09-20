"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path

from apitester.config.settings import ConfigManager, AppConfig


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def test_default_config_creation(self):
        """Test that default configuration is created properly."""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        assert isinstance(config, AppConfig)
        assert config.redis.host == "localhost"
        assert config.redis.port == 6379
        assert config.cache.enabled is True
        assert config.history.enabled is True
    
    def test_config_from_env_variables(self, monkeypatch):
        """Test configuration loading from environment variables."""
        # Set environment variables
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("REDIS_PORT", "6380")
        monkeypatch.setenv("CACHE_ENABLED", "false")
        monkeypatch.setenv("AI_ENABLED", "true")
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        assert config.redis.host == "redis.example.com"
        assert config.redis.port == 6380
        assert config.cache.enabled is False
        assert config.ai.enabled is True
    
    def test_config_file_loading(self):
        """Test configuration loading from YAML file."""
        config_data = """
redis:
  host: test.redis.com
  port: 6380
  database: 1

cache:
  enabled: false
  default_ttl: 600

ai:
  enabled: true
  provider: anthropic
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            config_file = f.name
        
        try:
            config_manager = ConfigManager(config_file)
            config = config_manager.get_config()
            
            assert config.redis.host == "test.redis.com"
            assert config.redis.port == 6380
            assert config.redis.database == 1
            assert config.cache.enabled is False
            assert config.cache.default_ttl == 600
            assert config.ai.enabled is True
            assert config.ai.provider == "anthropic"
        finally:
            os.unlink(config_file)
    
    def test_config_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            # Create config manager and modify config
            config_manager = ConfigManager(config_file)
            config = config_manager.get_config()
            config.redis.host = "modified.redis.com"
            config.cache.default_ttl = 900
            
            # Save configuration
            config_manager.save_config()
            
            # Load configuration in new manager
            new_config_manager = ConfigManager(config_file)
            new_config = new_config_manager.get_config()
            
            assert new_config.redis.host == "modified.redis.com"
            assert new_config.cache.default_ttl == 900
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)
    
    def test_invalid_config_file_handling(self):
        """Test handling of invalid configuration files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            # Should not raise exception, should use defaults
            config_manager = ConfigManager(config_file)
            config = config_manager.get_config()
            
            # Should have default values
            assert config.redis.host == "localhost"
            assert config.redis.port == 6379
        finally:
            os.unlink(config_file)
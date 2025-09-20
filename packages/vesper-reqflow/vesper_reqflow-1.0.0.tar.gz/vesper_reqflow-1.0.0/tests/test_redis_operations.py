"""Tests for Redis operations."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from apitester.storage.models import RequestTemplate, RequestRecord, Environment, HTTPMethod
from apitester.storage.operations import (
    TemplateOperations, EnvironmentOperations, HistoryOperations, CacheOperations
)
from apitester.storage.redis_client import RedisClient


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_client = Mock(spec=RedisClient)
    mock_client.is_connected.return_value = True
    mock_client.health_check.return_value = True
    return mock_client


@pytest.fixture
def sample_template():
    """Sample request template for testing."""
    return RequestTemplate(
        name="test-template",
        method=HTTPMethod.POST,
        url="https://api.example.com/users",
        headers={"Content-Type": "application/json"},
        body='{"name": "test"}',
        description="Test template"
    )


@pytest.fixture
def sample_record():
    """Sample request record for testing."""
    return RequestRecord(
        timestamp=datetime.now(),
        method=HTTPMethod.GET,
        url="https://api.example.com/users",
        response_status=200,
        response_time=0.5
    )


@pytest.fixture
def sample_environment():
    """Sample environment for testing."""
    return Environment(
        name="test-env",
        variables={"API_KEY": "test-key", "BASE_URL": "https://api.test.com"}
    )


class TestTemplateOperations:
    """Test template operations."""
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_save_template(self, mock_get_client, mock_redis, sample_template):
        """Test saving a template."""
        mock_get_client.return_value = mock_redis
        mock_redis.set_hash.return_value = True
        
        ops = TemplateOperations()
        result = ops.save_template(sample_template)
        
        assert result is True
        mock_redis.set_hash.assert_called_once()
        
        # Check the key format
        call_args = mock_redis.set_hash.call_args
        key = call_args[0][0]
        assert key == "template:test-template"
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_load_template(self, mock_get_client, mock_redis, sample_template):
        """Test loading a template."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = sample_template.to_dict()
        
        ops = TemplateOperations()
        result = ops.load_template("test-template")
        
        assert result is not None
        assert result.name == "test-template"
        assert result.method == HTTPMethod.POST
        assert result.url == "https://api.example.com/users"
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_load_nonexistent_template(self, mock_get_client, mock_redis):
        """Test loading a non-existent template."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = {}
        
        ops = TemplateOperations()
        result = ops.load_template("nonexistent")
        
        assert result is None
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_list_templates(self, mock_get_client, mock_redis):
        """Test listing templates."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_keys_pattern.return_value = [
            "template:template1",
            "template:template2",
            "template:template3"
        ]
        
        ops = TemplateOperations()
        result = ops.list_templates()
        
        assert len(result) == 3
        assert "template1" in result
        assert "template2" in result
        assert "template3" in result
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_delete_template(self, mock_get_client, mock_redis):
        """Test deleting a template."""
        mock_get_client.return_value = mock_redis
        mock_redis.delete_key.return_value = True
        
        ops = TemplateOperations()
        result = ops.delete_template("test-template")
        
        assert result is True
        mock_redis.delete_key.assert_called_once_with("template:test-template")


class TestEnvironmentOperations:
    """Test environment operations."""
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_save_environment(self, mock_get_client, mock_redis, sample_environment):
        """Test saving an environment."""
        mock_get_client.return_value = mock_redis
        mock_redis.set_hash.return_value = True
        
        ops = EnvironmentOperations()
        result = ops.save_environment(sample_environment)
        
        assert result is True
        mock_redis.set_hash.assert_called_once()
        
        # Check the key format
        call_args = mock_redis.set_hash.call_args
        key = call_args[0][0]
        assert key == "env:test-env"
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_set_variable(self, mock_get_client, mock_redis):
        """Test setting an environment variable."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = {}  # Environment doesn't exist
        mock_redis.set_hash.return_value = True
        
        ops = EnvironmentOperations()
        result = ops.set_variable("test-env", "NEW_VAR", "new-value")
        
        assert result is True
        mock_redis.set_hash.assert_called_once()
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_get_variable(self, mock_get_client, mock_redis, sample_environment):
        """Test getting an environment variable."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = sample_environment.to_dict()
        
        ops = EnvironmentOperations()
        result = ops.get_variable("test-env", "API_KEY")
        
        assert result == "test-key"
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_get_nonexistent_variable(self, mock_get_client, mock_redis):
        """Test getting a non-existent variable."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = {}
        
        ops = EnvironmentOperations()
        result = ops.get_variable("nonexistent-env", "NONEXISTENT_VAR")
        
        assert result is None
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_set_current_environment(self, mock_get_client, mock_redis):
        """Test setting current environment."""
        mock_get_client.return_value = mock_redis
        mock_redis.get_hash.return_value = {}
        mock_redis.set_hash.return_value = True
        
        ops = EnvironmentOperations()
        result = ops.set_current_environment("production")
        
        assert result is True
        mock_redis.set_hash.assert_called_once()


class TestHistoryOperations:
    """Test history operations."""
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_add_request(self, mock_get_config, mock_get_client, mock_redis, sample_record):
        """Test adding a request to history."""
        # Mock config
        mock_config = Mock()
        mock_config.history.max_entries = 100
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        mock_redis.push_to_list.return_value = True
        
        ops = HistoryOperations()
        result = ops.add_request(sample_record)
        
        assert result is True
        mock_redis.push_to_list.assert_called_once()
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_get_history(self, mock_get_config, mock_get_client, mock_redis, sample_record):
        """Test getting request history."""
        # Mock config
        mock_config = Mock()
        mock_config.history.max_entries = 100
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        mock_redis.get_list.return_value = [sample_record.to_dict()]
        
        ops = HistoryOperations()
        result = ops.get_history()
        
        assert len(result) == 1
        assert result[0].method == HTTPMethod.GET
        assert result[0].url == "https://api.example.com/users"
    
    @patch('apitester.storage.operations.get_redis_client')
    def test_clear_history(self, mock_get_client, mock_redis):
        """Test clearing history."""
        mock_get_client.return_value = mock_redis
        mock_redis.delete_key.return_value = True
        
        ops = HistoryOperations()
        result = ops.clear_history()
        
        assert result is True
        mock_redis.delete_key.assert_called_once_with("history")


class TestCacheOperations:
    """Test cache operations."""
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_generate_cache_key(self, mock_get_config, mock_get_client, mock_redis):
        """Test cache key generation."""
        mock_config = Mock()
        mock_config.cache.enabled = True
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        
        ops = CacheOperations()
        key = ops.generate_cache_key("GET", "https://api.example.com/users", {})
        
        assert key.startswith("cache:get:")
        assert len(key) > 20  # Should have hash suffix
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_cache_response(self, mock_get_config, mock_get_client, mock_redis):
        """Test caching a response."""
        mock_config = Mock()
        mock_config.cache.enabled = True
        mock_config.cache.default_ttl = 300
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        mock_redis.set_with_ttl.return_value = True
        
        ops = CacheOperations()
        result = ops.cache_response(
            "GET", "https://api.example.com/users", {},
            200, {}, '{"users": []}'
        )
        
        assert result is True
        mock_redis.set_with_ttl.assert_called_once()
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_get_cached_response(self, mock_get_config, mock_get_client, mock_redis):
        """Test getting cached response."""
        mock_config = Mock()
        mock_config.cache.enabled = True
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        
        # Mock cached entry
        from apitester.storage.models import CacheEntry
        entry = CacheEntry(
            key="test-key",
            response_status=200,
            response_headers={},
            response_body='{"users": []}',
            created_at=datetime.now(),
            ttl=300
        )
        
        mock_redis.get_with_ttl.return_value = (entry.to_dict(), 250)
        mock_redis.set_with_ttl.return_value = True
        
        ops = CacheOperations()
        result = ops.get_cached_response("GET", "https://api.example.com/users", {})
        
        assert result is not None
        status, headers, body, hit_count = result
        assert status == 200
        assert body == '{"users": []}'
    
    @patch('apitester.storage.operations.get_redis_client')
    @patch('apitester.storage.operations.get_config')
    def test_cache_disabled(self, mock_get_config, mock_get_client, mock_redis):
        """Test cache operations when caching is disabled."""
        mock_config = Mock()
        mock_config.cache.enabled = False
        mock_get_config.return_value = mock_config
        
        mock_get_client.return_value = mock_redis
        
        ops = CacheOperations()
        
        # Cache response should return False when disabled
        result = ops.cache_response(
            "GET", "https://api.example.com/users", {},
            200, {}, '{"users": []}'
        )
        assert result is False
        
        # Get cached response should return None when disabled
        result = ops.get_cached_response("GET", "https://api.example.com/users", {})
        assert result is None
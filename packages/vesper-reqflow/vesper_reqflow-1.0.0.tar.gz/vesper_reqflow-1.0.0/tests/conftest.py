"""Pytest configuration and fixtures for API Tester tests."""

import pytest
from unittest.mock import Mock, patch
import tempfile
import os
import json
from pathlib import Path
import fakeredis

# Import test utilities
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provide a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def fake_redis():
    """Provide a fake Redis instance for testing."""
    return fakeredis.FakeRedis()


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    config = Mock()
    
    # Redis configuration
    config.redis.host = "localhost"
    config.redis.port = 6379
    config.redis.database = 0
    config.redis.password = None
    
    # Cache configuration
    config.cache.enabled = True
    config.cache.default_ttl = 3600
    config.cache.max_entries = 10000
    
    # History configuration
    config.history.enabled = True
    config.history.max_entries = 50000
    config.history.auto_cleanup = True
    
    # AI configuration
    config.ai.enabled = False
    config.ai.provider = "openai"
    config.ai.model = "gpt-3.5-turbo"
    config.ai.api_key = None
    
    # Output configuration
    config.output.color_enabled = True
    config.output.pretty_print = True
    config.output.json_indent = 2
    
    # Global settings
    config.timeout = 30
    config.current_environment = "default"
    config.verbose = False
    config.debug = False
    
    return config


@pytest.fixture
def mock_http_response():
    """Provide a mock HTTP response for testing."""
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"test": true}'
    response.url = "https://api.example.com/test"
    response.elapsed.total_seconds.return_value = 0.5
    response.is_success.return_value = True
    return response


@pytest.fixture
def mock_template():
    """Provide a mock template for testing."""
    template = Mock()
    template.name = "test-template"
    template.method.value = "GET"
    template.url = "https://api.example.com/users"
    template.headers = {"Accept": "application/json"}
    template.body = None
    template.params = {}
    template.description = "Test template"
    template.tags = ["test"]
    template.created_at = Mock()
    template.created_at.strftime.return_value = "2024-01-01 12:00:00"
    template.updated_at = Mock()
    template.updated_at.strftime.return_value = "2024-01-01 12:00:00"
    template.validate.return_value = []
    return template


@pytest.fixture
def temp_config_file():
    """Provide a temporary configuration file for testing."""
    config_content = {
        "redis": {
            "host": "localhost",
            "port": 6379,
            "database": 0
        },
        "cache": {
            "enabled": True,
            "default_ttl": 3600
        },
        "history": {
            "enabled": True,
            "max_entries": 10000
        },
        "ai": {
            "enabled": False,
            "provider": "openai"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_content, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def temp_template_file():
    """Provide a temporary template file for testing."""
    template_data = {
        "templates": [
            {
                "name": "test-template-1",
                "method": "GET",
                "url": "https://api.example.com/users",
                "headers": {"Accept": "application/json"},
                "description": "Get users"
            },
            {
                "name": "test-template-2",
                "method": "POST",
                "url": "https://api.example.com/users",
                "headers": {"Content-Type": "application/json"},
                "body": '{"name": "test"}',
                "description": "Create user"
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def temp_environment_file():
    """Provide a temporary environment file for testing."""
    env_data = {
        "API_BASE": "https://api.example.com",
        "API_KEY": "test123",
        "VERSION": "v1"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(env_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def mock_redis_client(fake_redis):
    """Provide a mock Redis client that uses fake Redis."""
    with patch('src.apitester.storage.redis_client.redis.Redis') as mock_redis:
        mock_redis.return_value = fake_redis
        yield fake_redis


@pytest.fixture
def mock_ai_assistant():
    """Provide a mock AI assistant for testing."""
    assistant = Mock()
    assistant.is_available.return_value = True
    assistant.provider_name = "openai"
    
    # Mock AI responses
    from src.apitester.ai.assistant import AIResponse
    
    assistant.suggest_headers.return_value = AIResponse(
        content='[{"header": "Authorization", "value": "Bearer token"}]',
        confidence=0.8,
        metadata={"provider": "openai"}
    )
    
    assistant.explain_status_code.return_value = AIResponse(
        content="This status code indicates success",
        confidence=0.9,
        metadata={"provider": "openai"}
    )
    
    assistant.validate_json_structure.return_value = AIResponse(
        content="The JSON structure is valid",
        confidence=0.85,
        metadata={"provider": "openai"}
    )
    
    return assistant


@pytest.fixture(autouse=True)
def mock_redis_for_all_tests(fake_redis):
    """Automatically mock Redis for all tests."""
    with patch('src.apitester.storage.redis_client.redis.Redis') as mock_redis:
        mock_redis.return_value = fake_redis
        yield fake_redis


@pytest.fixture(autouse=True)
def mock_config_for_all_tests(mock_config):
    """Automatically mock configuration for all tests."""
    with patch('src.apitester.config.settings.get_config') as mock_get_config:
        mock_get_config.return_value = mock_config
        yield mock_config


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "cli: mark test as a CLI test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as requiring AI functionality"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_cli" in item.nodeid:
            item.add_marker(pytest.mark.cli)
        elif "test_ai" in item.nodeid:
            item.add_marker(pytest.mark.ai)
        elif "test_redis" in item.nodeid:
            item.add_marker(pytest.mark.redis)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "performance" in item.nodeid or "large" in item.nodeid:
            item.add_marker(pytest.mark.slow)


# Custom assertions
class APITesterAssertions:
    """Custom assertions for API Tester tests."""
    
    @staticmethod
    def assert_valid_json(text):
        """Assert that text is valid JSON."""
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")
    
    @staticmethod
    def assert_valid_url(url):
        """Assert that URL is valid."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        assert parsed.scheme in ['http', 'https'], f"Invalid URL scheme: {url}"
        assert parsed.netloc, f"Invalid URL netloc: {url}"
    
    @staticmethod
    def assert_valid_http_method(method):
        """Assert that HTTP method is valid."""
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        assert method.upper() in valid_methods, f"Invalid HTTP method: {method}"
    
    @staticmethod
    def assert_redis_key_exists(redis_client, key):
        """Assert that Redis key exists."""
        assert redis_client.exists(key), f"Redis key does not exist: {key}"
    
    @staticmethod
    def assert_redis_key_not_exists(redis_client, key):
        """Assert that Redis key does not exist."""
        assert not redis_client.exists(key), f"Redis key should not exist: {key}"


@pytest.fixture
def assertions():
    """Provide custom assertions for tests."""
    return APITesterAssertions()


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_request_data(method="GET", url="https://api.example.com/test", **kwargs):
        """Create request data for testing."""
        data = {
            "method": method,
            "url": url,
            "headers": kwargs.get("headers", {}),
            "body": kwargs.get("body"),
            "params": kwargs.get("params", {})
        }
        return {k: v for k, v in data.items() if v is not None}
    
    @staticmethod
    def create_template_data(name="test-template", **kwargs):
        """Create template data for testing."""
        return {
            "name": name,
            "method": kwargs.get("method", "GET"),
            "url": kwargs.get("url", "https://api.example.com/test"),
            "headers": kwargs.get("headers", {}),
            "body": kwargs.get("body"),
            "params": kwargs.get("params", {}),
            "description": kwargs.get("description", "Test template"),
            "tags": kwargs.get("tags", [])
        }
    
    @staticmethod
    def create_environment_data(name="test-env", **kwargs):
        """Create environment data for testing."""
        return {
            "name": name,
            "description": kwargs.get("description", "Test environment"),
            "variables": kwargs.get("variables", {})
        }
    
    @staticmethod
    def create_history_entry(**kwargs):
        """Create history entry for testing."""
        return {
            "id": kwargs.get("id", "test-id"),
            "method": kwargs.get("method", "GET"),
            "url": kwargs.get("url", "https://api.example.com/test"),
            "status_code": kwargs.get("status_code", 200),
            "timestamp": kwargs.get("timestamp", "2024-01-01T12:00:00"),
            "response_time": kwargs.get("response_time", 0.5),
            "request_headers": kwargs.get("request_headers", {}),
            "response_headers": kwargs.get("response_headers", {}),
            "request_body": kwargs.get("request_body"),
            "response_body": kwargs.get("response_body", '{"test": true}')
        }


@pytest.fixture
def test_data():
    """Provide test data factory."""
    return TestDataFactory()


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Provide a performance timer for testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def assert_faster_than(self, seconds):
            assert self.elapsed < seconds, f"Operation took {self.elapsed}s, expected < {seconds}s"
    
    return Timer()


# Environment setup/teardown
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test environment variables
    os.environ["APITESTER_TEST_MODE"] = "true"
    os.environ["APITESTER_LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup
    os.environ.pop("APITESTER_TEST_MODE", None)
    os.environ.pop("APITESTER_LOG_LEVEL", None)


# Skip conditions
def skip_if_no_redis():
    """Skip test if Redis is not available."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return False
    except:
        return True


def skip_if_no_ai():
    """Skip test if AI libraries are not available."""
    try:
        import openai
        return False
    except ImportError:
        return True


# Pytest plugins
pytest_plugins = [
    "pytest_mock",  # For advanced mocking
    "pytest_cov",   # For coverage reporting
]
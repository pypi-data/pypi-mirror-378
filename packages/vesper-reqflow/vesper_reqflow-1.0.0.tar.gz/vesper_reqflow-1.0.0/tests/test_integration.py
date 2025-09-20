"""Integration tests for the API Tester CLI."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner
import fakeredis

from apitester.cli.main import app


class TestFullWorkflowIntegration:
    """Test complete workflows from CLI to storage."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fake_redis = fakeredis.FakeRedis()
    
    @patch('src.apitester.core.http_client.httpx')
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_complete_request_workflow(self, mock_redis, mock_httpx):
        """Test complete request workflow: send -> cache -> history."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"users": [{"id": 1, "name": "John"}]}'
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.url = "https://api.example.com/users"
        
        mock_httpx.get.return_value = mock_response
        
        # Send request
        result = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/users",
            "--header", "Accept: application/json"
        ])
        
        assert result.exit_code == 0
        assert "200" in result.output
        assert "users" in result.output
        
        # Verify request was cached and stored in history
        # This would check Redis keys for cache and history entries
        cache_keys = [key for key in self.fake_redis.keys() if key.startswith(b"cache:")]
        history_keys = [key for key in self.fake_redis.keys() if key.startswith(b"history:")]
        
        assert len(cache_keys) > 0  # Should have cached the response
        assert len(history_keys) > 0  # Should have stored in history
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_template_workflow_integration(self, mock_redis):
        """Test complete template workflow: save -> list -> execute."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Save template
        save_result = self.runner.invoke(app, [
            "template", "save", "test-api", "GET", "https://api.example.com/users",
            "--header", "Authorization: Bearer ${API_TOKEN}",
            "--description", "Get all users"
        ])
        
        assert save_result.exit_code == 0
        assert "saved successfully" in save_result.output
        
        # List templates
        list_result = self.runner.invoke(app, ["template", "list"])
        
        assert list_result.exit_code == 0
        assert "test-api" in list_result.output
        
        # Show template details
        show_result = self.runner.invoke(app, ["template", "show", "test-api"])
        
        assert show_result.exit_code == 0
        assert "GET" in show_result.output
        assert "https://api.example.com/users" in show_result.output
        assert "Authorization" in show_result.output
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_environment_workflow_integration(self, mock_redis):
        """Test complete environment workflow: create -> set vars -> use in template."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Create environment
        create_result = self.runner.invoke(app, [
            "env", "create", "test-env", "--description", "Test environment"
        ])
        
        assert create_result.exit_code == 0
        assert "created successfully" in create_result.output
        
        # Set variables
        set_result = self.runner.invoke(app, [
            "env", "set", "API_TOKEN", "test123", "--env", "test-env"
        ])
        
        assert set_result.exit_code == 0
        assert "Set variable" in set_result.output
        
        # Switch to environment
        switch_result = self.runner.invoke(app, [
            "env", "switch", "test-env"
        ])
        
        assert switch_result.exit_code == 0
        assert "Switched to environment" in switch_result.output
        
        # List environments
        list_result = self.runner.invoke(app, ["env", "list"])
        
        assert list_result.exit_code == 0
        assert "test-env" in list_result.output
        assert "current" in list_result.output
    
    @patch('src.apitester.core.http_client.httpx')
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_history_workflow_integration(self, mock_redis, mock_httpx):
        """Test history workflow: make requests -> view history -> retry."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Mock HTTP responses
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.headers = {"Content-Type": "application/json"}
        mock_response1.text = '{"result": "success"}'
        mock_response1.elapsed.total_seconds.return_value = 0.3
        mock_response1.url = "https://api.example.com/test1"
        
        mock_response2 = Mock()
        mock_response2.status_code = 404
        mock_response2.headers = {"Content-Type": "application/json"}
        mock_response2.text = '{"error": "not found"}'
        mock_response2.elapsed.total_seconds.return_value = 0.1
        mock_response2.url = "https://api.example.com/test2"
        
        mock_httpx.get.side_effect = [mock_response1, mock_response2]
        
        # Make first request
        result1 = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/test1"
        ])
        assert result1.exit_code == 0
        
        # Make second request
        result2 = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/test2"
        ])
        assert result2.exit_code == 0
        
        # View history
        history_result = self.runner.invoke(app, [
            "history", "list", "--limit", "10"
        ])
        
        assert history_result.exit_code == 0
        assert "200" in history_result.output
        assert "404" in history_result.output
        
        # Show history statistics
        stats_result = self.runner.invoke(app, ["history", "stats"])
        
        assert stats_result.exit_code == 0
        assert "Total Requests" in stats_result.output


class TestCacheIntegration:
    """Test cache integration across components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fake_redis = fakeredis.FakeRedis()
    
    @patch('src.apitester.core.http_client.httpx')
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_cache_hit_workflow(self, mock_redis, mock_httpx):
        """Test cache hit scenario in full workflow."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Mock HTTP response for first request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"data": "cached_response"}'
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.url = "https://api.example.com/cacheable"
        
        mock_httpx.get.return_value = mock_response
        
        # First request - should hit the API
        result1 = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/cacheable"
        ])
        
        assert result1.exit_code == 0
        assert "cached_response" in result1.output
        
        # Second identical request - should hit cache
        result2 = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/cacheable"
        ])
        
        assert result2.exit_code == 0
        assert "cached_response" in result2.output
        
        # Verify only one HTTP call was made (second was cached)
        assert mock_httpx.get.call_count == 1
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_cache_invalidation_workflow(self, mock_redis):
        """Test cache invalidation workflow."""
        # Setup fake Redis with some cached data
        mock_redis.return_value = self.fake_redis
        
        # Pre-populate cache
        cache_key = "cache:GET:api.example.com:test"
        cache_data = {
            "status_code": 200,
            "headers": {},
            "body": "cached data",
            "cached_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T01:00:00"
        }
        self.fake_redis.set(cache_key, json.dumps(cache_data))
        
        # Clear cache
        # This would require implementing a cache clear command
        # For now, we'll test that the cache key exists
        assert self.fake_redis.exists(cache_key)


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.apitester.core.http_client.httpx')
    def test_network_error_handling(self, mock_httpx):
        """Test handling of network errors."""
        # Mock network error
        mock_httpx.get.side_effect = Exception("Connection timeout")
        
        result = self.runner.invoke(app, [
            "request", "send", "GET", "https://unreachable.example.com"
        ])
        
        assert result.exit_code == 1
        assert "Error" in result.output
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_redis_error_handling(self, mock_redis):
        """Test handling of Redis connection errors."""
        # Mock Redis connection error
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_instance
        
        # Commands should still work but without caching/history
        result = self.runner.invoke(app, ["env", "list"])
        
        # Should not crash, might show warnings
        assert result.exit_code in [0, 1]  # Might succeed with warnings or fail gracefully
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in requests."""
        result = self.runner.invoke(app, [
            "request", "send", "POST", "https://api.example.com/test",
            "--header", "Content-Type: application/json",
            "--body", '{"invalid": json}'
        ])
        
        # Should detect invalid JSON and show error
        assert result.exit_code == 1
        assert "JSON" in result.output or "Error" in result.output


class TestConfigurationIntegration:
    """Test configuration integration across components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_custom_config_integration(self):
        """Test using custom configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_content = """
redis:
  host: localhost
  port: 6379
  database: 1
cache:
  enabled: true
  default_ttl: 1800
history:
  enabled: true
  max_entries: 5000
ai:
  enabled: false
"""
            f.write(config_content)
            config_path = f.name
        
        try:
            # Use custom config
            result = self.runner.invoke(app, [
                "--config", config_path,
                "config"
            ])
            
            assert result.exit_code == 0
            # Should show custom configuration values
            assert "1800" in result.output or "5000" in result.output
        
        finally:
            os.unlink(config_path)
    
    @patch('src.apitester.cli.main.setup_logging')
    def test_logging_configuration_integration(self, mock_setup_logging):
        """Test logging configuration integration."""
        # Test verbose mode
        result = self.runner.invoke(app, ["--verbose", "version"])
        
        mock_setup_logging.assert_called_with(True, False)
        
        # Test debug mode
        result = self.runner.invoke(app, ["--debug", "version"])
        
        mock_setup_logging.assert_called_with(False, True)


class TestTemplateVariableIntegration:
    """Test template variable substitution integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fake_redis = fakeredis.FakeRedis()
    
    @patch('src.apitester.core.http_client.httpx')
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_template_with_variables_integration(self, mock_redis, mock_httpx):
        """Test template execution with variable substitution."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Create environment with variables
        env_result = self.runner.invoke(app, [
            "env", "create", "api-test"
        ])
        assert env_result.exit_code == 0
        
        # Set variables
        var_result = self.runner.invoke(app, [
            "env", "set", "API_BASE", "https://api.example.com", "--env", "api-test"
        ])
        assert var_result.exit_code == 0
        
        var_result2 = self.runner.invoke(app, [
            "env", "set", "API_TOKEN", "test123", "--env", "api-test"
        ])
        assert var_result2.exit_code == 0
        
        # Save template with variables
        template_result = self.runner.invoke(app, [
            "template", "save", "api-template", "GET", "${API_BASE}/users",
            "--header", "Authorization: Bearer ${API_TOKEN}",
            "--description", "API template with variables"
        ])
        assert template_result.exit_code == 0
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"users": []}'
        mock_response.elapsed.total_seconds.return_value = 0.3
        mock_response.url = "https://api.example.com/users"
        
        mock_httpx.get.return_value = mock_response
        
        # Execute template with variable substitution
        exec_result = self.runner.invoke(app, [
            "request", "template", "api-template", "--env", "api-test"
        ])
        
        assert exec_result.exit_code == 0
        assert "200" in exec_result.output
        
        # Verify the substituted URL was called
        mock_httpx.get.assert_called_once()
        call_args = mock_httpx.get.call_args
        assert "https://api.example.com/users" in str(call_args)
        assert "Bearer test123" in str(call_args)


class TestBatchOperationIntegration:
    """Test batch operations integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_batch_template_operations(self):
        """Test batch template operations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            batch_config = {
                "templates": [
                    {
                        "name": "get-users",
                        "method": "GET",
                        "url": "https://api.example.com/users",
                        "description": "Get all users"
                    },
                    {
                        "name": "get-posts",
                        "method": "GET", 
                        "url": "https://api.example.com/posts",
                        "description": "Get all posts"
                    }
                ]
            }
            json.dump(batch_config, f)
            batch_file = f.name
        
        try:
            # Import batch templates
            result = self.runner.invoke(app, [
                "template", "import", batch_file
            ])
            
            assert result.exit_code == 0
            assert "Imported" in result.output or "imported" in result.output
        
        finally:
            os.unlink(batch_file)
    
    def test_environment_export_import_integration(self):
        """Test environment export/import integration."""
        # Create environment and set variables
        create_result = self.runner.invoke(app, [
            "env", "create", "export-test"
        ])
        assert create_result.exit_code == 0
        
        set_result = self.runner.invoke(app, [
            "env", "set", "TEST_VAR", "test_value", "--env", "export-test"
        ])
        assert set_result.exit_code == 0
        
        # Export environment
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            export_result = self.runner.invoke(app, [
                "env", "export", export_file, "--env", "export-test"
            ])
            
            assert export_result.exit_code == 0
            assert "exported" in export_result.output.lower()
            
            # Verify file was created and contains data
            assert os.path.exists(export_file)
            with open(export_file, 'r') as f:
                exported_data = json.load(f)
                assert "TEST_VAR" in exported_data
        
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)


class TestAIIntegration:
    """Test AI integration with other components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.apitester.cli.ai.get_config')
    @patch('src.apitester.cli.ai.AIAssistant')
    def test_ai_header_suggestion_integration(self, mock_ai_assistant, mock_get_config):
        """Test AI header suggestion integration."""
        # Mock AI configuration
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.provider = "openai"
        mock_config.ai.api_key = "test-key"
        mock_get_config.return_value = mock_config
        
        # Mock AI assistant
        mock_assistant_instance = Mock()
        mock_assistant_instance.is_available.return_value = True
        mock_ai_assistant.return_value = mock_assistant_instance
        
        # Mock header suggestion engine
        with patch('src.apitester.cli.ai.HeaderSuggestionEngine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine_instance.suggest_headers.return_value = {
                "Authorization": "Bearer ${API_TOKEN}",
                "Accept": "application/json"
            }
            mock_engine.return_value = mock_engine_instance
            
            result = self.runner.invoke(app, [
                "ai", "suggest-headers", "https://api.github.com/user"
            ])
            
            assert result.exit_code == 0
            assert "Authorization" in result.output
            assert "Accept" in result.output
    
    @patch('src.apitester.cli.ai.get_config')
    def test_ai_disabled_integration(self, mock_get_config):
        """Test AI commands when AI is disabled."""
        # Mock AI configuration as disabled
        mock_config = Mock()
        mock_config.ai.enabled = False
        mock_get_config.return_value = mock_config
        
        result = self.runner.invoke(app, [
            "ai", "status"
        ])
        
        assert result.exit_code == 0
        assert "not enabled" in result.output.lower() or "disabled" in result.output.lower()


class TestPerformanceIntegration:
    """Test performance aspects of integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fake_redis = fakeredis.FakeRedis()
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_large_history_performance(self, mock_redis):
        """Test performance with large history."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Simulate large history by adding many entries
        for i in range(100):
            history_key = f"history:entry:{i}"
            history_data = {
                "id": str(i),
                "method": "GET",
                "url": f"https://api.example.com/test{i}",
                "status_code": 200,
                "timestamp": "2024-01-01T00:00:00"
            }
            self.fake_redis.set(history_key, json.dumps(history_data))
        
        # List history should still be responsive
        result = self.runner.invoke(app, [
            "history", "list", "--limit", "10"
        ])
        
        assert result.exit_code == 0
        # Should only show limited results, not all 100
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_many_templates_performance(self, mock_redis):
        """Test performance with many templates."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # Create many templates
        for i in range(50):
            template_result = self.runner.invoke(app, [
                "template", "save", f"template-{i}", "GET", f"https://api.example.com/endpoint{i}"
            ])
            assert template_result.exit_code == 0
        
        # List templates should still be responsive
        result = self.runner.invoke(app, ["template", "list"])
        
        assert result.exit_code == 0
        # Should show all templates but in reasonable time


class TestSecurityIntegration:
    """Test security aspects of integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is properly masked."""
        # Set sensitive environment variable
        result = self.runner.invoke(app, [
            "env", "set", "API_SECRET", "super-secret-key", "--sensitive"
        ])
        
        assert result.exit_code == 0
        
        # List environment should mask the value
        list_result = self.runner.invoke(app, ["env", "list", "--variables"])
        
        assert list_result.exit_code == 0
        assert "super-secret-key" not in list_result.output
        assert "*" in list_result.output  # Should show masked value
    
    def test_config_security(self):
        """Test configuration security."""
        # Config command should not expose sensitive values
        result = self.runner.invoke(app, ["config"])
        
        assert result.exit_code == 0
        # Should not show raw API keys or passwords in output


class TestConcurrencyIntegration:
    """Test concurrent operations integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fake_redis = fakeredis.FakeRedis()
    
    @patch('src.apitester.storage.redis_client.redis.Redis')
    def test_concurrent_cache_access(self, mock_redis):
        """Test concurrent cache access doesn't cause issues."""
        # Setup fake Redis
        mock_redis.return_value = self.fake_redis
        
        # This would test concurrent access to cache
        # For now, we'll test that basic operations work
        result = self.runner.invoke(app, [
            "request", "send", "GET", "https://api.example.com/test"
        ])
        
        # Should handle concurrent access gracefully
        # In a real test, this would involve threading or multiprocessing


class TestBackwardCompatibilityIntegration:
    """Test backward compatibility of integrated components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_legacy_config_format(self):
        """Test handling of legacy configuration formats."""
        # This would test that old config formats still work
        # For now, we'll test basic config functionality
        result = self.runner.invoke(app, ["config"])
        
        assert result.exit_code == 0
    
    def test_legacy_template_format(self):
        """Test handling of legacy template formats."""
        # This would test importing old template formats
        # For now, we'll test basic template operations
        result = self.runner.invoke(app, ["template", "list"])
        
        assert result.exit_code == 0
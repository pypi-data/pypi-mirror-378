"""Tests for CLI commands."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
import json
from pathlib import Path

from apitester.cli.main import app
from apitester.cli.request import request_app
from apitester.cli.template import template_app
from apitester.cli.environment import env_app
from apitester.cli.history import history_app
from apitester.cli.ai import ai_app


class TestMainCLI:
    """Test cases for main CLI application."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_main_help(self):
        """Test main CLI help command."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Agentic API Tester CLI" in result.output
        assert "request" in result.output
        assert "template" in result.output
        assert "env" in result.output
        assert "history" in result.output
    
    @patch('src.apitester.cli.main.get_config')
    def test_version_command(self, mock_get_config):
        """Test version command."""
        with patch('src.apitester.__version__', "1.0.0"), \
             patch('src.apitester.__description__', "Test description"):
            
            result = self.runner.invoke(app, ["version"])
            
            assert result.exit_code == 0
            assert "1.0.0" in result.output
            assert "Agentic API Tester CLI" in result.output
    
    @patch('src.apitester.cli.main.get_config')
    def test_config_command(self, mock_get_config):
        """Test config command."""
        mock_config = Mock()
        mock_config.redis.host = "localhost"
        mock_config.redis.port = 6379
        mock_config.redis.database = 0
        mock_config.cache.enabled = True
        mock_config.cache.default_ttl = 3600
        mock_config.history.enabled = True
        mock_config.history.max_entries = 10000
        mock_config.ai.enabled = False
        mock_config.ai.provider = "openai"
        mock_config.ai.model = "gpt-3.5-turbo"
        mock_get_config.return_value = mock_config
        
        result = self.runner.invoke(app, ["config"])
        
        assert result.exit_code == 0
        assert "localhost" in result.output
        assert "6379" in result.output
    
    @patch('src.apitester.cli.main.get_redis_client')
    @patch('src.apitester.cli.main.EnvironmentManager')
    @patch('src.apitester.cli.main.TemplateManager')
    @patch('src.apitester.cli.main.HistoryManager')
    @patch('src.apitester.cli.main.CacheManager')
    def test_status_command(self, mock_cache, mock_history, mock_template, mock_env, mock_redis):
        """Test status command."""
        # Mock Redis client
        mock_redis_client = Mock()
        mock_redis_client.health_check.return_value = True
        mock_redis_client.config.host = "localhost"
        mock_redis_client.config.port = 6379
        mock_redis.return_value = mock_redis_client
        
        # Mock managers
        mock_env_instance = Mock()
        mock_env_instance.list_environments.return_value = ["default", "test"]
        mock_env_instance.get_current_environment.return_value = "default"
        mock_env.return_value = mock_env_instance
        
        mock_template_instance = Mock()
        mock_template_instance.list_templates.return_value = ["template1", "template2"]
        mock_template.return_value = mock_template_instance
        
        mock_history_instance = Mock()
        mock_history_instance.get_history_count.return_value = 100
        mock_history.return_value = mock_history_instance
        
        mock_cache_instance = Mock()
        mock_cache_instance.get_cache_statistics.return_value = {
            "enabled": True,
            "total_entries": 50
        }
        mock_cache.return_value = mock_cache_instance
        
        result = self.runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "Connected" in result.output
        assert "Ready" in result.output


class TestRequestCLI:
    """Test cases for request CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_request_help(self):
        """Test request command help."""
        result = self.runner.invoke(request_app, ["--help"])
        
        assert result.exit_code == 0
        assert "Execute HTTP and GraphQL requests" in result.output
        assert "send" in result.output
        assert "graphql" in result.output
    
    @patch('src.apitester.cli.request.HTTPClient')
    @patch('src.apitester.cli.request.HistoryManager')
    @patch('src.apitester.cli.request.CacheManager')
    @patch('src.apitester.cli.request.ResponseFormatter')
    def test_send_request_get(self, mock_formatter, mock_cache, mock_history, mock_http):
        """Test sending GET request."""
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": true}'
        mock_response.is_success.return_value = True
        
        mock_http_instance = Mock()
        mock_http_instance.send_request.return_value = mock_response
        mock_http.return_value = mock_http_instance
        
        # Mock other components
        mock_cache.return_value.get_cached_response.return_value = None
        mock_history.return_value = Mock()
        mock_formatter.return_value = Mock()
        
        result = self.runner.invoke(request_app, [
            "send", "GET", "https://api.example.com/test"
        ])
        
        assert result.exit_code == 0
        mock_http_instance.send_request.assert_called_once()
    
    @patch('src.apitester.cli.request.HTTPClient')
    @patch('src.apitester.cli.request.HistoryManager')
    @patch('src.apitester.cli.request.CacheManager')
    @patch('src.apitester.cli.request.ResponseFormatter')
    def test_send_request_post_with_body(self, mock_formatter, mock_cache, mock_history, mock_http):
        """Test sending POST request with body."""
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"id": 123}'
        mock_response.is_success.return_value = True
        
        mock_http_instance = Mock()
        mock_http_instance.send_request.return_value = mock_response
        mock_http.return_value = mock_http_instance
        
        # Mock other components
        mock_cache.return_value.get_cached_response.return_value = None
        mock_history.return_value = Mock()
        mock_formatter.return_value = Mock()
        
        result = self.runner.invoke(request_app, [
            "send", "POST", "https://api.example.com/users",
            "--header", "Content-Type: application/json",
            "--body", '{"name": "test"}'
        ])
        
        assert result.exit_code == 0
        mock_http_instance.send_request.assert_called_once()
        
        # Verify request parameters
        call_args = mock_http_instance.send_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "https://api.example.com/users"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"
        assert call_args[1]["body"] == '{"name": "test"}'
    
    @patch('src.apitester.cli.request.GraphQLClient')
    @patch('src.apitester.cli.request.HTTPClient')
    @patch('src.apitester.cli.request.HistoryManager')
    @patch('src.apitester.cli.request.ResponseFormatter')
    def test_graphql_request(self, mock_formatter, mock_history, mock_http, mock_graphql):
        """Test GraphQL request."""
        # Mock GraphQL client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"data": {"user": {"id": "123"}}}'
        
        mock_graphql_instance = Mock()
        mock_graphql_instance.send_query.return_value = mock_response
        mock_graphql.return_value = mock_graphql_instance
        
        # Mock other components
        mock_http.return_value = Mock()
        mock_history.return_value = Mock()
        mock_formatter.return_value = Mock()
        
        result = self.runner.invoke(request_app, [
            "graphql", "https://api.github.com/graphql",
            "--query", "query { viewer { login } }",
            "--header", "Authorization: Bearer token"
        ])
        
        assert result.exit_code == 0
        mock_graphql_instance.send_query.assert_called_once()


class TestTemplateCLI:
    """Test cases for template CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_template_help(self):
        """Test template command help."""
        result = self.runner.invoke(template_app, ["--help"])
        
        assert result.exit_code == 0
        assert "Manage request templates" in result.output
        assert "save" in result.output
        assert "list" in result.output
    
    @patch('src.apitester.cli.template.TemplateManager')
    def test_save_template(self, mock_template_manager):
        """Test saving a template."""
        mock_template = Mock()
        mock_template.method.value = "GET"
        mock_template.url = "https://api.example.com/users"
        mock_template.description = "Test template"
        mock_template.tags = ["test"]
        
        mock_manager = Mock()
        mock_manager.save_template.return_value = mock_template
        mock_template_manager.return_value = mock_manager
        
        result = self.runner.invoke(template_app, [
            "save", "test-template", "GET", "https://api.example.com/users",
            "--description", "Test template",
            "--tag", "test"
        ])
        
        assert result.exit_code == 0
        assert "saved successfully" in result.output
        mock_manager.save_template.assert_called_once()
    
    @patch('src.apitester.cli.template.TemplateManager')
    def test_list_templates(self, mock_template_manager):
        """Test listing templates."""
        mock_manager = Mock()
        mock_manager.list_templates.return_value = ["template1", "template2", "template3"]
        mock_template_manager.return_value = mock_manager
        
        result = self.runner.invoke(template_app, ["list"])
        
        assert result.exit_code == 0
        assert "template1" in result.output
        assert "template2" in result.output
        assert "template3" in result.output
    
    @patch('src.apitester.cli.template.TemplateManager')
    def test_show_template(self, mock_template_manager):
        """Test showing template details."""
        mock_template = Mock()
        mock_template.method.value = "GET"
        mock_template.url = "https://api.example.com/users"
        mock_template.description = "Test template"
        mock_template.headers = {"Accept": "application/json"}
        mock_template.body = None
        mock_template.params = {}
        mock_template.tags = ["test"]
        mock_template.created_at = Mock()
        mock_template.created_at.strftime.return_value = "2024-01-01 12:00:00"
        mock_template.updated_at = Mock()
        mock_template.updated_at.strftime.return_value = "2024-01-01 12:00:00"
        
        mock_manager = Mock()
        mock_manager.load_template.return_value = mock_template
        mock_template_manager.return_value = mock_manager
        
        result = self.runner.invoke(template_app, ["show", "test-template"])
        
        assert result.exit_code == 0
        assert "GET" in result.output
        assert "https://api.example.com/users" in result.output
        assert "Test template" in result.output
    
    @patch('src.apitester.cli.template.TemplateManager')
    def test_delete_template(self, mock_template_manager):
        """Test deleting a template."""
        mock_manager = Mock()
        mock_manager.template_exists.return_value = True
        mock_manager.delete_template.return_value = True
        mock_template_manager.return_value = mock_manager
        
        result = self.runner.invoke(template_app, [
            "delete", "test-template", "--force"
        ])
        
        assert result.exit_code == 0
        assert "deleted successfully" in result.output
        mock_manager.delete_template.assert_called_once_with("test-template")


class TestEnvironmentCLI:
    """Test cases for environment CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_env_help(self):
        """Test environment command help."""
        result = self.runner.invoke(env_app, ["--help"])
        
        assert result.exit_code == 0
        assert "Manage environment variables" in result.output
        assert "list" in result.output
        assert "set" in result.output
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_list_environments(self, mock_env_manager):
        """Test listing environments."""
        mock_manager = Mock()
        mock_manager.list_environments.return_value = ["default", "development", "production"]
        mock_manager.get_current_environment.return_value = "default"
        mock_manager.get_environment_variables.return_value = {"API_KEY": "test123"}
        mock_env_manager.return_value = mock_manager
        
        result = self.runner.invoke(env_app, ["list"])
        
        assert result.exit_code == 0
        assert "default" in result.output
        assert "development" in result.output
        assert "production" in result.output
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_create_environment(self, mock_env_manager):
        """Test creating an environment."""
        mock_manager = Mock()
        mock_manager.environment_exists.return_value = False
        mock_manager.create_environment.return_value = True
        mock_env_manager.return_value = mock_manager
        
        result = self.runner.invoke(env_app, [
            "create", "test-env", "--description", "Test environment"
        ])
        
        assert result.exit_code == 0
        assert "created successfully" in result.output
        mock_manager.create_environment.assert_called_once()
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_set_variable(self, mock_env_manager):
        """Test setting environment variable."""
        mock_manager = Mock()
        mock_manager.get_current_environment.return_value = "default"
        mock_manager.environment_exists.return_value = True
        mock_manager.set_variable.return_value = True
        mock_env_manager.return_value = mock_manager
        
        result = self.runner.invoke(env_app, [
            "set", "API_KEY", "test123"
        ])
        
        assert result.exit_code == 0
        assert "Set variable" in result.output
        mock_manager.set_variable.assert_called_once()
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_get_variable(self, mock_env_manager):
        """Test getting environment variable."""
        mock_manager = Mock()
        mock_manager.get_current_environment.return_value = "default"
        mock_manager.environment_exists.return_value = True
        mock_manager.get_variable.return_value = "test123"
        mock_env_manager.return_value = mock_manager
        
        result = self.runner.invoke(env_app, ["get", "API_KEY"])
        
        assert result.exit_code == 0
        assert "API_KEY" in result.output
        assert "test123" in result.output


class TestHistoryCLI:
    """Test cases for history CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_history_help(self):
        """Test history command help."""
        result = self.runner.invoke(history_app, ["--help"])
        
        assert result.exit_code == 0
        assert "View and manage request history" in result.output
        assert "list" in result.output
        assert "show" in result.output
    
    @patch('src.apitester.cli.history.HistoryManager')
    @patch('src.apitester.cli.history.HistoryQuery')
    def test_list_history(self, mock_query, mock_history_manager):
        """Test listing history."""
        mock_entries = [
            {
                "id": "1",
                "method": "GET",
                "url": "https://api.example.com/users",
                "response_status": 200,
                "timestamp": "2024-01-01T12:00:00",
                "response_time": 0.5
            },
            {
                "id": "2",
                "method": "POST",
                "url": "https://api.example.com/users",
                "response_status": 201,
                "timestamp": "2024-01-01T12:01:00",
                "response_time": 0.8
            }
        ]
        
        mock_manager = Mock()
        mock_manager.query_history.return_value = mock_entries
        mock_history_manager.return_value = mock_manager
        
        mock_query.return_value = Mock()
        
        result = self.runner.invoke(history_app, ["list", "--limit", "10"])
        
        assert result.exit_code == 0
        assert "GET" in result.output
        assert "POST" in result.output
        assert "200" in result.output
        assert "201" in result.output
    
    @patch('src.apitester.cli.history.HistoryManager')
    def test_show_history_entry(self, mock_history_manager):
        """Test showing history entry details."""
        mock_entry = {
            "id": "test-id",
            "method": "GET",
            "url": "https://api.example.com/users",
            "response_status": 200,
            "timestamp": "2024-01-01T12:00:00",
            "response_time": 0.5,
            "request_headers": {"Accept": "application/json"},
            "response_headers": {"Content-Type": "application/json"},
            "response_body": '{"users": []}'
        }
        
        mock_manager = Mock()
        mock_manager.get_history_entry.return_value = mock_entry
        mock_history_manager.return_value = mock_manager
        
        result = self.runner.invoke(history_app, ["show", "test-id"])
        
        assert result.exit_code == 0
        assert "GET" in result.output
        assert "https://api.example.com/users" in result.output
        assert "200" in result.output


class TestAICLI:
    """Test cases for AI CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_ai_help(self):
        """Test AI command help."""
        result = self.runner.invoke(ai_app, ["--help"])
        
        assert result.exit_code == 0
        assert "AI-powered assistance" in result.output
        assert "status" in result.output
        assert "suggest-headers" in result.output
    
    @patch('src.apitester.cli.ai.get_config')
    def test_ai_status(self, mock_get_config):
        """Test AI status command."""
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.provider = "openai"
        mock_config.ai.model = "gpt-3.5-turbo"
        mock_config.ai.api_key = "test-key"
        mock_get_config.return_value = mock_config
        
        result = self.runner.invoke(ai_app, ["status"])
        
        assert result.exit_code == 0
        assert "openai" in result.output
        assert "gpt-3.5-turbo" in result.output
    
    @patch('src.apitester.cli.ai.get_ai_assistant')
    @patch('src.apitester.cli.ai.HeaderSuggestionEngine')
    def test_suggest_headers(self, mock_header_engine, mock_get_assistant):
        """Test AI header suggestions."""
        mock_assistant = Mock()
        mock_get_assistant.return_value = mock_assistant
        
        mock_engine = Mock()
        mock_engine.suggest_headers.return_value = {
            "Authorization": "Bearer ${API_TOKEN}",
            "Accept": "application/json"
        }
        mock_header_engine.return_value = mock_engine
        
        result = self.runner.invoke(ai_app, [
            "suggest-headers", "https://api.github.com/user"
        ])
        
        assert result.exit_code == 0
        assert "Authorization" in result.output
        assert "Accept" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.apitester.cli.request.HTTPClient')
    @patch('src.apitester.cli.template.TemplateManager')
    def test_request_template_workflow(self, mock_template_manager, mock_http_client):
        """Test complete workflow: save template -> execute template."""
        # Mock template manager
        mock_template = Mock()
        mock_template.method.value = "GET"
        mock_template.url = "https://api.example.com/users"
        mock_template.description = "Get users"
        mock_template.tags = []
        
        mock_manager = Mock()
        mock_manager.save_template.return_value = mock_template
        mock_template_manager.return_value = mock_manager
        
        # Mock HTTP client for template execution
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '{"users": []}'
        mock_response.is_success.return_value = True
        
        mock_client = Mock()
        mock_client.send_request.return_value = mock_response
        mock_http_client.return_value = mock_client
        
        # Save template
        save_result = self.runner.invoke(template_app, [
            "save", "users-template", "GET", "https://api.example.com/users",
            "--description", "Get users"
        ])
        
        assert save_result.exit_code == 0
        assert "saved successfully" in save_result.output
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_environment_workflow(self, mock_env_manager):
        """Test complete environment workflow: create -> set vars -> switch."""
        mock_manager = Mock()
        mock_manager.environment_exists.return_value = False
        mock_manager.create_environment.return_value = True
        mock_manager.set_variable.return_value = True
        mock_manager.set_current_environment.return_value = True
        mock_manager.get_environment_variables.return_value = {"API_KEY": "test123"}
        mock_env_manager.return_value = mock_manager
        
        # Create environment
        create_result = self.runner.invoke(env_app, [
            "create", "test-env", "--description", "Test environment"
        ])
        assert create_result.exit_code == 0
        
        # Set variable
        set_result = self.runner.invoke(env_app, [
            "set", "API_KEY", "test123", "--env", "test-env"
        ])
        assert set_result.exit_code == 0
        
        # Switch environment
        switch_result = self.runner.invoke(env_app, ["switch", "test-env"])
        assert switch_result.exit_code == 0


class TestCLIErrorHandling:
    """Test error handling in CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        result = self.runner.invoke(app, ["invalid-command"])
        
        assert result.exit_code != 0
        # Should show help or error message
    
    @patch('src.apitester.cli.request.HTTPClient')
    def test_request_error_handling(self, mock_http_client):
        """Test error handling in request commands."""
        # Mock HTTP client to raise error
        mock_client = Mock()
        mock_client.send_request.side_effect = Exception("Connection error")
        mock_http_client.return_value = mock_client
        
        result = self.runner.invoke(request_app, [
            "send", "GET", "https://invalid-url.example.com"
        ])
        
        assert result.exit_code == 1
        assert "Error" in result.output
    
    @patch('src.apitester.cli.template.TemplateManager')
    def test_template_not_found_error(self, mock_template_manager):
        """Test template not found error handling."""
        from apitester.core.template_manager import TemplateNotFoundError
        
        mock_manager = Mock()
        mock_manager.load_template.side_effect = TemplateNotFoundError("Template not found")
        mock_template_manager.return_value = mock_manager
        
        result = self.runner.invoke(template_app, ["show", "nonexistent-template"])
        
        assert result.exit_code == 1
        assert "not found" in result.output
    
    @patch('src.apitester.cli.environment.EnvironmentManager')
    def test_environment_error_handling(self, mock_env_manager):
        """Test environment error handling."""
        from apitester.exceptions import EnvironmentError
        
        mock_manager = Mock()
        mock_manager.create_environment.side_effect = EnvironmentError("Environment exists")
        mock_env_manager.return_value = mock_manager
        
        result = self.runner.invoke(env_app, [
            "create", "existing-env"
        ])
        
        assert result.exit_code == 1
        assert "Error" in result.output


class TestCLIConfiguration:
    """Test CLI configuration handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.apitester.cli.main.get_config_manager')
    @patch('src.apitester.cli.main.get_config')
    def test_custom_config_file(self, mock_get_config, mock_get_config_manager):
        """Test using custom configuration file."""
        mock_config = Mock()
        mock_config.verbose = False
        mock_config.debug = False
        
        mock_manager = Mock()
        mock_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_manager
        mock_get_config.return_value = mock_config
        
        result = self.runner.invoke(app, [
            "--config", "/path/to/custom/config.yaml",
            "version"
        ])
        
        # Should not fail with custom config
        mock_get_config_manager.assert_called_with("/path/to/custom/config.yaml")
    
    @patch('src.apitester.cli.main.setup_logging')
    @patch('src.apitester.cli.main.get_config_manager')
    def test_verbose_mode(self, mock_get_config_manager, mock_setup_logging):
        """Test verbose mode."""
        mock_config = Mock()
        mock_config.verbose = True
        mock_config.debug = False
        
        mock_manager = Mock()
        mock_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_manager
        
        result = self.runner.invoke(app, ["--verbose", "version"])
        
        # Should call setup_logging with verbose=True
        mock_setup_logging.assert_called_with(True, False)
    
    @patch('src.apitester.cli.main.setup_logging')
    @patch('src.apitester.cli.main.get_config_manager')
    def test_debug_mode(self, mock_get_config_manager, mock_setup_logging):
        """Test debug mode."""
        mock_config = Mock()
        mock_config.verbose = False
        mock_config.debug = True
        
        mock_manager = Mock()
        mock_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_manager
        
        result = self.runner.invoke(app, ["--debug", "version"])
        
        # Should call setup_logging with debug=True
        mock_setup_logging.assert_called_with(False, True)
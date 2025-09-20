"""Tests for variable substitution engine."""

import pytest
from unittest.mock import Mock, patch

from apitester.core.variable_substitution import (
    VariableSubstitutionEngine,
    VariableSubstitutionError
)


class TestVariableSubstitutionEngine:
    """Test cases for VariableSubstitutionEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = VariableSubstitutionEngine()
    
    def test_simple_variable_substitution(self):
        """Test basic variable substitution."""
        template = "Hello ${NAME}!"
        variables = {"NAME": "World"}
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "Hello World!"
    
    def test_multiple_variable_substitution(self):
        """Test substitution with multiple variables."""
        template = "${METHOD} ${URL}/api/${VERSION}"
        variables = {
            "METHOD": "GET",
            "URL": "https://api.example.com",
            "VERSION": "v1"
        }
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "GET https://api.example.com/api/v1"
    
    def test_nested_variable_substitution(self):
        """Test nested variable references."""
        template = "${BASE_URL}/${API_${VERSION}}"
        variables = {
            "BASE_URL": "https://api.example.com",
            "VERSION": "1",
            "API_1": "v1/users"
        }
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "https://api.example.com/v1/users"
    
    def test_missing_variable_error(self):
        """Test error handling for missing variables."""
        template = "Hello ${MISSING_VAR}!"
        variables = {}
        
        with pytest.raises(VariableSubstitutionError) as exc_info:
            self.engine.substitute_variables(template, variables)
        
        assert "MISSING_VAR" in str(exc_info.value)
    
    def test_environment_variable_substitution(self):
        """Test substitution with environment variables."""
        with patch.dict('os.environ', {'TEST_VAR': 'test_value'}):
            template = "Value: ${TEST_VAR}"
            
            result = self.engine.substitute_variables(template, {}, use_env=True)
            assert result == "Value: test_value"
    
    def test_variable_precedence(self):
        """Test that provided variables take precedence over environment."""
        with patch.dict('os.environ', {'TEST_VAR': 'env_value'}):
            template = "Value: ${TEST_VAR}"
            variables = {"TEST_VAR": "provided_value"}
            
            result = self.engine.substitute_variables(template, variables, use_env=True)
            assert result == "Value: provided_value"
    
    def test_escape_sequences(self):
        """Test handling of escaped variable syntax."""
        template = "Literal: \\${NOT_A_VAR} and ${REAL_VAR}"
        variables = {"REAL_VAR": "substituted"}
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "Literal: ${NOT_A_VAR} and substituted"
    
    def test_empty_template(self):
        """Test handling of empty template."""
        result = self.engine.substitute_variables("", {})
        assert result == ""
    
    def test_no_variables_in_template(self):
        """Test template with no variables."""
        template = "No variables here"
        result = self.engine.substitute_variables(template, {"VAR": "value"})
        assert result == template
    
    def test_extract_variables(self):
        """Test extraction of variable names from template."""
        template = "${VAR1} and ${VAR2} and ${VAR1} again"
        
        variables = self.engine.extract_variables(template)
        assert variables == {"VAR1", "VAR2"}
    
    def test_extract_nested_variables(self):
        """Test extraction of nested variable references."""
        template = "${BASE}/${API_${VERSION}}"
        
        variables = self.engine.extract_variables(template)
        assert "BASE" in variables
        assert "VERSION" in variables
        # Note: API_${VERSION} would be extracted as a pattern
    
    def test_validate_variables(self):
        """Test variable validation."""
        template = "${VAR1} and ${VAR2}"
        available_vars = {"VAR1": "value1", "VAR2": "value2"}
        
        result = self.engine.validate_variables(template, available_vars)
        assert result["valid"] is True
        assert result["missing_variables"] == []
    
    def test_validate_missing_variables(self):
        """Test validation with missing variables."""
        template = "${VAR1} and ${VAR2} and ${VAR3}"
        available_vars = {"VAR1": "value1"}
        
        result = self.engine.validate_variables(template, available_vars)
        assert result["valid"] is False
        assert set(result["missing_variables"]) == {"VAR2", "VAR3"}
    
    def test_substitute_with_environment_manager(self):
        """Test substitution using environment manager."""
        mock_env_manager = Mock()
        mock_env_manager.get_environment_variables.return_value = {
            "API_KEY": "secret123",
            "BASE_URL": "https://api.test.com"
        }
        
        template = "${BASE_URL}/users?key=${API_KEY}"
        
        with patch('src.apitester.core.variable_substitution.EnvironmentManager', return_value=mock_env_manager):
            result = self.engine.substitute(template, "test_env")
        
        assert result == "https://api.test.com/users?key=secret123"
    
    def test_substitute_with_custom_variables(self):
        """Test substitution with custom variables override."""
        mock_env_manager = Mock()
        mock_env_manager.get_environment_variables.return_value = {
            "API_KEY": "env_key",
            "BASE_URL": "https://api.test.com"
        }
        
        template = "${BASE_URL}/users?key=${API_KEY}"
        custom_vars = {"API_KEY": "custom_key"}
        
        with patch('src.apitester.core.variable_substitution.EnvironmentManager', return_value=mock_env_manager):
            result = self.engine.substitute(template, "test_env", custom_vars)
        
        assert result == "https://api.test.com/users?key=custom_key"
    
    def test_complex_json_substitution(self):
        """Test substitution in complex JSON structures."""
        template = '''
        {
            "url": "${BASE_URL}/api/${VERSION}",
            "headers": {
                "Authorization": "Bearer ${TOKEN}",
                "Content-Type": "application/json"
            },
            "data": {
                "user_id": "${USER_ID}",
                "action": "test"
            }
        }
        '''
        
        variables = {
            "BASE_URL": "https://api.example.com",
            "VERSION": "v2",
            "TOKEN": "abc123",
            "USER_ID": "12345"
        }
        
        result = self.engine.substitute_variables(template, variables)
        
        # Verify key substitutions
        assert "https://api.example.com/api/v2" in result
        assert "Bearer abc123" in result
        assert '"user_id": "12345"' in result
    
    def test_url_encoding_substitution(self):
        """Test substitution with URL encoding."""
        template = "${BASE_URL}/search?q=${QUERY}"
        variables = {
            "BASE_URL": "https://api.example.com",
            "QUERY": "hello world"
        }
        
        result = self.engine.substitute_variables(template, variables, url_encode=True)
        assert result == "https://api.example.com/search?q=hello%20world"
    
    def test_case_sensitive_variables(self):
        """Test that variable names are case sensitive."""
        template = "${var} and ${VAR}"
        variables = {"var": "lowercase", "VAR": "uppercase"}
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "lowercase and uppercase"
    
    def test_special_characters_in_values(self):
        """Test substitution with special characters in values."""
        template = "Password: ${PASS}"
        variables = {"PASS": "p@$$w0rd!@#$%^&*()"}
        
        result = self.engine.substitute_variables(template, variables)
        assert result == "Password: p@$$w0rd!@#$%^&*()"
    
    def test_recursive_substitution_prevention(self):
        """Test prevention of infinite recursion in substitution."""
        template = "${VAR1}"
        variables = {"VAR1": "${VAR2}", "VAR2": "${VAR1}"}
        
        # Should not cause infinite recursion
        with pytest.raises(VariableSubstitutionError):
            self.engine.substitute_variables(template, variables, max_depth=10)


class TestVariableSubstitutionIntegration:
    """Integration tests for variable substitution with other components."""
    
    def test_integration_with_template_execution(self):
        """Test variable substitution in template execution context."""
        engine = VariableSubstitutionEngine()
        
        # Simulate template data
        template_data = {
            "url": "${API_BASE}/users/${USER_ID}",
            "headers": {
                "Authorization": "Bearer ${API_TOKEN}",
                "User-Agent": "${APP_NAME}/${VERSION}"
            },
            "body": '{"action": "${ACTION}", "timestamp": "${TIMESTAMP}"}'
        }
        
        variables = {
            "API_BASE": "https://api.example.com",
            "USER_ID": "123",
            "API_TOKEN": "token123",
            "APP_NAME": "APITester",
            "VERSION": "1.0",
            "ACTION": "update",
            "TIMESTAMP": "2024-01-01T00:00:00Z"
        }
        
        # Substitute in URL
        url = engine.substitute_variables(template_data["url"], variables)
        assert url == "https://api.example.com/users/123"
        
        # Substitute in headers
        auth_header = engine.substitute_variables(
            template_data["headers"]["Authorization"], variables
        )
        assert auth_header == "Bearer token123"
        
        user_agent = engine.substitute_variables(
            template_data["headers"]["User-Agent"], variables
        )
        assert user_agent == "APITester/1.0"
        
        # Substitute in body
        body = engine.substitute_variables(template_data["body"], variables)
        assert '"action": "update"' in body
        assert '"timestamp": "2024-01-01T00:00:00Z"' in body
    
    def test_error_handling_in_batch_substitution(self):
        """Test error handling when substituting multiple templates."""
        engine = VariableSubstitutionEngine()
        
        templates = [
            "${VALID_VAR}",
            "${MISSING_VAR}",
            "${ANOTHER_VALID_VAR}"
        ]
        
        variables = {
            "VALID_VAR": "valid",
            "ANOTHER_VALID_VAR": "also_valid"
        }
        
        results = []
        errors = []
        
        for template in templates:
            try:
                result = engine.substitute_variables(template, variables)
                results.append(result)
            except VariableSubstitutionError as e:
                errors.append(str(e))
        
        assert len(results) == 2
        assert len(errors) == 1
        assert "MISSING_VAR" in errors[0]
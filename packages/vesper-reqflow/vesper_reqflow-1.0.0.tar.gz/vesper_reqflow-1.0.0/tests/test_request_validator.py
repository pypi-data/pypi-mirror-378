"""Tests for request validator."""

import pytest
from unittest.mock import Mock, patch
import json

from apitester.core.request_validator import (
    RequestValidator,
    ValidationError
)


class TestRequestValidator:
    """Test cases for RequestValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RequestValidator()
    
    def test_validate_http_method_valid(self):
        """Test validation of valid HTTP methods."""
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        
        for method in valid_methods:
            result = self.validator.validate_http_method(method)
            assert result.is_valid
            assert result.errors == []
    
    def test_validate_http_method_invalid(self):
        """Test validation of invalid HTTP methods."""
        invalid_methods = ["INVALID", "get", "123", "", None]
        
        for method in invalid_methods:
            result = self.validator.validate_http_method(method)
            assert not result.is_valid
            assert len(result.errors) > 0
    
    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://api.example.com",
            "http://localhost:3000",
            "https://api.example.com/v1/users",
            "https://api.example.com/users?id=123",
            "https://subdomain.example.com:8080/path"
        ]
        
        for url in valid_urls:
            result = self.validator.validate_url(url)
            assert result.is_valid, f"URL {url} should be valid"
            assert result.errors == []
    
    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Unsupported scheme
            "",
            None,
            "http://",
            "https://"
        ]
        
        for url in invalid_urls:
            result = self.validator.validate_url(url)
            assert not result.is_valid, f"URL {url} should be invalid"
            assert len(result.errors) > 0
    
    def test_validate_headers_valid(self):
        """Test validation of valid headers."""
        valid_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123",
            "User-Agent": "APITester/1.0",
            "Accept": "application/json",
            "X-Custom-Header": "custom-value"
        }
        
        result = self.validator.validate_headers(valid_headers)
        assert result.is_valid
        assert result.errors == []
    
    def test_validate_headers_invalid(self):
        """Test validation of invalid headers."""
        # Headers with invalid characters
        invalid_headers = {
            "Content Type": "application/json",  # Space in header name
            "": "value",  # Empty header name
            "Valid-Header": "",  # Empty value (should be allowed)
            "Invalid\nHeader": "value"  # Newline in header name
        }
        
        result = self.validator.validate_headers(invalid_headers)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_json_body_valid(self):
        """Test validation of valid JSON bodies."""
        valid_json_bodies = [
            '{"name": "test"}',
            '{"users": [{"id": 1}, {"id": 2}]}',
            '[]',
            '{}',
            '"simple string"',
            '123',
            'true'
        ]
        
        for body in valid_json_bodies:
            result = self.validator.validate_json_body(body)
            assert result.is_valid, f"JSON body {body} should be valid"
            assert result.errors == []
    
    def test_validate_json_body_invalid(self):
        """Test validation of invalid JSON bodies."""
        invalid_json_bodies = [
            '{"name": "test"',  # Missing closing brace
            '{"name": test}',    # Unquoted value
            '{name: "test"}',    # Unquoted key
            '{"name": "test",}', # Trailing comma
            'undefined',         # Invalid literal
            ''                   # Empty string
        ]
        
        for body in invalid_json_bodies:
            result = self.validator.validate_json_body(body)
            assert not result.is_valid, f"JSON body {body} should be invalid"
            assert len(result.errors) > 0
    
    def test_validate_content_type_json_match(self):
        """Test validation of Content-Type matching JSON body."""
        headers = {"Content-Type": "application/json"}
        body = '{"test": true}'
        
        result = self.validator.validate_content_type_match(headers, body)
        assert result.is_valid
        assert result.errors == []
    
    def test_validate_content_type_json_mismatch(self):
        """Test validation of Content-Type not matching JSON body."""
        headers = {"Content-Type": "text/plain"}
        body = '{"test": true}'
        
        result = self.validator.validate_content_type_match(headers, body)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Content-Type" in result.errors[0]
    
    def test_validate_query_parameters_valid(self):
        """Test validation of valid query parameters."""
        valid_params = {
            "id": "123",
            "name": "test",
            "active": "true",
            "tags": "tag1,tag2",
            "empty": ""  # Empty values should be allowed
        }
        
        result = self.validator.validate_query_parameters(valid_params)
        assert result.is_valid
        assert result.errors == []
    
    def test_validate_query_parameters_invalid(self):
        """Test validation of invalid query parameters."""
        # Parameters with None values
        invalid_params = {
            "valid": "value",
            "invalid": None  # None values should be flagged
        }
        
        result = self.validator.validate_query_parameters(invalid_params)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_complete_request_valid(self):
        """Test validation of a complete valid request."""
        request_data = {
            "method": "POST",
            "url": "https://api.example.com/users",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer token123"
            },
            "body": '{"name": "John", "email": "john@example.com"}',
            "params": {
                "version": "v1"
            }
        }
        
        result = self.validator.validate_request(request_data)
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []
    
    def test_validate_complete_request_invalid(self):
        """Test validation of a complete invalid request."""
        request_data = {
            "method": "INVALID",
            "url": "not-a-url",
            "headers": {
                "Content Type": "application/json",  # Invalid header name
                "": "value"  # Empty header name
            },
            "body": '{"name": "test"',  # Invalid JSON
            "params": {
                "valid": "value",
                "invalid": None  # Invalid parameter value
            }
        }
        
        result = self.validator.validate_request(request_data)
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Should have errors for method, URL, headers, body, and params
        error_text = " ".join(result.errors)
        assert "method" in error_text.lower()
        assert "url" in error_text.lower()
        assert "header" in error_text.lower()
        assert "json" in error_text.lower()
    
    def test_validate_with_warnings(self):
        """Test validation that produces warnings."""
        request_data = {
            "method": "GET",
            "url": "http://api.example.com",  # HTTP instead of HTTPS
            "headers": {
                "Content-Type": "application/json"
            },
            "body": '{"data": "test"}',  # Body with GET request
            "params": {}
        }
        
        result = self.validator.validate_request(request_data)
        assert result.is_valid  # Should be valid but with warnings
        assert len(result.warnings) > 0
        
        warning_text = " ".join(result.warnings)
        assert "http" in warning_text.lower() or "body" in warning_text.lower()
    
    def test_validate_graphql_query_valid(self):
        """Test validation of valid GraphQL queries."""
        valid_queries = [
            "query { user { id name } }",
            "mutation { createUser(input: {name: \"test\"}) { id } }",
            "query GetUser($id: ID!) { user(id: $id) { name } }",
            "{ user { id } }"  # Shorthand query
        ]
        
        for query in valid_queries:
            result = self.validator.validate_graphql_query(query)
            assert result.is_valid, f"GraphQL query should be valid: {query}"
            assert result.errors == []
    
    def test_validate_graphql_query_invalid(self):
        """Test validation of invalid GraphQL queries."""
        invalid_queries = [
            "",  # Empty query
            "not a query",  # Invalid syntax
            "query {",  # Incomplete query
            "query { user { id name }",  # Missing closing brace
            None  # None value
        ]
        
        for query in invalid_queries:
            result = self.validator.validate_graphql_query(query)
            assert not result.is_valid, f"GraphQL query should be invalid: {query}"
            assert len(result.errors) > 0
    
    def test_validate_graphql_variables_valid(self):
        """Test validation of valid GraphQL variables."""
        valid_variables = [
            '{"id": "123"}',
            '{"input": {"name": "test", "active": true}}',
            '{}',
            None  # No variables is valid
        ]
        
        for variables in valid_variables:
            result = self.validator.validate_graphql_variables(variables)
            assert result.is_valid, f"GraphQL variables should be valid: {variables}"
            assert result.errors == []
    
    def test_validate_graphql_variables_invalid(self):
        """Test validation of invalid GraphQL variables."""
        invalid_variables = [
            '{"id": 123',  # Invalid JSON
            '{id: "123"}',  # Unquoted key
            'not json'      # Not JSON
        ]
        
        for variables in invalid_variables:
            result = self.validator.validate_graphql_variables(variables)
            assert not result.is_valid, f"GraphQL variables should be invalid: {variables}"
            assert len(result.errors) > 0
    
    def test_validate_template_structure(self):
        """Test validation of template structure."""
        valid_template = {
            "name": "test-template",
            "method": "GET",
            "url": "https://api.example.com/users",
            "headers": {"Accept": "application/json"},
            "description": "Test template"
        }
        
        result = self.validator.validate_template(valid_template)
        assert result.is_valid
        assert result.errors == []
    
    def test_validate_template_missing_required_fields(self):
        """Test validation of template with missing required fields."""
        invalid_template = {
            "description": "Missing required fields"
            # Missing name, method, url
        }
        
        result = self.validator.validate_template(invalid_template)
        assert not result.is_valid
        assert len(result.errors) > 0
        
        error_text = " ".join(result.errors)
        assert "name" in error_text.lower()
        assert "method" in error_text.lower()
        assert "url" in error_text.lower()
    
    def test_validate_batch_requests(self):
        """Test validation of batch request configuration."""
        batch_config = {
            "requests": [
                {
                    "name": "request1",
                    "method": "GET",
                    "url": "https://api.example.com/users"
                },
                {
                    "name": "request2",
                    "method": "POST",
                    "url": "https://api.example.com/users",
                    "body": '{"name": "test"}'
                }
            ]
        }
        
        result = self.validator.validate_batch_config(batch_config)
        assert result.is_valid
        assert result.errors == []
    
    def test_validate_batch_requests_invalid(self):
        """Test validation of invalid batch request configuration."""
        invalid_batch_config = {
            "requests": [
                {
                    "name": "request1",
                    "method": "INVALID",  # Invalid method
                    "url": "not-a-url"   # Invalid URL
                },
                {
                    # Missing name and method
                    "url": "https://api.example.com/users"
                }
            ]
        }
        
        result = self.validator.validate_batch_config(invalid_batch_config)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_security_validation(self):
        """Test security-related validation."""
        # Test for potential security issues
        request_data = {
            "method": "POST",
            "url": "https://api.example.com/users",
            "headers": {
                "Authorization": "Bearer token123"
            },
            "body": '{"script": "<script>alert(1)</script>"}'  # Potential XSS
        }
        
        result = self.validator.validate_request(request_data, security_check=True)
        
        # Should still be valid but may have security warnings
        if result.warnings:
            warning_text = " ".join(result.warnings)
            # Check if security warnings are present
            assert any(keyword in warning_text.lower() 
                      for keyword in ["script", "security", "xss"])
    
    def test_performance_validation(self):
        """Test performance-related validation."""
        # Large request body
        large_body = '{"data": "' + "x" * 10000 + '"}'
        
        request_data = {
            "method": "POST",
            "url": "https://api.example.com/upload",
            "body": large_body
        }
        
        result = self.validator.validate_request(request_data, performance_check=True)
        
        # Should be valid but may have performance warnings
        if result.warnings:
            warning_text = " ".join(result.warnings)
            assert any(keyword in warning_text.lower() 
                      for keyword in ["size", "large", "performance"])
    
    def test_custom_validation_rules(self):
        """Test custom validation rules."""
        def custom_rule(request_data):
            """Custom validation rule."""
            errors = []
            warnings = []
            
            if request_data.get("url", "").endswith("/admin"):
                warnings.append("Admin endpoint detected")
            
            return errors, warnings
        
        validator = RequestValidator()
        validator.add_custom_rule(custom_rule)
        
        request_data = {
            "method": "GET",
            "url": "https://api.example.com/admin"
        }
        
        result = validator.validate_request(request_data)
        assert result.is_valid
        assert len(result.warnings) > 0
        assert "admin" in result.warnings[0].lower()


class TestValidationResult:
    """Test cases for ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creation of ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            errors=["error1", "error2"],
            warnings=["warning1"]
        )
        
        assert result.is_valid is True
        assert result.errors == ["error1", "error2"]
        assert result.warnings == ["warning1"]
    
    def test_validation_result_string_representation(self):
        """Test string representation of ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            errors=["Invalid method"],
            warnings=["Use HTTPS"]
        )
        
        str_repr = str(result)
        assert "Invalid method" in str_repr
        assert "Use HTTPS" in str_repr
    
    def test_validation_result_merge(self):
        """Test merging of ValidationResult objects."""
        result1 = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["warning1"]
        )
        
        result2 = ValidationResult(
            is_valid=False,
            errors=["error1"],
            warnings=["warning2"]
        )
        
        merged = result1.merge(result2)
        
        assert merged.is_valid is False  # False if any result is invalid
        assert merged.errors == ["error1"]
        assert set(merged.warnings) == {"warning1", "warning2"}


class TestValidationIntegration:
    """Integration tests for request validation."""
    
    def test_integration_with_template_validation(self):
        """Test validation integration with template system."""
        validator = RequestValidator()
        
        # Simulate template with variables
        template_data = {
            "name": "api-test",
            "method": "POST",
            "url": "${BASE_URL}/api/users",
            "headers": {
                "Authorization": "Bearer ${API_TOKEN}",
                "Content-Type": "application/json"
            },
            "body": '{"name": "${USER_NAME}", "email": "${USER_EMAIL}"}'
        }
        
        # Validate template structure
        result = validator.validate_template(template_data)
        assert result.is_valid
        
        # Validate after variable substitution
        substituted_data = {
            "method": "POST",
            "url": "https://api.example.com/api/users",
            "headers": {
                "Authorization": "Bearer token123",
                "Content-Type": "application/json"
            },
            "body": '{"name": "John", "email": "john@example.com"}'
        }
        
        result = validator.validate_request(substituted_data)
        assert result.is_valid
    
    def test_validation_error_aggregation(self):
        """Test aggregation of multiple validation errors."""
        validator = RequestValidator()
        
        # Request with multiple issues
        request_data = {
            "method": "INVALID",      # Invalid method
            "url": "not-a-url",       # Invalid URL
            "headers": {
                "": "value",          # Invalid header
                "Content-Type": "application/json"
            },
            "body": '{"invalid": json}',  # Invalid JSON
            "params": {
                "valid": "value",
                "invalid": None       # Invalid parameter
            }
        }
        
        result = validator.validate_request(request_data)
        
        assert not result.is_valid
        assert len(result.errors) >= 4  # Should have multiple errors
        
        # Verify all error types are captured
        all_errors = " ".join(result.errors).lower()
        assert "method" in all_errors
        assert "url" in all_errors
        assert "header" in all_errors
        assert "json" in all_errors
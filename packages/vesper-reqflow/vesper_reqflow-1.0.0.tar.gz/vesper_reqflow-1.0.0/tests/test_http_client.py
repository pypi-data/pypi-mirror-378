"""Tests for HTTP client functionality."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from apitester.core.http_client import HTTPClient, HTTPResponse, HTTPClientError, RequestValidationError
from apitester.core.graphql_client import GraphQLClient, GraphQLResponse, GraphQLValidationError
from apitester.core.request_validator import RequestValidator, RequestPreprocessor, ValidationError
from apitester.storage.models import HTTPMethod, RequestRecord


class TestHTTPClient:
    """Test HTTP client functionality."""
    
    @pytest.fixture
    def mock_httpx_response(self):
        """Mock httpx response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.text = '{"message": "success"}'
        mock_response.content = b'{"message": "success"}'
        mock_response.url = 'https://api.example.com/test'
        mock_response.json.return_value = {"message": "success"}
        return mock_response
    
    @pytest.fixture
    def mock_httpx_client(self, mock_httpx_response):
        """Mock httpx client."""
        mock_client = Mock()
        mock_client.request.return_value = mock_httpx_response
        return mock_client
    
    def test_validate_request_valid(self):
        """Test request validation with valid parameters."""
        client = HTTPClient()
        
        # Should not raise exception
        client.validate_request(
            method='GET',
            url='https://api.example.com/test',
            headers={'Accept': 'application/json'},
            params={'limit': '10'}
        )
    
    def test_validate_request_invalid_method(self):
        """Test request validation with invalid method."""
        client = HTTPClient()
        
        with pytest.raises(RequestValidationError):
            client.validate_request(
                method='INVALID',
                url='https://api.example.com/test'
            )
    
    def test_validate_request_invalid_url(self):
        """Test request validation with invalid URL."""
        client = HTTPClient()
        
        with pytest.raises(RequestValidationError):
            client.validate_request(
                method='GET',
                url='not-a-url'
            )
    
    def test_validate_request_invalid_json_body(self):
        """Test request validation with invalid JSON body."""
        client = HTTPClient()
        
        with pytest.raises(RequestValidationError):
            client.validate_request(
                method='POST',
                url='https://api.example.com/test',
                headers={'Content-Type': 'application/json'},
                body='{"invalid": json}'
            )
    
    @patch('apitester.core.http_client.httpx.Client')
    def test_send_request_success(self, mock_client_class, mock_httpx_client, mock_httpx_response):
        """Test successful HTTP request."""
        mock_client_class.return_value = mock_httpx_client
        
        client = HTTPClient()
        response = client.send_request(
            method='GET',
            url='https://api.example.com/test'
        )
        
        assert isinstance(response, HTTPResponse)
        assert response.status_code == 200
        assert response.text == '{"message": "success"}'
        assert response.is_success()
    
    @patch('apitester.core.http_client.httpx.Client')
    def test_send_request_with_json_body(self, mock_client_class, mock_httpx_client):
        """Test HTTP request with JSON body."""
        mock_client_class.return_value = mock_httpx_client
        
        client = HTTPClient()
        client.send_request(
            method='POST',
            url='https://api.example.com/test',
            headers={'Content-Type': 'application/json'},
            body='{"name": "test"}'
        )
        
        # Verify the request was made with correct parameters
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args[1]
        
        assert call_args['method'] == 'POST'
        assert call_args['url'] == 'https://api.example.com/test'
        assert 'json' in call_args
        assert call_args['json'] == {"name": "test"}
    
    def test_create_request_record(self):
        """Test creating request record."""
        client = HTTPClient()
        
        # Mock response
        mock_response = Mock(spec=HTTPResponse)
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.text = '{"result": "ok"}'
        mock_response.request_time = 0.5
        
        record = client.create_request_record(
            method='GET',
            url='https://api.example.com/test',
            headers={'Accept': 'application/json'},
            response=mock_response,
            template_name='test-template'
        )
        
        assert isinstance(record, RequestRecord)
        assert record.method == HTTPMethod.GET
        assert record.url == 'https://api.example.com/test'
        assert record.response_status == 200
        assert record.response_time == 0.5
        assert record.template_name == 'test-template'


class TestGraphQLClient:
    """Test GraphQL client functionality."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client."""
        mock_client = Mock(spec=HTTPClient)
        return mock_client
    
    @pytest.fixture
    def mock_graphql_response(self):
        """Mock GraphQL HTTP response."""
        mock_response = Mock(spec=HTTPResponse)
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.request_time = 0.3
        mock_response.from_cache = False
        mock_response.is_success.return_value = True
        mock_response.json.return_value = {
            "data": {"user": {"id": "1", "name": "John"}},
            "errors": None
        }
        return mock_response
    
    def test_validate_query_valid(self):
        """Test GraphQL query validation with valid query."""
        client = GraphQLClient()
        
        # Should not raise exception
        client.validate_query('query { user { id name } }')
        client.validate_query('mutation CreateUser($name: String!) { createUser(name: $name) { id } }')
    
    def test_validate_query_invalid_empty(self):
        """Test GraphQL query validation with empty query."""
        client = GraphQLClient()
        
        with pytest.raises(GraphQLValidationError):
            client.validate_query('')
    
    def test_validate_query_invalid_syntax(self):
        """Test GraphQL query validation with invalid syntax."""
        client = GraphQLClient()
        
        with pytest.raises(GraphQLValidationError):
            client.validate_query('invalid query syntax')
    
    def test_validate_query_unmatched_braces(self):
        """Test GraphQL query validation with unmatched braces."""
        client = GraphQLClient()
        
        with pytest.raises(GraphQLValidationError):
            client.validate_query('query { user { id name }')  # Missing closing brace
    
    def test_validate_variables_valid(self):
        """Test GraphQL variables validation with valid variables."""
        client = GraphQLClient()
        
        # Should not raise exception
        client.validate_variables({'name': 'John', 'age': 30})
        client.validate_variables(None)
        client.validate_variables({})
    
    def test_validate_variables_invalid(self):
        """Test GraphQL variables validation with invalid variables."""
        client = GraphQLClient()
        
        with pytest.raises(GraphQLValidationError):
            client.validate_variables("not a dict")
    
    def test_extract_operation_name(self):
        """Test extracting operation name from GraphQL query."""
        client = GraphQLClient()
        
        # Named query
        name = client.extract_operation_name('query GetUser { user { id } }')
        assert name == 'GetUser'
        
        # Named mutation
        name = client.extract_operation_name('mutation CreateUser($name: String!) { createUser(name: $name) { id } }')
        assert name == 'CreateUser'
        
        # Anonymous query
        name = client.extract_operation_name('{ user { id } }')
        assert name is None
    
    def test_send_query_success(self, mock_http_client, mock_graphql_response):
        """Test successful GraphQL query."""
        mock_http_client.send_request.return_value = mock_graphql_response
        
        client = GraphQLClient(mock_http_client)
        response = client.send_query(
            url='https://api.example.com/graphql',
            query='query { user { id name } }'
        )
        
        assert isinstance(response, GraphQLResponse)
        assert response.is_success()
        assert response.data == {"user": {"id": "1", "name": "John"}}
        
        # Verify HTTP request was made correctly
        mock_http_client.send_request.assert_called_once()
        call_args = mock_http_client.send_request.call_args[1]
        
        assert call_args['method'] == 'POST'
        assert call_args['url'] == 'https://api.example.com/graphql'
        assert 'Content-Type' in call_args['headers']
        assert call_args['headers']['Content-Type'] == 'application/json'
        
        # Verify request body
        body_data = json.loads(call_args['body'])
        assert 'query' in body_data
        assert body_data['query'] == 'query { user { id name } }'
    
    def test_send_query_with_variables(self, mock_http_client, mock_graphql_response):
        """Test GraphQL query with variables."""
        mock_http_client.send_request.return_value = mock_graphql_response
        
        client = GraphQLClient(mock_http_client)
        client.send_query(
            url='https://api.example.com/graphql',
            query='query GetUser($id: ID!) { user(id: $id) { id name } }',
            variables={'id': '123'}
        )
        
        # Verify variables were included in request
        call_args = mock_http_client.send_request.call_args[1]
        body_data = json.loads(call_args['body'])
        
        assert 'variables' in body_data
        assert body_data['variables'] == {'id': '123'}


class TestRequestValidator:
    """Test request validator functionality."""
    
    def test_validate_method_valid(self):
        """Test HTTP method validation with valid methods."""
        validator = RequestValidator()
        
        assert validator.validate_method('GET') == HTTPMethod.GET
        assert validator.validate_method('post') == HTTPMethod.POST
        assert validator.validate_method('PUT') == HTTPMethod.PUT
    
    def test_validate_method_invalid(self):
        """Test HTTP method validation with invalid method."""
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_method('INVALID')
    
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        validator = RequestValidator()
        
        url = validator.validate_url('https://api.example.com/test')
        assert url == 'https://api.example.com/test'
        
        url = validator.validate_url('http://localhost:8080/api')
        assert url == 'http://localhost:8080/api'
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_url('not-a-url')
        
        with pytest.raises(ValidationError):
            validator.validate_url('ftp://example.com')  # Invalid scheme
        
        with pytest.raises(ValidationError):
            validator.validate_url('')  # Empty URL
    
    def test_validate_headers_valid(self):
        """Test header validation with valid headers."""
        validator = RequestValidator()
        
        headers = validator.validate_headers({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
            'Accept': 'application/json'
        })
        
        assert 'Content-Type' in headers
        assert headers['Content-Type'] == 'application/json'
    
    def test_validate_headers_invalid_content_length(self):
        """Test header validation with invalid Content-Length."""
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_headers({'Content-Length': 'invalid'})
        
        with pytest.raises(ValidationError):
            validator.validate_headers({'Content-Length': '-1'})
    
    def test_validate_json_body_valid(self):
        """Test JSON body validation with valid JSON."""
        validator = RequestValidator()
        
        body = validator._validate_json_body('{"name": "test", "value": 123}')
        assert '"name":"test"' in body  # Normalized JSON
    
    def test_validate_json_body_invalid(self):
        """Test JSON body validation with invalid JSON."""
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator._validate_json_body('{"invalid": json}')
    
    def test_validate_xml_body_valid(self):
        """Test XML body validation with valid XML."""
        validator = RequestValidator()
        
        xml_body = '<root><item>test</item></root>'
        result = validator._validate_xml_body(xml_body)
        assert result == xml_body
    
    def test_validate_xml_body_invalid(self):
        """Test XML body validation with invalid XML."""
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator._validate_xml_body('<invalid><xml>')
    
    def test_validate_complete_request(self):
        """Test complete request validation."""
        validator = RequestValidator()
        
        validated = validator.validate_complete_request(
            method='POST',
            url='https://api.example.com/test',
            headers={'Content-Type': 'application/json'},
            body='{"name": "test"}',
            params={'debug': 'true'}
        )
        
        assert validated['method'] == HTTPMethod.POST
        assert validated['url'] == 'https://api.example.com/test'
        assert 'Content-Type' in validated['headers']
        assert validated['body'] is not None
        assert 'debug' in validated['params']


class TestRequestPreprocessor:
    """Test request preprocessor functionality."""
    
    def test_detect_content_type_json(self):
        """Test content type detection for JSON."""
        preprocessor = RequestPreprocessor()
        
        content_type = preprocessor.detect_content_type('{"name": "test"}')
        assert content_type == 'application/json'
    
    def test_detect_content_type_xml(self):
        """Test content type detection for XML."""
        preprocessor = RequestPreprocessor()
        
        content_type = preprocessor.detect_content_type('<root><item>test</item></root>')
        assert content_type == 'application/xml'
    
    def test_detect_content_type_form(self):
        """Test content type detection for form data."""
        preprocessor = RequestPreprocessor()
        
        content_type = preprocessor.detect_content_type('name=test&value=123')
        assert content_type == 'application/x-www-form-urlencoded'
    
    def test_detect_content_type_text(self):
        """Test content type detection for plain text."""
        preprocessor = RequestPreprocessor()
        
        content_type = preprocessor.detect_content_type('plain text content')
        assert content_type == 'text/plain'
    
    def test_add_default_headers(self):
        """Test adding default headers."""
        preprocessor = RequestPreprocessor()
        
        headers = preprocessor.add_default_headers(
            headers={'Authorization': 'Bearer token'},
            body='{"name": "test"}'
        )
        
        assert 'Authorization' in headers
        assert 'Content-Type' in headers
        assert 'Content-Length' in headers
        assert 'User-Agent' in headers
        assert headers['Content-Type'] == 'application/json'
    
    def test_merge_headers_case_insensitive(self):
        """Test case-insensitive header merging."""
        preprocessor = RequestPreprocessor()
        
        merged = preprocessor.merge_headers(
            {'content-type': 'application/json'},
            {'Content-Type': 'application/xml'}
        )
        
        # Should have only one Content-Type header
        content_type_keys = [k for k in merged.keys() if k.lower() == 'content-type']
        assert len(content_type_keys) == 1
        assert merged['Content-Type'] == 'application/xml'
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_body_from_file(self, mock_read_text, mock_exists):
        """Test loading body from file."""
        mock_exists.return_value = True
        mock_read_text.return_value = '{"name": "test"}'
        
        preprocessor = RequestPreprocessor()
        body, content_type = preprocessor.load_body_from_file('test.json')
        
        assert body == '{"name": "test"}'
        assert content_type == 'application/json'
    
    def test_preprocess_request_complete(self):
        """Test complete request preprocessing."""
        preprocessor = RequestPreprocessor()
        
        processed = preprocessor.preprocess_request(
            method='POST',
            url='https://api.example.com/test',
            headers={'Authorization': 'Bearer token'},
            body='{"name": "test"}',
            params={'debug': 'true'}
        )
        
        assert processed['method'] == HTTPMethod.POST
        assert processed['url'] == 'https://api.example.com/test'
        assert 'Authorization' in processed['headers']
        assert 'Content-Type' in processed['headers']
        assert processed['body'] is not None
        assert 'debug' in processed['params']
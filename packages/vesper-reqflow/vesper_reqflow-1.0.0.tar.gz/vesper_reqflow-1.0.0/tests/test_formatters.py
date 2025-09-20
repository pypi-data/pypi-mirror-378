"""Tests for response formatters."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from rich.console import Console
from rich.table import Table
from rich.text import Text

from apitester.formatters.response_formatter import ResponseFormatter
from apitester.formatters.table_formatter import TableFormatter
from apitester.formatters.response_saver import ResponseSaver, ResponseSaveError
from apitester.core.http_client import HTTPResponse
from apitester.core.graphql_client import GraphQLResponse


class TestResponseFormatter:
    """Test response formatter functionality."""
    
    @pytest.fixture
    def formatter(self):
        """Create response formatter with mock console."""
        console = Mock(spec=Console)
        return ResponseFormatter(console)
    
    @pytest.fixture
    def mock_http_response(self):
        """Mock HTTP response."""
        response = Mock(spec=HTTPResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json'}
        response.text = '{"message": "success"}'
        response.url = 'https://api.example.com/test'
        response.request_time = 0.5
        response.from_cache = False
        return response
    
    @pytest.fixture
    def mock_graphql_response(self):
        """Mock GraphQL response."""
        response = Mock(spec=GraphQLResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json'}
        response.request_time = 0.3
        response.from_cache = False
        response.has_errors.return_value = False
        response.data = {"user": {"id": "1", "name": "John"}}
        response.get_error_messages.return_value = []
        response.extensions = None
        return response
    
    def test_get_status_color(self, formatter):
        """Test status code color mapping."""
        assert formatter.get_status_color(200) == "green"
        assert formatter.get_status_color(201) == "green"
        assert formatter.get_status_color(301) == "cyan"
        assert formatter.get_status_color(404) == "yellow"
        assert formatter.get_status_color(500) == "red"
        assert formatter.get_status_color(999) == "white"
    
    def test_colorize_status(self, formatter):
        """Test status code colorization."""
        status_text = formatter.colorize_status(200)
        assert isinstance(status_text, Text)
        assert "200" in str(status_text)
        assert "OK" in str(status_text)
    
    def test_format_headers(self, formatter):
        """Test header formatting."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123'
        }
        
        table = formatter.format_headers(headers)
        assert isinstance(table, Table)
    
    def test_pretty_print_json_valid(self, formatter):
        """Test JSON pretty printing with valid JSON."""
        json_data = '{"name": "test", "value": 123}'
        result = formatter.pretty_print_json(json_data)
        
        # Should return Syntax object
        assert hasattr(result, 'code')
    
    def test_pretty_print_json_invalid(self, formatter):
        """Test JSON pretty printing with invalid JSON."""
        invalid_json = '{"invalid": json}'
        result = formatter.pretty_print_json(invalid_json)
        
        # Should still return Syntax object (as text)
        assert hasattr(result, 'code')
    
    def test_pretty_print_xml_valid(self, formatter):
        """Test XML pretty printing with valid XML."""
        xml_data = '<root><item>test</item></root>'
        result = formatter.pretty_print_xml(xml_data)
        
        assert hasattr(result, 'code')
    
    def test_detect_content_type_json(self, formatter):
        """Test content type detection for JSON."""
        headers = {'Content-Type': 'application/json'}
        content_type = formatter.detect_content_type('{"test": true}', headers)
        assert content_type == 'json'
    
    def test_detect_content_type_xml(self, formatter):
        """Test content type detection for XML."""
        headers = {'Content-Type': 'application/xml'}
        content_type = formatter.detect_content_type('<root></root>', headers)
        assert content_type == 'xml'
    
    def test_detect_content_type_by_content(self, formatter):
        """Test content type detection by content analysis."""
        # JSON detection
        content_type = formatter.detect_content_type('{"test": true}', {})
        assert content_type == 'json'
        
        # XML detection
        content_type = formatter.detect_content_type('<root></root>', {})
        assert content_type == 'xml'
        
        # HTML detection
        content_type = formatter.detect_content_type('<html><body></body></html>', {})
        assert content_type == 'html'
    
    def test_format_timing_info(self, formatter):
        """Test timing information formatting."""
        # Fast request
        timing = formatter.format_timing_info(0.05)
        assert isinstance(timing, Text)
        
        # Cached request
        timing = formatter.format_timing_info(0.1, from_cache=True)
        assert "cached" in str(timing)
    
    def test_format_http_response(self, formatter, mock_http_response):
        """Test HTTP response formatting."""
        formatter.format_http_response(mock_http_response)
        
        # Verify console.print was called
        assert formatter.console.print.called
    
    def test_format_graphql_response(self, formatter, mock_graphql_response):
        """Test GraphQL response formatting."""
        formatter.format_graphql_response(mock_graphql_response)
        
        # Verify console.print was called
        assert formatter.console.print.called
    
    def test_format_graphql_response_with_errors(self, formatter):
        """Test GraphQL response formatting with errors."""
        response = Mock(spec=GraphQLResponse)
        response.status_code = 200
        response.headers = {}
        response.request_time = 0.3
        response.from_cache = False
        response.has_errors.return_value = True
        response.get_error_messages.return_value = ["Field 'user' not found"]
        response.data = None
        response.extensions = None
        
        formatter.format_graphql_response(response)
        
        # Verify console.print was called
        assert formatter.console.print.called


class TestTableFormatter:
    """Test table formatter functionality."""
    
    @pytest.fixture
    def formatter(self):
        """Create table formatter with mock console."""
        console = Mock(spec=Console)
        return TableFormatter(console)
    
    @pytest.fixture
    def sample_array_data(self):
        """Sample array data for table formatting."""
        return [
            {"id": 1, "name": "John", "email": "john@example.com", "active": True},
            {"id": 2, "name": "Jane", "email": "jane@example.com", "active": False},
            {"id": 3, "name": "Bob", "email": "bob@example.com", "active": True}
        ]
    
    def test_detect_table_structure_valid(self, formatter, sample_array_data):
        """Test table structure detection with valid data."""
        assert formatter.detect_table_structure(sample_array_data) is True
    
    def test_detect_table_structure_invalid(self, formatter):
        """Test table structure detection with invalid data."""
        # Not a list
        assert formatter.detect_table_structure({"key": "value"}) is False
        
        # Empty list
        assert formatter.detect_table_structure([]) is False
        
        # Mixed types
        assert formatter.detect_table_structure([1, "string", {"key": "value"}]) is False
        
        # Inconsistent dictionaries
        inconsistent_data = [
            {"a": 1, "b": 2},
            {"x": 1, "y": 2, "z": 3}
        ]
        # This might still be considered valid depending on overlap threshold
        result = formatter.detect_table_structure(inconsistent_data)
        assert isinstance(result, bool)
    
    def test_extract_columns(self, formatter, sample_array_data):
        """Test column extraction from array data."""
        columns = formatter.extract_columns(sample_array_data)
        
        assert "id" in columns
        assert "name" in columns
        assert "email" in columns
        assert "active" in columns
        
        # ID should be first (priority key)
        assert columns[0] == "id"
    
    def test_format_cell_value(self, formatter):
        """Test cell value formatting."""
        # None
        assert formatter.format_cell_value(None) == ""
        
        # Boolean
        assert formatter.format_cell_value(True) == "✅"
        assert formatter.format_cell_value(False) == "❌"
        
        # Numbers
        assert formatter.format_cell_value(123) == "123"
        assert formatter.format_cell_value(45.67) == "45.67"
        
        # Strings
        assert formatter.format_cell_value("test") == "test"
        
        # Long strings (truncated)
        long_string = "x" * 200
        result = formatter.format_cell_value(long_string)
        assert len(result) <= formatter.max_cell_length
        assert result.endswith("...")
        
        # Complex objects (JSON)
        complex_obj = {"nested": {"key": "value"}}
        result = formatter.format_cell_value(complex_obj)
        assert isinstance(result, str)
    
    def test_get_column_style(self, formatter):
        """Test column style determination."""
        # ID column
        style = formatter.get_column_style("id", [1, 2, 3])
        assert "cyan" in style
        
        # Name column
        style = formatter.get_column_style("name", ["John", "Jane"])
        assert "white" in style
        
        # Email column
        style = formatter.get_column_style("email", ["test@example.com"])
        assert "blue" in style
        
        # Boolean values
        style = formatter.get_column_style("active", [True, False, True])
        assert "cyan" in style
    
    def test_create_rich_table(self, formatter, sample_array_data):
        """Test Rich table creation."""
        table = formatter.create_rich_table(sample_array_data, "Test Table")
        
        assert isinstance(table, Table)
        assert table.title == "Test Table"
    
    def test_create_rich_table_empty(self, formatter):
        """Test Rich table creation with empty data."""
        table = formatter.create_rich_table([], "Empty Table")
        
        assert isinstance(table, Table)
        assert "Empty" in table.title
    
    def test_format_as_table_single(self, formatter, sample_array_data):
        """Test table formatting without pagination."""
        result = formatter.format_as_table(sample_array_data, "Test")
        
        assert isinstance(result, Table)
    
    def test_format_as_table_paginated(self, formatter):
        """Test table formatting with pagination."""
        # Create large dataset
        large_data = [{"id": i, "name": f"User{i}"} for i in range(100)]
        
        result = formatter.format_as_table(large_data, "Large Dataset", max_rows=20)
        
        assert isinstance(result, list)
        assert len(result) > 1  # Should be paginated
        assert all(isinstance(table, Table) for table in result)
    
    def test_format_as_table_invalid_data(self, formatter):
        """Test table formatting with invalid data."""
        with pytest.raises(ValueError):
            formatter.format_as_table("not a list")
    
    def test_analyze_data_structure(self, formatter, sample_array_data):
        """Test data structure analysis."""
        analysis = formatter.analyze_data_structure(sample_array_data)
        
        assert analysis['is_array'] is True
        assert analysis['length'] == 3
        assert analysis['is_table_suitable'] is True
        assert len(analysis['columns']) > 0
        assert 'id' in analysis['data_types']
    
    def test_suggest_display_format(self, formatter, sample_array_data):
        """Test display format suggestion."""
        # Table-suitable data
        format_suggestion = formatter.suggest_display_format(sample_array_data)
        assert format_suggestion == 'table'
        
        # Simple list
        simple_list = [1, 2, 3, 4, 5]
        format_suggestion = formatter.suggest_display_format(simple_list)
        assert format_suggestion == 'list'
        
        # Dictionary
        dict_data = {"key": "value"}
        format_suggestion = formatter.suggest_display_format(dict_data)
        assert format_suggestion == 'json'
        
        # Single value
        format_suggestion = formatter.suggest_display_format("single value")
        assert format_suggestion == 'single'
    
    def test_format_simple_list(self, formatter):
        """Test simple list formatting."""
        simple_list = ["apple", "banana", "cherry"]
        table = formatter.format_simple_list(simple_list, "Fruits")
        
        assert isinstance(table, Table)
        assert "Fruits" in table.title


class TestResponseSaver:
    """Test response saver functionality."""
    
    @pytest.fixture
    def saver(self):
        """Create response saver."""
        return ResponseSaver()
    
    @pytest.fixture
    def mock_http_response(self):
        """Mock HTTP response."""
        response = Mock(spec=HTTPResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json'}
        response.text = '{"message": "success"}'
        response.content = b'{"message": "success"}'
        response.url = 'https://api.example.com/test'
        response.request_time = 0.5
        return response
    
    @pytest.fixture
    def mock_graphql_response(self):
        """Mock GraphQL response."""
        response = Mock(spec=GraphQLResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json'}
        response.request_time = 0.3
        response.to_dict.return_value = {
            "data": {"user": {"id": "1", "name": "John"}},
            "errors": None
        }
        return response
    
    def test_generate_filename(self, saver):
        """Test filename generation."""
        # With timestamp
        filename = saver.generate_filename("test", "json", True)
        assert filename.startswith("test_")
        assert filename.endswith(".json")
        
        # Without timestamp
        filename = saver.generate_filename("test", "json", False)
        assert filename == "test.json"
        
        # Default name
        filename = saver.generate_filename(None, "json", False)
        assert filename == "response.json"
    
    def test_detect_response_format(self, saver, mock_http_response, mock_graphql_response):
        """Test response format detection."""
        # GraphQL response
        format_type = saver.detect_response_format(mock_graphql_response)
        assert format_type == 'json'
        
        # HTTP JSON response
        format_type = saver.detect_response_format(mock_http_response)
        assert format_type == 'json'
        
        # HTTP XML response
        mock_http_response.headers = {'Content-Type': 'application/xml'}
        format_type = saver.detect_response_format(mock_http_response)
        assert format_type == 'xml'
        
        # HTTP HTML response
        mock_http_response.headers = {'Content-Type': 'text/html'}
        format_type = saver.detect_response_format(mock_http_response)
        assert format_type == 'html'
        
        # HTTP plain text response
        mock_http_response.headers = {'Content-Type': 'text/plain'}
        format_type = saver.detect_response_format(mock_http_response)
        assert format_type == 'text'
    
    def test_save_response_body(self, saver, mock_http_response):
        """Test saving response body to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_response.json"
            
            saved_path = saver.save_response_body(mock_http_response, file_path)
            
            assert saved_path.exists()
            assert saved_path == file_path
            
            # Verify content
            content = saved_path.read_text()
            assert "success" in content
    
    def test_save_response_headers(self, saver, mock_http_response):
        """Test saving response headers to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_headers.json"
            
            saved_path = saver.save_response_headers(mock_http_response, file_path)
            
            assert saved_path.exists()
            assert saved_path == file_path
            
            # Verify content
            content = json.loads(saved_path.read_text())
            assert content['status_code'] == 200
            assert 'headers' in content
            assert 'timestamp' in content
    
    def test_save_complete_response(self, saver, mock_http_response):
        """Test saving complete response."""
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_files = saver.save_complete_response(
                mock_http_response, 
                temp_dir, 
                "test_response"
            )
            
            assert 'body' in saved_files
            assert 'headers' in saved_files
            assert saved_files['body'].exists()
            assert saved_files['headers'].exists()
    
    def test_save_raw_response(self, saver, mock_http_response):
        """Test saving raw response content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_raw.bin"
            
            saved_path = saver.save_raw_response(mock_http_response, file_path)
            
            assert saved_path.exists()
            assert saved_path == file_path
            
            # Verify content
            content = saved_path.read_bytes()
            assert content == mock_http_response.content
    
    def test_save_response_summary(self, saver, mock_http_response):
        """Test saving response summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_summary.json"
            
            request_info = {
                'method': 'GET',
                'url': 'https://api.example.com/test'
            }
            
            saved_path = saver.save_response_summary(
                mock_http_response, 
                file_path, 
                request_info
            )
            
            assert saved_path.exists()
            
            # Verify content
            content = json.loads(saved_path.read_text())
            assert content['status_code'] == 200
            assert content['response_type'] == 'HTTP'
            assert 'request' in content
    
    def test_ensure_directory_creation(self, saver):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new" / "nested" / "directory"
            
            result_dir = saver.ensure_directory(new_dir)
            
            assert result_dir.exists()
            assert result_dir.is_dir()
    
    def test_save_error_handling(self, saver):
        """Test error handling in save operations."""
        # Try to save to invalid path
        with pytest.raises(ResponseSaveError):
            invalid_path = Path("/invalid/path/that/does/not/exist/file.json")
            saver.save_response_body(Mock(), invalid_path)
    
    @patch('pathlib.Path.mkdir')
    def test_permission_error_handling(self, mock_mkdir, saver):
        """Test permission error handling."""
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(ResponseSaveError):
            saver.ensure_directory("/some/path")
    
    def test_cleanup_old_files(self, saver):
        """Test cleanup of old files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            for i in range(5):
                (temp_path / f"response_{i}.json").write_text('{"test": true}')
            
            # Cleanup with max_files=3
            deleted_count = saver.cleanup_old_files(temp_path, max_files=3)
            
            assert deleted_count >= 0
            
            # Check remaining files
            remaining_files = list(temp_path.glob("*.json"))
            assert len(remaining_files) <= 3
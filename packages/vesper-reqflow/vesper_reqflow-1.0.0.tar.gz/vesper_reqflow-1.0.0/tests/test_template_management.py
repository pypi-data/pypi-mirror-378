"""Tests for template management system."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from apitester.core.template_manager import (
    TemplateManager, TemplateManagerError, TemplateNotFoundError, TemplateValidationError
)
from apitester.core.template_executor import (
    TemplateExecutor, TemplateExecutionError, VariableSubstitutionError
)
from apitester.core.template_importer import (
    TemplateImporter, TemplateImportError, TemplateExportError
)
from apitester.storage.models import RequestTemplate, HTTPMethod


class TestTemplateManager:
    """Test template manager functionality."""
    
    @pytest.fixture
    def mock_template_ops(self):
        """Mock template operations."""
        with patch('apitester.core.template_manager.TemplateOperations') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def template_manager(self, mock_template_ops):
        """Create template manager with mocked operations."""
        return TemplateManager()
    
    @pytest.fixture
    def sample_template_data(self):
        """Sample template data for testing."""
        return {
            'name': 'test-template',
            'method': 'POST',
            'url': 'https://api.example.com/users',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"name": "test"}',
            'params': {'debug': 'true'},
            'description': 'Test template',
            'tags': ['test', 'api']
        }
    
    def test_save_template_success(self, template_manager, mock_template_ops, sample_template_data):
        """Test successful template saving."""
        mock_template_ops.template_exists.return_value = False
        mock_template_ops.save_template.return_value = True
        
        template = template_manager.save_template(**sample_template_data)
        
        assert isinstance(template, RequestTemplate)
        assert template.name == 'test-template'
        assert template.method == HTTPMethod.POST
        assert template.url == 'https://api.example.com/users'
        
        mock_template_ops.save_template.assert_called_once()
    
    def test_save_template_already_exists(self, template_manager, mock_template_ops, sample_template_data):
        """Test saving template that already exists."""
        mock_template_ops.template_exists.return_value = True
        
        with pytest.raises(TemplateManagerError, match="already exists"):
            template_manager.save_template(**sample_template_data)
    
    def test_save_template_with_overwrite(self, template_manager, mock_template_ops, sample_template_data):
        """Test saving template with overwrite enabled."""
        mock_template_ops.template_exists.return_value = True
        mock_template_ops.save_template.return_value = True
        
        template = template_manager.save_template(overwrite=True, **sample_template_data)
        
        assert isinstance(template, RequestTemplate)
        mock_template_ops.save_template.assert_called_once()
    
    def test_save_template_validation_error(self, template_manager, mock_template_ops):
        """Test template saving with validation error."""
        mock_template_ops.template_exists.return_value = False
        
        with pytest.raises(TemplateValidationError):
            template_manager.save_template(
                name='',  # Invalid empty name
                method='GET',
                url='https://api.example.com'
            )
    
    def test_load_template_success(self, template_manager, mock_template_ops):
        """Test successful template loading."""
        mock_template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/test'
        )
        mock_template_ops.load_template.return_value = mock_template
        
        template = template_manager.load_template('test-template')
        
        assert template == mock_template
        mock_template_ops.load_template.assert_called_once_with('test-template')
    
    def test_load_template_not_found(self, template_manager, mock_template_ops):
        """Test loading non-existent template."""
        mock_template_ops.load_template.return_value = None
        
        with pytest.raises(TemplateNotFoundError):
            template_manager.load_template('nonexistent')
    
    def test_list_templates(self, template_manager, mock_template_ops):
        """Test listing templates."""
        mock_template_ops.list_templates.return_value = ['template1', 'template2', 'template3']
        
        templates = template_manager.list_templates()
        
        assert templates == ['template1', 'template2', 'template3']
        mock_template_ops.list_templates.assert_called_once()
    
    def test_delete_template_success(self, template_manager, mock_template_ops):
        """Test successful template deletion."""
        mock_template_ops.template_exists.return_value = True
        mock_template_ops.delete_template.return_value = True
        
        result = template_manager.delete_template('test-template')
        
        assert result is True
        mock_template_ops.delete_template.assert_called_once_with('test-template')
    
    def test_delete_template_not_found(self, template_manager, mock_template_ops):
        """Test deleting non-existent template."""
        mock_template_ops.template_exists.return_value = False
        
        with pytest.raises(TemplateNotFoundError):
            template_manager.delete_template('nonexistent')
    
    def test_update_template(self, template_manager, mock_template_ops):
        """Test template updating."""
        mock_template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/test',
            description='Original description'
        )
        mock_template_ops.load_template.return_value = mock_template
        mock_template_ops.save_template.return_value = True
        
        updated_template = template_manager.update_template(
            'test-template',
            description='Updated description',
            method='POST'
        )
        
        assert updated_template.description == 'Updated description'
        assert updated_template.method == HTTPMethod.POST
        mock_template_ops.save_template.assert_called_once()
    
    def test_duplicate_template(self, template_manager, mock_template_ops):
        """Test template duplication."""
        source_template = RequestTemplate(
            name='source-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/test',
            description='Source template'
        )
        
        mock_template_ops.load_template.return_value = source_template
        mock_template_ops.template_exists.return_value = False
        mock_template_ops.save_template.return_value = True
        
        new_template = template_manager.duplicate_template('source-template', 'new-template')
        
        assert new_template.name == 'new-template'
        assert new_template.method == source_template.method
        assert new_template.url == source_template.url
        assert new_template.description == 'Source template (copy)'
    
    def test_search_templates(self, template_manager, mock_template_ops):
        """Test template searching."""
        mock_template_ops.list_templates.return_value = ['api-users', 'api-posts', 'web-login']
        
        # Mock template loading for search
        def mock_load_template(name):
            templates = {
                'api-users': RequestTemplate(
                    name='api-users',
                    method=HTTPMethod.GET,
                    url='https://api.example.com/users',
                    description='Get users from API'
                ),
                'api-posts': RequestTemplate(
                    name='api-posts',
                    method=HTTPMethod.GET,
                    url='https://api.example.com/posts',
                    description='Get posts from API'
                ),
                'web-login': RequestTemplate(
                    name='web-login',
                    method=HTTPMethod.POST,
                    url='https://web.example.com/login',
                    description='Login to web interface'
                )
            }
            return templates.get(name)
        
        mock_template_ops.load_template.side_effect = mock_load_template
        
        # Search for 'api'
        results = template_manager.search_templates('api')
        
        assert len(results) == 2
        assert all('api' in result['name'] or 'api' in result['description'] or 'api' in result['url'] 
                  for result in results)
    
    def test_validate_template_name(self, template_manager):
        """Test template name validation."""
        # Valid names
        assert template_manager.validate_template_name('valid-name') is True
        assert template_manager.validate_template_name('valid_name_123') is True
        
        # Invalid names
        with pytest.raises(TemplateValidationError):
            template_manager.validate_template_name('')  # Empty
        
        with pytest.raises(TemplateValidationError):
            template_manager.validate_template_name('name/with/slash')  # Invalid character
        
        with pytest.raises(TemplateValidationError):
            template_manager.validate_template_name('x' * 101)  # Too long


class TestTemplateExecutor:
    """Test template executor functionality."""
    
    @pytest.fixture
    def mock_template_manager(self):
        """Mock template manager."""
        with patch('apitester.core.template_executor.TemplateManager') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.request_time = 0.5
        mock_client.send_request.return_value = mock_response
        return mock_client
    
    @pytest.fixture
    def template_executor(self, mock_http_client):
        """Create template executor with mocked dependencies."""
        return TemplateExecutor(http_client=mock_http_client)
    
    def test_substitute_variables_simple(self, template_executor):
        """Test simple variable substitution."""
        # Mock environment operations
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {'API_KEY': 'test-key', 'BASE_URL': 'https://api.test.com'}
            mock_load.return_value = mock_env
            
            result = template_executor.substitute_variables(
                'Authorization: Bearer ${API_KEY}',
                environment='test'
            )
            
            assert result == 'Authorization: Bearer test-key'
    
    def test_substitute_variables_with_default(self, template_executor):
        """Test variable substitution with default values."""
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {}
            mock_load.return_value = mock_env
            
            result = template_executor.substitute_variables(
                'Host: ${HOST:localhost}',
                environment='test'
            )
            
            assert result == 'Host: localhost'
    
    def test_substitute_variables_missing(self, template_executor):
        """Test variable substitution with missing variables."""
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {}
            mock_load.return_value = mock_env
            
            with pytest.raises(VariableSubstitutionError):
                template_executor.substitute_variables(
                    'Authorization: Bearer ${MISSING_KEY}',
                    environment='test'
                )
    
    def test_substitute_variables_custom_override(self, template_executor):
        """Test variable substitution with custom variables."""
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {'API_KEY': 'env-key'}
            mock_load.return_value = mock_env
            
            result = template_executor.substitute_variables(
                'Authorization: Bearer ${API_KEY}',
                environment='test',
                custom_variables={'API_KEY': 'custom-key'}
            )
            
            assert result == 'Authorization: Bearer custom-key'  # Custom overrides env
    
    def test_apply_template_overrides(self, template_executor):
        """Test applying overrides to template."""
        template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'},
            params={'limit': '10'}
        )
        
        overridden = template_executor.apply_template_overrides(
            template,
            method='POST',
            headers={'Content-Type': 'application/json'},
            params={'debug': 'true'}
        )
        
        assert overridden.method == HTTPMethod.POST
        assert overridden.headers['Accept'] == 'application/json'  # Original
        assert overridden.headers['Content-Type'] == 'application/json'  # Override
        assert overridden.params['limit'] == '10'  # Original
        assert overridden.params['debug'] == 'true'  # Override
    
    def test_execute_template_success(self, template_executor, mock_template_manager, mock_http_client):
        """Test successful template execution."""
        template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'}
        )
        
        mock_template_manager.load_template.return_value = template
        
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {}
            mock_load.return_value = mock_env
            
            response = template_executor.execute_template('test-template')
            
            assert response.status_code == 200
            mock_http_client.send_request.assert_called_once()
    
    def test_execute_template_batch(self, template_executor, mock_template_manager, mock_http_client):
        """Test batch template execution."""
        template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/users'
        )
        
        mock_template_manager.load_template.return_value = template
        
        with patch.object(template_executor.env_ops, 'load_environment') as mock_load:
            mock_env = Mock()
            mock_env.variables = {}
            mock_load.return_value = mock_env
            
            configs = [
                {'template_name': 'test-template'},
                {'template_name': 'test-template', 'overrides': {'method': 'POST'}}
            ]
            
            results = template_executor.execute_template_batch(configs)
            
            assert len(results) == 2
            assert all(result['success'] for result in results)
    
    def test_extract_variables_from_template(self, template_executor, mock_template_manager):
        """Test extracting variables from template."""
        template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://${HOST}/api/${VERSION}/users',
            headers={'Authorization': 'Bearer ${API_KEY}'},
            body='{"user_id": "${USER_ID}"}',
            params={'env': '${ENVIRONMENT}'}
        )
        
        mock_template_manager.load_template.return_value = template
        
        variables = template_executor.extract_variables_from_template('test-template')
        
        expected_vars = ['API_KEY', 'ENVIRONMENT', 'HOST', 'USER_ID', 'VERSION']
        assert sorted(variables) == expected_vars


class TestTemplateImporter:
    """Test template importer functionality."""
    
    @pytest.fixture
    def template_importer(self):
        """Create template importer."""
        return TemplateImporter()
    
    @pytest.fixture
    def sample_export_data(self):
        """Sample export data for testing."""
        return {
            'export_info': {
                'version': '1.0',
                'exported_at': '2023-01-01T00:00:00',
                'template_count': 2
            },
            'templates': {
                'get-users': {
                    'method': 'GET',
                    'url': 'https://api.example.com/users',
                    'headers': {'Accept': 'application/json'},
                    'body': '',
                    'params': {},
                    'description': 'Get all users',
                    'tags': ['api', 'users']
                },
                'create-user': {
                    'method': 'POST',
                    'url': 'https://api.example.com/users',
                    'headers': {'Content-Type': 'application/json'},
                    'body': '{"name": "test"}',
                    'params': {},
                    'description': 'Create new user',
                    'tags': ['api', 'users']
                }
            }
        }
    
    @patch('apitester.core.template_importer.TemplateManager')
    def test_export_templates_json(self, mock_manager_class, template_importer):
        """Test exporting templates to JSON."""
        mock_manager = mock_manager_class.return_value
        mock_manager.list_templates.return_value = ['test-template']
        
        mock_template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/test',
            description='Test template'
        )
        mock_manager.load_template.return_value = mock_template
        
        result = template_importer.export_templates(['test-template'], format_type='json')
        
        assert isinstance(result, str)
        data = json.loads(result)
        assert 'export_info' in data
        assert 'templates' in data
        assert 'test-template' in data['templates']
    
    @patch('apitester.core.template_importer.TemplateManager')
    def test_export_templates_yaml(self, mock_manager_class, template_importer):
        """Test exporting templates to YAML."""
        mock_manager = mock_manager_class.return_value
        mock_manager.list_templates.return_value = ['test-template']
        
        mock_template = RequestTemplate(
            name='test-template',
            method=HTTPMethod.GET,
            url='https://api.example.com/test'
        )
        mock_manager.load_template.return_value = mock_template
        
        result = template_importer.export_templates(['test-template'], format_type='yaml')
        
        assert isinstance(result, str)
        assert 'export_info:' in result
        assert 'templates:' in result
    
    def test_export_templates_to_file(self, template_importer):
        """Test exporting templates to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "templates.json"
            
            with patch.object(template_importer, 'export_templates') as mock_export:
                mock_export.return_value = '{"test": "data"}'
                
                result_path = template_importer.export_templates_to_file(
                    file_path, 
                    template_names=['test']
                )
                
                assert result_path.exists()
                assert result_path == file_path
                content = result_path.read_text()
                assert content == '{"test": "data"}'
    
    @patch('apitester.core.template_importer.TemplateManager')
    def test_import_templates_json(self, mock_manager_class, template_importer, sample_export_data):
        """Test importing templates from JSON."""
        mock_manager = mock_manager_class.return_value
        mock_manager.template_ops.template_exists.return_value = False
        mock_manager.template_ops.save_template.return_value = True
        
        json_data = json.dumps(sample_export_data)
        
        results = template_importer.import_templates(json_data, 'json')
        
        assert results['success'] is True
        assert results['imported_count'] == 2
        assert results['error_count'] == 0
        assert len(results['imported_templates']) == 2
    
    @patch('apitester.core.template_importer.TemplateManager')
    def test_import_templates_with_conflicts(self, mock_manager_class, template_importer, sample_export_data):
        """Test importing templates with existing conflicts."""
        mock_manager = mock_manager_class.return_value
        mock_manager.template_ops.template_exists.return_value = True  # Templates exist
        
        json_data = json.dumps(sample_export_data)
        
        results = template_importer.import_templates(
            json_data, 
            'json', 
            overwrite_existing=False
        )
        
        assert results['imported_count'] == 0
        assert results['skipped_count'] == 2
        assert len(results['skipped_templates']) == 2
    
    def test_import_templates_from_file(self, template_importer, sample_export_data):
        """Test importing templates from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "templates.json"
            file_path.write_text(json.dumps(sample_export_data))
            
            with patch.object(template_importer, 'import_templates') as mock_import:
                mock_import.return_value = {'success': True, 'imported_count': 2}
                
                results = template_importer.import_templates_from_file(file_path)
                
                assert results['success'] is True
                mock_import.assert_called_once()
    
    def test_convert_postman_collection(self, template_importer):
        """Test converting Postman collection."""
        postman_data = {
            'info': {
                'name': 'Test Collection'
            },
            'item': [
                {
                    'name': 'Get Users',
                    'request': {
                        'method': 'GET',
                        'url': 'https://api.example.com/users',
                        'header': [
                            {'key': 'Accept', 'value': 'application/json'}
                        ]
                    }
                },
                {
                    'name': 'Create User',
                    'request': {
                        'method': 'POST',
                        'url': 'https://api.example.com/users',
                        'header': [
                            {'key': 'Content-Type', 'value': 'application/json'}
                        ],
                        'body': {
                            'mode': 'raw',
                            'raw': '{"name": "test"}'
                        }
                    }
                }
            ]
        }
        
        converted = template_importer.convert_postman_collection(postman_data)
        
        assert 'export_info' in converted
        assert 'templates' in converted
        assert len(converted['templates']) == 2
        
        # Check converted templates
        templates = converted['templates']
        assert any('get_users' in name for name in templates.keys())
        assert any('create_user' in name for name in templates.keys())
    
    def test_import_invalid_format(self, template_importer):
        """Test importing with invalid format."""
        with pytest.raises(TemplateImportError):
            template_importer.import_templates('{"test": true}', 'invalid_format')
    
    def test_import_invalid_json(self, template_importer):
        """Test importing invalid JSON."""
        with pytest.raises(TemplateImportError):
            template_importer.import_templates('invalid json', 'json')
    
    def test_import_missing_structure(self, template_importer):
        """Test importing data with missing required structure."""
        invalid_data = json.dumps({'not_templates': {}})
        
        with pytest.raises(TemplateImportError):
            template_importer.import_templates(invalid_data, 'json')
"""Tests for environment management system."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from apitester.core.env_manager import (
    EnvironmentManager, EnvironmentManagerError, EnvironmentNotFoundError, EnvironmentValidationError
)
from apitester.core.variable_substitution import (
    VariableSubstitutionEngine, VariableSubstitutionError, CircularReferenceError
)
from apitester.core.env_operations import (
    EnvironmentOperations, EnvironmentOperationsError
)
from apitester.storage.models import Environment


class TestEnvironmentManager:
    """Test environment manager functionality."""
    
    @pytest.fixture
    def mock_env_ops(self):
        """Mock environment operations."""
        with patch('apitester.core.env_manager.EnvironmentOperations') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def env_manager(self, mock_env_ops):
        """Create environment manager with mocked operations."""
        return EnvironmentManager()
    
    @pytest.fixture
    def sample_environment(self):
        """Sample environment for testing."""
        return Environment(
            name='test-env',
            variables={'API_KEY': 'test-key', 'BASE_URL': 'https://api.test.com'},
            description='Test environment'
        )
    
    def test_create_environment_success(self, env_manager, mock_env_ops):
        """Test successful environment creation."""
        mock_env_ops.save_environment.return_value = True
        
        environment = env_manager.create_environment(
            name='test-env',
            description='Test environment',
            variables={'API_KEY': 'test-key'}
        )
        
        assert isinstance(environment, Environment)
        assert environment.name == 'test-env'
        assert environment.description == 'Test environment'
        assert environment.variables['API_KEY'] == 'test-key'
        
        mock_env_ops.save_environment.assert_called_once()
    
    def test_create_environment_invalid_name(self, env_manager, mock_env_ops):
        """Test environment creation with invalid name."""
        with pytest.raises(EnvironmentValidationError):
            env_manager.create_environment('')  # Empty name
        
        with pytest.raises(EnvironmentValidationError):
            env_manager.create_environment('invalid/name')  # Invalid characters
        
        with pytest.raises(EnvironmentValidationError):
            env_manager.create_environment('system')  # Reserved name
    
    def test_load_environment_success(self, env_manager, mock_env_ops, sample_environment):
        """Test successful environment loading."""
        mock_env_ops.load_environment.return_value = sample_environment
        
        environment = env_manager.load_environment('test-env')
        
        assert environment == sample_environment
        mock_env_ops.load_environment.assert_called_once_with('test-env')
    
    def test_load_environment_not_found(self, env_manager, mock_env_ops):
        """Test loading non-existent environment."""
        mock_env_ops.load_environment.return_value = None
        
        with pytest.raises(EnvironmentNotFoundError):
            env_manager.load_environment('nonexistent')
    
    def test_list_environments(self, env_manager, mock_env_ops):
        """Test listing environments."""
        mock_env_ops.list_environments.return_value = ['env1', 'env2', 'env3']
        mock_env_ops.get_current_environment.return_value = 'env1'
        
        environments = env_manager.list_environments()
        
        assert len(environments) == 3
        assert any(env['name'] == 'env1' and env['is_current'] for env in environments)
    
    def test_set_variable_success(self, env_manager, mock_env_ops):
        """Test setting environment variable."""
        mock_env_ops.set_variable.return_value = True
        
        # Mock environment existence check
        with patch.object(env_manager, 'environment_exists', return_value=True):
            result = env_manager.set_variable('test-env', 'API_KEY', 'new-key')
        
        assert result is True
        mock_env_ops.set_variable.assert_called_once_with('test-env', 'API_KEY', 'new-key')
    
    def test_set_variable_create_env(self, env_manager, mock_env_ops):
        """Test setting variable with environment creation."""
        mock_env_ops.set_variable.return_value = True
        mock_env_ops.save_environment.return_value = True
        
        # Mock environment doesn't exist
        with patch.object(env_manager, 'environment_exists', return_value=False):
            result = env_manager.set_variable('new-env', 'API_KEY', 'key', create_env_if_missing=True)
        
        assert result is True
    
    def test_get_variable_success(self, env_manager, mock_env_ops):
        """Test getting environment variable."""
        mock_env_ops.get_variable.return_value = 'test-value'
        
        value = env_manager.get_variable('test-env', 'API_KEY')
        
        assert value == 'test-value'
        mock_env_ops.get_variable.assert_called_once_with('test-env', 'API_KEY')
    
    def test_get_variable_with_default(self, env_manager, mock_env_ops):
        """Test getting variable with default value."""
        mock_env_ops.get_variable.return_value = None
        
        value = env_manager.get_variable('test-env', 'MISSING_KEY', default='default-value')
        
        assert value == 'default-value'
    
    def test_delete_variable_success(self, env_manager, mock_env_ops):
        """Test deleting environment variable."""
        mock_env_ops.delete_variable.return_value = True
        
        with patch.object(env_manager, 'environment_exists', return_value=True):
            result = env_manager.delete_variable('test-env', 'API_KEY')
        
        assert result is True
        mock_env_ops.delete_variable.assert_called_once_with('test-env', 'API_KEY')
    
    def test_delete_environment_success(self, env_manager, mock_env_ops):
        """Test deleting environment."""
        mock_env_ops.delete_environment.return_value = True
        mock_env_ops.get_current_environment.return_value = 'other-env'
        
        with patch.object(env_manager, 'environment_exists', return_value=True):
            result = env_manager.delete_environment('test-env')
        
        assert result is True
        mock_env_ops.delete_environment.assert_called_once_with('test-env')
    
    def test_delete_current_environment_without_force(self, env_manager, mock_env_ops):
        """Test deleting current environment without force."""
        mock_env_ops.get_current_environment.return_value = 'test-env'
        
        with patch.object(env_manager, 'environment_exists', return_value=True):
            with pytest.raises(EnvironmentManagerError, match="Cannot delete current environment"):
                env_manager.delete_environment('test-env')
    
    def test_copy_environment(self, env_manager, mock_env_ops, sample_environment):
        """Test copying environment."""
        mock_env_ops.load_environment.return_value = sample_environment
        mock_env_ops.save_environment.return_value = True
        
        with patch.object(env_manager, 'environment_exists', side_effect=[True, False]):
            copied_env = env_manager.copy_environment('source-env', 'target-env')
        
        assert copied_env.name == 'target-env'
        assert copied_env.variables == sample_environment.variables
        assert 'Copy of source-env' in copied_env.description
    
    def test_merge_environments(self, env_manager, mock_env_ops):
        """Test merging environments."""
        target_env = Environment(
            name='target-env',
            variables={'KEY1': 'value1', 'KEY2': 'old_value'}
        )
        
        source_env = Environment(
            name='source-env',
            variables={'KEY2': 'new_value', 'KEY3': 'value3'}
        )
        
        mock_env_ops.load_environment.side_effect = [target_env, source_env]
        mock_env_ops.save_environment.return_value = True
        
        merged_env = env_manager.merge_environments('target-env', ['source-env'], 'source')
        
        assert merged_env.variables['KEY1'] == 'value1'  # Unchanged
        assert merged_env.variables['KEY2'] == 'new_value'  # Updated from source
        assert merged_env.variables['KEY3'] == 'value3'  # Added from source
    
    def test_search_templates(self, env_manager, mock_env_ops):
        """Test searching environments."""
        mock_env_ops.list_environments.return_value = ['api-dev', 'api-prod', 'web-dev']
        
        def mock_load_env(name):
            envs = {
                'api-dev': Environment(name='api-dev', description='API development environment'),
                'api-prod': Environment(name='api-prod', description='API production environment'),
                'web-dev': Environment(name='web-dev', description='Web development environment')
            }
            return envs.get(name)
        
        mock_env_ops.load_environment.side_effect = mock_load_env
        
        results = env_manager.search_environments('api')
        
        assert len(results) == 2
        assert all('api' in result['name'] or 'api' in result['description'] for result in results)


class TestVariableSubstitutionEngine:
    """Test variable substitution engine functionality."""
    
    @pytest.fixture
    def mock_env_manager(self):
        """Mock environment manager."""
        mock_manager = Mock()
        mock_manager.list_variables.return_value = {
            'variables': {
                'API_KEY': 'test-key',
                'BASE_URL': 'https://api.test.com',
                'NESTED_VAR': '${API_KEY}-suffix'
            }
        }
        return mock_manager
    
    @pytest.fixture
    def substitution_engine(self, mock_env_manager):
        """Create substitution engine with mocked environment manager."""
        return VariableSubstitutionEngine(mock_env_manager)
    
    def test_simple_variable_substitution(self, substitution_engine):
        """Test simple variable substitution."""
        result = substitution_engine.substitute('Authorization: Bearer ${API_KEY}')
        
        assert result == 'Authorization: Bearer test-key'
    
    def test_variable_with_default(self, substitution_engine):
        """Test variable substitution with default value."""
        result = substitution_engine.substitute('Host: ${HOST:localhost}')
        
        assert result == 'Host: localhost'
    
    def test_nested_variable_substitution(self, substitution_engine):
        """Test nested variable substitution."""
        result = substitution_engine.substitute('Token: ${NESTED_VAR}')
        
        assert result == 'Token: test-key-suffix'
    
    def test_custom_variables_override(self, substitution_engine):
        """Test custom variables overriding environment variables."""
        result = substitution_engine.substitute(
            'Key: ${API_KEY}',
            custom_variables={'API_KEY': 'custom-key'}
        )
        
        assert result == 'Key: custom-key'
    
    def test_missing_variable_error(self, substitution_engine):
        """Test error on missing variable."""
        with pytest.raises(VariableSubstitutionError, match="Missing variables"):
            substitution_engine.substitute('Value: ${MISSING_VAR}')
    
    def test_circular_reference_detection(self, substitution_engine):
        """Test circular reference detection."""
        # Mock circular reference
        substitution_engine.env_manager.list_variables.return_value = {
            'variables': {
                'VAR1': '${VAR2}',
                'VAR2': '${VAR1}'
            }
        }
        
        with pytest.raises(CircularReferenceError):
            substitution_engine.substitute('${VAR1}')
    
    def test_function_now(self, substitution_engine):
        """Test now() function."""
        result = substitution_engine.substitute('${now()}')
        
        # Should return current timestamp in default format
        assert len(result) > 10  # Basic check that it returned something
    
    def test_function_uuid(self, substitution_engine):
        """Test uuid() function."""
        result = substitution_engine.substitute('${uuid()}')
        
        # Should return UUID v4 format
        assert len(result) == 36
        assert result.count('-') == 4
    
    def test_function_base64_encode(self, substitution_engine):
        """Test base64() function for encoding."""
        result = substitution_engine.substitute('${base64("hello", "encode")}')
        
        assert result == 'aGVsbG8='
    
    def test_function_base64_decode(self, substitution_engine):
        """Test base64() function for decoding."""
        result = substitution_engine.substitute('${base64("aGVsbG8=", "decode")}')
        
        assert result == 'hello'
    
    def test_function_upper(self, substitution_engine):
        """Test upper() function."""
        result = substitution_engine.substitute('${upper("hello world")}')
        
        assert result == 'HELLO WORLD'
    
    def test_function_lower(self, substitution_engine):
        """Test lower() function."""
        result = substitution_engine.substitute('${lower("HELLO WORLD")}')
        
        assert result == 'hello world'
    
    def test_function_replace(self, substitution_engine):
        """Test replace() function."""
        result = substitution_engine.substitute('${replace("hello world", "world", "universe")}')
        
        assert result == 'hello universe'
    
    def test_function_substring(self, substitution_engine):
        """Test substring() function."""
        result = substitution_engine.substitute('${substring("hello world", "0", "5")}')
        
        assert result == 'hello'
    
    def test_function_length(self, substitution_engine):
        """Test length() function."""
        result = substitution_engine.substitute('${length("hello")}')
        
        assert result == '5'
    
    def test_function_json_extract(self, substitution_engine):
        """Test json_extract() function."""
        json_data = '{"user": {"name": "John", "age": 30}}'
        result = substitution_engine.substitute(f'${{json_extract("{json_data}", "user.name")}}')
        
        assert result == 'John'
    
    def test_extract_variables(self, substitution_engine):
        """Test extracting variables from text."""
        text = 'URL: ${BASE_URL}/api/${VERSION}?key=${API_KEY}'
        variables = substitution_engine.extract_variables(text)
        
        expected = ['API_KEY', 'BASE_URL', 'VERSION']
        assert sorted(variables) == expected
    
    def test_validate_syntax_valid(self, substitution_engine):
        """Test syntax validation with valid text."""
        errors = substitution_engine.validate_syntax('${VAR1} and ${VAR2:default}')
        
        assert len(errors) == 0
    
    def test_validate_syntax_invalid_braces(self, substitution_engine):
        """Test syntax validation with unmatched braces."""
        errors = substitution_engine.validate_syntax('${VAR1 and ${VAR2}')
        
        assert len(errors) > 0
        assert any('brace' in error.lower() for error in errors)
    
    def test_validate_syntax_unknown_function(self, substitution_engine):
        """Test syntax validation with unknown function."""
        errors = substitution_engine.validate_syntax('${unknown_function()}')
        
        assert len(errors) > 0
        assert any('unknown function' in error.lower() for error in errors)
    
    def test_register_custom_function(self, substitution_engine):
        """Test registering custom function."""
        def custom_func(args, context):
            return f"custom:{args[0]}" if args else "custom:empty"
        
        substitution_engine.register_function('custom', custom_func)
        
        result = substitution_engine.substitute('${custom("test")}')
        assert result == 'custom:test'
    
    def test_list_functions(self, substitution_engine):
        """Test listing available functions."""
        functions = substitution_engine.list_functions()
        
        assert len(functions) > 0
        assert any(func['name'] == 'now' for func in functions)
        assert any(func['name'] == 'uuid' for func in functions)
        assert all('description' in func for func in functions)


class TestEnvironmentOperations:
    """Test environment operations functionality."""
    
    @pytest.fixture
    def mock_env_manager(self):
        """Mock environment manager."""
        return Mock()
    
    @pytest.fixture
    def env_operations(self, mock_env_manager):
        """Create environment operations with mocked manager."""
        return EnvironmentOperations(mock_env_manager)
    
    def test_bulk_set_variables(self, env_operations, mock_env_manager):
        """Test bulk setting variables."""
        mock_env = Environment(name='test-env', variables={'OLD_VAR': 'old_value'})
        mock_env_manager.environment_exists.return_value = True
        mock_env_manager.load_environment.return_value = mock_env
        mock_env_manager.env_ops.save_environment.return_value = True
        
        variables = {
            'NEW_VAR': 'new_value',
            'OLD_VAR': 'updated_value',
            'ANOTHER_VAR': 'another_value'
        }
        
        result = env_operations.bulk_set_variables('test-env', variables, overwrite=True)
        
        assert result['success'] is True
        assert result['added_count'] == 2  # NEW_VAR, ANOTHER_VAR
        assert result['updated_count'] == 1  # OLD_VAR
        assert result['skipped_count'] == 0
    
    def test_bulk_delete_variables(self, env_operations, mock_env_manager):
        """Test bulk deleting variables."""
        mock_env = Environment(
            name='test-env', 
            variables={'VAR1': 'value1', 'VAR2': 'value2', 'VAR3': 'value3'}
        )
        mock_env_manager.load_environment.return_value = mock_env
        mock_env_manager.env_ops.save_environment.return_value = True
        
        keys_to_delete = ['VAR1', 'VAR3', 'MISSING_VAR']
        
        result = env_operations.bulk_delete_variables('test-env', keys_to_delete)
        
        assert result['success'] is True
        assert result['deleted_count'] == 2  # VAR1, VAR3
        assert result['missing_count'] == 1  # MISSING_VAR
    
    def test_search_variables(self, env_operations, mock_env_manager):
        """Test searching variables across environments."""
        mock_env_manager.list_environments.return_value = [
            {'name': 'env1'}, {'name': 'env2'}
        ]
        
        def mock_list_variables(env_name, include_values=True):
            if env_name == 'env1':
                return {'variables': {'API_KEY': 'key1', 'BASE_URL': 'url1'}}
            else:
                return {'variables': {'API_SECRET': 'secret2', 'API_KEY': 'key2'}}
        
        mock_env_manager.list_variables.side_effect = mock_list_variables
        
        results = env_operations.search_variables('API', search_keys=True)
        
        assert len(results) == 3  # API_KEY from both envs, API_SECRET from env2
        assert all('API' in result['key'] for result in results)
    
    def test_compare_environments(self, env_operations, mock_env_manager):
        """Test comparing two environments."""
        env1 = Environment(
            name='env1',
            variables={'SAME_VAR': 'same_value', 'DIFF_VAR': 'value1', 'ONLY_ENV1': 'value'}
        )
        env2 = Environment(
            name='env2',
            variables={'SAME_VAR': 'same_value', 'DIFF_VAR': 'value2', 'ONLY_ENV2': 'value'}
        )
        
        mock_env_manager.load_environment.side_effect = [env1, env2]
        
        result = env_operations.compare_environments('env1', 'env2')
        
        assert result['same_count'] == 1  # SAME_VAR
        assert result['different_count'] == 1  # DIFF_VAR
        assert result['only_in_env1_count'] == 1  # ONLY_ENV1
        assert result['only_in_env2_count'] == 1  # ONLY_ENV2
        assert result['similarity_percentage'] == 25.0  # 1 same out of 4 total
    
    def test_export_environments(self, env_operations, mock_env_manager):
        """Test exporting environments."""
        mock_env_manager.list_environments.return_value = [
            {'name': 'env1'}, {'name': 'env2'}
        ]
        
        def mock_export_env(name, include_sensitive):
            return {
                'name': name,
                'variables': {'VAR1': 'value1'},
                'exported_at': '2023-01-01T00:00:00'
            }
        
        mock_env_manager.export_environment.side_effect = mock_export_env
        
        result = env_operations.export_environments(format_type='json')
        
        assert isinstance(result, str)
        data = json.loads(result)
        assert 'export_info' in data
        assert 'environments' in data
        assert len(data['environments']) == 2
    
    def test_import_environments(self, env_operations, mock_env_manager):
        """Test importing environments."""
        import_data = {
            'environments': {
                'env1': {
                    'name': 'env1',
                    'variables': {'VAR1': 'value1'},
                    'description': 'Test environment'
                },
                'env2': {
                    'name': 'env2',
                    'variables': {'VAR2': 'value2'},
                    'description': 'Another test environment'
                }
            }
        }
        
        mock_env_manager.environment_exists.return_value = False
        mock_env_manager.import_environment.return_value = Mock()
        
        json_data = json.dumps(import_data)
        result = env_operations.import_environments(json_data, 'json')
        
        assert result['success'] is True
        assert result['imported_count'] == 2
        assert result['error_count'] == 0
    
    def test_backup_environments(self, env_operations):
        """Test creating environment backup."""
        with patch.object(env_operations, 'export_environments') as mock_export:
            mock_export.return_value = '{"test": "data"}'
            
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_path = Path(temp_dir) / "backup.json"
                
                result_path = env_operations.backup_environments(backup_path)
                
                assert result_path.exists()
                assert result_path == backup_path
                content = result_path.read_text()
                assert content == '{"test": "data"}'
    
    def test_restore_environments(self, env_operations):
        """Test restoring environments from backup."""
        backup_data = {
            'environments': {
                'restored-env': {
                    'name': 'restored-env',
                    'variables': {'RESTORED_VAR': 'restored_value'}
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_path = Path(temp_dir) / "backup.json"
            backup_path.write_text(json.dumps(backup_data))
            
            with patch.object(env_operations, 'import_environments') as mock_import:
                mock_import.return_value = {'success': True, 'imported_count': 1}
                
                result = env_operations.restore_environments(backup_path)
                
                assert result['success'] is True
                mock_import.assert_called_once()
    
    def test_get_environment_statistics(self, env_operations, mock_env_manager):
        """Test getting environment statistics."""
        mock_env_manager.list_environments.return_value = [
            {
                'name': 'env1',
                'variable_count': 5,
                'age_days': 10
            },
            {
                'name': 'env2',
                'variable_count': 3,
                'age_days': 5
            }
        ]
        mock_env_manager.get_current_environment.return_value = 'env1'
        
        stats = env_operations.get_environment_statistics()
        
        assert stats['total_environments'] == 2
        assert stats['total_variables'] == 8
        assert stats['current_environment'] == 'env1'
        assert stats['average_variables_per_env'] == 4.0
        assert stats['largest_environment'] == 'env1'
        assert stats['oldest_environment'] == 'env1'
        assert stats['newest_environment'] == 'env2'
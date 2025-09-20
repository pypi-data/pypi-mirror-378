"""Environment operations for bulk management and advanced features."""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from .env_manager import EnvironmentManager, EnvironmentManagerError, EnvironmentNotFoundError
from ..storage.models import Environment


logger = logging.getLogger(__name__)


class EnvironmentOperationsError(Exception):
    """Raised when environment operations fail."""
    pass


class EnvironmentOperations:
    """Advanced environment operations for bulk management and import/export."""
    
    def __init__(self, env_manager: Optional[EnvironmentManager] = None):
        self.env_manager = env_manager or EnvironmentManager()
    
    def bulk_set_variables(self, env_name: str, variables: Dict[str, str],
                          overwrite: bool = True, create_backup: bool = True) -> Dict[str, Any]:
        """
        Set multiple variables in an environment at once.
        
        Args:
            env_name: Environment name
            variables: Dictionary of variables to set
            overwrite: Whether to overwrite existing variables
            create_backup: Whether to create backup before changes
            
        Returns:
            Dictionary with operation results
            
        Raises:
            EnvironmentOperationsError: If operation fails
        """
        try:
            # Create backup if requested
            backup_data = None
            if create_backup and self.env_manager.environment_exists(env_name):
                backup_data = self.env_manager.export_environment(env_name, include_sensitive=True)
            
            # Load existing environment or create new one
            if self.env_manager.environment_exists(env_name):
                environment = self.env_manager.load_environment(env_name)
            else:
                environment = self.env_manager.create_environment(env_name)
            
            # Track changes
            added_vars = []
            updated_vars = []
            skipped_vars = []
            
            # Set variables
            for key, value in variables.items():
                if key in environment.variables:
                    if overwrite:
                        old_value = environment.variables[key]
                        environment.set_variable(key, value)
                        updated_vars.append({
                            'key': key,
                            'old_value': old_value,
                            'new_value': value
                        })
                    else:
                        skipped_vars.append({
                            'key': key,
                            'reason': 'Variable already exists',
                            'existing_value': environment.variables[key]
                        })
                else:
                    environment.set_variable(key, value)
                    added_vars.append({
                        'key': key,
                        'value': value
                    })
            
            # Save environment
            success = self.env_manager.env_ops.save_environment(environment)
            if not success:
                raise EnvironmentOperationsError(f"Failed to save environment '{env_name}'")
            
            result = {
                'success': True,
                'environment': env_name,
                'added_count': len(added_vars),
                'updated_count': len(updated_vars),
                'skipped_count': len(skipped_vars),
                'added_variables': added_vars,
                'updated_variables': updated_vars,
                'skipped_variables': skipped_vars,
                'backup_created': backup_data is not None,
                'backup_data': backup_data
            }
            
            logger.info(f"Bulk set {len(variables)} variables in environment '{env_name}': "
                       f"{len(added_vars)} added, {len(updated_vars)} updated, {len(skipped_vars)} skipped")
            
            return result
            
        except Exception as e:
            if isinstance(e, EnvironmentOperationsError):
                raise
            raise EnvironmentOperationsError(f"Bulk variable set failed: {e}")
    
    def bulk_delete_variables(self, env_name: str, variable_keys: List[str],
                            ignore_missing: bool = True) -> Dict[str, Any]:
        """
        Delete multiple variables from an environment.
        
        Args:
            env_name: Environment name
            variable_keys: List of variable keys to delete
            ignore_missing: Whether to ignore missing variables
            
        Returns:
            Dictionary with operation results
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentOperationsError: If operation fails
        """
        try:
            environment = self.env_manager.load_environment(env_name)
            
            deleted_vars = []
            missing_vars = []
            
            for key in variable_keys:
                if key in environment.variables:
                    old_value = environment.variables[key]
                    success = environment.delete_variable(key)
                    if success:
                        deleted_vars.append({
                            'key': key,
                            'old_value': old_value
                        })
                else:
                    missing_vars.append(key)
                    if not ignore_missing:
                        raise EnvironmentOperationsError(f"Variable '{key}' not found in environment '{env_name}'")
            
            # Save environment if any changes were made
            if deleted_vars:
                success = self.env_manager.env_ops.save_environment(environment)
                if not success:
                    raise EnvironmentOperationsError(f"Failed to save environment '{env_name}'")
            
            result = {
                'success': True,
                'environment': env_name,
                'deleted_count': len(deleted_vars),
                'missing_count': len(missing_vars),
                'deleted_variables': deleted_vars,
                'missing_variables': missing_vars
            }
            
            logger.info(f"Bulk deleted {len(deleted_vars)} variables from environment '{env_name}'")
            return result
            
        except (EnvironmentNotFoundError, EnvironmentOperationsError):
            raise
        except Exception as e:
            raise EnvironmentOperationsError(f"Bulk variable deletion failed: {e}")
    
    def search_variables(self, query: str, environments: Optional[List[str]] = None,
                        search_keys: bool = True, search_values: bool = False,
                        case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search for variables across environments.
        
        Args:
            query: Search query
            environments: List of environments to search (None for all)
            search_keys: Whether to search in variable keys
            search_values: Whether to search in variable values
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of matching variables with environment info
            
        Raises:
            EnvironmentOperationsError: If search fails
        """
        try:
            if not query.strip():
                return []
            
            search_query = query if case_sensitive else query.lower()
            
            # Get environments to search
            if environments is None:
                env_list = self.env_manager.list_environments()
                environments = [env['name'] for env in env_list]
            
            results = []
            
            for env_name in environments:
                try:
                    env_vars = self.env_manager.list_variables(env_name, include_values=search_values)
                    
                    for key, value in env_vars.get('variables', {}).items():
                        match_found = False
                        match_type = []
                        
                        # Search in key
                        if search_keys:
                            search_key = key if case_sensitive else key.lower()
                            if search_query in search_key:
                                match_found = True
                                match_type.append('key')
                        
                        # Search in value
                        if search_values and isinstance(value, str):
                            search_value = value if case_sensitive else value.lower()
                            if search_query in search_value:
                                match_found = True
                                match_type.append('value')
                        
                        if match_found:
                            results.append({
                                'environment': env_name,
                                'key': key,
                                'value': value if search_values else '***',
                                'match_type': match_type
                            })
                
                except Exception as e:
                    logger.warning(f"Error searching environment '{env_name}': {e}")
                    continue
            
            # Sort results by environment, then by key
            results.sort(key=lambda x: (x['environment'], x['key']))
            
            logger.debug(f"Variable search for '{query}' found {len(results)} matches")
            return results
            
        except Exception as e:
            raise EnvironmentOperationsError(f"Variable search failed: {e}")
    
    def compare_environments(self, env1_name: str, env2_name: str) -> Dict[str, Any]:
        """
        Compare variables between two environments.
        
        Args:
            env1_name: First environment name
            env2_name: Second environment name
            
        Returns:
            Dictionary with comparison results
            
        Raises:
            EnvironmentNotFoundError: If either environment doesn't exist
            EnvironmentOperationsError: If comparison fails
        """
        try:
            env1 = self.env_manager.load_environment(env1_name)
            env2 = self.env_manager.load_environment(env2_name)
            
            env1_vars = env1.variables
            env2_vars = env2.variables
            
            # Find differences
            only_in_env1 = []
            only_in_env2 = []
            different_values = []
            same_values = []
            
            all_keys = set(env1_vars.keys()) | set(env2_vars.keys())
            
            for key in all_keys:
                if key in env1_vars and key in env2_vars:
                    if env1_vars[key] == env2_vars[key]:
                        same_values.append({
                            'key': key,
                            'value': env1_vars[key]
                        })
                    else:
                        different_values.append({
                            'key': key,
                            'env1_value': env1_vars[key],
                            'env2_value': env2_vars[key]
                        })
                elif key in env1_vars:
                    only_in_env1.append({
                        'key': key,
                        'value': env1_vars[key]
                    })
                else:
                    only_in_env2.append({
                        'key': key,
                        'value': env2_vars[key]
                    })
            
            result = {
                'env1': env1_name,
                'env2': env2_name,
                'total_keys': len(all_keys),
                'same_count': len(same_values),
                'different_count': len(different_values),
                'only_in_env1_count': len(only_in_env1),
                'only_in_env2_count': len(only_in_env2),
                'same_variables': same_values,
                'different_variables': different_values,
                'only_in_env1': only_in_env1,
                'only_in_env2': only_in_env2,
                'similarity_percentage': (len(same_values) / len(all_keys) * 100) if all_keys else 100
            }
            
            logger.info(f"Compared environments '{env1_name}' and '{env2_name}': "
                       f"{result['similarity_percentage']:.1f}% similarity")
            
            return result
            
        except (EnvironmentNotFoundError, EnvironmentOperationsError):
            raise
        except Exception as e:
            raise EnvironmentOperationsError(f"Environment comparison failed: {e}")
    
    def export_environments(self, env_names: Optional[List[str]] = None,
                          format_type: str = 'json', include_sensitive: bool = False,
                          pretty_print: bool = True) -> str:
        """
        Export multiple environments to JSON or YAML format.
        
        Args:
            env_names: List of environment names to export (None for all)
            format_type: Export format ('json' or 'yaml')
            include_sensitive: Whether to include sensitive variables
            pretty_print: Whether to format output for readability
            
        Returns:
            Exported data as string
            
        Raises:
            EnvironmentOperationsError: If export fails
        """
        try:
            if format_type not in ['json', 'yaml', 'yml']:
                raise EnvironmentOperationsError(f"Unsupported format: {format_type}")
            
            # Get environments to export
            if env_names is None:
                env_list = self.env_manager.list_environments()
                env_names = [env['name'] for env in env_list]
            
            # Export environments
            exported_data = {
                'export_info': {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'exported_by': 'Agentic API Tester',
                    'environment_count': len(env_names),
                    'format': format_type,
                    'includes_sensitive': include_sensitive
                },
                'environments': {}
            }
            
            for env_name in env_names:
                try:
                    env_data = self.env_manager.export_environment(env_name, include_sensitive)
                    exported_data['environments'][env_name] = env_data
                except Exception as e:
                    logger.error(f"Failed to export environment '{env_name}': {e}")
                    continue
            
            # Format output
            if format_type == 'json':
                if pretty_print:
                    return json.dumps(exported_data, indent=2, ensure_ascii=False)
                else:
                    return json.dumps(exported_data, separators=(',', ':'), ensure_ascii=False)
            else:  # yaml
                if pretty_print:
                    return yaml.dump(exported_data, default_flow_style=False, indent=2,
                                   allow_unicode=True, sort_keys=False)
                else:
                    return yaml.dump(exported_data, default_flow_style=True, allow_unicode=True)
            
        except Exception as e:
            if isinstance(e, EnvironmentOperationsError):
                raise
            raise EnvironmentOperationsError(f"Environment export failed: {e}")
    
    def import_environments(self, data: str, format_type: str,
                          overwrite_existing: bool = False,
                          merge_variables: bool = False,
                          dry_run: bool = False) -> Dict[str, Any]:
        """
        Import multiple environments from JSON or YAML data.
        
        Args:
            data: Environment data as string
            format_type: Data format ('json' or 'yaml')
            overwrite_existing: Whether to overwrite existing environments
            merge_variables: Whether to merge variables with existing environments
            dry_run: If True, validate but don't actually import
            
        Returns:
            Dictionary with import results
            
        Raises:
            EnvironmentOperationsError: If import fails
        """
        try:
            if format_type not in ['json', 'yaml', 'yml']:
                raise EnvironmentOperationsError(f"Unsupported format: {format_type}")
            
            # Parse data
            if format_type == 'json':
                parsed_data = json.loads(data)
            else:
                parsed_data = yaml.safe_load(data)
            
            # Validate structure
            if not isinstance(parsed_data, dict) or 'environments' not in parsed_data:
                raise EnvironmentOperationsError("Invalid import data structure")
            
            environments_data = parsed_data['environments']
            
            # Import environments
            results = {
                'success': True,
                'imported_count': 0,
                'updated_count': 0,
                'skipped_count': 0,
                'error_count': 0,
                'errors': [],
                'imported_environments': [],
                'updated_environments': [],
                'skipped_environments': [],
                'dry_run': dry_run
            }
            
            for env_name, env_data in environments_data.items():
                try:
                    env_exists = self.env_manager.environment_exists(env_name)
                    
                    if env_exists and not overwrite_existing and not merge_variables:
                        results['skipped_count'] += 1
                        results['skipped_environments'].append({
                            'name': env_name,
                            'reason': 'Environment already exists'
                        })
                        continue
                    
                    if not dry_run:
                        if env_exists and merge_variables:
                            # Merge with existing environment
                            existing_env = self.env_manager.load_environment(env_name)
                            new_variables = env_data.get('variables', {})
                            
                            # Update existing variables
                            for key, value in new_variables.items():
                                existing_env.set_variable(key, value)
                            
                            # Update description if provided
                            if env_data.get('description'):
                                existing_env.description = env_data['description']
                            
                            self.env_manager.env_ops.save_environment(existing_env)
                            
                            results['updated_count'] += 1
                            results['updated_environments'].append({
                                'name': env_name,
                                'variables_added': len(new_variables)
                            })
                        else:
                            # Import as new environment
                            imported_env = self.env_manager.import_environment(env_data, overwrite_existing)
                            
                            results['imported_count'] += 1
                            results['imported_environments'].append({
                                'name': env_name,
                                'variables_count': len(imported_env.variables),
                                'overwritten': env_exists
                            })
                    else:
                        # Dry run - just validate
                        if env_exists and merge_variables:
                            results['updated_count'] += 1
                        else:
                            results['imported_count'] += 1
                
                except Exception as e:
                    results['error_count'] += 1
                    results['errors'].append({
                        'environment': env_name,
                        'error': str(e)
                    })
                    logger.error(f"Failed to import environment '{env_name}': {e}")
            
            results['success'] = results['error_count'] == 0
            
            if dry_run:
                logger.info(f"Dry run completed: {results['imported_count']} would be imported, "
                           f"{results['updated_count']} would be updated")
            else:
                logger.info(f"Import completed: {results['imported_count']} imported, "
                           f"{results['updated_count']} updated, {results['skipped_count']} skipped, "
                           f"{results['error_count']} errors")
            
            return results
            
        except Exception as e:
            if isinstance(e, EnvironmentOperationsError):
                raise
            raise EnvironmentOperationsError(f"Environment import failed: {e}")
    
    def backup_environments(self, backup_path: Optional[Union[str, Path]] = None,
                          env_names: Optional[List[str]] = None,
                          include_sensitive: bool = True) -> Path:
        """
        Create backup of environments.
        
        Args:
            backup_path: Path for backup file (auto-generated if None)
            env_names: List of environments to backup (None for all)
            include_sensitive: Whether to include sensitive variables
            
        Returns:
            Path to backup file
            
        Raises:
            EnvironmentOperationsError: If backup fails
        """
        try:
            # Generate backup path if not provided
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = Path.cwd() / f"env_backup_{timestamp}.json"
            else:
                backup_path = Path(backup_path)
            
            # Export environments
            exported_data = self.export_environments(
                env_names=env_names,
                format_type='json',
                include_sensitive=include_sensitive,
                pretty_print=True
            )
            
            # Ensure backup directory exists
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(exported_data)
            
            logger.info(f"Created environment backup at {backup_path}")
            return backup_path
            
        except Exception as e:
            raise EnvironmentOperationsError(f"Environment backup failed: {e}")
    
    def restore_environments(self, backup_path: Union[str, Path],
                           overwrite_existing: bool = False,
                           selective_restore: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Restore environments from backup.
        
        Args:
            backup_path: Path to backup file
            overwrite_existing: Whether to overwrite existing environments
            selective_restore: List of specific environments to restore (None for all)
            
        Returns:
            Dictionary with restore results
            
        Raises:
            EnvironmentOperationsError: If restore fails
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise EnvironmentOperationsError(f"Backup file not found: {backup_path}")
            
            # Read backup file
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            
            # Determine format from file extension
            format_type = 'yaml' if backup_path.suffix.lower() in ['.yaml', '.yml'] else 'json'
            
            # Filter environments if selective restore
            if selective_restore:
                if format_type == 'json':
                    parsed_data = json.loads(backup_data)
                else:
                    parsed_data = yaml.safe_load(backup_data)
                
                # Filter environments
                filtered_envs = {name: data for name, data in parsed_data['environments'].items()
                               if name in selective_restore}
                parsed_data['environments'] = filtered_envs
                
                # Re-serialize
                if format_type == 'json':
                    backup_data = json.dumps(parsed_data, indent=2)
                else:
                    backup_data = yaml.dump(parsed_data, default_flow_style=False, indent=2)
            
            # Import environments
            results = self.import_environments(
                data=backup_data,
                format_type=format_type,
                overwrite_existing=overwrite_existing,
                merge_variables=False,
                dry_run=False
            )
            
            logger.info(f"Restored environments from backup {backup_path}")
            return results
            
        except Exception as e:
            if isinstance(e, EnvironmentOperationsError):
                raise
            raise EnvironmentOperationsError(f"Environment restore failed: {e}")
    
    def get_environment_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all environments.
        
        Returns:
            Dictionary with environment statistics
        """
        try:
            env_list = self.env_manager.list_environments(include_metadata=True)
            current_env = self.env_manager.get_current_environment()
            
            total_envs = len(env_list)
            total_vars = 0
            oldest_env = None
            newest_env = None
            largest_env = None
            
            env_ages = []
            var_counts = []
            
            for env_info in env_list:
                if 'variable_count' in env_info:
                    var_count = env_info['variable_count']
                    total_vars += var_count
                    var_counts.append(var_count)
                    
                    # Track largest environment
                    if largest_env is None or var_count > largest_env['variable_count']:
                        largest_env = env_info
                
                if 'age_days' in env_info:
                    age = env_info['age_days']
                    env_ages.append(age)
                    
                    # Track oldest and newest
                    if oldest_env is None or age > oldest_env['age_days']:
                        oldest_env = env_info
                    if newest_env is None or age < newest_env['age_days']:
                        newest_env = env_info
            
            stats = {
                'total_environments': total_envs,
                'total_variables': total_vars,
                'current_environment': current_env,
                'average_variables_per_env': total_vars / total_envs if total_envs > 0 else 0,
                'largest_environment': largest_env['name'] if largest_env else None,
                'largest_environment_size': largest_env['variable_count'] if largest_env else 0,
                'oldest_environment': oldest_env['name'] if oldest_env else None,
                'oldest_environment_age_days': oldest_env['age_days'] if oldest_env else 0,
                'newest_environment': newest_env['name'] if newest_env else None,
                'newest_environment_age_days': newest_env['age_days'] if newest_env else 0,
                'environments': env_list
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get environment statistics: {e}")
            return {
                'total_environments': 0,
                'total_variables': 0,
                'current_environment': 'unknown',
                'error': str(e)
            }
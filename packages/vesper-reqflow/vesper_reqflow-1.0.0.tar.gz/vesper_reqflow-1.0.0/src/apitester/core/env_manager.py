"""Environment variable manager for managing different environments."""

import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime

from ..storage.operations import EnvironmentOperations
from ..storage.models import Environment


logger = logging.getLogger(__name__)


class EnvironmentManagerError(Exception):
    """Base exception for environment manager errors."""
    pass


class EnvironmentNotFoundError(EnvironmentManagerError):
    """Raised when environment is not found."""
    pass


class EnvironmentValidationError(EnvironmentManagerError):
    """Raised when environment validation fails."""
    pass


class EnvironmentManager:
    """Manages environment variables across different environments (dev/staging/prod)."""
    
    def __init__(self):
        self.env_ops = EnvironmentOperations()
        self.reserved_names = {'system', 'global', 'config', 'admin', 'root'}
    
    def create_environment(self, name: str, description: str = "",
                          variables: Optional[Dict[str, str]] = None,
                          set_as_current: bool = False) -> Environment:
        """
        Create a new environment.
        
        Args:
            name: Environment name
            description: Environment description
            variables: Initial variables
            set_as_current: Whether to set as current environment
            
        Returns:
            Created Environment instance
            
        Raises:
            EnvironmentValidationError: If environment data is invalid
            EnvironmentManagerError: If environment already exists or creation fails
        """
        try:
            # Validate environment name
            self._validate_environment_name(name)
            
            # Check if environment already exists
            if self.environment_exists(name):
                raise EnvironmentManagerError(f"Environment '{name}' already exists")
            
            # Create environment
            environment = Environment(
                name=name,
                variables=variables or {},
                description=description,
                is_active=set_as_current,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Validate environment
            validation_errors = environment.validate()
            if validation_errors:
                raise EnvironmentValidationError(f"Environment validation failed: {'; '.join(validation_errors)}")
            
            # Save environment
            success = self.env_ops.save_environment(environment)
            if not success:
                raise EnvironmentManagerError(f"Failed to save environment '{name}'")
            
            # Set as current if requested
            if set_as_current:
                self.set_current_environment(name)
            
            logger.info(f"Created environment '{name}' with {len(environment.variables)} variables")
            return environment
            
        except (EnvironmentValidationError, EnvironmentManagerError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to create environment '{name}': {e}")
    
    def load_environment(self, name: str) -> Environment:
        """
        Load an environment by name.
        
        Args:
            name: Environment name
            
        Returns:
            Environment instance
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentManagerError: If loading fails
        """
        try:
            environment = self.env_ops.load_environment(name)
            if environment is None:
                raise EnvironmentNotFoundError(f"Environment '{name}' not found")
            
            logger.debug(f"Loaded environment '{name}' with {len(environment.variables)} variables")
            return environment
            
        except EnvironmentNotFoundError:
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to load environment '{name}': {e}")
    
    def list_environments(self, include_metadata: bool = False) -> List[str]:
        """
        List all environments with optional metadata.
        
        Args:
            include_metadata: Whether to include detailed metadata
            
        Returns:
            List of environment information dictionaries
            
        Raises:
            EnvironmentManagerError: If listing fails
        """
        try:
            env_names = self.env_ops.list_environments()
            return env_names
            
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to list environments: {e}")
    
    def delete_environment(self, name: str, force: bool = False) -> bool:
        """
        Delete an environment.
        
        Args:
            name: Environment name
            force: Whether to force deletion of current environment
            
        Returns:
            True if environment was deleted
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentManagerError: If deletion fails or environment is current
        """
        try:
            # Check if environment exists
            if not self.environment_exists(name):
                raise EnvironmentNotFoundError(f"Environment '{name}' not found")
            
            # Check if it's the current environment
            current_env = self.get_current_environment()
            if name == current_env and not force:
                raise EnvironmentManagerError(
                    f"Cannot delete current environment '{name}'. "
                    f"Switch to another environment first or use force=True"
                )
            
            # Delete environment
            success = self.env_ops.delete_environment(name)
            
            if success:
                logger.info(f"Deleted environment '{name}'")
                
                # If we deleted the current environment, switch to default
                if name == current_env:
                    try:
                        self.set_current_environment("default")
                    except Exception:
                        # If default doesn't exist, create it
                        self.create_environment("default", "Default environment", set_as_current=True)
            
            return success
            
        except (EnvironmentNotFoundError, EnvironmentManagerError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to delete environment '{name}': {e}")
    
    def set_variable(self, env_name: str, key: str, value: str,
                    create_env_if_missing: bool = True) -> bool:
        """
        Set a variable in an environment.
        
        Args:
            env_name: Environment name
            key: Variable key
            value: Variable value
            create_env_if_missing: Whether to create environment if it doesn't exist
            
        Returns:
            True if variable was set
            
        Raises:
            EnvironmentValidationError: If variable key/value is invalid
            EnvironmentNotFoundError: If environment doesn't exist and create_env_if_missing=False
            EnvironmentManagerError: If setting fails
        """
        try:
            # Validate variable key and value
            self._validate_variable_key(key)
            self._validate_variable_value(value)
            
            # Check if environment exists
            if not self.environment_exists(env_name):
                if create_env_if_missing:
                    self.create_environment(env_name, f"Auto-created environment for {env_name}")
                else:
                    raise EnvironmentNotFoundError(f"Environment '{env_name}' not found")
            
            # Set variable
            success = self.env_ops.set_variable(env_name, key, value)
            if success:
                logger.debug(f"Set variable '{key}' in environment '{env_name}'")
            
            return success
            
        except (EnvironmentValidationError, EnvironmentNotFoundError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to set variable '{key}' in environment '{env_name}': {e}")
    
    def get_variable(self, env_name: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a variable from an environment.
        
        Args:
            env_name: Environment name
            key: Variable key
            default: Default value if variable not found
            
        Returns:
            Variable value or default
        """
        try:
            value = self.env_ops.get_variable(env_name, key)
            return value if value is not None else default
        except Exception as e:
            logger.error(f"Failed to get variable '{key}' from environment '{env_name}': {e}")
            return default
    
    def delete_variable(self, env_name: str, key: str) -> bool:
        """
        Delete a variable from an environment.
        
        Args:
            env_name: Environment name
            key: Variable key
            
        Returns:
            True if variable was deleted
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentManagerError: If deletion fails
        """
        try:
            if not self.environment_exists(env_name):
                raise EnvironmentNotFoundError(f"Environment '{env_name}' not found")
            
            success = self.env_ops.delete_variable(env_name, key)
            if success:
                logger.debug(f"Deleted variable '{key}' from environment '{env_name}'")
            
            return success
            
        except EnvironmentNotFoundError:
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to delete variable '{key}' from environment '{env_name}': {e}")
    
    def list_variables(self, env_name: str, include_values: bool = True) -> Dict[str, Any]:
        """
        List variables in an environment.
        
        Args:
            env_name: Environment name
            include_values: Whether to include variable values (for security)
            
        Returns:
            Dictionary with variable information
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentManagerError: If listing fails
        """
        try:
            environment = self.load_environment(env_name)
            
            result = {
                'environment': env_name,
                'variable_count': len(environment.variables),
                'variables': {}
            }
            
            for key, value in environment.variables.items():
                if include_values:
                    result['variables'][key] = value
                else:
                    # Mask sensitive values
                    if self._is_sensitive_key(key):
                        result['variables'][key] = "***"
                    else:
                        result['variables'][key] = value
            
            return result
            
        except EnvironmentNotFoundError:
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to list variables for environment '{env_name}': {e}")
    
    def get_current_environment(self) -> str:
        """
        Get the name of the current active environment.
        
        Returns:
            Current environment name
        """
        try:
            return self.env_ops.get_current_environment()
        except Exception as e:
            logger.error(f"Failed to get current environment: {e}")
            return "default"
    
    def set_current_environment(self, env_name: str) -> bool:
        """
        Set the current active environment.
        
        Args:
            env_name: Environment name to set as current
            
        Returns:
            True if environment was set as current
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
            EnvironmentManagerError: If setting fails
        """
        try:
            if not self.environment_exists(env_name):
                raise EnvironmentNotFoundError(f"Environment '{env_name}' not found")
            
            success = self.env_ops.set_current_environment(env_name)
            if success:
                logger.info(f"Set current environment to '{env_name}'")
            
            return success
            
        except EnvironmentNotFoundError:
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to set current environment to '{env_name}': {e}")
    
    def environment_exists(self, name: str) -> bool:
        """
        Check if an environment exists.
        
        Args:
            name: Environment name
            
        Returns:
            True if environment exists
        """
        try:
            environment = self.env_ops.load_environment(name)
            return environment is not None
        except Exception:
            return False
    
    def copy_environment(self, source_name: str, target_name: str,
                        include_variables: bool = True,
                        overwrite: bool = False) -> Environment:
        """
        Copy an environment to a new environment.
        
        Args:
            source_name: Source environment name
            target_name: Target environment name
            include_variables: Whether to copy variables
            overwrite: Whether to overwrite existing target environment
            
        Returns:
            Created target environment
            
        Raises:
            EnvironmentNotFoundError: If source environment doesn't exist
            EnvironmentManagerError: If target exists and overwrite=False or copy fails
        """
        try:
            # Load source environment
            source_env = self.load_environment(source_name)
            
            # Check if target exists
            if self.environment_exists(target_name) and not overwrite:
                raise EnvironmentManagerError(f"Target environment '{target_name}' already exists")
            
            # Create target environment
            target_variables = source_env.variables.copy() if include_variables else {}
            
            target_env = Environment(
                name=target_name,
                variables=target_variables,
                description=f"Copy of {source_name}: {source_env.description}",
                is_active=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save target environment
            success = self.env_ops.save_environment(target_env)
            if not success:
                raise EnvironmentManagerError(f"Failed to save copied environment '{target_name}'")
            
            logger.info(f"Copied environment '{source_name}' to '{target_name}' "
                       f"with {len(target_variables)} variables")
            return target_env
            
        except (EnvironmentNotFoundError, EnvironmentManagerError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to copy environment: {e}")
    
    def merge_environments(self, target_name: str, source_names: List[str],
                          conflict_resolution: str = "target") -> Environment:
        """
        Merge multiple environments into a target environment.
        
        Args:
            target_name: Target environment name
            source_names: List of source environment names
            conflict_resolution: How to resolve conflicts ("target", "source", "error")
            
        Returns:
            Updated target environment
            
        Raises:
            EnvironmentNotFoundError: If any environment doesn't exist
            EnvironmentManagerError: If merge fails or conflicts occur
        """
        try:
            # Load target environment
            target_env = self.load_environment(target_name)
            
            # Track conflicts
            conflicts = []
            
            # Merge each source environment
            for source_name in source_names:
                source_env = self.load_environment(source_name)
                
                for key, value in source_env.variables.items():
                    if key in target_env.variables:
                        if target_env.variables[key] != value:
                            conflicts.append({
                                'key': key,
                                'target_value': target_env.variables[key],
                                'source_value': value,
                                'source_env': source_name
                            })
                            
                            # Apply conflict resolution
                            if conflict_resolution == "source":
                                target_env.variables[key] = value
                            elif conflict_resolution == "error":
                                raise EnvironmentManagerError(
                                    f"Conflict for variable '{key}': "
                                    f"target='{target_env.variables[key]}', "
                                    f"source='{value}' from '{source_name}'"
                                )
                            # "target" keeps existing value
                    else:
                        target_env.variables[key] = value
            
            # Update timestamp
            target_env.update_timestamp()
            
            # Save merged environment
            success = self.env_ops.save_environment(target_env)
            if not success:
                raise EnvironmentManagerError(f"Failed to save merged environment '{target_name}'")
            
            logger.info(f"Merged {len(source_names)} environments into '{target_name}' "
                       f"with {len(conflicts)} conflicts resolved")
            return target_env
            
        except (EnvironmentNotFoundError, EnvironmentManagerError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to merge environments: {e}")
    
    def export_environment(self, env_name: str, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Export environment to dictionary format.
        
        Args:
            env_name: Environment name
            include_sensitive: Whether to include sensitive variables
            
        Returns:
            Environment data dictionary
            
        Raises:
            EnvironmentNotFoundError: If environment doesn't exist
        """
        try:
            environment = self.load_environment(env_name)
            
            variables = {}
            for key, value in environment.variables.items():
                if include_sensitive or not self._is_sensitive_key(key):
                    variables[key] = value
                else:
                    variables[key] = "***SENSITIVE***"
            
            return {
                'name': environment.name,
                'description': environment.description,
                'variables': variables,
                'created_at': environment.created_at.isoformat(),
                'updated_at': environment.updated_at.isoformat(),
                'exported_at': datetime.now().isoformat()
            }
            
        except EnvironmentNotFoundError:
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to export environment '{env_name}': {e}")
    
    def import_environment(self, data: Dict[str, Any], overwrite: bool = False) -> Environment:
        """
        Import environment from dictionary format.
        
        Args:
            data: Environment data dictionary
            overwrite: Whether to overwrite existing environment
            
        Returns:
            Imported environment
            
        Raises:
            EnvironmentValidationError: If import data is invalid
            EnvironmentManagerError: If import fails
        """
        try:
            # Validate import data
            if not isinstance(data, dict) or 'name' not in data:
                raise EnvironmentValidationError("Invalid environment import data")
            
            env_name = data['name']
            
            # Check if environment exists
            if self.environment_exists(env_name) and not overwrite:
                raise EnvironmentManagerError(f"Environment '{env_name}' already exists")
            
            # Create environment from data
            environment = Environment(
                name=env_name,
                description=data.get('description', ''),
                variables=data.get('variables', {}),
                is_active=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Validate environment
            validation_errors = environment.validate()
            if validation_errors:
                raise EnvironmentValidationError(f"Environment validation failed: {'; '.join(validation_errors)}")
            
            # Save environment
            success = self.env_ops.save_environment(environment)
            if not success:
                raise EnvironmentManagerError(f"Failed to save imported environment '{env_name}'")
            
            logger.info(f"Imported environment '{env_name}' with {len(environment.variables)} variables")
            return environment
            
        except (EnvironmentValidationError, EnvironmentManagerError):
            raise
        except Exception as e:
            raise EnvironmentManagerError(f"Failed to import environment: {e}")
    
    def _validate_environment_name(self, name: str) -> None:
        """Validate environment name."""
        if not name or not name.strip():
            raise EnvironmentValidationError("Environment name cannot be empty")
        
        name = name.strip()
        
        if len(name) > 50:
            raise EnvironmentValidationError("Environment name cannot exceed 50 characters")
        
        if not name.replace('-', '').replace('_', '').isalnum():
            raise EnvironmentValidationError("Environment name can only contain letters, numbers, hyphens, and underscores")
        
        if name.lower() in self.reserved_names:
            raise EnvironmentValidationError(f"Environment name '{name}' is reserved")
    
    def _validate_variable_key(self, key: str) -> None:
        """Validate variable key."""
        if not key or not key.strip():
            raise EnvironmentValidationError("Variable key cannot be empty")
        
        key = key.strip()
        
        if len(key) > 100:
            raise EnvironmentValidationError("Variable key cannot exceed 100 characters")
        
        if not key.replace('_', '').replace('-', '').isalnum():
            raise EnvironmentValidationError("Variable key can only contain letters, numbers, hyphens, and underscores")
    
    def _validate_variable_value(self, value: str) -> None:
        """Validate variable value."""
        if len(value) > 10000:
            raise EnvironmentValidationError("Variable value cannot exceed 10000 characters")
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if variable key contains sensitive information."""
        sensitive_patterns = [
            'password', 'passwd', 'pwd', 'secret', 'key', 'token', 'auth',
            'credential', 'private', 'secure', 'api_key', 'access_token'
        ]
        
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)
    
    def get_environment_variables(self, env_name: str) -> Dict[str, str]:
        """
        Get all variables from an environment.
        
        Args:
            env_name: Environment name
            
        Returns:
            Dictionary of variables
        """
        try:
            environment = self.load_environment(env_name)
            return environment.variables.copy()
        except Exception as e:
            logger.error(f"Failed to get variables for environment '{env_name}': {e}")
            return {}
    
    def variable_exists(self, env_name: str, key: str) -> bool:
        """
        Check if a variable exists in an environment.
        
        Args:
            env_name: Environment name
            key: Variable key
            
        Returns:
            True if variable exists
        """
        try:
            value = self.get_variable(env_name, key)
            return value is not None
        except Exception:
            return False
    
    def unset_variable(self, env_name: str, key: str) -> bool:
        """
        Remove a variable from an environment.
        
        Args:
            env_name: Environment name
            key: Variable key
            
        Returns:
            True if variable was removed
        """
        return self.delete_variable(env_name, key)
    
    def clear_environment(self, env_name: str) -> bool:
        """
        Clear all variables from an environment.
        
        Args:
            env_name: Environment name
            
        Returns:
            True if environment was cleared
        """
        try:
            environment = self.load_environment(env_name)
            environment.variables.clear()
            environment.update_timestamp()
            
            success = self.env_ops.save_environment(environment)
            if success:
                logger.info(f"Cleared all variables from environment '{env_name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear environment '{env_name}': {e}")
            return False
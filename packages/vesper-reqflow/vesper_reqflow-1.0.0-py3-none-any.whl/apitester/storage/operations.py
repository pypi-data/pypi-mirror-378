"""Redis operations for different data types with error handling."""

import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .redis_client import get_redis_client, RedisOperationError
from .models import (
    RequestTemplate, RequestRecord, Environment, CacheEntry,
    HTTPMethod, validate_http_method, validate_url
)
from ..config.settings import get_config


logger = logging.getLogger(__name__)


class TemplateOperations:
    """Redis operations for request templates."""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.key_prefix = "template:"
    
    def save_template(self, template: RequestTemplate) -> bool:
        """
        Save request template to Redis.
        
        Args:
            template: RequestTemplate instance
            
        Returns:
            bool: True if successful
            
        Raises:
            RedisOperationError: If Redis operation fails
        """
        try:
            # Validate template
            errors = template.validate()
            if errors:
                raise ValueError(f"Template validation failed: {', '.join(errors)}")
            
            # Update timestamp
            template.update_timestamp()
            
            # Store in Redis hash
            key = f"{self.key_prefix}{template.name}"
            data = template.to_dict()
            
            success = self.redis.set_hash(key, data)
            if success:
                logger.info(f"Saved template '{template.name}'")
            return success
            
        except Exception as e:
            logger.error(f"Failed to save template '{template.name}': {e}")
            raise RedisOperationError(f"Failed to save template: {e}")
    
    def load_template(self, name: str) -> Optional[RequestTemplate]:
        """
        Load request template from Redis.
        
        Args:
            name: Template name
            
        Returns:
            RequestTemplate or None if not found
        """
        try:
            key = f"{self.key_prefix}{name}"
            data = self.redis.get_hash(key)
            
            if not data:
                logger.debug(f"Template '{name}' not found")
                return None
            
            template = RequestTemplate.from_dict(data)
            logger.debug(f"Loaded template '{name}'")
            return template
            
        except Exception as e:
            logger.error(f"Failed to load template '{name}': {e}")
            raise RedisOperationError(f"Failed to load template: {e}")
    
    def list_templates(self) -> List[str]:
        """
        List all template names.
        
        Returns:
            List of template names
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.get_keys_pattern(pattern)
            
            # Extract template names from keys
            names = [key.replace(self.key_prefix, "") for key in keys]
            names.sort()
            
            logger.debug(f"Found {len(names)} templates")
            return names
            
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            raise RedisOperationError(f"Failed to list templates: {e}")
    
    def delete_template(self, name: str) -> bool:
        """
        Delete request template.
        
        Args:
            name: Template name
            
        Returns:
            bool: True if template was deleted
        """
        try:
            key = f"{self.key_prefix}{name}"
            success = self.redis.delete_key(key)
            
            if success:
                logger.info(f"Deleted template '{name}'")
            else:
                logger.debug(f"Template '{name}' not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete template '{name}': {e}")
            raise RedisOperationError(f"Failed to delete template: {e}")
    
    def template_exists(self, name: str) -> bool:
        """
        Check if template exists.
        
        Args:
            name: Template name
            
        Returns:
            bool: True if template exists
        """
        try:
            key = f"{self.key_prefix}{name}"
            return self.redis.exists(key)
        except Exception as e:
            logger.error(f"Failed to check template existence '{name}': {e}")
            return False
    
    def get_template_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all templates.
        
        Returns:
            List of template metadata dictionaries
        """
        try:
            templates = []
            names = self.list_templates()
            
            for name in names:
                template = self.load_template(name)
                if template:
                    templates.append({
                        'name': template.name,
                        'method': template.method.value,
                        'url': template.url,
                        'created_at': template.created_at.isoformat(),
                        'updated_at': template.updated_at.isoformat(),
                        'description': template.description,
                        'tags': template.tags,
                    })
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get template metadata: {e}")
            raise RedisOperationError(f"Failed to get template metadata: {e}")


class EnvironmentOperations:
    """Redis operations for environment variables."""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.key_prefix = "env:"
        self.config_key = "config:global"
    
    def save_environment(self, environment: Environment) -> bool:
        """
        Save environment to Redis.
        
        Args:
            environment: Environment instance
            
        Returns:
            bool: True if successful
        """
        try:
            # Validate environment
            errors = environment.validate()
            if errors:
                raise ValueError(f"Environment validation failed: {', '.join(errors)}")
            
            # Update timestamp
            environment.update_timestamp()
            
            # Store in Redis hash
            key = f"{self.key_prefix}{environment.name}"
            data = environment.to_dict()
            
            success = self.redis.set_hash(key, data)
            if success:
                logger.info(f"Saved environment '{environment.name}'")
            return success
            
        except Exception as e:
            logger.error(f"Failed to save environment '{environment.name}': {e}")
            raise RedisOperationError(f"Failed to save environment: {e}")
    
    def load_environment(self, name: str) -> Optional[Environment]:
        """
        Load environment from Redis.
        
        Args:
            name: Environment name
            
        Returns:
            Environment or None if not found
        """
        try:
            key = f"{self.key_prefix}{name}"
            data = self.redis.get_hash(key)
            
            if not data:
                logger.debug(f"Environment '{name}' not found")
                return None
            
            environment = Environment.from_dict(data)
            logger.debug(f"Loaded environment '{name}'")
            return environment
            
        except Exception as e:
            logger.error(f"Failed to load environment '{name}': {e}")
            raise RedisOperationError(f"Failed to load environment: {e}")
    
    def list_environments(self) -> List[str]:
        """
        List all environment names.
        
        Returns:
            List of environment names
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.get_keys_pattern(pattern)
            
            # Extract environment names from keys
            names = [key.replace(self.key_prefix, "") for key in keys]
            names.sort()
            
            logger.debug(f"Found {len(names)} environments")
            return names
            
        except Exception as e:
            logger.error(f"Failed to list environments: {e}")
            raise RedisOperationError(f"Failed to list environments: {e}")
    
    def delete_environment(self, name: str) -> bool:
        """
        Delete environment.
        
        Args:
            name: Environment name
            
        Returns:
            bool: True if environment was deleted
        """
        try:
            key = f"{self.key_prefix}{name}"
            success = self.redis.delete_key(key)
            
            if success:
                logger.info(f"Deleted environment '{name}'")
                
                # If this was the active environment, reset to default
                current_env = self.get_current_environment()
                if current_env == name:
                    self.set_current_environment("default")
            else:
                logger.debug(f"Environment '{name}' not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete environment '{name}': {e}")
            raise RedisOperationError(f"Failed to delete environment: {e}")
    
    def set_variable(self, env_name: str, key: str, value: str) -> bool:
        """
        Set environment variable.
        
        Args:
            env_name: Environment name
            key: Variable key
            value: Variable value
            
        Returns:
            bool: True if successful
        """
        try:
            # Load or create environment
            environment = self.load_environment(env_name)
            if not environment:
                environment = Environment(name=env_name)
            
            # Set variable
            environment.set_variable(key, value)
            
            # Save environment
            return self.save_environment(environment)
            
        except Exception as e:
            logger.error(f"Failed to set variable '{key}' in environment '{env_name}': {e}")
            raise RedisOperationError(f"Failed to set environment variable: {e}")
    
    def get_variable(self, env_name: str, key: str) -> Optional[str]:
        """
        Get environment variable.
        
        Args:
            env_name: Environment name
            key: Variable key
            
        Returns:
            Variable value or None if not found
        """
        try:
            environment = self.load_environment(env_name)
            if not environment:
                return None
            
            return environment.get_variable(key)
            
        except Exception as e:
            logger.error(f"Failed to get variable '{key}' from environment '{env_name}': {e}")
            return None
    
    def delete_variable(self, env_name: str, key: str) -> bool:
        """
        Delete environment variable.
        
        Args:
            env_name: Environment name
            key: Variable key
            
        Returns:
            bool: True if variable was deleted
        """
        try:
            environment = self.load_environment(env_name)
            if not environment:
                return False
            
            success = environment.delete_variable(key)
            if success:
                self.save_environment(environment)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete variable '{key}' from environment '{env_name}': {e}")
            raise RedisOperationError(f"Failed to delete environment variable: {e}")
    
    def get_current_environment(self) -> str:
        """
        Get current active environment name.
        
        Returns:
            Current environment name
        """
        try:
            config_data = self.redis.get_hash(self.config_key)
            return config_data.get('current_environment', 'default')
        except Exception:
            return 'default'
    
    def set_current_environment(self, env_name: str) -> bool:
        """
        Set current active environment.
        
        Args:
            env_name: Environment name
            
        Returns:
            bool: True if successful
        """
        try:
            # Get existing config or create new
            config_data = self.redis.get_hash(self.config_key) or {}
            config_data['current_environment'] = env_name
            
            success = self.redis.set_hash(self.config_key, config_data)
            if success:
                logger.info(f"Set current environment to '{env_name}'")
            return success
            
        except Exception as e:
            logger.error(f"Failed to set current environment to '{env_name}': {e}")
            raise RedisOperationError(f"Failed to set current environment: {e}")


class HistoryOperations:
    """Redis operations for request history."""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.key = "history"
        self.config = get_config()
    
    def add_request(self, record: RequestRecord) -> bool:
        """
        Add request record to history.
        
        Args:
            record: RequestRecord instance
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert to dictionary for storage
            data = record.to_dict()
            
            # Add to Redis list with size limit
            max_size = self.config.history.max_entries
            success = self.redis.push_to_list(self.key, data, max_size)
            
            if success:
                logger.debug(f"Added request to history: {record.method} {record.url}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to add request to history: {e}")
            raise RedisOperationError(f"Failed to add request to history: {e}")
    
    def get_history(self, limit: Optional[int] = None) -> List[RequestRecord]:
        """
        Get request history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of RequestRecord instances
        """
        try:
            # Use provided limit or config default
            if limit is None:
                limit = self.config.history.max_entries
            
            # Get records from Redis list
            data_list = self.redis.get_list(self.key, 0, limit - 1)
            
            # Convert to RequestRecord instances
            records = []
            for data in data_list:
                try:
                    record = RequestRecord.from_dict(data)
                    records.append(record)
                except Exception as e:
                    logger.warning(f"Failed to parse history record: {e}")
                    continue
            
            logger.debug(f"Retrieved {len(records)} history records")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            raise RedisOperationError(f"Failed to get history: {e}")
    
    def get_last_request(self) -> Optional[RequestRecord]:
        """
        Get the most recent request record.
        
        Returns:
            RequestRecord or None if no history
        """
        try:
            records = self.get_history(1)
            return records[0] if records else None
        except Exception as e:
            logger.error(f"Failed to get last request: {e}")
            return None
    
    def clear_history(self) -> bool:
        """
        Clear all request history.
        
        Returns:
            bool: True if successful
        """
        try:
            success = self.redis.delete_key(self.key)
            if success:
                logger.info("Cleared request history")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            raise RedisOperationError(f"Failed to clear history: {e}")
    
    def get_history_count(self) -> int:
        """
        Get total number of history records.
        
        Returns:
            Number of history records
        """
        try:
            return self.redis.get_list_length(self.key)
        except Exception as e:
            logger.error(f"Failed to get history count: {e}")
            return 0


class CacheOperations:
    """Redis operations for response caching."""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.key_prefix = "cache:"
        self.config = get_config()
    
    def generate_cache_key(self, method: str, url: str, headers: Dict[str, str]) -> str:
        """
        Generate cache key for request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            
        Returns:
            Cache key string
        """
        # Create a hash of the request parameters
        cache_data = f"{method.upper()}:{url}"
        
        # Include relevant headers in cache key
        relevant_headers = ['authorization', 'content-type', 'accept']
        for header in relevant_headers:
            if header in headers:
                cache_data += f":{header}:{headers[header]}"
        
        # Generate hash
        cache_hash = hashlib.md5(cache_data.encode()).hexdigest()
        return f"{self.key_prefix}{method.lower()}:{cache_hash}"
    
    def cache_response(self, method: str, url: str, headers: Dict[str, str], 
                      response_status: int, response_headers: Dict[str, str], 
                      response_body: str, ttl: Optional[int] = None) -> bool:
        """
        Cache API response.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            response_status: Response status code
            response_headers: Response headers
            response_body: Response body
            ttl: Time to live in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.config.cache.enabled:
                return False
            
            # Use provided TTL or config default
            if ttl is None:
                ttl = self.config.cache.default_ttl
            
            # Generate cache key
            cache_key = self.generate_cache_key(method, url, headers)
            
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                response_status=response_status,
                response_headers=response_headers,
                response_body=response_body,
                created_at=datetime.now(),
                ttl=ttl
            )
            
            # Store in Redis with TTL
            success = self.redis.set_with_ttl(cache_key, entry.to_dict(), ttl)
            
            if success:
                logger.debug(f"Cached response for {method} {url}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False  # Don't raise exception for cache failures
    
    def get_cached_response(self, method: str, url: str, 
                           headers: Dict[str, str]) -> Optional[Tuple[int, Dict[str, str], str, int]]:
        """
        Get cached response.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            
        Returns:
            Tuple of (status, headers, body, hit_count) or None if not cached
        """
        try:
            if not self.config.cache.enabled:
                return None
            
            # Generate cache key
            cache_key = self.generate_cache_key(method, url, headers)
            
            # Get from Redis
            data, ttl = self.redis.get_with_ttl(cache_key)
            if not data:
                return None
            
            # Parse cache entry
            entry = CacheEntry.from_dict(data)
            
            # Check if expired
            if entry.is_expired():
                # Remove expired entry
                self.redis.delete_key(cache_key)
                return None
            
            # Increment hit count and update cache
            entry.increment_hit_count()
            if ttl and ttl > 0:
                self.redis.set_with_ttl(cache_key, entry.to_dict(), ttl)
            
            logger.debug(f"Cache hit for {method} {url}")
            return (entry.response_status, entry.response_headers, 
                   entry.response_body, entry.hit_count)
            
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None  # Don't raise exception for cache failures
    
    def clear_cache(self) -> bool:
        """
        Clear all cached responses.
        
        Returns:
            bool: True if successful
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.get_keys_pattern(pattern)
            
            if not keys:
                return True
            
            # Delete all cache keys
            for key in keys:
                self.redis.delete_key(key)
            
            logger.info(f"Cleared {len(keys)} cached responses")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise RedisOperationError(f"Failed to clear cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.get_keys_pattern(pattern)
            
            total_entries = len(keys)
            total_hits = 0
            expired_entries = 0
            
            for key in keys:
                try:
                    data, ttl = self.redis.get_with_ttl(key)
                    if data:
                        entry = CacheEntry.from_dict(data)
                        total_hits += entry.hit_count
                        if entry.is_expired():
                            expired_entries += 1
                except Exception:
                    continue
            
            return {
                'total_entries': total_entries,
                'total_hits': total_hits,
                'expired_entries': expired_entries,
                'enabled': self.config.cache.enabled,
                'default_ttl': self.config.cache.default_ttl,
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'total_entries': 0,
                'total_hits': 0,
                'expired_entries': 0,
                'enabled': self.config.cache.enabled,
                'default_ttl': self.config.cache.default_ttl,
            }
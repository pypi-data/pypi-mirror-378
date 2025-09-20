"""Redis client with connection management and error handling."""

import redis
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager

from ..config.settings import get_config, RedisConfig


logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Raised when Redis connection fails."""
    pass


class RedisOperationError(Exception):
    """Raised when Redis operation fails."""
    pass


class RedisClient:
    """Redis client with connection management, retry logic, and error handling."""
    
    def __init__(self, config: Optional[RedisConfig] = None):
        """Initialize Redis client with configuration."""
        self.config = config or get_config().redis
        self._client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._last_health_check = 0
        self._is_connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Redis server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                db=self.config.database,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=True,  # Automatically decode responses to strings
                max_connections=20,
            )
            
            # Create Redis client
            self._client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            self._client.ping()
            self._is_connected = True
            self._last_health_check = time.time()
            
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            return True
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._is_connected = False
            raise RedisConnectionError(f"Cannot connect to Redis server: {e}")
        except redis.AuthenticationError as e:
            logger.error(f"Redis authentication failed: {e}")
            self._is_connected = False
            raise RedisConnectionError(f"Redis authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self._is_connected = False
            raise RedisConnectionError(f"Unexpected Redis connection error: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self._connection_pool:
            self._connection_pool.disconnect()
        self._client = None
        self._connection_pool = None
        self._is_connected = False
        logger.info("Disconnected from Redis")
    
    def is_connected(self) -> bool:
        """Check if client is connected to Redis."""
        return self._is_connected and self._client is not None
    
    def health_check(self) -> bool:
        """
        Perform health check on Redis connection.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        current_time = time.time()
        
        # Only check if enough time has passed since last check
        if current_time - self._last_health_check < self.config.health_check_interval:
            return self._is_connected
        
        try:
            if self._client:
                self._client.ping()
                self._is_connected = True
                self._last_health_check = current_time
                return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            self._is_connected = False
            return False
        
        return False
    
    def _ensure_connection(self) -> None:
        """Ensure Redis connection is active, reconnect if necessary."""
        if not self.is_connected() or not self.health_check():
            logger.info("Attempting to reconnect to Redis...")
            self.connect()
    
    @contextmanager
    def _handle_redis_errors(self, operation: str):
        """Context manager for handling Redis operation errors."""
        try:
            self._ensure_connection()
            yield
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error during {operation}: {e}")
            self._is_connected = False
            raise RedisOperationError(f"Connection lost during {operation}: {e}")
        except redis.TimeoutError as e:
            logger.error(f"Redis timeout during {operation}: {e}")
            raise RedisOperationError(f"Operation timed out during {operation}: {e}")
        except redis.ResponseError as e:
            logger.error(f"Redis response error during {operation}: {e}")
            raise RedisOperationError(f"Invalid response during {operation}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during {operation}: {e}")
            raise RedisOperationError(f"Unexpected error during {operation}: {e}")
    
    def set_hash(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Store dictionary data as Redis hash.
        
        Args:
            key: Redis key
            data: Dictionary to store
            
        Returns:
            bool: True if successful
        """
        with self._handle_redis_errors(f"set_hash({key})"):
            # Convert all values to JSON strings for consistent storage
            serialized_data = {k: json.dumps(v) if not isinstance(v, str) else v 
                             for k, v in data.items()}
            result = self._client.hset(key, mapping=serialized_data)
            logger.debug(f"Set hash {key} with {len(data)} fields")
            return True
    
    def get_hash(self, key: str) -> Dict[str, Any]:
        """
        Retrieve hash data from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            dict: Retrieved data, empty dict if key doesn't exist
        """
        with self._handle_redis_errors(f"get_hash({key})"):
            data = self._client.hgetall(key)
            if not data:
                return {}
            
            # Deserialize JSON values back to original types
            result = {}
            for k, v in data.items():
                try:
                    # Try to parse as JSON first
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, keep as string
                    result[k] = v
            
            logger.debug(f"Retrieved hash {key} with {len(result)} fields")
            return result
    
    def delete_hash_field(self, key: str, field: str) -> bool:
        """
        Delete a field from Redis hash.
        
        Args:
            key: Redis key
            field: Hash field to delete
            
        Returns:
            bool: True if field was deleted
        """
        with self._handle_redis_errors(f"delete_hash_field({key}, {field})"):
            result = self._client.hdel(key, field)
            logger.debug(f"Deleted field {field} from hash {key}")
            return result > 0
    
    def push_to_list(self, key: str, value: Any, max_size: Optional[int] = None) -> bool:
        """
        Push value to Redis list (FIFO queue).
        
        Args:
            key: Redis key
            value: Value to push
            max_size: Maximum list size, oldest items removed if exceeded
            
        Returns:
            bool: True if successful
        """
        with self._handle_redis_errors(f"push_to_list({key})"):
            # Serialize value to JSON
            serialized_value = json.dumps(value)
            
            # Push to list
            self._client.lpush(key, serialized_value)
            
            # Trim list if max_size specified
            if max_size and max_size > 0:
                self._client.ltrim(key, 0, max_size - 1)
            
            logger.debug(f"Pushed value to list {key}")
            return True
    
    def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Retrieve list data from Redis.
        
        Args:
            key: Redis key
            start: Start index (0-based)
            end: End index (-1 for all)
            
        Returns:
            list: Retrieved data
        """
        with self._handle_redis_errors(f"get_list({key})"):
            data = self._client.lrange(key, start, end)
            
            # Deserialize JSON values
            result = []
            for item in data:
                try:
                    result.append(json.loads(item))
                except (json.JSONDecodeError, TypeError):
                    result.append(item)
            
            logger.debug(f"Retrieved {len(result)} items from list {key}")
            return result
    
    def get_list_length(self, key: str) -> int:
        """
        Get length of Redis list.
        
        Args:
            key: Redis key
            
        Returns:
            int: List length
        """
        with self._handle_redis_errors(f"get_list_length({key})"):
            length = self._client.llen(key)
            return length
    
    def set_with_ttl(self, key: str, value: Any, ttl: int) -> bool:
        """
        Set key with TTL (time to live).
        
        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds
            
        Returns:
            bool: True if successful
        """
        with self._handle_redis_errors(f"set_with_ttl({key})"):
            serialized_value = json.dumps(value)
            result = self._client.setex(key, ttl, serialized_value)
            logger.debug(f"Set key {key} with TTL {ttl}s")
            return result
    
    def get_with_ttl(self, key: str) -> tuple[Any, Optional[int]]:
        """
        Get value and remaining TTL.
        
        Args:
            key: Redis key
            
        Returns:
            tuple: (value, ttl_seconds) or (None, None) if key doesn't exist
        """
        with self._handle_redis_errors(f"get_with_ttl({key})"):
            value = self._client.get(key)
            if value is None:
                return None, None
            
            ttl = self._client.ttl(key)
            
            # Deserialize value
            try:
                deserialized_value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                deserialized_value = value
            
            logger.debug(f"Retrieved key {key} with TTL {ttl}s")
            return deserialized_value, ttl if ttl > 0 else None
    
    def delete_key(self, key: str) -> bool:
        """
        Delete key from Redis.
        
        Args:
            key: Redis key to delete
            
        Returns:
            bool: True if key was deleted
        """
        with self._handle_redis_errors(f"delete_key({key})"):
            result = self._client.delete(key)
            logger.debug(f"Deleted key {key}")
            return result > 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if key exists
        """
        with self._handle_redis_errors(f"exists({key})"):
            result = self._client.exists(key)
            return result > 0
    
    def get_keys_pattern(self, pattern: str) -> List[str]:
        """
        Get keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "template:*")
            
        Returns:
            list: List of matching keys
        """
        with self._handle_redis_errors(f"get_keys_pattern({pattern})"):
            keys = self._client.keys(pattern)
            logger.debug(f"Found {len(keys)} keys matching pattern {pattern}")
            return keys
    
    def clear_all(self) -> bool:
        """
        Clear all data from current database.
        WARNING: This deletes all data!
        
        Returns:
            bool: True if successful
        """
        with self._handle_redis_errors("clear_all"):
            result = self._client.flushdb()
            logger.warning("Cleared all data from Redis database")
            return result
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get Redis server information.
        
        Returns:
            dict: Redis server info
        """
        with self._handle_redis_errors("get_info"):
            info = self._client.info()
            return info


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client(config: Optional[RedisConfig] = None) -> RedisClient:
    """
    Get the global Redis client instance.
    
    Args:
        config: Optional Redis configuration
        
    Returns:
        RedisClient: Global Redis client instance
    """
    global _redis_client
    if _redis_client is None or config:
        _redis_client = RedisClient(config)
        if not _redis_client.is_connected():
            _redis_client.connect()
    return _redis_client


def reset_redis_client() -> None:
    """Reset the global Redis client instance (useful for testing)."""
    global _redis_client
    if _redis_client:
        _redis_client.disconnect()
    _redis_client = None
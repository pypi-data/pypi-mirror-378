"""Comprehensive tests for cache manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import time

from apitester.core.cache_manager import CacheManager
from apitester.exceptions import CacheError


class TestCacheManager:
    """Comprehensive test cases for CacheManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock Redis client
        self.mock_redis = Mock()
        self.mock_redis.get.return_value = None
        self.mock_redis.set.return_value = True
        self.mock_redis.delete.return_value = 1
        self.mock_redis.exists.return_value = False
        self.mock_redis.keys.return_value = []
        self.mock_redis.ttl.return_value = -1
        
        # Mock configuration
        self.mock_config = Mock()
        self.mock_config.cache.enabled = True
        self.mock_config.cache.default_ttl = 3600
        self.mock_config.cache.max_entries = 1000
        
        with patch('src.apitester.core.cache_manager.get_redis_client', return_value=self.mock_redis), \
             patch('src.apitester.core.cache_manager.get_config', return_value=self.mock_config):
            self.cache_manager = CacheManager()
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        assert self.cache_manager.enabled is True
        assert self.cache_manager.default_ttl == 3600
        assert self.cache_manager.max_entries == 1000
    
    def test_cache_manager_disabled(self):
        """Test cache manager when caching is disabled."""
        self.mock_config.cache.enabled = False
        
        with patch('src.apitester.core.cache_manager.get_config', return_value=self.mock_config):
            cache_manager = CacheManager()
            assert cache_manager.enabled is False
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        request_data = {
            "method": "GET",
            "url": "https://api.example.com/users",
            "headers": {"Authorization": "Bearer token"},
            "params": {"limit": "10"}
        }
        
        key = self.cache_manager._generate_cache_key(request_data)
        
        assert isinstance(key, str)
        assert len(key) > 0
        assert "GET" in key or key.startswith("cache:")
    
    def test_generate_cache_key_consistency(self):
        """Test that same request data generates same cache key."""
        request_data = {
            "method": "GET",
            "url": "https://api.example.com/users",
            "headers": {"Authorization": "Bearer token"},
            "params": {"limit": "10"}
        }
        
        key1 = self.cache_manager._generate_cache_key(request_data)
        key2 = self.cache_manager._generate_cache_key(request_data)
        
        assert key1 == key2
    
    def test_generate_cache_key_different_requests(self):
        """Test that different requests generate different cache keys."""
        request1 = {
            "method": "GET",
            "url": "https://api.example.com/users"
        }
        
        request2 = {
            "method": "POST",
            "url": "https://api.example.com/users"
        }
        
        key1 = self.cache_manager._generate_cache_key(request1)
        key2 = self.cache_manager._generate_cache_key(request2)
        
        assert key1 != key2
    
    def test_cache_response_success(self):
        """Test successful response caching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"users": []}'
        mock_response.request_time = 0.5
        
        request_data = {
            "method": "GET",
            "url": "https://api.example.com/users"
        }
        
        result = self.cache_manager.cache_response(request_data, mock_response)
        
        assert result is True
        self.mock_redis.set.assert_called_once()
        
        # Verify the cached data structure
        call_args = self.mock_redis.set.call_args
        cached_data = json.loads(call_args[0][1])
        
        assert cached_data["status_code"] == 200
        assert cached_data["headers"] == {"Content-Type": "application/json"}
        assert cached_data["body"] == '{"users": []}'
        assert cached_data["request_time"] == 0.5
        assert "cached_at" in cached_data
        assert "expires_at" in cached_data
    
    def test_cache_response_with_custom_ttl(self):
        """Test caching with custom TTL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "test"
        mock_response.request_time = 0.1
        
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        custom_ttl = 1800
        
        self.cache_manager.cache_response(request_data, mock_response, ttl=custom_ttl)
        
        # Verify TTL was used
        call_args = self.mock_redis.set.call_args
        assert call_args[1]["ex"] == custom_ttl
    
    def test_get_cached_response_hit(self):
        """Test cache hit scenario."""
        cached_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"cached": true}',
            "request_time": 0.3,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "hit_count": 1
        }
        
        self.mock_redis.get.return_value = json.dumps(cached_data)
        
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        result = self.cache_manager.get_cached_response(request_data)
        
        assert result is not None
        cache_entry, hit_count = result
        
        assert cache_entry["status_code"] == 200
        assert cache_entry["body"] == '{"cached": true}'
        assert hit_count == 2  # Should increment hit count
    
    def test_get_cached_response_miss(self):
        """Test cache miss scenario."""
        self.mock_redis.get.return_value = None
        
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        result = self.cache_manager.get_cached_response(request_data)
        
        assert result is None
    
    def test_get_cached_response_expired(self):
        """Test expired cache entry."""
        expired_data = {
            "status_code": 200,
            "headers": {},
            "body": "expired",
            "request_time": 0.1,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),  # Expired
            "hit_count": 1
        }
        
        self.mock_redis.get.return_value = json.dumps(expired_data)
        
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        result = self.cache_manager.get_cached_response(request_data)
        
        assert result is None
        # Should delete expired entry
        self.mock_redis.delete.assert_called_once()
    
    def test_invalidate_cache_single_key(self):
        """Test cache invalidation for single key."""
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        result = self.cache_manager.invalidate_cache(request_data)
        
        assert result is True
        self.mock_redis.delete.assert_called_once()
    
    def test_invalidate_cache_pattern(self):
        """Test cache invalidation by pattern."""
        self.mock_redis.keys.return_value = [
            "cache:GET:api.example.com:1",
            "cache:GET:api.example.com:2",
            "cache:POST:api.example.com:1"
        ]
        
        result = self.cache_manager.invalidate_cache_pattern("*api.example.com*")
        
        assert result == 3
        assert self.mock_redis.delete.call_count == 3
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        self.mock_redis.keys.return_value = [
            "cache:key1",
            "cache:key2",
            "cache:key3"
        ]
        
        result = self.cache_manager.clear_cache()
        
        assert result == 3
        assert self.mock_redis.delete.call_count == 3
    
    def test_get_cache_statistics(self):
        """Test cache statistics retrieval."""
        # Mock cache keys
        cache_keys = [
            "cache:GET:api.example.com:1",
            "cache:POST:api.example.com:2",
            "cache:GET:api.test.com:3"
        ]
        self.mock_redis.keys.return_value = cache_keys
        
        # Mock cache entries with different data
        cache_entries = [
            {
                "status_code": 200,
                "hit_count": 5,
                "cached_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            },
            {
                "status_code": 404,
                "hit_count": 2,
                "cached_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
            },
            {
                "status_code": 200,
                "hit_count": 10,
                "cached_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "expires_at": (datetime.now() - timedelta(hours=1)).isoformat()  # Expired
            }
        ]
        
        def mock_get(key):
            index = cache_keys.index(key)
            return json.dumps(cache_entries[index])
        
        self.mock_redis.get.side_effect = mock_get
        
        stats = self.cache_manager.get_cache_statistics()
        
        assert stats["enabled"] is True
        assert stats["total_entries"] == 3
        assert stats["total_hits"] == 17  # 5 + 2 + 10
        assert stats["expired_entries"] == 1
        assert "hit_rate" in stats
        assert "cache_size_mb" in stats
    
    def test_cache_size_limit_enforcement(self):
        """Test cache size limit enforcement."""
        # Set low max entries for testing
        self.cache_manager.max_entries = 2
        
        # Mock existing cache keys
        self.mock_redis.keys.return_value = [
            "cache:key1",
            "cache:key2",
            "cache:key3"  # Exceeds limit
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "test"
        mock_response.request_time = 0.1
        
        request_data = {"method": "GET", "url": "https://api.example.com/new"}
        
        # Should trigger cleanup
        self.cache_manager.cache_response(request_data, mock_response)
        
        # Verify cleanup was attempted
        assert self.mock_redis.keys.called
    
    def test_cache_disabled_operations(self):
        """Test cache operations when caching is disabled."""
        self.cache_manager.enabled = False
        
        mock_response = Mock()
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        # Cache operations should return early
        cache_result = self.cache_manager.cache_response(request_data, mock_response)
        assert cache_result is False
        
        get_result = self.cache_manager.get_cached_response(request_data)
        assert get_result is None
        
        # Redis should not be called
        self.mock_redis.set.assert_not_called()
        self.mock_redis.get.assert_not_called()
    
    def test_cache_error_handling(self):
        """Test error handling in cache operations."""
        # Mock Redis error
        self.mock_redis.set.side_effect = Exception("Redis connection error")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "test"
        mock_response.request_time = 0.1
        
        request_data = {"method": "GET", "url": "https://api.example.com/test"}
        
        # Should handle error gracefully
        result = self.cache_manager.cache_response(request_data, mock_response)
        assert result is False
    
    def test_cache_key_normalization(self):
        """Test cache key normalization for consistent caching."""
        # Test that different header orders produce same key
        request1 = {
            "method": "GET",
            "url": "https://api.example.com/test",
            "headers": {"A": "1", "B": "2"}
        }
        
        request2 = {
            "method": "GET",
            "url": "https://api.example.com/test",
            "headers": {"B": "2", "A": "1"}  # Different order
        }
        
        key1 = self.cache_manager._generate_cache_key(request1)
        key2 = self.cache_manager._generate_cache_key(request2)
        
        assert key1 == key2
    
    def test_cache_entry_serialization(self):
        """Test cache entry serialization and deserialization."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"Location": "/users/123"}
        mock_response.text = '{"id": 123, "name": "test"}'
        mock_response.request_time = 0.75
        
        # Test serialization
        cache_entry = self.cache_manager._create_cache_entry(mock_response, ttl=1800)
        
        assert cache_entry["status_code"] == 201
        assert cache_entry["headers"] == {"Location": "/users/123"}
        assert cache_entry["body"] == '{"id": 123, "name": "test"}'
        assert cache_entry["request_time"] == 0.75
        assert cache_entry["hit_count"] == 0
        assert "cached_at" in cache_entry
        assert "expires_at" in cache_entry
        
        # Test that it can be JSON serialized
        serialized = json.dumps(cache_entry)
        deserialized = json.loads(serialized)
        
        assert deserialized["status_code"] == 201
        assert deserialized["body"] == '{"id": 123, "name": "test"}'
    
    def test_cache_cleanup_expired_entries(self):
        """Test cleanup of expired cache entries."""
        # Mock cache keys with mixed expired/valid entries
        cache_keys = ["cache:key1", "cache:key2", "cache:key3"]
        self.mock_redis.keys.return_value = cache_keys
        
        # Mock cache entries - some expired, some valid
        now = datetime.now()
        cache_entries = [
            {  # Expired
                "expires_at": (now - timedelta(hours=1)).isoformat(),
                "hit_count": 1
            },
            {  # Valid
                "expires_at": (now + timedelta(hours=1)).isoformat(),
                "hit_count": 2
            },
            {  # Expired
                "expires_at": (now - timedelta(minutes=30)).isoformat(),
                "hit_count": 3
            }
        ]
        
        def mock_get(key):
            index = cache_keys.index(key)
            return json.dumps(cache_entries[index])
        
        self.mock_redis.get.side_effect = mock_get
        
        # Trigger cleanup
        cleaned = self.cache_manager.cleanup_expired_entries()
        
        assert cleaned == 2  # Should clean 2 expired entries
        assert self.mock_redis.delete.call_count == 2
    
    def test_cache_performance_metrics(self):
        """Test cache performance metrics calculation."""
        # Setup cache statistics
        self.mock_redis.keys.return_value = ["cache:key1", "cache:key2"]
        
        cache_entries = [
            {
                "hit_count": 10,
                "request_time": 0.5,
                "cached_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            },
            {
                "hit_count": 5,
                "request_time": 1.2,
                "cached_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }
        ]
        
        def mock_get(key):
            index = ["cache:key1", "cache:key2"].index(key)
            return json.dumps(cache_entries[index])
        
        self.mock_redis.get.side_effect = mock_get
        
        stats = self.cache_manager.get_cache_statistics()
        
        assert stats["total_hits"] == 15
        assert stats["average_request_time"] == 0.85  # (0.5 + 1.2) / 2
        assert "hit_rate" in stats
        assert stats["total_entries"] == 2


class TestCacheEntry:
    """Test cases for CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry_data = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"test": true}',
            "request_time": 0.5,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "hit_count": 0
        }
        
        entry = CacheEntry(entry_data)
        
        assert entry.status_code == 200
        assert entry.headers == {"Content-Type": "application/json"}
        assert entry.body == '{"test": true}'
        assert entry.request_time == 0.5
        assert entry.hit_count == 0
    
    def test_cache_entry_is_expired(self):
        """Test cache entry expiration check."""
        # Create expired entry
        expired_entry = CacheEntry({
            "status_code": 200,
            "headers": {},
            "body": "",
            "request_time": 0.1,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "hit_count": 0
        })
        
        assert expired_entry.is_expired() is True
        
        # Create valid entry
        valid_entry = CacheEntry({
            "status_code": 200,
            "headers": {},
            "body": "",
            "request_time": 0.1,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "hit_count": 0
        })
        
        assert valid_entry.is_expired() is False
    
    def test_cache_entry_increment_hit_count(self):
        """Test cache entry hit count increment."""
        entry = CacheEntry({
            "status_code": 200,
            "headers": {},
            "body": "",
            "request_time": 0.1,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "hit_count": 5
        })
        
        entry.increment_hit_count()
        assert entry.hit_count == 6
        
        entry.increment_hit_count()
        assert entry.hit_count == 7


class TestCacheIntegration:
    """Integration tests for cache manager with other components."""
    
    def test_cache_integration_with_http_client(self):
        """Test cache integration with HTTP client."""
        # This would test the full flow of:
        # 1. HTTP client checks cache
        # 2. Makes request if cache miss
        # 3. Stores response in cache
        # 4. Returns cached response on subsequent requests
        
        mock_redis = Mock()
        mock_config = Mock()
        mock_config.cache.enabled = True
        mock_config.cache.default_ttl = 3600
        mock_config.cache.max_entries = 1000
        
        with patch('src.apitester.core.cache_manager.get_redis_client', return_value=mock_redis), \
             patch('src.apitester.core.cache_manager.get_config', return_value=mock_config):
            
            cache_manager = CacheManager()
            
            # Simulate first request (cache miss)
            mock_redis.get.return_value = None
            
            request_data = {
                "method": "GET",
                "url": "https://api.example.com/users"
            }
            
            cached_response = cache_manager.get_cached_response(request_data)
            assert cached_response is None
            
            # Simulate storing response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.text = '{"users": []}'
            mock_response.request_time = 0.5
            
            cache_manager.cache_response(request_data, mock_response)
            
            # Verify cache was called
            mock_redis.set.assert_called_once()
    
    def test_cache_with_different_environments(self):
        """Test cache behavior with different environments."""
        mock_redis = Mock()
        mock_config = Mock()
        mock_config.cache.enabled = True
        mock_config.cache.default_ttl = 3600
        mock_config.cache.max_entries = 1000
        
        with patch('src.apitester.core.cache_manager.get_redis_client', return_value=mock_redis), \
             patch('src.apitester.core.cache_manager.get_config', return_value=mock_config):
            
            cache_manager = CacheManager()
            
            # Same request but different environments should have different cache keys
            base_request = {
                "method": "GET",
                "url": "https://api.example.com/users"
            }
            
            dev_request = {**base_request, "environment": "development"}
            prod_request = {**base_request, "environment": "production"}
            
            dev_key = cache_manager._generate_cache_key(dev_request)
            prod_key = cache_manager._generate_cache_key(prod_request)
            
            assert dev_key != prod_key
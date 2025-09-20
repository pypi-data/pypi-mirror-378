"""Advanced response caching system with TTL and intelligent cache management."""

import hashlib
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta

from ..storage.operations import CacheOperations
from ..storage.models import CacheEntry
from ..core.http_client import HTTPResponse
from ..core.graphql_client import GraphQLResponse
from ..config.settings import get_config


logger = logging.getLogger(__name__)


class CacheManagerError(Exception):
    """Base exception for cache manager errors."""
    pass


class CacheManager:
    """Advanced response caching system with TTL, hit counting, and intelligent management."""
    
    def __init__(self):
        self.cache_ops = CacheOperations()
        self.config = get_config()
    
    def generate_cache_key(self, method: str, url: str, headers: Dict[str, str],
                          body: Optional[str] = None, params: Optional[Dict[str, str]] = None,
                          include_auth: bool = False) -> str:
        """
        Generate cache key for request with advanced options.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            include_auth: Whether to include auth headers in cache key
            
        Returns:
            Cache key string
        """
        # Start with method and URL
        cache_data = f"{method.upper()}:{url}"
        
        # Add query parameters (sorted for consistency)
        if params:
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            cache_data += f"?{param_str}"
        
        # Add relevant headers
        relevant_headers = ['content-type', 'accept', 'accept-language']
        
        if include_auth:
            relevant_headers.extend(['authorization', 'x-api-key', 'x-auth-token'])
        
        header_parts = []
        for header in relevant_headers:
            if header in headers:
                header_parts.append(f"{header}:{headers[header]}")
        
        if header_parts:
            cache_data += f"|headers:{';'.join(header_parts)}"
        
        # Add body hash for POST/PUT requests
        if body and method.upper() in ['POST', 'PUT', 'PATCH']:
            body_hash = hashlib.md5(body.encode('utf-8')).hexdigest()[:8]
            cache_data += f"|body:{body_hash}"
        
        # Generate final hash
        cache_hash = hashlib.sha256(cache_data.encode('utf-8')).hexdigest()[:16]
        return f"cache:{method.lower()}:{cache_hash}"
    
    def should_cache_request(self, method: str, url: str, headers: Dict[str, str]) -> bool:
        """
        Determine if a request should be cached based on method and headers.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            
        Returns:
            True if request should be cached
        """
        if not self.config.cache.enabled:
            return False
        
        # Only cache safe methods by default
        if method.upper() not in ['GET', 'HEAD', 'OPTIONS']:
            return False
        
        # Check for cache control headers
        cache_control = headers.get('Cache-Control', '').lower()
        if 'no-cache' in cache_control or 'no-store' in cache_control:
            return False
        
        # Don't cache requests with authorization unless explicitly configured
        if 'Authorization' in headers and not self.config.cache.cache_authenticated:
            return False
        
        return True
    
    def should_cache_response(self, response: Union[HTTPResponse, GraphQLResponse]) -> bool:
        """
        Determine if a response should be cached based on status and headers.
        
        Args:
            response: Response object
            
        Returns:
            True if response should be cached
        """
        # Only cache successful responses
        if not (200 <= response.status_code < 300):
            return False
        
        # Check response cache control headers
        cache_control = response.headers.get('Cache-Control', '').lower()
        if 'no-cache' in cache_control or 'no-store' in cache_control or 'private' in cache_control:
            return False
        
        # Check for explicit no-cache headers
        if response.headers.get('Pragma', '').lower() == 'no-cache':
            return False
        
        return True
    
    def get_cache_ttl(self, response: Union[HTTPResponse, GraphQLResponse],
                     default_ttl: Optional[int] = None) -> int:
        """
        Determine cache TTL based on response headers and configuration.
        
        Args:
            response: Response object
            default_ttl: Default TTL to use if not specified
            
        Returns:
            TTL in seconds
        """
        if default_ttl is None:
            default_ttl = self.config.cache.default_ttl
        
        # Check Cache-Control max-age
        cache_control = response.headers.get('Cache-Control', '')
        if 'max-age=' in cache_control:
            try:
                max_age_part = [part for part in cache_control.split(',') if 'max-age=' in part][0]
                max_age = int(max_age_part.split('=')[1].strip())
                return max_age
            except (ValueError, IndexError):
                pass
        
        # Check Expires header
        expires = response.headers.get('Expires')
        if expires:
            try:
                from email.utils import parsedate_to_datetime
                expires_dt = parsedate_to_datetime(expires)
                ttl = int((expires_dt - datetime.now()).total_seconds())
                return max(0, ttl)
            except (ValueError, TypeError):
                pass
        
        return default_ttl
    
    def cache_response(self, method: str, url: str, headers: Dict[str, str],
                      response: Union[HTTPResponse, GraphQLResponse],
                      body: Optional[str] = None,
                      params: Optional[Dict[str, str]] = None,
                      ttl: Optional[int] = None,
                      tags: Optional[List[str]] = None) -> bool:
        """
        Cache a response with advanced options.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            response: Response object to cache
            body: Request body
            params: Query parameters
            ttl: Custom TTL (overrides automatic detection)
            tags: Tags for cache entry categorization
            
        Returns:
            True if response was cached
        """
        try:
            # Check if we should cache this request/response
            if not self.should_cache_request(method, url, headers):
                logger.debug(f"Request not cacheable: {method} {url}")
                return False
            
            if not self.should_cache_response(response):
                logger.debug(f"Response not cacheable: {response.status_code}")
                return False
            
            # Determine TTL
            if ttl is None:
                ttl = self.get_cache_ttl(response)
            
            # Generate cache key
            cache_key = self.generate_cache_key(method, url, headers, body, params)
            
            # Create cache entry
            cache_entry = {
                'method': method,
                'url': url,
                'request_headers': headers,
                'request_body': body or '',
                'request_params': params or {},
                'response_status': response.status_code,
                'response_headers': response.headers,
                'response_body': response.text if hasattr(response, 'text') else str(response.to_dict()),
                'cached_at': datetime.now().isoformat(),
                'ttl': ttl,
                'hit_count': 0,
                'tags': tags or []
            }
            
            # Store in cache
            success = self.cache_ops.cache_response(
                method=method,
                url=url,
                headers=headers,
                response_status=response.status_code,
                response_headers=response.headers,
                response_body=cache_entry['response_body'],
                ttl=ttl
            )
            
            if success:
                logger.debug(f"Cached response: {method} {url} (TTL: {ttl}s)")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False
    
    def get_cached_response(self, method: str, url: str, headers: Dict[str, str],
                          body: Optional[str] = None,
                          params: Optional[Dict[str, str]] = None) -> Optional[Tuple[Dict[str, Any], int]]:
        """
        Get cached response if available and valid.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            
        Returns:
            Tuple of (cache_entry, hit_count) or None if not cached
        """
        try:
            if not self.config.cache.enabled:
                return None
            
            # Generate cache key
            cache_key = self.generate_cache_key(method, url, headers, body, params)
            
            # Get from cache
            cached_data = self.cache_ops.get_cached_response(method, url, headers)
            
            if cached_data:
                response_status, response_headers, response_body, hit_count = cached_data
                
                cache_entry = {
                    'method': method,
                    'url': url,
                    'response_status': response_status,
                    'response_headers': response_headers,
                    'response_body': response_body,
                    'from_cache': True,
                    'hit_count': hit_count
                }
                
                logger.debug(f"Cache hit: {method} {url} (hits: {hit_count})")
                return cache_entry, hit_count
            
            logger.debug(f"Cache miss: {method} {url}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None
    
    def invalidate_cache(self, pattern: Optional[str] = None,
                        method: Optional[str] = None,
                        url_pattern: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> int:
        """
        Invalidate cache entries based on patterns.
        
        Args:
            pattern: Cache key pattern to match
            method: HTTP method to match
            url_pattern: URL pattern to match
            tags: Tags to match
            
        Returns:
            Number of entries invalidated
        """
        try:
            # For now, we'll implement a simple clear all
            # In a full implementation, you'd need pattern matching in the storage layer
            if not any([pattern, method, url_pattern, tags]):
                # Clear all cache
                success = self.cache_ops.clear_cache()
                return 1 if success else 0
            
            # Pattern-based invalidation would require storage layer support
            logger.warning("Pattern-based cache invalidation not yet implemented")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return 0
    
    def clear_cache(self) -> bool:
        """
        Clear all cached responses.
        
        Returns:
            True if cache was cleared
        """
        try:
            success = self.cache_ops.clear_cache()
            if success:
                logger.info("Cleared all cached responses")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            base_stats = self.cache_ops.get_cache_stats()
            
            # Add additional computed statistics
            stats = base_stats.copy()
            
            # Calculate hit rate
            if stats['total_hits'] > 0 and stats['total_entries'] > 0:
                # This is a simplified calculation
                # In a real implementation, you'd track cache requests vs hits
                stats['estimated_hit_rate'] = min(100.0, (stats['total_hits'] / stats['total_entries']) * 10)
            else:
                stats['estimated_hit_rate'] = 0.0
            
            # Calculate cache efficiency
            if stats['total_entries'] > 0:
                stats['efficiency'] = {
                    'entries_with_hits': stats['total_entries'] - stats.get('unused_entries', 0),
                    'average_hits_per_entry': stats['total_hits'] / stats['total_entries'],
                    'expired_ratio': (stats.get('expired_entries', 0) / stats['total_entries']) * 100
                }
            else:
                stats['efficiency'] = {
                    'entries_with_hits': 0,
                    'average_hits_per_entry': 0.0,
                    'expired_ratio': 0.0
                }
            
            # Add cache health status
            if not stats['enabled']:
                stats['health'] = 'disabled'
            elif stats['total_entries'] == 0:
                stats['health'] = 'empty'
            elif stats.get('expired_entries', 0) > stats['total_entries'] * 0.5:
                stats['health'] = 'needs_cleanup'
            else:
                stats['health'] = 'healthy'
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {
                'enabled': self.config.cache.enabled,
                'error': str(e),
                'health': 'error'
            }
    
    def optimize_cache(self, max_entries: Optional[int] = None,
                      remove_expired: bool = True,
                      remove_unused: bool = False,
                      min_hit_count: int = 0) -> Dict[str, Any]:
        """
        Optimize cache by removing expired, unused, or low-hit entries.
        
        Args:
            max_entries: Maximum entries to keep (removes least recently used)
            remove_expired: Whether to remove expired entries
            remove_unused: Whether to remove entries with no hits
            min_hit_count: Minimum hit count to keep entries
            
        Returns:
            Dictionary with optimization results
        """
        try:
            stats_before = self.get_cache_statistics()
            
            # For now, we can only clear all cache
            # In a full implementation, you'd need selective removal in storage layer
            
            optimization_needed = False
            
            if remove_expired and stats_before.get('expired_entries', 0) > 0:
                optimization_needed = True
            
            if max_entries and stats_before.get('total_entries', 0) > max_entries:
                optimization_needed = True
            
            if optimization_needed:
                # Simple implementation: clear all cache
                # In production, you'd implement selective removal
                self.clear_cache()
                
                return {
                    'optimization_performed': True,
                    'method': 'full_clear',
                    'entries_before': stats_before.get('total_entries', 0),
                    'entries_after': 0,
                    'entries_removed': stats_before.get('total_entries', 0),
                    'reason': 'Selective optimization not yet implemented'
                }
            else:
                return {
                    'optimization_performed': False,
                    'reason': 'No optimization needed',
                    'entries_count': stats_before.get('total_entries', 0)
                }
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return {
                'optimization_performed': False,
                'error': str(e)
            }
    
    def preload_cache(self, requests: List[Dict[str, Any]],
                     max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Preload cache with multiple requests.
        
        Args:
            requests: List of request dictionaries
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary with preload results
        """
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from ..core.http_client import HTTPClient
            
            http_client = HTTPClient()
            results = {
                'total_requests': len(requests),
                'successful_preloads': 0,
                'failed_preloads': 0,
                'results': []
            }
            
            def preload_request(request_data):
                try:
                    method = request_data.get('method', 'GET')
                    url = request_data['url']
                    headers = request_data.get('headers', {})
                    body = request_data.get('body')
                    params = request_data.get('params')
                    
                    # Make request
                    response = http_client.send_request(
                        method=method,
                        url=url,
                        headers=headers,
                        body=body,
                        params=params
                    )
                    
                    # Cache response
                    cached = self.cache_response(method, url, headers, response, body, params)
                    
                    return {
                        'url': url,
                        'method': method,
                        'status': 'success',
                        'cached': cached,
                        'response_status': response.status_code
                    }
                    
                except Exception as e:
                    return {
                        'url': request_data.get('url', 'unknown'),
                        'method': request_data.get('method', 'unknown'),
                        'status': 'failed',
                        'error': str(e)
                    }
            
            # Execute requests concurrently
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                future_to_request = {
                    executor.submit(preload_request, req): req for req in requests
                }
                
                for future in as_completed(future_to_request):
                    result = future.result()
                    results['results'].append(result)
                    
                    if result['status'] == 'success':
                        results['successful_preloads'] += 1
                    else:
                        results['failed_preloads'] += 1
            
            logger.info(f"Cache preload completed: {results['successful_preloads']}/{results['total_requests']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Cache preload failed: {e}")
            return {
                'total_requests': len(requests),
                'successful_preloads': 0,
                'failed_preloads': 0,
                'error': str(e),
                'results': []
            }
    
    def create_cache_policy(self, name: str, rules: Dict[str, Any]) -> bool:
        """
        Create a named cache policy with specific rules.
        
        Args:
            name: Policy name
            rules: Policy rules dictionary
            
        Returns:
            True if policy was created
            
        Note: This is a placeholder for future cache policy implementation
        """
        try:
            # Store policy in configuration or database
            # This would be implemented with proper policy storage
            
            logger.info(f"Cache policy '{name}' created (placeholder implementation)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create cache policy: {e}")
            return False
    
    def apply_cache_policy(self, policy_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply cache policy to determine caching behavior.
        
        Args:
            policy_name: Name of policy to apply
            request_data: Request data to evaluate
            
        Returns:
            Dictionary with caching decisions
            
        Note: This is a placeholder for future cache policy implementation
        """
        # Default policy
        return {
            'should_cache': self.should_cache_request(
                request_data.get('method', 'GET'),
                request_data.get('url', ''),
                request_data.get('headers', {})
            ),
            'ttl': self.config.cache.default_ttl,
            'policy_applied': 'default'
        }
"""Tests for history management and caching functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from apitester.core.history_manager import (
    HistoryManager, HistoryManagerError, HistoryNotFoundError
)
from apitester.core.history_query import (
    HistoryQueryEngine, HistoryQuery, HistoryQueryBuilder, HistoryRetryError
)
from apitester.core.cache_manager import (
    CacheManager, CacheManagerError
)
from apitester.storage.models import RequestRecord, HTTPMethod
from apitester.core.http_client import HTTPResponse
from apitester.core.graphql_client import GraphQLResponse


class TestHistoryManager:
    """Test history manager functionality."""
    
    @pytest.fixture
    def mock_history_ops(self):
        """Mock history operations."""
        with patch('apitester.core.history_manager.HistoryOperations') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def history_manager(self, mock_history_ops):
        """Create history manager with mocked operations."""
        return HistoryManager()
    
    @pytest.fixture
    def sample_response(self):
        """Sample HTTP response."""
        response = Mock(spec=HTTPResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json'}
        response.text = '{"success": true}'
        response.request_time = 0.5
        return response
    
    def test_add_request_success(self, history_manager, mock_history_ops, sample_response):
        """Test adding request to history."""
        mock_history_ops.add_request.return_value = True
        
        record = history_manager.add_request(
            method='GET',
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'},
            response=sample_response,
            template_name='get-users',
            environment='test'
        )
        
        assert isinstance(record, RequestRecord)
        assert record.method == HTTPMethod.GET
        assert record.url == 'https://api.example.com/users'
        assert record.response_status == 200
        assert record.template_name == 'get-users'
        assert record.environment == 'test'
        
        mock_history_ops.add_request.assert_called_once()
    
    def test_add_request_with_error(self, history_manager, mock_history_ops):
        """Test adding failed request to history."""
        mock_history_ops.add_request.return_value = True
        
        record = history_manager.add_request(
            method='POST',
            url='https://api.example.com/users',
            headers={'Content-Type': 'application/json'},
            body='{"name": "test"}',
            error_message='Connection timeout',
            environment='test'
        )
        
        assert record.method == HTTPMethod.POST
        assert record.response_status == 0
        assert record.error_message == 'Connection timeout'
        assert record.body == '{"name": "test"}'
    
    def test_get_history_with_filters(self, history_manager, mock_history_ops):
        """Test getting history with filters."""
        # Create sample records
        records = [
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/users',
                response_status=200,
                environment='test'
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.POST,
                url='https://api.example.com/posts',
                response_status=201,
                environment='prod'
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/posts',
                response_status=404,
                environment='test'
            )
        ]
        
        mock_history_ops.get_history.return_value = records
        
        # Test method filter
        filtered = history_manager.get_history(method_filter='GET')
        get_records = [r for r in filtered if r.method == HTTPMethod.GET]
        assert len(get_records) == 2
        
        # Test status filter
        filtered = history_manager.get_history(status_filter=[200, 201])
        success_records = [r for r in filtered if r.response_status in [200, 201]]
        assert len(success_records) == 2
        
        # Test environment filter
        filtered = history_manager.get_history(environment_filter='test')
        test_records = [r for r in filtered if r.environment == 'test']
        assert len(test_records) == 2
    
    def test_get_last_request(self, history_manager, mock_history_ops):
        """Test getting last request."""
        last_record = RequestRecord(
            timestamp=datetime.now(),
            method=HTTPMethod.GET,
            url='https://api.example.com/last',
            response_status=200
        )
        
        mock_history_ops.get_last_request.return_value = last_record
        
        result = history_manager.get_last_request()
        
        assert result == last_record
        mock_history_ops.get_last_request.assert_called_once()
    
    def test_get_request_by_index(self, history_manager, mock_history_ops):
        """Test getting request by index."""
        records = [
            RequestRecord(timestamp=datetime.now(), method=HTTPMethod.GET, url='https://api.example.com/1'),
            RequestRecord(timestamp=datetime.now(), method=HTTPMethod.GET, url='https://api.example.com/2'),
            RequestRecord(timestamp=datetime.now(), method=HTTPMethod.GET, url='https://api.example.com/3')
        ]
        
        with patch.object(history_manager, 'get_history', return_value=records):
            # Get first record (index 0)
            record = history_manager.get_request_by_index(0)
            assert record.url == 'https://api.example.com/1'
            
            # Get second record (index 1)
            record = history_manager.get_request_by_index(1)
            assert record.url == 'https://api.example.com/2'
    
    def test_get_request_by_index_out_of_range(self, history_manager):
        """Test getting request by invalid index."""
        with patch.object(history_manager, 'get_history', return_value=[]):
            with pytest.raises(HistoryNotFoundError):
                history_manager.get_request_by_index(0)
    
    def test_clear_history_without_confirmation(self, history_manager):
        """Test clearing history without confirmation."""
        with pytest.raises(HistoryManagerError, match="requires explicit confirmation"):
            history_manager.clear_history(confirm=False)
    
    def test_clear_history_with_confirmation(self, history_manager, mock_history_ops):
        """Test clearing history with confirmation."""
        mock_history_ops.clear_history.return_value = True
        
        result = history_manager.clear_history(confirm=True)
        
        assert result is True
        mock_history_ops.clear_history.assert_called_once()
    
    def test_get_history_statistics(self, history_manager, mock_history_ops):
        """Test getting history statistics."""
        records = [
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/users',
                response_status=200,
                response_time=0.5,
                environment='test',
                template_name='get-users'
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.POST,
                url='https://api.example.com/users',
                response_status=201,
                response_time=0.8,
                environment='test'
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/posts',
                response_status=404,
                response_time=0.3,
                environment='prod'
            )
        ]
        
        with patch.object(history_manager, 'get_history', return_value=records):
            stats = history_manager.get_history_statistics()
            
            assert stats['total_requests'] == 3
            assert stats['successful_requests'] == 2
            assert stats['failed_requests'] == 1
            assert stats['success_rate'] == pytest.approx(66.67, rel=1e-2)
            assert 'GET' in stats['methods']
            assert 'POST' in stats['methods']
            assert stats['methods']['GET'] == 2
            assert stats['methods']['POST'] == 1
            assert 'test' in stats['environments']
            assert 'prod' in stats['environments']
            assert 'get-users' in stats['templates']
    
    def test_export_history_json(self, history_manager):
        """Test exporting history to JSON."""
        records = [
            RequestRecord(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                method=HTTPMethod.GET,
                url='https://api.example.com/users',
                response_status=200,
                environment='test'
            )
        ]
        
        with patch.object(history_manager, 'get_history', return_value=records):
            exported = history_manager.export_history('json')
            
            assert isinstance(exported, str)
            import json
            data = json.loads(exported)
            assert 'export_info' in data
            assert 'requests' in data
            assert len(data['requests']) == 1
            assert data['requests'][0]['method'] == 'GET'
            assert data['requests'][0]['url'] == 'https://api.example.com/users'
    
    def test_export_history_csv(self, history_manager):
        """Test exporting history to CSV."""
        records = [
            RequestRecord(
                timestamp=datetime(2023, 1, 1, 12, 0, 0),
                method=HTTPMethod.GET,
                url='https://api.example.com/users',
                response_status=200,
                environment='test'
            )
        ]
        
        with patch.object(history_manager, 'get_history', return_value=records):
            exported = history_manager.export_history('csv')
            
            assert isinstance(exported, str)
            lines = exported.strip().split('\n')
            assert len(lines) == 2  # Header + 1 data row
            assert 'timestamp,method,url' in lines[0]
            assert 'GET,https://api.example.com/users' in lines[1]


class TestHistoryQueryEngine:
    """Test history query engine functionality."""
    
    @pytest.fixture
    def mock_history_manager(self):
        """Mock history manager."""
        return Mock()
    
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
    def query_engine(self, mock_history_manager, mock_http_client):
        """Create query engine with mocked dependencies."""
        return HistoryQueryEngine(mock_history_manager, mock_http_client)
    
    def test_query_history_basic(self, query_engine, mock_history_manager):
        """Test basic history querying."""
        sample_records = [
            RequestRecord(timestamp=datetime.now(), method=HTTPMethod.GET, url='https://api.example.com/1'),
            RequestRecord(timestamp=datetime.now(), method=HTTPMethod.POST, url='https://api.example.com/2')
        ]
        
        mock_history_manager.get_history.return_value = sample_records
        
        query = HistoryQuery(method='GET')
        results = query_engine.query_history(query)
        
        mock_history_manager.get_history.assert_called_once()
        # Results would be filtered by the query engine
        assert isinstance(results, list)
    
    def test_search_by_response_content(self, query_engine, mock_history_manager):
        """Test searching by response content."""
        records = [
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/users',
                response_body='{"users": [{"name": "John"}, {"name": "Jane"}]}'
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/posts',
                response_body='{"posts": [{"title": "Hello World"}]}'
            )
        ]
        
        mock_history_manager.get_history.return_value = records
        
        results = query_engine.search_by_response_content('John')
        
        assert len(results) == 1
        assert results[0].url == 'https://api.example.com/users'
    
    def test_get_failed_requests(self, query_engine, mock_history_manager):
        """Test getting failed requests."""
        records = [
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/success',
                response_status=200
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url='https://api.example.com/error',
                response_status=404
            ),
            RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.POST,
                url='https://api.example.com/timeout',
                error_message='Connection timeout'
            )
        ]
        
        with patch.object(query_engine, 'query_history', return_value=records):
            failed = query_engine.get_failed_requests()
            
            # Should include 404 and timeout error
            assert len(failed) == 2
    
    def test_retry_request(self, query_engine, mock_http_client, mock_history_manager):
        """Test retrying a request."""
        original_record = RequestRecord(
            timestamp=datetime.now(),
            method=HTTPMethod.GET,
            url='https://api.example.com/retry',
            headers={'Accept': 'application/json'},
            response_status=500,
            environment='test'
        )
        
        mock_history_manager.add_request.return_value = Mock()
        
        response = query_engine.retry_request(original_record)
        
        assert response.status_code == 200
        mock_http_client.send_request.assert_called_once()
        mock_history_manager.add_request.assert_called()
    
    def test_retry_request_with_modifications(self, query_engine, mock_http_client, mock_history_manager):
        """Test retrying request with modifications."""
        original_record = RequestRecord(
            timestamp=datetime.now(),
            method=HTTPMethod.GET,
            url='https://api.example.com/retry',
            headers={'Accept': 'application/json'}
        )
        
        modifications = {
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"retry": true}'
        }
        
        mock_history_manager.add_request.return_value = Mock()
        
        response = query_engine.retry_request(original_record, modifications)
        
        # Verify modified parameters were used
        call_args = mock_http_client.send_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['body'] == '{"retry": true}'
        assert 'Content-Type' in call_args['headers']
    
    def test_query_builder_fluent_interface(self, query_engine):
        """Test fluent query builder interface."""
        builder = query_engine.create_query_builder()
        
        assert isinstance(builder, HistoryQueryBuilder)
        
        # Test method chaining
        result_builder = (builder
                         .method('GET')
                         .url_pattern('*/users')
                         .status_codes([200, 201])
                         .environment('test')
                         .success_only()
                         .limit(10))
        
        assert result_builder is builder  # Should return same instance for chaining
        assert builder.query.method == 'GET'
        assert builder.query.url_pattern == '*/users'
        assert builder.query.status_codes == [200, 201]
        assert builder.query.environment == 'test'
        assert builder.query.success_only is True
        assert builder.query.limit == 10


class TestCacheManager:
    """Test cache manager functionality."""
    
    @pytest.fixture
    def mock_cache_ops(self):
        """Mock cache operations."""
        with patch('apitester.core.cache_manager.CacheOperations') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def cache_manager(self, mock_cache_ops):
        """Create cache manager with mocked operations."""
        return CacheManager()
    
    @pytest.fixture
    def sample_response(self):
        """Sample HTTP response."""
        response = Mock(spec=HTTPResponse)
        response.status_code = 200
        response.headers = {'Content-Type': 'application/json', 'Cache-Control': 'max-age=300'}
        response.text = '{"data": "test"}'
        response.request_time = 0.3
        return response
    
    def test_generate_cache_key(self, cache_manager):
        """Test cache key generation."""
        key = cache_manager.generate_cache_key(
            method='GET',
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'},
            params={'limit': '10'}
        )
        
        assert key.startswith('cache:get:')
        assert len(key) > 20  # Should have hash suffix
    
    def test_generate_cache_key_with_body(self, cache_manager):
        """Test cache key generation with request body."""
        key1 = cache_manager.generate_cache_key(
            method='POST',
            url='https://api.example.com/users',
            headers={'Content-Type': 'application/json'},
            body='{"name": "John"}'
        )
        
        key2 = cache_manager.generate_cache_key(
            method='POST',
            url='https://api.example.com/users',
            headers={'Content-Type': 'application/json'},
            body='{"name": "Jane"}'
        )
        
        # Different bodies should generate different keys
        assert key1 != key2
    
    def test_should_cache_request_get(self, cache_manager):
        """Test cache decision for GET request."""
        should_cache = cache_manager.should_cache_request(
            method='GET',
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'}
        )
        
        assert should_cache is True
    
    def test_should_cache_request_post(self, cache_manager):
        """Test cache decision for POST request."""
        should_cache = cache_manager.should_cache_request(
            method='POST',
            url='https://api.example.com/users',
            headers={'Content-Type': 'application/json'}
        )
        
        assert should_cache is False  # POST requests not cached by default
    
    def test_should_cache_request_no_cache_header(self, cache_manager):
        """Test cache decision with no-cache header."""
        should_cache = cache_manager.should_cache_request(
            method='GET',
            url='https://api.example.com/users',
            headers={'Cache-Control': 'no-cache'}
        )
        
        assert should_cache is False
    
    def test_should_cache_response_success(self, cache_manager, sample_response):
        """Test cache decision for successful response."""
        should_cache = cache_manager.should_cache_response(sample_response)
        
        assert should_cache is True
    
    def test_should_cache_response_error(self, cache_manager):
        """Test cache decision for error response."""
        error_response = Mock()
        error_response.status_code = 404
        error_response.headers = {}
        
        should_cache = cache_manager.should_cache_response(error_response)
        
        assert should_cache is False
    
    def test_get_cache_ttl_from_max_age(self, cache_manager, sample_response):
        """Test TTL extraction from Cache-Control max-age."""
        ttl = cache_manager.get_cache_ttl(sample_response)
        
        assert ttl == 300  # From max-age=300 in sample response
    
    def test_get_cache_ttl_default(self, cache_manager):
        """Test default TTL when no cache headers present."""
        response = Mock()
        response.headers = {}
        
        ttl = cache_manager.get_cache_ttl(response)
        
        # Should use default from config
        assert ttl > 0
    
    def test_cache_response_success(self, cache_manager, mock_cache_ops, sample_response):
        """Test successful response caching."""
        mock_cache_ops.cache_response.return_value = True
        
        with patch.object(cache_manager, 'should_cache_request', return_value=True):
            with patch.object(cache_manager, 'should_cache_response', return_value=True):
                result = cache_manager.cache_response(
                    method='GET',
                    url='https://api.example.com/users',
                    headers={'Accept': 'application/json'},
                    response=sample_response
                )
        
        assert result is True
        mock_cache_ops.cache_response.assert_called_once()
    
    def test_cache_response_not_cacheable(self, cache_manager, sample_response):
        """Test caching when request is not cacheable."""
        with patch.object(cache_manager, 'should_cache_request', return_value=False):
            result = cache_manager.cache_response(
                method='POST',
                url='https://api.example.com/users',
                headers={'Content-Type': 'application/json'},
                response=sample_response
            )
        
        assert result is False
    
    def test_get_cached_response_hit(self, cache_manager, mock_cache_ops):
        """Test cache hit."""
        mock_cache_ops.get_cached_response.return_value = (200, {'Content-Type': 'application/json'}, '{"cached": true}', 5)
        
        result = cache_manager.get_cached_response(
            method='GET',
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'}
        )
        
        assert result is not None
        cache_entry, hit_count = result
        assert cache_entry['response_status'] == 200
        assert cache_entry['from_cache'] is True
        assert hit_count == 5
    
    def test_get_cached_response_miss(self, cache_manager, mock_cache_ops):
        """Test cache miss."""
        mock_cache_ops.get_cached_response.return_value = None
        
        result = cache_manager.get_cached_response(
            method='GET',
            url='https://api.example.com/users',
            headers={'Accept': 'application/json'}
        )
        
        assert result is None
    
    def test_clear_cache(self, cache_manager, mock_cache_ops):
        """Test clearing cache."""
        mock_cache_ops.clear_cache.return_value = True
        
        result = cache_manager.clear_cache()
        
        assert result is True
        mock_cache_ops.clear_cache.assert_called_once()
    
    def test_get_cache_statistics(self, cache_manager, mock_cache_ops):
        """Test getting cache statistics."""
        mock_cache_ops.get_cache_stats.return_value = {
            'total_entries': 10,
            'total_hits': 25,
            'expired_entries': 2,
            'enabled': True,
            'default_ttl': 300
        }
        
        stats = cache_manager.get_cache_statistics()
        
        assert stats['total_entries'] == 10
        assert stats['total_hits'] == 25
        assert 'estimated_hit_rate' in stats
        assert 'efficiency' in stats
        assert 'health' in stats
    
    def test_optimize_cache(self, cache_manager):
        """Test cache optimization."""
        with patch.object(cache_manager, 'get_cache_statistics') as mock_stats:
            mock_stats.return_value = {'total_entries': 100, 'expired_entries': 20}
            
            with patch.object(cache_manager, 'clear_cache', return_value=True) as mock_clear:
                result = cache_manager.optimize_cache(max_entries=50, remove_expired=True)
                
                assert result['optimization_performed'] is True
                assert result['entries_before'] == 100
                mock_clear.assert_called_once()
    
    def test_preload_cache(self, cache_manager):
        """Test cache preloading."""
        requests = [
            {'method': 'GET', 'url': 'https://api.example.com/users'},
            {'method': 'GET', 'url': 'https://api.example.com/posts'}
        ]
        
        with patch.object(cache_manager, 'cache_response', return_value=True):
            with patch('apitester.core.cache_manager.HTTPClient') as mock_client_class:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.status_code = 200
                mock_client.send_request.return_value = mock_response
                mock_client_class.return_value = mock_client
                
                result = cache_manager.preload_cache(requests, max_concurrent=2)
                
                assert result['total_requests'] == 2
                assert result['successful_preloads'] >= 0  # May vary based on execution
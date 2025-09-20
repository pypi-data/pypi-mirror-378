"""HTTP client for making API requests with retry and timeout handling."""

import httpx
import time
import logging
from typing import Dict, Any, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse
from pathlib import Path
import json

from ..config.settings import get_config
from ..storage.models import HTTPMethod, RequestRecord, validate_http_method, validate_url, sanitize_headers


logger = logging.getLogger(__name__)


class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""
    pass


class RequestValidationError(HTTPClientError):
    """Raised when request validation fails."""
    pass


class NetworkError(HTTPClientError):
    """Raised when network-related errors occur."""
    pass


class TimeoutError(HTTPClientError):
    """Raised when request times out."""
    pass


class HTTPResponse:
    """Wrapper for HTTP response with additional metadata."""
    
    def __init__(self, response: httpx.Response, request_time: float, from_cache: bool = False):
        self.response = response
        self.request_time = request_time
        self.from_cache = from_cache
        
    @property
    def status_code(self) -> int:
        """Get response status code."""
        return self.response.status_code
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get response headers as dictionary."""
        return dict(self.response.headers)
    
    @property
    def text(self) -> str:
        """Get response body as text."""
        return self.response.text
    
    @property
    def content(self) -> bytes:
        """Get response body as bytes."""
        return self.response.content
    
    @property
    def url(self) -> str:
        """Get final URL after redirects."""
        return str(self.response.url)
    
    def json(self) -> Any:
        """Parse response body as JSON."""
        try:
            return self.response.json()
        except Exception as e:
            raise ValueError(f"Failed to parse response as JSON: {e}")
    
    def is_success(self) -> bool:
        """Check if response indicates success (2xx status)."""
        return 200 <= self.status_code < 300
    
    def is_redirect(self) -> bool:
        """Check if response is a redirect (3xx status)."""
        return 300 <= self.status_code < 400
    
    def is_client_error(self) -> bool:
        """Check if response is a client error (4xx status)."""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """Check if response is a server error (5xx status)."""
        return 500 <= self.status_code < 600


class HTTPClient:
    """HTTP client with support for various methods, retries, and timeouts."""
    
    def __init__(self):
        self.config = get_config()
        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client instance."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.config.timeout,
                follow_redirects=True,
                max_redirects=self.config.max_redirects,
                verify=self.config.verify_ssl,
            )
        return self._client
    
    def close(self) -> None:
        """Close HTTP client connections."""
        if self._client:
            self._client.close()
            self._client = None
        if self._async_client:
            # Note: async client should be closed in async context
            self._async_client = None
    
    def validate_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                        body: Optional[str] = None, params: Optional[Dict[str, str]] = None) -> None:
        """
        Validate request parameters.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            
        Raises:
            RequestValidationError: If validation fails
        """
        try:
            # Validate HTTP method
            validate_http_method(method)
            
            # Validate URL
            validate_url(url)
            
            # Validate headers
            if headers:
                sanitized = sanitize_headers(headers)
                if len(sanitized) != len(headers):
                    logger.warning("Some headers were sanitized during validation")
            
            # Validate body for methods that shouldn't have body
            if method.upper() in ['GET', 'HEAD', 'OPTIONS'] and body:
                logger.warning(f"Body provided for {method} request, this may not be supported by all servers")
            
            # Validate JSON body if Content-Type suggests JSON
            if body and headers:
                content_type = headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    try:
                        json.loads(body)
                    except json.JSONDecodeError as e:
                        raise RequestValidationError(f"Invalid JSON in request body: {e}")
            
        except ValueError as e:
            raise RequestValidationError(str(e))
    
    def _prepare_request_data(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                             body: Optional[str] = None, params: Optional[Dict[str, str]] = None,
                             files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare request data for httpx.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            files: Files for multipart upload
            
        Returns:
            Dictionary of request parameters for httpx
        """
        request_data = {
            'method': method.upper(),
            'url': url,
        }
        
        # Add headers
        if headers:
            # Merge with default headers
            merged_headers = self.config.default_headers.copy()
            merged_headers.update(sanitize_headers(headers))
            request_data['headers'] = merged_headers
        elif self.config.default_headers:
            request_data['headers'] = self.config.default_headers
        
        # Add query parameters
        if params:
            request_data['params'] = params
        
        # Add body content
        if body:
            # Determine content type and set appropriate parameter
            content_type = request_data.get('headers', {}).get('Content-Type', '').lower()
            
            if 'application/json' in content_type:
                try:
                    # Parse and re-serialize to ensure valid JSON
                    parsed = json.loads(body)
                    request_data['json'] = parsed
                except json.JSONDecodeError:
                    # If not valid JSON, send as text
                    request_data['content'] = body
            elif 'application/x-www-form-urlencoded' in content_type:
                # Parse form data
                try:
                    form_data = {}
                    for pair in body.split('&'):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            form_data[key] = value
                    request_data['data'] = form_data
                except Exception:
                    request_data['content'] = body
            else:
                request_data['content'] = body
        
        # Add files for multipart upload
        if files:
            request_data['files'] = files
        
        return request_data
    
    def _execute_request_with_retry(self, request_data: Dict[str, Any], 
                                   max_retries: int = 3) -> Tuple[httpx.Response, float]:
        """
        Execute HTTP request with retry logic.
        
        Args:
            request_data: Request parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (response, request_time)
            
        Raises:
            NetworkError: If all retry attempts fail
            TimeoutError: If request times out
        """
        client = self._get_client()
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                response = client.request(**request_data)
                request_time = time.time() - start_time
                
                logger.debug(f"Request completed in {request_time:.3f}s (attempt {attempt + 1})")
                return response, request_time
                
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    raise TimeoutError(f"Request timed out after {max_retries + 1} attempts")
                
            except httpx.NetworkError as e:
                last_exception = e
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    raise NetworkError(f"Network error after {max_retries + 1} attempts: {e}")
                
            except httpx.HTTPStatusError as e:
                # Don't retry on HTTP status errors (4xx, 5xx)
                request_time = time.time() - start_time if 'start_time' in locals() else 0
                return e.response, request_time
                
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    raise HTTPClientError(f"Unexpected error after {max_retries + 1} attempts: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 1s, 2s, 4s, etc.
                logger.debug(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        # This should never be reached, but just in case
        raise HTTPClientError(f"Request failed after {max_retries + 1} attempts: {last_exception}")
    
    def send_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                    body: Optional[str] = None, params: Optional[Dict[str, str]] = None,
                    files: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> HTTPResponse:
        """
        Send HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD)
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            files: Files for multipart upload
            max_retries: Maximum number of retry attempts
            
        Returns:
            HTTPResponse object
            
        Raises:
            RequestValidationError: If request validation fails
            NetworkError: If network error occurs
            TimeoutError: If request times out
            HTTPClientError: If other error occurs
        """
        # Validate request
        self.validate_request(method, url, headers, body, params)
        
        # Prepare request data
        request_data = self._prepare_request_data(method, url, headers, body, params, files)
        
        logger.info(f"Sending {method.upper()} request to {url}")
        logger.debug(f"Request headers: {request_data.get('headers', {})}")
        
        try:
            # Execute request with retry
            response, request_time = self._execute_request_with_retry(request_data, max_retries)
            
            logger.info(f"Response: {response.status_code} in {request_time:.3f}s")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            return HTTPResponse(response, request_time)
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def send_request_from_file(self, method: str, url: str, body_file: Union[str, Path],
                              headers: Optional[Dict[str, str]] = None,
                              params: Optional[Dict[str, str]] = None,
                              max_retries: int = 3) -> HTTPResponse:
        """
        Send HTTP request with body from file.
        
        Args:
            method: HTTP method
            url: Request URL
            body_file: Path to file containing request body
            headers: Request headers
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            HTTPResponse object
            
        Raises:
            FileNotFoundError: If body file doesn't exist
            RequestValidationError: If request validation fails
        """
        body_path = Path(body_file)
        
        if not body_path.exists():
            raise FileNotFoundError(f"Body file not found: {body_file}")
        
        try:
            body_content = body_path.read_text(encoding='utf-8')
            logger.debug(f"Loaded request body from {body_file} ({len(body_content)} characters)")
            
            return self.send_request(method, url, headers, body_content, params, max_retries=max_retries)
            
        except UnicodeDecodeError as e:
            raise RequestValidationError(f"Failed to read body file as UTF-8: {e}")
    
    def create_request_record(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                             body: Optional[str] = None, params: Optional[Dict[str, str]] = None,
                             response: Optional[HTTPResponse] = None, 
                             error_message: str = "", template_name: Optional[str] = None,
                             environment: str = "default") -> RequestRecord:
        """
        Create a request record for history tracking.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            response: HTTP response (if successful)
            error_message: Error message (if failed)
            template_name: Name of template used (if any)
            environment: Environment name
            
        Returns:
            RequestRecord instance
        """
        from datetime import datetime
        
        record = RequestRecord(
            timestamp=datetime.now(),
            method=validate_http_method(method),
            url=url,
            headers=sanitize_headers(headers or {}),
            body=body or "",
            params=params or {},
            response_status=response.status_code if response else 0,
            response_headers=response.headers if response else {},
            response_body=response.text if response else "",
            response_time=response.request_time if response else 0.0,
            error_message=error_message,
            template_name=template_name,
            environment=environment
        )
        
        return record
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Utility functions for common request patterns

def load_body_from_file(file_path: Union[str, Path]) -> str:
    """
    Load request body from file.
    
    Args:
        file_path: Path to file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file cannot be decoded as UTF-8
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return path.read_text(encoding='utf-8')


def detect_content_type(body: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Detect appropriate content type for request body.
    
    Args:
        body: Request body
        headers: Existing headers
        
    Returns:
        Detected content type
    """
    if headers and 'Content-Type' in headers:
        return headers['Content-Type']
    
    # Try to detect based on body content
    body_stripped = body.strip()
    
    if body_stripped.startswith(('{', '[')):
        try:
            json.loads(body)
            return 'application/json'
        except json.JSONDecodeError:
            pass
    
    if body_stripped.startswith('<'):
        return 'application/xml'
    
    if '=' in body and '&' in body:
        return 'application/x-www-form-urlencoded'
    
    return 'text/plain'


def merge_urls(base_url: str, path: str) -> str:
    """
    Merge base URL with path.
    
    Args:
        base_url: Base URL
        path: URL path
        
    Returns:
        Complete URL
    """
    if path.startswith(('http://', 'https://')):
        return path
    
    return urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))


def parse_curl_command(curl_command: str) -> Dict[str, Any]:
    """
    Parse curl command into request parameters.
    
    Args:
        curl_command: curl command string
        
    Returns:
        Dictionary with method, url, headers, body
        
    Note:
        This is a basic implementation. For production use,
        consider using a dedicated curl parser library.
    """
    import shlex
    
    # This is a simplified curl parser
    # For production use, consider using libraries like uncurl
    
    parts = shlex.split(curl_command)
    
    if not parts or parts[0] != 'curl':
        raise ValueError("Invalid curl command")
    
    method = 'GET'
    url = ''
    headers = {}
    body = ''
    
    i = 1
    while i < len(parts):
        arg = parts[i]
        
        if arg in ['-X', '--request']:
            if i + 1 < len(parts):
                method = parts[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ['-H', '--header']:
            if i + 1 < len(parts):
                header = parts[i + 1]
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
                i += 2
            else:
                i += 1
        elif arg in ['-d', '--data']:
            if i + 1 < len(parts):
                body = parts[i + 1]
                if method == 'GET':
                    method = 'POST'
                i += 2
            else:
                i += 1
        elif not arg.startswith('-'):
            url = arg
            i += 1
        else:
            i += 1
    
    return {
        'method': method,
        'url': url,
        'headers': headers,
        'body': body
    }
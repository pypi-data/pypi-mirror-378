"""Request validation and preprocessing utilities."""

import json
import xml.etree.ElementTree as ET
import mimetypes
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode
import logging

from ..storage.models import HTTPMethod, validate_http_method, validate_url, sanitize_headers


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when request validation fails."""
    pass


class PreprocessingError(Exception):
    """Raised when request preprocessing fails."""
    pass


class RequestValidator:
    """Validates and preprocesses HTTP requests."""
    
    def __init__(self):
        self.supported_methods = [method.value for method in HTTPMethod]
        self.methods_without_body = ['GET', 'HEAD', 'OPTIONS']
    
    def validate_method(self, method: str) -> HTTPMethod:
        """
        Validate HTTP method.
        
        Args:
            method: HTTP method string
            
        Returns:
            HTTPMethod enum
            
        Raises:
            ValidationError: If method is invalid
        """
        try:
            return validate_http_method(method)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_url(self, url: str) -> str:
        """
        Validate and normalize URL.
        
        Args:
            url: URL string
            
        Returns:
            Normalized URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        try:
            normalized_url = validate_url(url)
            
            # Additional URL validation
            parsed = urlparse(normalized_url)
            
            if not parsed.netloc:
                raise ValidationError("URL must include a hostname")
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError("URL scheme must be http or https")
            
            return normalized_url
            
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Validate and sanitize headers.
        
        Args:
            headers: Headers dictionary
            
        Returns:
            Sanitized headers dictionary
            
        Raises:
            ValidationError: If headers are invalid
        """
        if not headers:
            return {}
        
        try:
            sanitized = sanitize_headers(headers)
            
            # Validate specific headers
            for key, value in sanitized.items():
                self._validate_header(key, value)
            
            return sanitized
            
        except Exception as e:
            raise ValidationError(f"Invalid headers: {e}")
    
    def _validate_header(self, key: str, value: str) -> None:
        """
        Validate individual header.
        
        Args:
            key: Header name
            value: Header value
            
        Raises:
            ValidationError: If header is invalid
        """
        # Check for forbidden characters in header names
        if not re.match(r'^[a-zA-Z0-9!#$&\-\^_`|~]+$', key):
            raise ValidationError(f"Invalid header name: {key}")
        
        # Check for control characters in header values
        if any(ord(c) < 32 and c not in '\t' for c in value):
            raise ValidationError(f"Invalid control characters in header value: {key}")
        
        # Validate specific headers
        if key.lower() == 'content-length':
            try:
                length = int(value)
                if length < 0:
                    raise ValidationError("Content-Length cannot be negative")
            except ValueError:
                raise ValidationError("Content-Length must be a valid integer")
        
        elif key.lower() == 'content-type':
            self._validate_content_type(value)
    
    def _validate_content_type(self, content_type: str) -> None:
        """
        Validate Content-Type header.
        
        Args:
            content_type: Content-Type header value
            
        Raises:
            ValidationError: If content type is invalid
        """
        # Basic content type validation
        if ';' in content_type:
            main_type = content_type.split(';')[0].strip()
        else:
            main_type = content_type.strip()
        
        if '/' not in main_type:
            raise ValidationError(f"Invalid Content-Type format: {content_type}")
        
        type_part, subtype_part = main_type.split('/', 1)
        
        if not type_part or not subtype_part:
            raise ValidationError(f"Invalid Content-Type format: {content_type}")
    
    def validate_body(self, body: Optional[str], method: str, 
                     content_type: Optional[str] = None) -> Optional[str]:
        """
        Validate request body.
        
        Args:
            body: Request body
            method: HTTP method
            content_type: Content-Type header
            
        Returns:
            Validated body or None
            
        Raises:
            ValidationError: If body is invalid
        """
        if not body:
            return None
        
        # Check if method supports body
        if method.upper() in self.methods_without_body:
            logger.warning(f"Body provided for {method} request, this may not be supported")
        
        # Validate based on content type
        if content_type:
            content_type_lower = content_type.lower()
            
            if 'application/json' in content_type_lower:
                return self._validate_json_body(body)
            elif 'application/xml' in content_type_lower or 'text/xml' in content_type_lower:
                return self._validate_xml_body(body)
            elif 'application/x-www-form-urlencoded' in content_type_lower:
                return self._validate_form_body(body)
        
        # If no specific content type, try to detect and validate
        return self._validate_body_by_detection(body)
    
    def _validate_json_body(self, body: str) -> str:
        """
        Validate JSON body.
        
        Args:
            body: JSON body string
            
        Returns:
            Validated JSON body
            
        Raises:
            ValidationError: If JSON is invalid
        """
        try:
            # Parse and re-serialize to validate and normalize
            parsed = json.loads(body)
            return json.dumps(parsed, separators=(',', ':'))
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON body: {e}")
    
    def _validate_xml_body(self, body: str) -> str:
        """
        Validate XML body.
        
        Args:
            body: XML body string
            
        Returns:
            Validated XML body
            
        Raises:
            ValidationError: If XML is invalid
        """
        try:
            # Parse XML to validate syntax
            ET.fromstring(body)
            return body
        except ET.ParseError as e:
            raise ValidationError(f"Invalid XML body: {e}")
    
    def _validate_form_body(self, body: str) -> str:
        """
        Validate form-encoded body.
        
        Args:
            body: Form-encoded body string
            
        Returns:
            Validated form body
            
        Raises:
            ValidationError: If form data is invalid
        """
        try:
            # Parse and re-encode to validate
            parsed = parse_qs(body, strict_parsing=True)
            
            # Flatten single-value lists
            flattened = {}
            for key, values in parsed.items():
                if len(values) == 1:
                    flattened[key] = values[0]
                else:
                    flattened[key] = values
            
            return urlencode(flattened, doseq=True)
            
        except ValueError as e:
            raise ValidationError(f"Invalid form data: {e}")
    
    def _validate_body_by_detection(self, body: str) -> str:
        """
        Validate body by detecting content type.
        
        Args:
            body: Request body
            
        Returns:
            Validated body
        """
        body_stripped = body.strip()
        
        # Try JSON first
        if body_stripped.startswith(('{', '[')):
            try:
                return self._validate_json_body(body)
            except ValidationError:
                pass
        
        # Try XML
        if body_stripped.startswith('<'):
            try:
                return self._validate_xml_body(body)
            except ValidationError:
                pass
        
        # Try form data
        if '=' in body and ('&' in body or body.count('=') == 1):
            try:
                return self._validate_form_body(body)
            except ValidationError:
                pass
        
        # Return as-is for plain text
        return body
    
    def validate_params(self, params: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Validate query parameters.
        
        Args:
            params: Query parameters dictionary
            
        Returns:
            Validated parameters
            
        Raises:
            ValidationError: If parameters are invalid
        """
        if not params:
            return {}
        
        validated = {}
        
        for key, value in params.items():
            if not isinstance(key, str):
                raise ValidationError(f"Parameter key must be string: {key}")
            
            if not isinstance(value, str):
                # Convert to string if possible
                try:
                    value = str(value)
                except Exception:
                    raise ValidationError(f"Parameter value must be convertible to string: {key}={value}")
            
            # Validate parameter name (basic validation)
            if not key:
                raise ValidationError("Parameter key cannot be empty")
            
            validated[key] = value
        
        return validated
    
    def validate_complete_request(self, method: str, url: str, 
                                 headers: Optional[Dict[str, str]] = None,
                                 body: Optional[str] = None,
                                 params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate complete request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            
        Returns:
            Dictionary with validated request components
            
        Raises:
            ValidationError: If any component is invalid
        """
        validated = {}
        
        # Validate method
        validated['method'] = self.validate_method(method)
        
        # Validate URL
        validated['url'] = self.validate_url(url)
        
        # Validate headers
        validated['headers'] = self.validate_headers(headers)
        
        # Validate parameters
        validated['params'] = self.validate_params(params)
        
        # Get content type for body validation
        content_type = validated['headers'].get('Content-Type')
        
        # Validate body
        validated['body'] = self.validate_body(body, method, content_type)
        
        return validated


class RequestPreprocessor:
    """Preprocesses requests for execution."""
    
    def __init__(self):
        self.validator = RequestValidator()
    
    def detect_content_type(self, body: Optional[str], 
                           headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Detect appropriate content type for request body.
        
        Args:
            body: Request body
            headers: Existing headers
            
        Returns:
            Detected content type or None
        """
        if not body:
            return None
        
        # Check if Content-Type already specified
        if headers:
            for key, value in headers.items():
                if key.lower() == 'content-type':
                    return value
        
        body_stripped = body.strip()
        
        # Detect JSON
        if body_stripped.startswith(('{', '[')):
            try:
                json.loads(body)
                return 'application/json'
            except json.JSONDecodeError:
                pass
        
        # Detect XML
        if body_stripped.startswith('<'):
            try:
                ET.fromstring(body)
                return 'application/xml'
            except ET.ParseError:
                pass
        
        # Detect form data
        if '=' in body and ('&' in body or body.count('=') == 1):
            try:
                parse_qs(body, strict_parsing=True)
                return 'application/x-www-form-urlencoded'
            except ValueError:
                pass
        
        # Default to plain text
        return 'text/plain'
    
    def load_body_from_file(self, file_path: Union[str, Path]) -> Tuple[str, Optional[str]]:
        """
        Load request body from file and detect content type.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (body_content, detected_content_type)
            
        Raises:
            PreprocessingError: If file cannot be loaded
        """
        path = Path(file_path)
        
        if not path.exists():
            raise PreprocessingError(f"File not found: {file_path}")
        
        try:
            body = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try reading as binary for non-text files
            try:
                body = path.read_bytes().decode('utf-8', errors='replace')
                logger.warning(f"File {file_path} contains non-UTF-8 characters, some may be replaced")
            except Exception as e:
                raise PreprocessingError(f"Failed to read file {file_path}: {e}")
        except Exception as e:
            raise PreprocessingError(f"Failed to read file {file_path}: {e}")
        
        # Detect content type based on file extension and content
        content_type = None
        
        # Try MIME type detection based on file extension
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type:
            content_type = mime_type
        else:
            # Detect based on content
            content_type = self.detect_content_type(body)
        
        logger.debug(f"Loaded {len(body)} characters from {file_path}, detected content type: {content_type}")
        
        return body, content_type
    
    def merge_headers(self, base_headers: Optional[Dict[str, str]], 
                     additional_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Merge headers with case-insensitive handling.
        
        Args:
            base_headers: Base headers
            additional_headers: Additional headers to merge
            
        Returns:
            Merged headers dictionary
        """
        merged = {}
        
        # Add base headers
        if base_headers:
            for key, value in base_headers.items():
                merged[key] = value
        
        # Add additional headers (case-insensitive override)
        if additional_headers:
            for key, value in additional_headers.items():
                # Check for existing header with different case
                existing_key = None
                for existing in merged.keys():
                    if existing.lower() == key.lower():
                        existing_key = existing
                        break
                
                if existing_key:
                    # Replace existing header
                    del merged[existing_key]
                
                merged[key] = value
        
        return merged
    
    def add_default_headers(self, headers: Optional[Dict[str, str]], 
                           body: Optional[str] = None) -> Dict[str, str]:
        """
        Add default headers based on request content.
        
        Args:
            headers: Existing headers
            body: Request body
            
        Returns:
            Headers with defaults added
        """
        result = headers.copy() if headers else {}
        
        # Add Content-Type if body exists and no Content-Type specified
        if body and not any(key.lower() == 'content-type' for key in result.keys()):
            content_type = self.detect_content_type(body)
            if content_type:
                result['Content-Type'] = content_type
        
        # Add Content-Length if body exists
        if body and not any(key.lower() == 'content-length' for key in result.keys()):
            result['Content-Length'] = str(len(body.encode('utf-8')))
        
        # Add User-Agent if not specified
        if not any(key.lower() == 'user-agent' for key in result.keys()):
            result['User-Agent'] = 'Agentic-API-Tester/0.1.0'
        
        # Add Accept if not specified
        if not any(key.lower() == 'accept' for key in result.keys()):
            result['Accept'] = '*/*'
        
        return result
    
    def preprocess_request(self, method: str, url: str,
                          headers: Optional[Dict[str, str]] = None,
                          body: Optional[str] = None,
                          params: Optional[Dict[str, str]] = None,
                          body_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Preprocess complete request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            body_file: Path to file containing body
            
        Returns:
            Dictionary with preprocessed request components
            
        Raises:
            ValidationError: If validation fails
            PreprocessingError: If preprocessing fails
        """
        # Load body from file if specified
        if body_file:
            if body:
                raise PreprocessingError("Cannot specify both body and body_file")
            
            body, detected_content_type = self.load_body_from_file(body_file)
            
            # Add detected content type to headers if not already specified
            if detected_content_type and headers:
                if not any(key.lower() == 'content-type' for key in headers.keys()):
                    headers = headers.copy()
                    headers['Content-Type'] = detected_content_type
            elif detected_content_type:
                headers = {'Content-Type': detected_content_type}
        
        # Add default headers
        processed_headers = self.add_default_headers(headers, body)
        
        # Validate complete request
        validated = self.validator.validate_complete_request(
            method, url, processed_headers, body, params
        )
        
        logger.debug(f"Preprocessed {method.upper()} request to {url}")
        
        return validated


# Utility functions

def is_json_content(content_type: Optional[str]) -> bool:
    """Check if content type indicates JSON."""
    if not content_type:
        return False
    return 'application/json' in content_type.lower()


def is_xml_content(content_type: Optional[str]) -> bool:
    """Check if content type indicates XML."""
    if not content_type:
        return False
    content_type_lower = content_type.lower()
    return 'application/xml' in content_type_lower or 'text/xml' in content_type_lower


def is_form_content(content_type: Optional[str]) -> bool:
    """Check if content type indicates form data."""
    if not content_type:
        return False
    return 'application/x-www-form-urlencoded' in content_type.lower()


def is_multipart_content(content_type: Optional[str]) -> bool:
    """Check if content type indicates multipart data."""
    if not content_type:
        return False
    return 'multipart/' in content_type.lower()


def extract_charset_from_content_type(content_type: str) -> Optional[str]:
    """Extract charset from Content-Type header."""
    if 'charset=' not in content_type.lower():
        return None
    
    # Find charset parameter
    parts = content_type.split(';')
    for part in parts[1:]:  # Skip main type
        part = part.strip()
        if part.lower().startswith('charset='):
            charset = part.split('=', 1)[1].strip()
            # Remove quotes if present
            if charset.startswith('"') and charset.endswith('"'):
                charset = charset[1:-1]
            return charset
    
    return None
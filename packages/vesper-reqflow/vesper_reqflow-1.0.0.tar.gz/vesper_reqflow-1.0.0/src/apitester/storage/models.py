"""Data models for Agentic API Tester with serialization support."""

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Union
from enum import Enum


class HTTPMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ContentType(str, Enum):
    """Common content types."""
    JSON = "application/json"
    XML = "application/xml"
    FORM_DATA = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain"
    HTML = "text/html"


@dataclass
class RequestTemplate:
    """Template for storing reusable API requests."""
    name: str
    method: HTTPMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    params: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure method is HTTPMethod enum
        if isinstance(self.method, str):
            self.method = HTTPMethod(self.method.upper())
        
        # Ensure timestamps are datetime objects
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['method'] = self.method.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestTemplate':
        """Create instance from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle method field
        if 'method' in data and isinstance(data['method'], str):
            data['method'] = HTTPMethod(data['method'])
        
        # Ensure required fields have defaults
        data.setdefault('headers', {})
        data.setdefault('params', {})
        data.setdefault('body', '')
        data.setdefault('description', '')
        data.setdefault('tags', [])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RequestTemplate':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """
        Validate template data.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Template name is required")
        
        if not self.url or not self.url.strip():
            errors.append("URL is required")
        
        # Basic URL validation
        if self.url and not (self.url.startswith('http://') or self.url.startswith('https://')):
            errors.append("URL must start with http:// or https://")
        
        # Validate headers
        if self.headers:
            for key, value in self.headers.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"Header '{key}' must have string key and value")
        
        # Validate params
        if self.params:
            for key, value in self.params.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"Parameter '{key}' must have string key and value")
        
        return errors
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()


@dataclass
class RequestRecord:
    """Record of an executed API request for history tracking."""
    timestamp: datetime
    method: HTTPMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    params: Dict[str, str] = field(default_factory=dict)
    response_status: int = 0
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: str = ""
    response_time: float = 0.0
    error_message: str = ""
    template_name: Optional[str] = None
    environment: str = "default"
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure method is HTTPMethod enum
        if isinstance(self.method, str):
            self.method = HTTPMethod(self.method.upper())
        
        # Ensure timestamp is datetime object
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['method'] = self.method.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestRecord':
        """Create instance from dictionary."""
        # Handle datetime field
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Handle method field
        if 'method' in data and isinstance(data['method'], str):
            data['method'] = HTTPMethod(data['method'])
        
        # Ensure required fields have defaults
        data.setdefault('headers', {})
        data.setdefault('params', {})
        data.setdefault('response_headers', {})
        data.setdefault('body', '')
        data.setdefault('response_body', '')
        data.setdefault('error_message', '')
        data.setdefault('environment', 'default')
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RequestRecord':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def was_successful(self) -> bool:
        """Check if the request was successful (2xx status code)."""
        return 200 <= self.response_status < 300
    
    def get_status_category(self) -> str:
        """Get status code category for color coding."""
        if 200 <= self.response_status < 300:
            return "success"
        elif 300 <= self.response_status < 400:
            return "redirect"
        elif 400 <= self.response_status < 500:
            return "client_error"
        elif 500 <= self.response_status < 600:
            return "server_error"
        else:
            return "unknown"


@dataclass
class Environment:
    """Environment configuration with variables."""
    name: str
    variables: Dict[str, str] = field(default_factory=dict)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure timestamps are datetime objects
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Environment':
        """Create instance from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Ensure required fields have defaults
        data.setdefault('variables', {})
        data.setdefault('description', '')
        data.setdefault('is_active', False)
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Environment':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def set_variable(self, key: str, value: str) -> None:
        """Set environment variable."""
        self.variables[key] = value
        self.update_timestamp()
    
    def get_variable(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return self.variables.get(key, default)
    
    def delete_variable(self, key: str) -> bool:
        """Delete environment variable."""
        if key in self.variables:
            del self.variables[key]
            self.update_timestamp()
            return True
        return False
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
    
    def validate(self) -> List[str]:
        """
        Validate environment data.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Environment name is required")
        
        # Validate variable names (should be valid identifiers)
        for key in self.variables.keys():
            if not key.replace('_', '').replace('-', '').isalnum():
                errors.append(f"Variable name '{key}' contains invalid characters")
        
        return errors


@dataclass
class CacheEntry:
    """Cache entry for storing API responses."""
    key: str
    response_status: int
    response_headers: Dict[str, str]
    response_body: str
    created_at: datetime
    ttl: int
    hit_count: int = 0
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create instance from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        data.setdefault('response_headers', {})
        data.setdefault('hit_count', 0)
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CacheEntry':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl <= 0:
            return False  # No expiration
        
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl
    
    def increment_hit_count(self) -> None:
        """Increment cache hit counter."""
        self.hit_count += 1


# Utility functions for model validation and conversion

def validate_http_method(method: str) -> HTTPMethod:
    """
    Validate and convert HTTP method string.
    
    Args:
        method: HTTP method string
        
    Returns:
        HTTPMethod: Validated HTTP method enum
        
    Raises:
        ValueError: If method is not supported
    """
    try:
        return HTTPMethod(method.upper())
    except ValueError:
        valid_methods = [m.value for m in HTTPMethod]
        raise ValueError(f"Unsupported HTTP method '{method}'. Valid methods: {valid_methods}")


def validate_url(url: str) -> str:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        str: Validated URL
        
    Raises:
        ValueError: If URL format is invalid
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
    
    url = url.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValueError("URL must start with http:// or https://")
    
    return url


def sanitize_headers(headers: Dict[str, Any]) -> Dict[str, str]:
    """
    Sanitize headers dictionary to ensure string keys and values.
    
    Args:
        headers: Headers dictionary
        
    Returns:
        Dict[str, str]: Sanitized headers
    """
    if not headers:
        return {}
    
    sanitized = {}
    for key, value in headers.items():
        if not isinstance(key, str):
            key = str(key)
        if not isinstance(value, str):
            value = str(value)
        sanitized[key] = value
    
    return sanitized


def merge_headers(base_headers: Dict[str, str], override_headers: Dict[str, str]) -> Dict[str, str]:
    """
    Merge headers with override taking precedence.
    
    Args:
        base_headers: Base headers dictionary
        override_headers: Override headers dictionary
        
    Returns:
        Dict[str, str]: Merged headers
    """
    merged = base_headers.copy()
    merged.update(override_headers)
    return merged
"""
Custom exception hierarchy for Agentic API Tester CLI.

This module defines all custom exceptions used throughout the application,
providing clear error messages and suggested solutions for users.
"""

from typing import Optional, Dict, Any, List
import traceback


class APITesterError(Exception):
    """Base exception for all API Tester errors."""
    
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return formatted error message with suggestion if available."""
        result = self.message
        if self.suggestion:
            result += f"\n💡 Suggestion: {self.suggestion}"
        if self.error_code:
            result += f"\n🔍 Error Code: {self.error_code}"
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "suggestion": self.suggestion,
            "error_code": self.error_code,
            "details": self.details,
            "traceback": traceback.format_exc() if hasattr(self, '__traceback__') else None
        }


# Configuration Errors
class ConfigurationError(APITesterError):
    """Raised when there's an issue with configuration."""
    
    def __init__(self, message: str, config_path: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check your configuration file at {config_path}" if config_path 
            else "Verify your configuration settings"
        )
        super().__init__(message, suggestion, "CONFIG_ERROR", **kwargs)
        self.config_path = config_path


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid or malformed."""
    
    def __init__(self, message: str, config_path: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            "Run 'apitester config validate' to check your configuration"
        )
        super().__init__(message, config_path=config_path, suggestion=suggestion, **kwargs)


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Add '{config_key}' to your configuration" if config_key
            else "Run 'apitester config --generate' to create a default configuration"
        )
        super().__init__(message, suggestion=suggestion, **kwargs)
        self.config_key = config_key


# Connection Errors
class ConnectionError(APITesterError):
    """Base class for connection-related errors."""
    
    def __init__(self, message: str, host: Optional[str] = None, port: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port


class RedisConnectionError(ConnectionError):
    """Raised when Redis connection fails."""
    
    def __init__(self, message: str, host: str = "localhost", port: int = 6379, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Ensure Redis is running on {host}:{port}. "
            "Try: redis-server or docker run -p 6379:6379 redis:alpine"
        )
        super().__init__(
            message, 
            host=host, 
            port=port, 
            suggestion=suggestion,
            error_code="REDIS_CONNECTION_ERROR",
            **kwargs
        )


class NetworkError(ConnectionError):
    """Raised when network requests fail."""
    
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            "Check your internet connection and verify the URL is correct"
        )
        super().__init__(
            message, 
            suggestion=suggestion,
            error_code="NETWORK_ERROR",
            **kwargs
        )
        self.url = url


class TimeoutError(NetworkError):
    """Raised when requests timeout."""
    
    def __init__(self, message: str, timeout: Optional[float] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Increase timeout (current: {timeout}s) or check server responsiveness"
            if timeout else "Increase timeout or check server responsiveness"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="TIMEOUT_ERROR",
            **kwargs
        )
        self.timeout = timeout


# Authentication Errors
class AuthenticationError(APITesterError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            "Verify your API key, token, or credentials are correct and not expired"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="AUTH_ERROR",
            **kwargs
        )
        self.auth_type = auth_type


class InvalidAPIKeyError(AuthenticationError):
    """Raised when API key is invalid or expired."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check your {provider} API key and ensure it's not expired"
            if provider else "Check your API key and ensure it's not expired"
        )
        super().__init__(
            message,
            auth_type="api_key",
            suggestion=suggestion,
            **kwargs
        )
        self.provider = provider


# Template Errors
class TemplateError(APITesterError):
    """Base class for template-related errors."""
    
    def __init__(self, message: str, template_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.template_name = template_name


class TemplateNotFoundError(TemplateError):
    """Raised when a template is not found."""
    
    def __init__(self, template_name: str, **kwargs):
        message = f"Template '{template_name}' not found"
        suggestion = kwargs.get('suggestion') or (
            f"Use 'apitester template list' to see available templates or "
            f"create it with 'apitester template save {template_name} ...'"
        )
        super().__init__(
            message,
            template_name=template_name,
            suggestion=suggestion,
            error_code="TEMPLATE_NOT_FOUND",
            **kwargs
        )


class InvalidTemplateError(TemplateError):
    """Raised when a template is invalid or malformed."""
    
    def __init__(self, message: str, template_name: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            "Check template syntax and ensure all required fields are present"
        )
        super().__init__(
            message,
            template_name=template_name,
            suggestion=suggestion,
            error_code="INVALID_TEMPLATE",
            **kwargs
        )


class VariableSubstitutionError(TemplateError):
    """Raised when variable substitution fails."""
    
    def __init__(self, message: str, variable_name: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Define variable '{variable_name}' in your environment or pass it with --var"
            if variable_name else "Check that all required variables are defined"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="VARIABLE_SUBSTITUTION_ERROR",
            **kwargs
        )
        self.variable_name = variable_name


# Environment Errors
class EnvironmentError(APITesterError):
    """Base class for environment-related errors."""
    
    def __init__(self, message: str, environment_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.environment_name = environment_name


class EnvironmentNotFoundError(EnvironmentError):
    """Raised when an environment is not found."""
    
    def __init__(self, environment_name: str, **kwargs):
        message = f"Environment '{environment_name}' not found"
        suggestion = kwargs.get('suggestion') or (
            f"Use 'apitester env list' to see available environments or "
            f"create it with 'apitester env create {environment_name}'"
        )
        super().__init__(
            message,
            environment_name=environment_name,
            suggestion=suggestion,
            error_code="ENVIRONMENT_NOT_FOUND",
            **kwargs
        )


# Request Errors
class RequestError(APITesterError):
    """Base class for HTTP request errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class HTTPError(RequestError):
    """Raised when HTTP request returns an error status."""
    
    def __init__(self, message: str, status_code: int, url: Optional[str] = None, **kwargs):
        suggestion = self._get_status_suggestion(status_code)
        super().__init__(
            message,
            status_code=status_code,
            suggestion=suggestion,
            error_code=f"HTTP_{status_code}",
            **kwargs
        )
        self.url = url
    
    @staticmethod
    def _get_status_suggestion(status_code: int) -> str:
        """Get suggestion based on HTTP status code."""
        suggestions = {
            400: "Check request syntax, parameters, and body format",
            401: "Verify authentication credentials (API key, token, etc.)",
            403: "Check permissions - you may not have access to this resource",
            404: "Verify the URL is correct and the resource exists",
            405: "Check if you're using the correct HTTP method (GET, POST, etc.)",
            408: "Request timed out - try again or increase timeout",
            409: "Resource conflict - check if resource already exists",
            422: "Validation error - check request body and parameters",
            429: "Rate limit exceeded - wait before making more requests",
            500: "Server error - try again later or contact API provider",
            502: "Bad gateway - API server may be down",
            503: "Service unavailable - API server is temporarily down",
            504: "Gateway timeout - API server is not responding"
        }
        return suggestions.get(status_code, "Check API documentation for this status code")


class InvalidRequestError(RequestError):
    """Raised when request parameters are invalid."""
    
    def __init__(self, message: str, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            "Check request method, URL, headers, and body format"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="INVALID_REQUEST",
            **kwargs
        )


# Data Errors
class DataError(APITesterError):
    """Base class for data-related errors."""
    pass


class SerializationError(DataError):
    """Raised when data serialization/deserialization fails."""
    
    def __init__(self, message: str, data_format: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check {data_format} format and syntax" if data_format
            else "Check data format and syntax"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="SERIALIZATION_ERROR",
            **kwargs
        )
        self.data_format = data_format


class ValidationError(DataError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check the value for field '{field_name}'" if field_name
            else "Check data values and types"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="VALIDATION_ERROR",
            **kwargs
        )
        self.field_name = field_name


# AI Errors
class AIError(APITesterError):
    """Base class for AI-related errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider


class AIProviderError(AIError):
    """Raised when AI provider API fails."""
    
    def __init__(self, message: str, provider: str, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check your {provider} API key and quota limits"
        )
        super().__init__(
            message,
            provider=provider,
            suggestion=suggestion,
            error_code="AI_PROVIDER_ERROR",
            **kwargs
        )


class AINotConfiguredError(AIError):
    """Raised when AI features are used but not configured."""
    
    def __init__(self, **kwargs):
        message = "AI features are not configured"
        suggestion = kwargs.get('suggestion') or (
            "Configure AI with 'apitester ai configure --provider <provider> --api-key <key>'"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="AI_NOT_CONFIGURED",
            **kwargs
        )


# File System Errors
class FileSystemError(APITesterError):
    """Base class for file system errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path


class FileNotFoundError(FileSystemError):
    """Raised when a required file is not found."""
    
    def __init__(self, file_path: str, **kwargs):
        message = f"File not found: {file_path}"
        suggestion = kwargs.get('suggestion') or (
            f"Ensure the file '{file_path}' exists and you have read permissions"
        )
        super().__init__(
            message,
            file_path=file_path,
            suggestion=suggestion,
            error_code="FILE_NOT_FOUND",
            **kwargs
        )


class PermissionError(FileSystemError):
    """Raised when file permissions are insufficient."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        suggestion = kwargs.get('suggestion') or (
            f"Check file permissions for '{file_path}'" if file_path
            else "Check file and directory permissions"
        )
        super().__init__(
            message,
            file_path=file_path,
            suggestion=suggestion,
            error_code="PERMISSION_ERROR",
            **kwargs
        )


# Cache Errors
class CacheError(APITesterError):
    """Base class for cache-related errors."""
    pass


class CacheUnavailableError(CacheError):
    """Raised when cache is unavailable but required."""
    
    def __init__(self, **kwargs):
        message = "Cache is unavailable"
        suggestion = kwargs.get('suggestion') or (
            "Check Redis connection or disable caching in configuration"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="CACHE_UNAVAILABLE",
            **kwargs
        )


# CLI Errors
class CLIError(APITesterError):
    """Base class for CLI-specific errors."""
    pass


class InvalidCommandError(CLIError):
    """Raised when CLI command is invalid."""
    
    def __init__(self, command: str, **kwargs):
        message = f"Invalid command: {command}"
        suggestion = kwargs.get('suggestion') or (
            "Use 'apitester --help' to see available commands"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="INVALID_COMMAND",
            **kwargs
        )
        self.command = command


class MissingArgumentError(CLIError):
    """Raised when required CLI argument is missing."""
    
    def __init__(self, argument: str, **kwargs):
        message = f"Missing required argument: {argument}"
        suggestion = kwargs.get('suggestion') or (
            f"Provide the required argument '{argument}'"
        )
        super().__init__(
            message,
            suggestion=suggestion,
            error_code="MISSING_ARGUMENT",
            **kwargs
        )
        self.argument = argument


# Utility functions for error handling
def handle_redis_unavailable() -> None:
    """Handle graceful degradation when Redis is unavailable."""
    from .core.logging import get_logger
    logger = get_logger(__name__)
    
    logger.warning(
        "Redis is unavailable. Running in degraded mode without caching and history."
    )


def format_error_for_user(error: Exception) -> str:
    """Format error message for user-friendly display."""
    if isinstance(error, APITesterError):
        return str(error)
    
    # Handle common Python exceptions
    error_messages = {
        ConnectionRefusedError: "Connection refused. Check if the service is running.",
        TimeoutError: "Operation timed out. Try again or increase timeout.",
        PermissionError: "Permission denied. Check file and directory permissions.",
        FileNotFoundError: "File not found. Check the file path.",
        ValueError: "Invalid value provided. Check your input.",
        KeyError: "Required key not found. Check your configuration.",
    }
    
    error_type = type(error)
    if error_type in error_messages:
        return f"{error_messages[error_type]}\n💡 Suggestion: {str(error)}"
    
    return f"Unexpected error: {str(error)}"


def get_error_suggestions(error: Exception) -> List[str]:
    """Get list of suggestions for resolving an error."""
    suggestions = []
    
    if isinstance(error, APITesterError) and error.suggestion:
        suggestions.append(error.suggestion)
    
    # Add general suggestions based on error type
    if isinstance(error, (ConnectionRefusedError, RedisConnectionError)):
        suggestions.extend([
            "Check if Redis is running: redis-cli ping",
            "Start Redis: redis-server or docker run -p 6379:6379 redis:alpine",
            "Verify Redis configuration in your config file"
        ])
    
    elif isinstance(error, (NetworkError, TimeoutError)):
        suggestions.extend([
            "Check your internet connection",
            "Verify the URL is correct and accessible",
            "Try increasing the timeout value"
        ])
    
    elif isinstance(error, AuthenticationError):
        suggestions.extend([
            "Verify your API key or token is correct",
            "Check if your credentials have expired",
            "Ensure you have the necessary permissions"
        ])
    
    return suggestions
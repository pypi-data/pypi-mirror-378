"""
Comprehensive error handling system for graceful degradation and user-friendly error messages.

This module provides centralized error handling, graceful degradation when services
are unavailable, and user-friendly error reporting with suggested solutions.
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable, List, Type
from functools import wraps
import redis
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..exceptions import (
    APITesterError,
    RedisConnectionError,
    NetworkError,
    AuthenticationError,
    ConfigurationError,
    TemplateError,
    EnvironmentError,
    format_error_for_user,
    get_error_suggestions,
    handle_redis_unavailable
)
from .logging import get_logger


class ErrorHandler:
    """Centralized error handler for the application."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(stderr=True)
        self.logger = get_logger()
        self._degraded_mode = False
        self._redis_available = True
        self._error_counts: Dict[str, int] = {}
    
    @property
    def is_degraded_mode(self) -> bool:
        """Check if application is running in degraded mode."""
        return self._degraded_mode
    
    @property
    def is_redis_available(self) -> bool:
        """Check if Redis is available."""
        return self._redis_available
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[str] = None,
        show_traceback: bool = False,
        exit_on_critical: bool = True
    ) -> bool:
        """
        Handle an error with appropriate logging and user feedback.
        
        Returns:
            bool: True if error was handled gracefully, False if critical
        """
        error_type = type(error).__name__
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1
        
        # Log the error
        self.logger.log_error(error, context=context)
        
        # Handle specific error types
        if isinstance(error, RedisConnectionError):
            return self._handle_redis_error(error)
        elif isinstance(error, NetworkError):
            return self._handle_network_error(error)
        elif isinstance(error, AuthenticationError):
            return self._handle_auth_error(error)
        elif isinstance(error, ConfigurationError):
            return self._handle_config_error(error)
        elif isinstance(error, (TemplateError, EnvironmentError)):
            return self._handle_data_error(error)
        elif isinstance(error, APITesterError):
            return self._handle_api_tester_error(error)
        else:
            return self._handle_unexpected_error(error, show_traceback, exit_on_critical)
    
    def _handle_redis_error(self, error: RedisConnectionError) -> bool:
        """Handle Redis connection errors with graceful degradation."""
        if not self._degraded_mode:
            self._degraded_mode = True
            self._redis_available = False
            handle_redis_unavailable()
            
            self.console.print(
                Panel(
                    Text.from_markup(
                        f"[yellow]⚠️  Redis Unavailable[/yellow]\n\n"
                        f"[white]{error.message}[/white]\n\n"
                        f"[dim]Running in degraded mode without caching and history.[/dim]\n"
                        f"[dim]💡 {error.suggestion}[/dim]"
                    ),
                    title="[yellow]Warning[/yellow]",
                    border_style="yellow"
                )
            )
        
        return True  # Graceful degradation
    
    def _handle_network_error(self, error: NetworkError) -> bool:
        """Handle network errors."""
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[red]🌐 Network Error[/red]\n\n"
                    f"[white]{error.message}[/white]\n\n"
                    f"[dim]💡 {error.suggestion}[/dim]"
                ),
                title="[red]Network Error[/red]",
                border_style="red"
            )
        )
        return False  # Not recoverable
    
    def _handle_auth_error(self, error: AuthenticationError) -> bool:
        """Handle authentication errors."""
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[red]🔐 Authentication Error[/red]\n\n"
                    f"[white]{error.message}[/white]\n\n"
                    f"[dim]💡 {error.suggestion}[/dim]"
                ),
                title="[red]Authentication Failed[/red]",
                border_style="red"
            )
        )
        return False  # Not recoverable
    
    def _handle_config_error(self, error: ConfigurationError) -> bool:
        """Handle configuration errors."""
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[yellow]⚙️  Configuration Error[/yellow]\n\n"
                    f"[white]{error.message}[/white]\n\n"
                    f"[dim]💡 {error.suggestion}[/dim]"
                ),
                title="[yellow]Configuration Issue[/yellow]",
                border_style="yellow"
            )
        )
        return False  # Requires user action
    
    def _handle_data_error(self, error: APITesterError) -> bool:
        """Handle template and environment errors."""
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[yellow]📝 Data Error[/yellow]\n\n"
                    f"[white]{error.message}[/white]\n\n"
                    f"[dim]💡 {error.suggestion}[/dim]"
                ),
                title="[yellow]Data Issue[/yellow]",
                border_style="yellow"
            )
        )
        return False  # Requires user action
    
    def _handle_api_tester_error(self, error: APITesterError) -> bool:
        """Handle general API Tester errors."""
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[red]❌ Error[/red]\n\n"
                    f"[white]{error.message}[/white]\n\n"
                    f"[dim]💡 {error.suggestion or 'Check the documentation for help'}[/dim]"
                ),
                title="[red]Error[/red]",
                border_style="red"
            )
        )
        return False
    
    def _handle_unexpected_error(
        self,
        error: Exception,
        show_traceback: bool,
        exit_on_critical: bool
    ) -> bool:
        """Handle unexpected errors."""
        error_msg = format_error_for_user(error)
        
        if show_traceback:
            self.console.print(f"\n[red]Traceback:[/red]")
            self.console.print(traceback.format_exc())
        
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[red]💥 Unexpected Error[/red]\n\n"
                    f"[white]{error_msg}[/white]\n\n"
                    f"[dim]This is likely a bug. Please report it with the error details.[/dim]"
                ),
                title="[red]Unexpected Error[/red]",
                border_style="red"
            )
        )
        
        if exit_on_critical:
            self.logger.critical(f"Critical error: {str(error)}")
            sys.exit(1)
        
        return False
    
    def check_redis_availability(self, redis_client) -> bool:
        """Check if Redis is available and update status."""
        try:
            redis_client.ping()
            if not self._redis_available:
                self._redis_available = True
                self._degraded_mode = False
                self.logger.info("Redis connection restored")
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            if self._redis_available:
                self._redis_available = False
                self._degraded_mode = True
                self.logger.warning("Redis connection lost")
            return False
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics for monitoring."""
        return self._error_counts.copy()
    
    def reset_error_statistics(self) -> None:
        """Reset error statistics."""
        self._error_counts.clear()


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(
    error: Exception,
    context: Optional[str] = None,
    show_traceback: bool = False,
    exit_on_critical: bool = True
) -> bool:
    """Handle an error using the global error handler."""
    return get_error_handler().handle_error(
        error, context, show_traceback, exit_on_critical
    )


# Decorators for error handling
def handle_errors(
    context: Optional[str] = None,
    show_traceback: bool = False,
    exit_on_critical: bool = True,
    graceful_degradation: bool = False
):
    """Decorator to handle errors in functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handled = handle_error(
                    e, 
                    context or f"{func.__module__}.{func.__name__}",
                    show_traceback,
                    exit_on_critical and not graceful_degradation
                )
                
                if graceful_degradation and handled:
                    return None
                elif not handled and not exit_on_critical:
                    raise
        
        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: Optional[List[Type[Exception]]] = None
):
    """Decorator to retry functions on specific errors."""
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            retry_exceptions = retry_on or [NetworkError, RedisConnectionError]
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries or not any(isinstance(e, exc) for exc in retry_exceptions):
                        raise
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time:.1f}s: {str(e)}"
                    )
                    time.sleep(wait_time)
            
            return None  # Should never reach here
        
        return wrapper
    return decorator


def safe_operation(
    default_return=None,
    log_errors: bool = True,
    context: Optional[str] = None
):
    """Decorator to make operations safe by catching all exceptions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = get_logger()
                    logger.log_error(e, context=context or f"{func.__module__}.{func.__name__}")
                return default_return
        
        return wrapper
    return decorator


# Context managers for error handling
class ErrorContext:
    """Context manager for handling errors in code blocks."""
    
    def __init__(
        self,
        context: str,
        show_traceback: bool = False,
        exit_on_critical: bool = True,
        graceful_degradation: bool = False
    ):
        self.context = context
        self.show_traceback = show_traceback
        self.exit_on_critical = exit_on_critical
        self.graceful_degradation = graceful_degradation
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            handled = handle_error(
                exc_val,
                self.context,
                self.show_traceback,
                self.exit_on_critical and not self.graceful_degradation
            )
            
            if self.graceful_degradation and handled:
                return True  # Suppress the exception
        
        return False  # Let the exception propagate


# Utility functions for error handling
def is_redis_available() -> bool:
    """Check if Redis is available."""
    return get_error_handler().is_redis_available


def is_degraded_mode() -> bool:
    """Check if application is in degraded mode."""
    return get_error_handler().is_degraded_mode


def format_exception_for_user(exc: Exception) -> str:
    """Format exception for user-friendly display."""
    return format_error_for_user(exc)


def get_exception_suggestions(exc: Exception) -> List[str]:
    """Get suggestions for resolving an exception."""
    return get_error_suggestions(exc)


def create_error_report(exc: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """Create a structured error report."""
    return {
        "error_type": type(exc).__name__,
        "message": str(exc),
        "context": context,
        "suggestions": get_exception_suggestions(exc),
        "traceback": traceback.format_exc(),
        "is_api_tester_error": isinstance(exc, APITesterError),
        "error_code": getattr(exc, 'error_code', None),
        "details": getattr(exc, 'details', {})
    }


# Health check functions
def check_system_health() -> Dict[str, Any]:
    """Check overall system health."""
    handler = get_error_handler()
    
    health_status = {
        "redis_available": handler.is_redis_available,
        "degraded_mode": handler.is_degraded_mode,
        "error_counts": handler.get_error_statistics(),
        "status": "healthy"
    }
    
    if handler.is_degraded_mode:
        health_status["status"] = "degraded"
    
    total_errors = sum(handler.get_error_statistics().values())
    if total_errors > 10:  # Threshold for unhealthy
        health_status["status"] = "unhealthy"
    
    return health_status


def reset_health_status() -> None:
    """Reset health status and error counts."""
    get_error_handler().reset_error_statistics()
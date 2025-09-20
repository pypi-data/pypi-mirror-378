"""
Comprehensive logging system for Agentic API Tester CLI.

This module provides structured logging with configurable levels, formatters,
and handlers for different use cases including debugging, performance monitoring,
and error tracking.
"""

import logging
import logging.handlers
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from contextlib import contextmanager
import threading
from dataclasses import dataclass, asdict

from ..exceptions import APITesterError


@dataclass
class LogContext:
    """Context information for structured logging."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    template_name: Optional[str] = None
    environment: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context if available
        if self.include_context and hasattr(record, 'context'):
            log_data["context"] = record.context.to_dict()
        
        # Add exception information
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process',
                              'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_data[key] = value
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stderr.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if self.use_colors:
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build message
        message = record.getMessage()
        
        # Add context if available
        context_str = ""
        if hasattr(record, 'context') and record.context:
            context_parts = []
            ctx = record.context.to_dict()
            if ctx.get('operation'):
                context_parts.append(f"op={ctx['operation']}")
            if ctx.get('request_id'):
                context_parts.append(f"req={ctx['request_id'][:8]}")
            if context_parts:
                context_str = f" [{', '.join(context_parts)}]"
        
        return f"{timestamp} {record.levelname:8} {record.name}{context_str}: {message}"


class PerformanceLogger:
    """Logger for performance monitoring and metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def start_timer(self, name: str) -> None:
        """Start a performance timer."""
        with self._lock:
            self._timers[name] = time.time()
    
    def end_timer(self, name: str, log_level: int = logging.INFO) -> float:
        """End a performance timer and log the duration."""
        with self._lock:
            if name not in self._timers:
                self.logger.warning(f"Timer '{name}' was not started")
                return 0.0
            
            duration = time.time() - self._timers[name]
            del self._timers[name]
            
            self.logger.log(
                log_level,
                f"Performance: {name} completed in {duration:.3f}s",
                extra={"performance_metric": name, "duration": duration}
            )
            
            return duration
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a performance counter."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value
    
    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        with self._lock:
            return self._counters.get(name, 0)
    
    def log_counters(self, log_level: int = logging.INFO) -> None:
        """Log all current counter values."""
        with self._lock:
            if self._counters:
                self.logger.log(
                    log_level,
                    f"Performance counters: {self._counters}",
                    extra={"performance_counters": self._counters.copy()}
                )
    
    @contextmanager
    def timer(self, name: str, log_level: int = logging.INFO):
        """Context manager for timing operations."""
        self.start_timer(name)
        try:
            yield
        finally:
            self.end_timer(name, log_level)


class APITesterLogger:
    """Main logger class for the API Tester application."""
    
    def __init__(self, name: str = "apitester"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.context = LogContext()
        self.performance = PerformanceLogger(self.logger)
        self._configured = False
    
    def configure(
        self,
        level: Union[str, int] = logging.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True,
        structured_logging: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        use_colors: bool = True
    ) -> None:
        """Configure the logger with specified settings."""
        if self._configured:
            return
        
        # Set level
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stderr)
            if structured_logging:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(ColoredFormatter(use_colors))
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        self._configured = True
    
    def set_context(self, **kwargs) -> None:
        """Set logging context."""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
    
    def clear_context(self) -> None:
        """Clear logging context."""
        self.context = LogContext()
    
    def _log_with_context(self, level: int, message: str, **kwargs) -> None:
        """Log message with context."""
        extra = kwargs.copy()
        extra['context'] = self.context
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        """Log HTTP request details."""
        self.info(
            f"HTTP Request: {method} {url}",
            method=method,
            url=url,
            headers=headers,
            body_length=len(body) if body else 0,
            request_id=request_id
        )
    
    def log_response(
        self,
        status_code: int,
        headers: Optional[Dict[str, str]] = None,
        body_length: int = 0,
        duration: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> None:
        """Log HTTP response details."""
        self.info(
            f"HTTP Response: {status_code}",
            status_code=status_code,
            headers=headers,
            body_length=body_length,
            duration=duration,
            request_id=request_id
        )
    
    def log_error(self, error: Exception, **kwargs) -> None:
        """Log error with structured information."""
        if isinstance(error, APITesterError):
            error_data = error.to_dict()
            self.error(
                f"API Tester Error: {error.message}",
                error_type=error.__class__.__name__,
                error_code=error.error_code,
                suggestion=error.suggestion,
                details=error.details,
                **kwargs
            )
        else:
            self.exception(
                f"Unexpected error: {str(error)}",
                error_type=error.__class__.__name__,
                **kwargs
            )
    
    def log_operation_start(self, operation: str, **kwargs) -> None:
        """Log the start of an operation."""
        self.set_context(operation=operation)
        self.info(f"Starting operation: {operation}", **kwargs)
        self.performance.start_timer(operation)
    
    def log_operation_end(self, operation: str, success: bool = True, **kwargs) -> None:
        """Log the end of an operation."""
        duration = self.performance.end_timer(operation, logging.DEBUG)
        status = "completed" if success else "failed"
        self.info(
            f"Operation {status}: {operation} ({duration:.3f}s)",
            operation=operation,
            success=success,
            duration=duration,
            **kwargs
        )
    
    @contextmanager
    def operation(self, name: str, **kwargs):
        """Context manager for logging operations."""
        self.log_operation_start(name, **kwargs)
        try:
            yield
            self.log_operation_end(name, success=True)
        except Exception as e:
            self.log_operation_end(name, success=False)
            self.log_error(e)
            raise


# Global logger instance
_logger_instance: Optional[APITesterLogger] = None
_logger_lock = threading.Lock()


def get_logger(name: Optional[str] = None) -> APITesterLogger:
    """Get or create the global logger instance."""
    global _logger_instance
    
    with _logger_lock:
        if _logger_instance is None:
            _logger_instance = APITesterLogger(name or "apitester")
        return _logger_instance


def configure_logging(
    level: Union[str, int] = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    structured_logging: bool = False,
    **kwargs
) -> None:
    """Configure the global logger."""
    logger = get_logger()
    logger.configure(
        level=level,
        log_file=log_file,
        console_output=console_output,
        structured_logging=structured_logging,
        **kwargs
    )


def set_log_level(level: Union[str, int]) -> None:
    """Set the global log level."""
    logger = get_logger()
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.logger.setLevel(level)


def get_log_level() -> str:
    """Get the current log level."""
    logger = get_logger()
    return logging.getLevelName(logger.logger.level)


# Convenience functions
def debug(message: str, **kwargs) -> None:
    """Log debug message using global logger."""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """Log info message using global logger."""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """Log warning message using global logger."""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """Log error message using global logger."""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """Log critical message using global logger."""
    get_logger().critical(message, **kwargs)


def exception(message: str, **kwargs) -> None:
    """Log exception using global logger."""
    get_logger().exception(message, **kwargs)


# Decorators for automatic logging
def log_function_call(logger: Optional[APITesterLogger] = None):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger()
            func_name = f"{func.__module__}.{func.__name__}"
            
            log.debug(f"Calling function: {func_name}")
            
            try:
                with log.performance.timer(func_name, logging.DEBUG):
                    result = func(*args, **kwargs)
                log.debug(f"Function completed: {func_name}")
                return result
            except Exception as e:
                log.error(f"Function failed: {func_name} - {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_performance(operation_name: Optional[str] = None):
    """Decorator to log function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = get_logger()
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with log.performance.timer(name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator
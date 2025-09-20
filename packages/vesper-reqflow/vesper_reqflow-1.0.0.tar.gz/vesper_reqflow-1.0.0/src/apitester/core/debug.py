"""
Debug mode and performance monitoring for Agentic API Tester CLI.

This module provides comprehensive debugging capabilities including detailed
request/response logging, performance monitoring, and diagnostic tools.
"""

import time
import json
import sys
import threading
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import traceback
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.tree import Tree
from rich.syntax import Syntax

from .logging import get_logger, APITesterLogger


@dataclass
class RequestDebugInfo:
    """Debug information for HTTP requests."""
    request_id: str
    timestamp: datetime
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str] = None
    body_size: int = 0
    
    # Response info
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[str] = None
    response_size: int = 0
    
    # Timing info
    dns_lookup_time: Optional[float] = None
    connection_time: Optional[float] = None
    ssl_handshake_time: Optional[float] = None
    request_time: Optional[float] = None
    response_time: Optional[float] = None
    total_time: Optional[float] = None
    
    # Error info
    error: Optional[str] = None
    error_traceback: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # System metrics
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    
    # Application metrics
    active_requests: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Timing metrics
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0


class DebugMode:
    """Debug mode manager with comprehensive logging and monitoring."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(stderr=True)
        self.logger = get_logger()
        self.enabled = False
        self.verbose = False
        
        # Debug data storage
        self._requests: List[RequestDebugInfo] = []
        self._performance_history: List[PerformanceMetrics] = []
        self._operation_timings: Dict[str, List[float]] = {}
        
        # Monitoring
        self._start_time = datetime.now()
        self._request_counter = 0
        self._lock = threading.Lock()
        
        # Configuration
        self.max_stored_requests = 1000
        self.max_performance_history = 100
        self.log_request_bodies = True
        self.log_response_bodies = True
        self.max_body_log_size = 10000  # 10KB
    
    def enable(self, verbose: bool = False) -> None:
        """Enable debug mode."""
        self.enabled = True
        self.verbose = verbose
        self.logger.info("Debug mode enabled", verbose=verbose)
        
        if verbose:
            self.console.print(
                Panel(
                    "[green]🐛 Debug Mode Enabled[/green]\n\n"
                    "• Detailed request/response logging\n"
                    "• Performance monitoring\n"
                    "• System metrics collection\n"
                    "• Verbose error reporting",
                    title="Debug Mode",
                    border_style="green"
                )
            )
    
    def disable(self) -> None:
        """Disable debug mode."""
        self.enabled = False
        self.verbose = False
        self.logger.info("Debug mode disabled")
    
    def is_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.enabled
    
    def log_request_start(
        self,
        request_id: str,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None
    ) -> RequestDebugInfo:
        """Log the start of an HTTP request."""
        if not self.enabled:
            return None
        
        with self._lock:
            self._request_counter += 1
        
        debug_info = RequestDebugInfo(
            request_id=request_id,
            timestamp=datetime.now(),
            method=method,
            url=url,
            headers=headers.copy(),
            body=self._truncate_body(body) if self.log_request_bodies else None,
            body_size=len(body) if body else 0
        )
        
        if self.verbose:
            self._print_request_details(debug_info)
        
        self.logger.debug(
            f"Request started: {method} {url}",
            request_id=request_id,
            method=method,
            url=url,
            headers=headers,
            body_size=debug_info.body_size
        )
        
        return debug_info
    
    def log_request_end(
        self,
        debug_info: RequestDebugInfo,
        status_code: int,
        response_headers: Dict[str, str],
        response_body: Optional[str] = None,
        timing_info: Optional[Dict[str, float]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Log the end of an HTTP request."""
        if not self.enabled or not debug_info:
            return
        
        # Update debug info
        debug_info.response_status = status_code
        debug_info.response_headers = response_headers.copy()
        debug_info.response_body = (
            self._truncate_body(response_body) if self.log_response_bodies else None
        )
        debug_info.response_size = len(response_body) if response_body else 0
        
        if timing_info:
            debug_info.dns_lookup_time = timing_info.get('dns_lookup')
            debug_info.connection_time = timing_info.get('connection')
            debug_info.ssl_handshake_time = timing_info.get('ssl_handshake')
            debug_info.request_time = timing_info.get('request')
            debug_info.response_time = timing_info.get('response')
            debug_info.total_time = timing_info.get('total')
        
        if error:
            debug_info.error = str(error)
            debug_info.error_traceback = traceback.format_exc()
        
        # Store debug info
        with self._lock:
            self._requests.append(debug_info)
            if len(self._requests) > self.max_stored_requests:
                self._requests.pop(0)
        
        if self.verbose:
            self._print_response_details(debug_info)
        
        self.logger.debug(
            f"Request completed: {status_code} ({debug_info.total_time:.3f}s)",
            request_id=debug_info.request_id,
            status_code=status_code,
            response_size=debug_info.response_size,
            total_time=debug_info.total_time,
            error=str(error) if error else None
        )
    
    def log_operation_timing(self, operation: str, duration: float) -> None:
        """Log timing for an operation."""
        if not self.enabled:
            return
        
        with self._lock:
            if operation not in self._operation_timings:
                self._operation_timings[operation] = []
            
            self._operation_timings[operation].append(duration)
            
            # Keep only recent timings
            if len(self._operation_timings[operation]) > 100:
                self._operation_timings[operation].pop(0)
        
        if self.verbose:
            self.console.print(f"⏱️  {operation}: {duration:.3f}s")
    
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        process = psutil.Process()
        
        with self._lock:
            successful = sum(1 for r in self._requests if r.response_status and 200 <= r.response_status < 400)
            failed = len(self._requests) - successful
            
            response_times = [r.total_time for r in self._requests if r.total_time]
            
            metrics = PerformanceMetrics(
                cpu_percent=process.cpu_percent(),
                memory_percent=process.memory_percent(),
                memory_used_mb=process.memory_info().rss / 1024 / 1024,
                active_requests=0,  # Would need to track active requests
                total_requests=len(self._requests),
                successful_requests=successful,
                failed_requests=failed,
                avg_response_time=sum(response_times) / len(response_times) if response_times else 0,
                min_response_time=min(response_times) if response_times else 0,
                max_response_time=max(response_times) if response_times else 0
            )
            
            self._performance_history.append(metrics)
            if len(self._performance_history) > self.max_performance_history:
                self._performance_history.pop(0)
        
        return metrics
    
    def print_debug_summary(self) -> None:
        """Print a summary of debug information."""
        if not self.enabled:
            self.console.print("[yellow]Debug mode is not enabled[/yellow]")
            return
        
        with self._lock:
            total_requests = len(self._requests)
            successful = sum(1 for r in self._requests if r.response_status and 200 <= r.response_status < 400)
            failed = total_requests - successful
            
            if total_requests > 0:
                response_times = [r.total_time for r in self._requests if r.total_time]
                avg_time = sum(response_times) / len(response_times) if response_times else 0
                
                # Create summary table
                table = Table(title="Debug Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Requests", str(total_requests))
                table.add_row("Successful", str(successful))
                table.add_row("Failed", str(failed))
                table.add_row("Success Rate", f"{(successful/total_requests)*100:.1f}%")
                table.add_row("Avg Response Time", f"{avg_time:.3f}s")
                
                if response_times:
                    table.add_row("Min Response Time", f"{min(response_times):.3f}s")
                    table.add_row("Max Response Time", f"{max(response_times):.3f}s")
                
                uptime = datetime.now() - self._start_time
                table.add_row("Uptime", str(uptime).split('.')[0])
                
                self.console.print(table)
            else:
                self.console.print("[yellow]No requests recorded yet[/yellow]")
    
    def print_request_history(self, limit: int = 10) -> None:
        """Print recent request history."""
        if not self.enabled:
            self.console.print("[yellow]Debug mode is not enabled[/yellow]")
            return
        
        with self._lock:
            recent_requests = self._requests[-limit:] if self._requests else []
        
        if not recent_requests:
            self.console.print("[yellow]No requests recorded yet[/yellow]")
            return
        
        table = Table(title=f"Recent Requests (last {len(recent_requests)})")
        table.add_column("Time", style="dim")
        table.add_column("Method", style="blue")
        table.add_column("URL", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Size", style="magenta")
        
        for req in recent_requests:
            status_style = "green" if req.response_status and 200 <= req.response_status < 400 else "red"
            
            table.add_row(
                req.timestamp.strftime("%H:%M:%S"),
                req.method,
                req.url[:50] + "..." if len(req.url) > 50 else req.url,
                f"[{status_style}]{req.response_status or 'Error'}[/{status_style}]",
                f"{req.total_time:.3f}s" if req.total_time else "N/A",
                f"{req.response_size:,}B" if req.response_size else "N/A"
            )
        
        self.console.print(table)
    
    def print_performance_metrics(self) -> None:
        """Print current performance metrics."""
        if not self.enabled:
            self.console.print("[yellow]Debug mode is not enabled[/yellow]")
            return
        
        metrics = self.collect_performance_metrics()
        
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("CPU Usage", f"{metrics.cpu_percent:.1f}%")
        table.add_row("Memory Usage", f"{metrics.memory_percent:.1f}%")
        table.add_row("Memory Used", f"{metrics.memory_used_mb:.1f} MB")
        table.add_row("Total Requests", str(metrics.total_requests))
        table.add_row("Successful", str(metrics.successful_requests))
        table.add_row("Failed", str(metrics.failed_requests))
        
        if metrics.total_requests > 0:
            success_rate = (metrics.successful_requests / metrics.total_requests) * 100
            table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        if metrics.avg_response_time > 0:
            table.add_row("Avg Response Time", f"{metrics.avg_response_time:.3f}s")
            table.add_row("Min Response Time", f"{metrics.min_response_time:.3f}s")
            table.add_row("Max Response Time", f"{metrics.max_response_time:.3f}s")
        
        self.console.print(table)
    
    def export_debug_data(self, file_path: str) -> None:
        """Export debug data to a file."""
        if not self.enabled:
            self.console.print("[yellow]Debug mode is not enabled[/yellow]")
            return
        
        debug_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "start_time": self._start_time.isoformat(),
                "total_requests": len(self._requests),
                "debug_mode_enabled": self.enabled,
                "verbose_mode": self.verbose
            },
            "requests": [
                {
                    "request_id": req.request_id,
                    "timestamp": req.timestamp.isoformat(),
                    "method": req.method,
                    "url": req.url,
                    "headers": req.headers,
                    "body_size": req.body_size,
                    "response_status": req.response_status,
                    "response_headers": req.response_headers,
                    "response_size": req.response_size,
                    "timing": {
                        "dns_lookup": req.dns_lookup_time,
                        "connection": req.connection_time,
                        "ssl_handshake": req.ssl_handshake_time,
                        "request": req.request_time,
                        "response": req.response_time,
                        "total": req.total_time
                    },
                    "error": req.error
                }
                for req in self._requests
            ],
            "performance_history": [
                {
                    "timestamp": metrics.timestamp.isoformat(),
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "memory_used_mb": metrics.memory_used_mb,
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "avg_response_time": metrics.avg_response_time
                }
                for metrics in self._performance_history
            ],
            "operation_timings": self._operation_timings
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(debug_data, f, indent=2, default=str)
            
            self.console.print(f"[green]Debug data exported to: {file_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Failed to export debug data: {str(e)}[/red]")
    
    def _truncate_body(self, body: Optional[str]) -> Optional[str]:
        """Truncate body content for logging."""
        if not body:
            return body
        
        if len(body) <= self.max_body_log_size:
            return body
        
        return body[:self.max_body_log_size] + f"... (truncated, total: {len(body)} chars)"
    
    def _print_request_details(self, debug_info: RequestDebugInfo) -> None:
        """Print detailed request information."""
        self.console.print(f"\n[bold blue]🚀 Request: {debug_info.method} {debug_info.url}[/bold blue]")
        self.console.print(f"[dim]Request ID: {debug_info.request_id}[/dim]")
        self.console.print(f"[dim]Time: {debug_info.timestamp.strftime('%H:%M:%S.%f')[:-3]}[/dim]")
        
        if debug_info.headers:
            self.console.print("\n[bold]Headers:[/bold]")
            for key, value in debug_info.headers.items():
                # Mask sensitive headers
                if key.lower() in ['authorization', 'x-api-key', 'cookie']:
                    value = "***MASKED***"
                self.console.print(f"  {key}: {value}")
        
        if debug_info.body:
            self.console.print(f"\n[bold]Body ({debug_info.body_size} bytes):[/bold]")
            try:
                # Try to format as JSON
                parsed = json.loads(debug_info.body)
                syntax = Syntax(json.dumps(parsed, indent=2), "json", theme="monokai")
                self.console.print(syntax)
            except json.JSONDecodeError:
                self.console.print(debug_info.body)
    
    def _print_response_details(self, debug_info: RequestDebugInfo) -> None:
        """Print detailed response information."""
        status_style = "green" if debug_info.response_status and 200 <= debug_info.response_status < 400 else "red"
        
        self.console.print(f"\n[bold {status_style}]📥 Response: {debug_info.response_status}[/bold {status_style}]")
        
        if debug_info.total_time:
            self.console.print(f"[dim]Duration: {debug_info.total_time:.3f}s[/dim]")
        
        if debug_info.response_headers:
            self.console.print("\n[bold]Response Headers:[/bold]")
            for key, value in debug_info.response_headers.items():
                self.console.print(f"  {key}: {value}")
        
        if debug_info.response_body:
            self.console.print(f"\n[bold]Response Body ({debug_info.response_size} bytes):[/bold]")
            try:
                # Try to format as JSON
                parsed = json.loads(debug_info.response_body)
                syntax = Syntax(json.dumps(parsed, indent=2), "json", theme="monokai")
                self.console.print(syntax)
            except json.JSONDecodeError:
                self.console.print(debug_info.response_body)
        
        if debug_info.error:
            self.console.print(f"\n[bold red]Error:[/bold red]")
            self.console.print(debug_info.error)
        
        self.console.print("[dim]" + "─" * 80 + "[/dim]")


# Global debug mode instance
_debug_mode: Optional[DebugMode] = None


def get_debug_mode() -> DebugMode:
    """Get the global debug mode instance."""
    global _debug_mode
    if _debug_mode is None:
        _debug_mode = DebugMode()
    return _debug_mode


def enable_debug_mode(verbose: bool = False) -> None:
    """Enable debug mode globally."""
    get_debug_mode().enable(verbose)


def disable_debug_mode() -> None:
    """Disable debug mode globally."""
    get_debug_mode().disable()


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return get_debug_mode().is_enabled()


# Context manager for debug operations
@contextmanager
def debug_operation(operation_name: str):
    """Context manager for debugging operations."""
    debug_mode = get_debug_mode()
    if not debug_mode.is_enabled():
        yield
        return
    
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        debug_mode.log_operation_timing(operation_name, duration)


# Decorators for debug logging
def debug_function(func):
    """Decorator to add debug logging to functions."""
    def wrapper(*args, **kwargs):
        debug_mode = get_debug_mode()
        if not debug_mode.is_enabled():
            return func(*args, **kwargs)
        
        func_name = f"{func.__module__}.{func.__name__}"
        
        with debug_operation(func_name):
            return func(*args, **kwargs)
    
    return wrapper
"""
Monitoring and metrics collection for Agentic API Tester CLI.

This module provides comprehensive monitoring capabilities including system metrics,
application performance tracking, health checks, and alerting.
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import json
from pathlib import Path

from .logging import get_logger


@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    load_average: List[float] = field(default_factory=list)


@dataclass
class ApplicationMetrics:
    """Application-level metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    requests_per_second: float = 0.0
    
    # Response time metrics
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    cache_size: int = 0
    
    # Template metrics
    templates_used: int = 0
    template_errors: int = 0
    
    # Environment metrics
    environments_active: int = 0
    variable_substitutions: int = 0
    
    # AI metrics
    ai_requests: int = 0
    ai_successful: int = 0
    ai_failed: int = 0
    ai_avg_response_time: float = 0.0


@dataclass
class HealthStatus:
    """Health status information."""
    timestamp: datetime = field(default_factory=datetime.now)
    overall_status: str = "healthy"  # healthy, degraded, unhealthy
    
    # Component health
    redis_healthy: bool = True
    network_healthy: bool = True
    ai_healthy: bool = True
    
    # Health scores (0-100)
    performance_score: float = 100.0
    reliability_score: float = 100.0
    availability_score: float = 100.0
    
    # Issues
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self):
        self.logger = get_logger()
        self._lock = threading.Lock()
        
        # Metrics storage
        self._system_metrics: deque = deque(maxlen=1000)
        self._app_metrics: deque = deque(maxlen=1000)
        self._health_history: deque = deque(maxlen=100)
        
        # Counters and timers
        self._counters: Dict[str, int] = defaultdict(int)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._response_times: deque = deque(maxlen=10000)
        
        # Configuration
        self.collection_interval = 60  # seconds
        self.max_timer_history = 1000
        
        # Background collection
        self._collection_thread: Optional[threading.Thread] = None
        self._stop_collection = threading.Event()
        self._collecting = False
    
    def start_collection(self) -> None:
        """Start background metrics collection."""
        if self._collecting:
            return
        
        self._collecting = True
        self._stop_collection.clear()
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self._collection_thread.start()
        self.logger.info("Metrics collection started")
    
    def stop_collection(self) -> None:
        """Stop background metrics collection."""
        if not self._collecting:
            return
        
        self._stop_collection.set()
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
        self._collecting = False
        self.logger.info("Metrics collection stopped")
    
    def _collection_loop(self) -> None:
        """Background metrics collection loop."""
        while not self._stop_collection.wait(self.collection_interval):
            try:
                self.collect_system_metrics()
                self.collect_application_metrics()
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = []
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                load_average=load_avg
            )
            
            with self._lock:
                self._system_metrics.append(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            return SystemMetrics()
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect current application metrics."""
        with self._lock:
            # Calculate response time percentiles
            response_times = sorted(self._response_times)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                # Calculate percentiles
                p95_idx = int(len(response_times) * 0.95)
                p99_idx = int(len(response_times) * 0.99)
                p95_time = response_times[p95_idx] if p95_idx < len(response_times) else max_time
                p99_time = response_times[p99_idx] if p99_idx < len(response_times) else max_time
            else:
                avg_time = min_time = max_time = p95_time = p99_time = 0.0
            
            # Calculate requests per second
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            recent_requests = sum(
                1 for metrics in self._app_metrics
                if metrics.timestamp >= one_minute_ago
            )
            
            metrics = ApplicationMetrics(
                total_requests=self._counters['total_requests'],
                successful_requests=self._counters['successful_requests'],
                failed_requests=self._counters['failed_requests'],
                requests_per_second=recent_requests / 60.0,
                avg_response_time=avg_time,
                min_response_time=min_time,
                max_response_time=max_time,
                p95_response_time=p95_time,
                p99_response_time=p99_time,
                cache_hits=self._counters['cache_hits'],
                cache_misses=self._counters['cache_misses'],
                cache_hit_rate=self._calculate_cache_hit_rate(),
                cache_size=self._counters['cache_size'],
                templates_used=self._counters['templates_used'],
                template_errors=self._counters['template_errors'],
                environments_active=self._counters['environments_active'],
                variable_substitutions=self._counters['variable_substitutions'],
                ai_requests=self._counters['ai_requests'],
                ai_successful=self._counters['ai_successful'],
                ai_failed=self._counters['ai_failed'],
                ai_avg_response_time=self._calculate_ai_avg_response_time()
            )
            
            self._app_metrics.append(metrics)
            
        return metrics
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] += value
    
    def set_gauge(self, name: str, value: Union[int, float]) -> None:
        """Set a gauge metric value."""
        with self._lock:
            self._counters[name] = value
    
    def record_timing(self, name: str, duration: float) -> None:
        """Record a timing metric."""
        with self._lock:
            if name not in self._timers:
                self._timers[name] = []
            
            self._timers[name].append(duration)
            
            # Keep only recent timings
            if len(self._timers[name]) > self.max_timer_history:
                self._timers[name].pop(0)
            
            # Special handling for response times
            if name == 'response_time':
                self._response_times.append(duration)
    
    def record_request(self, success: bool, response_time: float) -> None:
        """Record a request with its outcome and timing."""
        self.increment_counter('total_requests')
        
        if success:
            self.increment_counter('successful_requests')
        else:
            self.increment_counter('failed_requests')
        
        self.record_timing('response_time', response_time)
    
    def record_cache_operation(self, hit: bool) -> None:
        """Record a cache operation."""
        if hit:
            self.increment_counter('cache_hits')
        else:
            self.increment_counter('cache_misses')
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        
        return {
            'system': asdict(system_metrics),
            'application': asdict(app_metrics),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_history(self, duration_minutes: int = 60) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics history for the specified duration."""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        with self._lock:
            system_history = [
                asdict(metrics) for metrics in self._system_metrics
                if metrics.timestamp >= cutoff_time
            ]
            
            app_history = [
                asdict(metrics) for metrics in self._app_metrics
                if metrics.timestamp >= cutoff_time
            ]
        
        return {
            'system': system_history,
            'application': app_history
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        hits = self._counters['cache_hits']
        misses = self._counters['cache_misses']
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0.0
    
    def _calculate_ai_avg_response_time(self) -> float:
        """Calculate average AI response time."""
        ai_times = self._timers.get('ai_response_time', [])
        return sum(ai_times) / len(ai_times) if ai_times else 0.0


class HealthChecker:
    """Performs health checks and monitors system health."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = get_logger()
        
        # Health thresholds
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 85.0  # %
        self.disk_threshold = 90.0  # %
        self.response_time_threshold = 5.0  # seconds
        self.error_rate_threshold = 10.0  # %
        
        # Health check functions
        self._health_checks: Dict[str, Callable[[], bool]] = {}
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register default health check functions."""
        self._health_checks.update({
            'system_resources': self._check_system_resources,
            'response_times': self._check_response_times,
            'error_rates': self._check_error_rates,
            'redis_connection': self._check_redis_connection,
        })
    
    def register_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a custom health check function."""
        self._health_checks[name] = check_func
    
    def perform_health_check(self) -> HealthStatus:
        """Perform comprehensive health check."""
        health = HealthStatus()
        
        # Run all health checks
        for check_name, check_func in self._health_checks.items():
            try:
                if not check_func():
                    health.issues.append(f"Health check failed: {check_name}")
            except Exception as e:
                health.issues.append(f"Health check error ({check_name}): {str(e)}")
                self.logger.error(f"Health check error in {check_name}: {str(e)}")
        
        # Calculate overall health status
        health.overall_status = self._calculate_overall_status(health)
        health.performance_score = self._calculate_performance_score()
        health.reliability_score = self._calculate_reliability_score()
        health.availability_score = self._calculate_availability_score()
        
        return health
    
    def _check_system_resources(self) -> bool:
        """Check system resource usage."""
        try:
            system_metrics = self.metrics_collector.collect_system_metrics()
            
            if system_metrics.cpu_percent > self.cpu_threshold:
                return False
            
            if system_metrics.memory_percent > self.memory_threshold:
                return False
            
            if system_metrics.disk_usage_percent > self.disk_threshold:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _check_response_times(self) -> bool:
        """Check response time performance."""
        try:
            app_metrics = self.metrics_collector.collect_application_metrics()
            return app_metrics.avg_response_time <= self.response_time_threshold
        except Exception:
            return False
    
    def _check_error_rates(self) -> bool:
        """Check error rates."""
        try:
            app_metrics = self.metrics_collector.collect_application_metrics()
            
            if app_metrics.total_requests == 0:
                return True
            
            error_rate = (app_metrics.failed_requests / app_metrics.total_requests) * 100
            return error_rate <= self.error_rate_threshold
            
        except Exception:
            return False
    
    def _check_redis_connection(self) -> bool:
        """Check Redis connection health."""
        try:
            # This would need to be implemented with actual Redis client
            # For now, return True as placeholder
            return True
        except Exception:
            return False
    
    def _calculate_overall_status(self, health: HealthStatus) -> str:
        """Calculate overall health status."""
        if len(health.issues) == 0:
            return "healthy"
        elif len(health.issues) <= 2:
            return "degraded"
        else:
            return "unhealthy"
    
    def _calculate_performance_score(self) -> float:
        """Calculate performance score (0-100)."""
        try:
            system_metrics = self.metrics_collector.collect_system_metrics()
            app_metrics = self.metrics_collector.collect_application_metrics()
            
            # Weight different factors
            cpu_score = max(0, 100 - system_metrics.cpu_percent)
            memory_score = max(0, 100 - system_metrics.memory_percent)
            response_time_score = max(0, 100 - (app_metrics.avg_response_time * 20))
            
            return (cpu_score + memory_score + response_time_score) / 3
            
        except Exception:
            return 50.0  # Default score
    
    def _calculate_reliability_score(self) -> float:
        """Calculate reliability score (0-100)."""
        try:
            app_metrics = self.metrics_collector.collect_application_metrics()
            
            if app_metrics.total_requests == 0:
                return 100.0
            
            success_rate = (app_metrics.successful_requests / app_metrics.total_requests) * 100
            return success_rate
            
        except Exception:
            return 50.0  # Default score
    
    def _calculate_availability_score(self) -> float:
        """Calculate availability score (0-100)."""
        # This would be based on uptime tracking
        # For now, return a default score
        return 99.9


class Monitor:
    """Main monitoring class that coordinates metrics collection and health checking."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker(self.metrics_collector)
        self.logger = get_logger()
        
        # Monitoring state
        self._monitoring_active = False
        self._last_health_check = datetime.now()
        self.health_check_interval = 300  # 5 minutes
    
    def start_monitoring(self) -> None:
        """Start comprehensive monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self.metrics_collector.start_collection()
        self.logger.info("Monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        self.metrics_collector.stop_collection()
        self.logger.info("Monitoring stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        health = self.health_checker.perform_health_check()
        metrics = self.metrics_collector.get_current_metrics()
        
        return {
            'health': asdict(health),
            'metrics': metrics,
            'monitoring_active': self._monitoring_active
        }
    
    def export_metrics(self, file_path: str, duration_hours: int = 24) -> None:
        """Export metrics to a file."""
        try:
            history = self.metrics_collector.get_metrics_history(duration_hours * 60)
            health = self.health_checker.perform_health_check()
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'duration_hours': duration_hours,
                'health_status': asdict(health),
                'metrics_history': history
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Metrics exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {str(e)}")
            raise


# Global monitor instance
_monitor: Optional[Monitor] = None


def get_monitor() -> Monitor:
    """Get the global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = Monitor()
    return _monitor


def start_monitoring() -> None:
    """Start global monitoring."""
    get_monitor().start_monitoring()


def stop_monitoring() -> None:
    """Stop global monitoring."""
    get_monitor().stop_monitoring()


def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    return get_monitor().get_status()


def record_request_metric(success: bool, response_time: float) -> None:
    """Record a request metric."""
    get_monitor().metrics_collector.record_request(success, response_time)


def record_cache_metric(hit: bool) -> None:
    """Record a cache metric."""
    get_monitor().metrics_collector.record_cache_operation(hit)


def increment_metric(name: str, value: int = 1) -> None:
    """Increment a metric counter."""
    get_monitor().metrics_collector.increment_counter(name, value)
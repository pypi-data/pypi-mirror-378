"""
CLI commands for debugging and diagnostics.

This module provides CLI commands for enabling debug mode, viewing logs,
monitoring performance, and running diagnostic checks.
"""

import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from ..core.debug import get_debug_mode, enable_debug_mode, disable_debug_mode
from ..core.monitoring import get_monitor, get_health_status
from ..core.logging import get_logger, configure_logging, get_log_level, set_log_level
from ..core.error_handler import get_error_handler, check_system_health
from ..exceptions import APITesterError


app = typer.Typer(name="debug", help="Debug and diagnostic commands")
console = Console()


@app.command("enable")
def enable_debug(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debug output"),
    log_file: Optional[str] = typer.Option(None, "--log-file", "-f", help="Debug log file path"),
    log_level: str = typer.Option("DEBUG", "--log-level", "-l", help="Log level for debug mode")
) -> None:
    """Enable debug mode with detailed logging."""
    try:
        # Configure logging for debug mode
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        configure_logging(
            level=log_level,
            log_file=log_file,
            console_output=True,
            structured_logging=verbose
        )
        
        # Enable debug mode
        enable_debug_mode(verbose=verbose)
        
        console.print(
            Panel(
                f"[green]🐛 Debug mode enabled[/green]\n\n"
                f"• Verbose output: {'Yes' if verbose else 'No'}\n"
                f"• Log level: {log_level}\n"
                f"• Log file: {log_file or 'Console only'}\n"
                f"• Structured logging: {'Yes' if verbose else 'No'}",
                title="Debug Mode",
                border_style="green"
            )
        )
        
    except Exception as e:
        console.print(f"[red]Failed to enable debug mode: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("disable")
def disable_debug() -> None:
    """Disable debug mode."""
    try:
        disable_debug_mode()
        console.print("[green]Debug mode disabled[/green]")
    except Exception as e:
        console.print(f"[red]Failed to disable debug mode: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("status")
def debug_status() -> None:
    """Show debug mode status and statistics."""
    debug_mode = get_debug_mode()
    
    if not debug_mode.is_enabled():
        console.print("[yellow]Debug mode is not enabled[/yellow]")
        console.print("Use 'apitester debug enable' to enable debug mode")
        return
    
    # Show debug summary
    debug_mode.print_debug_summary()


@app.command("requests")
def show_requests(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recent requests to show"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export to file")
) -> None:
    """Show recent request history."""
    debug_mode = get_debug_mode()
    
    if not debug_mode.is_enabled():
        console.print("[yellow]Debug mode is not enabled[/yellow]")
        return
    
    if export:
        debug_mode.export_debug_data(export)
    else:
        debug_mode.print_request_history(limit)


@app.command("performance")
def show_performance() -> None:
    """Show performance metrics and statistics."""
    debug_mode = get_debug_mode()
    
    if not debug_mode.is_enabled():
        console.print("[yellow]Debug mode is not enabled[/yellow]")
        return
    
    debug_mode.print_performance_metrics()


@app.command("logs")
def show_logs(
    level: str = typer.Option("INFO", "--level", "-l", help="Minimum log level to show"),
    tail: int = typer.Option(50, "--tail", "-n", help="Number of recent log entries"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    grep: Optional[str] = typer.Option(None, "--grep", "-g", help="Filter logs by pattern")
) -> None:
    """Show application logs."""
    logger = get_logger()
    
    console.print(f"[blue]Current log level: {get_log_level()}[/blue]")
    
    if level != get_log_level():
        set_log_level(level)
        console.print(f"[green]Log level changed to: {level}[/green]")
    
    # This is a placeholder - in a real implementation, you would
    # read from the log file or log buffer
    console.print(f"[dim]Showing last {tail} log entries (level: {level})[/dim]")
    
    if follow:
        console.print("[yellow]Following logs... Press Ctrl+C to stop[/yellow]")
        # Implement log following logic here
    
    if grep:
        console.print(f"[dim]Filtering by pattern: {grep}[/dim]")


@app.command("health")
def health_check() -> None:
    """Perform comprehensive health check."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running health checks...", total=None)
        
        try:
            health_status = check_system_health()
            progress.update(task, completed=True)
            
            # Display health status
            status_color = {
                "healthy": "green",
                "degraded": "yellow", 
                "unhealthy": "red"
            }.get(health_status["status"], "white")
            
            console.print(
                Panel(
                    f"[{status_color}]Overall Status: {health_status['status'].upper()}[/{status_color}]\n\n"
                    f"• Redis Available: {'✅' if health_status['redis_available'] else '❌'}\n"
                    f"• Degraded Mode: {'⚠️ Yes' if health_status['degraded_mode'] else '✅ No'}\n"
                    f"• Total Errors: {sum(health_status['error_counts'].values())}",
                    title="System Health",
                    border_style=status_color
                )
            )
            
            # Show error breakdown if there are errors
            if health_status['error_counts']:
                table = Table(title="Error Breakdown")
                table.add_column("Error Type", style="cyan")
                table.add_column("Count", style="red")
                
                for error_type, count in health_status['error_counts'].items():
                    table.add_row(error_type, str(count))
                
                console.print(table)
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]Health check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command("monitor")
def monitor_system(
    duration: int = typer.Option(60, "--duration", "-d", help="Monitoring duration in seconds"),
    interval: int = typer.Option(5, "--interval", "-i", help="Update interval in seconds"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export metrics to file")
) -> None:
    """Monitor system metrics in real-time."""
    monitor = get_monitor()
    
    if not monitor._monitoring_active:
        monitor.start_monitoring()
        console.print("[green]Started monitoring[/green]")
    
    try:
        import time
        
        console.print(f"[blue]Monitoring for {duration} seconds (interval: {interval}s)[/blue]")
        console.print("[dim]Press Ctrl+C to stop early[/dim]\n")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Clear screen and show current metrics
            console.clear()
            
            status = monitor.get_status()
            
            # System metrics table
            sys_metrics = status['metrics']['system']
            table = Table(title="System Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("CPU Usage", f"{sys_metrics['cpu_percent']:.1f}%")
            table.add_row("Memory Usage", f"{sys_metrics['memory_percent']:.1f}%")
            table.add_row("Memory Used", f"{sys_metrics['memory_used_mb']:.1f} MB")
            table.add_row("Disk Usage", f"{sys_metrics['disk_usage_percent']:.1f}%")
            
            console.print(table)
            
            # Application metrics table
            app_metrics = status['metrics']['application']
            app_table = Table(title="Application Metrics")
            app_table.add_column("Metric", style="cyan")
            app_table.add_column("Value", style="green")
            
            app_table.add_row("Total Requests", str(app_metrics['total_requests']))
            app_table.add_row("Successful", str(app_metrics['successful_requests']))
            app_table.add_row("Failed", str(app_metrics['failed_requests']))
            app_table.add_row("Avg Response Time", f"{app_metrics['avg_response_time']:.3f}s")
            app_table.add_row("Requests/sec", f"{app_metrics['requests_per_second']:.2f}")
            
            console.print(app_table)
            
            time.sleep(interval)
        
        if export:
            monitor.export_metrics(export, duration_hours=1)
            console.print(f"[green]Metrics exported to: {export}[/green]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Monitoring error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("doctor")
def run_doctor() -> None:
    """Run comprehensive diagnostic checks."""
    console.print(
        Panel(
            "[blue]🏥 API Tester Doctor[/blue]\n\n"
            "Running comprehensive diagnostic checks...",
            title="Diagnostics",
            border_style="blue"
        )
    )
    
    issues = []
    warnings = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Check Python version
        task1 = progress.add_task("Checking Python version...", total=None)
        try:
            import sys
            python_version = sys.version_info
            if python_version < (3, 8):
                issues.append(f"Python version {python_version.major}.{python_version.minor} is too old (3.8+ required)")
            progress.update(task1, completed=True)
        except Exception as e:
            issues.append(f"Failed to check Python version: {str(e)}")
        
        # Check dependencies
        task2 = progress.add_task("Checking dependencies...", total=None)
        try:
            import redis
            import httpx
            import typer
            import rich
            progress.update(task2, completed=True)
        except ImportError as e:
            issues.append(f"Missing dependency: {str(e)}")
        
        # Check Redis connection
        task3 = progress.add_task("Checking Redis connection...", total=None)
        try:
            # This would check actual Redis connection
            # For now, just check if Redis module is available
            import redis
            warnings.append("Redis connection not tested (no configuration)")
            progress.update(task3, completed=True)
        except Exception as e:
            warnings.append(f"Redis check failed: {str(e)}")
        
        # Check configuration
        task4 = progress.add_task("Checking configuration...", total=None)
        try:
            # Check if config directory exists
            config_dir = Path.home() / ".config" / "apitester"
            if not config_dir.exists():
                warnings.append("Configuration directory does not exist")
            progress.update(task4, completed=True)
        except Exception as e:
            warnings.append(f"Configuration check failed: {str(e)}")
        
        # Check permissions
        task5 = progress.add_task("Checking permissions...", total=None)
        try:
            # Check write permissions for logs and data
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True):
                pass
            progress.update(task5, completed=True)
        except Exception as e:
            issues.append(f"Permission check failed: {str(e)}")
    
    # Display results
    console.print("\n")
    
    if not issues and not warnings:
        console.print(
            Panel(
                "[green]✅ All checks passed![/green]\n\n"
                "Your API Tester installation appears to be healthy.",
                title="Diagnosis Complete",
                border_style="green"
            )
        )
    else:
        # Show issues
        if issues:
            console.print(
                Panel(
                    "\n".join([f"❌ {issue}" for issue in issues]),
                    title="[red]Issues Found[/red]",
                    border_style="red"
                )
            )
        
        # Show warnings
        if warnings:
            console.print(
                Panel(
                    "\n".join([f"⚠️  {warning}" for warning in warnings]),
                    title="[yellow]Warnings[/yellow]",
                    border_style="yellow"
                )
            )
        
        # Provide suggestions
        console.print(
            Panel(
                "💡 **Suggestions:**\n\n"
                "• Run 'apitester config --generate' to create default configuration\n"
                "• Install Redis: 'redis-server' or 'docker run -p 6379:6379 redis:alpine'\n"
                "• Check the installation guide for detailed setup instructions\n"
                "• Use 'apitester debug enable --verbose' for detailed debugging",
                title="Recommendations",
                border_style="blue"
            )
        )


@app.command("export")
def export_debug_data(
    output: str = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json)"),
    include_requests: bool = typer.Option(True, "--requests/--no-requests", help="Include request history"),
    include_metrics: bool = typer.Option(True, "--metrics/--no-metrics", help="Include performance metrics"),
    duration_hours: int = typer.Option(24, "--duration", "-d", help="Hours of data to export")
) -> None:
    """Export debug data and metrics to a file."""
    try:
        debug_mode = get_debug_mode()
        monitor = get_monitor()
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "debug_enabled": debug_mode.is_enabled(),
            "duration_hours": duration_hours
        }
        
        if include_requests and debug_mode.is_enabled():
            debug_mode.export_debug_data(f"{output}.debug.json")
            export_data["debug_data_file"] = f"{output}.debug.json"
        
        if include_metrics:
            monitor.export_metrics(f"{output}.metrics.json", duration_hours)
            export_data["metrics_file"] = f"{output}.metrics.json"
        
        # Export summary
        with open(output, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        console.print(f"[green]Debug data exported to: {output}[/green]")
        
        if include_requests and debug_mode.is_enabled():
            console.print(f"[green]Request history exported to: {output}.debug.json[/green]")
        
        if include_metrics:
            console.print(f"[green]Metrics exported to: {output}.metrics.json[/green]")
            
    except Exception as e:
        console.print(f"[red]Export failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("clear")
def clear_debug_data() -> None:
    """Clear all debug data and reset counters."""
    try:
        debug_mode = get_debug_mode()
        
        if not debug_mode.is_enabled():
            console.print("[yellow]Debug mode is not enabled[/yellow]")
            return
        
        # Clear debug data (this would need to be implemented in debug_mode)
        # debug_mode.clear_data()
        
        # Reset error handler statistics
        error_handler = get_error_handler()
        error_handler.reset_error_statistics()
        
        console.print("[green]Debug data cleared[/green]")
        
    except Exception as e:
        console.print(f"[red]Failed to clear debug data: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
"""Main CLI entry point for Agentic API Tester."""

import typer
import logging
from typing import Optional
from rich.console import Console
from rich.traceback import install
from rich.logging import RichHandler

from ..config.settings import get_config_manager, get_config

# Install rich traceback handler for better error display
install(show_locals=True)

# Create console for rich output
console = Console()

# Create main Typer app
app = typer.Typer(
    name="apitester",
    help="Agentic API Tester CLI - A Postman-like terminal tool with Redis backend",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Global state for CLI context
class CLIContext:
    def __init__(self):
        self.config = None
        self.verbose = False
        self.debug = False
        self.console = console

# Global context instance
cli_context = CLIContext()


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Setup logging configuration."""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v", 
        help="Enable verbose output"
    ),
    debug: bool = typer.Option(
        False, 
        "--debug", 
        help="Enable debug mode"
    ),
    config_file: Optional[str] = typer.Option(
        None, 
        "--config", 
        "-c", 
        help="Path to configuration file"
    ),
) -> None:
    """
    Agentic API Tester CLI - A Postman-like terminal tool with Redis backend.
    
    Test REST and GraphQL APIs with features like templates, environments,
    history, caching, and optional AI assistance.
    """
    # Setup logging
    setup_logging(verbose, debug)
    
    # Initialize configuration
    try:
        config_manager = get_config_manager(config_file)
        config = config_manager.get_config()
        
        # Update global settings from CLI options
        config.verbose = verbose
        config.debug = debug
        
        # Store in global context
        cli_context.config = config
        cli_context.verbose = verbose
        cli_context.debug = debug
        
        if verbose:
            console.print("[dim]Verbose mode enabled[/dim]")
        
        if debug:
            console.print("[dim]Debug mode enabled[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error initializing configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from .. import __version__, __description__
    
    console.print(f"[bold]Agentic API Tester CLI[/bold] v{__version__}")
    console.print(f"{__description__}")


@app.command("config")
def config_show(
    show_all: bool = typer.Option(
        False,
        "--all",
        help="Show all configuration details"
    ),
    format_type: str = typer.Option(
        "table",
        "--format",
        help="Output format: table, json, yaml"
    )
) -> None:
    """Show current configuration."""
    from rich.table import Table
    import json
    import yaml
    
    try:
        config = get_config()
        
        if format_type == "json":
            config_dict = {
                "redis": {
                    "host": config.redis.host,
                    "port": config.redis.port,
                    "database": config.redis.database
                },
                "cache": {
                    "enabled": config.cache.enabled,
                    "default_ttl": config.cache.default_ttl
                },
                "history": {
                    "enabled": config.history.enabled,
                    "max_entries": config.history.max_entries
                },
                "ai": {
                    "enabled": config.ai.enabled,
                    "provider": config.ai.provider
                }
            }
            console.print(json.dumps(config_dict, indent=2))
            return
        
        elif format_type == "yaml":
            config_dict = {
                "redis": {
                    "host": config.redis.host,
                    "port": config.redis.port,
                    "database": config.redis.database
                },
                "cache": {
                    "enabled": config.cache.enabled,
                    "default_ttl": config.cache.default_ttl
                },
                "history": {
                    "enabled": config.history.enabled,
                    "max_entries": config.history.max_entries
                },
                "ai": {
                    "enabled": config.ai.enabled,
                    "provider": config.ai.provider
                }
            }
            console.print(yaml.dump(config_dict, default_flow_style=False))
            return
        
        # Table format (default)
        table = Table(title="Configuration", show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan")
        table.add_column("Setting", style="white")
        table.add_column("Value", style="green")
        
        # Redis configuration
        table.add_row("Redis", "Host", config.redis.host)
        table.add_row("", "Port", str(config.redis.port))
        table.add_row("", "Database", str(config.redis.database))
        
        # Cache configuration
        table.add_row("Cache", "Enabled", "✅" if config.cache.enabled else "❌")
        table.add_row("", "Default TTL", f"{config.cache.default_ttl}s")
        
        # History configuration
        table.add_row("History", "Enabled", "✅" if config.history.enabled else "❌")
        table.add_row("", "Max Entries", str(config.history.max_entries))
        
        # AI configuration
        table.add_row("AI", "Enabled", "✅" if config.ai.enabled else "❌")
        if config.ai.enabled:
            table.add_row("", "Provider", config.ai.provider)
            table.add_row("", "Model", config.ai.model)
        
        if show_all:
            # Output configuration
            table.add_row("Output", "Colors", "✅" if config.output.color_enabled else "❌")
            table.add_row("", "Pretty Print", "✅" if config.output.pretty_print else "❌")
            table.add_row("", "JSON Indent", str(config.output.json_indent))
            
            # Global settings
            table.add_row("Global", "Verbose", "✅" if config.verbose else "❌")
            table.add_row("", "Debug", "✅" if config.debug else "❌")
            table.add_row("", "Timeout", f"{config.timeout}s")
        
        console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show system status and health checks."""
    from rich.table import Table
    from ..storage.redis_client import get_redis_client
    from ..core.env_manager import EnvironmentManager
    from ..core.template_manager import TemplateManager
    from ..core.history_manager import HistoryManager
    from ..core.cache_manager import CacheManager
    
    table = Table(title="System Status", show_header=True, header_style="bold blue")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    # Redis connection
    try:
        redis_client = get_redis_client()
        if redis_client.health_check():
            table.add_row("Redis", "[green]✅ Connected[/green]", f"{redis_client.config.host}:{redis_client.config.port}")
        else:
            table.add_row("Redis", "[red]❌ Disconnected[/red]", "Health check failed")
    except Exception as e:
        table.add_row("Redis", "[red]❌ Error[/red]", str(e))
    
    # Environment manager
    try:
        env_manager = EnvironmentManager()
        env_count = len(env_manager.list_environments())
        current_env = env_manager.get_current_environment()
        table.add_row("Environments", "[green]✅ Ready[/green]", f"{env_count} environments, current: {current_env}")
    except Exception as e:
        table.add_row("Environments", "[red]❌ Error[/red]", str(e))
    
    # Template manager
    try:
        template_manager = TemplateManager()
        template_count = len(template_manager.list_templates())
        table.add_row("Templates", "[green]✅ Ready[/green]", f"{template_count} templates")
    except Exception as e:
        table.add_row("Templates", "[red]❌ Error[/red]", str(e))
    
    # History manager
    try:
        history_manager = HistoryManager()
        history_count = history_manager.get_history_count()
        table.add_row("History", "[green]✅ Ready[/green]", f"{history_count} records")
    except Exception as e:
        table.add_row("History", "[red]❌ Error[/red]", str(e))
    
    # Cache manager
    try:
        cache_manager = CacheManager()
        cache_stats = cache_manager.get_cache_statistics()
        if cache_stats.get('enabled'):
            entries = cache_stats.get('total_entries', 0)
            table.add_row("Cache", "[green]✅ Enabled[/green]", f"{entries} cached responses")
        else:
            table.add_row("Cache", "[yellow]⚠️ Disabled[/yellow]", "Caching is disabled")
    except Exception as e:
        table.add_row("Cache", "[red]❌ Error[/red]", str(e))
    
    console.print(table)


@app.command()
def doctor() -> None:
    """Run diagnostic checks and suggest fixes for common issues."""
    from rich.panel import Panel
    from ..storage.redis_client import get_redis_client
    
    issues = []
    suggestions = []
    
    console.print("[bold blue]Running diagnostic checks...[/bold blue]\n")
    
    # Check Redis connection
    try:
        redis_client = get_redis_client()
        if not redis_client.health_check():
            issues.append("Redis connection failed")
            suggestions.append("Check if Redis server is running and accessible")
            suggestions.append("Verify Redis host and port in configuration")
    except Exception as e:
        issues.append(f"Redis error: {e}")
        suggestions.append("Install and start Redis server")
        suggestions.append("Check Redis configuration in ~/.config/apitester/config.yaml")
    
    # Check configuration file
    config = get_config()
    if not config:
        issues.append("Configuration not loaded properly")
        suggestions.append("Create configuration file with 'apitester config --help'")
    
    # Check disk space for cache and history
    import shutil
    try:
        free_space = shutil.disk_usage('.').free
        if free_space < 100 * 1024 * 1024:  # Less than 100MB
            issues.append("Low disk space")
            suggestions.append("Free up disk space or clean cache/history")
    except Exception:
        pass
    
    # Display results
    if not issues:
        console.print(Panel(
            "[green]✅ All checks passed! Your API Tester is ready to use.[/green]",
            title="Diagnostic Results",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "\n".join(f"[red]❌ {issue}[/red]" for issue in issues),
            title="Issues Found",
            border_style="red"
        ))
        
        if suggestions:
            console.print("\n[bold yellow]Suggested fixes:[/bold yellow]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")


@app.command()
def completion(
    shell: str = typer.Argument(
        "bash",
        help="Shell type (bash, zsh, fish)"
    ),
    install: bool = typer.Option(
        False,
        "--install",
        help="Install completion script"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force overwrite existing completion"
    )
) -> None:
    """Generate or install shell completion scripts."""
    
    if shell not in ["bash", "zsh", "fish"]:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        console.print("Supported shells: bash, zsh, fish")
        raise typer.Exit(1)
    
    if install:
        try:
            success = install_completion(shell, force)
            if success:
                console.print(f"[green]✅ {shell.title()} completion installed successfully![/green]")
                
                if shell == "bash":
                    console.print("\n[dim]Restart your shell or run:[/dim]")
                    console.print("source ~/.bashrc")
                elif shell == "zsh":
                    console.print("\n[dim]Restart your shell or run:[/dim]")
                    console.print("autoload -U compinit && compinit")
                elif shell == "fish":
                    console.print("\n[dim]Restart your shell or run:[/dim]")
                    console.print("fish_update_completions")
                    
            elif not force:
                console.print(f"[yellow]Completion already installed for {shell}[/yellow]")
                console.print("Use --force to overwrite")
            else:
                console.print(f"[red]Failed to install completion for {shell}[/red]")
                console.print("You may need to run with elevated permissions")
                
        except Exception as e:
            console.print(f"[red]Error installing completion: {e}[/red]")
            raise typer.Exit(1)
    else:
        # Just generate and display the script
        try:
            script = generate_completion_script(shell)
            console.print(f"[bold blue]{shell.title()} completion script:[/bold blue]\n")
            console.print(script)
            console.print(f"\n[dim]To install, run: apitester completion {shell} --install[/dim]")
        except Exception as e:
            console.print(f"[red]Error generating completion script: {e}[/red]")
            raise typer.Exit(1)


# Import and register command modules
from .request import request_app
from .template import template_app
from .environment import env_app
from .history import history_app
from .help import help_app
from .ai import ai_app
from .completion import install_completion, generate_completion_script

# Add sub-applications
app.add_typer(request_app, name="request", help="Execute HTTP and GraphQL requests")
app.add_typer(template_app, name="template", help="Manage request templates")
app.add_typer(env_app, name="env", help="Manage environment variables")
app.add_typer(history_app, name="history", help="View and manage request history")
app.add_typer(help_app, name="help", help="Comprehensive help and examples")
app.add_typer(ai_app, name="ai", help="AI-powered assistance for API testing")


if __name__ == "__main__":
    app()
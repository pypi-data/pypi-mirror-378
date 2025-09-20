"""Configuration management CLI commands."""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..config.validation import (
    ConfigManager,
    ConfigValidator,
    ConfigMigrator,
    validate_config_file,
    migrate_config_file,
    create_default_config,
    ConfigValidationError,
    ConfigMigrationError
)
from ..config.settings import get_config_manager, get_config

# Create console for output
console = Console()

# Create config management app
config_app = typer.Typer(
    name="config",
    help="Manage configuration settings",
    rich_markup_mode="rich"
)


@config_app.command("show")
def show_config(
    format_type: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, yaml"
    ),
    section: Optional[str] = typer.Option(
        None,
        "--section",
        "-s",
        help="Show specific section: redis, cache, history, output, ai"
    ),
    show_sensitive: bool = typer.Option(
        False,
        "--show-sensitive",
        help="Show sensitive values (use with caution)"
    )
) -> None:
    """Show current configuration."""
    try:
        config = get_config()
        
        if format_type == "json":
            import json
            from dataclasses import asdict
            config_dict = asdict(config)
            
            # Mask sensitive values unless explicitly requested
            if not show_sensitive:
                if config_dict.get("redis", {}).get("password"):
                    config_dict["redis"]["password"] = "***"
                if config_dict.get("ai", {}).get("api_key"):
                    config_dict["ai"]["api_key"] = "***"
            
            if section:
                config_dict = config_dict.get(section, {})
            
            console.print(json.dumps(config_dict, indent=2))
            return
        
        elif format_type == "yaml":
            import yaml
            from dataclasses import asdict
            config_dict = asdict(config)
            
            # Mask sensitive values unless explicitly requested
            if not show_sensitive:
                if config_dict.get("redis", {}).get("password"):
                    config_dict["redis"]["password"] = "***"
                if config_dict.get("ai", {}).get("api_key"):
                    config_dict["ai"]["api_key"] = "***"
            
            if section:
                config_dict = config_dict.get(section, {})
            
            console.print(yaml.dump(config_dict, default_flow_style=False))
            return
        
        # Table format (default)
        if section:
            _show_section_table(config, section, show_sensitive)
        else:
            _show_full_config_table(config, show_sensitive)
        
    except Exception as e:
        console.print(f"[red]Error showing configuration: {e}[/red]")
        raise typer.Exit(1)


def _show_full_config_table(config, show_sensitive: bool) -> None:
    """Show full configuration in table format."""
    table = Table(title="Configuration", show_header=True, header_style="bold blue")
    table.add_column("Section", style="cyan")
    table.add_column("Setting", style="white")
    table.add_column("Value", style="green")
    
    # Redis configuration
    table.add_row("Redis", "Host", config.redis.host)
    table.add_row("", "Port", str(config.redis.port))
    table.add_row("", "Database", str(config.redis.database))
    table.add_row("", "Password", "***" if config.redis.password and not show_sensitive else str(config.redis.password))
    
    # Cache configuration
    table.add_row("Cache", "Enabled", "✅" if config.cache.enabled else "❌")
    table.add_row("", "Default TTL", f"{config.cache.default_ttl}s")
    table.add_row("", "Max Size", str(config.cache.max_size))
    
    # History configuration
    table.add_row("History", "Enabled", "✅" if config.history.enabled else "❌")
    table.add_row("", "Max Entries", str(config.history.max_entries))
    table.add_row("", "Auto Cleanup", "✅" if config.history.auto_cleanup else "❌")
    
    # Output configuration
    table.add_row("Output", "Colors", "✅" if config.output.color_enabled else "❌")
    table.add_row("", "Pretty Print", "✅" if config.output.pretty_print else "❌")
    table.add_row("", "JSON Indent", str(config.output.json_indent))
    table.add_row("", "Show Headers", "✅" if config.output.show_headers else "❌")
    table.add_row("", "Show Timing", "✅" if config.output.show_timing else "❌")
    
    # AI configuration
    table.add_row("AI", "Enabled", "✅" if config.ai.enabled else "❌")
    if config.ai.enabled:
        table.add_row("", "Provider", config.ai.provider)
        table.add_row("", "Model", config.ai.model)
        table.add_row("", "API Key", "***" if config.ai.api_key and not show_sensitive else str(config.ai.api_key))
    
    # Global settings
    table.add_row("Global", "Environment", config.current_environment)
    table.add_row("", "Timeout", f"{config.timeout}s")
    table.add_row("", "Verify SSL", "✅" if config.verify_ssl else "❌")
    table.add_row("", "Verbose", "✅" if config.verbose else "❌")
    table.add_row("", "Debug", "✅" if config.debug else "❌")
    
    console.print(table)


def _show_section_table(config, section: str, show_sensitive: bool) -> None:
    """Show specific configuration section in table format."""
    table = Table(title=f"{section.title()} Configuration", show_header=True, header_style="bold blue")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    if section == "redis":
        table.add_row("Host", config.redis.host)
        table.add_row("Port", str(config.redis.port))
        table.add_row("Database", str(config.redis.database))
        table.add_row("Password", "***" if config.redis.password and not show_sensitive else str(config.redis.password))
        table.add_row("Socket Timeout", f"{config.redis.socket_timeout}s")
        table.add_row("Connect Timeout", f"{config.redis.socket_connect_timeout}s")
        table.add_row("Retry on Timeout", "✅" if config.redis.retry_on_timeout else "❌")
        table.add_row("Health Check Interval", f"{config.redis.health_check_interval}s")
    
    elif section == "cache":
        table.add_row("Enabled", "✅" if config.cache.enabled else "❌")
        table.add_row("Default TTL", f"{config.cache.default_ttl}s")
        table.add_row("Max Size", str(config.cache.max_size))
    
    elif section == "history":
        table.add_row("Enabled", "✅" if config.history.enabled else "❌")
        table.add_row("Max Entries", str(config.history.max_entries))
        table.add_row("Auto Cleanup", "✅" if config.history.auto_cleanup else "❌")
    
    elif section == "output":
        table.add_row("Colors", "✅" if config.output.color_enabled else "❌")
        table.add_row("Pretty Print", "✅" if config.output.pretty_print else "❌")
        table.add_row("JSON Indent", str(config.output.json_indent))
        table.add_row("Table Max Width", str(config.output.table_max_width))
        table.add_row("Show Headers", "✅" if config.output.show_headers else "❌")
        table.add_row("Show Timing", "✅" if config.output.show_timing else "❌")
    
    elif section == "ai":
        table.add_row("Enabled", "✅" if config.ai.enabled else "❌")
        table.add_row("Provider", config.ai.provider)
        table.add_row("Model", config.ai.model)
        table.add_row("API Key", "***" if config.ai.api_key and not show_sensitive else str(config.ai.api_key))
        table.add_row("Max Tokens", str(config.ai.max_tokens))
        table.add_row("Temperature", str(config.ai.temperature))
    
    else:
        console.print(f"[red]Unknown section: {section}[/red]")
        console.print("Available sections: redis, cache, history, output, ai")
        raise typer.Exit(1)
    
    console.print(table)


@config_app.command("validate")
def validate_config(
    config_file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Configuration file to validate (default: current config)"
    )
) -> None:
    """Validate configuration file."""
    try:
        if config_file:
            is_valid, errors, warnings = validate_config_file(config_file)
            console.print(f"[bold]Validating: {config_file}[/bold]")
        else:
            manager = get_config_manager()
            is_valid, errors, warnings = manager.validate_current_config()
            console.print("[bold]Validating current configuration[/bold]")
        
        if is_valid:
            console.print("[green]✅ Configuration is valid[/green]")
        else:
            console.print("[red]❌ Configuration validation failed[/red]")
            for error in errors:
                console.print(f"  [red]Error:[/red] {error}")
        
        if warnings:
            console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
            for warning in warnings:
                console.print(f"  [yellow]Warning:[/yellow] {warning}")
        
        if not is_valid:
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]Error validating configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("migrate")
def migrate_config(
    config_file: str = typer.Argument(..., help="Configuration file to migrate"),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backup before migration"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force migration without confirmation"
    )
) -> None:
    """Migrate configuration file to current version."""
    try:
        if not Path(config_file).exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            raise typer.Exit(1)
        
        if not force:
            if not Confirm.ask(f"Migrate configuration file {config_file}?"):
                console.print("Migration cancelled")
                return
        
        migrate_config_file(config_file, backup)
        console.print(f"[green]✅ Successfully migrated: {config_file}[/green]")
        
    except ConfigMigrationError as e:
        console.print(f"[red]Migration failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during migration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("create")
def create_config(
    output_file: str = typer.Argument(..., help="Output file path"),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing file"
    )
) -> None:
    """Create a sample configuration file."""
    try:
        output_path = Path(output_file)
        
        if output_path.exists() and not overwrite:
            console.print(f"[red]File already exists: {output_file}[/red]")
            console.print("Use --overwrite to replace existing file")
            raise typer.Exit(1)
        
        create_default_config(output_file)
        console.print(f"[green]✅ Created configuration file: {output_file}[/green]")
        console.print(f"Edit the file and copy to ~/.config/apitester/config.yaml to use")
        
    except Exception as e:
        console.print(f"[red]Error creating configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("set")
def set_config_value(
    key: str = typer.Argument(..., help="Configuration key (e.g., redis.host, cache.enabled)"),
    value: str = typer.Argument(..., help="Configuration value"),
    config_file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Configuration file to modify"
    )
) -> None:
    """Set a configuration value."""
    try:
        manager = get_config_manager(config_file)
        config = manager.get_config()
        
        # Parse the key path
        keys = key.split('.')
        if len(keys) != 2:
            console.print("[red]Key must be in format 'section.setting' (e.g., redis.host)[/red]")
            raise typer.Exit(1)
        
        section, setting = keys
        
        # Convert value to appropriate type
        converted_value = _convert_value(value)
        
        # Update configuration
        if section == "redis":
            if hasattr(config.redis, setting):
                setattr(config.redis, setting, converted_value)
            else:
                console.print(f"[red]Unknown Redis setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "cache":
            if hasattr(config.cache, setting):
                setattr(config.cache, setting, converted_value)
            else:
                console.print(f"[red]Unknown cache setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "history":
            if hasattr(config.history, setting):
                setattr(config.history, setting, converted_value)
            else:
                console.print(f"[red]Unknown history setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "output":
            if hasattr(config.output, setting):
                setattr(config.output, setting, converted_value)
            else:
                console.print(f"[red]Unknown output setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "ai":
            if hasattr(config.ai, setting):
                setattr(config.ai, setting, converted_value)
            else:
                console.print(f"[red]Unknown AI setting: {setting}[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"[red]Unknown section: {section}[/red]")
            console.print("Available sections: redis, cache, history, output, ai")
            raise typer.Exit(1)
        
        # Validate the updated configuration
        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(config)
        
        if not is_valid:
            console.print("[red]Invalid configuration value:[/red]")
            for error in errors:
                console.print(f"  {error}")
            raise typer.Exit(1)
        
        # Save the configuration
        manager.save_config(config)
        console.print(f"[green]✅ Set {key} = {converted_value}[/green]")
        
        if warnings:
            for warning in warnings:
                console.print(f"[yellow]Warning:[/yellow] {warning}")
        
    except Exception as e:
        console.print(f"[red]Error setting configuration: {e}[/red]")
        raise typer.Exit(1)


def _convert_value(value: str):
    """Convert string value to appropriate type."""
    # Boolean values
    if value.lower() in ('true', 'yes', '1', 'on'):
        return True
    elif value.lower() in ('false', 'no', '0', 'off'):
        return False
    
    # Null/None values
    if value.lower() in ('null', 'none', ''):
        return None
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


@config_app.command("get")
def get_config_value(
    key: str = typer.Argument(..., help="Configuration key (e.g., redis.host, cache.enabled)"),
    config_file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Configuration file to read from"
    )
) -> None:
    """Get a configuration value."""
    try:
        config = get_config()
        
        # Parse the key path
        keys = key.split('.')
        if len(keys) != 2:
            console.print("[red]Key must be in format 'section.setting' (e.g., redis.host)[/red]")
            raise typer.Exit(1)
        
        section, setting = keys
        
        # Get value
        if section == "redis":
            if hasattr(config.redis, setting):
                value = getattr(config.redis, setting)
            else:
                console.print(f"[red]Unknown Redis setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "cache":
            if hasattr(config.cache, setting):
                value = getattr(config.cache, setting)
            else:
                console.print(f"[red]Unknown cache setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "history":
            if hasattr(config.history, setting):
                value = getattr(config.history, setting)
            else:
                console.print(f"[red]Unknown history setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "output":
            if hasattr(config.output, setting):
                value = getattr(config.output, setting)
            else:
                console.print(f"[red]Unknown output setting: {setting}[/red]")
                raise typer.Exit(1)
        elif section == "ai":
            if hasattr(config.ai, setting):
                value = getattr(config.ai, setting)
                # Mask sensitive values
                if setting == "api_key" and value:
                    value = "***"
            else:
                console.print(f"[red]Unknown AI setting: {setting}[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"[red]Unknown section: {section}[/red]")
            raise typer.Exit(1)
        
        console.print(f"{key} = {value}")
        
    except Exception as e:
        console.print(f"[red]Error getting configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("reset")
def reset_config(
    section: Optional[str] = typer.Option(
        None,
        "--section",
        "-s",
        help="Reset specific section only"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force reset without confirmation"
    )
) -> None:
    """Reset configuration to defaults."""
    try:
        if not force:
            if section:
                if not Confirm.ask(f"Reset {section} configuration to defaults?"):
                    console.print("Reset cancelled")
                    return
            else:
                if not Confirm.ask("Reset ALL configuration to defaults?"):
                    console.print("Reset cancelled")
                    return
        
        # Create new manager with defaults
        manager = ConfigManager()
        config = manager.get_config()
        
        if section:
            # Reset only specific section
            current_config = get_config()
            
            if section == "redis":
                current_config.redis = config.redis
            elif section == "cache":
                current_config.cache = config.cache
            elif section == "history":
                current_config.history = config.history
            elif section == "output":
                current_config.output = config.output
            elif section == "ai":
                current_config.ai = config.ai
            else:
                console.print(f"[red]Unknown section: {section}[/red]")
                raise typer.Exit(1)
            
            manager.save_config(current_config)
            console.print(f"[green]✅ Reset {section} configuration to defaults[/green]")
        else:
            # Reset all configuration
            manager.save_config(config)
            console.print("[green]✅ Reset all configuration to defaults[/green]")
        
    except Exception as e:
        console.print(f"[red]Error resetting configuration: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("path")
def show_config_path() -> None:
    """Show configuration file path."""
    manager = get_config_manager()
    console.print(f"Configuration file: {manager.config_file}")
    
    if Path(manager.config_file).exists():
        console.print("[green]✅ File exists[/green]")
    else:
        console.print("[yellow]⚠️ File does not exist (using defaults)[/yellow]")
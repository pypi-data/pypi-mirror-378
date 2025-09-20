"""Environment management commands for the CLI."""

import typer
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.env_manager import EnvironmentManager
from ..exceptions import EnvironmentError
from ..core.env_operations import EnvironmentOperations

# Create console for output
console = Console()

# Create environment app
env_app = typer.Typer(
    name="env",
    help="Manage environment variables and configurations",
    rich_markup_mode="rich"
)


@env_app.command("list")
def list_environments(
    show_variables: bool = typer.Option(
        False,
        "--variables",
        "-v",
        help="Show variables for each environment"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Show variables for specific environment only"
    )
) -> None:
    """List all environments and optionally their variables."""
    try:
        env_manager = EnvironmentManager()
        
        if environment:
            # Show specific environment
            if not env_manager.environment_exists(environment):
                console.print(f"[red]Environment '{environment}' not found[/red]")
                raise typer.Exit(1)
            
            variables = env_manager.get_environment_variables(environment)
            current_env = env_manager.get_current_environment()
            
            # Create panel for environment
            status = " (current)" if environment == current_env else ""
            title = f"Environment: {environment}{status}"
            
            if variables:
                content_lines = []
                for key, value in variables.items():
                    # Mask sensitive values
                    display_value = value
                    if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                        display_value = '*' * min(len(value), 8)
                    content_lines.append(f"{key} = {display_value}")
                
                content = "\n".join(content_lines)
            else:
                content = "[dim]No variables defined[/dim]"
            
            panel = Panel(content, title=title, border_style="blue")
            console.print(panel)
            
        else:
            # List all environments
            environments = env_manager.list_environments()
            current_env = env_manager.get_current_environment()
            
            if not environments:
                console.print("[yellow]No environments found[/yellow]")
                return
            
            if show_variables:
                # Show detailed view with variables
                for env_name in environments:
                    variables = env_manager.get_environment_variables(env_name)
                    status = " (current)" if env_name == current_env else ""
                    title = f"Environment: {env_name}{status}"
                    
                    if variables:
                        content_lines = []
                        for key, value in variables.items():
                            # Mask sensitive values
                            display_value = value
                            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                                display_value = '*' * min(len(value), 8)
                            content_lines.append(f"{key} = {display_value}")
                        
                        content = "\n".join(content_lines)
                    else:
                        content = "[dim]No variables defined[/dim]"
                    
                    panel = Panel(content, title=title, border_style="blue")
                    console.print(panel)
                    console.print()  # Add spacing
            else:
                # Show simple table
                table = Table(title="Environments", show_header=True, header_style="bold blue")
                table.add_column("Name", style="cyan")
                table.add_column("Variables", style="white")
                table.add_column("Status", style="green")
                
                for env_name in environments:
                    variables = env_manager.get_environment_variables(env_name)
                    var_count = len(variables)
                    status = "current" if env_name == current_env else ""
                    
                    table.add_row(
                        env_name,
                        f"{var_count} variables",
                        status
                    )
                
                console.print(table)
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("create")
def create_environment(
    name: str = typer.Argument(..., help="Environment name"),
    description: str = typer.Option(
        "",
        "--description",
        "--desc",
        help="Environment description"
    ),
    copy_from: Optional[str] = typer.Option(
        None,
        "--copy-from",
        help="Copy variables from existing environment"
    ),
    set_current: bool = typer.Option(
        False,
        "--set-current",
        help="Set as current environment after creation"
    )
) -> None:
    """Create a new environment."""
    try:
        env_manager = EnvironmentManager()
        
        # Check if environment already exists
        if env_manager.environment_exists(name):
            console.print(f"[red]Environment '{name}' already exists[/red]")
            raise typer.Exit(1)
        
        # Create environment
        env_manager.create_environment(name, description)
        
        # Copy variables if requested
        if copy_from:
            if not env_manager.environment_exists(copy_from):
                console.print(f"[yellow]Warning: Source environment '{copy_from}' not found, created empty environment[/yellow]")
            else:
                source_vars = env_manager.get_environment_variables(copy_from)
                for key, value in source_vars.items():
                    env_manager.set_variable(name, key, value)
                console.print(f"[green]Copied {len(source_vars)} variables from '{copy_from}'[/green]")
        
        # Set as current if requested
        if set_current:
            env_manager.set_current_environment(name)
            console.print(f"[green]✓[/green] Environment '[bold]{name}[/bold]' created and set as current")
        else:
            console.print(f"[green]✓[/green] Environment '[bold]{name}[/bold]' created successfully")
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("delete")
def delete_environment(
    name: str = typer.Argument(..., help="Environment name"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
) -> None:
    """Delete an environment."""
    try:
        env_manager = EnvironmentManager()
        
        # Check if environment exists
        if not env_manager.environment_exists(name):
            console.print(f"[red]Environment '{name}' not found[/red]")
            raise typer.Exit(1)
        
        # Prevent deletion of default environment
        if name == "default":
            console.print("[red]Cannot delete the default environment[/red]")
            raise typer.Exit(1)
        
        # Check if it's the current environment
        current_env = env_manager.get_current_environment()
        if name == current_env:
            console.print(f"[yellow]Warning: '{name}' is the current environment[/yellow]")
            if not force:
                switch_to_default = typer.confirm("Switch to 'default' environment and continue deletion?")
                if not switch_to_default:
                    console.print("Deletion cancelled")
                    return
            env_manager.set_current_environment("default")
            console.print("Switched to 'default' environment")
        
        # Confirm deletion unless force flag is used
        if not force:
            variables = env_manager.get_environment_variables(name)
            var_count = len(variables)
            confirm = typer.confirm(f"Delete environment '{name}' with {var_count} variables?")
            if not confirm:
                console.print("Deletion cancelled")
                return
        
        # Delete environment
        success = env_manager.delete_environment(name)
        
        if success:
            console.print(f"[green]✓[/green] Environment '[bold]{name}[/bold]' deleted successfully")
        else:
            console.print(f"[red]Failed to delete environment '{name}'[/red]")
            raise typer.Exit(1)
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("current")
def show_current_environment() -> None:
    """Show the current environment."""
    try:
        env_manager = EnvironmentManager()
        current_env = env_manager.get_current_environment()
        
        console.print(f"Current environment: [bold cyan]{current_env}[/bold cyan]")
        
        # Show variables in current environment
        variables = env_manager.get_environment_variables(current_env)
        if variables:
            console.print(f"\nVariables ({len(variables)}):")
            for key, value in variables.items():
                # Mask sensitive values
                display_value = value
                if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    display_value = '*' * min(len(value), 8)
                console.print(f"  {key} = {display_value}")
        else:
            console.print("\n[dim]No variables defined[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("switch")
def switch_environment(
    name: str = typer.Argument(..., help="Environment name to switch to")
) -> None:
    """Switch to a different environment."""
    try:
        env_manager = EnvironmentManager()
        
        # Check if environment exists
        if not env_manager.environment_exists(name):
            console.print(f"[red]Environment '{name}' not found[/red]")
            
            # Suggest similar environment names
            environments = env_manager.list_environments()
            similar = [env for env in environments if name.lower() in env.lower()]
            if similar:
                console.print(f"Did you mean: {', '.join(similar)}?")
            
            raise typer.Exit(1)
        
        # Switch environment
        env_manager.set_current_environment(name)
        console.print(f"[green]✓[/green] Switched to environment '[bold]{name}[/bold]'")
        
        # Show variables in new environment
        variables = env_manager.get_environment_variables(name)
        if variables:
            console.print(f"\nVariables available ({len(variables)}):")
            for key in variables.keys():
                console.print(f"  • {key}")
        else:
            console.print("\n[dim]No variables defined in this environment[/dim]")
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("set")
def set_variable(
    key: str = typer.Argument(..., help="Variable name"),
    value: str = typer.Argument(..., help="Variable value"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to set variable in (default: current)"
    ),
    description: str = typer.Option(
        "",
        "--description",
        "--desc",
        help="Variable description"
    ),
    sensitive: bool = typer.Option(
        False,
        "--sensitive",
        help="Mark variable as sensitive (will be masked in output)"
    )
) -> None:
    """Set an environment variable."""
    try:
        env_manager = EnvironmentManager()
        
        # Use current environment if not specified
        if not environment:
            environment = env_manager.get_current_environment()
        
        # Check if environment exists
        if not env_manager.environment_exists(environment):
            console.print(f"[red]Environment '{environment}' not found[/red]")
            raise typer.Exit(1)
        
        # Set variable
        env_manager.set_variable(environment, key, value)
        
        # Display confirmation
        display_value = value
        if sensitive or any(sensitive_word in key.lower() for sensitive_word in ['password', 'secret', 'key', 'token']):
            display_value = '*' * min(len(value), 8)
        
        console.print(f"[green]✓[/green] Set variable '[bold]{key}[/bold]' = '{display_value}' in environment '[bold]{environment}[/bold]'")
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("get")
def get_variable(
    key: str = typer.Argument(..., help="Variable name"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to get variable from (default: current)"
    ),
    show_sensitive: bool = typer.Option(
        False,
        "--show-sensitive",
        help="Show sensitive values (use with caution)"
    )
) -> None:
    """Get an environment variable value."""
    try:
        env_manager = EnvironmentManager()
        
        # Use current environment if not specified
        if not environment:
            environment = env_manager.get_current_environment()
        
        # Check if environment exists
        if not env_manager.environment_exists(environment):
            console.print(f"[red]Environment '{environment}' not found[/red]")
            raise typer.Exit(1)
        
        # Get variable
        value = env_manager.get_variable(environment, key)
        
        if value is None:
            console.print(f"[red]Variable '{key}' not found in environment '{environment}'[/red]")
            raise typer.Exit(1)
        
        # Display value
        display_value = value
        if not show_sensitive and any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
            display_value = '*' * min(len(value), 8)
        
        console.print(f"[bold]{key}[/bold] = {display_value}")
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("unset")
def unset_variable(
    key: str = typer.Argument(..., help="Variable name"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to remove variable from (default: current)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
) -> None:
    """Remove an environment variable."""
    try:
        env_manager = EnvironmentManager()
        
        # Use current environment if not specified
        if not environment:
            environment = env_manager.get_current_environment()
        
        # Check if environment exists
        if not env_manager.environment_exists(environment):
            console.print(f"[red]Environment '{environment}' not found[/red]")
            raise typer.Exit(1)
        
        # Check if variable exists
        if not env_manager.variable_exists(environment, key):
            console.print(f"[red]Variable '{key}' not found in environment '{environment}'[/red]")
            raise typer.Exit(1)
        
        # Confirm deletion unless force flag is used
        if not force:
            confirm = typer.confirm(f"Remove variable '{key}' from environment '{environment}'?")
            if not confirm:
                console.print("Operation cancelled")
                return
        
        # Remove variable
        success = env_manager.unset_variable(environment, key)
        
        if success:
            console.print(f"[green]✓[/green] Variable '[bold]{key}[/bold]' removed from environment '[bold]{environment}[/bold]'")
        else:
            console.print(f"[red]Failed to remove variable '{key}'[/red]")
            raise typer.Exit(1)
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("export")
def export_environment(
    output_file: Path = typer.Argument(..., help="Output file path"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to export (default: current)"
    ),
    format_type: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Export format (json, yaml, env)"
    ),
    include_sensitive: bool = typer.Option(
        False,
        "--include-sensitive",
        help="Include sensitive variables (use with caution)"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing file"
    )
) -> None:
    """Export environment variables to file."""
    try:
        env_operations = EnvironmentOperations()
        
        # Use current environment if not specified
        if not environment:
            env_manager = EnvironmentManager()
            environment = env_manager.get_current_environment()
        
        # Export environment
        saved_path = env_operations.export_environment_to_file(
            environment_name=environment,
            file_path=output_file,
            format_type=format_type,
            include_sensitive=include_sensitive,
            overwrite=overwrite
        )
        
        console.print(f"[green]✓[/green] Environment '[bold]{environment}[/bold]' exported to [bold]{saved_path}[/bold]")
        
        if not include_sensitive:
            console.print("[dim]Note: Sensitive variables were excluded. Use --include-sensitive to include them.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("import")
def import_environment(
    input_file: Path = typer.Argument(..., help="Input file path"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Target environment name (default: filename without extension)"
    ),
    format_type: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Import format (json, yaml, env, auto-detected from file extension)"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing variables"
    ),
    create_env: bool = typer.Option(
        True,
        "--create-env/--no-create-env",
        help="Create environment if it doesn't exist"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be imported without actually importing"
    )
) -> None:
    """Import environment variables from file."""
    try:
        env_operations = EnvironmentOperations()
        
        # Use filename as environment name if not specified
        if not environment:
            environment = input_file.stem
        
        # Import environment
        results = env_operations.import_environment_from_file(
            file_path=input_file,
            environment_name=environment,
            format_type=format_type,
            overwrite_existing=overwrite,
            create_environment=create_env,
            dry_run=dry_run
        )
        
        # Display results
        if dry_run:
            console.print(f"[cyan]Dry run results for environment '{environment}':[/cyan]")
        else:
            console.print(f"[green]✓[/green] Import completed for environment '[bold]{environment}[/bold]':")
        
        console.print(f"  Imported: {results['imported_count']} variables")
        console.print(f"  Skipped: {results['skipped_count']} variables")
        console.print(f"  Errors: {results['error_count']} variables")
        
        # Show imported variables
        if results['imported_variables']:
            console.print(f"\n[bold]Imported variables:[/bold]")
            for var in results['imported_variables']:
                status = " (overwritten)" if var.get('overwritten') else ""
                console.print(f"  • {var['key']}{status}")
        
        # Show skipped variables
        if results['skipped_variables']:
            console.print(f"\n[yellow]Skipped variables:[/yellow]")
            for var in results['skipped_variables']:
                console.print(f"  • {var['key']} - {var['reason']}")
        
        # Show errors
        if results['errors']:
            console.print(f"\n[red]Errors:[/red]")
            for error in results['errors']:
                console.print(f"  • {error['key']}: {error['error']}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("copy")
def copy_environment(
    source: str = typer.Argument(..., help="Source environment name"),
    target: str = typer.Argument(..., help="Target environment name"),
    overwrite_vars: bool = typer.Option(
        False,
        "--overwrite-vars",
        help="Overwrite existing variables in target environment"
    ),
    create_target: bool = typer.Option(
        True,
        "--create-target/--no-create-target",
        help="Create target environment if it doesn't exist"
    )
) -> None:
    """Copy variables from one environment to another."""
    try:
        env_manager = EnvironmentManager()
        
        # Check if source environment exists
        if not env_manager.environment_exists(source):
            console.print(f"[red]Source environment '{source}' not found[/red]")
            raise typer.Exit(1)
        
        # Check if target environment exists
        if not env_manager.environment_exists(target):
            if create_target:
                env_manager.create_environment(target, f"Copied from {source}")
                console.print(f"[green]Created target environment '{target}'[/green]")
            else:
                console.print(f"[red]Target environment '{target}' not found[/red]")
                raise typer.Exit(1)
        
        # Get source variables
        source_vars = env_manager.get_environment_variables(source)
        
        if not source_vars:
            console.print(f"[yellow]No variables to copy from environment '{source}'[/yellow]")
            return
        
        # Copy variables
        copied_count = 0
        skipped_count = 0
        
        for key, value in source_vars.items():
            if env_manager.variable_exists(target, key) and not overwrite_vars:
                skipped_count += 1
                continue
            
            env_manager.set_variable(target, key, value)
            copied_count += 1
        
        # Display results
        console.print(f"[green]✓[/green] Copied {copied_count} variables from '[bold]{source}[/bold]' to '[bold]{target}[/bold]'")
        
        if skipped_count > 0:
            console.print(f"[yellow]Skipped {skipped_count} existing variables (use --overwrite-vars to overwrite)[/yellow]")
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@env_app.command("clear")
def clear_environment(
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to clear (default: current)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
) -> None:
    """Clear all variables from an environment."""
    try:
        env_manager = EnvironmentManager()
        
        # Use current environment if not specified
        if not environment:
            environment = env_manager.get_current_environment()
        
        # Check if environment exists
        if not env_manager.environment_exists(environment):
            console.print(f"[red]Environment '{environment}' not found[/red]")
            raise typer.Exit(1)
        
        # Prevent clearing default environment without confirmation
        if environment == "default" and not force:
            console.print("[yellow]Warning: You are about to clear the default environment[/yellow]")
        
        # Get variable count for confirmation
        variables = env_manager.get_environment_variables(environment)
        var_count = len(variables)
        
        if var_count == 0:
            console.print(f"[yellow]Environment '{environment}' is already empty[/yellow]")
            return
        
        # Confirm clearing unless force flag is used
        if not force:
            confirm = typer.confirm(f"Clear all {var_count} variables from environment '{environment}'?")
            if not confirm:
                console.print("Operation cancelled")
                return
        
        # Clear environment
        success = env_manager.clear_environment(environment)
        
        if success:
            console.print(f"[green]✓[/green] Cleared {var_count} variables from environment '[bold]{environment}[/bold]'")
        else:
            console.print(f"[red]Failed to clear environment '{environment}'[/red]")
            raise typer.Exit(1)
        
    except EnvironmentError as e:
        console.print(f"[red]Environment Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
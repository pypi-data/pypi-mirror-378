"""Template management commands for the CLI."""

import typer
import json
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.template_manager import TemplateManager, TemplateManagerError, TemplateNotFoundError
from ..core.template_importer import TemplateImporter, TemplateImportError, TemplateExportError
from ..core.template_executor import TemplateExecutor
from ..ai.assistant import AIAssistant, AIAssistantError
from ..ai.integrations import JSONValidator
from ..config.settings import get_config

# Create console for output
console = Console()

# Create template app
template_app = typer.Typer(
    name="template",
    help="Manage request templates",
    rich_markup_mode="rich"
)


@template_app.command("save")
def save_template(
    name: str = typer.Argument(..., help="Template name"),
    method: str = typer.Argument(..., help="HTTP method"),
    url: str = typer.Argument(..., help="Request URL"),
    headers: Optional[List[str]] = typer.Option(
        None, 
        "--header", 
        "-H", 
        help="Request headers in 'Key: Value' format"
    ),
    body: Optional[str] = typer.Option(
        None, 
        "--body", 
        "-d", 
        help="Request body"
    ),
    body_file: Optional[Path] = typer.Option(
        None, 
        "--body-file", 
        "-f", 
        help="File containing request body"
    ),
    params: Optional[List[str]] = typer.Option(
        None, 
        "--param", 
        "-p", 
        help="Query parameters in 'key=value' format"
    ),
    description: str = typer.Option(
        "", 
        "--description", 
        "--desc", 
        help="Template description"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, 
        "--tag", 
        "-t", 
        help="Template tags"
    ),
    overwrite: bool = typer.Option(
        False, 
        "--overwrite", 
        help="Overwrite existing template"
    )
) -> None:
    """Save a request as a template."""
    try:
        template_manager = TemplateManager()
        
        # Parse headers and parameters
        from .request import parse_headers, parse_params
        header_dict = parse_headers(headers or [])
        param_dict = parse_params(params or [])
        
        # Handle body input
        request_body = None
        if body_file:
            request_body = body_file.read_text(encoding='utf-8')
        elif body:
            request_body = body
        
        # Save template
        template = template_manager.save_template(
            name=name,
            method=method,
            url=url,
            headers=header_dict,
            body=request_body,
            params=param_dict,
            description=description,
            tags=tags,
            overwrite=overwrite
        )
        
        console.print(f"[green]✓[/green] Template '[bold]{name}[/bold]' saved successfully")
        console.print(f"  Method: {template.method.value}")
        console.print(f"  URL: {template.url}")
        if template.description:
            console.print(f"  Description: {template.description}")
        if template.tags:
            console.print(f"  Tags: {', '.join(template.tags)}")
        
    except TemplateManagerError as e:
        console.print(f"[red]Template Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("list")
def list_templates(
    tags: Optional[List[str]] = typer.Option(
        None, 
        "--tag", 
        "-t", 
        help="Filter by tags"
    ),
    method: Optional[str] = typer.Option(
        None, 
        "--method", 
        "-m", 
        help="Filter by HTTP method"
    ),
    search: Optional[str] = typer.Option(
        None, 
        "--search", 
        "-s", 
        help="Search in name, description, or URL"
    ),
    detailed: bool = typer.Option(
        False, 
        "--detailed", 
        "-d", 
        help="Show detailed information"
    )
) -> None:
    """List saved templates."""
    try:
        template_manager = TemplateManager()
        
        # Get filtered templates
        template_names = template_manager.list_templates(
            tags=tags,
            method_filter=method,
            search_term=search
        )
        
        if not template_names:
            console.print("[yellow]No templates found matching the criteria[/yellow]")
            return
        
        if detailed:
            # Show detailed information
            metadata_list = template_manager.get_template_metadata()
            metadata_dict = {meta['name']: meta for meta in metadata_list}
            
            table = Table(title=f"Templates ({len(template_names)} found)", show_header=True, header_style="bold blue")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Method", style="yellow", no_wrap=True)
            table.add_column("URL", style="blue")
            table.add_column("Description", style="white")
            table.add_column("Tags", style="green")
            table.add_column("Created", style="dim", no_wrap=True)
            
            for name in template_names:
                meta = metadata_dict.get(name, {})
                
                # Truncate long URLs
                url = meta.get('url', '')
                if len(url) > 50:
                    url = url[:47] + "..."
                
                # Format tags
                tags_str = ', '.join(meta.get('tags', []))
                if len(tags_str) > 20:
                    tags_str = tags_str[:17] + "..."
                
                # Format creation date
                created_at = meta.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at)
                        created_str = dt.strftime('%Y-%m-%d')
                    except:
                        created_str = created_at[:10]
                else:
                    created_str = 'unknown'
                
                table.add_row(
                    name,
                    meta.get('method', 'unknown'),
                    url,
                    meta.get('description', ''),
                    tags_str,
                    created_str
                )
            
            console.print(table)
        else:
            # Show simple list
            console.print(f"[bold]Templates ({len(template_names)} found):[/bold]")
            for name in template_names:
                console.print(f"  • {name}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("show")
def show_template(
    name: str = typer.Argument(..., help="Template name"),
    show_variables: bool = typer.Option(
        False, 
        "--variables", 
        "-v", 
        help="Show variables used in template"
    )
) -> None:
    """Show template details."""
    try:
        template_manager = TemplateManager()
        template_executor = TemplateExecutor()
        
        # Load template
        template = template_manager.load_template(name)
        
        # Create display panel
        content_lines = [
            f"[bold]Method:[/bold] {template.method.value}",
            f"[bold]URL:[/bold] {template.url}",
        ]
        
        if template.description:
            content_lines.append(f"[bold]Description:[/bold] {template.description}")
        
        if template.headers:
            content_lines.append(f"[bold]Headers:[/bold]")
            for key, value in template.headers.items():
                content_lines.append(f"  {key}: {value}")
        
        if template.body:
            content_lines.append(f"[bold]Body:[/bold]")
            # Truncate long bodies
            body_display = template.body
            if len(body_display) > 200:
                body_display = body_display[:197] + "..."
            content_lines.append(f"  {body_display}")
        
        if template.params:
            content_lines.append(f"[bold]Parameters:[/bold]")
            for key, value in template.params.items():
                content_lines.append(f"  {key}={value}")
        
        if template.tags:
            content_lines.append(f"[bold]Tags:[/bold] {', '.join(template.tags)}")
        
        content_lines.extend([
            f"[bold]Created:[/bold] {template.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"[bold]Updated:[/bold] {template.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        panel = Panel(
            "\n".join(content_lines),
            title=f"Template: {name}",
            border_style="blue"
        )
        
        console.print(panel)
        
        # Show variables if requested
        if show_variables:
            try:
                variables = template_executor.extract_variables_from_template(name)
                if variables:
                    console.print(f"\n[bold]Variables used ({len(variables)}):[/bold]")
                    for var in variables:
                        console.print(f"  • ${{{var}}}")
                else:
                    console.print("\n[dim]No variables found in template[/dim]")
            except Exception as e:
                console.print(f"\n[yellow]Warning: Could not extract variables: {e}[/yellow]")
        
    except TemplateNotFoundError as e:
        console.print(f"[red]Template not found: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("delete")
def delete_template(
    name: str = typer.Argument(..., help="Template name"),
    force: bool = typer.Option(
        False, 
        "--force", 
        "-f", 
        help="Skip confirmation prompt"
    )
) -> None:
    """Delete a template."""
    try:
        template_manager = TemplateManager()
        
        # Check if template exists
        if not template_manager.template_exists(name):
            console.print(f"[red]Template '{name}' not found[/red]")
            raise typer.Exit(1)
        
        # Confirm deletion unless force flag is used
        if not force:
            confirm = typer.confirm(f"Delete template '{name}'?")
            if not confirm:
                console.print("Deletion cancelled")
                return
        
        # Delete template
        success = template_manager.delete_template(name)
        
        if success:
            console.print(f"[green]✓[/green] Template '[bold]{name}[/bold]' deleted successfully")
        else:
            console.print(f"[red]Failed to delete template '{name}'[/red]")
            raise typer.Exit(1)
        
    except TemplateNotFoundError as e:
        console.print(f"[red]Template not found: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("export")
def export_templates(
    output_file: Path = typer.Argument(..., help="Output file path"),
    templates: Optional[List[str]] = typer.Option(
        None, 
        "--template", 
        "-t", 
        help="Specific templates to export (default: all)"
    ),
    format_type: Optional[str] = typer.Option(
        None, 
        "--format", 
        "-f", 
        help="Export format (json/yaml, auto-detected from file extension)"
    ),
    include_metadata: bool = typer.Option(
        True, 
        "--metadata/--no-metadata", 
        help="Include creation/update timestamps"
    ),
    overwrite: bool = typer.Option(
        False, 
        "--overwrite", 
        help="Overwrite existing file"
    )
) -> None:
    """Export templates to file."""
    try:
        template_importer = TemplateImporter()
        
        # Export templates
        saved_path = template_importer.export_templates_to_file(
            file_path=output_file,
            template_names=templates,
            format_type=format_type,
            include_metadata=include_metadata,
            overwrite=overwrite
        )
        
        # Count exported templates
        template_count = len(templates) if templates else len(TemplateManager().list_templates())
        
        console.print(f"[green]✓[/green] Exported {template_count} templates to [bold]{saved_path}[/bold]")
        
    except TemplateExportError as e:
        console.print(f"[red]Export Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("import")
def import_templates(
    input_file: Path = typer.Argument(..., help="Input file path"),
    format_type: Optional[str] = typer.Option(
        None, 
        "--format", 
        "-f", 
        help="Import format (json/yaml, auto-detected from file extension)"
    ),
    overwrite: bool = typer.Option(
        False, 
        "--overwrite", 
        help="Overwrite existing templates"
    ),
    validate: bool = typer.Option(
        True, 
        "--validate/--no-validate", 
        help="Validate templates before importing"
    ),
    dry_run: bool = typer.Option(
        False, 
        "--dry-run", 
        help="Show what would be imported without actually importing"
    )
) -> None:
    """Import templates from file."""
    try:
        template_importer = TemplateImporter()
        
        # Import templates
        results = template_importer.import_templates_from_file(
            file_path=input_file,
            format_type=format_type,
            overwrite_existing=overwrite,
            validate_before_import=validate,
            dry_run=dry_run
        )
        
        # Display results
        if dry_run:
            console.print(f"[cyan]Dry run results:[/cyan]")
        
        console.print(f"[green]✓[/green] Import completed:")
        console.print(f"  Imported: {results['imported_count']}")
        console.print(f"  Skipped: {results['skipped_count']}")
        console.print(f"  Errors: {results['error_count']}")
        
        # Show imported templates
        if results['imported_templates']:
            console.print(f"\n[bold]Imported templates:[/bold]")
            for template in results['imported_templates']:
                status = " (overwritten)" if template.get('overwritten') else ""
                console.print(f"  • {template['name']} ({template['method']} {template['url']}){status}")
        
        # Show skipped templates
        if results['skipped_templates']:
            console.print(f"\n[yellow]Skipped templates:[/yellow]")
            for template in results['skipped_templates']:
                console.print(f"  • {template['name']} - {template['reason']}")
        
        # Show errors
        if results['errors']:
            console.print(f"\n[red]Errors:[/red]")
            for error in results['errors']:
                console.print(f"  • {error['template_name']}: {error['error']}")
        
    except TemplateImportError as e:
        console.print(f"[red]Import Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("search")
def search_templates(
    query: str = typer.Argument(..., help="Search query"),
    fields: Optional[List[str]] = typer.Option(
        None, 
        "--field", 
        help="Fields to search in (name, description, url, tags)"
    )
) -> None:
    """Search templates."""
    try:
        template_manager = TemplateManager()
        
        # Search templates
        results = template_manager.search_templates(query, fields)
        
        if not results:
            console.print(f"[yellow]No templates found matching '{query}'[/yellow]")
            return
        
        # Display results
        table = Table(title=f"Search Results for '{query}' ({len(results)} found)", 
                     show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Method", style="yellow", no_wrap=True)
        table.add_column("URL", style="blue")
        table.add_column("Matches", style="green", no_wrap=True)
        
        for result in results:
            # Truncate long URLs
            url = result['url']
            if len(url) > 60:
                url = url[:57] + "..."
            
            # Format matched fields
            matches = ', '.join(result['matched_fields'])
            
            table.add_row(
                result['name'],
                result['method'],
                url,
                matches
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("duplicate")
def duplicate_template(
    source_name: str = typer.Argument(..., help="Source template name"),
    new_name: str = typer.Argument(..., help="New template name"),
    description_suffix: str = typer.Option(
        " (copy)", 
        "--suffix", 
        help="Suffix to add to description"
    )
) -> None:
    """Duplicate a template."""
    try:
        template_manager = TemplateManager()
        
        # Duplicate template
        new_template = template_manager.duplicate_template(
            source_name=source_name,
            new_name=new_name,
            description_suffix=description_suffix
        )
        
        console.print(f"[green]✓[/green] Template '[bold]{source_name}[/bold]' duplicated as '[bold]{new_name}[/bold]'")
        console.print(f"  Method: {new_template.method.value}")
        console.print(f"  URL: {new_template.url}")
        
    except TemplateNotFoundError as e:
        console.print(f"[red]Template not found: {e}[/red]")
        raise typer.Exit(1)
    except TemplateManagerError as e:
        console.print(f"[red]Template Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@template_app.command("validate")
def validate_template(
    name: str = typer.Argument(..., help="Template name"),
    environment: str = typer.Option(
        "default", 
        "--env", 
        "-e", 
        help="Environment to validate variables against"
    ),
    ai_validate: bool = typer.Option(
        False,
        "--ai-validate",
        help="Use AI to validate template structure and suggest improvements"
    )
) -> None:
    """Validate a template and its variables."""
    try:
        template_manager = TemplateManager()
        template_executor = TemplateExecutor()
        
        # Load template
        template = template_manager.load_template(name)
        
        # Validate template structure
        validation_errors = template.validate()
        
        # Validate variables
        variable_validation = template_executor.validate_template_variables(name, environment)
        
        # Display results
        console.print(f"[bold]Validation Results for Template '{name}':[/bold]")
        
        # Template structure validation
        if validation_errors:
            console.print(f"[red]✗ Template Structure Errors:[/red]")
            for error in validation_errors:
                console.print(f"  • {error}")
        else:
            console.print(f"[green]✓ Template structure is valid[/green]")
        
        # Variable validation
        if variable_validation['valid']:
            console.print(f"[green]✓ All variables can be resolved[/green]")
        else:
            console.print(f"[red]✗ Variable resolution errors:[/red]")
            for var in variable_validation['missing_variables']:
                console.print(f"  • Missing variable: ${{{var}}}")
        
        # Show variables found
        if variable_validation['variables_found']:
            console.print(f"\n[bold]Variables found ({len(variable_validation['variables_found'])}):[/bold]")
            for var in variable_validation['variables_found']:
                status = "✓" if var in variable_validation['available_variables'] else "✗"
                console.print(f"  {status} ${{{var}}}")
        
        # AI validation if requested
        if ai_validate:
            try:
                config = get_config()
                if config.ai.enabled:
                    console.print(f"\n[bold blue]AI Validation Analysis:[/bold blue]")
                    
                    ai_assistant = AIAssistant()
                    
                    # Validate JSON body if present
                    if template.body and template.body.strip().startswith(('{', '[')):
                        validator = JSONValidator(ai_assistant)
                        json_result = validator.validate_json(template.body, use_ai=True)
                        
                        if json_result.get('ai_analysis'):
                            console.print("JSON Body Analysis:")
                            console.print(f"  {json_result['ai_analysis']}")
                        
                        if json_result['suggestions']:
                            console.print("JSON Suggestions:")
                            for suggestion in json_result['suggestions'][:3]:
                                console.print(f"  • {suggestion}")
                    
                    # Get AI suggestions for the template
                    template_info = {
                        "url": template.url,
                        "method": template.method.value,
                        "description": template.description or f"{template.method.value} {template.url}",
                        "headers": template.headers,
                        "body": template.body
                    }
                    
                    ai_response = ai_assistant.suggest_test_cases(template_info)
                    if ai_response and ai_response.content:
                        console.print("\nAI Template Analysis:")
                        # Show first few lines of AI analysis
                        lines = ai_response.content.split('\n')[:5]
                        for line in lines:
                            if line.strip():
                                console.print(f"  {line.strip()}")
                else:
                    console.print(f"\n[yellow]AI validation requested but AI not enabled[/yellow]")
            except AIAssistantError as e:
                console.print(f"\n[yellow]AI validation failed: {e}[/yellow]")
            except Exception:
                pass  # Don't fail validation for AI errors
        
        # Overall status
        overall_valid = not validation_errors and variable_validation['valid']
        if overall_valid:
            console.print(f"\n[green]✓ Template '{name}' is ready for execution[/green]")
        else:
            console.print(f"\n[red]✗ Template '{name}' has validation issues[/red]")
            raise typer.Exit(1)
        
    except TemplateNotFoundError as e:
        console.print(f"[red]Template not found: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@template_app.command("ai-suggest")
def ai_suggest_template(
    url: str = typer.Argument(..., help="API endpoint URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Template description"),
    save_template: bool = typer.Option(False, "--save", "-s", help="Save the suggested template"),
    template_name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for saved template")
) -> None:
    """Use AI to suggest a complete template for an API endpoint."""
    try:
        config = get_config()
        if not config.ai.enabled:
            console.print("[red]AI assistant is not enabled[/red]")
            console.print("Enable AI in configuration to use this feature")
            raise typer.Exit(1)
        
        ai_assistant = AIAssistant()
        
        # Get AI suggestions for headers
        from ..ai.integrations import HeaderSuggestionEngine
        header_engine = HeaderSuggestionEngine(ai_assistant)
        
        with console.status(f"[bold green]Analyzing {method} {url} with AI..."):
            suggested_headers = header_engine.suggest_headers(url, method, use_ai=True)
            
            # Get AI suggestions for the endpoint
            endpoint_info = {
                "url": url,
                "method": method,
                "description": description or f"{method} {url}"
            }
            
            ai_response = ai_assistant.suggest_test_cases(endpoint_info)
        
        # Display suggestions
        console.print(f"[bold blue]AI Template Suggestions for {method} {url}[/bold blue]")
        
        # Show suggested headers
        if suggested_headers:
            console.print(f"\n[bold cyan]Suggested Headers:[/bold cyan]")
            for header, value in suggested_headers.items():
                console.print(f"  {header}: {value}")
        
        # Show AI analysis
        if ai_response and ai_response.content:
            console.print(f"\n[bold cyan]AI Analysis:[/bold cyan]")
            # Parse and display key insights
            lines = ai_response.content.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    console.print(f"  {line.strip()}")
        
        # Offer to save as template
        if save_template:
            if not template_name:
                # Generate template name from URL
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                template_name = f"{method.lower()}-{parsed_url.netloc.replace('.', '-')}-{parsed_url.path.replace('/', '-').strip('-')}"
                template_name = template_name[:50]  # Limit length
            
            try:
                template_manager = TemplateManager()
                
                # Create template with AI suggestions
                template = template_manager.save_template(
                    name=template_name,
                    method=method,
                    url=url,
                    headers=suggested_headers,
                    description=description or f"AI-suggested template for {method} {url}",
                    tags=["ai-generated"],
                    overwrite=False
                )
                
                console.print(f"\n[green]✓ Template '{template_name}' saved with AI suggestions[/green]")
                console.print(f"Execute with: apitester request template {template_name}")
                
            except TemplateManagerError as e:
                console.print(f"\n[red]Failed to save template: {e}[/red]")
        else:
            console.print(f"\n[dim]To save as template, use: --save --name my-template-name[/dim]")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
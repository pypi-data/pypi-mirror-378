"""AI assistant commands for the CLI."""

import typer
import json
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from ..ai.assistant import AIAssistant, AIAssistantError, AIProvider
from ..ai.integrations import (
    HeaderSuggestionEngine, 
    StatusCodeExplainer, 
    JSONValidator,
    OpenAPIIntegration,
    ErrorMessageInterpreter
)
from ..config.settings import get_config

# Create console for output
console = Console()

# Create AI app
ai_app = typer.Typer(
    name="ai",
    help="AI-powered assistance for API testing",
    rich_markup_mode="rich"
)


def get_ai_assistant() -> Optional[AIAssistant]:
    """Get configured AI assistant or None if not available."""
    try:
        config = get_config()
        if not config.ai.enabled:
            return None
        
        return AIAssistant()
    except Exception:
        return None


def check_ai_availability() -> bool:
    """Check if AI assistant is available and show error if not."""
    assistant = get_ai_assistant()
    if not assistant or not assistant.is_available():
        console.print("[red]AI assistant is not configured or available[/red]")
        console.print("Enable AI in configuration and set API key:")
        console.print("  apitester config --help")
        return False
    return True


@ai_app.command("status")
def ai_status() -> None:
    """Show AI assistant status and configuration."""
    config = get_config()
    
    table = Table(title="AI Assistant Status", show_header=True, header_style="bold blue")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Status", style="green")
    
    # AI configuration
    table.add_row("Enabled", str(config.ai.enabled), "✅" if config.ai.enabled else "❌")
    table.add_row("Provider", config.ai.provider, "✅" if config.ai.provider else "❌")
    table.add_row("Model", config.ai.model or "default", "✅" if config.ai.model else "⚠️")
    
    # API key status
    api_key_status = "✅ Configured" if config.ai.api_key else "❌ Missing"
    table.add_row("API Key", "***" if config.ai.api_key else "Not set", api_key_status)
    
    # Test connection
    assistant = get_ai_assistant()
    if assistant and assistant.is_available():
        connection_status = "✅ Available"
        try:
            # Quick test
            test_response = assistant.explain_status_code(200)
            if test_response and test_response.content:
                connection_status = "✅ Working"
        except Exception:
            connection_status = "⚠️ Connection issues"
    else:
        connection_status = "❌ Not available"
    
    table.add_row("Connection", "", connection_status)
    
    console.print(table)
    
    if not config.ai.enabled:
        console.print("\n[yellow]To enable AI assistant:[/yellow]")
        console.print("1. Set AI provider and API key in configuration")
        console.print("2. Enable AI in config: ai.enabled = true")
        console.print("3. Test with: apitester ai status")


@ai_app.command("suggest-headers")
def suggest_headers(
    url: str = typer.Argument(..., help="Request URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, headers)")
) -> None:
    """Suggest appropriate headers for a request."""
    if not check_ai_availability():
        return
    
    try:
        assistant = get_ai_assistant()
        header_engine = HeaderSuggestionEngine(assistant)
        
        with console.status(f"[bold green]Analyzing {method} {url}..."):
            suggested_headers = header_engine.suggest_headers(url, method)
        
        if not suggested_headers:
            console.print("[yellow]No header suggestions available[/yellow]")
            return
        
        if output_format == "json":
            console.print(json.dumps(suggested_headers, indent=2))
        elif output_format == "headers":
            for key, value in suggested_headers.items():
                console.print(f"{key}: {value}")
        else:  # table format
            table = Table(title=f"Suggested Headers for {method} {url}", show_header=True, header_style="bold blue")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Purpose", style="dim")
            
            # Add purpose explanations for common headers
            purposes = {
                "Authorization": "Authentication credentials",
                "Content-Type": "Request body format",
                "Accept": "Expected response format",
                "User-Agent": "Client identification",
                "Accept-Encoding": "Supported compression",
                "Cache-Control": "Caching behavior"
            }
            
            for header, value in suggested_headers.items():
                purpose = purposes.get(header, "API-specific header")
                table.add_row(header, value, purpose)
            
            console.print(table)
        
        console.print(f"\n[dim]Use these headers with: --header \"{list(suggested_headers.keys())[0]}: {list(suggested_headers.values())[0]}\"[/dim]")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("explain-status")
def explain_status_code(
    status_code: int = typer.Argument(..., help="HTTP status code to explain"),
    response_body: Optional[str] = typer.Option(None, "--body", "-b", help="Response body for context"),
    response_file: Optional[Path] = typer.Option(None, "--body-file", "-f", help="File containing response body")
) -> None:
    """Explain HTTP status code and suggest solutions."""
    if not check_ai_availability():
        return
    
    try:
        assistant = get_ai_assistant()
        explainer = StatusCodeExplainer(assistant)
        
        # Load response body from file if provided
        if response_file and response_file.exists():
            response_body = response_file.read_text(encoding='utf-8')
        
        with console.status(f"[bold green]Analyzing status code {status_code}..."):
            explanation = explainer.explain_status_code(status_code, response_body)
        
        # Display explanation
        console.print(f"[bold blue]HTTP {status_code} - {explanation['meaning']}[/bold blue]")
        console.print(f"Category: [{explanation['category'].lower().replace(' ', '_')}]{explanation['category']}[/{explanation['category'].lower().replace(' ', '_')}]")
        
        if explanation.get('ai_explanation'):
            console.print("\n[bold]AI Analysis:[/bold]")
            markdown = Markdown(explanation['ai_explanation'])
            console.print(Panel(markdown, border_style="blue", padding=(1, 2)))
        
        if explanation['suggestions']:
            console.print("\n[bold yellow]Troubleshooting Suggestions:[/bold yellow]")
            for i, suggestion in enumerate(explanation['suggestions'], 1):
                console.print(f"  {i}. {suggestion}")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("validate-json")
def validate_json(
    json_input: Optional[str] = typer.Argument(None, help="JSON string to validate"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="File containing JSON to validate"),
    schema: Optional[str] = typer.Option(None, "--schema", "-s", help="Expected schema or format description")
) -> None:
    """Validate JSON structure and get improvement suggestions."""
    if not check_ai_availability():
        return
    
    if not json_input and not json_file:
        console.print("[red]Provide JSON string as argument or use --file option[/red]")
        raise typer.Exit(1)
    
    try:
        # Load JSON data
        if json_file and json_file.exists():
            json_data = json_file.read_text(encoding='utf-8')
        else:
            json_data = json_input
        
        assistant = get_ai_assistant()
        validator = JSONValidator(assistant)
        
        with console.status("[bold green]Validating JSON structure..."):
            result = validator.validate_json(json_data, schema)
        
        # Display results
        if result['valid']:
            console.print("[green]✅ JSON is valid[/green]")
        else:
            console.print("[red]❌ JSON validation failed[/red]")
            for error in result['errors']:
                console.print(f"  • {error}")
        
        if result.get('ai_analysis'):
            console.print("\n[bold]AI Analysis:[/bold]")
            markdown = Markdown(result['ai_analysis'])
            console.print(Panel(markdown, border_style="blue", padding=(1, 2)))
        
        if result['suggestions']:
            console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for i, suggestion in enumerate(result['suggestions'], 1):
                console.print(f"  {i}. {suggestion}")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("generate-examples")
def generate_examples(
    spec_file: Path = typer.Argument(..., help="OpenAPI/Swagger specification file"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", "-e", help="Specific endpoint to focus on"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, curl)"),
    save_file: Optional[Path] = typer.Option(None, "--save", "-s", help="Save examples to file")
) -> None:
    """Generate request examples from OpenAPI/Swagger specification."""
    if not check_ai_availability():
        return
    
    if not spec_file.exists():
        console.print(f"[red]Specification file not found: {spec_file}[/red]")
        raise typer.Exit(1)
    
    try:
        # Load API specification
        spec_content = spec_file.read_text(encoding='utf-8')
        
        assistant = get_ai_assistant()
        openapi_integration = OpenAPIIntegration(assistant)
        
        with console.status("[bold green]Generating request examples..."):
            result = openapi_integration.generate_request_examples(spec_content, endpoint)
        
        examples = result['examples']
        
        if not examples:
            console.print("[yellow]No examples could be generated[/yellow]")
            return
        
        # Display examples
        if output_format == "json":
            output = json.dumps(examples, indent=2)
            console.print(output)
        elif output_format == "curl":
            for i, example in enumerate(examples, 1):
                console.print(f"[bold cyan]Example {i}: {example.get('description', 'Request')}[/bold cyan]")
                curl_cmd = f"curl -X {example['method']} '{example['url']}'"
                
                for header, value in example.get('headers', {}).items():
                    curl_cmd += f" \\\\\n  -H '{header}: {value}'"
                
                if example.get('body'):
                    curl_cmd += f" \\\\\n  -d '{example['body']}'"
                
                console.print(f"[dim]{curl_cmd}[/dim]")
                console.print()
        else:  # table format
            table = Table(title=f"Generated Examples ({len(examples)} found)", show_header=True, header_style="bold blue")
            table.add_column("Method", style="cyan", width=8)
            table.add_column("Endpoint", style="blue")
            table.add_column("Description", style="white")
            table.add_column("Headers", style="dim", width=15)
            
            for example in examples:
                url = example['url']
                if len(url) > 50:
                    url = url[:47] + "..."
                
                headers_count = len(example.get('headers', {}))
                headers_text = f"{headers_count} headers" if headers_count > 0 else "None"
                
                table.add_row(
                    example['method'],
                    url,
                    example.get('description', 'API request')[:40],
                    headers_text
                )
            
            console.print(table)
        
        # Save to file if requested
        if save_file:
            if output_format == "json":
                save_file.write_text(json.dumps(examples, indent=2))
            else:
                # Save as shell script with curl commands
                script_content = "#!/bin/bash\n# Generated API examples\n\n"
                for i, example in enumerate(examples, 1):
                    script_content += f"# Example {i}: {example.get('description', 'Request')}\n"
                    curl_cmd = f"curl -X {example['method']} '{example['url']}'"
                    
                    for header, value in example.get('headers', {}).items():
                        curl_cmd += f" \\\\\n  -H '{header}: {value}'"
                    
                    if example.get('body'):
                        curl_cmd += f" \\\\\n  -d '{example['body']}'"
                    
                    script_content += curl_cmd + "\n\n"
                
                save_file.write_text(script_content)
            
            console.print(f"[green]Examples saved to {save_file}[/green]")
        
        if result['ai_generated']:
            console.print(f"\n[dim]Examples generated using AI assistance[/dim]")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("interpret-error")
def interpret_error(
    error_message: str = typer.Argument(..., help="Error message to interpret"),
    context_file: Optional[Path] = typer.Option(None, "--context", "-c", help="JSON file with request context"),
    method: Optional[str] = typer.Option(None, "--method", "-m", help="HTTP method used"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Request URL"),
    status_code: Optional[int] = typer.Option(None, "--status", "-s", help="HTTP status code")
) -> None:
    """Interpret error messages and suggest solutions."""
    if not check_ai_availability():
        return
    
    try:
        # Build request context
        request_context = {}
        
        if context_file and context_file.exists():
            context_data = json.loads(context_file.read_text(encoding='utf-8'))
            request_context.update(context_data)
        
        if method:
            request_context['method'] = method
        if url:
            request_context['url'] = url
        if status_code:
            request_context['status_code'] = status_code
        
        assistant = get_ai_assistant()
        interpreter = ErrorMessageInterpreter(assistant)
        
        with console.status("[bold green]Interpreting error message..."):
            result = interpreter.interpret_error(error_message, request_context)
        
        # Display results
        console.print(f"[bold red]Error Analysis[/bold red]")
        console.print(f"Error Type: {result['error_type'].replace('_', ' ').title()}")
        
        if result['causes']:
            console.print("\n[bold yellow]Possible Causes:[/bold yellow]")
            for cause in result['causes']:
                console.print(f"  • {cause}")
        
        if result['solutions']:
            console.print("\n[bold green]Suggested Solutions:[/bold green]")
            for i, solution in enumerate(result['solutions'], 1):
                console.print(f"  {i}. {solution}")
        
        if result.get('ai_interpretation'):
            console.print("\n[bold]AI Analysis:[/bold]")
            markdown = Markdown(result['ai_interpretation'])
            console.print(Panel(markdown, border_style="blue", padding=(1, 2)))
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("test-cases")
def suggest_test_cases(
    endpoint_url: str = typer.Argument(..., help="API endpoint URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Endpoint description"),
    parameters: Optional[List[str]] = typer.Option(None, "--param", "-p", help="Parameters in 'name:type' format"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, markdown)")
) -> None:
    """Suggest comprehensive test cases for an API endpoint."""
    if not check_ai_availability():
        return
    
    try:
        # Build endpoint info
        endpoint_info = {
            "url": endpoint_url,
            "method": method,
            "description": description or f"{method} {endpoint_url}"
        }
        
        if parameters:
            endpoint_info["parameters"] = []
            for param in parameters:
                if ':' in param:
                    name, param_type = param.split(':', 1)
                    endpoint_info["parameters"].append({
                        "name": name.strip(),
                        "type": param_type.strip()
                    })
        
        assistant = get_ai_assistant()
        
        with console.status("[bold green]Generating test cases..."):
            ai_response = assistant.suggest_test_cases(endpoint_info)
        
        # Display test cases
        if output_format == "json":
            test_cases = {
                "endpoint": endpoint_info,
                "ai_suggestions": ai_response.content,
                "metadata": ai_response.metadata
            }
            console.print(json.dumps(test_cases, indent=2))
        elif output_format == "markdown":
            console.print(ai_response.content)
        else:  # table format
            console.print(f"[bold blue]Test Cases for {method} {endpoint_url}[/bold blue]")
            
            # Parse AI response for structured display
            content = ai_response.content
            sections = content.split('\n\n')
            
            for section in sections:
                if section.strip():
                    lines = section.strip().split('\n')
                    if lines:
                        # Check if this looks like a section header
                        header = lines[0].strip()
                        if header.endswith(':') or header.startswith('#'):
                            console.print(f"\n[bold cyan]{header}[/bold cyan]")
                            for line in lines[1:]:
                                if line.strip():
                                    console.print(f"  {line.strip()}")
                        else:
                            for line in lines:
                                if line.strip():
                                    console.print(f"  {line.strip()}")
        
        console.print(f"\n[dim]Test cases generated using AI assistance[/dim]")
        
    except AIAssistantError as e:
        console.print(f"[red]AI Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@ai_app.command("configure")
def configure_ai(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (openai, anthropic, gemini)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key for the provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name to use"),
    enable: Optional[bool] = typer.Option(None, "--enable/--disable", help="Enable or disable AI assistant"),
    test_connection: bool = typer.Option(False, "--test", help="Test the AI connection after configuration")
) -> None:
    """Configure AI assistant settings."""
    
    if not any([provider, api_key, model, enable is not None]):
        # Show current configuration
        ai_status()
        return
    
    try:
        config = get_config()
        
        # Update configuration
        if provider:
            if provider.lower() not in ["openai", "anthropic", "gemini"]:
                console.print(f"[red]Unsupported provider: {provider}[/red]")
                console.print("Supported providers: openai, anthropic, gemini")
                raise typer.Exit(1)
            config.ai.provider = provider.lower()
            console.print(f"[green]Set AI provider to: {provider}[/green]")
        
        if api_key:
            config.ai.api_key = api_key
            console.print("[green]API key updated[/green]")
        
        if model:
            config.ai.model = model
            console.print(f"[green]Set model to: {model}[/green]")
        
        if enable is not None:
            config.ai.enabled = enable
            status_text = "enabled" if enable else "disabled"
            console.print(f"[green]AI assistant {status_text}[/green]")
        
        # Save configuration (this would need to be implemented in config manager)
        # config_manager.save_config(config)
        
        # Test connection if requested
        if test_connection and config.ai.enabled:
            console.print("\n[cyan]Testing AI connection...[/cyan]")
            try:
                assistant = AIAssistant()
                if assistant.is_available():
                    test_response = assistant.explain_status_code(200)
                    if test_response and test_response.content:
                        console.print("[green]✅ AI assistant is working correctly[/green]")
                    else:
                        console.print("[yellow]⚠️ AI assistant responded but with empty content[/yellow]")
                else:
                    console.print("[red]❌ AI assistant is not available[/red]")
            except Exception as e:
                console.print(f"[red]❌ Connection test failed: {e}[/red]")
        
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
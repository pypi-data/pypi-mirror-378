"""Request execution commands for the CLI."""

import typer
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..core.http_client import HTTPClient, HTTPClientError
from ..core.graphql_client import GraphQLClient, GraphQLError
from ..core.template_executor import TemplateExecutor, TemplateExecutionError
from ..core.history_manager import HistoryManager
from ..core.cache_manager import CacheManager
from ..formatters.response_formatter import ResponseFormatter
from ..formatters.table_formatter import TableFormatter
from ..formatters.response_saver import ResponseSaver
from ..config.settings import get_config
from ..ai.assistant import AIAssistant, AIAssistantError
from ..ai.integrations import HeaderSuggestionEngine, StatusCodeExplainer, ErrorMessageInterpreter

# Create console for output
console = Console()

# Create request app
request_app = typer.Typer(
    name="request",
    help="Execute HTTP and GraphQL requests",
    rich_markup_mode="rich"
)


def parse_headers(headers: List[str]) -> Dict[str, str]:
    """Parse header strings into dictionary."""
    header_dict = {}
    for header in headers:
        if ':' in header:
            key, value = header.split(':', 1)
            header_dict[key.strip()] = value.strip()
        else:
            console.print(f"[yellow]Warning: Invalid header format '{header}', expected 'Key: Value'[/yellow]")
    return header_dict


def parse_params(params: List[str]) -> Dict[str, str]:
    """Parse parameter strings into dictionary."""
    param_dict = {}
    for param in params:
        if '=' in param:
            key, value = param.split('=', 1)
            param_dict[key.strip()] = value.strip()
        else:
            console.print(f"[yellow]Warning: Invalid parameter format '{param}', expected 'key=value'[/yellow]")
    return param_dict


@request_app.command("send")
def send_request(
    method: str = typer.Argument(..., help="HTTP method (GET, POST, PUT, PATCH, DELETE, OPTIONS)"),
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
        help="Request body (JSON string or @filename)"
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
    environment: str = typer.Option(
        "default", 
        "--env", 
        "-e", 
        help="Environment to use for variable substitution"
    ),
    no_cache: bool = typer.Option(
        False, 
        "--no-cache", 
        help="Disable response caching"
    ),
    save_response: Optional[Path] = typer.Option(
        None, 
        "--save", 
        "-s", 
        help="Save response to file"
    ),
    table_view: bool = typer.Option(
        False, 
        "--table", 
        "-t", 
        help="Display array responses in table format"
    ),
    no_history: bool = typer.Option(
        False, 
        "--no-history", 
        help="Don't save request to history"
    ),
    max_retries: int = typer.Option(
        3, 
        "--retries", 
        help="Maximum number of retry attempts"
    ),
    ai_suggest_headers: bool = typer.Option(
        False,
        "--ai-headers",
        help="Use AI to suggest appropriate headers"
    ),
    ai_explain_response: bool = typer.Option(
        False,
        "--ai-explain",
        help="Use AI to explain response status and errors"
    )
) -> None:
    """Send an HTTP request."""
    try:
        # Initialize components
        http_client = HTTPClient()
        history_manager = HistoryManager()
        cache_manager = CacheManager()
        formatter = ResponseFormatter(console)
        table_formatter = TableFormatter(console)
        response_saver = ResponseSaver()
        
        # Parse headers and parameters
        header_dict = parse_headers(headers or [])
        param_dict = parse_params(params or [])
        
        # Use AI to suggest headers if requested
        if ai_suggest_headers:
            try:
                config = get_config()
                if config.ai.enabled:
                    ai_assistant = AIAssistant()
                    header_engine = HeaderSuggestionEngine(ai_assistant)
                    suggested_headers = header_engine.suggest_headers(url, method, use_ai=True)
                    
                    # Merge suggested headers (don't override existing)
                    for key, value in suggested_headers.items():
                        if key not in header_dict:
                            header_dict[key] = value
                            console.print(f"[dim]AI suggested header: {key}: {value}[/dim]")
                else:
                    console.print("[yellow]AI not enabled, skipping header suggestions[/yellow]")
            except AIAssistantError as e:
                console.print(f"[yellow]AI header suggestion failed: {e}[/yellow]")
        
        # Handle body input
        request_body = None
        if body_file:
            request_body = body_file.read_text(encoding='utf-8')
        elif body:
            if body.startswith('@'):
                # Read from file
                file_path = Path(body[1:])
                request_body = file_path.read_text(encoding='utf-8')
            else:
                request_body = body
        
        # Validate JSON body with AI if requested and body looks like JSON
        if request_body and ai_explain_response and request_body.strip().startswith(('{', '[')):
            try:
                config = get_config()
                if config.ai.enabled:
                    from ..ai.integrations import JSONValidator
                    ai_assistant = AIAssistant()
                    validator = JSONValidator(ai_assistant)
                    
                    validation_result = validator.validate_json(request_body, use_ai=True)
                    
                    if not validation_result['valid']:
                        console.print("[yellow]JSON validation issues detected:[/yellow]")
                        for error in validation_result['errors']:
                            console.print(f"  • {error}")
                    
                    if validation_result['suggestions']:
                        console.print("[dim]AI suggestions for JSON body:[/dim]")
                        for suggestion in validation_result['suggestions'][:2]:
                            console.print(f"  • {suggestion}")
            except Exception:
                pass  # Don't block request for validation errors
        
        # Check cache first (if enabled)
        cached_response = None
        if not no_cache:
            cached_response = cache_manager.get_cached_response(
                method=method,
                url=url,
                headers=header_dict,
                body=request_body,
                params=param_dict
            )
        
        if cached_response:
            console.print("[cyan]Using cached response[/cyan]")
            cache_entry, hit_count = cached_response
            
            # Create mock response object for formatting
            class CachedResponse:
                def __init__(self, entry):
                    self.status_code = entry['response_status']
                    self.headers = entry['response_headers']
                    self.text = entry['response_body']
                    self.url = entry['url']
                    self.request_time = 0.0
                    self.from_cache = True
            
            response = CachedResponse(cache_entry)
        else:
            # Make actual request
            with console.status(f"[bold green]Sending {method.upper()} request to {url}..."):
                response = http_client.send_request(
                    method=method,
                    url=url,
                    headers=header_dict,
                    body=request_body,
                    params=param_dict,
                    max_retries=max_retries
                )
            
            # Cache response if successful and caching enabled
            if not no_cache and response.is_success():
                cache_manager.cache_response(
                    method=method,
                    url=url,
                    headers=header_dict,
                    response=response,
                    body=request_body,
                    params=param_dict
                )
        
        # Display response
        if table_view and response.text:
            try:
                # Try to parse as JSON and display as table
                data = json.loads(response.text)
                if table_formatter.detect_table_structure(data):
                    table_formatter.display_table(data, f"Response from {url}")
                else:
                    formatter.format_http_response(response)
            except json.JSONDecodeError:
                formatter.format_http_response(response)
        else:
            formatter.format_http_response(response)
        
        # Use AI to explain response if requested
        if ai_explain_response:
            try:
                config = get_config()
                if config.ai.enabled:
                    ai_assistant = AIAssistant()
                    explainer = StatusCodeExplainer(ai_assistant)
                    
                    # Get response body for context (limit size)
                    response_body = response.text[:1000] if response.text else None
                    explanation = explainer.explain_status_code(response.status_code, response_body, use_ai=True)
                    
                    console.print(f"\n[bold blue]AI Analysis:[/bold blue]")
                    console.print(f"Status: {explanation['meaning']}")
                    
                    if explanation.get('ai_explanation'):
                        console.print(f"\n{explanation['ai_explanation']}")
                    
                    if explanation['suggestions']:
                        console.print(f"\n[bold yellow]Suggestions:[/bold yellow]")
                        for i, suggestion in enumerate(explanation['suggestions'][:3], 1):
                            console.print(f"  {i}. {suggestion}")
                else:
                    console.print("[yellow]AI not enabled, skipping response explanation[/yellow]")
            except AIAssistantError as e:
                console.print(f"[yellow]AI response explanation failed: {e}[/yellow]")
        
        # Save response if requested
        if save_response:
            saved_files = response_saver.save_complete_response(
                response=response,
                directory=save_response.parent,
                base_name=save_response.stem
            )
            console.print(f"[green]Response saved to {saved_files['body']}[/green]")
        
        # Add to history (unless disabled)
        if not no_history:
            history_manager.add_request(
                method=method,
                url=url,
                headers=header_dict,
                body=request_body,
                params=param_dict,
                response=response,
                environment=environment
            )
        
    except HTTPClientError as e:
        console.print(f"[red]HTTP Error: {e}[/red]")
        
        # Use AI to interpret error if available
        if ai_explain_response:
            try:
                config = get_config()
                if config.ai.enabled:
                    ai_assistant = AIAssistant()
                    interpreter = ErrorMessageInterpreter(ai_assistant)
                    
                    request_context = {
                        "method": method,
                        "url": url,
                        "headers": header_dict,
                        "error_type": "http_client_error"
                    }
                    
                    result = interpreter.interpret_error(str(e), request_context, use_ai=True)
                    
                    if result.get('ai_interpretation'):
                        console.print(f"\n[bold blue]AI Error Analysis:[/bold blue]")
                        console.print(result['ai_interpretation'])
                    
                    if result['solutions']:
                        console.print(f"\n[bold yellow]Suggested Solutions:[/bold yellow]")
                        for i, solution in enumerate(result['solutions'][:3], 1):
                            console.print(f"  {i}. {solution}")
            except Exception:
                pass  # Don't let AI errors mask the original error
        
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        
        # Use AI to interpret error if available
        if ai_explain_response:
            try:
                config = get_config()
                if config.ai.enabled:
                    ai_assistant = AIAssistant()
                    interpreter = ErrorMessageInterpreter(ai_assistant)
                    
                    request_context = {
                        "method": method,
                        "url": url,
                        "headers": header_dict,
                        "error_type": "general_error"
                    }
                    
                    result = interpreter.interpret_error(str(e), request_context, use_ai=True)
                    
                    if result.get('ai_interpretation'):
                        console.print(f"\n[bold blue]AI Error Analysis:[/bold blue]")
                        console.print(result['ai_interpretation'])
                    
                    if result['solutions']:
                        console.print(f"\n[bold yellow]Suggested Solutions:[/bold yellow]")
                        for i, solution in enumerate(result['solutions'][:3], 1):
                            console.print(f"  {i}. {solution}")
            except Exception:
                pass  # Don't let AI errors mask the original error
        
        raise typer.Exit(1)


@request_app.command("graphql")
def send_graphql_request(
    url: str = typer.Argument(..., help="GraphQL endpoint URL"),
    query: Optional[str] = typer.Option(
        None, 
        "--query", 
        "-q", 
        help="GraphQL query string or @filename"
    ),
    query_file: Optional[Path] = typer.Option(
        None, 
        "--query-file", 
        "-f", 
        help="File containing GraphQL query"
    ),
    variables: Optional[str] = typer.Option(
        None, 
        "--variables", 
        "-v", 
        help="GraphQL variables as JSON string or @filename"
    ),
    operation_name: Optional[str] = typer.Option(
        None, 
        "--operation", 
        "-o", 
        help="GraphQL operation name"
    ),
    headers: Optional[List[str]] = typer.Option(
        None, 
        "--header", 
        "-H", 
        help="Request headers in 'Key: Value' format"
    ),
    environment: str = typer.Option(
        "default", 
        "--env", 
        "-e", 
        help="Environment to use for variable substitution"
    ),
    save_response: Optional[Path] = typer.Option(
        None, 
        "--save", 
        "-s", 
        help="Save response to file"
    ),
    no_history: bool = typer.Option(
        False, 
        "--no-history", 
        help="Don't save request to history"
    ),
    max_retries: int = typer.Option(
        3, 
        "--retries", 
        help="Maximum number of retry attempts"
    )
) -> None:
    """Send a GraphQL request."""
    try:
        # Initialize components
        http_client = HTTPClient()
        graphql_client = GraphQLClient(http_client)
        history_manager = HistoryManager()
        formatter = ResponseFormatter(console)
        response_saver = ResponseSaver()
        
        # Parse headers
        header_dict = parse_headers(headers or [])
        
        # Handle query input
        graphql_query = None
        if query_file:
            graphql_query = query_file.read_text(encoding='utf-8')
        elif query:
            if query.startswith('@'):
                # Read from file
                file_path = Path(query[1:])
                graphql_query = file_path.read_text(encoding='utf-8')
            else:
                graphql_query = query
        else:
            console.print("[red]Error: GraphQL query is required (use --query or --query-file)[/red]")
            raise typer.Exit(1)
        
        # Handle variables
        variables_dict = None
        if variables:
            if variables.startswith('@'):
                # Read from file
                file_path = Path(variables[1:])
                variables_dict = json.loads(file_path.read_text(encoding='utf-8'))
            else:
                variables_dict = json.loads(variables)
        
        # Send GraphQL request
        with console.status(f"[bold green]Sending GraphQL request to {url}..."):
            response = graphql_client.send_query(
                url=url,
                query=graphql_query,
                variables=variables_dict,
                headers=header_dict,
                operation_name=operation_name,
                max_retries=max_retries
            )
        
        # Display response
        formatter.format_graphql_response(response)
        
        # Save response if requested
        if save_response:
            saved_files = response_saver.save_complete_response(
                response=response,
                directory=save_response.parent,
                base_name=save_response.stem
            )
            console.print(f"[green]Response saved to {saved_files['body']}[/green]")
        
        # Add to history (unless disabled)
        if not no_history:
            history_manager.add_request(
                method="POST",  # GraphQL is typically POST
                url=url,
                headers=header_dict,
                body=json.dumps({
                    'query': graphql_query,
                    'variables': variables_dict,
                    'operationName': operation_name
                }),
                response=response,
                environment=environment,
                tags=['graphql']
            )
        
    except GraphQLError as e:
        console.print(f"[red]GraphQL Error: {e}[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@request_app.command("template")
def execute_template(
    template_name: str = typer.Argument(..., help="Name of template to execute"),
    environment: str = typer.Option(
        "default", 
        "--env", 
        "-e", 
        help="Environment to use for variable substitution"
    ),
    override_method: Optional[str] = typer.Option(
        None, 
        "--method", 
        help="Override template HTTP method"
    ),
    override_url: Optional[str] = typer.Option(
        None, 
        "--url", 
        help="Override template URL"
    ),
    override_headers: Optional[List[str]] = typer.Option(
        None, 
        "--header", 
        "-H", 
        help="Override/add headers in 'Key: Value' format"
    ),
    override_body: Optional[str] = typer.Option(
        None, 
        "--body", 
        help="Override template body"
    ),
    override_params: Optional[List[str]] = typer.Option(
        None, 
        "--param", 
        "-p", 
        help="Override/add parameters in 'key=value' format"
    ),
    variables: Optional[List[str]] = typer.Option(
        None, 
        "--var", 
        "-v", 
        help="Custom variables in 'key=value' format"
    ),
    graphql: bool = typer.Option(
        False, 
        "--graphql", 
        help="Execute as GraphQL request"
    ),
    table_view: bool = typer.Option(
        False, 
        "--table", 
        "-t", 
        help="Display array responses in table format"
    ),
    save_response: Optional[Path] = typer.Option(
        None, 
        "--save", 
        "-s", 
        help="Save response to file"
    ),
    max_retries: int = typer.Option(
        3, 
        "--retries", 
        help="Maximum number of retry attempts"
    )
) -> None:
    """Execute a saved template."""
    try:
        # Initialize components
        template_executor = TemplateExecutor()
        formatter = ResponseFormatter(console)
        table_formatter = TableFormatter(console)
        response_saver = ResponseSaver()
        
        # Parse overrides
        override_header_dict = parse_headers(override_headers or [])
        override_param_dict = parse_params(override_params or [])
        
        # Parse custom variables
        custom_vars = {}
        for var in (variables or []):
            if '=' in var:
                key, value = var.split('=', 1)
                custom_vars[key.strip()] = value.strip()
        
        # Execute template
        with console.status(f"[bold green]Executing template '{template_name}'..."):
            response = template_executor.execute_template(
                template_name=template_name,
                environment=environment,
                custom_variables=custom_vars,
                method=override_method,
                url=override_url,
                headers=override_header_dict if override_header_dict else None,
                body=override_body,
                params=override_param_dict if override_param_dict else None,
                max_retries=max_retries,
                is_graphql=graphql
            )
        
        # Display response
        if graphql:
            formatter.format_graphql_response(response)
        elif table_view and hasattr(response, 'text') and response.text:
            try:
                data = json.loads(response.text)
                if table_formatter.detect_table_structure(data):
                    table_formatter.display_table(data, f"Template: {template_name}")
                else:
                    formatter.format_http_response(response)
            except json.JSONDecodeError:
                formatter.format_http_response(response)
        else:
            formatter.format_http_response(response)
        
        # Save response if requested
        if save_response:
            saved_files = response_saver.save_complete_response(
                response=response,
                directory=save_response.parent,
                base_name=save_response.stem
            )
            console.print(f"[green]Response saved to {saved_files['body']}[/green]")
        
    except TemplateExecutionError as e:
        console.print(f"[red]Template Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@request_app.command("batch")
def execute_batch_requests(
    config_file: Path = typer.Argument(..., help="JSON file containing batch request configuration"),
    environment: str = typer.Option(
        "default", 
        "--env", 
        "-e", 
        help="Environment to use for variable substitution"
    ),
    stop_on_error: bool = typer.Option(
        False, 
        "--stop-on-error", 
        help="Stop execution on first error"
    ),
    save_responses: Optional[Path] = typer.Option(
        None, 
        "--save-dir", 
        help="Directory to save all responses"
    ),
    summary_only: bool = typer.Option(
        False, 
        "--summary", 
        help="Show only summary, not individual responses"
    )
) -> None:
    """Execute multiple requests from a configuration file."""
    try:
        # Load batch configuration
        if not config_file.exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            raise typer.Exit(1)
        
        batch_config = json.loads(config_file.read_text(encoding='utf-8'))
        
        # Initialize components
        template_executor = TemplateExecutor()
        formatter = ResponseFormatter(console)
        response_saver = ResponseSaver()
        
        # Execute batch
        with console.status("[bold green]Executing batch requests..."):
            results = template_executor.execute_template_batch(
                template_configs=batch_config.get('requests', []),
                environment=environment,
                stop_on_error=stop_on_error
            )
        
        # Display results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        if not summary_only:
            for result in results:
                if result['success']:
                    console.print(f"[green]✓[/green] {result['template_name']} - {result['response'].status_code}")
                    if not summary_only:
                        formatter.format_http_response(result['response'], show_headers=False, show_body=False)
                else:
                    console.print(f"[red]✗[/red] {result['template_name']} - {result['error']}")
        
        # Show summary
        formatter.format_summary(
            total_requests=len(results),
            successful=successful,
            failed=failed,
            total_time=sum(r['execution_time'] for r in results)
        )
        
        # Save responses if requested
        if save_responses:
            save_responses.mkdir(parents=True, exist_ok=True)
            for i, result in enumerate(results):
                if result['success'] and result['response']:
                    filename = f"{result['template_name']}_{i+1:03d}"
                    response_saver.save_complete_response(
                        response=result['response'],
                        directory=save_responses,
                        base_name=filename
                    )
            console.print(f"[green]Responses saved to {save_responses}[/green]")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in configuration file: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
"""History management commands for the CLI."""

import typer
import json
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.history_manager import HistoryManager, HistoryManagerError
from ..core.history_query import HistoryQuery
from ..formatters.response_formatter import ResponseFormatter
from ..formatters.response_saver import ResponseSaver

# Create console for output
console = Console()

# Create history app
history_app = typer.Typer(
    name="history",
    help="View and manage request history",
    rich_markup_mode="rich"
)


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        
        # If within last 24 hours, show relative time
        if now - dt < timedelta(days=1):
            diff = now - dt
            if diff.total_seconds() < 60:
                return "just now"
            elif diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes}m ago"
            else:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours}h ago"
        else:
            return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return timestamp[:16]  # Fallback to truncated string


@history_app.command("list")
def list_history(
    limit: int = typer.Option(
        20,
        "--limit",
        "-l",
        help="Maximum number of entries to show"
    ),
    method: Optional[str] = typer.Option(
        None,
        "--method",
        "-m",
        help="Filter by HTTP method"
    ),
    status: Optional[int] = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by response status code"
    ),
    url_pattern: Optional[str] = typer.Option(
        None,
        "--url",
        "-u",
        help="Filter by URL pattern (substring match)"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Filter by environment"
    ),
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter by tags"
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Show entries since date/time (e.g., '2024-01-01', '1h', '30m')"
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Show detailed information"
    ),
    success_only: bool = typer.Option(
        False,
        "--success-only",
        help="Show only successful requests (2xx status codes)"
    ),
    errors_only: bool = typer.Option(
        False,
        "--errors-only",
        help="Show only failed requests (4xx, 5xx status codes)"
    )
) -> None:
    """List request history with optional filtering."""
    try:
        history_manager = HistoryManager()
        
        # Parse since parameter
        since_datetime = None
        if since:
            try:
                # Try parsing as relative time (e.g., '1h', '30m', '2d')
                if since.endswith('m'):
                    minutes = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(minutes=minutes)
                elif since.endswith('h'):
                    hours = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(hours=hours)
                elif since.endswith('d'):
                    days = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(days=days)
                else:
                    # Try parsing as absolute date/time
                    since_datetime = datetime.fromisoformat(since)
            except ValueError:
                console.print(f"[red]Invalid date format: {since}[/red]")
                raise typer.Exit(1)
        
        # Build query
        query = HistoryQuery()
        
        if method:
            query = query.filter_by_method(method.upper())
        
        if status:
            query = query.filter_by_status_code(status)
        
        if url_pattern:
            query = query.filter_by_url_pattern(url_pattern)
        
        if environment:
            query = query.filter_by_environment(environment)
        
        if tags:
            query = query.filter_by_tags(tags)
        
        if since_datetime:
            query = query.filter_by_date_range(since_datetime)
        
        if success_only:
            query = query.filter_by_status_range(200, 299)
        elif errors_only:
            query = query.filter_by_status_range(400, 599)
        
        query = query.limit(limit).order_by_date(descending=True)
        
        # Execute query
        entries = history_manager.query_history(query)
        
        if not entries:
            console.print("[yellow]No history entries found matching the criteria[/yellow]")
            return
        
        if detailed:
            # Show detailed view
            for i, entry in enumerate(entries):
                if i > 0:
                    console.print()  # Add spacing between entries
                
                # Create panel for each entry
                status_color = "green" if 200 <= entry.get('response_status', 0) < 300 else "red"
                title = f"{entry.get('method', 'UNKNOWN')} {entry.get('url', 'Unknown URL')}"
                
                content_lines = [
                    f"[bold]Status:[/bold] [{status_color}]{entry.get('response_status', 'Unknown')}[/{status_color}]",
                    f"[bold]Time:[/bold] {format_timestamp(entry.get('timestamp', ''))}",
                    f"[bold]Duration:[/bold] {entry.get('response_time', 0):.3f}s"
                ]
                
                if entry.get('environment'):
                    content_lines.append(f"[bold]Environment:[/bold] {entry['environment']}")
                
                if entry.get('tags'):
                    content_lines.append(f"[bold]Tags:[/bold] {', '.join(entry['tags'])}")
                
                if entry.get('request_headers'):
                    content_lines.append(f"[bold]Headers:[/bold] {len(entry['request_headers'])} headers")
                
                if entry.get('request_body'):
                    body_preview = entry['request_body'][:100]
                    if len(entry['request_body']) > 100:
                        body_preview += "..."
                    content_lines.append(f"[bold]Body:[/bold] {body_preview}")
                
                panel = Panel(
                    "\
".join(content_lines),
                    title=title,
                    border_style="blue"
                )
                console.print(panel)
        else:
            # Show table view
            table = Table(title=f"Request History ({len(entries)} entries)", 
                         show_header=True, header_style="bold blue")
            table.add_column("#", style="dim", width=4)
            table.add_column("Method", style="cyan", width=8)
            table.add_column("URL", style="blue")
            table.add_column("Status", style="white", width=8)
            table.add_column("Time", style="green", width=12)
            table.add_column("Duration", style="yellow", width=10)
            
            for i, entry in enumerate(entries, 1):
                # Truncate long URLs
                url = entry.get('url', 'Unknown')
                if len(url) > 60:
                    url = url[:57] + "..."
                
                # Color status code
                status = entry.get('response_status', 'Unknown')
                status_color = "green" if isinstance(status, int) and 200 <= status < 300 else "red"
                status_str = f"[{status_color}]{status}[/{status_color}]"
                
                # Format duration
                duration = entry.get('response_time', 0)
                duration_str = f"{duration:.3f}s" if isinstance(duration, (int, float)) else "Unknown"
                
                table.add_row(
                    str(i),
                    entry.get('method', 'UNKNOWN'),
                    url,
                    status_str,
                    format_timestamp(entry.get('timestamp', '')),
                    duration_str
                )
            
            console.print(table)
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@history_app.command("show")
def show_history_entry(
    entry_id: str = typer.Argument(..., help="History entry ID"),
    show_request: bool = typer.Option(
        True,
        "--request/--no-request",
        help="Show request details"
    ),
    show_response: bool = typer.Option(
        True,
        "--response/--no-response",
        help="Show response details"
    ),
    show_headers: bool = typer.Option(
        True,
        "--headers/--no-headers",
        help="Show request/response headers"
    ),
    show_body: bool = typer.Option(
        True,
        "--body/--no-body",
        help="Show request/response body"
    )
) -> None:
    """Show detailed information for a specific history entry."""
    try:
        history_manager = HistoryManager()
        
        # Get history entry
        entry = history_manager.get_history_entry(entry_id)
        
        if not entry:
            console.print(f"[red]History entry '{entry_id}' not found[/red]")
            raise typer.Exit(1)
        
        formatter = ResponseFormatter(console)
        
        # Show request details
        if show_request:
            console.print("[bold blue]Request Details:[/bold blue]")
            console.print(f"Method: {entry.get('method', 'Unknown')}")
            console.print(f"URL: {entry.get('url', 'Unknown')}")
            console.print(f"Timestamp: {entry.get('timestamp', 'Unknown')}")
            
            if entry.get('environment'):
                console.print(f"Environment: {entry['environment']}")
            
            if entry.get('tags'):
                console.print(f"Tags: {', '.join(entry['tags'])}")
            
            if show_headers and entry.get('request_headers'):
                console.print("\
[bold]Request Headers:[/bold]")
                for key, value in entry['request_headers'].items():
                    console.print(f"  {key}: {value}")
            
            if show_body and entry.get('request_body'):
                console.print("\
[bold]Request Body:[/bold]")
                try:
                    # Try to format as JSON
                    body_data = json.loads(entry['request_body'])
                    formatted_body = json.dumps(body_data, indent=2)
                    console.print(formatted_body)
                except json.JSONDecodeError:
                    console.print(entry['request_body'])
            
            console.print()
        
        # Show response details
        if show_response:
            console.print("[bold blue]Response Details:[/bold blue]")
            
            # Create mock response object for formatter
            class HistoryResponse:
                def __init__(self, entry):
                    self.status_code = entry.get('response_status', 0)
                    self.headers = entry.get('response_headers', {})
                    self.text = entry.get('response_body', '')
                    self.url = entry.get('url', '')
                    self.request_time = entry.get('response_time', 0.0)
                    self.from_cache = False
                    self.from_history = True
            
            response = HistoryResponse(entry)
            formatter.format_http_response(
                response, 
                show_headers=show_headers, 
                show_body=show_body
            )
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@history_app.command("retry")
def retry_request(
    entry_id: str = typer.Argument(..., help="History entry ID to retry"),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment to use for variable substitution (default: original)"
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
        help="Don't save retry to history"
    )
) -> None:
    """Retry a request from history."""
    try:
        history_manager = HistoryManager()
        
        # Get history entry
        entry = history_manager.get_history_entry(entry_id)
        
        if not entry:
            console.print(f"[red]History entry '{entry_id}' not found[/red]")
            raise typer.Exit(1)
        
        # Use original environment if not specified
        if not environment:
            environment = entry.get('environment', 'default')
        
        console.print(f"[cyan]Retrying request: {entry.get('method', 'UNKNOWN')} {entry.get('url', 'Unknown')}[/cyan]")
        
        # Retry the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Sending request...", total=None)
            
            response = history_manager.retry_request(
                entry_id=entry_id,
                environment=environment,
                save_to_history=not no_history
            )
        
        # Display response
        formatter = ResponseFormatter(console)
        formatter.format_http_response(response)
        
        # Save response if requested
        if save_response:
            response_saver = ResponseSaver()
            saved_files = response_saver.save_complete_response(
                response=response,
                directory=save_response.parent,
                base_name=save_response.stem
            )
            console.print(f"[green]Response saved to {saved_files['body']}[/green]")
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@history_app.command("delete")
def delete_history_entries(
    entry_ids: Optional[List[str]] = typer.Argument(
        None,
        help="Specific entry IDs to delete"
    ),
    all_entries: bool = typer.Option(
        False,
        "--all",
        help="Delete all history entries"
    ),
    older_than: Optional[str] = typer.Option(
        None,
        "--older-than",
        help="Delete entries older than specified time (e.g., '7d', '1h', '30m')"
    ),
    method: Optional[str] = typer.Option(
        None,
        "--method",
        "-m",
        help="Delete entries with specific HTTP method"
    ),
    status_range: Optional[str] = typer.Option(
        None,
        "--status-range",
        help="Delete entries with status codes in range (e.g., '400-499')"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
) -> None:
    """Delete history entries."""
    try:
        history_manager = HistoryManager()
        
        if not any([entry_ids, all_entries, older_than, method, status_range]):
            console.print("[red]Must specify entries to delete (entry IDs, --all, --older-than, etc.)[/red]")
            raise typer.Exit(1)
        
        if entry_ids:
            # Delete specific entries
            if not force:
                confirm = typer.confirm(f"Delete {len(entry_ids)} history entries?")
                if not confirm:
                    console.print("Deletion cancelled")
                    return
            
            deleted_count = 0
            for entry_id in entry_ids:
                if history_manager.delete_history_entry(entry_id):
                    deleted_count += 1
                else:
                    console.print(f"[yellow]Warning: Entry '{entry_id}' not found[/yellow]")
            
            console.print(f"[green]✓[/green] Deleted {deleted_count} history entries")
        
        elif all_entries:
            # Delete all entries
            total_count = history_manager.get_history_count()
            
            if total_count == 0:
                console.print("[yellow]No history entries to delete[/yellow]")
                return
            
            if not force:
                confirm = typer.confirm(f"Delete ALL {total_count} history entries? This cannot be undone.")
                if not confirm:
                    console.print("Deletion cancelled")
                    return
            
            deleted_count = history_manager.clear_history()
            console.print(f"[green]✓[/green] Deleted {deleted_count} history entries")
        
        else:
            # Delete with filters
            query = HistoryQuery()
            
            if older_than:
                # Parse older_than parameter
                try:
                    if older_than.endswith('m'):
                        minutes = int(older_than[:-1])
                        cutoff_date = datetime.now() - timedelta(minutes=minutes)
                    elif older_than.endswith('h'):
                        hours = int(older_than[:-1])
                        cutoff_date = datetime.now() - timedelta(hours=hours)
                    elif older_than.endswith('d'):
                        days = int(older_than[:-1])
                        cutoff_date = datetime.now() - timedelta(days=days)
                    else:
                        cutoff_date = datetime.fromisoformat(older_than)
                    
                    query = query.filter_by_date_range(end_date=cutoff_date)
                except ValueError:
                    console.print(f"[red]Invalid date format: {older_than}[/red]")
                    raise typer.Exit(1)
            
            if method:
                query = query.filter_by_method(method.upper())
            
            if status_range:
                try:
                    if '-' in status_range:
                        start_status, end_status = map(int, status_range.split('-'))
                        query = query.filter_by_status_range(start_status, end_status)
                    else:
                        status_code = int(status_range)
                        query = query.filter_by_status_code(status_code)
                except ValueError:
                    console.print(f"[red]Invalid status range format: {status_range}[/red]")
                    raise typer.Exit(1)
            
            # Get matching entries
            matching_entries = history_manager.query_history(query)
            
            if not matching_entries:
                console.print("[yellow]No history entries match the specified criteria[/yellow]")
                return
            
            if not force:
                confirm = typer.confirm(f"Delete {len(matching_entries)} matching history entries?")
                if not confirm:
                    console.print("Deletion cancelled")
                    return
            
            # Delete matching entries
            deleted_count = 0
            for entry in matching_entries:
                if history_manager.delete_history_entry(entry.get('id')):
                    deleted_count += 1
            
            console.print(f"[green]✓[/green] Deleted {deleted_count} history entries")
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@history_app.command("export")
def export_history(
    output_file: Path = typer.Argument(..., help="Output file path"),
    format_type: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Export format (json, csv, yaml)"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum number of entries to export"
    ),
    method: Optional[str] = typer.Option(
        None,
        "--method",
        "-m",
        help="Filter by HTTP method"
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Export entries since date/time"
    ),
    include_bodies: bool = typer.Option(
        True,
        "--bodies/--no-bodies",
        help="Include request/response bodies"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing file"
    )
) -> None:
    """Export history to file."""
    try:
        history_manager = HistoryManager()
        
        # Build query
        query = HistoryQuery()
        
        if method:
            query = query.filter_by_method(method.upper())
        
        if since:
            try:
                if since.endswith('m'):
                    minutes = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(minutes=minutes)
                elif since.endswith('h'):
                    hours = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(hours=hours)
                elif since.endswith('d'):
                    days = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(days=days)
                else:
                    since_datetime = datetime.fromisoformat(since)
                
                query = query.filter_by_date_range(since_datetime)
            except ValueError:
                console.print(f"[red]Invalid date format: {since}[/red]")
                raise typer.Exit(1)
        
        if limit:
            query = query.limit(limit)
        
        query = query.order_by_date(descending=True)
        
        # Export history
        saved_path = history_manager.export_history_to_file(
            file_path=output_file,
            query=query,
            format_type=format_type,
            include_bodies=include_bodies,
            overwrite=overwrite
        )
        
        # Get count of exported entries
        entries = history_manager.query_history(query)
        entry_count = len(entries)
        
        console.print(f"[green]✓[/green] Exported {entry_count} history entries to [bold]{saved_path}[/bold]")
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@history_app.command("stats")
def show_history_stats(
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Show detailed statistics"
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Show stats since date/time"
    )
) -> None:
    """Show history statistics."""
    try:
        history_manager = HistoryManager()
        
        # Build query for time filtering
        query = HistoryQuery()
        
        if since:
            try:
                if since.endswith('m'):
                    minutes = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(minutes=minutes)
                elif since.endswith('h'):
                    hours = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(hours=hours)
                elif since.endswith('d'):
                    days = int(since[:-1])
                    since_datetime = datetime.now() - timedelta(days=days)
                else:
                    since_datetime = datetime.fromisoformat(since)
                
                query = query.filter_by_date_range(since_datetime)
            except ValueError:
                console.print(f"[red]Invalid date format: {since}[/red]")
                raise typer.Exit(1)
        
        # Get statistics
        stats = history_manager.get_history_statistics(query)
        
        # Display basic stats
        console.print("[bold blue]History Statistics[/bold blue]")
        console.print(f"Total Requests: {stats['total_requests']}")
        console.print(f"Successful (2xx): {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
        console.print(f"Client Errors (4xx): {stats['client_errors']}")
        console.print(f"Server Errors (5xx): {stats['server_errors']}")
        console.print(f"Average Response Time: {stats['avg_response_time']:.3f}s")
        
        if detailed:
            console.print("\
[bold]Method Distribution:[/bold]")
            for method, count in stats['methods'].items():
                percentage = (count / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
                console.print(f"  {method}: {count} ({percentage:.1f}%)")
            
            console.print("\
[bold]Status Code Distribution:[/bold]")
            for status, count in sorted(stats['status_codes'].items()):
                percentage = (count / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
                console.print(f"  {status}: {count} ({percentage:.1f}%)")
            
            if stats['environments']:
                console.print("\
[bold]Environment Usage:[/bold]")
                for env, count in stats['environments'].items():
                    percentage = (count / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
                    console.print(f"  {env}: {count} ({percentage:.1f}%)")
            
            if stats['top_domains']:
                console.print("\
[bold]Top Domains:[/bold]")
                for domain, count in stats['top_domains']:
                    percentage = (count / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
                    console.print(f"  {domain}: {count} ({percentage:.1f}%)")
        
    except HistoryManagerError as e:
        console.print(f"[red]History Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
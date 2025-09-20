"""Response formatter with Rich integration for beautiful terminal output."""

import json
import xml.dom.minidom
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import re
import logging

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status

from ..config.settings import get_config
from ..core.http_client import HTTPResponse
from ..core.graphql_client import GraphQLResponse


logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats API responses with color-coded status and pretty-printing."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config = get_config()
    
    def get_status_color(self, status_code: int) -> str:
        """
        Get color for HTTP status code based on requirements.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            Rich color name
        """
        if 200 <= status_code < 300:
            return "green"  # 2xx → green
        elif 300 <= status_code < 400:
            return "cyan"   # 3xx → cyan
        elif 400 <= status_code < 500:
            return "yellow" # 4xx → yellow
        elif 500 <= status_code < 600:
            return "red"    # 5xx → red
        else:
            return "white"  # Unknown
    
    def get_status_emoji(self, status_code: int) -> str:
        """Get emoji for status code."""
        if 200 <= status_code < 300:
            return "✅"
        elif 300 <= status_code < 400:
            return "🔄"
        elif 400 <= status_code < 500:
            return "⚠️"
        elif 500 <= status_code < 600:
            return "❌"
        else:
            return "❓"
    
    def colorize_status(self, status_code: int) -> Text:
        """
        Create colorized status code text.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            Rich Text object with colored status
        """
        color = self.get_status_color(status_code)
        emoji = self.get_status_emoji(status_code)
        
        # Get status message
        status_messages = {
            200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
            301: "Moved Permanently", 302: "Found", 304: "Not Modified",
            400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
            405: "Method Not Allowed", 409: "Conflict", 422: "Unprocessable Entity",
            500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable"
        }
        
        status_message = status_messages.get(status_code, "Unknown")
        
        return Text(f"{emoji} {status_code} {status_message}", style=f"bold {color}")
    
    def format_headers(self, headers: Dict[str, str]) -> Table:
        """
        Format headers as a Rich table.
        
        Args:
            headers: Headers dictionary
            
        Returns:
            Rich Table with formatted headers
        """
        table = Table(title="Headers", show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        for name, value in sorted(headers.items()):
            # Truncate very long header values
            if len(value) > 100:
                display_value = value[:97] + "..."
            else:
                display_value = value
            
            table.add_row(name, display_value)
        
        return table
    
    def pretty_print_json(self, json_data: Union[str, Dict, List], title: str = "Response Body") -> Syntax:
        """
        Pretty-print JSON with syntax highlighting.
        
        Args:
            json_data: JSON data (string or parsed object)
            title: Title for the syntax block
            
        Returns:
            Rich Syntax object with highlighted JSON
        """
        try:
            if isinstance(json_data, str):
                # Parse and re-format for consistent indentation
                parsed = json.loads(json_data)
                formatted = json.dumps(parsed, indent=self.config.output.json_indent, ensure_ascii=False)
            else:
                formatted = json.dumps(json_data, indent=self.config.output.json_indent, ensure_ascii=False)
            
            return Syntax(
                formatted,
                "json",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
                background_color="default"
            )
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON: {e}")
            # Return as plain text if JSON parsing fails
            content = str(json_data)
            return Syntax(content, "text", theme="monokai", background_color="default")
    
    def pretty_print_xml(self, xml_data: str, title: str = "Response Body") -> Syntax:
        """
        Pretty-print XML with syntax highlighting.
        
        Args:
            xml_data: XML data string
            title: Title for the syntax block
            
        Returns:
            Rich Syntax object with highlighted XML
        """
        try:
            # Parse and pretty-print XML
            dom = xml.dom.minidom.parseString(xml_data)
            formatted = dom.toprettyxml(indent="  ", encoding=None)
            
            # Remove extra blank lines
            lines = [line for line in formatted.split('\n') if line.strip()]
            formatted = '\n'.join(lines)
            
            return Syntax(
                formatted,
                "xml",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
                background_color="default"
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse XML: {e}")
            # Return as plain text if XML parsing fails
            return Syntax(xml_data, "xml", theme="monokai", background_color="default")
    
    def pretty_print_html(self, html_data: str, title: str = "Response Body") -> Syntax:
        """
        Pretty-print HTML with syntax highlighting.
        
        Args:
            html_data: HTML data string
            title: Title for the syntax block
            
        Returns:
            Rich Syntax object with highlighted HTML
        """
        try:
            # Basic HTML formatting (for more advanced formatting, consider using BeautifulSoup)
            formatted = self._format_html_basic(html_data)
            
            return Syntax(
                formatted,
                "html",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
                background_color="default"
            )
            
        except Exception as e:
            logger.warning(f"Failed to format HTML: {e}")
            return Syntax(html_data, "html", theme="monokai", background_color="default")
    
    def _format_html_basic(self, html: str) -> str:
        """Basic HTML formatting for better readability."""
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html.strip())
        
        # Add newlines after certain tags
        html = re.sub(r'(<(?:div|p|h[1-6]|section|article|header|footer|nav|main)[^>]*>)', r'\n\1', html)
        html = re.sub(r'(</(?:div|p|h[1-6]|section|article|header|footer|nav|main)>)', r'\1\n', html)
        html = re.sub(r'(<br[^>]*>)', r'\1\n', html)
        
        # Basic indentation
        lines = html.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Decrease indent for closing tags
            if line.startswith('</'):
                indent_level = max(0, indent_level - 1)
            
            formatted_lines.append('  ' * indent_level + line)
            
            # Increase indent for opening tags (but not self-closing)
            if line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def detect_content_type(self, content: str, headers: Dict[str, str]) -> str:
        """
        Detect content type from headers or content.
        
        Args:
            content: Response content
            headers: Response headers
            
        Returns:
            Detected content type
        """
        # Check Content-Type header first
        content_type = headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type or 'text/json' in content_type:
            return 'json'
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            return 'xml'
        elif 'text/html' in content_type:
            return 'html'
        elif 'text/plain' in content_type:
            return 'text'
        
        # Try to detect from content
        content_stripped = content.strip()
        
        if content_stripped.startswith(('{', '[')):
            try:
                json.loads(content)
                return 'json'
            except json.JSONDecodeError:
                pass
        
        if content_stripped.startswith('<'):
            if content_stripped.lower().startswith('<!doctype html') or '<html' in content_stripped.lower():
                return 'html'
            else:
                return 'xml'
        
        return 'text'
    
    def format_response_body(self, content: str, headers: Dict[str, str]) -> Union[Syntax, Text]:
        """
        Format response body based on content type.
        
        Args:
            content: Response content
            headers: Response headers
            
        Returns:
            Formatted content as Rich object
        """
        if not content.strip():
            return Text("(empty response)", style="dim")
        
        content_type = self.detect_content_type(content, headers)
        
        if content_type == 'json':
            return self.pretty_print_json(content)
        elif content_type == 'xml':
            return self.pretty_print_xml(content)
        elif content_type == 'html':
            return self.pretty_print_html(content)
        else:
            # Plain text
            return Syntax(content, "text", theme="monokai", background_color="default")
    
    def format_timing_info(self, request_time: float, from_cache: bool = False) -> Text:
        """
        Format timing information.
        
        Args:
            request_time: Request execution time in seconds
            from_cache: Whether response came from cache
            
        Returns:
            Formatted timing text
        """
        if from_cache:
            return Text(f"⚡ {request_time:.3f}s (cached)", style="dim cyan")
        else:
            if request_time < 0.1:
                style = "green"
            elif request_time < 1.0:
                style = "yellow"
            else:
                style = "red"
            
            return Text(f"⏱️  {request_time:.3f}s", style=style)
    
    def format_http_response(self, response: HTTPResponse, show_headers: bool = True,
                           show_body: bool = True, show_timing: bool = True) -> None:
        """
        Format and display HTTP response.
        
        Args:
            response: HTTP response object
            show_headers: Whether to show headers
            show_body: Whether to show response body
            show_timing: Whether to show timing information
        """
        # Status line
        status_text = self.colorize_status(response.status_code)
        
        # Create main panel content
        content_parts = []
        
        # Add URL and timing info
        url_text = Text(f"🌐 {response.url}", style="blue")
        content_parts.append(url_text)
        
        if show_timing:
            timing_text = self.format_timing_info(response.request_time, response.from_cache)
            content_parts.append(timing_text)
        
        # Add status
        content_parts.append(status_text)
        
        # Create status panel
        status_panel = Panel(
            "\n".join(str(part) for part in content_parts),
            title="Response",
            border_style="blue"
        )
        
        self.console.print(status_panel)
        
        # Show headers if requested
        if show_headers and response.headers:
            headers_table = self.format_headers(response.headers)
            self.console.print(headers_table)
            self.console.print()
        
        # Show body if requested and present
        if show_body and response.text:
            body_content = self.format_response_body(response.text, response.headers)
            
            body_panel = Panel(
                body_content,
                title="Response Body",
                border_style="green"
            )
            
            self.console.print(body_panel)
    
    def format_graphql_response(self, response: GraphQLResponse, show_headers: bool = True,
                              show_timing: bool = True) -> None:
        """
        Format and display GraphQL response.
        
        Args:
            response: GraphQL response object
            show_headers: Whether to show headers
            show_timing: Whether to show timing information
        """
        # Status line
        status_text = self.colorize_status(response.status_code)
        
        # Create main panel content
        content_parts = []
        
        # Add timing info
        if show_timing:
            timing_text = self.format_timing_info(response.request_time, response.from_cache)
            content_parts.append(timing_text)
        
        # Add status
        content_parts.append(status_text)
        
        # GraphQL-specific status
        if response.has_errors():
            error_text = Text("❌ GraphQL Errors", style="bold red")
            content_parts.append(error_text)
        elif response.data is not None:
            success_text = Text("✅ GraphQL Success", style="bold green")
            content_parts.append(success_text)
        
        # Create status panel
        status_panel = Panel(
            "\n".join(str(part) for part in content_parts),
            title="GraphQL Response",
            border_style="blue"
        )
        
        self.console.print(status_panel)
        
        # Show headers if requested
        if show_headers and response.headers:
            headers_table = self.format_headers(response.headers)
            self.console.print(headers_table)
            self.console.print()
        
        # Show GraphQL errors if present
        if response.has_errors():
            error_messages = response.get_error_messages()
            
            error_table = Table(title="GraphQL Errors", show_header=True, header_style="bold red")
            error_table.add_column("Error", style="red")
            
            for message in error_messages:
                error_table.add_row(message)
            
            self.console.print(error_table)
            self.console.print()
        
        # Show data if present
        if response.data is not None:
            data_content = self.pretty_print_json(response.data, "GraphQL Data")
            
            data_panel = Panel(
                data_content,
                title="GraphQL Data",
                border_style="green"
            )
            
            self.console.print(data_panel)
        
        # Show extensions if present
        if response.extensions:
            extensions_content = self.pretty_print_json(response.extensions, "GraphQL Extensions")
            
            extensions_panel = Panel(
                extensions_content,
                title="GraphQL Extensions",
                border_style="yellow"
            )
            
            self.console.print(extensions_panel)
    
    def format_error(self, error: Exception, request_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Format and display error information.
        
        Args:
            error: Exception that occurred
            request_info: Optional request information for context
        """
        error_text = Text(f"❌ {type(error).__name__}: {str(error)}", style="bold red")
        
        content_parts = [error_text]
        
        # Add request context if available
        if request_info:
            method = request_info.get('method', 'UNKNOWN')
            url = request_info.get('url', 'unknown')
            context_text = Text(f"🌐 {method} {url}", style="dim blue")
            content_parts.insert(0, context_text)
        
        error_panel = Panel(
            "\n".join(str(part) for part in content_parts),
            title="Error",
            border_style="red"
        )
        
        self.console.print(error_panel)
    
    def show_progress(self, description: str = "Processing...") -> Status:
        """
        Show progress indicator.
        
        Args:
            description: Progress description
            
        Returns:
            Rich Status object for context management
        """
        return Status(description, console=self.console, spinner="dots")
    
    def format_summary(self, total_requests: int, successful: int, failed: int, 
                      total_time: float) -> None:
        """
        Format and display summary statistics.
        
        Args:
            total_requests: Total number of requests
            successful: Number of successful requests
            failed: Number of failed requests
            total_time: Total execution time
        """
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
        
        summary_table = Table(title="Summary", show_header=True, header_style="bold blue")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Total Requests", str(total_requests))
        summary_table.add_row("Successful", f"{successful} ({success_rate:.1f}%)")
        summary_table.add_row("Failed", str(failed))
        summary_table.add_row("Total Time", f"{total_time:.3f}s")
        
        if total_requests > 0:
            avg_time = total_time / total_requests
            summary_table.add_row("Average Time", f"{avg_time:.3f}s")
        
        self.console.print(summary_table)
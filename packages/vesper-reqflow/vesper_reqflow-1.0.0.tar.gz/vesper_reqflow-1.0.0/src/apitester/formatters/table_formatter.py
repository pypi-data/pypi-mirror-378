"""Table formatter for displaying array responses in tabular format."""

import json
from typing import Any, Dict, List, Optional, Union, Set, Tuple
import logging

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns

from ..config.settings import get_config


logger = logging.getLogger(__name__)


class TableFormatter:
    """Formats array data as Rich tables with auto-detection and pagination."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config = get_config()
        self.max_width = self.config.output.table_max_width
        self.max_cell_length = 100
        self.max_rows_per_page = 50
    
    def detect_table_structure(self, data: Any) -> bool:
        """
        Detect if data can be displayed as a table.
        
        Args:
            data: Data to analyze
            
        Returns:
            True if data is suitable for table display
        """
        if not isinstance(data, list):
            return False
        
        if len(data) == 0:
            return False
        
        # Check if all items are dictionaries with similar structure
        if not all(isinstance(item, dict) for item in data):
            return False
        
        # Check if there's at least some consistency in keys
        if len(data) == 1:
            return True
        
        # Get keys from first few items to check consistency
        sample_size = min(5, len(data))
        key_sets = [set(item.keys()) for item in data[:sample_size]]
        
        # Calculate key overlap
        common_keys = set.intersection(*key_sets) if key_sets else set()
        all_keys = set.union(*key_sets) if key_sets else set()
        
        # If at least 50% of keys are common, consider it table-worthy
        if len(all_keys) == 0:
            return False
        
        overlap_ratio = len(common_keys) / len(all_keys)
        return overlap_ratio >= 0.5
    
    def extract_columns(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Extract column names from array of dictionaries.
        
        Args:
            data: Array of dictionaries
            
        Returns:
            List of column names in optimal order
        """
        if not data:
            return []
        
        # Count frequency of each key
        key_counts = {}
        for item in data:
            for key in item.keys():
                key_counts[key] = key_counts.get(key, 0) + 1
        
        # Sort keys by frequency (most common first) and then alphabetically
        sorted_keys = sorted(key_counts.keys(), key=lambda k: (-key_counts[k], k))
        
        # Prioritize common identifier fields
        priority_keys = ['id', 'name', 'title', 'email', 'username', 'type', 'status']
        
        # Reorder to put priority keys first
        final_keys = []
        for priority_key in priority_keys:
            if priority_key in sorted_keys:
                final_keys.append(priority_key)
                sorted_keys.remove(priority_key)
        
        # Add remaining keys
        final_keys.extend(sorted_keys)
        
        return final_keys
    
    def format_cell_value(self, value: Any) -> str:
        """
        Format a cell value for display in table.
        
        Args:
            value: Cell value
            
        Returns:
            Formatted string representation
        """
        if value is None:
            return ""
        
        if isinstance(value, bool):
            return "✅" if value else "❌"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            # Truncate long strings
            if len(value) > self.max_cell_length:
                return value[:self.max_cell_length - 3] + "..."
            return value
        
        if isinstance(value, (list, dict)):
            # Convert complex types to JSON
            try:
                json_str = json.dumps(value, separators=(',', ':'))
                if len(json_str) > self.max_cell_length:
                    return json_str[:self.max_cell_length - 3] + "..."
                return json_str
            except (TypeError, ValueError):
                return str(value)
        
        return str(value)
    
    def get_column_style(self, column_name: str, values: List[Any]) -> str:
        """
        Determine appropriate style for column based on its content.
        
        Args:
            column_name: Name of the column
            values: List of values in the column
            
        Returns:
            Rich style string
        """
        # Style based on column name
        name_lower = column_name.lower()
        
        if name_lower in ['id', 'uuid', 'guid']:
            return "dim cyan"
        elif name_lower in ['name', 'title', 'username']:
            return "bold white"
        elif name_lower in ['email', 'url', 'link']:
            return "blue"
        elif name_lower in ['status', 'state']:
            return "yellow"
        elif name_lower in ['created_at', 'updated_at', 'date', 'time']:
            return "green"
        elif name_lower in ['count', 'total', 'amount', 'price', 'value']:
            return "magenta"
        
        # Style based on content type
        if values:
            sample_values = [v for v in values[:10] if v is not None]
            
            if sample_values:
                if all(isinstance(v, bool) for v in sample_values):
                    return "cyan"
                elif all(isinstance(v, (int, float)) for v in sample_values):
                    return "magenta"
                elif all(isinstance(v, str) and v.startswith(('http://', 'https://')) for v in sample_values):
                    return "blue underline"
        
        return "white"
    
    def create_rich_table(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Table:
        """
        Create Rich table from array of dictionaries.
        
        Args:
            data: Array of dictionaries
            title: Optional table title
            
        Returns:
            Rich Table object
        """
        if not data:
            table = Table(title=title or "Empty Result")
            table.add_column("Message", style="dim")
            table.add_row("No data to display")
            return table
        
        # Extract columns
        columns = self.extract_columns(data)
        
        if not columns:
            table = Table(title=title or "Invalid Data")
            table.add_column("Message", style="dim")
            table.add_row("No valid columns found")
            return table
        
        # Create table
        table = Table(
            title=title or f"Results ({len(data)} rows)",
            show_header=True,
            header_style="bold blue",
            show_lines=False,
            expand=False
        )
        
        # Add columns with appropriate styles
        for column in columns:
            # Get values for this column to determine style
            column_values = [item.get(column) for item in data]
            style = self.get_column_style(column, column_values)
            
            # Format column name
            display_name = column.replace('_', ' ').title()
            
            table.add_column(display_name, style=style, no_wrap=True)
        
        # Add rows
        for item in data:
            row_values = []
            for column in columns:
                value = item.get(column)
                formatted_value = self.format_cell_value(value)
                row_values.append(formatted_value)
            
            table.add_row(*row_values)
        
        return table
    
    def format_as_table(self, data: Any, title: Optional[str] = None, 
                       max_rows: Optional[int] = None) -> Union[Table, List[Table]]:
        """
        Format data as table(s) with pagination if needed.
        
        Args:
            data: Data to format
            title: Optional table title
            max_rows: Maximum rows per table (for pagination)
            
        Returns:
            Single Table or list of Tables if paginated
        """
        if not self.detect_table_structure(data):
            raise ValueError("Data is not suitable for table display")
        
        max_rows = max_rows or self.max_rows_per_page
        
        # If data fits in one table, return single table
        if len(data) <= max_rows:
            return self.create_rich_table(data, title)
        
        # Split into multiple tables for pagination
        tables = []
        for i in range(0, len(data), max_rows):
            chunk = data[i:i + max_rows]
            page_num = (i // max_rows) + 1
            total_pages = (len(data) + max_rows - 1) // max_rows
            
            chunk_title = f"{title or 'Results'} (Page {page_num}/{total_pages})"
            table = self.create_rich_table(chunk, chunk_title)
            tables.append(table)
        
        return tables
    
    def display_table(self, data: Any, title: Optional[str] = None, 
                     show_pagination: bool = True) -> None:
        """
        Display data as table(s) in the console.
        
        Args:
            data: Data to display
            title: Optional table title
            show_pagination: Whether to show pagination info
        """
        try:
            result = self.format_as_table(data, title)
            
            if isinstance(result, Table):
                # Single table
                self.console.print(result)
            else:
                # Multiple tables (paginated)
                for i, table in enumerate(result):
                    if i > 0 and show_pagination:
                        # Add separator between pages
                        self.console.print("\n" + "─" * 50 + "\n")
                    
                    self.console.print(table)
                
                if show_pagination and len(result) > 1:
                    # Show pagination summary
                    total_rows = len(data)
                    pages = len(result)
                    
                    pagination_text = Text(
                        f"📄 Showing {total_rows} rows across {pages} pages",
                        style="dim cyan"
                    )
                    
                    pagination_panel = Panel(
                        pagination_text,
                        border_style="dim",
                        padding=(0, 1)
                    )
                    
                    self.console.print("\n")
                    self.console.print(pagination_panel)
        
        except ValueError as e:
            # Data not suitable for table display
            error_text = Text(f"Cannot display as table: {e}", style="yellow")
            error_panel = Panel(error_text, title="Table Display Error", border_style="yellow")
            self.console.print(error_panel)
    
    def analyze_data_structure(self, data: Any) -> Dict[str, Any]:
        """
        Analyze data structure and provide insights.
        
        Args:
            data: Data to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'is_array': isinstance(data, list),
            'length': len(data) if isinstance(data, list) else 0,
            'is_table_suitable': False,
            'columns': [],
            'data_types': {},
            'sample_data': None
        }
        
        if not isinstance(data, list):
            return analysis
        
        analysis['is_table_suitable'] = self.detect_table_structure(data)
        
        if analysis['is_table_suitable'] and data:
            analysis['columns'] = self.extract_columns(data)
            
            # Analyze data types for each column
            for column in analysis['columns']:
                column_values = [item.get(column) for item in data if isinstance(item, dict)]
                non_null_values = [v for v in column_values if v is not None]
                
                if non_null_values:
                    # Determine predominant type
                    type_counts = {}
                    for value in non_null_values[:20]:  # Sample first 20 values
                        value_type = type(value).__name__
                        type_counts[value_type] = type_counts.get(value_type, 0) + 1
                    
                    predominant_type = max(type_counts, key=type_counts.get)
                    analysis['data_types'][column] = predominant_type
            
            # Provide sample data (first few rows)
            analysis['sample_data'] = data[:3] if len(data) > 3 else data
        
        return analysis
    
    def suggest_display_format(self, data: Any) -> str:
        """
        Suggest the best display format for the data.
        
        Args:
            data: Data to analyze
            
        Returns:
            Suggested format ('table', 'json', 'list', 'single')
        """
        if not isinstance(data, (list, dict)):
            return 'single'
        
        if isinstance(data, dict):
            return 'json'
        
        if isinstance(data, list):
            if len(data) == 0:
                return 'json'
            
            if self.detect_table_structure(data):
                return 'table'
            
            # Check if it's a simple list of primitives
            if all(isinstance(item, (str, int, float, bool)) for item in data):
                return 'list'
            
            return 'json'
        
        return 'json'
    
    def format_simple_list(self, data: List[Any], title: Optional[str] = None) -> Table:
        """
        Format simple list (non-dict items) as a single-column table.
        
        Args:
            data: List of simple values
            title: Optional table title
            
        Returns:
            Rich Table object
        """
        table = Table(
            title=title or f"List ({len(data)} items)",
            show_header=True,
            header_style="bold blue"
        )
        
        table.add_column("Value", style="white")
        
        for item in data:
            formatted_value = self.format_cell_value(item)
            table.add_row(formatted_value)
        
        return table
    
    def create_summary_table(self, analysis: Dict[str, Any]) -> Table:
        """
        Create summary table from data analysis.
        
        Args:
            analysis: Analysis results from analyze_data_structure
            
        Returns:
            Rich Table with summary information
        """
        table = Table(title="Data Analysis", show_header=True, header_style="bold blue")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Is Array", "✅" if analysis['is_array'] else "❌")
        table.add_row("Length", str(analysis['length']))
        table.add_row("Table Suitable", "✅" if analysis['is_table_suitable'] else "❌")
        
        if analysis['columns']:
            table.add_row("Columns", str(len(analysis['columns'])))
            table.add_row("Column Names", ", ".join(analysis['columns'][:5]))
        
        if analysis['data_types']:
            type_summary = []
            for col, dtype in list(analysis['data_types'].items())[:3]:
                type_summary.append(f"{col}: {dtype}")
            table.add_row("Data Types", "; ".join(type_summary))
        
        return table
"""History query builder for filtering and searching request history."""

from typing import Optional, List, Any, Dict
from datetime import datetime


class HistoryQuery:
    """Builder class for constructing history queries with filters."""
    
    def __init__(self):
        self.filters = {}
        self._limit = None
        self._offset = 0
        self._order_by = 'timestamp'
        self._descending = True
    
    def filter_by_method(self, method: str) -> 'HistoryQuery':
        """Filter by HTTP method."""
        self.filters['method'] = method.upper()
        return self
    
    def filter_by_status_code(self, status_code: int) -> 'HistoryQuery':
        """Filter by specific status code."""
        self.filters['status_code'] = status_code
        return self
    
    def filter_by_status_range(self, start_status: int, end_status: int) -> 'HistoryQuery':
        """Filter by status code range."""
        self.filters['status_range'] = (start_status, end_status)
        return self
    
    def filter_by_url_pattern(self, pattern: str) -> 'HistoryQuery':
        """Filter by URL pattern (substring match)."""
        self.filters['url_pattern'] = pattern
        return self
    
    def filter_by_environment(self, environment: str) -> 'HistoryQuery':
        """Filter by environment name."""
        self.filters['environment'] = environment
        return self
    
    def filter_by_tags(self, tags: List[str]) -> 'HistoryQuery':
        """Filter by tags (any of the specified tags)."""
        self.filters['tags'] = tags
        return self
    
    def filter_by_date_range(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> 'HistoryQuery':
        """Filter by date range."""
        if start_date or end_date:
            self.filters['date_range'] = (start_date, end_date)
        return self
    
    def filter_by_template(self, template_name: str) -> 'HistoryQuery':
        """Filter by template name."""
        self.filters['template'] = template_name
        return self
    
    def filter_by_success(self, success_only: bool = True) -> 'HistoryQuery':
        """Filter by success status."""
        if success_only:
            self.filters['success_only'] = True
        return self
    
    def filter_by_errors(self, errors_only: bool = True) -> 'HistoryQuery':
        """Filter by error status."""
        if errors_only:
            self.filters['errors_only'] = True
        return self
    
    def limit(self, count: int) -> 'HistoryQuery':
        """Limit number of results."""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'HistoryQuery':
        """Set result offset."""
        self._offset = count
        return self
    
    def order_by_date(self, descending: bool = True) -> 'HistoryQuery':
        """Order results by date."""
        self._order_by = 'timestamp'
        self._descending = descending
        return self
    
    def order_by_status(self, descending: bool = False) -> 'HistoryQuery':
        """Order results by status code."""
        self._order_by = 'status'
        self._descending = descending
        return self
    
    def order_by_response_time(self, descending: bool = True) -> 'HistoryQuery':
        """Order results by response time."""
        self._order_by = 'response_time'
        self._descending = descending
        return self
    
    def get_filters(self) -> Dict[str, Any]:
        """Get all filters as dictionary."""
        return self.filters.copy()
    
    def get_limit(self) -> Optional[int]:
        """Get result limit."""
        return self._limit
    
    def get_offset(self) -> int:
        """Get result offset."""
        return self._offset
    
    def get_order_by(self) -> tuple:
        """Get ordering information as (field, descending)."""
        return (self._order_by, self._descending)
    
    def matches_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Check if an entry matches this query's filters.
        
        Args:
            entry: History entry dictionary
            
        Returns:
            True if entry matches all filters
        """
        # Method filter
        if 'method' in self.filters:
            if entry.get('method', '').upper() != self.filters['method']:
                return False
        
        # Status code filter
        if 'status_code' in self.filters:
            if entry.get('response_status') != self.filters['status_code']:
                return False
        
        # Status range filter
        if 'status_range' in self.filters:
            start_status, end_status = self.filters['status_range']
            status = entry.get('response_status', 0)
            if not (start_status <= status <= end_status):
                return False
        
        # URL pattern filter
        if 'url_pattern' in self.filters:
            url = entry.get('url', '')
            if self.filters['url_pattern'].lower() not in url.lower():
                return False
        
        # Environment filter
        if 'environment' in self.filters:
            if entry.get('environment') != self.filters['environment']:
                return False
        
        # Tags filter
        if 'tags' in self.filters:
            entry_tags = entry.get('tags', [])
            if not any(tag in entry_tags for tag in self.filters['tags']):
                return False
        
        # Date range filter
        if 'date_range' in self.filters:
            start_date, end_date = self.filters['date_range']
            entry_timestamp = entry.get('timestamp')
            
            if entry_timestamp:
                try:
                    if isinstance(entry_timestamp, str):
                        entry_date = datetime.fromisoformat(entry_timestamp.replace('Z', '+00:00'))
                    else:
                        entry_date = entry_timestamp
                    
                    if start_date and entry_date < start_date:
                        return False
                    if end_date and entry_date > end_date:
                        return False
                except (ValueError, TypeError):
                    return False
        
        # Template filter
        if 'template' in self.filters:
            if entry.get('template_name') != self.filters['template']:
                return False
        
        # Success filter
        if 'success_only' in self.filters:
            status = entry.get('response_status', 0)
            if not (200 <= status < 300):
                return False
        
        # Errors filter
        if 'errors_only' in self.filters:
            status = entry.get('response_status', 0)
            if not (400 <= status < 600):
                return False
        
        return True
    
    def apply_to_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply this query to a list of entries.
        
        Args:
            entries: List of history entry dictionaries
            
        Returns:
            Filtered and sorted list of entries
        """
        # Apply filters
        filtered_entries = [entry for entry in entries if self.matches_entry(entry)]
        
        # Apply sorting
        if self._order_by == 'timestamp':
            filtered_entries.sort(
                key=lambda x: x.get('timestamp', ''),
                reverse=self._descending
            )
        elif self._order_by == 'status':
            filtered_entries.sort(
                key=lambda x: x.get('response_status', 0),
                reverse=self._descending
            )
        elif self._order_by == 'response_time':
            filtered_entries.sort(
                key=lambda x: x.get('response_time', 0),
                reverse=self._descending
            )
        
        # Apply offset and limit
        if self._offset > 0:
            filtered_entries = filtered_entries[self._offset:]
        
        if self._limit is not None:
            filtered_entries = filtered_entries[:self._limit]
        
        return filtered_entries
    
    def __str__(self) -> str:
        """String representation of the query."""
        parts = []
        
        for key, value in self.filters.items():
            if key == 'date_range':
                start, end = value
                if start and end:
                    parts.append(f"date: {start.date()} to {end.date()}")
                elif start:
                    parts.append(f"date: from {start.date()}")
                elif end:
                    parts.append(f"date: until {end.date()}")
            else:
                parts.append(f"{key}: {value}")
        
        if self._limit:
            parts.append(f"limit: {self._limit}")
        
        if self._offset:
            parts.append(f"offset: {self._offset}")
        
        order_desc = "desc" if self._descending else "asc"
        parts.append(f"order: {self._order_by} {order_desc}")
        
        return "HistoryQuery(" + ", ".join(parts) + ")"
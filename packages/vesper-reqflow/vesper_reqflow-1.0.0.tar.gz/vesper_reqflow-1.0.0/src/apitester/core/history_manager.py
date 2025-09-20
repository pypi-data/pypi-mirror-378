"""History manager for tracking and managing API request history."""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta

from ..storage.operations import HistoryOperations
from ..storage.models import RequestRecord, HTTPMethod
from ..core.http_client import HTTPResponse
from ..core.graphql_client import GraphQLResponse
from ..config.settings import get_config


logger = logging.getLogger(__name__)


class HistoryManagerError(Exception):
    """Base exception for history manager errors."""
    pass


class HistoryNotFoundError(HistoryManagerError):
    """Raised when history record is not found."""
    pass


class HistoryManager:
    """Manages API request history with persistence and querying capabilities."""
    
    def __init__(self):
        self.history_ops = HistoryOperations()
        self.config = get_config()
    
    def add_request(self, method: str, url: str, 
                   headers: Optional[Dict[str, str]] = None,
                   body: Optional[str] = None,
                   params: Optional[Dict[str, str]] = None,
                   response: Optional[Union[HTTPResponse, GraphQLResponse]] = None,
                   error_message: str = "",
                   template_name: Optional[str] = None,
                   environment: str = "default",
                   tags: Optional[List[str]] = None) -> RequestRecord:
        """
        Add a request to history.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            response: Response object (if successful)
            error_message: Error message (if failed)
            template_name: Name of template used (if any)
            environment: Environment name
            tags: Additional tags for categorization
            
        Returns:
            Created RequestRecord instance
            
        Raises:
            HistoryManagerError: If adding to history fails
        """
        try:
            # Create request record
            record = RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod(method.upper()),
                url=url,
                headers=headers or {},
                body=body or "",
                params=params or {},
                response_status=response.status_code if response else 0,
                response_headers=response.headers if response else {},
                response_body=response.text if hasattr(response, 'text') else "",
                response_time=response.request_time if response else 0.0,
                error_message=error_message,
                template_name=template_name,
                environment=environment
            )
            
            # Add tags if provided
            if tags:
                record.tags = tags
            
            # Add to storage
            success = self.history_ops.add_request(record)
            if not success:
                raise HistoryManagerError("Failed to add request to history")
            
            logger.debug(f"Added request to history: {method} {url}")
            return record
            
        except Exception as e:
            if isinstance(e, HistoryManagerError):
                raise
            raise HistoryManagerError(f"Failed to add request to history: {e}")
    
    def get_history(self, limit: Optional[int] = None, 
                   offset: int = 0,
                   method_filter: Optional[str] = None,
                   status_filter: Optional[List[int]] = None,
                   environment_filter: Optional[str] = None,
                   template_filter: Optional[str] = None,
                   date_from: Optional[datetime] = None,
                   date_to: Optional[datetime] = None,
                   search_term: Optional[str] = None,
                   include_errors: bool = True) -> List[RequestRecord]:
        """
        Get request history with filtering and pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            method_filter: Filter by HTTP method
            status_filter: Filter by response status codes
            environment_filter: Filter by environment
            template_filter: Filter by template name
            date_from: Filter records from this date
            date_to: Filter records to this date
            search_term: Search in URL or error message
            include_errors: Whether to include failed requests
            
        Returns:
            List of RequestRecord instances
            
        Raises:
            HistoryManagerError: If retrieval fails
        """
        try:
            # Get all history records
            all_records = self.history_ops.get_history(limit=None)
            
            # Apply filters
            filtered_records = []
            
            for record in all_records:
                # Method filter
                if method_filter and record.method.value.upper() != method_filter.upper():
                    continue
                
                # Status filter
                if status_filter and record.response_status not in status_filter:
                    continue
                
                # Environment filter
                if environment_filter and record.environment != environment_filter:
                    continue
                
                # Template filter
                if template_filter and record.template_name != template_filter:
                    continue
                
                # Date filters
                if date_from and record.timestamp < date_from:
                    continue
                
                if date_to and record.timestamp > date_to:
                    continue
                
                # Search term filter
                if search_term:
                    search_lower = search_term.lower()
                    if not any(search_lower in field.lower() for field in [
                        record.url,
                        record.error_message,
                        record.template_name or ""
                    ]):
                        continue
                
                # Error filter
                if not include_errors and record.error_message:
                    continue
                
                filtered_records.append(record)
            
            # Apply pagination
            if offset > 0:
                filtered_records = filtered_records[offset:]
            
            if limit is not None:
                filtered_records = filtered_records[:limit]
            
            logger.debug(f"Retrieved {len(filtered_records)} history records")
            return filtered_records
            
        except Exception as e:
            raise HistoryManagerError(f"Failed to get history: {e}")
    
    def get_last_request(self) -> Optional[RequestRecord]:
        """
        Get the most recent request record.
        
        Returns:
            Most recent RequestRecord or None if no history
        """
        try:
            return self.history_ops.get_last_request()
        except Exception as e:
            logger.error(f"Failed to get last request: {e}")
            return None
    
    def get_request_by_index(self, index: int) -> RequestRecord:
        """
        Get request record by index (0 = most recent).
        
        Args:
            index: Index of request (0-based, 0 = most recent)
            
        Returns:
            RequestRecord instance
            
        Raises:
            HistoryNotFoundError: If index is out of range
            HistoryManagerError: If retrieval fails
        """
        try:
            history = self.get_history(limit=index + 1)
            
            if index >= len(history):
                raise HistoryNotFoundError(f"No request found at index {index}")
            
            return history[index]
            
        except HistoryNotFoundError:
            raise
        except Exception as e:
            raise HistoryManagerError(f"Failed to get request by index: {e}")
    
    def clear_history(self, confirm: bool = False) -> bool:
        """
        Clear all request history.
        
        Args:
            confirm: Confirmation flag to prevent accidental deletion
            
        Returns:
            True if history was cleared
            
        Raises:
            HistoryManagerError: If clearing fails or not confirmed
        """
        if not confirm:
            raise HistoryManagerError("History clearing requires explicit confirmation")
        
        try:
            success = self.history_ops.clear_history()
            if success:
                logger.info("Cleared request history")
            return success
            
        except Exception as e:
            raise HistoryManagerError(f"Failed to clear history: {e}")
    
    def get_history_count(self) -> int:
        """
        Get total number of history records.
        
        Returns:
            Number of history records
        """
        try:
            return self.history_ops.get_history_count()
        except Exception as e:
            logger.error(f"Failed to get history count: {e}")
            return 0
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about request history.
        
        Returns:
            Dictionary with history statistics
        """
        try:
            all_records = self.get_history()
            
            if not all_records:
                return {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'success_rate': 0.0,
                    'methods': {},
                    'environments': {},
                    'templates': {},
                    'status_codes': {},
                    'average_response_time': 0.0,
                    'date_range': None
                }
            
            # Calculate statistics
            total_requests = len(all_records)
            successful_requests = sum(1 for r in all_records if r.was_successful())
            failed_requests = total_requests - successful_requests
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Method distribution
            methods = {}
            for record in all_records:
                method = record.method.value
                methods[method] = methods.get(method, 0) + 1
            
            # Environment distribution
            environments = {}
            for record in all_records:
                env = record.environment
                environments[env] = environments.get(env, 0) + 1
            
            # Template usage
            templates = {}
            for record in all_records:
                if record.template_name:
                    templates[record.template_name] = templates.get(record.template_name, 0) + 1
            
            # Status code distribution
            status_codes = {}
            for record in all_records:
                if record.response_status > 0:
                    status = record.response_status
                    status_codes[status] = status_codes.get(status, 0) + 1
            
            # Average response time
            response_times = [r.response_time for r in all_records if r.response_time > 0]
            average_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Date range
            timestamps = [r.timestamp for r in all_records]
            date_range = {
                'earliest': min(timestamps).isoformat(),
                'latest': max(timestamps).isoformat()
            } if timestamps else None
            
            return {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': success_rate,
                'methods': methods,
                'environments': environments,
                'templates': templates,
                'status_codes': status_codes,
                'average_response_time': average_response_time,
                'date_range': date_range
            }
            
        except Exception as e:
            logger.error(f"Failed to get history statistics: {e}")
            return {'error': str(e)}
    
    def export_history(self, format_type: str = 'json',
                      filters: Optional[Dict[str, Any]] = None,
                      include_response_bodies: bool = False) -> str:
        """
        Export request history to JSON or CSV format.
        
        Args:
            format_type: Export format ('json' or 'csv')
            filters: Filters to apply (same as get_history parameters)
            include_response_bodies: Whether to include response bodies
            
        Returns:
            Exported data as string
            
        Raises:
            HistoryManagerError: If export fails
        """
        try:
            # Get filtered history
            filters = filters or {}
            history = self.get_history(**filters)
            
            if format_type.lower() == 'json':
                return self._export_history_json(history, include_response_bodies)
            elif format_type.lower() == 'csv':
                return self._export_history_csv(history, include_response_bodies)
            else:
                raise HistoryManagerError(f"Unsupported export format: {format_type}")
            
        except Exception as e:
            if isinstance(e, HistoryManagerError):
                raise
            raise HistoryManagerError(f"Failed to export history: {e}")
    
    def _export_history_json(self, history: List[RequestRecord], 
                           include_response_bodies: bool) -> str:
        """Export history to JSON format."""
        import json
        
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'record_count': len(history),
                'includes_response_bodies': include_response_bodies
            },
            'requests': []
        }
        
        for record in history:
            request_data = {
                'timestamp': record.timestamp.isoformat(),
                'method': record.method.value,
                'url': record.url,
                'headers': record.headers,
                'body': record.body,
                'params': record.params,
                'response_status': record.response_status,
                'response_headers': record.response_headers,
                'response_time': record.response_time,
                'error_message': record.error_message,
                'template_name': record.template_name,
                'environment': record.environment,
                'success': record.was_successful()
            }
            
            if include_response_bodies:
                request_data['response_body'] = record.response_body
            
            export_data['requests'].append(request_data)
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _export_history_csv(self, history: List[RequestRecord], 
                          include_response_bodies: bool) -> str:
        """Export history to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        
        # Define CSV columns
        columns = [
            'timestamp', 'method', 'url', 'response_status', 'response_time',
            'success', 'error_message', 'template_name', 'environment'
        ]
        
        if include_response_bodies:
            columns.extend(['request_body', 'response_body'])
        
        writer = csv.writer(output)
        writer.writerow(columns)
        
        for record in history:
            row = [
                record.timestamp.isoformat(),
                record.method.value,
                record.url,
                record.response_status,
                record.response_time,
                record.was_successful(),
                record.error_message,
                record.template_name or '',
                record.environment
            ]
            
            if include_response_bodies:
                row.extend([
                    record.body,
                    record.response_body
                ])
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def cleanup_old_history(self, max_age_days: int = 30, 
                          max_records: Optional[int] = None,
                          dry_run: bool = False) -> Dict[str, Any]:
        """
        Clean up old history records.
        
        Args:
            max_age_days: Maximum age in days for records to keep
            max_records: Maximum number of records to keep (newest first)
            dry_run: If True, return what would be deleted without deleting
            
        Returns:
            Dictionary with cleanup results
            
        Raises:
            HistoryManagerError: If cleanup fails
        """
        try:
            all_records = self.get_history()
            
            if not all_records:
                return {
                    'total_records': 0,
                    'records_to_delete': 0,
                    'records_to_keep': 0,
                    'dry_run': dry_run
                }
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Find records to delete
            records_to_delete = []
            
            # Delete by age
            for record in all_records:
                if record.timestamp < cutoff_date:
                    records_to_delete.append(record)
            
            # Delete by count (keep newest records)
            if max_records and len(all_records) > max_records:
                # Sort by timestamp (newest first)
                sorted_records = sorted(all_records, key=lambda r: r.timestamp, reverse=True)
                excess_records = sorted_records[max_records:]
                
                # Add excess records to deletion list (avoid duplicates)
                for record in excess_records:
                    if record not in records_to_delete:
                        records_to_delete.append(record)
            
            result = {
                'total_records': len(all_records),
                'records_to_delete': len(records_to_delete),
                'records_to_keep': len(all_records) - len(records_to_delete),
                'dry_run': dry_run,
                'cutoff_date': cutoff_date.isoformat(),
                'max_records': max_records
            }
            
            if not dry_run and records_to_delete:
                # Note: This is a simplified implementation
                # In a real implementation, you'd need to modify the storage layer
                # to support selective deletion of history records
                logger.warning("Selective history deletion not yet implemented in storage layer")
                result['warning'] = "Selective deletion not implemented - use clear_history() for full cleanup"
            
            logger.info(f"History cleanup: {result['records_to_delete']} records marked for deletion")
            return result
            
        except Exception as e:
            raise HistoryManagerError(f"Failed to cleanup history: {e}")
    
    def find_similar_requests(self, reference_record: RequestRecord,
                            similarity_threshold: float = 0.8,
                            max_results: int = 10) -> List[Tuple[RequestRecord, float]]:
        """
        Find requests similar to a reference request.
        
        Args:
            reference_record: Reference request to compare against
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples (RequestRecord, similarity_score)
        """
        try:
            all_records = self.get_history()
            similar_requests = []
            
            for record in all_records:
                if record.timestamp == reference_record.timestamp:
                    continue  # Skip the reference record itself
                
                similarity = self._calculate_request_similarity(reference_record, record)
                
                if similarity >= similarity_threshold:
                    similar_requests.append((record, similarity))
            
            # Sort by similarity (highest first)
            similar_requests.sort(key=lambda x: x[1], reverse=True)
            
            return similar_requests[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to find similar requests: {e}")
            return []
    
    def _calculate_request_similarity(self, record1: RequestRecord, record2: RequestRecord) -> float:
        """Calculate similarity score between two requests."""
        score = 0.0
        total_weight = 0.0
        
        # Method similarity (weight: 0.2)
        if record1.method == record2.method:
            score += 0.2
        total_weight += 0.2
        
        # URL similarity (weight: 0.4)
        url_similarity = self._calculate_string_similarity(record1.url, record2.url)
        score += url_similarity * 0.4
        total_weight += 0.4
        
        # Environment similarity (weight: 0.1)
        if record1.environment == record2.environment:
            score += 0.1
        total_weight += 0.1
        
        # Template similarity (weight: 0.2)
        if record1.template_name and record2.template_name:
            if record1.template_name == record2.template_name:
                score += 0.2
        elif not record1.template_name and not record2.template_name:
            score += 0.1  # Both don't use templates
        total_weight += 0.2
        
        # Status similarity (weight: 0.1)
        if record1.response_status == record2.response_status:
            score += 0.1
        total_weight += 0.1
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple ratio."""
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0
        
        # Simple character-based similarity
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        if str1_lower == str2_lower:
            return 1.0
        
        # Calculate longest common subsequence ratio
        longer = str1_lower if len(str1_lower) > len(str2_lower) else str2_lower
        shorter = str2_lower if len(str1_lower) > len(str2_lower) else str1_lower
        
        matches = sum(1 for c in shorter if c in longer)
        return matches / len(longer) if longer else 0.0
    
    def query_history(self, query=None) -> List[Dict[str, Any]]:
        """
        Query history using a HistoryQuery object.
        
        Args:
            query: HistoryQuery object with filters (optional)
            
        Returns:
            List of history records as dictionaries
        """
        try:
            # Get all history records
            all_records = self.get_history()
            
            # Convert RequestRecord objects to dictionaries for compatibility
            history_dicts = []
            for record in all_records:
                history_dict = {
                    'id': f"{record.timestamp.isoformat()}_{record.method.value}_{hash(record.url) % 10000}",
                    'timestamp': record.timestamp.isoformat(),
                    'method': record.method.value,
                    'url': record.url,
                    'headers': record.headers,
                    'body': record.body,
                    'params': record.params,
                    'response_status': record.response_status,
                    'response_headers': record.response_headers,
                    'response_body': record.response_body,
                    'response_time': record.response_time,
                    'error_message': record.error_message,
                    'template_name': record.template_name,
                    'environment': record.environment,
                    'tags': getattr(record, 'tags', [])
                }
                history_dicts.append(history_dict)
            
            # Apply query filters if provided
            if query is not None:
                history_dicts = query.apply_to_entries(history_dicts)
            
            return history_dicts
            
        except Exception as e:
            logger.error(f"Failed to query history: {e}")
            return []
    
    def get_history_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific history entry by ID.
        
        Args:
            entry_id: History entry ID
            
        Returns:
            History entry as dictionary or None if not found
        """
        try:
            all_entries = self.query_history(None)  # Get all entries
            
            for entry in all_entries:
                if entry.get('id') == entry_id:
                    return entry
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get history entry {entry_id}: {e}")
            return None
    
    def delete_history_entry(self, entry_id: str) -> bool:
        """
        Delete a specific history entry.
        
        Args:
            entry_id: History entry ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you'd need to modify the storage layer
            # to support selective deletion
            logger.warning(f"Selective deletion of entry {entry_id} not implemented")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete history entry {entry_id}: {e}")
            return False
    
    def retry_request(self, entry_id: str, environment: str = "default", save_to_history: bool = True):
        """
        Retry a request from history.
        
        Args:
            entry_id: History entry ID
            environment: Environment to use
            save_to_history: Whether to save retry to history
            
        Returns:
            Response object
        """
        try:
            entry = self.get_history_entry(entry_id)
            if not entry:
                raise HistoryManagerError(f"History entry {entry_id} not found")
            
            # This would need to be implemented with the HTTP client
            # For now, raise an error indicating it's not implemented
            raise HistoryManagerError("Request retry not yet implemented")
            
        except Exception as e:
            logger.error(f"Failed to retry request {entry_id}: {e}")
            raise HistoryManagerError(f"Failed to retry request: {e}")
    
    def export_history_to_file(self, file_path, query=None, format_type="json", include_bodies=True, overwrite=False):
        """
        Export history to file.
        
        Args:
            file_path: Output file path
            query: HistoryQuery object (optional)
            format_type: Export format
            include_bodies: Whether to include response bodies
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to saved file
        """
        try:
            import json
            from pathlib import Path
            
            # Get history entries
            entries = self.query_history(query)
            
            # Prepare export data
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'format': format_type,
                'include_bodies': include_bodies,
                'entries': entries if include_bodies else [
                    {k: v for k, v in entry.items() if k not in ['response_body', 'body']}
                    for entry in entries
                ]
            }
            
            # Write to file
            file_path = Path(file_path)
            if file_path.exists() and not overwrite:
                raise HistoryManagerError(f"File {file_path} already exists")
            
            with open(file_path, 'w') as f:
                if format_type.lower() == 'json':
                    json.dump(export_data, f, indent=2)
                else:
                    raise HistoryManagerError(f"Unsupported format: {format_type}")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            raise HistoryManagerError(f"Failed to export history: {e}")
    
    def get_history_statistics(self, query=None) -> Dict[str, Any]:
        """
        Get history statistics with optional query filtering.
        
        Args:
            query: HistoryQuery object (optional)
            
        Returns:
            Dictionary with statistics
        """
        try:
            entries = self.query_history(query)
            
            if not entries:
                return {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'client_errors': 0,
                    'server_errors': 0,
                    'success_rate': 0.0,
                    'avg_response_time': 0.0,
                    'methods': {},
                    'status_codes': {},
                    'environments': {},
                    'top_domains': []
                }
            
            total_requests = len(entries)
            successful_requests = sum(1 for e in entries if 200 <= e.get('response_status', 0) < 300)
            client_errors = sum(1 for e in entries if 400 <= e.get('response_status', 0) < 500)
            server_errors = sum(1 for e in entries if 500 <= e.get('response_status', 0) < 600)
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate average response time
            response_times = [e.get('response_time', 0) for e in entries if e.get('response_time', 0) > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Method distribution
            methods = {}
            for entry in entries:
                method = entry.get('method', 'UNKNOWN')
                methods[method] = methods.get(method, 0) + 1
            
            # Status code distribution
            status_codes = {}
            for entry in entries:
                status = entry.get('response_status', 0)
                if status > 0:
                    status_codes[status] = status_codes.get(status, 0) + 1
            
            # Environment distribution
            environments = {}
            for entry in entries:
                env = entry.get('environment', 'default')
                environments[env] = environments.get(env, 0) + 1
            
            # Top domains
            from urllib.parse import urlparse
            domains = {}
            for entry in entries:
                try:
                    domain = urlparse(entry.get('url', '')).netloc
                    if domain:
                        domains[domain] = domains.get(domain, 0) + 1
                except:
                    pass
            
            top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'client_errors': client_errors,
                'server_errors': server_errors,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'methods': methods,
                'status_codes': status_codes,
                'environments': environments,
                'top_domains': top_domains
            }
            
        except Exception as e:
            logger.error(f"Failed to get history statistics: {e}")
            return {'error': str(e)}
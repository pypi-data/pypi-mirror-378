"""Response saving functionality for API responses."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import logging

from ..core.http_client import HTTPResponse
from ..core.graphql_client import GraphQLResponse


logger = logging.getLogger(__name__)


class ResponseSaveError(Exception):
    """Raised when response saving fails."""
    pass


class ResponseSaver:
    """Handles saving API responses to files in various formats."""
    
    def __init__(self):
        self.default_directory = Path.cwd() / "api_responses"
    
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure directory exists, create if necessary.
        
        Args:
            directory: Directory path
            
        Returns:
            Path object for the directory
            
        Raises:
            ResponseSaveError: If directory cannot be created
        """
        dir_path = Path(directory)
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return dir_path
        except PermissionError:
            raise ResponseSaveError(f"Permission denied creating directory: {directory}")
        except OSError as e:
            raise ResponseSaveError(f"Failed to create directory {directory}: {e}")
    
    def generate_filename(self, base_name: Optional[str] = None, 
                         extension: str = "json", 
                         include_timestamp: bool = True) -> str:
        """
        Generate filename for response file.
        
        Args:
            base_name: Base name for the file
            extension: File extension
            include_timestamp: Whether to include timestamp
            
        Returns:
            Generated filename
        """
        if not base_name:
            base_name = "response"
        
        # Sanitize base name
        safe_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_', '.'))
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.{extension}"
        else:
            filename = f"{safe_name}.{extension}"
        
        return filename
    
    def detect_response_format(self, response: Union[HTTPResponse, GraphQLResponse]) -> str:
        """
        Detect appropriate format for saving response.
        
        Args:
            response: Response object
            
        Returns:
            Detected format ('json', 'xml', 'html', 'text')
        """
        if isinstance(response, GraphQLResponse):
            return 'json'  # GraphQL responses are always JSON
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type or 'text/json' in content_type:
            return 'json'
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            return 'xml'
        elif 'text/html' in content_type:
            return 'html'
        else:
            return 'text'
    
    def save_response_body(self, response: Union[HTTPResponse, GraphQLResponse],
                          file_path: Union[str, Path],
                          format_type: Optional[str] = None,
                          pretty_print: bool = True) -> Path:
        """
        Save response body to file.
        
        Args:
            response: Response object
            file_path: Path to save file
            format_type: Format type ('json', 'xml', 'html', 'text')
            pretty_print: Whether to format content for readability
            
        Returns:
            Path to saved file
            
        Raises:
            ResponseSaveError: If saving fails
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        self.ensure_directory(file_path.parent)
        
        # Detect format if not specified
        if not format_type:
            format_type = self.detect_response_format(response)
        
        try:
            # Get content based on response type
            if isinstance(response, GraphQLResponse):
                content = self._format_graphql_content(response, pretty_print)
            else:
                content = self._format_http_content(response, format_type, pretty_print)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved response body to {file_path}")
            return file_path
            
        except Exception as e:
            raise ResponseSaveError(f"Failed to save response body: {e}")
    
    def _format_http_content(self, response: HTTPResponse, 
                           format_type: str, pretty_print: bool) -> str:
        """Format HTTP response content for saving."""
        content = response.text
        
        if not pretty_print:
            return content
        
        if format_type == 'json':
            try:
                # Parse and re-format JSON
                parsed = json.loads(content)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # Return as-is if not valid JSON
                return content
        
        elif format_type == 'xml':
            try:
                # Basic XML formatting
                import xml.dom.minidom
                dom = xml.dom.minidom.parseString(content)
                return dom.toprettyxml(indent="  ", encoding=None)
            except Exception:
                # Return as-is if XML parsing fails
                return content
        
        # For HTML and text, return as-is
        return content
    
    def _format_graphql_content(self, response: GraphQLResponse, pretty_print: bool) -> str:
        """Format GraphQL response content for saving."""
        response_data = response.to_dict()
        
        if pretty_print:
            return json.dumps(response_data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(response_data, separators=(',', ':'))
    
    def save_response_headers(self, response: Union[HTTPResponse, GraphQLResponse],
                            file_path: Union[str, Path]) -> Path:
        """
        Save response headers to file.
        
        Args:
            response: Response object
            file_path: Path to save file
            
        Returns:
            Path to saved file
            
        Raises:
            ResponseSaveError: If saving fails
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        self.ensure_directory(file_path.parent)
        
        try:
            headers_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'timestamp': datetime.now().isoformat(),
                'request_time': response.request_time
            }
            
            if hasattr(response, 'url'):
                headers_data['url'] = response.url
            
            content = json.dumps(headers_data, indent=2, ensure_ascii=False)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved response headers to {file_path}")
            return file_path
            
        except Exception as e:
            raise ResponseSaveError(f"Failed to save response headers: {e}")
    
    def save_complete_response(self, response: Union[HTTPResponse, GraphQLResponse],
                             directory: Optional[Union[str, Path]] = None,
                             base_name: Optional[str] = None,
                             include_headers: bool = True,
                             pretty_print: bool = True) -> Dict[str, Path]:
        """
        Save complete response (body and optionally headers) to files.
        
        Args:
            response: Response object
            directory: Directory to save files (default: ./api_responses)
            base_name: Base name for files
            include_headers: Whether to save headers separately
            pretty_print: Whether to format content for readability
            
        Returns:
            Dictionary mapping file types to saved paths
            
        Raises:
            ResponseSaveError: If saving fails
        """
        if directory is None:
            directory = self.default_directory
        
        directory = self.ensure_directory(directory)
        
        # Generate base filename
        if not base_name:
            if isinstance(response, GraphQLResponse):
                base_name = "graphql_response"
            else:
                base_name = "http_response"
        
        saved_files = {}
        
        try:
            # Save response body
            format_type = self.detect_response_format(response)
            body_filename = self.generate_filename(base_name, format_type)
            body_path = directory / body_filename
            
            saved_files['body'] = self.save_response_body(
                response, body_path, format_type, pretty_print
            )
            
            # Save headers if requested
            if include_headers:
                headers_filename = self.generate_filename(f"{base_name}_headers", "json")
                headers_path = directory / headers_filename
                
                saved_files['headers'] = self.save_response_headers(response, headers_path)
            
            return saved_files
            
        except Exception as e:
            # Clean up any partially saved files
            for file_path in saved_files.values():
                try:
                    if file_path.exists():
                        file_path.unlink()
                except Exception:
                    pass
            
            raise ResponseSaveError(f"Failed to save complete response: {e}")
    
    def save_raw_response(self, response: HTTPResponse, file_path: Union[str, Path]) -> Path:
        """
        Save raw response content (bytes) to file.
        
        Args:
            response: HTTP response object
            file_path: Path to save file
            
        Returns:
            Path to saved file
            
        Raises:
            ResponseSaveError: If saving fails
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        self.ensure_directory(file_path.parent)
        
        try:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Saved raw response to {file_path}")
            return file_path
            
        except Exception as e:
            raise ResponseSaveError(f"Failed to save raw response: {e}")
    
    def save_response_summary(self, response: Union[HTTPResponse, GraphQLResponse],
                            file_path: Union[str, Path],
                            request_info: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save response summary with metadata.
        
        Args:
            response: Response object
            file_path: Path to save file
            request_info: Optional request information
            
        Returns:
            Path to saved file
            
        Raises:
            ResponseSaveError: If saving fails
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        self.ensure_directory(file_path.parent)
        
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'status_code': response.status_code,
                'request_time': response.request_time,
                'headers': dict(response.headers),
                'response_type': 'GraphQL' if isinstance(response, GraphQLResponse) else 'HTTP'
            }
            
            if hasattr(response, 'url'):
                summary['url'] = response.url
            
            if hasattr(response, 'from_cache'):
                summary['from_cache'] = response.from_cache
            
            # Add request information if provided
            if request_info:
                summary['request'] = request_info
            
            # Add response-specific data
            if isinstance(response, GraphQLResponse):
                summary['has_errors'] = response.has_errors()
                if response.has_errors():
                    summary['error_messages'] = response.get_error_messages()
                summary['has_data'] = response.data is not None
            else:
                summary['content_length'] = len(response.text)
                summary['content_type'] = response.headers.get('Content-Type', 'unknown')
            
            content = json.dumps(summary, indent=2, ensure_ascii=False)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved response summary to {file_path}")
            return file_path
            
        except Exception as e:
            raise ResponseSaveError(f"Failed to save response summary: {e}")
    
    def get_available_space(self, directory: Union[str, Path]) -> int:
        """
        Get available disk space in directory.
        
        Args:
            directory: Directory path
            
        Returns:
            Available space in bytes
        """
        try:
            stat = os.statvfs(str(directory))
            return stat.f_bavail * stat.f_frsize
        except (OSError, AttributeError):
            # statvfs not available on Windows, use shutil
            import shutil
            try:
                _, _, free = shutil.disk_usage(str(directory))
                return free
            except Exception:
                return -1  # Unknown
    
    def check_disk_space(self, directory: Union[str, Path], 
                        required_space: int = 1024 * 1024) -> bool:
        """
        Check if sufficient disk space is available.
        
        Args:
            directory: Directory path
            required_space: Required space in bytes (default: 1MB)
            
        Returns:
            True if sufficient space available
        """
        available = self.get_available_space(directory)
        if available == -1:
            return True  # Unknown, assume OK
        
        return available >= required_space
    
    def cleanup_old_files(self, directory: Union[str, Path], 
                         max_files: int = 100, 
                         max_age_days: int = 30) -> int:
        """
        Clean up old response files.
        
        Args:
            directory: Directory to clean
            max_files: Maximum number of files to keep
            max_age_days: Maximum age in days
            
        Returns:
            Number of files deleted
        """
        directory = Path(directory)
        
        if not directory.exists():
            return 0
        
        deleted_count = 0
        current_time = datetime.now()
        
        try:
            # Get all response files
            files = []
            for pattern in ['*.json', '*.xml', '*.html', '*.txt']:
                files.extend(directory.glob(pattern))
            
            # Sort by modification time (oldest first)
            files.sort(key=lambda f: f.stat().st_mtime)
            
            # Delete files exceeding max_files limit
            if len(files) > max_files:
                excess_files = files[:-max_files]
                for file_path in excess_files:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted excess file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {e}")
            
            # Delete files older than max_age_days
            max_age_seconds = max_age_days * 24 * 3600
            
            for file_path in files:
                try:
                    file_age = current_time.timestamp() - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return deleted_count


# Utility functions

def save_response_quick(response: Union[HTTPResponse, GraphQLResponse],
                       filename: Optional[str] = None,
                       directory: Optional[Union[str, Path]] = None) -> Path:
    """
    Quick save response with automatic filename generation.
    
    Args:
        response: Response object
        filename: Optional filename
        directory: Optional directory
        
    Returns:
        Path to saved file
    """
    saver = ResponseSaver()
    
    if filename:
        file_path = Path(directory or saver.default_directory) / filename
        return saver.save_response_body(response, file_path)
    else:
        saved_files = saver.save_complete_response(response, directory)
        return saved_files['body']


def save_multiple_responses(responses: List[Union[HTTPResponse, GraphQLResponse]],
                          directory: Optional[Union[str, Path]] = None,
                          base_name: str = "response") -> List[Dict[str, Path]]:
    """
    Save multiple responses with indexed filenames.
    
    Args:
        responses: List of response objects
        directory: Directory to save files
        base_name: Base name for files
        
    Returns:
        List of dictionaries mapping file types to paths
    """
    saver = ResponseSaver()
    saved_files_list = []
    
    for i, response in enumerate(responses, 1):
        indexed_name = f"{base_name}_{i:03d}"
        saved_files = saver.save_complete_response(response, directory, indexed_name)
        saved_files_list.append(saved_files)
    
    return saved_files_list
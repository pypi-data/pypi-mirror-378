"""Template import/export functionality for JSON and YAML formats."""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime

from .template_manager import TemplateManager, TemplateManagerError, TemplateValidationError
from ..storage.models import RequestTemplate, HTTPMethod


logger = logging.getLogger(__name__)


class TemplateImportError(Exception):
    """Raised when template import fails."""
    pass


class TemplateExportError(Exception):
    """Raised when template export fails."""
    pass


class TemplateImporter:
    """Handles import and export of request templates in various formats."""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.supported_formats = ['json', 'yaml', 'yml']
    
    def export_templates(self, template_names: Optional[List[str]] = None,
                        format_type: str = 'json',
                        include_metadata: bool = True,
                        pretty_print: bool = True) -> str:
        """
        Export templates to JSON or YAML format.
        
        Args:
            template_names: List of template names to export (None for all)
            format_type: Export format ('json' or 'yaml')
            include_metadata: Whether to include creation/update timestamps
            pretty_print: Whether to format output for readability
            
        Returns:
            Exported data as string
            
        Raises:
            TemplateExportError: If export fails
        """
        try:
            if format_type.lower() not in self.supported_formats:
                raise TemplateExportError(f"Unsupported format: {format_type}")
            
            # Get templates to export
            if template_names is None:
                template_names = self.template_manager.list_templates()
            
            if not template_names:
                logger.warning("No templates to export")
                return self._format_output({}, format_type, pretty_print)
            
            # Export templates
            exported_data = {
                'export_info': {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'exported_by': 'Agentic API Tester',
                    'template_count': len(template_names),
                    'format': format_type
                },
                'templates': {}
            }
            
            for template_name in template_names:
                try:
                    template = self.template_manager.load_template(template_name)
                    template_data = self._template_to_export_dict(template, include_metadata)
                    exported_data['templates'][template_name] = template_data
                    
                except Exception as e:
                    logger.error(f"Failed to export template '{template_name}': {e}")
                    # Continue with other templates
                    continue
            
            logger.info(f"Exported {len(exported_data['templates'])} templates in {format_type} format")
            return self._format_output(exported_data, format_type, pretty_print)
            
        except Exception as e:
            if isinstance(e, TemplateExportError):
                raise
            raise TemplateExportError(f"Export failed: {e}")
    
    def _template_to_export_dict(self, template: RequestTemplate, include_metadata: bool) -> Dict[str, Any]:
        """Convert template to export dictionary format."""
        data = {
            'method': template.method.value,
            'url': template.url,
            'headers': template.headers,
            'body': template.body,
            'params': template.params,
            'description': template.description,
            'tags': template.tags
        }
        
        if include_metadata:
            data['metadata'] = {
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat()
            }
        
        return data
    
    def _format_output(self, data: Dict[str, Any], format_type: str, pretty_print: bool) -> str:
        """Format output data as JSON or YAML."""
        if format_type.lower() == 'json':
            if pretty_print:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        elif format_type.lower() in ['yaml', 'yml']:
            if pretty_print:
                return yaml.dump(data, default_flow_style=False, indent=2, 
                               allow_unicode=True, sort_keys=False)
            else:
                return yaml.dump(data, default_flow_style=True, allow_unicode=True)
        
        else:
            raise TemplateExportError(f"Unsupported format: {format_type}")
    
    def export_templates_to_file(self, file_path: Union[str, Path],
                               template_names: Optional[List[str]] = None,
                               format_type: Optional[str] = None,
                               include_metadata: bool = True,
                               overwrite: bool = False) -> Path:
        """
        Export templates to file.
        
        Args:
            file_path: Path to export file
            template_names: List of template names to export (None for all)
            format_type: Export format (auto-detected from file extension if None)
            include_metadata: Whether to include creation/update timestamps
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to exported file
            
        Raises:
            TemplateExportError: If export fails
        """
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if file_path.exists() and not overwrite:
                raise TemplateExportError(f"File already exists: {file_path}")
            
            # Auto-detect format from extension
            if format_type is None:
                extension = file_path.suffix.lower()
                if extension == '.json':
                    format_type = 'json'
                elif extension in ['.yaml', '.yml']:
                    format_type = 'yaml'
                else:
                    raise TemplateExportError(f"Cannot determine format from extension: {extension}")
            
            # Export templates
            exported_content = self.export_templates(
                template_names=template_names,
                format_type=format_type,
                include_metadata=include_metadata,
                pretty_print=True
            )
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            logger.info(f"Exported templates to {file_path}")
            return file_path
            
        except Exception as e:
            if isinstance(e, TemplateExportError):
                raise
            raise TemplateExportError(f"Failed to export to file: {e}")
    
    def import_templates(self, data: str, format_type: str,
                        overwrite_existing: bool = False,
                        validate_before_import: bool = True,
                        dry_run: bool = False) -> Dict[str, Any]:
        """
        Import templates from JSON or YAML data.
        
        Args:
            data: Template data as string
            format_type: Data format ('json' or 'yaml')
            overwrite_existing: Whether to overwrite existing templates
            validate_before_import: Whether to validate templates before importing
            dry_run: If True, validate but don't actually import
            
        Returns:
            Dictionary with import results
            
        Raises:
            TemplateImportError: If import fails
        """
        try:
            if format_type.lower() not in self.supported_formats:
                raise TemplateImportError(f"Unsupported format: {format_type}")
            
            # Parse data
            parsed_data = self._parse_import_data(data, format_type)
            
            # Validate structure
            self._validate_import_structure(parsed_data)
            
            # Extract templates
            templates_data = parsed_data.get('templates', {})
            
            if not templates_data:
                return {
                    'success': True,
                    'imported_count': 0,
                    'skipped_count': 0,
                    'error_count': 0,
                    'errors': [],
                    'imported_templates': [],
                    'skipped_templates': [],
                    'dry_run': dry_run
                }
            
            # Import templates
            results = {
                'success': True,
                'imported_count': 0,
                'skipped_count': 0,
                'error_count': 0,
                'errors': [],
                'imported_templates': [],
                'skipped_templates': [],
                'dry_run': dry_run
            }
            
            for template_name, template_data in templates_data.items():
                try:
                    # Check if template exists
                    template_exists = self.template_manager.template_exists(template_name)
                    
                    if template_exists and not overwrite_existing:
                        results['skipped_count'] += 1
                        results['skipped_templates'].append({
                            'name': template_name,
                            'reason': 'Template already exists'
                        })
                        continue
                    
                    # Create template from data
                    template = self._create_template_from_data(template_name, template_data)
                    
                    # Validate template if requested
                    if validate_before_import:
                        validation_errors = template.validate()
                        if validation_errors:
                            raise TemplateValidationError(f"Validation failed: {'; '.join(validation_errors)}")
                    
                    # Import template (unless dry run)
                    if not dry_run:
                        self.template_manager.template_ops.save_template(template)
                    
                    results['imported_count'] += 1
                    results['imported_templates'].append({
                        'name': template_name,
                        'method': template.method.value,
                        'url': template.url,
                        'overwritten': template_exists
                    })
                    
                except Exception as e:
                    results['error_count'] += 1
                    results['errors'].append({
                        'template_name': template_name,
                        'error': str(e)
                    })
                    logger.error(f"Failed to import template '{template_name}': {e}")
            
            # Update overall success status
            results['success'] = results['error_count'] == 0
            
            if dry_run:
                logger.info(f"Dry run completed: {results['imported_count']} templates would be imported")
            else:
                logger.info(f"Import completed: {results['imported_count']} imported, "
                          f"{results['skipped_count']} skipped, {results['error_count']} errors")
            
            return results
            
        except Exception as e:
            if isinstance(e, TemplateImportError):
                raise
            raise TemplateImportError(f"Import failed: {e}")
    
    def _parse_import_data(self, data: str, format_type: str) -> Dict[str, Any]:
        """Parse import data from string."""
        try:
            if format_type.lower() == 'json':
                return json.loads(data)
            elif format_type.lower() in ['yaml', 'yml']:
                return yaml.safe_load(data)
            else:
                raise TemplateImportError(f"Unsupported format: {format_type}")
        
        except json.JSONDecodeError as e:
            raise TemplateImportError(f"Invalid JSON data: {e}")
        except yaml.YAMLError as e:
            raise TemplateImportError(f"Invalid YAML data: {e}")
    
    def _validate_import_structure(self, data: Dict[str, Any]) -> None:
        """Validate import data structure."""
        if not isinstance(data, dict):
            raise TemplateImportError("Import data must be a dictionary")
        
        if 'templates' not in data:
            raise TemplateImportError("Import data must contain 'templates' key")
        
        templates = data['templates']
        if not isinstance(templates, dict):
            raise TemplateImportError("'templates' must be a dictionary")
        
        # Validate each template structure
        for template_name, template_data in templates.items():
            if not isinstance(template_data, dict):
                raise TemplateImportError(f"Template '{template_name}' data must be a dictionary")
            
            required_fields = ['method', 'url']
            for field in required_fields:
                if field not in template_data:
                    raise TemplateImportError(f"Template '{template_name}' missing required field: {field}")
    
    def _create_template_from_data(self, name: str, data: Dict[str, Any]) -> RequestTemplate:
        """Create RequestTemplate from import data."""
        # Extract metadata if present
        metadata = data.get('metadata', {})
        
        # Parse timestamps
        created_at = datetime.now()
        updated_at = datetime.now()
        
        if 'created_at' in metadata:
            try:
                created_at = datetime.fromisoformat(metadata['created_at'])
            except ValueError:
                pass  # Use current time if parsing fails
        
        if 'updated_at' in metadata:
            try:
                updated_at = datetime.fromisoformat(metadata['updated_at'])
            except ValueError:
                pass  # Use current time if parsing fails
        
        # Create template
        template = RequestTemplate(
            name=name,
            method=HTTPMethod(data['method'].upper()),
            url=data['url'],
            headers=data.get('headers', {}),
            body=data.get('body', ''),
            params=data.get('params', {}),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            created_at=created_at,
            updated_at=updated_at
        )
        
        return template
    
    def import_templates_from_file(self, file_path: Union[str, Path],
                                 format_type: Optional[str] = None,
                                 overwrite_existing: bool = False,
                                 validate_before_import: bool = True,
                                 dry_run: bool = False) -> Dict[str, Any]:
        """
        Import templates from file.
        
        Args:
            file_path: Path to import file
            format_type: Data format (auto-detected from file extension if None)
            overwrite_existing: Whether to overwrite existing templates
            validate_before_import: Whether to validate templates before importing
            dry_run: If True, validate but don't actually import
            
        Returns:
            Dictionary with import results
            
        Raises:
            TemplateImportError: If import fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise TemplateImportError(f"File not found: {file_path}")
            
            # Auto-detect format from extension
            if format_type is None:
                extension = file_path.suffix.lower()
                if extension == '.json':
                    format_type = 'json'
                elif extension in ['.yaml', '.yml']:
                    format_type = 'yaml'
                else:
                    raise TemplateImportError(f"Cannot determine format from extension: {extension}")
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                raise TemplateImportError(f"Failed to read file: {e}")
            
            # Import templates
            results = self.import_templates(
                data=content,
                format_type=format_type,
                overwrite_existing=overwrite_existing,
                validate_before_import=validate_before_import,
                dry_run=dry_run
            )
            
            logger.info(f"Imported templates from {file_path}")
            return results
            
        except Exception as e:
            if isinstance(e, TemplateImportError):
                raise
            raise TemplateImportError(f"Failed to import from file: {e}")
    
    def convert_postman_collection(self, postman_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Postman collection to template format.
        
        Args:
            postman_data: Postman collection data
            
        Returns:
            Converted template data
            
        Raises:
            TemplateImportError: If conversion fails
        """
        try:
            if not isinstance(postman_data, dict):
                raise TemplateImportError("Postman data must be a dictionary")
            
            # Check if it's a Postman collection
            if 'info' not in postman_data or 'item' not in postman_data:
                raise TemplateImportError("Invalid Postman collection format")
            
            collection_info = postman_data['info']
            items = postman_data['item']
            
            # Convert to template format
            converted_data = {
                'export_info': {
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'exported_by': 'Agentic API Tester (Postman Converter)',
                    'source': f"Postman Collection: {collection_info.get('name', 'Unknown')}",
                    'template_count': 0,
                    'format': 'json'
                },
                'templates': {}
            }
            
            # Process items recursively
            self._process_postman_items(items, converted_data['templates'])
            
            converted_data['export_info']['template_count'] = len(converted_data['templates'])
            
            logger.info(f"Converted Postman collection with {len(converted_data['templates'])} requests")
            return converted_data
            
        except Exception as e:
            if isinstance(e, TemplateImportError):
                raise
            raise TemplateImportError(f"Postman conversion failed: {e}")
    
    def _process_postman_items(self, items: List[Dict[str, Any]], templates: Dict[str, Any], prefix: str = "") -> None:
        """Process Postman collection items recursively."""
        for item in items:
            if 'item' in item:
                # Folder - process recursively
                folder_name = item.get('name', 'folder')
                new_prefix = f"{prefix}{folder_name}_" if prefix else f"{folder_name}_"
                self._process_postman_items(item['item'], templates, new_prefix)
            
            elif 'request' in item:
                # Request item
                request_name = item.get('name', 'request')
                template_name = f"{prefix}{request_name}".replace(' ', '_').lower()
                
                # Ensure unique name
                original_name = template_name
                counter = 1
                while template_name in templates:
                    template_name = f"{original_name}_{counter}"
                    counter += 1
                
                # Convert request
                try:
                    template_data = self._convert_postman_request(item['request'])
                    template_data['description'] = item.get('description', '')
                    templates[template_name] = template_data
                except Exception as e:
                    logger.warning(f"Failed to convert Postman request '{request_name}': {e}")
    
    def _convert_postman_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert single Postman request to template format."""
        # Extract method
        method = request.get('method', 'GET').upper()
        
        # Extract URL
        url_data = request.get('url', {})
        if isinstance(url_data, str):
            url = url_data
        else:
            # Construct URL from parts
            protocol = url_data.get('protocol', 'https')
            host = url_data.get('host', [])
            path = url_data.get('path', [])
            
            if isinstance(host, list):
                host = '.'.join(host)
            if isinstance(path, list):
                path = '/'.join(path)
            
            url = f"{protocol}://{host}/{path}".replace('//', '/')
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
        
        # Extract headers
        headers = {}
        for header in request.get('header', []):
            if not header.get('disabled', False):
                headers[header.get('key', '')] = header.get('value', '')
        
        # Extract body
        body = ""
        body_data = request.get('body', {})
        if body_data:
            mode = body_data.get('mode', 'raw')
            if mode == 'raw':
                body = body_data.get('raw', '')
            elif mode == 'formdata':
                # Convert form data to URL-encoded format
                form_items = []
                for item in body_data.get('formdata', []):
                    if not item.get('disabled', False):
                        key = item.get('key', '')
                        value = item.get('value', '')
                        form_items.append(f"{key}={value}")
                body = '&'.join(form_items)
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            elif mode == 'urlencoded':
                # Convert URL-encoded data
                url_items = []
                for item in body_data.get('urlencoded', []):
                    if not item.get('disabled', False):
                        key = item.get('key', '')
                        value = item.get('value', '')
                        url_items.append(f"{key}={value}")
                body = '&'.join(url_items)
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        # Extract query parameters
        params = {}
        url_data = request.get('url', {})
        if isinstance(url_data, dict):
            for query in url_data.get('query', []):
                if not query.get('disabled', False):
                    params[query.get('key', '')] = query.get('value', '')
        
        return {
            'method': method,
            'url': url,
            'headers': headers,
            'body': body,
            'params': params,
            'tags': ['postman']
        }
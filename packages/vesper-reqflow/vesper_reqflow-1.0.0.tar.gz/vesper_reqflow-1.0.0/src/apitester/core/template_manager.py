"""Template manager for CRUD operations on request templates."""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from ..storage.operations import TemplateOperations
from ..storage.models import RequestTemplate, HTTPMethod, validate_http_method, validate_url
from ..core.request_validator import RequestValidator, ValidationError


logger = logging.getLogger(__name__)


class TemplateManagerError(Exception):
    """Base exception for template manager errors."""
    pass


class TemplateNotFoundError(TemplateManagerError):
    """Raised when template is not found."""
    pass


class TemplateValidationError(TemplateManagerError):
    """Raised when template validation fails."""
    pass


class TemplateManager:
    """Manages request templates with CRUD operations and validation."""
    
    def __init__(self):
        self.template_ops = TemplateOperations()
        self.validator = RequestValidator()
    
    def save_template(self, name: str, method: str, url: str,
                     headers: Optional[Dict[str, str]] = None,
                     body: Optional[str] = None,
                     params: Optional[Dict[str, str]] = None,
                     description: str = "",
                     tags: Optional[List[str]] = None,
                     overwrite: bool = False) -> RequestTemplate:
        """
        Save a new request template.
        
        Args:
            name: Template name (must be unique)
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            params: Query parameters
            description: Template description
            tags: Template tags for categorization
            overwrite: Whether to overwrite existing template
            
        Returns:
            Created RequestTemplate instance
            
        Raises:
            TemplateValidationError: If template data is invalid
            TemplateManagerError: If template already exists and overwrite=False
        """
        try:
            # Validate template name
            if not name or not name.strip():
                raise TemplateValidationError("Template name cannot be empty")
            
            name = name.strip()
            
            # Check if template already exists
            if not overwrite and self.template_exists(name):
                raise TemplateManagerError(f"Template '{name}' already exists. Use overwrite=True to replace it.")
            
            # Validate request components
            validated = self.validator.validate_complete_request(
                method=method,
                url=url,
                headers=headers,
                body=body,
                params=params
            )
            
            # Create template instance
            template = RequestTemplate(
                name=name,
                method=validated['method'],
                url=validated['url'],
                headers=validated['headers'],
                body=validated['body'] or "",
                params=validated['params'],
                description=description,
                tags=tags or [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Additional template-specific validation
            validation_errors = template.validate()
            if validation_errors:
                raise TemplateValidationError(f"Template validation failed: {'; '.join(validation_errors)}")
            
            # Save to storage
            success = self.template_ops.save_template(template)
            if not success:
                raise TemplateManagerError(f"Failed to save template '{name}'")
            
            logger.info(f"Saved template '{name}' ({method} {url})")
            return template
            
        except ValidationError as e:
            raise TemplateValidationError(f"Request validation failed: {e}")
        except Exception as e:
            if isinstance(e, (TemplateValidationError, TemplateManagerError)):
                raise
            raise TemplateManagerError(f"Unexpected error saving template: {e}")
    
    def load_template(self, name: str) -> RequestTemplate:
        """
        Load a request template by name.
        
        Args:
            name: Template name
            
        Returns:
            RequestTemplate instance
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateManagerError: If loading fails
        """
        try:
            template = self.template_ops.load_template(name)
            if template is None:
                raise TemplateNotFoundError(f"Template '{name}' not found")
            
            logger.debug(f"Loaded template '{name}'")
            return template
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            raise TemplateManagerError(f"Failed to load template '{name}': {e}")
    
    def list_templates(self, tags: Optional[List[str]] = None,
                      method_filter: Optional[str] = None,
                      search_term: Optional[str] = None) -> List[str]:
        """
        List template names with optional filtering.
        
        Args:
            tags: Filter by tags (templates must have at least one matching tag)
            method_filter: Filter by HTTP method
            search_term: Search in name, description, or URL
            
        Returns:
            List of template names matching filters
            
        Raises:
            TemplateManagerError: If listing fails
        """
        try:
            all_names = self.template_ops.list_templates()
            
            if not any([tags, method_filter, search_term]):
                return all_names
            
            # Apply filters
            filtered_names = []
            
            for name in all_names:
                try:
                    template = self.load_template(name)
                    
                    # Tag filter
                    if tags and not any(tag in template.tags for tag in tags):
                        continue
                    
                    # Method filter
                    if method_filter and template.method.value.upper() != method_filter.upper():
                        continue
                    
                    # Search term filter
                    if search_term:
                        search_lower = search_term.lower()
                        if not any(search_lower in field.lower() for field in [
                            template.name,
                            template.description,
                            template.url
                        ]):
                            continue
                    
                    filtered_names.append(name)
                    
                except Exception as e:
                    logger.warning(f"Error filtering template '{name}': {e}")
                    continue
            
            return filtered_names
            
        except Exception as e:
            raise TemplateManagerError(f"Failed to list templates: {e}")
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a request template.
        
        Args:
            name: Template name
            
        Returns:
            True if template was deleted
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateManagerError: If deletion fails
        """
        try:
            # Check if template exists
            if not self.template_exists(name):
                raise TemplateNotFoundError(f"Template '{name}' not found")
            
            success = self.template_ops.delete_template(name)
            if success:
                logger.info(f"Deleted template '{name}'")
            
            return success
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            raise TemplateManagerError(f"Failed to delete template '{name}': {e}")
    
    def template_exists(self, name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            name: Template name
            
        Returns:
            True if template exists
        """
        try:
            return self.template_ops.template_exists(name)
        except Exception as e:
            logger.error(f"Error checking template existence '{name}': {e}")
            return False
    
    def update_template(self, name: str, **updates) -> RequestTemplate:
        """
        Update an existing template.
        
        Args:
            name: Template name
            **updates: Fields to update (method, url, headers, body, params, description, tags)
            
        Returns:
            Updated RequestTemplate instance
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateValidationError: If updates are invalid
            TemplateManagerError: If update fails
        """
        try:
            # Load existing template
            template = self.load_template(name)
            
            # Apply updates
            if 'method' in updates:
                template.method = validate_http_method(updates['method'])
            
            if 'url' in updates:
                template.url = validate_url(updates['url'])
            
            if 'headers' in updates:
                template.headers = self.validator.validate_headers(updates['headers'])
            
            if 'body' in updates:
                content_type = template.headers.get('Content-Type')
                template.body = self.validator.validate_body(
                    updates['body'], template.method.value, content_type
                ) or ""
            
            if 'params' in updates:
                template.params = self.validator.validate_params(updates['params'])
            
            if 'description' in updates:
                template.description = str(updates['description'])
            
            if 'tags' in updates:
                template.tags = list(updates['tags']) if updates['tags'] else []
            
            # Update timestamp
            template.update_timestamp()
            
            # Validate updated template
            validation_errors = template.validate()
            if validation_errors:
                raise TemplateValidationError(f"Updated template validation failed: {'; '.join(validation_errors)}")
            
            # Save updated template
            success = self.template_ops.save_template(template)
            if not success:
                raise TemplateManagerError(f"Failed to save updated template '{name}'")
            
            logger.info(f"Updated template '{name}'")
            return template
            
        except (TemplateNotFoundError, TemplateValidationError):
            raise
        except ValidationError as e:
            raise TemplateValidationError(f"Validation failed: {e}")
        except Exception as e:
            raise TemplateManagerError(f"Failed to update template '{name}': {e}")
    
    def get_template_metadata(self, include_usage_stats: bool = False) -> List[Dict[str, Any]]:
        """
        Get metadata for all templates.
        
        Args:
            include_usage_stats: Whether to include usage statistics
            
        Returns:
            List of template metadata dictionaries
            
        Raises:
            TemplateManagerError: If metadata retrieval fails
        """
        try:
            metadata_list = self.template_ops.get_template_metadata()
            
            # Add additional computed fields
            for metadata in metadata_list:
                # Add age information
                created_at = datetime.fromisoformat(metadata['created_at'])
                updated_at = datetime.fromisoformat(metadata['updated_at'])
                
                age_days = (datetime.now() - created_at).days
                metadata['age_days'] = age_days
                
                last_modified_days = (datetime.now() - updated_at).days
                metadata['last_modified_days'] = last_modified_days
                
                # Add tag count
                metadata['tag_count'] = len(metadata.get('tags', []))
                
                # Add usage stats if requested
                if include_usage_stats:
                    # This would require additional tracking in the future
                    metadata['usage_count'] = 0  # Placeholder
                    metadata['last_used'] = None  # Placeholder
            
            return metadata_list
            
        except Exception as e:
            raise TemplateManagerError(f"Failed to get template metadata: {e}")
    
    def duplicate_template(self, source_name: str, new_name: str,
                          description_suffix: str = " (copy)") -> RequestTemplate:
        """
        Duplicate an existing template with a new name.
        
        Args:
            source_name: Name of template to duplicate
            new_name: Name for the new template
            description_suffix: Suffix to add to description
            
        Returns:
            New RequestTemplate instance
            
        Raises:
            TemplateNotFoundError: If source template doesn't exist
            TemplateManagerError: If new template name already exists or duplication fails
        """
        try:
            # Load source template
            source_template = self.load_template(source_name)
            
            # Check if new name already exists
            if self.template_exists(new_name):
                raise TemplateManagerError(f"Template '{new_name}' already exists")
            
            # Create new template
            new_template = RequestTemplate(
                name=new_name,
                method=source_template.method,
                url=source_template.url,
                headers=source_template.headers.copy(),
                body=source_template.body,
                params=source_template.params.copy(),
                description=source_template.description + description_suffix,
                tags=source_template.tags.copy(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save new template
            success = self.template_ops.save_template(new_template)
            if not success:
                raise TemplateManagerError(f"Failed to save duplicated template '{new_name}'")
            
            logger.info(f"Duplicated template '{source_name}' as '{new_name}'")
            return new_template
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            if isinstance(e, TemplateManagerError):
                raise
            raise TemplateManagerError(f"Failed to duplicate template: {e}")
    
    def rename_template(self, old_name: str, new_name: str) -> RequestTemplate:
        """
        Rename an existing template.
        
        Args:
            old_name: Current template name
            new_name: New template name
            
        Returns:
            Updated RequestTemplate instance
            
        Raises:
            TemplateNotFoundError: If source template doesn't exist
            TemplateManagerError: If new name already exists or rename fails
        """
        try:
            # Load existing template
            template = self.load_template(old_name)
            
            # Check if new name already exists
            if new_name != old_name and self.template_exists(new_name):
                raise TemplateManagerError(f"Template '{new_name}' already exists")
            
            # Update template name and timestamp
            template.name = new_name
            template.update_timestamp()
            
            # Save with new name
            success = self.template_ops.save_template(template)
            if not success:
                raise TemplateManagerError(f"Failed to save renamed template '{new_name}'")
            
            # Delete old template if name changed
            if new_name != old_name:
                self.template_ops.delete_template(old_name)
            
            logger.info(f"Renamed template '{old_name}' to '{new_name}'")
            return template
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            if isinstance(e, TemplateManagerError):
                raise
            raise TemplateManagerError(f"Failed to rename template: {e}")
    
    def search_templates(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search templates by query string.
        
        Args:
            query: Search query
            fields: Fields to search in (default: name, description, url, tags)
            
        Returns:
            List of matching templates with metadata and match info
            
        Raises:
            TemplateManagerError: If search fails
        """
        try:
            if not query or not query.strip():
                return []
            
            query_lower = query.strip().lower()
            
            if fields is None:
                fields = ['name', 'description', 'url', 'tags']
            
            results = []
            template_names = self.list_templates()
            
            for name in template_names:
                try:
                    template = self.load_template(name)
                    matches = []
                    
                    # Search in specified fields
                    if 'name' in fields and query_lower in template.name.lower():
                        matches.append('name')
                    
                    if 'description' in fields and query_lower in template.description.lower():
                        matches.append('description')
                    
                    if 'url' in fields and query_lower in template.url.lower():
                        matches.append('url')
                    
                    if 'tags' in fields:
                        for tag in template.tags:
                            if query_lower in tag.lower():
                                matches.append('tags')
                                break
                    
                    # If matches found, add to results
                    if matches:
                        result = {
                            'name': template.name,
                            'method': template.method.value,
                            'url': template.url,
                            'description': template.description,
                            'tags': template.tags,
                            'created_at': template.created_at.isoformat(),
                            'updated_at': template.updated_at.isoformat(),
                            'matched_fields': matches
                        }
                        results.append(result)
                
                except Exception as e:
                    logger.warning(f"Error searching template '{name}': {e}")
                    continue
            
            # Sort by relevance (number of matches, then by name)
            results.sort(key=lambda x: (-len(x['matched_fields']), x['name']))
            
            return results
            
        except Exception as e:
            raise TemplateManagerError(f"Search failed: {e}")
    
    def validate_template_name(self, name: str) -> bool:
        """
        Validate template name format.
        
        Args:
            name: Template name to validate
            
        Returns:
            True if name is valid
            
        Raises:
            TemplateValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise TemplateValidationError("Template name cannot be empty")
        
        name = name.strip()
        
        # Check length
        if len(name) > 100:
            raise TemplateValidationError("Template name cannot exceed 100 characters")
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                raise TemplateValidationError(f"Template name cannot contain '{char}'")
        
        # Check for reserved names
        reserved_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 
                         'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 
                         'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
        
        if name.lower() in reserved_names:
            raise TemplateValidationError(f"Template name '{name}' is reserved")
        
        return True
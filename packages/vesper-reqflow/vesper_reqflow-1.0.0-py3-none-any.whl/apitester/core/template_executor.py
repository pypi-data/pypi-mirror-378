"""Template executor with parameter override and variable substitution."""

import re
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime

from .template_manager import TemplateManager, TemplateNotFoundError, TemplateManagerError
from .http_client import HTTPClient, HTTPResponse
from .graphql_client import GraphQLClient, GraphQLResponse
from .request_validator import RequestValidator, ValidationError
from ..storage.models import RequestTemplate, RequestRecord, HTTPMethod
from ..storage.operations import EnvironmentOperations


logger = logging.getLogger(__name__)


class TemplateExecutionError(Exception):
    """Raised when template execution fails."""
    pass


class VariableSubstitutionError(Exception):
    """Raised when variable substitution fails."""
    pass


class TemplateExecutor:
    """Executes templates with parameter overrides and variable substitution."""
    
    def __init__(self, http_client: Optional[HTTPClient] = None,
                 graphql_client: Optional[GraphQLClient] = None):
        self.template_manager = TemplateManager()
        self.env_ops = EnvironmentOperations()
        self.validator = RequestValidator()
        self.http_client = http_client or HTTPClient()
        self.graphql_client = graphql_client or GraphQLClient(self.http_client)
        
        # Variable substitution pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
        self.variable_pattern = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')
    
    def substitute_variables(self, text: str, environment: str = "default",
                           custom_variables: Optional[Dict[str, str]] = None) -> str:
        """
        Substitute variables in text using environment variables and custom variables.
        
        Args:
            text: Text containing variables to substitute
            environment: Environment name for variable lookup
            custom_variables: Additional variables to use for substitution
            
        Returns:
            Text with variables substituted
            
        Raises:
            VariableSubstitutionError: If required variables are missing
        """
        if not text:
            return text
        
        # Combine environment variables with custom variables
        variables = {}
        
        # Load environment variables
        try:
            env = self.env_ops.load_environment(environment)
            if env:
                variables.update(env.variables)
        except Exception as e:
            logger.warning(f"Failed to load environment '{environment}': {e}")
        
        # Add custom variables (override environment variables)
        if custom_variables:
            variables.update(custom_variables)
        
        # Track missing variables
        missing_variables = []
        
        def replace_variable(match):
            var_name = match.group(1)
            default_value = match.group(2)
            
            if var_name in variables:
                return variables[var_name]
            elif default_value is not None:
                return default_value
            else:
                missing_variables.append(var_name)
                return match.group(0)  # Return original if not found
        
        # Perform substitution
        result = self.variable_pattern.sub(replace_variable, text)
        
        # Check for missing variables
        if missing_variables:
            raise VariableSubstitutionError(
                f"Missing variables: {', '.join(missing_variables)}. "
                f"Available variables: {', '.join(variables.keys()) if variables else 'none'}"
            )
        
        return result
    
    def substitute_variables_in_dict(self, data: Dict[str, Any], environment: str = "default",
                                   custom_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Substitute variables in dictionary values.
        
        Args:
            data: Dictionary with values that may contain variables
            environment: Environment name for variable lookup
            custom_variables: Additional variables to use for substitution
            
        Returns:
            Dictionary with variables substituted
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.substitute_variables(value, environment, custom_variables)
            elif isinstance(value, dict):
                result[key] = self.substitute_variables_in_dict(value, environment, custom_variables)
            elif isinstance(value, list):
                result[key] = [
                    self.substitute_variables(item, environment, custom_variables) 
                    if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def apply_template_overrides(self, template: RequestTemplate,
                               method: Optional[str] = None,
                               url: Optional[str] = None,
                               headers: Optional[Dict[str, str]] = None,
                               body: Optional[str] = None,
                               params: Optional[Dict[str, str]] = None) -> RequestTemplate:
        """
        Apply parameter overrides to a template.
        
        Args:
            template: Base template
            method: Override HTTP method
            url: Override URL
            headers: Override/merge headers
            body: Override body
            params: Override/merge parameters
            
        Returns:
            New RequestTemplate with overrides applied
            
        Raises:
            ValidationError: If overrides are invalid
        """
        # Create a copy of the template
        overridden = RequestTemplate(
            name=template.name,
            method=template.method,
            url=template.url,
            headers=template.headers.copy(),
            body=template.body,
            params=template.params.copy(),
            description=template.description,
            tags=template.tags.copy(),
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
        # Apply overrides
        if method is not None:
            overridden.method = self.validator.validate_method(method)
        
        if url is not None:
            overridden.url = self.validator.validate_url(url)
        
        if headers is not None:
            # Merge headers (override existing ones)
            validated_headers = self.validator.validate_headers(headers)
            overridden.headers.update(validated_headers)
        
        if body is not None:
            content_type = overridden.headers.get('Content-Type')
            overridden.body = self.validator.validate_body(body, overridden.method.value, content_type) or ""
        
        if params is not None:
            # Merge parameters (override existing ones)
            validated_params = self.validator.validate_params(params)
            overridden.params.update(validated_params)
        
        return overridden
    
    def prepare_template_for_execution(self, template_name: str,
                                     environment: str = "default",
                                     custom_variables: Optional[Dict[str, str]] = None,
                                     method: Optional[str] = None,
                                     url: Optional[str] = None,
                                     headers: Optional[Dict[str, str]] = None,
                                     body: Optional[str] = None,
                                     params: Optional[Dict[str, str]] = None) -> RequestTemplate:
        """
        Prepare template for execution with overrides and variable substitution.
        
        Args:
            template_name: Name of template to execute
            environment: Environment for variable substitution
            custom_variables: Additional variables for substitution
            method: Override HTTP method
            url: Override URL
            headers: Override/merge headers
            body: Override body
            params: Override/merge parameters
            
        Returns:
            Prepared RequestTemplate ready for execution
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
            VariableSubstitutionError: If variable substitution fails
            ValidationError: If overrides are invalid
        """
        # Load template
        template = self.template_manager.load_template(template_name)
        
        # Apply overrides first
        if any([method, url, headers, body, params]):
            template = self.apply_template_overrides(template, method, url, headers, body, params)
        
        # Perform variable substitution
        try:
            # Substitute in URL
            template.url = self.substitute_variables(template.url, environment, custom_variables)
            
            # Substitute in headers
            template.headers = self.substitute_variables_in_dict(template.headers, environment, custom_variables)
            
            # Substitute in body
            if template.body:
                # Handle case where body might be a dict (due to deserialization issues)
                if isinstance(template.body, dict):
                    import json
                    template.body = json.dumps(template.body)
                template.body = self.substitute_variables(template.body, environment, custom_variables)
            
            # Substitute in parameters
            template.params = self.substitute_variables_in_dict(template.params, environment, custom_variables)
            
        except VariableSubstitutionError as e:
            raise VariableSubstitutionError(f"Variable substitution failed for template '{template_name}': {e}")
        
        return template
    
    def execute_template(self, template_name: str,
                        environment: str = "default",
                        custom_variables: Optional[Dict[str, str]] = None,
                        method: Optional[str] = None,
                        url: Optional[str] = None,
                        headers: Optional[Dict[str, str]] = None,
                        body: Optional[str] = None,
                        params: Optional[Dict[str, str]] = None,
                        max_retries: int = 3,
                        is_graphql: bool = False) -> Union[HTTPResponse, GraphQLResponse]:
        """
        Execute a template with overrides and variable substitution.
        
        Args:
            template_name: Name of template to execute
            environment: Environment for variable substitution
            custom_variables: Additional variables for substitution
            method: Override HTTP method
            url: Override URL
            headers: Override/merge headers
            body: Override body
            params: Override/merge parameters
            max_retries: Maximum retry attempts
            is_graphql: Whether to execute as GraphQL request
            
        Returns:
            HTTP or GraphQL response
            
        Raises:
            TemplateExecutionError: If execution fails
        """
        try:
            # Prepare template
            prepared_template = self.prepare_template_for_execution(
                template_name, environment, custom_variables,
                method, url, headers, body, params
            )
            
            logger.info(f"Executing template '{template_name}' ({prepared_template.method.value} {prepared_template.url})")
            
            # Execute request
            if is_graphql:
                # For GraphQL, the body should contain the query
                if not prepared_template.body:
                    raise TemplateExecutionError("GraphQL template must have a query in the body")
                
                # Try to parse GraphQL query and variables
                graphql_data = self._parse_graphql_body(prepared_template.body)
                
                response = self.graphql_client.send_query(
                    url=prepared_template.url,
                    query=graphql_data['query'],
                    variables=graphql_data.get('variables'),
                    headers=prepared_template.headers,
                    operation_name=graphql_data.get('operationName'),
                    max_retries=max_retries
                )
            else:
                # Regular HTTP request
                response = self.http_client.send_request(
                    method=prepared_template.method.value,
                    url=prepared_template.url,
                    headers=prepared_template.headers,
                    body=prepared_template.body,
                    params=prepared_template.params,
                    max_retries=max_retries
                )
            
            logger.info(f"Template '{template_name}' executed successfully (status: {response.status_code})")
            return response
            
        except (TemplateNotFoundError, VariableSubstitutionError, ValidationError) as e:
            raise TemplateExecutionError(str(e))
        except Exception as e:
            raise TemplateExecutionError(f"Failed to execute template '{template_name}': {e}")
    
    def _parse_graphql_body(self, body: str) -> Dict[str, Any]:
        """
        Parse GraphQL request body.
        
        Args:
            body: Request body (JSON or plain GraphQL query)
            
        Returns:
            Dictionary with query, variables, and operationName
        """
        import json
        
        # Try to parse as JSON first (standard GraphQL request format)
        try:
            data = json.loads(body)
            if isinstance(data, dict) and 'query' in data:
                return data
        except json.JSONDecodeError:
            pass
        
        # Treat as plain GraphQL query
        return {'query': body.strip()}
    
    def execute_template_batch(self, template_configs: List[Dict[str, Any]],
                             environment: str = "default",
                             stop_on_error: bool = False) -> List[Dict[str, Any]]:
        """
        Execute multiple templates in batch.
        
        Args:
            template_configs: List of template execution configurations
            environment: Default environment for all templates
            stop_on_error: Whether to stop execution on first error
            
        Returns:
            List of execution results with responses and metadata
            
        Each template_config should contain:
            - template_name: str
            - custom_variables: Optional[Dict[str, str]]
            - overrides: Optional[Dict[str, Any]] (method, url, headers, body, params)
            - is_graphql: Optional[bool]
        """
        results = []
        
        for i, config in enumerate(template_configs):
            template_name = config.get('template_name')
            if not template_name:
                error_result = {
                    'index': i,
                    'template_name': None,
                    'success': False,
                    'error': 'Missing template_name in configuration',
                    'response': None,
                    'execution_time': 0
                }
                results.append(error_result)
                
                if stop_on_error:
                    break
                continue
            
            try:
                start_time = datetime.now()
                
                # Extract configuration
                custom_variables = config.get('custom_variables')
                overrides = config.get('overrides', {})
                is_graphql = config.get('is_graphql', False)
                
                # Execute template
                response = self.execute_template(
                    template_name=template_name,
                    environment=environment,
                    custom_variables=custom_variables,
                    is_graphql=is_graphql,
                    **overrides
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                result = {
                    'index': i,
                    'template_name': template_name,
                    'success': True,
                    'error': None,
                    'response': response,
                    'execution_time': execution_time
                }
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                
                result = {
                    'index': i,
                    'template_name': template_name,
                    'success': False,
                    'error': str(e),
                    'response': None,
                    'execution_time': execution_time
                }
                
                if stop_on_error:
                    results.append(result)
                    break
            
            results.append(result)
        
        return results
    
    def create_request_record_from_template(self, template_name: str, response: Union[HTTPResponse, GraphQLResponse],
                                          environment: str = "default",
                                          error_message: str = "") -> RequestRecord:
        """
        Create request record from template execution.
        
        Args:
            template_name: Name of executed template
            response: Response object (if successful)
            environment: Environment used
            error_message: Error message (if failed)
            
        Returns:
            RequestRecord instance
        """
        try:
            template = self.template_manager.load_template(template_name)
            
            return RequestRecord(
                timestamp=datetime.now(),
                method=template.method,
                url=template.url,
                headers=template.headers,
                body=template.body,
                params=template.params,
                response_status=response.status_code if response else 0,
                response_headers=response.headers if response else {},
                response_body=response.text if hasattr(response, 'text') else "",
                response_time=response.request_time if response else 0.0,
                error_message=error_message,
                template_name=template_name,
                environment=environment
            )
            
        except Exception as e:
            logger.error(f"Failed to create request record for template '{template_name}': {e}")
            # Return minimal record
            return RequestRecord(
                timestamp=datetime.now(),
                method=HTTPMethod.GET,
                url="unknown",
                template_name=template_name,
                environment=environment,
                error_message=error_message or str(e)
            )
    
    def extract_variables_from_template(self, template_name: str) -> List[str]:
        """
        Extract variable names used in a template.
        
        Args:
            template_name: Template name
            
        Returns:
            List of variable names found in the template
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        template = self.template_manager.load_template(template_name)
        
        variables = set()
        
        # Extract from URL
        variables.update(self._extract_variables_from_text(template.url))
        
        # Extract from headers
        for value in template.headers.values():
            variables.update(self._extract_variables_from_text(value))
        
        # Extract from body
        if template.body:
            variables.update(self._extract_variables_from_text(template.body))
        
        # Extract from parameters
        for value in template.params.values():
            variables.update(self._extract_variables_from_text(value))
        
        return sorted(list(variables))
    
    def _extract_variables_from_text(self, text: str) -> List[str]:
        """Extract variable names from text."""
        if not text:
            return []
        
        matches = self.variable_pattern.findall(text)
        return [match[0] for match in matches]
    
    def validate_template_variables(self, template_name: str, environment: str = "default",
                                  custom_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate that all variables in template can be resolved.
        
        Args:
            template_name: Template name
            environment: Environment for variable lookup
            custom_variables: Additional variables
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Extract variables from template
            template_variables = self.extract_variables_from_template(template_name)
            
            if not template_variables:
                return {
                    'valid': True,
                    'variables_found': [],
                    'missing_variables': [],
                    'available_variables': []
                }
            
            # Get available variables
            available_variables = {}
            
            # Load environment variables
            try:
                env = self.env_ops.load_environment(environment)
                if env:
                    available_variables.update(env.variables)
            except Exception:
                pass
            
            # Add custom variables
            if custom_variables:
                available_variables.update(custom_variables)
            
            # Check which variables are missing
            missing_variables = []
            for var in template_variables:
                if var not in available_variables:
                    missing_variables.append(var)
            
            return {
                'valid': len(missing_variables) == 0,
                'variables_found': template_variables,
                'missing_variables': missing_variables,
                'available_variables': list(available_variables.keys())
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'variables_found': [],
                'missing_variables': [],
                'available_variables': []
            }
"""GraphQL client for executing queries and mutations."""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .http_client import HTTPClient, HTTPResponse, RequestValidationError


logger = logging.getLogger(__name__)


class GraphQLError(Exception):
    """Base exception for GraphQL-related errors."""
    pass


class GraphQLValidationError(GraphQLError):
    """Raised when GraphQL query validation fails."""
    pass


class GraphQLExecutionError(GraphQLError):
    """Raised when GraphQL query execution fails."""
    pass


class GraphQLResponse:
    """Wrapper for GraphQL response with error handling."""
    
    def __init__(self, http_response: HTTPResponse):
        self.http_response = http_response
        self._parsed_data = None
        self._parse_response()
    
    def _parse_response(self) -> None:
        """Parse GraphQL response from HTTP response."""
        try:
            self._parsed_data = self.http_response.json()
        except ValueError as e:
            raise GraphQLExecutionError(f"Invalid JSON response: {e}")
        
        if not isinstance(self._parsed_data, dict):
            raise GraphQLExecutionError("GraphQL response must be a JSON object")
    
    @property
    def data(self) -> Optional[Any]:
        """Get response data."""
        return self._parsed_data.get('data')
    
    @property
    def errors(self) -> Optional[List[Dict[str, Any]]]:
        """Get response errors."""
        return self._parsed_data.get('errors')
    
    @property
    def extensions(self) -> Optional[Dict[str, Any]]:
        """Get response extensions."""
        return self._parsed_data.get('extensions')
    
    @property
    def status_code(self) -> int:
        """Get HTTP status code."""
        return self.http_response.status_code
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP response headers."""
        return self.http_response.headers
    
    @property
    def request_time(self) -> float:
        """Get request execution time."""
        return self.http_response.request_time
    
    @property
    def from_cache(self) -> bool:
        """Check if response came from cache."""
        return self.http_response.from_cache
    
    def has_errors(self) -> bool:
        """Check if response contains GraphQL errors."""
        return self.errors is not None and len(self.errors) > 0
    
    def is_success(self) -> bool:
        """Check if GraphQL query was successful."""
        return self.http_response.is_success() and not self.has_errors()
    
    def get_error_messages(self) -> List[str]:
        """Get list of error messages."""
        if not self.has_errors():
            return []
        
        messages = []
        for error in self.errors:
            message = error.get('message', 'Unknown GraphQL error')
            
            # Add location information if available
            locations = error.get('locations', [])
            if locations:
                location_info = []
                for loc in locations:
                    line = loc.get('line')
                    column = loc.get('column')
                    if line is not None and column is not None:
                        location_info.append(f"line {line}, column {column}")
                
                if location_info:
                    message += f" (at {', '.join(location_info)})"
            
            # Add path information if available
            path = error.get('path')
            if path:
                message += f" (path: {'.'.join(str(p) for p in path)})"
            
            messages.append(message)
        
        return messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return self._parsed_data


class GraphQLClient:
    """Client for executing GraphQL queries and mutations."""
    
    def __init__(self, http_client: Optional[HTTPClient] = None):
        self.http_client = http_client or HTTPClient()
    
    def validate_query(self, query: str) -> None:
        """
        Validate GraphQL query syntax.
        
        Args:
            query: GraphQL query string
            
        Raises:
            GraphQLValidationError: If query is invalid
        """
        if not query or not query.strip():
            raise GraphQLValidationError("GraphQL query cannot be empty")
        
        query = query.strip()
        
        # Basic syntax validation
        if not (query.startswith(('query', 'mutation', 'subscription', '{'))):
            raise GraphQLValidationError(
                "GraphQL query must start with 'query', 'mutation', 'subscription', or '{'"
            )
        
        # Check for balanced braces
        brace_count = 0
        in_string = False
        escape_next = False
        
        for char in query:
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count < 0:
                        raise GraphQLValidationError("Unmatched closing brace in GraphQL query")
        
        if brace_count != 0:
            raise GraphQLValidationError("Unmatched braces in GraphQL query")
        
        if in_string:
            raise GraphQLValidationError("Unterminated string in GraphQL query")
    
    def validate_variables(self, variables: Optional[Dict[str, Any]]) -> None:
        """
        Validate GraphQL variables.
        
        Args:
            variables: Variables dictionary
            
        Raises:
            GraphQLValidationError: If variables are invalid
        """
        if variables is None:
            return
        
        if not isinstance(variables, dict):
            raise GraphQLValidationError("GraphQL variables must be a dictionary")
        
        # Validate that variables can be JSON serialized
        try:
            json.dumps(variables)
        except (TypeError, ValueError) as e:
            raise GraphQLValidationError(f"GraphQL variables must be JSON serializable: {e}")
    
    def extract_operation_name(self, query: str) -> Optional[str]:
        """
        Extract operation name from GraphQL query.
        
        Args:
            query: GraphQL query string
            
        Returns:
            Operation name or None if not found
        """
        # Look for named operations like "query GetUser" or "mutation CreateUser"
        pattern = r'(?:query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)'
        match = re.search(pattern, query.strip())
        
        if match:
            return match.group(1)
        
        return None
    
    def send_query(self, url: str, query: str, variables: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, 
                   operation_name: Optional[str] = None,
                   max_retries: int = 3) -> GraphQLResponse:
        """
        Send GraphQL query.
        
        Args:
            url: GraphQL endpoint URL
            query: GraphQL query string
            variables: Query variables
            headers: HTTP headers
            operation_name: Operation name (optional)
            max_retries: Maximum retry attempts
            
        Returns:
            GraphQLResponse object
            
        Raises:
            GraphQLValidationError: If query or variables are invalid
            GraphQLExecutionError: If query execution fails
        """
        # Validate inputs
        self.validate_query(query)
        self.validate_variables(variables)
        
        # Prepare GraphQL request payload
        payload = {
            'query': query.strip()
        }
        
        if variables:
            payload['variables'] = variables
        
        if operation_name:
            payload['operationName'] = operation_name
        elif not operation_name:
            # Try to extract operation name from query
            extracted_name = self.extract_operation_name(query)
            if extracted_name:
                payload['operationName'] = extracted_name
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if headers:
            request_headers.update(headers)
        
        # Convert payload to JSON
        try:
            body = json.dumps(payload, indent=None, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            raise GraphQLValidationError(f"Failed to serialize GraphQL request: {e}")
        
        logger.info(f"Sending GraphQL query to {url}")
        logger.debug(f"GraphQL payload: {payload}")
        
        try:
            # Send HTTP POST request
            http_response = self.http_client.send_request(
                method='POST',
                url=url,
                headers=request_headers,
                body=body,
                max_retries=max_retries
            )
            
            # Wrap in GraphQL response
            graphql_response = GraphQLResponse(http_response)
            
            # Log results
            if graphql_response.is_success():
                logger.info(f"GraphQL query successful in {graphql_response.request_time:.3f}s")
            else:
                if graphql_response.has_errors():
                    error_messages = graphql_response.get_error_messages()
                    logger.warning(f"GraphQL query returned errors: {'; '.join(error_messages)}")
                else:
                    logger.warning(f"GraphQL query failed with HTTP {graphql_response.status_code}")
            
            return graphql_response
            
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            raise GraphQLExecutionError(f"Failed to execute GraphQL query: {e}")
    
    def send_query_from_file(self, url: str, query_file: Union[str, Path],
                            variables: Optional[Dict[str, Any]] = None,
                            headers: Optional[Dict[str, str]] = None,
                            operation_name: Optional[str] = None,
                            max_retries: int = 3) -> GraphQLResponse:
        """
        Send GraphQL query from file.
        
        Args:
            url: GraphQL endpoint URL
            query_file: Path to file containing GraphQL query
            variables: Query variables
            headers: HTTP headers
            operation_name: Operation name (optional)
            max_retries: Maximum retry attempts
            
        Returns:
            GraphQLResponse object
            
        Raises:
            FileNotFoundError: If query file doesn't exist
            GraphQLValidationError: If query is invalid
        """
        query_path = Path(query_file)
        
        if not query_path.exists():
            raise FileNotFoundError(f"GraphQL query file not found: {query_file}")
        
        try:
            query = query_path.read_text(encoding='utf-8')
            logger.debug(f"Loaded GraphQL query from {query_file}")
            
            return self.send_query(url, query, variables, headers, operation_name, max_retries)
            
        except UnicodeDecodeError as e:
            raise GraphQLValidationError(f"Failed to read query file as UTF-8: {e}")
    
    def send_mutation(self, url: str, mutation: str, variables: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     operation_name: Optional[str] = None,
                     max_retries: int = 3) -> GraphQLResponse:
        """
        Send GraphQL mutation (alias for send_query).
        
        Args:
            url: GraphQL endpoint URL
            mutation: GraphQL mutation string
            variables: Mutation variables
            headers: HTTP headers
            operation_name: Operation name (optional)
            max_retries: Maximum retry attempts
            
        Returns:
            GraphQLResponse object
        """
        return self.send_query(url, mutation, variables, headers, operation_name, max_retries)
    
    def introspect_schema(self, url: str, headers: Optional[Dict[str, str]] = None,
                         max_retries: int = 3) -> GraphQLResponse:
        """
        Perform GraphQL schema introspection.
        
        Args:
            url: GraphQL endpoint URL
            headers: HTTP headers
            max_retries: Maximum retry attempts
            
        Returns:
            GraphQLResponse with schema information
        """
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args {
                ...InputValue
              }
            }
          }
        }
        
        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }
        
        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
        }
        
        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        return self.send_query(url, introspection_query, headers=headers, 
                              operation_name="IntrospectionQuery", max_retries=max_retries)


# Utility functions for GraphQL

def format_graphql_query(query: str) -> str:
    """
    Format GraphQL query for better readability.
    
    Args:
        query: GraphQL query string
        
    Returns:
        Formatted query string
    """
    # This is a basic formatter. For production use,
    # consider using a dedicated GraphQL formatter library
    
    lines = []
    indent_level = 0
    in_string = False
    
    for char in query:
        if char == '"' and (not lines or lines[-1][-1:] != '\\'):
            in_string = not in_string
        
        if not in_string:
            if char == '{':
                lines.append('  ' * indent_level + char)
                indent_level += 1
            elif char == '}':
                indent_level = max(0, indent_level - 1)
                lines.append('  ' * indent_level + char)
            elif char == '\n':
                continue  # Skip existing newlines
            else:
                if lines and not lines[-1].endswith(' ') and char != ' ':
                    lines.append(char)
                elif char != ' ' or (lines and not lines[-1].endswith(' ')):
                    lines.append(char)
        else:
            lines.append(char)
    
    return ''.join(lines)


def extract_graphql_variables_from_query(query: str) -> List[str]:
    """
    Extract variable names from GraphQL query.
    
    Args:
        query: GraphQL query string
        
    Returns:
        List of variable names
    """
    # Find variable declarations like $variableName: Type
    pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)\s*:'
    matches = re.findall(pattern, query)
    
    return list(set(matches))  # Remove duplicates


def validate_graphql_variables_against_query(query: str, variables: Dict[str, Any]) -> List[str]:
    """
    Validate that provided variables match query requirements.
    
    Args:
        query: GraphQL query string
        variables: Variables dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Extract required variables from query
    query_variables = extract_graphql_variables_from_query(query)
    
    # Check for missing variables
    for var_name in query_variables:
        if var_name not in variables:
            errors.append(f"Missing required variable: ${var_name}")
    
    # Check for unused variables
    for var_name in variables:
        if var_name not in query_variables:
            errors.append(f"Unused variable: ${var_name}")
    
    return errors
"""AI integrations for enhanced API testing functionality."""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
from pathlib import Path

from .assistant import AIAssistant, AIResponse, AIAssistantError
from ..core.http_client import HTTPResponse


class HeaderSuggestionEngine:
    """AI-powered header suggestion engine."""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
        self._common_patterns = self._load_common_patterns()
    
    def _load_common_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load common header patterns for different API types."""
        return {
            "github.com": {
                "Authorization": "Bearer ${GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "API-Tester/1.0"
            },
            "api.twitter.com": {
                "Authorization": "Bearer ${TWITTER_TOKEN}",
                "Content-Type": "application/json"
            },
            "graph.facebook.com": {
                "Authorization": "Bearer ${FACEBOOK_TOKEN}",
                "Content-Type": "application/json"
            },
            "googleapis.com": {
                "Authorization": "Bearer ${GOOGLE_TOKEN}",
                "Content-Type": "application/json"
            },
            "api.stripe.com": {
                "Authorization": "Bearer ${STRIPE_SECRET_KEY}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "api.slack.com": {
                "Authorization": "Bearer ${SLACK_TOKEN}",
                "Content-Type": "application/json"
            }
        }
    
    def suggest_headers(self, url: str, method: str = "GET", use_ai: bool = True) -> Dict[str, str]:
        """Suggest headers for a request URL."""
        headers = {}
        
        # Start with pattern-based suggestions
        domain = urlparse(url).netloc.lower()
        for pattern, pattern_headers in self._common_patterns.items():
            if pattern in domain:
                headers.update(pattern_headers)
                break
        
        # Add method-specific headers
        if method.upper() in ["POST", "PUT", "PATCH"]:
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        
        # Add common headers
        if "Accept" not in headers:
            headers["Accept"] = "application/json"
        if "User-Agent" not in headers:
            headers["User-Agent"] = "API-Tester/1.0"
        
        # Use AI for additional suggestions if available and enabled
        if use_ai and self.ai_assistant.is_available():
            try:
                ai_response = self.ai_assistant.suggest_headers(url, method)
                ai_headers = self._extract_headers_from_ai_response(ai_response)
                
                # Merge AI suggestions (don't override existing)
                for key, value in ai_headers.items():
                    if key not in headers:
                        headers[key] = value
                        
            except AIAssistantError:
                pass  # Fall back to pattern-based suggestions
        
        return headers
    
    def _extract_headers_from_ai_response(self, ai_response: AIResponse) -> Dict[str, str]:
        """Extract headers from AI response."""
        try:
            content = ai_response.content.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                headers_list = json.loads(json_match.group())
                return {item.get('header', ''): item.get('value', '') 
                       for item in headers_list 
                       if isinstance(item, dict) and 'header' in item and 'value' in item}
            
            # Fallback: parse header-like lines
            headers = {}
            for line in content.split('\n'):
                if ':' in line and not line.strip().startswith(('#', '//', '/*')):
                    try:
                        key, value = line.split(':', 1)
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        if key and value:
                            headers[key] = value
                    except ValueError:
                        continue
            
            return headers
            
        except Exception:
            return {}


class StatusCodeExplainer:
    """AI-powered HTTP status code explanation."""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
        self._status_code_info = self._load_status_code_info()
    
    def _load_status_code_info(self) -> Dict[int, Dict[str, str]]:
        """Load basic status code information."""
        return {
            200: {"category": "Success", "meaning": "OK - Request successful"},
            201: {"category": "Success", "meaning": "Created - Resource created successfully"},
            204: {"category": "Success", "meaning": "No Content - Request successful, no response body"},
            400: {"category": "Client Error", "meaning": "Bad Request - Invalid request syntax or parameters"},
            401: {"category": "Client Error", "meaning": "Unauthorized - Authentication required or failed"},
            403: {"category": "Client Error", "meaning": "Forbidden - Access denied"},
            404: {"category": "Client Error", "meaning": "Not Found - Resource not found"},
            405: {"category": "Client Error", "meaning": "Method Not Allowed - HTTP method not supported"},
            409: {"category": "Client Error", "meaning": "Conflict - Request conflicts with current state"},
            422: {"category": "Client Error", "meaning": "Unprocessable Entity - Request syntax valid but semantically incorrect"},
            429: {"category": "Client Error", "meaning": "Too Many Requests - Rate limit exceeded"},
            500: {"category": "Server Error", "meaning": "Internal Server Error - Server encountered an error"},
            502: {"category": "Server Error", "meaning": "Bad Gateway - Invalid response from upstream server"},
            503: {"category": "Server Error", "meaning": "Service Unavailable - Server temporarily unavailable"},
            504: {"category": "Server Error", "meaning": "Gateway Timeout - Upstream server timeout"}
        }
    
    def explain_status_code(self, status_code: int, response_body: str = None, use_ai: bool = True) -> Dict[str, Any]:
        """Explain HTTP status code with context."""
        explanation = {
            "status_code": status_code,
            "category": "Unknown",
            "meaning": f"HTTP {status_code}",
            "suggestions": [],
            "ai_explanation": None
        }
        
        # Get basic info
        if status_code in self._status_code_info:
            info = self._status_code_info[status_code]
            explanation["category"] = info["category"]
            explanation["meaning"] = info["meaning"]
        
        # Add basic suggestions
        explanation["suggestions"] = self._get_basic_suggestions(status_code)
        
        # Use AI for detailed explanation if available
        if use_ai and self.ai_assistant.is_available():
            try:
                ai_response = self.ai_assistant.explain_status_code(status_code, response_body)
                explanation["ai_explanation"] = ai_response.content
                
                # Extract additional suggestions from AI response
                ai_suggestions = self._extract_suggestions_from_ai_response(ai_response)
                explanation["suggestions"].extend(ai_suggestions)
                
            except AIAssistantError:
                pass  # Fall back to basic explanation
        
        return explanation
    
    def _get_basic_suggestions(self, status_code: int) -> List[str]:
        """Get basic troubleshooting suggestions for status codes."""
        suggestions = []
        
        if status_code == 400:
            suggestions = [
                "Check request syntax and parameters",
                "Verify Content-Type header matches request body",
                "Validate JSON structure if sending JSON"
            ]
        elif status_code == 401:
            suggestions = [
                "Check authentication credentials",
                "Verify API key or token is valid",
                "Ensure Authorization header is properly formatted"
            ]
        elif status_code == 403:
            suggestions = [
                "Verify you have permission to access this resource",
                "Check if API key has required scopes",
                "Ensure you're not hitting rate limits"
            ]
        elif status_code == 404:
            suggestions = [
                "Verify the URL is correct",
                "Check if the resource exists",
                "Ensure the endpoint path is valid"
            ]
        elif status_code == 429:
            suggestions = [
                "Wait before retrying the request",
                "Check rate limit headers for retry timing",
                "Consider implementing exponential backoff"
            ]
        elif status_code >= 500:
            suggestions = [
                "Retry the request after a short delay",
                "Check if the service is experiencing issues",
                "Contact API support if problem persists"
            ]
        
        return suggestions
    
    def _extract_suggestions_from_ai_response(self, ai_response: AIResponse) -> List[str]:
        """Extract suggestions from AI response."""
        suggestions = []
        content = ai_response.content
        
        # Look for numbered lists
        for line in content.split('\n'):
            line = line.strip()
            if re.match(r'^\d+\.\s+', line):
                suggestion = re.sub(r'^\d+\.\s+', '', line)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Look for bullet points if no numbered list found
        if not suggestions:
            for line in content.split('\n'):
                line = line.strip()
                if re.match(r'^[-*•]\s+', line):
                    suggestion = re.sub(r'^[-*•]\s+', '', line)
                    if suggestion:
                        suggestions.append(suggestion)
        
        return suggestions[:5]  # Limit to 5 suggestions


class JSONValidator:
    """AI-powered JSON validation and suggestion engine."""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
    
    def validate_json(self, json_data: str, expected_schema: str = None, use_ai: bool = True) -> Dict[str, Any]:
        """Validate JSON structure and provide suggestions."""
        result = {
            "valid": False,
            "errors": [],
            "suggestions": [],
            "ai_analysis": None
        }
        
        # Basic JSON validation
        try:
            parsed_data = json.loads(json_data)
            result["valid"] = True
            result["parsed_data"] = parsed_data
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON syntax error: {e}")
            result["suggestions"].append("Check for missing commas, quotes, or brackets")
        
        # Use AI for advanced validation if available
        if use_ai and self.ai_assistant.is_available():
            try:
                ai_response = self.ai_assistant.validate_json_structure(json_data, expected_schema)
                result["ai_analysis"] = ai_response.content
                
                # Extract suggestions from AI response
                ai_suggestions = self._extract_suggestions_from_ai_response(ai_response)
                result["suggestions"].extend(ai_suggestions)
                
            except AIAssistantError:
                pass  # Fall back to basic validation
        
        return result
    
    def _extract_suggestions_from_ai_response(self, ai_response: AIResponse) -> List[str]:
        """Extract suggestions from AI response."""
        suggestions = []
        content = ai_response.content
        
        # Look for suggestion sections
        suggestion_patterns = [
            r'suggestions?:?\s*\n(.*?)(?:\n\n|\Z)',
            r'improvements?:?\s*\n(.*?)(?:\n\n|\Z)',
            r'recommendations?:?\s*\n(.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in suggestion_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                suggestion_text = match.group(1)
                for line in suggestion_text.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                        clean_line = re.sub(r'^[-*\d.]\s*', '', line)
                        if clean_line:
                            suggestions.append(clean_line)
                break
        
        return suggestions[:5]  # Limit to 5 suggestions


class OpenAPIIntegration:
    """AI-powered OpenAPI/Swagger integration."""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
    
    def generate_request_examples(self, openapi_spec: str, endpoint: str = None, use_ai: bool = True) -> Dict[str, Any]:
        """Generate request examples from OpenAPI specification."""
        result = {
            "examples": [],
            "ai_generated": False
        }
        
        # Try to parse OpenAPI spec
        try:
            spec_data = json.loads(openapi_spec) if isinstance(openapi_spec, str) else openapi_spec
            
            # Extract basic examples from spec
            basic_examples = self._extract_basic_examples(spec_data, endpoint)
            result["examples"].extend(basic_examples)
            
        except (json.JSONDecodeError, KeyError):
            pass  # Fall back to AI generation
        
        # Use AI to generate additional examples if available
        if use_ai and self.ai_assistant.is_available():
            try:
                ai_response = self.ai_assistant.generate_request_examples(openapi_spec, endpoint)
                ai_examples = self._extract_examples_from_ai_response(ai_response)
                result["examples"].extend(ai_examples)
                result["ai_generated"] = True
                
            except AIAssistantError:
                pass  # Use basic examples only
        
        return result
    
    def _extract_basic_examples(self, spec_data: Dict[str, Any], endpoint: str = None) -> List[Dict[str, Any]]:
        """Extract basic examples from OpenAPI specification."""
        examples = []
        
        try:
            paths = spec_data.get("paths", {})
            base_url = self._get_base_url(spec_data)
            
            for path, path_data in paths.items():
                if endpoint and endpoint not in path:
                    continue
                
                for method, method_data in path_data.items():
                    if method.lower() in ["get", "post", "put", "patch", "delete"]:
                        example = {
                            "method": method.upper(),
                            "url": f"{base_url}{path}",
                            "description": method_data.get("summary", f"{method.upper()} {path}"),
                            "headers": {},
                            "parameters": []
                        }
                        
                        # Extract parameters
                        parameters = method_data.get("parameters", [])
                        for param in parameters:
                            example["parameters"].append({
                                "name": param.get("name"),
                                "in": param.get("in"),
                                "required": param.get("required", False),
                                "example": param.get("example", f"<{param.get('name', 'value')}>")
                            })
                        
                        # Extract request body example
                        request_body = method_data.get("requestBody", {})
                        if request_body:
                            content = request_body.get("content", {})
                            for content_type, content_data in content.items():
                                example["headers"]["Content-Type"] = content_type
                                schema = content_data.get("schema", {})
                                if "example" in content_data:
                                    example["body"] = content_data["example"]
                                elif "example" in schema:
                                    example["body"] = schema["example"]
                                break
                        
                        examples.append(example)
        
        except (KeyError, TypeError):
            pass  # Return empty list if parsing fails
        
        return examples
    
    def _get_base_url(self, spec_data: Dict[str, Any]) -> str:
        """Extract base URL from OpenAPI specification."""
        try:
            # OpenAPI 3.x
            servers = spec_data.get("servers", [])
            if servers:
                return servers[0].get("url", "")
            
            # OpenAPI 2.x (Swagger)
            host = spec_data.get("host", "")
            schemes = spec_data.get("schemes", ["https"])
            base_path = spec_data.get("basePath", "")
            
            if host:
                return f"{schemes[0]}://{host}{base_path}"
            
        except (KeyError, TypeError, IndexError):
            pass
        
        return "https://api.example.com"
    
    def _extract_examples_from_ai_response(self, ai_response: AIResponse) -> List[Dict[str, Any]]:
        """Extract examples from AI response."""
        examples = []
        content = ai_response.content
        
        # Look for curl commands
        curl_pattern = r'curl\s+.*?(?=\n\n|\ncurl|\Z)'
        curl_matches = re.findall(curl_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for curl_command in curl_matches:
            example = self._parse_curl_command(curl_command)
            if example:
                examples.append(example)
        
        return examples
    
    def _parse_curl_command(self, curl_command: str) -> Optional[Dict[str, Any]]:
        """Parse curl command into structured example."""
        try:
            # Extract method
            method_match = re.search(r'-X\s+(\w+)', curl_command)
            method = method_match.group(1) if method_match else "GET"
            
            # Extract URL
            url_match = re.search(r'curl\s+.*?["\']?(https?://[^\s"\']+)', curl_command)
            if not url_match:
                return None
            url = url_match.group(1)
            
            # Extract headers
            headers = {}
            header_matches = re.findall(r'-H\s+["\']([^"\']+)["\']', curl_command)
            for header in header_matches:
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # Extract body
            body = None
            body_match = re.search(r'-d\s+["\']([^"\']+)["\']', curl_command)
            if body_match:
                body = body_match.group(1)
            
            return {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "description": f"{method} request to {url}"
            }
            
        except Exception:
            return None


class ErrorMessageInterpreter:
    """AI-powered error message interpretation."""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
        self._common_errors = self._load_common_errors()
    
    def _load_common_errors(self) -> Dict[str, Dict[str, Any]]:
        """Load common error patterns and solutions."""
        return {
            "connection_refused": {
                "patterns": ["connection refused", "connection failed", "unable to connect"],
                "causes": ["Server is down", "Wrong host/port", "Firewall blocking"],
                "solutions": ["Check server status", "Verify URL", "Check network connectivity"]
            },
            "timeout": {
                "patterns": ["timeout", "timed out", "request timeout"],
                "causes": ["Server overloaded", "Network issues", "Request too complex"],
                "solutions": ["Increase timeout", "Retry request", "Check server performance"]
            },
            "ssl_error": {
                "patterns": ["ssl error", "certificate", "handshake failed"],
                "causes": ["Invalid certificate", "SSL/TLS version mismatch", "Certificate expired"],
                "solutions": ["Check certificate validity", "Update SSL/TLS settings", "Use --no-verify-ssl for testing"]
            },
            "json_error": {
                "patterns": ["json", "parse error", "invalid json"],
                "causes": ["Malformed JSON", "Wrong Content-Type", "Server returned non-JSON"],
                "solutions": ["Validate JSON syntax", "Check Content-Type header", "Inspect raw response"]
            }
        }
    
    def interpret_error(self, error_message: str, request_context: Dict[str, Any] = None, use_ai: bool = True) -> Dict[str, Any]:
        """Interpret error message and provide solutions."""
        result = {
            "error_type": "unknown",
            "causes": [],
            "solutions": [],
            "ai_interpretation": None
        }
        
        # Pattern-based interpretation
        error_lower = error_message.lower()
        for error_type, error_info in self._common_errors.items():
            for pattern in error_info["patterns"]:
                if pattern in error_lower:
                    result["error_type"] = error_type
                    result["causes"] = error_info["causes"]
                    result["solutions"] = error_info["solutions"]
                    break
            if result["error_type"] != "unknown":
                break
        
        # Use AI for detailed interpretation if available
        if use_ai and self.ai_assistant.is_available():
            try:
                ai_response = self.ai_assistant.interpret_error_message(error_message, request_context)
                result["ai_interpretation"] = ai_response.content
                
                # Extract additional solutions from AI response
                ai_solutions = self._extract_solutions_from_ai_response(ai_response)
                result["solutions"].extend(ai_solutions)
                
            except AIAssistantError:
                pass  # Fall back to pattern-based interpretation
        
        return result
    
    def _extract_solutions_from_ai_response(self, ai_response: AIResponse) -> List[str]:
        """Extract solutions from AI response."""
        solutions = []
        content = ai_response.content
        
        # Look for solution sections
        solution_patterns = [
            r'solutions?:?\s*\n(.*?)(?:\n\n|\Z)',
            r'fixes?:?\s*\n(.*?)(?:\n\n|\Z)',
            r'troubleshooting:?\s*\n(.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                solution_text = match.group(1)
                for line in solution_text.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                        clean_line = re.sub(r'^[-*\d.]\s*', '', line)
                        if clean_line:
                            solutions.append(clean_line)
                break
        
        return solutions[:5]  # Limit to 5 solutions
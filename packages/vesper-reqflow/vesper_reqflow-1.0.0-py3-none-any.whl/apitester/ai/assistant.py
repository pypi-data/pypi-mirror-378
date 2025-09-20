"""AI Assistant base functionality for API testing assistance."""

import json
import re
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from ..config.settings import get_config


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


@dataclass
class AIResponse:
    """Response from AI assistant."""
    content: str
    confidence: float = 0.0
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class AIAssistantError(Exception):
    """Base exception for AI assistant errors."""
    pass


class AIProviderError(AIAssistantError):
    """Error with AI provider configuration or communication."""
    pass


class AIAssistantBase(ABC):
    """Abstract base class for AI assistants."""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate AI provider configuration."""
        pass
    
    @abstractmethod
    def _make_request(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Make request to AI provider."""
        pass
    
    def suggest_headers(self, url: str, method: str = "GET") -> AIResponse:
        """Suggest appropriate headers for a request."""
        system_prompt = """You are an API testing expert. Suggest appropriate HTTP headers for the given request.
        Focus on common, practical headers that would be useful for API testing.
        Return suggestions as a JSON array of objects with 'header' and 'value' keys."""
        
        prompt = f"""
        Suggest appropriate HTTP headers for this API request:
        Method: {method}
        URL: {url}
        
        Consider:
        - Content-Type headers for POST/PUT requests
        - Accept headers for response format
        - Authorization patterns based on URL patterns
        - Common API headers like User-Agent, Accept-Encoding
        
        Return as JSON array: [{"header": "Content-Type", "value": "application/json"}, ...]
        """
        
        return self._make_request(prompt, system_prompt)
    
    def explain_status_code(self, status_code: int, response_body: str = None) -> AIResponse:
        """Explain HTTP status code and suggest next steps."""
        system_prompt = """You are an API testing expert. Explain HTTP status codes in a helpful, 
        actionable way for developers testing APIs."""
        
        prompt = f"""
        Explain this HTTP status code: {status_code}
        
        Provide:
        1. What this status code means
        2. Common causes
        3. Suggested troubleshooting steps
        4. Whether this indicates success, client error, or server error
        """
        
        if response_body:
            prompt += f"\n\nResponse body: {response_body[:500]}..."
        
        return self._make_request(prompt, system_prompt)
    
    def validate_json_structure(self, json_data: str, expected_schema: str = None) -> AIResponse:
        """Validate JSON structure and suggest improvements."""
        system_prompt = """You are a JSON validation expert. Analyze JSON structure and provide 
        helpful feedback about validity, common issues, and improvements."""
        
        prompt = f"""
        Analyze this JSON data:
        {json_data}
        
        Check for:
        1. Valid JSON syntax
        2. Common structural issues
        3. Potential improvements
        4. Missing or unexpected fields
        """
        
        if expected_schema:
            prompt += f"\n\nExpected schema or format:\n{expected_schema}"
        
        return self._make_request(prompt, system_prompt)
    
    def generate_request_examples(self, api_spec: str, endpoint: str = None) -> AIResponse:
        """Generate request examples from API specification."""
        system_prompt = """You are an API documentation expert. Generate practical, 
        working request examples from API specifications."""
        
        prompt = f"""
        Generate HTTP request examples from this API specification:
        {api_spec}
        """
        
        if endpoint:
            prompt += f"\n\nFocus on endpoint: {endpoint}"
        
        prompt += """
        
        Provide:
        1. Complete curl commands
        2. Required headers
        3. Sample request bodies
        4. Expected response formats
        """
        
        return self._make_request(prompt, system_prompt)
    
    def interpret_error_message(self, error_message: str, request_context: Dict[str, Any] = None) -> AIResponse:
        """Interpret error messages and suggest solutions."""
        system_prompt = """You are an API troubleshooting expert. Interpret error messages 
        and provide actionable solutions for API testing issues."""
        
        prompt = f"""
        Interpret this error message and suggest solutions:
        {error_message}
        
        Provide:
        1. What the error means in plain language
        2. Likely causes
        3. Step-by-step troubleshooting
        4. How to prevent this error
        """
        
        if request_context:
            prompt += f"\n\nRequest context:\n{json.dumps(request_context, indent=2)}"
        
        return self._make_request(prompt, system_prompt)
    
    def suggest_test_cases(self, endpoint_info: Dict[str, Any]) -> AIResponse:
        """Suggest test cases for an API endpoint."""
        system_prompt = """You are an API testing expert. Suggest comprehensive test cases 
        for API endpoints covering happy path, edge cases, and error scenarios."""
        
        prompt = f"""
        Suggest test cases for this API endpoint:
        {json.dumps(endpoint_info, indent=2)}
        
        Include:
        1. Happy path scenarios
        2. Edge cases and boundary conditions
        3. Error scenarios (4xx, 5xx)
        4. Security considerations
        5. Performance considerations
        """
        
        return self._make_request(prompt, system_prompt)


class OpenAIAssistant(AIAssistantBase):
    """OpenAI-based AI assistant."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.default_model = model
        super().__init__(api_key, model)
    
    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise AIProviderError("OpenAI API key is required")
        
        if not self.model:
            self.model = self.default_model
    
    def _make_request(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Make request to OpenAI API."""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.3),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            
            content = response.choices[0].message.content
            
            return AIResponse(
                content=content,
                confidence=0.8,  # Default confidence for OpenAI
                metadata={
                    "model": self.model,
                    "provider": "openai",
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except ImportError:
            raise AIProviderError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            raise AIProviderError(f"OpenAI API error: {e}")


class AnthropicAssistant(AIAssistantBase):
    """Anthropic Claude-based AI assistant."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.default_model = model
        super().__init__(api_key, model)
    
    def _validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.api_key:
            raise AIProviderError("Anthropic API key is required")
        
        if not self.model:
            self.model = self.default_model
    
    def _make_request(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Make request to Anthropic API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Combine system prompt with user prompt for Anthropic
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.3),
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            content = response.content[0].text
            
            return AIResponse(
                content=content,
                confidence=0.8,  # Default confidence for Anthropic
                metadata={
                    "model": self.model,
                    "provider": "anthropic",
                    "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else 0
                }
            )
            
        except ImportError:
            raise AIProviderError("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            raise AIProviderError(f"Anthropic API error: {e}")


class GeminiAssistant(AIAssistantBase):
    """Google Gemini-based AI assistant."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.default_model = model
        super().__init__(api_key, model)
    
    def _validate_config(self) -> None:
        """Validate Gemini configuration."""
        if not self.api_key:
            raise AIProviderError("Gemini API key is required")
        
        if not self.model:
            self.model = self.default_model
    
    def _make_request(self, prompt: str, system_prompt: str = None, **kwargs) -> AIResponse:
        """Make request to Gemini API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            # Combine system prompt with user prompt for Gemini
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.3),
                    max_output_tokens=kwargs.get("max_tokens", 1000)
                )
            )
            
            content = response.text
            
            return AIResponse(
                content=content,
                confidence=0.8,  # Default confidence for Gemini
                metadata={
                    "model": self.model,
                    "provider": "gemini",
                    "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                }
            )
            
        except ImportError:
            raise AIProviderError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        except Exception as e:
            raise AIProviderError(f"Gemini API error: {e}")


class AIAssistant:
    """Main AI Assistant class that manages different providers."""
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """Initialize AI Assistant with specified provider."""
        config = get_config()
        
        # Use config values if not provided
        if not provider:
            provider = config.ai.provider if config.ai.enabled else "openai"
        if not api_key:
            api_key = config.ai.api_key if config.ai.enabled else None
        if not model:
            model = config.ai.model if config.ai.enabled else None
        
        self.provider_name = provider
        self.assistant = self._create_assistant(provider, api_key, model)
    
    def _create_assistant(self, provider: str, api_key: str, model: str) -> AIAssistantBase:
        """Create appropriate AI assistant based on provider."""
        if not api_key:
            raise AIProviderError(f"API key required for {provider}")
        
        provider_lower = provider.lower()
        
        if provider_lower == "openai":
            return OpenAIAssistant(api_key, model)
        elif provider_lower == "anthropic":
            return AnthropicAssistant(api_key, model)
        elif provider_lower == "gemini":
            return GeminiAssistant(api_key, model)
        else:
            raise AIProviderError(f"Unsupported AI provider: {provider}")
    
    def is_available(self) -> bool:
        """Check if AI assistant is available and configured."""
        try:
            config = get_config()
            return (config.ai.enabled and 
                   config.ai.api_key is not None and 
                   self.assistant is not None)
        except Exception:
            return False
    
    def suggest_headers(self, url: str, method: str = "GET") -> AIResponse:
        """Suggest appropriate headers for a request."""
        return self.assistant.suggest_headers(url, method)
    
    def explain_status_code(self, status_code: int, response_body: str = None) -> AIResponse:
        """Explain HTTP status code and suggest next steps."""
        return self.assistant.explain_status_code(status_code, response_body)
    
    def validate_json_structure(self, json_data: str, expected_schema: str = None) -> AIResponse:
        """Validate JSON structure and suggest improvements."""
        return self.assistant.validate_json_structure(json_data, expected_schema)
    
    def generate_request_examples(self, api_spec: str, endpoint: str = None) -> AIResponse:
        """Generate request examples from API specification."""
        return self.assistant.generate_request_examples(api_spec, endpoint)
    
    def interpret_error_message(self, error_message: str, request_context: Dict[str, Any] = None) -> AIResponse:
        """Interpret error messages and suggest solutions."""
        return self.assistant.interpret_error_message(error_message, request_context)
    
    def suggest_test_cases(self, endpoint_info: Dict[str, Any]) -> AIResponse:
        """Suggest test cases for an API endpoint."""
        return self.assistant.suggest_test_cases(endpoint_info)


# Utility functions for common AI-assisted tasks
def extract_headers_from_ai_response(ai_response: AIResponse) -> Dict[str, str]:
    """Extract headers from AI response content."""
    try:
        # Try to parse as JSON first
        content = ai_response.content.strip()
        
        # Look for JSON array in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            headers_list = json.loads(json_match.group())
            return {item['header']: item['value'] for item in headers_list if 'header' in item and 'value' in item}
        
        # Fallback: parse line by line
        headers = {}
        lines = content.split('\n')
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return headers
        
    except Exception:
        return {}


def extract_suggestions_from_ai_response(ai_response: AIResponse) -> List[str]:
    """Extract actionable suggestions from AI response."""
    content = ai_response.content
    suggestions = []
    
    # Look for numbered lists
    numbered_pattern = r'^\d+\.\s*(.+)$'
    for line in content.split('\n'):
        match = re.match(numbered_pattern, line.strip())
        if match:
            suggestions.append(match.group(1))
    
    # Look for bullet points
    if not suggestions:
        bullet_pattern = r'^[-*•]\s*(.+)$'
        for line in content.split('\n'):
            match = re.match(bullet_pattern, line.strip())
            if match:
                suggestions.append(match.group(1))
    
    return suggestions


def format_ai_response_for_display(ai_response: AIResponse) -> str:
    """Format AI response for console display."""
    formatted = ai_response.content
    
    # Add confidence indicator if available
    if ai_response.confidence > 0:
        confidence_text = f"(Confidence: {ai_response.confidence:.1%})"
        formatted = f"{formatted}\n\n{confidence_text}"
    
    # Add provider info if available
    if ai_response.metadata and 'provider' in ai_response.metadata:
        provider_info = f"Powered by {ai_response.metadata['provider']}"
        if 'model' in ai_response.metadata:
            provider_info += f" ({ai_response.metadata['model']})"
        formatted = f"{formatted}\n\n[dim]{provider_info}[/dim]"
    
    return formatted
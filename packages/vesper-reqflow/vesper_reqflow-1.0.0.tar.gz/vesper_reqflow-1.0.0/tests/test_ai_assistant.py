"""Tests for AI assistant functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from apitester.ai.assistant import (
    AIAssistant,
    AIAssistantBase,
    OpenAIAssistant,
    AnthropicAssistant,
    GeminiAssistant,
    AIResponse,
    AIAssistantError,
    AIProviderError,
    AIProvider
)


class TestAIResponse:
    """Test AIResponse data class."""
    
    def test_ai_response_creation(self):
        """Test creating AIResponse with default values."""
        response = AIResponse("Test content")
        
        assert response.content == "Test content"
        assert response.confidence == 0.0
        assert response.suggestions == []
        assert response.metadata == {}
    
    def test_ai_response_with_all_fields(self):
        """Test creating AIResponse with all fields."""
        response = AIResponse(
            content="Test content",
            confidence=0.8,
            suggestions=["suggestion1", "suggestion2"],
            metadata={"provider": "openai", "model": "gpt-3.5-turbo"}
        )
        
        assert response.content == "Test content"
        assert response.confidence == 0.8
        assert response.suggestions == ["suggestion1", "suggestion2"]
        assert response.metadata == {"provider": "openai", "model": "gpt-3.5-turbo"}


class TestOpenAIAssistant:
    """Test OpenAI assistant implementation."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        assistant = OpenAIAssistant("test-api-key", "gpt-3.5-turbo")
        
        assert assistant.api_key == "test-api-key"
        assert assistant.model == "gpt-3.5-turbo"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(AIProviderError, match="OpenAI API key is required"):
            OpenAIAssistant("", "gpt-3.5-turbo")
    
    def test_init_without_model_uses_default(self):
        """Test initialization without model uses default."""
        assistant = OpenAIAssistant("test-api-key")
        
        assert assistant.model == "gpt-3.5-turbo"
    
    @patch('src.apitester.ai.assistant.openai')
    def test_make_request_success(self, mock_openai):
        """Test successful API request."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 100
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        assistant = OpenAIAssistant("test-api-key")
        response = assistant._make_request("Test prompt", "System prompt")
        
        assert response.content == "Test response"
        assert response.confidence == 0.8
        assert response.metadata["provider"] == "openai"
        assert response.metadata["tokens_used"] == 100
    
    @patch('src.apitester.ai.assistant.openai')
    def test_make_request_import_error(self, mock_openai):
        """Test handling of missing OpenAI library."""
        mock_openai.side_effect = ImportError("No module named 'openai'")
        
        assistant = OpenAIAssistant("test-api-key")
        
        with pytest.raises(AIProviderError, match="OpenAI library not installed"):
            assistant._make_request("Test prompt")
    
    @patch('src.apitester.ai.assistant.openai')
    def test_suggest_headers(self, mock_openai):
        """Test header suggestion functionality."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        [
            {"header": "Authorization", "value": "Bearer ${API_TOKEN}"},
            {"header": "Content-Type", "value": "application/json"}
        ]
        """
        mock_response.usage.total_tokens = 50
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        assistant = OpenAIAssistant("test-api-key")
        response = assistant.suggest_headers("https://api.github.com/user", "GET")
        
        assert "Authorization" in response.content
        assert "Content-Type" in response.content
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.apitester.ai.assistant.openai')
    def test_explain_status_code(self, mock_openai):
        """Test status code explanation functionality."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "HTTP 404 means the resource was not found."
        mock_response.usage.total_tokens = 30
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        assistant = OpenAIAssistant("test-api-key")
        response = assistant.explain_status_code(404, "Not found")
        
        assert "404" in response.content
        assert "not found" in response.content.lower()


class TestAnthropicAssistant:
    """Test Anthropic assistant implementation."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        assistant = AnthropicAssistant("test-api-key", "claude-3-sonnet-20240229")
        
        assert assistant.api_key == "test-api-key"
        assert assistant.model == "claude-3-sonnet-20240229"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(AIProviderError, match="Anthropic API key is required"):
            AnthropicAssistant("")
    
    @patch('src.apitester.ai.assistant.anthropic')
    def test_make_request_success(self, mock_anthropic):
        """Test successful API request."""
        # Mock Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response from Claude"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 30
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        
        assistant = AnthropicAssistant("test-api-key")
        response = assistant._make_request("Test prompt", "System prompt")
        
        assert response.content == "Test response from Claude"
        assert response.confidence == 0.8
        assert response.metadata["provider"] == "anthropic"
        assert response.metadata["tokens_used"] == 80
    
    @patch('src.apitester.ai.assistant.anthropic')
    def test_make_request_import_error(self, mock_anthropic):
        """Test handling of missing Anthropic library."""
        mock_anthropic.side_effect = ImportError("No module named 'anthropic'")
        
        assistant = AnthropicAssistant("test-api-key")
        
        with pytest.raises(AIProviderError, match="Anthropic library not installed"):
            assistant._make_request("Test prompt")


class TestGeminiAssistant:
    """Test Gemini assistant implementation."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        assistant = GeminiAssistant("test-api-key", "gemini-pro")
        
        assert assistant.api_key == "test-api-key"
        assert assistant.model == "gemini-pro"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(AIProviderError, match="Gemini API key is required"):
            GeminiAssistant("")
    
    @patch('src.apitester.ai.assistant.google.generativeai')
    def test_make_request_success(self, mock_genai):
        """Test successful API request."""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "Test response from Gemini"
        mock_response.usage_metadata.total_token_count = 75
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        assistant = GeminiAssistant("test-api-key")
        response = assistant._make_request("Test prompt", "System prompt")
        
        assert response.content == "Test response from Gemini"
        assert response.confidence == 0.8
        assert response.metadata["provider"] == "gemini"
        assert response.metadata["tokens_used"] == 75
    
    @patch('src.apitester.ai.assistant.google.generativeai')
    def test_make_request_import_error(self, mock_genai):
        """Test handling of missing Gemini library."""
        mock_genai.side_effect = ImportError("No module named 'google.generativeai'")
        
        assistant = GeminiAssistant("test-api-key")
        
        with pytest.raises(AIProviderError, match="Google Generative AI library not installed"):
            assistant._make_request("Test prompt")


class TestAIAssistant:
    """Test main AIAssistant class."""
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_init_with_openai_provider(self, mock_get_config):
        """Test initialization with OpenAI provider."""
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.provider = "openai"
        mock_config.ai.api_key = "test-key"
        mock_config.ai.model = "gpt-3.5-turbo"
        mock_get_config.return_value = mock_config
        
        with patch('src.apitester.ai.assistant.OpenAIAssistant') as mock_openai:
            assistant = AIAssistant()
            
            mock_openai.assert_called_once_with("test-key", "gpt-3.5-turbo")
            assert assistant.provider_name == "openai"
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_init_with_anthropic_provider(self, mock_get_config):
        """Test initialization with Anthropic provider."""
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.provider = "anthropic"
        mock_config.ai.api_key = "test-key"
        mock_config.ai.model = "claude-3-sonnet-20240229"
        mock_get_config.return_value = mock_config
        
        with patch('src.apitester.ai.assistant.AnthropicAssistant') as mock_anthropic:
            assistant = AIAssistant()
            
            mock_anthropic.assert_called_once_with("test-key", "claude-3-sonnet-20240229")
            assert assistant.provider_name == "anthropic"
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_init_with_gemini_provider(self, mock_get_config):
        """Test initialization with Gemini provider."""
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.provider = "gemini"
        mock_config.ai.api_key = "test-key"
        mock_config.ai.model = "gemini-pro"
        mock_get_config.return_value = mock_config
        
        with patch('src.apitester.ai.assistant.GeminiAssistant') as mock_gemini:
            assistant = AIAssistant()
            
            mock_gemini.assert_called_once_with("test-key", "gemini-pro")
            assert assistant.provider_name == "gemini"
    
    def test_init_with_unsupported_provider(self):
        """Test initialization with unsupported provider raises error."""
        with pytest.raises(AIProviderError, match="Unsupported AI provider: invalid"):
            AIAssistant("invalid", "test-key", "model")
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(AIProviderError, match="API key required"):
            AIAssistant("openai", None, "model")
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_is_available_when_enabled(self, mock_get_config):
        """Test is_available returns True when properly configured."""
        mock_config = Mock()
        mock_config.ai.enabled = True
        mock_config.ai.api_key = "test-key"
        mock_get_config.return_value = mock_config
        
        with patch('src.apitester.ai.assistant.OpenAIAssistant'):
            assistant = AIAssistant("openai", "test-key", "model")
            assert assistant.is_available() is True
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_is_available_when_disabled(self, mock_get_config):
        """Test is_available returns False when AI is disabled."""
        mock_config = Mock()
        mock_config.ai.enabled = False
        mock_get_config.return_value = mock_config
        
        assistant = AIAssistant("openai", "test-key", "model")
        assert assistant.is_available() is False
    
    @patch('src.apitester.ai.assistant.get_config')
    def test_is_available_exception_handling(self, mock_get_config):
        """Test is_available handles exceptions gracefully."""
        mock_get_config.side_effect = Exception("Config error")
        
        assistant = AIAssistant("openai", "test-key", "model")
        assert assistant.is_available() is False


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_extract_headers_from_ai_response_json(self):
        """Test extracting headers from JSON response."""
        from apitester.ai.assistant import extract_headers_from_ai_response
        
        response = AIResponse("""
        [
            {"header": "Authorization", "value": "Bearer token"},
            {"header": "Content-Type", "value": "application/json"}
        ]
        """)
        
        headers = extract_headers_from_ai_response(response)
        
        assert headers["Authorization"] == "Bearer token"
        assert headers["Content-Type"] == "application/json"
    
    def test_extract_headers_from_ai_response_text(self):
        """Test extracting headers from text response."""
        from apitester.ai.assistant import extract_headers_from_ai_response
        
        response = AIResponse("""
        Authorization: Bearer token
        Content-Type: application/json
        Accept: application/json
        """)
        
        headers = extract_headers_from_ai_response(response)
        
        assert headers["Authorization"] == "Bearer token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
    
    def test_extract_headers_from_ai_response_invalid(self):
        """Test extracting headers from invalid response."""
        from apitester.ai.assistant import extract_headers_from_ai_response
        
        response = AIResponse("Invalid response format")
        
        headers = extract_headers_from_ai_response(response)
        
        assert headers == {}
    
    def test_extract_suggestions_from_ai_response_numbered(self):
        """Test extracting numbered suggestions."""
        from apitester.ai.assistant import extract_suggestions_from_ai_response
        
        response = AIResponse("""
        Here are some suggestions:
        1. Check your API key
        2. Verify the endpoint URL
        3. Ensure proper headers are set
        """)
        
        suggestions = extract_suggestions_from_ai_response(response)
        
        assert len(suggestions) == 3
        assert "Check your API key" in suggestions
        assert "Verify the endpoint URL" in suggestions
        assert "Ensure proper headers are set" in suggestions
    
    def test_extract_suggestions_from_ai_response_bullets(self):
        """Test extracting bullet point suggestions."""
        from apitester.ai.assistant import extract_suggestions_from_ai_response
        
        response = AIResponse("""
        Suggestions:
        - Check your API key
        * Verify the endpoint URL
        • Ensure proper headers are set
        """)
        
        suggestions = extract_suggestions_from_ai_response(response)
        
        assert len(suggestions) == 3
        assert "Check your API key" in suggestions
        assert "Verify the endpoint URL" in suggestions
        assert "Ensure proper headers are set" in suggestions
    
    def test_format_ai_response_for_display(self):
        """Test formatting AI response for display."""
        from apitester.ai.assistant import format_ai_response_for_display
        
        response = AIResponse(
            content="Test response",
            confidence=0.85,
            metadata={"provider": "openai", "model": "gpt-3.5-turbo"}
        )
        
        formatted = format_ai_response_for_display(response)
        
        assert "Test response" in formatted
        assert "85.0%" in formatted
        assert "openai" in formatted
        assert "gpt-3.5-turbo" in formatted


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock()
    config.ai.enabled = True
    config.ai.provider = "openai"
    config.ai.api_key = "test-key"
    config.ai.model = "gpt-3.5-turbo"
    return config


class TestAIAssistantIntegration:
    """Integration tests for AI assistant functionality."""
    
    @patch('src.apitester.ai.assistant.get_config')
    @patch('src.apitester.ai.assistant.openai')
    def test_full_workflow_header_suggestion(self, mock_openai, mock_get_config, mock_config):
        """Test complete workflow for header suggestion."""
        mock_get_config.return_value = mock_config
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        [
            {"header": "Authorization", "value": "Bearer ${GITHUB_TOKEN}"},
            {"header": "Accept", "value": "application/vnd.github.v3+json"}
        ]
        """
        mock_response.usage.total_tokens = 50
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        # Test the workflow
        assistant = AIAssistant()
        response = assistant.suggest_headers("https://api.github.com/user", "GET")
        
        assert response.content is not None
        assert "Authorization" in response.content
        assert "Accept" in response.content
        assert response.metadata["provider"] == "openai"
    
    @patch('src.apitester.ai.assistant.get_config')
    @patch('src.apitester.ai.assistant.openai')
    def test_full_workflow_status_explanation(self, mock_openai, mock_get_config, mock_config):
        """Test complete workflow for status code explanation."""
        mock_get_config.return_value = mock_config
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        HTTP 429 indicates that you have sent too many requests in a given amount of time.
        
        Common causes:
        1. Exceeding API rate limits
        2. Making requests too quickly
        
        Solutions:
        1. Implement exponential backoff
        2. Check rate limit headers
        3. Reduce request frequency
        """
        mock_response.usage.total_tokens = 100
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        # Test the workflow
        assistant = AIAssistant()
        response = assistant.explain_status_code(429, "Rate limit exceeded")
        
        assert response.content is not None
        assert "429" in response.content
        assert "rate limit" in response.content.lower()
        assert "exponential backoff" in response.content.lower()
        assert response.metadata["provider"] == "openai"
"""Tests for AI integration components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from apitester.ai.integrations import (
    HeaderSuggestionEngine,
    StatusCodeExplainer,
    JSONValidator,
    OpenAPIIntegration,
    ErrorMessageInterpreter
)
from apitester.ai.assistant import AIAssistant, AIResponse


@pytest.fixture
def mock_ai_assistant():
    """Mock AI assistant for testing."""
    assistant = Mock(spec=AIAssistant)
    assistant.is_available.return_value = True
    return assistant


@pytest.fixture
def sample_ai_response():
    """Sample AI response for testing."""
    return AIResponse(
        content="Test AI response content",
        confidence=0.8,
        suggestions=["suggestion1", "suggestion2"],
        metadata={"provider": "openai", "model": "gpt-3.5-turbo"}
    )


class TestHeaderSuggestionEngine:
    """Test header suggestion engine."""
    
    def test_init(self, mock_ai_assistant):
        """Test initialization."""
        engine = HeaderSuggestionEngine(mock_ai_assistant)
        
        assert engine.ai_assistant == mock_ai_assistant
        assert isinstance(engine._common_patterns, dict)
        assert "github.com" in engine._common_patterns
    
    def test_suggest_headers_github_pattern(self, mock_ai_assistant):
        """Test header suggestions for GitHub API pattern."""
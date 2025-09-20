"""Agentic API Tester CLI - A Postman-like terminal tool for API testing."""

__version__ = "1.0.0"
__description__ = "A Postman-like terminal tool for API testing with Redis backend and AI assistance"
__author__ = "API Tester Team"
__email__ = "team@apitester.dev"
__license__ = "MIT"
__url__ = "https://github.com/apitester/agentic-api-tester-cli"

# Package metadata
__all__ = [
    "__version__",
    "__description__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
]

# Version info tuple for programmatic access
VERSION_INFO = tuple(int(x) for x in __version__.split('.'))

# Minimum Python version required
PYTHON_REQUIRES = (3, 8)

# Check Python version
import sys
if sys.version_info < PYTHON_REQUIRES:
    raise RuntimeError(
        f"Python {PYTHON_REQUIRES[0]}.{PYTHON_REQUIRES[1]} or higher is required. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# Optional imports with graceful degradation
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Feature availability
AI_AVAILABLE = OPENAI_AVAILABLE or ANTHROPIC_AVAILABLE or GEMINI_AVAILABLE

# Package configuration
DEFAULT_CONFIG_DIR = "~/.config/apitester"
DEFAULT_CONFIG_FILE = "config.yaml"
DEFAULT_CACHE_DIR = "~/.cache/apitester"
DEFAULT_DATA_DIR = "~/.local/share/apitester"

# Application constants
APP_NAME = "apitester"
APP_DISPLAY_NAME = "Agentic API Tester"
USER_AGENT = f"Agentic-API-Tester/{__version__}"

# Redis configuration defaults
DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0

# Cache configuration defaults
DEFAULT_CACHE_TTL = 300  # 5 minutes
DEFAULT_CACHE_MAX_SIZE = 1000

# History configuration defaults
DEFAULT_HISTORY_MAX_ENTRIES = 10000

# AI configuration defaults
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-3.5-turbo"
DEFAULT_AI_MAX_TOKENS = 1000
DEFAULT_AI_TEMPERATURE = 0.1

# HTTP client defaults
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_REDIRECTS = 10
DEFAULT_VERIFY_SSL = True

# Output configuration defaults
DEFAULT_JSON_INDENT = 2
DEFAULT_TABLE_MAX_WIDTH = 120

# Logging configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_version() -> str:
    """Get the package version."""
    return __version__

def get_version_info() -> tuple:
    """Get the package version as a tuple."""
    return VERSION_INFO

def check_dependencies() -> dict:
    """Check availability of optional dependencies."""
    return {
        "redis": REDIS_AVAILABLE,
        "openai": OPENAI_AVAILABLE,
        "anthropic": ANTHROPIC_AVAILABLE,
        "gemini": GEMINI_AVAILABLE,
        "ai": AI_AVAILABLE,
    }

def get_user_agent() -> str:
    """Get the default User-Agent string."""
    return USER_AGENT

# Expose main CLI entry point
from .cli.main import app as cli_app

def main():
    """Main entry point for the CLI application."""
    cli_app()

# Type checking marker (PEP 561)
__all__.append("py.typed")
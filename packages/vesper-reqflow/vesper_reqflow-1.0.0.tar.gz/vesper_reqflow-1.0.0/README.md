# ReqFlow

[![PyPI version](https://badge.fury.io/py/agentic-api-tester-cli.svg)](https://badge.fury.io/py/agentic-api-tester-cli)
[![Python Support](https://img.shields.io/pypi/pyversions/agentic-api-tester-cli.svg)](https://pypi.org/project/agentic-api-tester-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/VesperAkshay/ReqFlow/workflows/Tests/badge.svg)](https://github.com/VesperAkshay/ReqFlow/actions)
[![Coverage](https://codecov.io/gh/VesperAkshay/ReqFlow/branch/main/graph/badge.svg)](https://codecov.io/gh/VesperAkshay/ReqFlow)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, Postman-like terminal tool for API testing with Redis backend, AI assistance, and comprehensive workflow management.

## 🚀 Features

### 🌐 **HTTP & GraphQL Support**
- Send REST requests (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- Execute GraphQL queries and mutations
- Support for custom headers, query parameters, and request bodies
- File upload and multipart form data support

### 📝 **Template System**
- Save and reuse request configurations
- Variable substitution with `${VARIABLE}` syntax
- Template import/export in JSON and YAML formats
- Template versioning and metadata tracking

### 🌍 **Environment Management**
- Manage multiple environments (dev, staging, prod)
- Environment-specific variable sets
- Easy environment switching
- Variable inheritance and overrides

### 📊 **Request History & Analytics**
- Persistent request history with Redis backend
- Request retry functionality
- Response time tracking and statistics
- History search and filtering

### ⚡ **Response Caching**
- Redis-based response caching with TTL
- Intelligent cache key generation
- Cache hit/miss indicators
- Configurable cache policies

### 🤖 **AI Assistant**
- **OpenAI, Anthropic, Google Gemini** integration
- Intelligent header suggestions
- HTTP status code explanations
- JSON structure validation
- Request example generation from OpenAPI specs

### 🎨 **Rich CLI Experience**
- Beautiful terminal interface with colors and tables
- Syntax highlighting for JSON, XML, and HTML responses
- Progress bars for batch operations
- Shell autocompletion
- Comprehensive help system

## 📦 Installation

### Quick Install

```bash
pip install vesper-reqflow
```

### With AI Features

```bash
pip install vesper-reqflow[ai]
```

### Development Installation

```bash
git clone https://github.com/VesperAkshay/ReqFlow.git
cd ReqFlow
pip install -e .[dev]
```

### Requirements

- **Python 3.8+**
- **Redis 6.0+** (for caching and history)
- **Optional**: AI provider API keys (OpenAI, Anthropic, or Google)

## 🎯 Quick Start

### Basic Usage

```bash
# Send a simple GET request
apitester request send GET https://jsonplaceholder.typicode.com/posts/1

# POST with JSON body
apitester request send POST https://httpbin.org/post \\
  --header \"Content-Type: application/json\" \\
  --body '{\"name\": \"John\", \"email\": \"john@example.com\"}'

# Check system status
apitester status
```

### Templates

```bash
# Save a template
apitester template save github-user GET https://api.github.com/users/${USERNAME} \\
  --header \"Authorization: Bearer ${GITHUB_TOKEN}\"

# Use the template
apitester request template github-user --var \"USERNAME=octocat\"

# List templates
apitester template list
```

### Environments

```bash
# Create environment
apitester env create development

# Set variables
apitester env set API_BASE https://api-dev.example.com
apitester env set API_KEY dev-key-123

# Switch environment
apitester env switch development
```

### AI Assistant

```bash
# Get header suggestions
apitester ai suggest-headers https://api.github.com/user

# Explain status codes
apitester ai explain-status 429

# Validate JSON
apitester ai validate-json '{\"name\": \"test\"}'
```

## 📚 Documentation

- **[Installation Guide](docs/installation.rst)** - Detailed setup instructions
- **[Quick Start](docs/quickstart.rst)** - Get up and running fast
- **[User Guide](docs/user-guide/)** - Comprehensive feature documentation
- **[CLI Reference](docs/cli-reference/)** - Complete command reference
- **[Examples](docs/examples.rst)** - Real-world use cases
- **[API Reference](docs/api/)** - Developer documentation

## 🔧 Configuration

### Basic Configuration

Create `~/.config/apitester/config.yaml`:

```yaml
redis:
  host: localhost
  port: 6379
  database: 0

cache:
  enabled: true
  default_ttl: 3600

history:
  enabled: true
  max_entries: 10000

ai:
  enabled: true
  provider: openai  # or anthropic, gemini
  model: gpt-3.5-turbo
```

### Environment Variables

```bash
# Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6379

# AI providers
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key
export GOOGLE_API_KEY=your-google-key
```

## 🎨 Examples

### REST API Testing

```bash
# Test user creation
apitester request send POST https://jsonplaceholder.typicode.com/users \\
  --header \"Content-Type: application/json\" \\
  --body '{
    \"name\": \"John Doe\",
    \"username\": \"johndoe\",
    \"email\": \"john@example.com\"
  }'

# Test with authentication
apitester request send GET https://api.github.com/user \\
  --header \"Authorization: Bearer $GITHUB_TOKEN\"
```

### GraphQL Queries

```bash
# Simple query
apitester request graphql https://api.github.com/graphql \\
  --header \"Authorization: Bearer $GITHUB_TOKEN\" \\
  --query 'query { viewer { login name } }'

# Query with variables
apitester request graphql https://api.github.com/graphql \\
  --header \"Authorization: Bearer $GITHUB_TOKEN\" \\
  --query 'query($login: String!) { user(login: $login) { name bio } }' \\
  --variables '{\"login\": \"octocat\"}'
```

### Batch Operations

```bash
# Create batch configuration
cat > batch.json << EOF
{
  \"requests\": [
    {\"name\": \"get-users\", \"template\": \"api-users\"},
    {\"name\": \"get-posts\", \"template\": \"api-posts\"}
  ]
}
EOF

# Execute batch
apitester request batch batch.json
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │   Core Engine   │    │  Storage Layer  │
│                 │    │                 │    │                 │
│ • Typer Commands│───▶│ • HTTP Client   │───▶│ • Redis Backend │
│ • Rich Output   │    │ • Template Mgr  │    │ • Data Models   │
│ • Autocompletion│    │ • Environment   │    │ • Serialization │
└─────────────────┘    │ • History       │    └─────────────────┘
                       │ • Cache         │
                       │ • AI Assistant  │    ┌─────────────────┐
                       └─────────────────┘    │  External APIs  │
                                              │                 │
                                              │ • OpenAI        │
                                              │ • Anthropic     │
                                              │ • Google Gemini │
                                              └─────────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apitester --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m cli          # CLI tests only

# Run performance tests
pytest -m slow --benchmark-only
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/VesperAkshay/ReqFlow.git
cd ReqFlow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Quality

We maintain high code quality standards:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing
- **bandit** for security analysis

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Postman](https://www.postman.com/) and [HTTPie](https://httpie.io/)
- Built with amazing open-source libraries:
  - [Typer](https://typer.tiangolo.com/) for CLI framework
  - [Rich](https://rich.readthedocs.io/) for terminal formatting
  - [httpx](https://www.python-httpx.org/) for HTTP client
  - [Redis](https://redis.io/) for data persistence
  - [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📞 Support

- **Documentation**: [Read the Docs](https://reqflow.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/VesperAkshay/ReqFlow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VesperAkshay/ReqFlow/discussions)
- **Email**: team@apitester.dev

## 🗺️ Roadmap

### v1.1.0
- [ ] WebSocket support
- [ ] Enhanced AI capabilities
- [ ] Additional output formats
- [ ] Performance improvements

### v1.2.0
- [ ] Advanced authentication methods
- [ ] Improved batch operations
- [ ] Enhanced reporting features
- [ ] Plugin system expansion

### v2.0.0
- [ ] Major architecture improvements
- [ ] New storage backends
- [ ] Advanced workflow automation
- [ ] Breaking API improvements

---

**Made with ❤️ by the ReqFlow Team**
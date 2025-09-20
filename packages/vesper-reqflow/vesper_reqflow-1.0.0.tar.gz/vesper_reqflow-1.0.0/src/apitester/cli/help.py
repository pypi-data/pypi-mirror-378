"""Comprehensive help system for the CLI."""

import typer
from typing import Optional, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Help content organized by topic
HELP_TOPICS = {
    "getting-started": {
        "title": "Getting Started with API Tester",
        "content": r"""
# Getting Started

Welcome to the Agentic API Tester CLI! This guide will help you get up and running quickly.

## Prerequisites

1. **Redis Server**: Make sure Redis is installed and running
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Install Redis (macOS with Homebrew)
   brew install redis
   
   # Start Redis
   redis-server
   ```

2. **Python Environment**: Ensure you have Python 3.8+ installed

## First Steps

1. **Check System Status**
   ```bash
   apitester status
   ```

2. **Run Diagnostics** (if there are issues)
   ```bash
   apitester doctor
   ```

3. **Send Your First Request**
   ```bash
   apitester request send GET https://jsonplaceholder.typicode.com/posts/1
   ```

4. **View Configuration**
   ```bash
   apitester config
   ```

## Quick Examples

- **GET request with headers**:
  ```bash
  apitester request send GET https://api.github.com/user \\
    --header "Authorization: token YOUR_TOKEN"
  ```

- **POST request with JSON body**:
  ```bash
  apitester request send POST https://jsonplaceholder.typicode.com/posts \\
    --header "Content-Type: application/json" \\
    --body '{"title": "Test", "body": "Content", "userId": 1}'
  ```

- **Save a template**:
  ```bash
  apitester template save github-user GET https://api.github.com/user \\
    --header "Authorization: token \\${GITHUB_TOKEN}" \\
    --description "Get current user info"
  ```

- **Set environment variables**:
  ```bash
  apitester env set GITHUB_TOKEN your_token_here
  apitester env set API_BASE_URL https://api.example.com
  ```

## Next Steps

- Learn about [templates](#templates) for reusable requests
- Set up [environments](#environments) for different configurations  
- Explore [history](#history) to track and retry requests
- Enable [shell completion](#completion) for better productivity

For detailed help on any command, use: `apitester COMMAND --help`
"""
    },
    
    "templates": {
        "title": "Working with Templates",
        "content": r"""
# Templates

Templates allow you to save and reuse request configurations with variable substitution.

## Creating Templates

**Save a simple template**:
```bash
apitester template save my-api GET https://api.example.com/users \
  --header "Authorization: Bearer \${API_TOKEN}" \
  --description "Get all users"
```

**Save with request body**:
```bash
apitester template save create-user POST https://api.example.com/users \\
  --header "Content-Type: application/json" \\
  --body '{"name": "\\${USER_NAME}", "email": "\\${USER_EMAIL}"}' \\
  --tag "user-management"
```

## Using Templates

**Execute a template**:
```bash
apitester request template my-api
```

**Execute with variable overrides**:
```bash
apitester request template create-user \\
  --var "USER_NAME=John Doe" \\
  --var "USER_EMAIL=john@example.com"
```

**Execute with different environment**:
```bash
apitester request template my-api --env production
```

## Managing Templates

**List all templates**:
```bash
apitester template list
```

**Show template details**:
```bash
apitester template show my-api --variables
```

**Search templates**:
```bash
apitester template search "user"
```

**Export templates**:
```bash
apitester template export my-templates.json
```

**Import templates**:
```bash
apitester template import shared-templates.json
```

## Variable Substitution

Templates support variable substitution using `\${VARIABLE_NAME}` syntax:

- Variables are resolved from the current environment
- You can override variables using `--var key=value`
- Missing variables will cause validation errors

**Example with variables**:
```bash
# Set environment variables
apitester env set API_BASE https://api.example.com
apitester env set API_VERSION v1

# Create template with variables
apitester template save api-endpoint GET \${API_BASE}/\${API_VERSION}/users

# Execute template (uses environment variables)
apitester request template api-endpoint
```
"""
    },
    
    "environments": {
        "title": "Environment Management",
        "content": r"""
# Environments

Environments help you manage different sets of variables for various deployment stages.

## Basic Environment Operations

**List environments**:
```bash
apitester env list
```

**Create new environment**:
```bash
apitester env create staging --description "Staging environment"
```

**Switch environments**:
```bash
apitester env switch staging
```

**Show current environment**:
```bash
apitester env current
```

## Managing Variables

**Set variables**:
```bash
apitester env set API_URL https://staging-api.example.com
apitester env set API_KEY your-staging-key --sensitive
```

**Get variable value**:
```bash
apitester env get API_URL
```

**Remove variable**:
```bash
apitester env unset API_KEY
```

**List all variables in environment**:
```bash
apitester env list --variables
```

## Environment Operations

**Copy environment**:
```bash
apitester env copy staging production
```

**Export environment**:
```bash
apitester env export staging-vars.json --env staging
```

**Import environment**:
```bash
apitester env import prod-vars.json --env production
```

**Clear all variables**:
```bash
apitester env clear --env staging
```

## Common Patterns

**Development Setup**:
```bash
apitester env create development
apitester env set API_URL http://localhost:3000 --env development
apitester env set DEBUG true --env development
```

**Production Setup**:
```bash
apitester env create production
apitester env set API_URL https://api.production.com --env production
apitester env set API_KEY prod-key-here --env production --sensitive
```

**Using with Templates**:
```bash
# Template uses \${API_URL} and \${API_KEY}
apitester request template my-api --env development  # Uses dev values
apitester request template my-api --env production   # Uses prod values
```
"""
    },
    
    "history": {
        "title": "Request History",
        "content": r"""
# Request History

The history system automatically tracks all your requests for easy replay and analysis.

## Viewing History

**List recent requests**:
```bash
apitester history list
```

**Show detailed history**:
```bash
apitester history list --detailed --limit 10
```

**Filter by method**:
```bash
apitester history list --method POST
```

**Filter by status code**:
```bash
apitester history list --status 200
```

**Filter by time**:
```bash
apitester history list --since 1h    # Last hour
apitester history list --since 2d    # Last 2 days
apitester history list --since "2024-01-01"  # Since specific date
```

**Show only errors**:
```bash
apitester history list --errors-only
```

## Request Details

**Show full request/response**:
```bash
apitester history show REQUEST_ID
```

**Show only request details**:
```bash
apitester history show REQUEST_ID --no-response
```

**Show only response**:
```bash
apitester history show REQUEST_ID --no-request
```

## Retrying Requests

**Retry a request**:
```bash
apitester history retry REQUEST_ID
```

**Retry with different environment**:
```bash
apitester history retry REQUEST_ID --env production
```

**Retry and save response**:
```bash
apitester history retry REQUEST_ID --save response.json
```

## History Management

**Delete specific entries**:
```bash
apitester history delete ENTRY_ID1 ENTRY_ID2
```

**Delete old entries**:
```bash
apitester history delete --older-than 7d
```

**Delete by status code**:
```bash
apitester history delete --status-range 400-499
```

**Clear all history**:
```bash
apitester history delete --all
```

## Export and Analysis

**Export history**:
```bash
apitester history export history.json
apitester history export history.csv --format csv
```

**Show statistics**:
```bash
apitester history stats
apitester history stats --detailed --since 1d
```

## Disabling History

**Disable for single request**:
```bash
apitester request send GET https://api.example.com --no-history
```

**Disable globally** (in config):
```yaml
history:
  enabled: false
```
"""
    },
    
    "completion": {
        "title": "Shell Completion",
        "content": r"""
# Shell Completion

Enable tab completion for faster command entry and discovery.

## Installation

**Bash completion**:
```bash
apitester completion bash --install
source ~/.bashrc
```

**Zsh completion**:
```bash
apitester completion zsh --install
autoload -U compinit && compinit
```

**Fish completion**:
```bash
apitester completion fish --install
fish_update_completions
```

## Manual Installation

**Generate completion script**:
```bash
apitester completion bash > apitester-completion.bash
```

**Add to shell profile**:
```bash
echo "source /path/to/apitester-completion.bash" >> ~/.bashrc
```

## What Gets Completed

- **Commands and subcommands**: `apitester req<TAB>` → `request`
- **HTTP methods**: `apitester request send G<TAB>` → `GET`
- **Template names**: `apitester template show my-<TAB>` → `my-template`
- **Environment names**: `apitester env switch st<TAB>` → `staging`
- **File paths**: `--body-file ./da<TAB>` → `./data.json`
- **Common headers**: `--header Con<TAB>` → `Content-Type`
- **Format options**: `--format j<TAB>` → `json`

## Troubleshooting

**Completion not working?**
1. Ensure completion is installed: `apitester completion bash --install`
2. Restart your shell or source the profile
3. Check if completion directory exists and is in PATH

**Force reinstall**:
```bash
apitester completion bash --install --force
```
"""
    },
    
    "configuration": {
        "title": "Configuration",
        "content": r"""
# Configuration

Customize API Tester behavior through configuration files and environment variables.

## Configuration File

**Default locations**:
- `~/.config/apitester/config.yaml`
- `./apitester.yaml` (project-specific)

**Specify custom config**:
```bash
apitester --config /path/to/config.yaml COMMAND
```

## Configuration Structure

```yaml
redis:
  host: localhost
  port: 6379
  database: 0
  password: null

cache:
  enabled: true
  default_ttl: 3600
  max_entries: 10000

history:
  enabled: true
  max_entries: 50000
  auto_cleanup: true

ai:
  enabled: false
  provider: openai
  model: gpt-3.5-turbo
  api_key: null

output:
  color_enabled: true
  pretty_print: true
  json_indent: 2
  table_style: "simple"

timeout: 30
current_environment: default
```

## Viewing Configuration

**Show current config**:
```bash
apitester config
```

**Show all details**:
```bash
apitester config --all
```

**Export as JSON**:
```bash
apitester config --format json
```

## Runtime Overrides

**Override Redis settings**:
```bash
apitester --redis-host redis.example.com --redis-port 6380 COMMAND
```

**Disable features**:
```bash
apitester --no-cache --no-history request send GET https://api.example.com
```

## Environment Variables

Some settings can be overridden with environment variables:

```bash
export APITESTER_REDIS_HOST=redis.example.com
export APITESTER_REDIS_PORT=6380
export APITESTER_DEBUG=true
```

## Common Configurations

**Minimal setup** (no Redis):
```yaml
cache:
  enabled: false
history:
  enabled: false
```

**High-performance setup**:
```yaml
cache:
  enabled: true
  default_ttl: 7200
  max_entries: 100000
history:
  max_entries: 100000
timeout: 60
```

**Development setup**:
```yaml
output:
  color_enabled: true
  pretty_print: true
  json_indent: 2
current_environment: development
```
"""
    },
    
    "troubleshooting": {
        "title": "Troubleshooting",
        "content": r"""
# Troubleshooting

Common issues and their solutions.

## System Diagnostics

**Run health checks**:
```bash
apitester doctor
```

**Check system status**:
```bash
apitester status
```

## Redis Issues

**Redis connection failed**:
1. Check if Redis is running: `redis-cli ping`
2. Verify host/port in config: `apitester config`
3. Check firewall settings
4. Try connecting manually: `redis-cli -h HOST -p PORT`

**Redis authentication**:
```yaml
redis:
  host: localhost
  port: 6379
  password: your-password
```

**Redis not installed**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

## Template Issues

**Template not found**:
```bash
apitester template list  # Check available templates
apitester template search "partial-name"
```

**Variable substitution errors**:
```bash
apitester template validate my-template --env current
apitester env list --variables  # Check available variables
```

**Template validation failed**:
- Check JSON syntax in body
- Verify all required variables are set
- Ensure URL format is correct

## Environment Issues

**Environment not found**:
```bash
apitester env list  # Show all environments
apitester env create missing-env
```

**Variables not resolving**:
```bash
apitester env current  # Check current environment
apitester env get VARIABLE_NAME  # Check specific variable
```

## Network Issues

**Request timeouts**:
```bash
apitester request send GET https://api.example.com --timeout 60
```

**SSL certificate errors**:
```bash
apitester request send GET https://api.example.com --no-verify-ssl
```

**Proxy configuration**:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Performance Issues

**Slow responses**:
- Check network connectivity
- Increase timeout: `--timeout 120`
- Disable cache temporarily: `--no-cache`

**High memory usage**:
- Clear history: `apitester history delete --all`
- Clear cache: Configure lower `max_entries`
- Reduce `history.max_entries` in config

## Debug Mode

**Enable verbose logging**:
```bash
apitester --verbose COMMAND
```

**Enable debug mode**:
```bash
apitester --debug COMMAND
```

## Getting Help

**Command-specific help**:
```bash
apitester COMMAND --help
apitester COMMAND SUBCOMMAND --help
```

**Show examples**:
```bash
apitester help examples
```

**Report issues**:
- Check existing issues on GitHub
- Include output from `apitester doctor`
- Provide minimal reproduction steps
"""
    },
    
    "examples": {
        "title": "Common Examples",
        "content": r"""
# Common Examples

Real-world usage patterns and examples.

## REST API Testing

**Basic CRUD operations**:
```bash
# GET - List resources
apitester request send GET https://jsonplaceholder.typicode.com/posts

# POST - Create resource
apitester request send POST https://jsonplaceholder.typicode.com/posts \\
  --header "Content-Type: application/json" \\
  --body '{"title": "My Post", "body": "Content", "userId": 1}'

# PUT - Update resource
apitester request send PUT https://jsonplaceholder.typicode.com/posts/1 \\
  --header "Content-Type: application/json" \\
  --body '{"id": 1, "title": "Updated", "body": "New content", "userId": 1}'

# DELETE - Remove resource
apitester request send DELETE https://jsonplaceholder.typicode.com/posts/1
```

**Authentication examples**:
```bash
# Bearer token
apitester request send GET https://api.github.com/user \\
  --header "Authorization: Bearer ghp_xxxxxxxxxxxx"

# API key in header
apitester request send GET https://api.example.com/data \\
  --header "X-API-Key: your-api-key"

# Basic auth
apitester request send GET https://api.example.com/secure \\
  --header "Authorization: Basic $(echo -n 'user:pass' | base64)"
```

## GraphQL Testing

**Simple query**:
```bash
apitester request graphql https://api.github.com/graphql \\
  --header "Authorization: Bearer YOUR_TOKEN" \\
  --query 'query { viewer { login name } }'
```

**Query with variables**:
```bash
apitester request graphql https://api.github.com/graphql \\
  --header "Authorization: Bearer YOUR_TOKEN" \\
  --query 'query($login: String!) { user(login: $login) { name bio } }' \\
  --variables '{"login": "octocat"}'
```

**Mutation**:
```bash
apitester request graphql https://api.github.com/graphql \\
  --header "Authorization: Bearer YOUR_TOKEN" \\
  --query 'mutation($input: CreateIssueInput!) { createIssue(input: $input) { issue { number title } } }' \\
  --variables '{"input": {"repositoryId": "REPO_ID", "title": "Bug report"}}'
```

## Template Workflows

**API testing suite**:
```bash
# Create environment
apitester env create api-testing
apitester env set BASE_URL https://api.example.com --env api-testing
apitester env set API_KEY your-key-here --env api-testing

# Create templates
apitester template save list-users GET \${BASE_URL}/users \\
  --header "Authorization: Bearer \${API_KEY}" \\
  --tag "users"

apitester template save create-user POST \${BASE_URL}/users \\
  --header "Authorization: Bearer \${API_KEY}" \\
  --header "Content-Type: application/json" \\
  --body '{"name": "\${USER_NAME}", "email": "\${USER_EMAIL}"}' \\
  --tag "users"

apitester template save get-user GET \${BASE_URL}/users/\${USER_ID} \\
  --header "Authorization: Bearer \${API_KEY}" \\
  --tag "users"

# Execute test suite
apitester env switch api-testing
apitester request template list-users
apitester request template create-user --var "USER_NAME=Test User" --var "USER_EMAIL=test@example.com"
apitester request template get-user --var "USER_ID=123"
```

## File Operations

**Upload file**:
```bash
apitester request send POST https://httpbin.org/post \\
  --header "Content-Type: multipart/form-data" \\
  --body-file ./upload.json
```

**Save response to file**:
```bash
apitester request send GET https://api.github.com/repos/microsoft/vscode \\
  --save repo-info.json
```

**Batch processing**:
```bash
# Create batch config file
cat > batch-requests.json << EOF
{
  "requests": [
    {
      "name": "get-user-1",
      "template": "get-user",
      "variables": {"USER_ID": "1"}
    },
    {
      "name": "get-user-2", 
      "template": "get-user",
      "variables": {"USER_ID": "2"}
    }
  ]
}
EOF

# Execute batch
apitester request batch batch-requests.json --save-dir ./responses/
```

## Monitoring and Analysis

**API health check**:
```bash
# Create health check template
apitester template save health-check GET \${API_URL}/health \\
  --description "API health endpoint"

# Regular health checks
apitester request template health-check
apitester history list --limit 5 --method GET
```

**Performance testing**:
```bash
# Test response times
for i in {1..10}; do
  apitester request send GET https://api.example.com/fast-endpoint
done

# Analyze performance
apitester history stats --since 5m --detailed
```

**Error analysis**:
```bash
# Show recent errors
apitester history list --errors-only --limit 10

# Export error details
apitester history export errors.json --since 1d --method POST
```

## Integration Examples

**CI/CD Pipeline**:
```bash
#!/bin/bash
# api-test.sh - Integration test script

set -e

# Setup
apitester env create ci-test
apitester env set API_URL $CI_API_URL --env ci-test
apitester env set API_KEY $CI_API_KEY --env ci-test

# Run tests
apitester env switch ci-test
apitester request template health-check
apitester request template user-crud-test

# Check results
if apitester history list --since 1m --errors-only | grep -q "Error"; then
  echo "API tests failed"
  exit 1
else
  echo "API tests passed"
fi
```

**Load testing preparation**:
```bash
# Create load test templates
apitester template save load-test-endpoint GET \${TARGET_URL}/api/data \\
  --header "Authorization: Bearer \${LOAD_TEST_TOKEN}"

# Export for external tools
apitester template export load-tests.json --template load-test-endpoint
```
"""
    }
}

# Command examples organized by category
COMMAND_EXAMPLES = {
    "request": [
        {
            "description": "Simple GET request",
            "command": "apitester request send GET https://jsonplaceholder.typicode.com/posts/1"
        },
        {
            "description": "POST with JSON body",
            "command": "apitester request send POST https://httpbin.org/post --header \"Content-Type: application/json\" --body '{\"key\": \"value\"}'"
        },
        {
            "description": "Request with custom headers",
            "command": "apitester request send GET https://api.github.com/user --header \"Authorization: Bearer YOUR_TOKEN\""
        },
        {
            "description": "Save response to file",
            "command": "apitester request send GET https://api.github.com/repos/microsoft/vscode --save repo-info.json"
        },
        {
            "description": "GraphQL query",
            "command": "apitester request graphql https://api.github.com/graphql --header \"Authorization: Bearer TOKEN\" --query 'query { viewer { login } }'"
        }
    ],
    "template": [
        {
            "description": "Save a template",
            "command": "apitester template save github-user GET https://api.github.com/user --header \"Authorization: Bearer ${GITHUB_TOKEN}\""
        },
        {
            "description": "List all templates",
            "command": "apitester template list --detailed"
        },
        {
            "description": "Execute a template",
            "command": "apitester request template github-user"
        },
        {
            "description": "Export templates",
            "command": "apitester template export my-templates.json"
        }
    ],
    "env": [
        {
            "description": "Create environment",
            "command": "apitester env create staging --description \"Staging environment\""
        },
        {
            "description": "Set environment variable",
            "command": "apitester env set API_KEY your-key-here --sensitive"
        },
        {
            "description": "Switch environment",
            "command": "apitester env switch production"
        },
        {
            "description": "Export environment",
            "command": "apitester env export staging-vars.json --env staging"
        }
    ],
    "history": [
        {
            "description": "List recent requests",
            "command": "apitester history list --limit 10"
        },
        {
            "description": "Show request details",
            "command": "apitester history show REQUEST_ID"
        },
        {
            "description": "Retry a request",
            "command": "apitester history retry REQUEST_ID --env production"
        },
        {
            "description": "Show statistics",
            "command": "apitester history stats --detailed --since 1d"
        }
    ]
}


def show_help_topic(topic: str) -> None:
    """Show help for a specific topic."""
    if topic not in HELP_TOPICS:
        console.print(f"[red]Unknown help topic: {topic}[/red]")
        console.print(f"Available topics: {', '.join(HELP_TOPICS.keys())}")
        return
    
    topic_info = HELP_TOPICS[topic]
    
    # Render markdown content
    markdown = Markdown(topic_info["content"])
    
    panel = Panel(
        markdown,
        title=f"Help: {topic_info['title']}",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)


def show_command_examples(command: Optional[str] = None) -> None:
    """Show examples for commands."""
    if command and command in COMMAND_EXAMPLES:
        # Show examples for specific command
        examples = COMMAND_EXAMPLES[command]
        
        table = Table(title=f"{command.title()} Command Examples", show_header=True, header_style="bold blue")
        table.add_column("Description", style="cyan")
        table.add_column("Command", style="white")
        
        for example in examples:
            table.add_row(example["description"], example["command"])
        
        console.print(table)
    
    else:
        # Show all examples organized by command
        for cmd, examples in COMMAND_EXAMPLES.items():
            console.print(f"\n[bold blue]{cmd.title()} Examples:[/bold blue]")
            
            for i, example in enumerate(examples, 1):
                console.print(f"  [cyan]{i}. {example['description']}[/cyan]")
                console.print(f"     [dim]{example['command']}[/dim]")


def show_help_overview() -> None:
    """Show overview of available help topics."""
    console.print("[bold blue]API Tester Help System[/bold blue]\n")
    
    console.print("Available help topics:")
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Topic", style="cyan")
    table.add_column("Description", style="white")
    
    topic_descriptions = {
        "getting-started": "Quick start guide and basic usage",
        "templates": "Creating and managing request templates",
        "environments": "Environment and variable management",
        "history": "Request history and replay functionality",
        "completion": "Shell completion setup and usage",
        "configuration": "Configuration files and settings",
        "troubleshooting": "Common issues and solutions",
        "examples": "Real-world usage examples"
    }
    
    for topic, info in HELP_TOPICS.items():
        description = topic_descriptions.get(topic, info["title"])
        table.add_row(topic, description)
    
    console.print(table)
    
    console.print(f"\n[dim]Usage: apitester help TOPIC[/dim]")
    console.print(f"[dim]Examples: apitester help examples[/dim]")


# Create help app
help_app = typer.Typer(
    name="help",
    help="Comprehensive help system",
    rich_markup_mode="rich"
)


@help_app.callback(invoke_without_command=True)
def help_main(
    ctx: typer.Context,
    topic: Optional[str] = typer.Argument(None, help="Help topic to display")
) -> None:
    """Show help information."""
    if topic:
        if topic == "examples":
            show_command_examples()
        else:
            show_help_topic(topic)
    else:
        show_help_overview()


@help_app.command("examples")
def show_examples(
    command: Optional[str] = typer.Argument(None, help="Show examples for specific command")
) -> None:
    """Show command examples."""
    show_command_examples(command)


@help_app.command("topics")
def list_topics() -> None:
    """List all available help topics."""
    show_help_overview()


@help_app.command("search")
def search_help(
    query: str = typer.Argument(..., help="Search term"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", help="Case sensitive search")
) -> None:
    """Search help content."""
    results = []
    
    search_query = query if case_sensitive else query.lower()
    
    for topic, info in HELP_TOPICS.items():
        content = info["content"] if case_sensitive else info["content"].lower()
        title = info["title"] if case_sensitive else info["title"].lower()
        
        if search_query in content or search_query in title:
            # Find context around matches
            lines = info["content"].split('\n')
            matching_lines = []
            
            for i, line in enumerate(lines):
                check_line = line if case_sensitive else line.lower()
                if search_query in check_line:
                    # Add context (line before and after)
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    context = lines[start:end]
                    matching_lines.extend(context)
            
            results.append({
                "topic": topic,
                "title": info["title"],
                "matches": matching_lines[:5]  # Limit to first 5 matches
            })
    
    if not results:
        console.print(f"[yellow]No help content found matching '{query}'[/yellow]")
        return
    
    console.print(f"[bold blue]Search Results for '{query}':[/bold blue]\n")
    
    for result in results:
        console.print(f"[bold cyan]{result['topic']}[/bold cyan] - {result['title']}")
        
        for match in result['matches']:
            if match.strip():
                # Highlight search term
                if not case_sensitive:
                    highlighted = match.replace(query, f"[yellow]{query}[/yellow]")
                else:
                    highlighted = match.replace(query, f"[yellow]{query}[/yellow]")
                console.print(f"  {highlighted}")
        
        console.print()
    
    console.print(f"[dim]Use 'apitester help TOPIC' to view full help for a topic[/dim]")


if __name__ == "__main__":
    help_app()
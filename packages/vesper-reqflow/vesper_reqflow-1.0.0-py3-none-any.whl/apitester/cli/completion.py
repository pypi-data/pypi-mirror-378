"""Shell completion support for the CLI."""

import typer
from typing import List, Optional
from pathlib import Path

from ..core.template_manager import TemplateManager
from ..core.env_manager import EnvironmentManager


def complete_template_names(incomplete: str) -> List[str]:
    """Complete template names."""
    try:
        template_manager = TemplateManager()
        templates = template_manager.list_templates()
        return [name for name in templates if name.startswith(incomplete)]
    except Exception:
        return []


def complete_environment_names(incomplete: str) -> List[str]:
    """Complete environment names."""
    try:
        env_manager = EnvironmentManager()
        environments = env_manager.list_environments()
        return [name for name in environments if name.startswith(incomplete)]
    except Exception:
        return []


def complete_http_methods(incomplete: str) -> List[str]:
    """Complete HTTP method names."""
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    return [method for method in methods if method.startswith(incomplete.upper())]


def complete_file_paths(incomplete: str) -> List[str]:
    """Complete file paths."""
    try:
        path = Path(incomplete)
        if path.is_dir():
            # Complete files in directory
            return [str(p) for p in path.iterdir() if p.name.startswith("")]
        else:
            # Complete based on parent directory
            parent = path.parent
            name_start = path.name
            if parent.exists():
                return [
                    str(parent / p.name) 
                    for p in parent.iterdir() 
                    if p.name.startswith(name_start)
                ]
    except Exception:
        pass
    return []


def complete_export_formats(incomplete: str) -> List[str]:
    """Complete export format names."""
    formats = ["json", "yaml", "csv", "env"]
    return [fmt for fmt in formats if fmt.startswith(incomplete.lower())]


def complete_variable_names(incomplete: str, environment: Optional[str] = None) -> List[str]:
    """Complete environment variable names."""
    try:
        env_manager = EnvironmentManager()
        
        if not environment:
            environment = env_manager.get_current_environment()
        
        if env_manager.environment_exists(environment):
            variables = env_manager.get_environment_variables(environment)
            return [name for name in variables.keys() if name.startswith(incomplete)]
    except Exception:
        pass
    return []


def complete_common_headers(incomplete: str) -> List[str]:
    """Complete common HTTP header names."""
    headers = [
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Authorization",
        "Cache-Control",
        "Content-Type",
        "Content-Length",
        "Cookie",
        "Host",
        "If-Modified-Since",
        "If-None-Match",
        "Origin",
        "Referer",
        "User-Agent",
        "X-API-Key",
        "X-Auth-Token",
        "X-Forwarded-For",
        "X-Requested-With"
    ]
    
    # Handle "Key: Value" format
    if ":" in incomplete:
        key, value_part = incomplete.split(":", 1)
        key = key.strip()
        
        # Complete common values for specific headers
        if key.lower() == "content-type":
            content_types = [
                "application/json",
                "application/xml",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain",
                "text/html",
                "text/csv"
            ]
            return [f"{key}: {ct}" for ct in content_types if ct.startswith(value_part.strip())]
        
        elif key.lower() == "accept":
            accept_types = [
                "application/json",
                "application/xml",
                "text/html",
                "text/plain",
                "*/*"
            ]
            return [f"{key}: {at}" for at in accept_types if at.startswith(value_part.strip())]
        
        elif key.lower() == "authorization":
            auth_types = [
                "Bearer ",
                "Basic ",
                "Digest ",
                "API-Key "
            ]
            return [f"{key}: {at}" for at in auth_types if at.startswith(value_part.strip())]
    
    else:
        # Complete header names
        return [header for header in headers if header.lower().startswith(incomplete.lower())]
    
    return []


def complete_url_schemes(incomplete: str) -> List[str]:
    """Complete URL schemes."""
    schemes = ["http://", "https://"]
    return [scheme for scheme in schemes if scheme.startswith(incomplete.lower())]


def complete_common_urls(incomplete: str) -> List[str]:
    """Complete common API URLs and patterns."""
    common_patterns = [
        "https://api.github.com/",
        "https://jsonplaceholder.typicode.com/",
        "https://httpbin.org/",
        "https://reqres.in/api/",
        "https://api.example.com/",
        "http://localhost:3000/",
        "http://localhost:8000/",
        "http://localhost:8080/"
    ]
    
    return [url for url in common_patterns if url.startswith(incomplete)]


def setup_completion_for_app(app: typer.Typer) -> None:
    """Setup completion callbacks for the main app."""
    
    # This would be called during app initialization to register
    # completion callbacks with typer commands that support them
    
    # Note: Typer's completion system works through callback functions
    # that are registered with specific parameters. The actual completion
    # is handled by the shell completion scripts generated by typer.
    
    pass


def generate_completion_script(shell: str = "bash") -> str:
    """Generate shell completion script."""
    
    if shell == "bash":
        return '''
# Bash completion for apitester
_apitester_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Basic command completion
    if [[ ${COMP_CWORD} == 1 ]]; then
        opts="request template env history config version status doctor"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
    
    # Subcommand completion
    case "${COMP_WORDS[1]}" in
        request)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="send graphql template batch"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ ${COMP_WORDS[2]} == "send" && ${COMP_CWORD} == 3 ]]; then
                opts="GET POST PUT PATCH DELETE HEAD OPTIONS"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        template)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="save list show delete export import search duplicate validate"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        env)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="list create delete current switch set get unset export import copy clear"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        history)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="list show retry delete export stats"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
    esac
    
    # File completion for certain options
    case "${prev}" in
        --body-file|--query-file|--save|--config|--export|--import)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            ;;
        --format)
            opts="json yaml csv env table"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
    esac
}

complete -F _apitester_completion apitester
'''
    
    elif shell == "zsh":
        return '''
#compdef apitester

_apitester() {
    local context state line
    typeset -A opt_args
    
    _arguments -C \\
        '1: :_apitester_commands' \\
        '*::arg:->args'
    
    case $state in
        args)
            case $words[1] in
                request)
                    _apitester_request
                    ;;
                template)
                    _apitester_template
                    ;;
                env)
                    _apitester_env
                    ;;
                history)
                    _apitester_history
                    ;;
            esac
            ;;
    esac
}

_apitester_commands() {
    local commands
    commands=(
        'request:Execute HTTP and GraphQL requests'
        'template:Manage request templates'
        'env:Manage environment variables'
        'history:View and manage request history'
        'config:Show configuration'
        'version:Show version information'
        'status:Show system status'
        'doctor:Run diagnostic checks'
    )
    _describe 'commands' commands
}

_apitester_request() {
    local commands
    commands=(
        'send:Send HTTP request'
        'graphql:Send GraphQL request'
        'template:Execute template'
        'batch:Execute batch requests'
    )
    _describe 'request commands' commands
}

_apitester_template() {
    local commands
    commands=(
        'save:Save request as template'
        'list:List templates'
        'show:Show template details'
        'delete:Delete template'
        'export:Export templates'
        'import:Import templates'
        'search:Search templates'
        'duplicate:Duplicate template'
        'validate:Validate template'
    )
    _describe 'template commands' commands
}

_apitester_env() {
    local commands
    commands=(
        'list:List environments'
        'create:Create environment'
        'delete:Delete environment'
        'current:Show current environment'
        'switch:Switch environment'
        'set:Set variable'
        'get:Get variable'
        'unset:Remove variable'
        'export:Export environment'
        'import:Import environment'
        'copy:Copy environment'
        'clear:Clear environment'
    )
    _describe 'environment commands' commands
}

_apitester_history() {
    local commands
    commands=(
        'list:List history'
        'show:Show history entry'
        'retry:Retry request'
        'delete:Delete entries'
        'export:Export history'
        'stats:Show statistics'
    )
    _describe 'history commands' commands
}

_apitester "$@"
'''
    
    elif shell == "fish":
        return '''
# Fish completion for apitester

# Main commands
complete -c apitester -n "__fish_use_subcommand" -a "request" -d "Execute HTTP and GraphQL requests"
complete -c apitester -n "__fish_use_subcommand" -a "template" -d "Manage request templates"
complete -c apitester -n "__fish_use_subcommand" -a "env" -d "Manage environment variables"
complete -c apitester -n "__fish_use_subcommand" -a "history" -d "View and manage request history"
complete -c apitester -n "__fish_use_subcommand" -a "config" -d "Show configuration"
complete -c apitester -n "__fish_use_subcommand" -a "version" -d "Show version information"
complete -c apitester -n "__fish_use_subcommand" -a "status" -d "Show system status"
complete -c apitester -n "__fish_use_subcommand" -a "doctor" -d "Run diagnostic checks"

# Request subcommands
complete -c apitester -n "__fish_seen_subcommand_from request" -a "send" -d "Send HTTP request"
complete -c apitester -n "__fish_seen_subcommand_from request" -a "graphql" -d "Send GraphQL request"
complete -c apitester -n "__fish_seen_subcommand_from request" -a "template" -d "Execute template"
complete -c apitester -n "__fish_seen_subcommand_from request" -a "batch" -d "Execute batch requests"

# HTTP methods for request send
complete -c apitester -n "__fish_seen_subcommand_from send" -a "GET POST PUT PATCH DELETE HEAD OPTIONS"

# Template subcommands
complete -c apitester -n "__fish_seen_subcommand_from template" -a "save list show delete export import search duplicate validate"

# Environment subcommands
complete -c apitester -n "__fish_seen_subcommand_from env" -a "list create delete current switch set get unset export import copy clear"

# History subcommands
complete -c apitester -n "__fish_seen_subcommand_from history" -a "list show retry delete export stats"

# Common options
complete -c apitester -l help -d "Show help message"
complete -c apitester -l version -d "Show version"
complete -c apitester -l verbose -s v -d "Enable verbose output"
complete -c apitester -l debug -d "Enable debug mode"
complete -c apitester -l config -s c -d "Configuration file" -F
complete -c apitester -l format -s f -a "json yaml csv env table" -d "Output format"
'''
    
    else:
        raise ValueError(f"Unsupported shell: {shell}")


def install_completion(shell: str, force: bool = False) -> bool:
    """Install shell completion script."""
    
    completion_script = generate_completion_script(shell)
    
    if shell == "bash":
        # Try to install in bash completion directory
        completion_dirs = [
            Path.home() / ".bash_completion.d",
            Path("/usr/local/etc/bash_completion.d"),
            Path("/etc/bash_completion.d")
        ]
        
        for completion_dir in completion_dirs:
            if completion_dir.exists() or completion_dir.parent.exists():
                try:
                    completion_dir.mkdir(exist_ok=True)
                    completion_file = completion_dir / "apitester"
                    
                    if completion_file.exists() and not force:
                        return False  # Already exists
                    
                    completion_file.write_text(completion_script)
                    return True
                except PermissionError:
                    continue
        
        # Fallback: add to .bashrc
        bashrc = Path.home() / ".bashrc"
        if bashrc.exists():
            bashrc_content = bashrc.read_text()
            if "apitester" not in bashrc_content or force:
                with bashrc.open("a") as f:
                    f.write(f"\n# Apitester completion\n{completion_script}\n")
                return True
    
    elif shell == "zsh":
        # Install in zsh completion directory
        zsh_completion_dirs = [
            Path.home() / ".zsh" / "completions",
            Path("/usr/local/share/zsh/site-functions"),
            Path("/usr/share/zsh/site-functions")
        ]
        
        for completion_dir in zsh_completion_dirs:
            if completion_dir.exists() or completion_dir.parent.exists():
                try:
                    completion_dir.mkdir(parents=True, exist_ok=True)
                    completion_file = completion_dir / "_apitester"
                    
                    if completion_file.exists() and not force:
                        return False
                    
                    completion_file.write_text(completion_script)
                    return True
                except PermissionError:
                    continue
    
    elif shell == "fish":
        # Install in fish completion directory
        fish_completion_dir = Path.home() / ".config" / "fish" / "completions"
        
        try:
            fish_completion_dir.mkdir(parents=True, exist_ok=True)
            completion_file = fish_completion_dir / "apitester.fish"
            
            if completion_file.exists() and not force:
                return False
            
            completion_file.write_text(completion_script)
            return True
        except PermissionError:
            pass
    
    return False


# Completion callback functions for typer
def template_name_completion():
    """Completion callback for template names."""
    def callback(incomplete: str):
        return complete_template_names(incomplete)
    return callback


def environment_name_completion():
    """Completion callback for environment names."""
    def callback(incomplete: str):
        return complete_environment_names(incomplete)
    return callback


def http_method_completion():
    """Completion callback for HTTP methods."""
    def callback(incomplete: str):
        return complete_http_methods(incomplete)
    return callback


def export_format_completion():
    """Completion callback for export formats."""
    def callback(incomplete: str):
        return complete_export_formats(incomplete)
    return callback
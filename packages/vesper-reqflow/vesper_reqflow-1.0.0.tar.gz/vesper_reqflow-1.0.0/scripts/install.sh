#!/bin/bash

# ReqFlow Installation Script
# This script installs the CLI tool and its dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
REDIS_MIN_VERSION="6.0"
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/reqflow"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                      ReqFlow                                 ║"
    echo "║                    Installation Script                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

version_compare() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

check_python() {
    print_step "Checking Python installation..."
    
    if ! check_command python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    
    if version_compare "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        print_success "Python $PYTHON_VERSION found (>= $PYTHON_MIN_VERSION required)"
    else
        print_error "Python $PYTHON_VERSION found, but $PYTHON_MIN_VERSION or higher is required"
        exit 1
    fi
}

check_pip() {
    print_step "Checking pip installation..."
    
    if ! check_command pip3; then
        print_warning "pip3 not found, attempting to install..."
        python3 -m ensurepip --upgrade
    fi
    
    print_success "pip is available"
}

check_redis() {
    print_step "Checking Redis installation..."
    
    if check_command redis-server; then
        REDIS_VERSION=$(redis-server --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if version_compare "$REDIS_VERSION" "$REDIS_MIN_VERSION"; then
            print_success "Redis $REDIS_VERSION found (>= $REDIS_MIN_VERSION required)"
            return 0
        else
            print_warning "Redis $REDIS_VERSION found, but $REDIS_MIN_VERSION or higher is recommended"
        fi
    else
        print_warning "Redis not found. Installing Redis is recommended for full functionality."
        echo "Please install Redis using your system package manager:"
        echo "  Ubuntu/Debian: sudo apt install redis-server"
        echo "  macOS: brew install redis"
        echo "  CentOS/RHEL: sudo yum install redis"
        echo ""
        read -p "Continue without Redis? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

install_package() {
    print_step "Installing Agentic API Tester CLI..."
    
    # Check if we should install with AI features
    echo "Installation options:"
    echo "1. Basic installation (HTTP client, templates, history)"
    echo "2. Full installation with AI features (requires API keys)"
    echo "3. Development installation (includes testing tools)"
    echo ""
    read -p "Choose installation type (1-3) [1]: " INSTALL_TYPE
    INSTALL_TYPE=${INSTALL_TYPE:-1}
    
    case $INSTALL_TYPE in
        1)
            pip3 install --user reqflow
            ;;
        2)
            pip3 install --user "reqflow[ai]"
            ;;
        3)
            pip3 install --user "reqflow[dev,ai]"
            ;;
        *)
            print_error "Invalid option. Using basic installation."
            pip3 install --user reqflow
            ;;
    esac
    
    print_success "Package installed successfully"
}

setup_config() {
    print_step "Setting up configuration..."
    
    # Create config directory
    mkdir -p "$CONFIG_DIR"
    
    # Create default configuration if it doesn't exist
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        cat > "$CONFIG_DIR/config.yaml" << EOF
# Agentic API Tester CLI Configuration

redis:
  host: localhost
  port: 6379
  database: 0
  # password: your-redis-password

cache:
  enabled: true
  default_ttl: 3600  # 1 hour

history:
  enabled: true
  max_entries: 10000

ai:
  enabled: false
  provider: openai  # openai, anthropic, gemini
  model: gpt-3.5-turbo
  # api_key: your-api-key (use environment variable instead)

output:
  format: auto  # auto, json, table, yaml
  colors: true
  show_headers: false
  show_timing: true

logging:
  level: INFO
  file: ~/.local/share/apitester/logs/apitester.log
EOF
        print_success "Created default configuration at $CONFIG_DIR/config.yaml"
    else
        print_warning "Configuration file already exists at $CONFIG_DIR/config.yaml"
    fi
}

setup_shell_completion() {
    print_step "Setting up shell completion..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case $SHELL_NAME in
        bash)
            COMPLETION_FILE="$HOME/.bash_completion"
            if [ -f "$HOME/.bashrc" ]; then
                if ! grep -q "apitester completion" "$HOME/.bashrc"; then
                    echo "" >> "$HOME/.bashrc"
                    echo "# Agentic API Tester CLI completion" >> "$HOME/.bashrc"
                    echo 'eval "$(_APITESTER_COMPLETE=bash_source apitester)"' >> "$HOME/.bashrc"
                    print_success "Added bash completion to ~/.bashrc"
                fi
            fi
            ;;
        zsh)
            if [ -f "$HOME/.zshrc" ]; then
                if ! grep -q "apitester completion" "$HOME/.zshrc"; then
                    echo "" >> "$HOME/.zshrc"
                    echo "# Agentic API Tester CLI completion" >> "$HOME/.zshrc"
                    echo 'eval "$(_APITESTER_COMPLETE=zsh_source apitester)"' >> "$HOME/.zshrc"
                    print_success "Added zsh completion to ~/.zshrc"
                fi
            fi
            ;;
        fish)
            FISH_COMPLETION_DIR="$HOME/.config/fish/completions"
            mkdir -p "$FISH_COMPLETION_DIR"
            if [ ! -f "$FISH_COMPLETION_DIR/apitester.fish" ]; then
                echo 'complete -c apitester -f -a "(_APITESTER_COMPLETE=fish_source apitester)"' > "$FISH_COMPLETION_DIR/apitester.fish"
                print_success "Added fish completion"
            fi
            ;;
        *)
            print_warning "Unknown shell: $SHELL_NAME. Shell completion not configured."
            ;;
    esac
}

check_installation() {
    print_step "Verifying installation..."
    
    # Check if apitester command is available
    if check_command apitester; then
        VERSION=$(apitester --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
        print_success "apitester command is available (version: $VERSION)"
    else
        print_error "apitester command not found in PATH"
        print_warning "You may need to add $INSTALL_DIR to your PATH"
        echo "Add this line to your shell profile:"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\""
        return 1
    fi
    
    # Test basic functionality
    if apitester status >/dev/null 2>&1; then
        print_success "Basic functionality test passed"
    else
        print_warning "Basic functionality test failed (this may be normal if Redis is not running)"
    fi
    
    return 0
}

setup_ai_config() {
    if [ "$INSTALL_TYPE" = "2" ] || [ "$INSTALL_TYPE" = "3" ]; then
        print_step "Setting up AI configuration..."
        echo ""
        echo "To use AI features, you'll need API keys from supported providers:"
        echo "1. OpenAI: https://platform.openai.com/api-keys"
        echo "2. Anthropic: https://console.anthropic.com/"
        echo "3. Google Gemini: https://makersuite.google.com/app/apikey"
        echo ""
        echo "Set your API key as an environment variable:"
        echo "  export OPENAI_API_KEY='your-key-here'"
        echo "  export ANTHROPIC_API_KEY='your-key-here'"
        echo "  export GOOGLE_API_KEY='your-key-here'"
        echo ""
        echo "Then enable AI in the configuration:"
        echo "  apitester ai configure --provider openai --enable"
        echo ""
    fi
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
    echo -e "║                     Installation Complete!                   ║"
    echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Test the installation: apitester --help"
    echo "3. Send your first request: apitester request send GET https://httpbin.org/get"
    echo "4. Read the documentation: apitester help"
    echo ""
    echo "Configuration file: $CONFIG_DIR/config.yaml"
    echo "Documentation: https://reqflow.readthedocs.io/"
    echo "GitHub: https://github.com/VesperAkshay/ReqFlow"
    echo ""
    echo "Happy API testing! 🚀"
}

# Main installation flow
main() {
    print_header
    
    # Check prerequisites
    check_python
    check_pip
    check_redis
    
    # Install package
    install_package
    
    # Setup configuration
    setup_config
    setup_shell_completion
    
    # Setup AI if requested
    setup_ai_config
    
    # Verify installation
    if check_installation; then
        print_next_steps
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Agentic API Tester CLI Installation Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --uninstall    Uninstall the CLI tool"
        echo "  --update       Update to the latest version"
        echo ""
        exit 0
        ;;
    --uninstall)
        print_step "Uninstalling ReqFlow..."
        pip3 uninstall -y reqflow
        print_success "Uninstalled successfully"
        echo "Configuration files in $CONFIG_DIR were not removed"
        exit 0
        ;;
    --update)
        print_step "Updating ReqFlow..."
        pip3 install --user --upgrade reqflow
        print_success "Updated successfully"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
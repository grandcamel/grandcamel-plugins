#!/usr/bin/env bash
#
# AS-Plugins Setup Wizard
# Creates Python virtual environment and runs interactive setup
#
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory (where as-plugins is cloned)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Detect if virtualenv activation exists in a file
check_venv_in_file() {
    local file="$1"
    [[ -f "$file" ]] && grep -q "as-plugins-venv" "$file"
}

# Find existing as-plugins venv configuration
# Returns: "active:<path>" | "file:<config_file_path>" | exits with 1 if not found
detect_existing_venv() {
    # 1. Active venv
    if [[ -n "$VIRTUAL_ENV" && "$VIRTUAL_ENV" == *"as-plugins"* ]]; then
        echo "active:$VIRTUAL_ENV"
        return 0
    fi

    # 2-3. Check .d directories
    for rc_d in "$HOME/.bashrc.d/50-as-plugins.sh" "$HOME/.zshrc.d/50-as-plugins.sh"; do
        if check_venv_in_file "$rc_d"; then
            echo "file:$rc_d"
            return 0
        fi
    done

    # 4-5. Check rc files directly
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if check_venv_in_file "$rc"; then
            echo "file:$rc"
            return 0
        fi
    done

    return 1
}

# Extract venv path from a config file
extract_venv_path_from_file() {
    local file="$1"
    # Look for: source "/path/to/as-plugins-venv/bin/activate" or source '/path/...' or source path/...
    grep -oE '(source|\.)[[:space:]]+["'"'"']?[^"'"'"'[:space:]]*as-plugins-venv[^"'"'"'[:space:]]*["'"'"']?' "$file" 2>/dev/null | \
        sed -E 's/(source|\.)//; s/[[:space:]]+//g; s/["'"'"']//g; s|/bin/activate||' | \
        head -1
}

# Configure shell activation for new venv
configure_shell_activation() {
    local venv_dir="$1"
    local activation_line="source \"$venv_dir/bin/activate\""
    local configured=false

    # Prefer .d directories if they exist
    if [[ -d "$HOME/.bashrc.d" ]]; then
        echo "$activation_line" > "$HOME/.bashrc.d/50-as-plugins.sh"
        echo -e "${GREEN}  ✓ Created ~/.bashrc.d/50-as-plugins.sh${NC}"
        configured=true
    fi

    if [[ -d "$HOME/.zshrc.d" ]]; then
        echo "$activation_line" > "$HOME/.zshrc.d/50-as-plugins.sh"
        echo -e "${GREEN}  ✓ Created ~/.zshrc.d/50-as-plugins.sh${NC}"
        configured=true
    fi

    # Fallback: append to rc files if no .d directories used
    if [[ "$configured" != "true" ]]; then
        if [[ -f "$HOME/.bashrc" ]]; then
            echo "" >> "$HOME/.bashrc"
            echo "# AS-Plugins virtualenv" >> "$HOME/.bashrc"
            echo "$activation_line" >> "$HOME/.bashrc"
            echo -e "${GREEN}  ✓ Added activation to ~/.bashrc${NC}"
        fi
        if [[ -f "$HOME/.zshrc" ]]; then
            echo "" >> "$HOME/.zshrc"
            echo "# AS-Plugins virtualenv" >> "$HOME/.zshrc"
            echo "$activation_line" >> "$HOME/.zshrc"
            echo -e "${GREEN}  ✓ Added activation to ~/.zshrc${NC}"
        fi
    fi
}

# Parse arguments
FORCE=false
SKIP_PLUGINS=false
NO_KEYCHAIN=false
PLATFORMS=""
VALIDATE_ONLY=false
SKIP_CREDENTIALS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=true
            shift
            ;;
        --skip-plugins)
            SKIP_PLUGINS=true
            shift
            ;;
        --no-keychain)
            NO_KEYCHAIN=true
            shift
            ;;
        --platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --skip-credentials)
            SKIP_CREDENTIALS=true
            shift
            ;;
        --help|-h)
            echo "AS-Plugins Setup Wizard"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --force, -f        Force recreation of virtual environment"
            echo "  --skip-plugins     Skip Claude Code plugin installation"
            echo "  --no-keychain      Don't use OS keychain for token storage"
            echo "  --platforms        Comma-separated platforms (confluence,jira,splunk)"
            echo "  --validate-only    Validate existing credentials and exit"
            echo "  --skip-credentials Skip credential prompts, install packages/plugins only"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}"
echo "╭──────────────────────────────────────────────────╮"
echo "│       Assistant Skills - Setup Wizard            │"
echo "│                                                  │"
echo "│  One-command setup for Claude Code plugins       │"
echo "│  with Confluence, JIRA, and Splunk integration   │"
echo "╰──────────────────────────────────────────────────╯"
echo -e "${NC}"

# Check Python version
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}  ✗ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 9 ]]; then
    echo -e "${RED}  ✗ Python 3.9+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Python $PYTHON_VERSION${NC}"

# Check for Claude Code CLI (optional warning)
if command -v claude &> /dev/null; then
    echo -e "${GREEN}  ✓ Claude Code CLI${NC}"
    CLAUDE_AVAILABLE=true
else
    echo -e "${YELLOW}  ! Claude Code CLI not found (plugin installation will be skipped)${NC}"
    CLAUDE_AVAILABLE=false
    SKIP_PLUGINS=true
fi

# Detect existing virtualenv configuration
echo ""
echo "Detecting virtualenv configuration..."
VENV_SOURCE=""
VENV_DIR=""

if VENV_RESULT=$(detect_existing_venv); then
    VENV_SOURCE="${VENV_RESULT%%:*}"
    VENV_LOCATION="${VENV_RESULT#*:}"

    if [[ "$VENV_SOURCE" == "active" ]]; then
        VENV_DIR="$VENV_LOCATION"
        echo -e "${GREEN}  ✓ Using active virtualenv: $VENV_DIR${NC}"
    else
        # Extract venv path from the file
        VENV_DIR=$(extract_venv_path_from_file "$VENV_LOCATION")
        if [[ -n "$VENV_DIR" ]]; then
            echo -e "${GREEN}  ✓ Found existing venv config in: $VENV_LOCATION${NC}"
            echo -e "${GREEN}    Venv path: $VENV_DIR${NC}"
        else
            echo -e "${YELLOW}  ! Could not extract venv path from $VENV_LOCATION${NC}"
            VENV_DIR="$HOME/.as-plugins-venv"
        fi
    fi
else
    VENV_DIR="$HOME/.as-plugins-venv"
    echo -e "${YELLOW}  No existing virtualenv found, will create at $VENV_DIR${NC}"
fi

# Create venv if needed (unless using active venv)
if [[ "$VENV_SOURCE" != "active" ]]; then
    if [[ -d "$VENV_DIR" && "$FORCE" != "true" ]]; then
        echo ""
        echo -e "${YELLOW}Virtual environment exists at $VENV_DIR${NC}"
        read -p "Recreate it? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        fi
    fi

    if [[ ! -d "$VENV_DIR" ]]; then
        echo ""
        echo "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}  ✓ Created $VENV_DIR${NC}"

        # Configure shell activation for new venv
        configure_shell_activation "$VENV_DIR"
    fi

    # Activate the venv
    echo ""
    echo "Activating virtualenv..."
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}  ✓ Activated $VENV_DIR${NC}"
fi

# Install base dependencies
echo ""
echo "Installing base dependencies..."

# Upgrade pip and install wheel
pip install --upgrade pip wheel > /dev/null 2>&1
echo -e "${GREEN}  ✓ pip and wheel${NC}"

# Install setup dependencies (rich for UI, requests for API validation)
pip install rich requests > /dev/null 2>&1
echo -e "${GREEN}  ✓ rich and requests${NC}"

# Run the Python setup wizard
echo ""
export AS_PLUGINS_REPO_DIR="$REPO_DIR"
export AS_PLUGINS_VENV_DIR="$VENV_DIR"
export AS_PLUGINS_SKIP_PLUGINS="$SKIP_PLUGINS"
export AS_PLUGINS_NO_KEYCHAIN="$NO_KEYCHAIN"
export AS_PLUGINS_PLATFORMS="$PLATFORMS"
export AS_PLUGINS_VALIDATE_ONLY="$VALIDATE_ONLY"
export AS_PLUGINS_SKIP_CREDENTIALS="$SKIP_CREDENTIALS"

python3 -m scripts.setup.main

# Show activation instructions
echo ""
echo -e "${BLUE}To activate the Python environment:${NC}"
echo "  source $VENV_DIR/bin/activate"
echo ""

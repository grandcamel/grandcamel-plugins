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
VENV_DIR="$REPO_DIR/.venv"

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

# Create or recreate virtual environment
if [[ -d "$VENV_DIR" && "$FORCE" != "true" ]]; then
    echo ""
    echo -e "${YELLOW}Virtual environment already exists at $VENV_DIR${NC}"
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
fi

# Activate and install base dependencies
echo ""
echo "Installing base dependencies..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

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

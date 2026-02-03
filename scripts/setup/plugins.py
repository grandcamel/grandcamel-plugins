#!/usr/bin/env python3
"""
Claude Code plugin management for AS-Plugins Setup Wizard.

Handles marketplace and plugin installation via the Claude CLI.
"""

import platform
import shutil
import subprocess
from typing import Optional


def check_cli_installed(cli_name: str) -> bool:
    """Check if a CLI tool is installed and available in PATH."""
    return shutil.which(cli_name) is not None


def detect_os() -> str:
    """Detect the current operating system and package manager."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        # Try to detect package manager
        if shutil.which("apt"):
            return "linux_apt"
        elif shutil.which("dnf"):
            return "linux_dnf"
        elif shutil.which("pacman"):
            return "linux_pacman"
        return "linux"
    elif system == "windows":
        return "windows"
    return "unknown"


def get_cli_install_instructions(cli_name: str) -> dict:
    """
    Get platform-specific installation instructions for a CLI tool.

    Args:
        cli_name: Name of the CLI tool (e.g., "glab")

    Returns:
        Dictionary of os_type -> installation command
    """
    instructions = {
        "glab": {
            "macos": "brew install glab",
            "linux_apt": "sudo apt install glab",
            "linux_dnf": "sudo dnf install glab",
            "linux_pacman": "sudo pacman -S gitlab-glab",
            "linux": "See https://gitlab.com/gitlab-org/cli#installation",
            "windows": "winget install glab",
            "manual": "https://gitlab.com/gitlab-org/cli#installation",
        },
    }
    return instructions.get(cli_name, {})


def check_claude_cli() -> bool:
    """Check if Claude Code CLI is available."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_claude_command(args: list[str], timeout: int = 60) -> tuple[bool, str]:
    """
    Run a Claude CLI command.

    Args:
        args: Command arguments (without 'claude' prefix)
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            ["claude"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "Claude CLI not found"
    except Exception as e:
        return False, str(e)


def check_marketplace_added() -> bool:
    """Check if as-plugins marketplace is already added."""
    success, output = run_claude_command(["plugin", "marketplace", "list"])
    if not success:
        return False

    # Check if grandcamel/as-plugins appears in output
    return "grandcamel/as-plugins" in output or "as-plugins" in output


def add_marketplace() -> bool:
    """Add the as-plugins marketplace."""
    success, _ = run_claude_command(
        ["plugin", "marketplace", "add", "grandcamel/as-plugins"]
    )
    return success


def remove_marketplace() -> bool:
    """Remove the as-plugins marketplace."""
    success, _ = run_claude_command(
        ["plugin", "marketplace", "remove", "as-plugins"]
    )
    return success


def get_installed_plugins() -> list[str]:
    """Get list of installed plugin names."""
    success, output = run_claude_command(["plugin", "list"])
    if not success:
        return []

    # Parse plugin list output
    # Format: "  ❯ plugin-name@marketplace"
    plugins = []
    for line in output.splitlines():
        line = line.strip()

        # Look for lines starting with ❯ (bullet character)
        if line.startswith("❯"):
            # Extract: "❯ plugin-name@marketplace" -> "plugin-name"
            parts = line[1:].strip().split("@")
            if parts:
                name = parts[0].strip()
                if name:
                    plugins.append(name)

    return plugins


def install_plugin(plugin_name: str) -> bool:
    """
    Install a plugin from the as-plugins marketplace.

    Args:
        plugin_name: Plugin name (e.g., "jira-assistant-skills")

    Returns:
        True if installation succeeded
    """
    # Install with @as-plugins suffix and user scope
    success, output = run_claude_command([
        "plugin", "install",
        f"{plugin_name}@as-plugins",
        "--scope", "user",
    ], timeout=120)  # Plugins may take time to download

    return success


def uninstall_plugin(plugin_name: str) -> bool:
    """
    Uninstall a plugin.

    Args:
        plugin_name: Plugin name

    Returns:
        True if uninstallation succeeded
    """
    success, _ = run_claude_command([
        "plugin", "uninstall", plugin_name,
    ])
    return success


def get_plugin_info(plugin_name: str) -> Optional[dict]:
    """
    Get information about a plugin.

    Args:
        plugin_name: Plugin name

    Returns:
        Dictionary with plugin info or None
    """
    success, output = run_claude_command([
        "plugin", "info", plugin_name,
    ])

    if not success:
        return None

    # Parse output into dict (format varies)
    info = {"name": plugin_name, "raw": output}

    # Try to extract common fields
    for line in output.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            info[key.strip().lower()] = value.strip()

    return info

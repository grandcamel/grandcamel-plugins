#!/usr/bin/env python3
"""
AS-Plugins Setup Wizard - Main Orchestrator

Interactive setup for Assistant Skills Claude Code plugins with
Confluence, JIRA, and Splunk integration.
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

from .credentials import collect_credentials, PLATFORM_CONFIGS
from .validate import validate_credentials
from .env_file import load_env_file, save_env_file, mask_value
from .plugins import (
    check_claude_cli,
    check_marketplace_added,
    add_marketplace,
    install_plugin,
    get_installed_plugins,
)

console = Console()

# Environment variables from bash wrapper
REPO_DIR = Path(os.environ.get("AS_PLUGINS_REPO_DIR", Path(__file__).parent.parent.parent))
VENV_DIR = Path(os.environ.get("AS_PLUGINS_VENV_DIR", REPO_DIR / ".venv"))
SKIP_PLUGINS = os.environ.get("AS_PLUGINS_SKIP_PLUGINS", "false").lower() == "true"
NO_KEYCHAIN = os.environ.get("AS_PLUGINS_NO_KEYCHAIN", "false").lower() == "true"
PLATFORMS_ARG = os.environ.get("AS_PLUGINS_PLATFORMS", "")

# Check if stdin is a TTY (interactive mode)
IS_INTERACTIVE = sys.stdin.isatty()

ENV_FILE = Path.home() / ".env"


def show_welcome():
    """Display welcome banner."""
    console.print()


def detect_existing_config():
    """Detect existing ~/.env configuration."""
    env_vars = load_env_file(ENV_FILE)
    configured = {}

    for platform, config in PLATFORM_CONFIGS.items():
        required_vars = config["required_vars"]
        if all(env_vars.get(var) for var in required_vars):
            configured[platform] = {var: env_vars[var] for var in required_vars}

    return configured, env_vars


def show_existing_config(configured: dict):
    """Display existing configuration."""
    if not configured:
        return

    console.print("[yellow]Detected existing configuration:[/yellow]")
    table = Table(box=box.SIMPLE)
    table.add_column("Platform", style="cyan")
    table.add_column("Status", style="green")

    for platform in configured:
        table.add_row(platform.capitalize(), "Configured")

    console.print(table)
    console.print()


def select_platforms(configured: dict) -> list[str]:
    """Interactive platform selection."""
    # If platforms specified via command line
    if PLATFORMS_ARG:
        platforms = [p.strip().lower() for p in PLATFORMS_ARG.split(",")]
        valid = [p for p in platforms if p in PLATFORM_CONFIGS]
        if valid:
            return valid

    console.print("[bold]Which platforms would you like to configure?[/bold]")
    console.print()
    console.print("  [1] Confluence + JIRA (Atlassian Cloud)")
    console.print("  [2] All platforms (Confluence + JIRA + Splunk)")
    console.print("  [3] Confluence only")
    console.print("  [4] JIRA only")
    console.print("  [5] Splunk only")
    console.print()

    choices = {
        "1": ["confluence", "jira"],
        "2": ["confluence", "jira", "splunk"],
        "3": ["confluence"],
        "4": ["jira"],
        "5": ["splunk"],
    }

    choice = Prompt.ask("Select", choices=list(choices.keys()), default="1")
    return choices[choice]


def install_python_packages(platforms: list[str]):
    """Install Python packages for selected platforms."""
    console.print()
    console.print("[bold]Installing Python Libraries[/bold]")

    packages = {
        "confluence": ("confluence-as", "1.1.0"),
        "jira": ("jira-as", "1.0.0"),
        "splunk": ("splunk-as", "1.1.6"),
    }

    import subprocess

    pip_path = VENV_DIR / "bin" / "pip"

    for platform in platforms:
        if platform in packages:
            pkg_name, version = packages[platform]
            console.print(f"  {pkg_name} {version} ... ", end="")
            try:
                result = subprocess.run(
                    [str(pip_path), "install", f"{pkg_name}>={version}"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                console.print("[green]OK[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]FAILED[/red]")
                console.print(f"[dim]{e.stderr}[/dim]")


def install_claude_plugins(platforms: list[str]):
    """Install Claude Code plugins for selected platforms."""
    if SKIP_PLUGINS:
        console.print()
        console.print("[dim]Skipping Claude Code plugin installation (--skip-plugins)[/dim]")
        return

    if not check_claude_cli():
        console.print()
        console.print("[yellow]Claude Code CLI not available - skipping plugin installation[/yellow]")
        return

    console.print()
    console.print("[bold]Installing Claude Code Plugins[/bold]")

    # Check/add marketplace
    if not check_marketplace_added():
        console.print("  Adding as-plugins marketplace ... ", end="")
        if add_marketplace():
            console.print("[green]OK[/green]")
        else:
            console.print("[red]FAILED[/red]")
            return

    # Map platforms to plugin names
    plugin_names = {
        "confluence": "confluence-assistant-skills",
        "jira": "jira-assistant-skills",
        "splunk": "splunk-assistant-skills",
    }

    installed = get_installed_plugins()

    for platform in platforms:
        plugin_name = plugin_names.get(platform)
        if not plugin_name:
            continue

        # Check if already installed
        if plugin_name in installed:
            console.print(f"  {plugin_name} ... [dim]already installed[/dim]")
            continue

        console.print(f"  {plugin_name} ... ", end="")
        if install_plugin(plugin_name):
            console.print("[green]OK[/green]")
        else:
            console.print("[red]FAILED[/red]")


def show_summary(platforms: list[str], env_vars: dict):
    """Display setup summary."""
    console.print()
    console.print(Panel(
        "[bold green]Setup Complete![/bold green]",
        box=box.DOUBLE,
        expand=False
    ))
    console.print()

    # Configured platforms
    console.print("[bold]Configured platforms:[/bold]")
    for platform in platforms:
        config = PLATFORM_CONFIGS[platform]
        url_var = config.get("url_var", "")
        url = env_vars.get(url_var, "")
        if url:
            # Extract domain from URL
            domain = url.replace("https://", "").replace("http://", "").rstrip("/")
            console.print(f"  [green]OK[/green] {platform.capitalize()} ({domain})")
        else:
            console.print(f"  [green]OK[/green] {platform.capitalize()}")

    # Show installed plugins if not skipped
    if not SKIP_PLUGINS and check_claude_cli():
        installed = get_installed_plugins()
        plugin_names = {
            "confluence": "confluence-assistant-skills",
            "jira": "jira-assistant-skills",
            "splunk": "splunk-assistant-skills",
        }

        relevant = [plugin_names[p] for p in platforms if plugin_names.get(p) in installed]
        if relevant:
            console.print()
            console.print("[bold]Installed Claude Code plugins:[/bold]")
            for plugin in relevant:
                console.print(f"  [green]OK[/green] {plugin}@as-plugins")

    # Sample commands
    console.print()
    console.print("[bold]Try these commands in Claude Code:[/bold]")
    if "confluence" in platforms:
        console.print('  "List all Confluence spaces"')
    if "jira" in platforms:
        console.print('  "Show my open JIRA issues"')
    if "splunk" in platforms:
        console.print('  "Run a Splunk search for errors"')


def main():
    """Main setup wizard entry point."""
    show_welcome()

    # Check for interactive mode
    if not IS_INTERACTIVE:
        console.print("[yellow]Non-interactive mode detected.[/yellow]")
        console.print("For non-interactive setup, set environment variables directly:")
        console.print("  CONFLUENCE_SITE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN")
        console.print("  JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        console.print("  SPLUNK_URL, SPLUNK_USERNAME, SPLUNK_PASSWORD")
        console.print("")
        console.print("Or run setup.sh in a terminal for interactive prompts.")
        sys.exit(1)

    # Detect existing config
    configured, existing_env = detect_existing_config()
    show_existing_config(configured)

    # Select platforms
    platforms = select_platforms(configured)
    console.print()

    # Track credentials to reconfigure
    credentials = {}
    reuse_atlassian = None

    # Collect credentials for each platform
    for platform in platforms:
        config = PLATFORM_CONFIGS[platform]
        console.print(f"[bold cyan]{config['title']}[/bold cyan]")

        # Check if we can reuse Atlassian credentials
        if platform in ["jira"] and "confluence" in platforms and "confluence" in credentials:
            if reuse_atlassian is None:
                reuse_atlassian = Confirm.ask("Use same Atlassian credentials?", default=True)

            if reuse_atlassian:
                # Copy credentials from confluence
                creds = credentials["confluence"].copy()
                console.print("  Testing connection ... ", end="")

                # Validate with JIRA endpoint
                success, message = validate_credentials(platform, creds)
                if success:
                    console.print(f"[green]OK[/green] {message}")
                    credentials[platform] = creds
                    console.print()
                    continue
                else:
                    console.print(f"[yellow]Failed[/yellow] - {message}")
                    console.print("  Collecting JIRA-specific credentials...")
                    reuse_atlassian = False

        # Collect credentials interactively
        creds = collect_credentials(platform, existing_env)

        # Validate credentials
        console.print("  Testing connection ... ", end="")
        success, message = validate_credentials(platform, creds)

        if success:
            console.print(f"[green]OK[/green] {message}")
            credentials[platform] = creds
        else:
            console.print(f"[red]Failed[/red] - {message}")
            if Confirm.ask("  Continue anyway?", default=False):
                credentials[platform] = creds
            else:
                console.print(f"  [dim]Skipping {platform}[/dim]")

        console.print()

    # No platforms configured
    if not credentials:
        console.print("[yellow]No platforms configured. Exiting.[/yellow]")
        sys.exit(1)

    # Prepare env vars to save
    new_env_vars = existing_env.copy()
    for platform, creds in credentials.items():
        new_env_vars.update(creds)

    # Save to ~/.env
    console.print("[bold]Saving Configuration[/bold]")
    backup_path = save_env_file(ENV_FILE, new_env_vars)
    if backup_path:
        console.print(f"  Backed up ~/.env -> {backup_path.name}")
    console.print(f"  Updated ~/.env with credentials")
    console.print(f"  Permissions set to 600")

    # Install Python packages
    install_python_packages(list(credentials.keys()))

    # Install Claude Code plugins
    install_claude_plugins(list(credentials.keys()))

    # Show summary
    show_summary(list(credentials.keys()), new_env_vars)


if __name__ == "__main__":
    main()

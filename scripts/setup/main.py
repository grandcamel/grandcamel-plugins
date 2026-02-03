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
from .env_file import load_env_file, save_env_file, mask_value, discover_env_files
from .plugins import (
    check_claude_cli,
    check_cli_installed,
    check_marketplace_added,
    add_marketplace,
    detect_os,
    get_cli_install_instructions,
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
VALIDATE_ONLY = os.environ.get("AS_PLUGINS_VALIDATE_ONLY", "false").lower() == "true"
SKIP_CREDENTIALS = os.environ.get("AS_PLUGINS_SKIP_CREDENTIALS", "false").lower() == "true"

# Check if stdin is a TTY (interactive mode)
IS_INTERACTIVE = sys.stdin.isatty()

ENV_FILE = Path.home() / ".env"


def show_welcome():
    """Display welcome banner."""
    console.print()


def detect_existing_config():
    """
    Detect existing configuration from multiple sources.

    Checks (in priority order):
        1. Shell environment (os.environ)
        2. ~/.env
        3. as-demo/secrets/.env (sibling project)

    Returns:
        (configured, merged_env, sources) where sources is the ordered
        list of (label, env_dict) for use in collect_credentials().
    """
    # Build ordered sources list
    sources = []

    # 1. Shell environment — filter to platform-relevant vars
    platform_prefixes = ("CONFLUENCE_", "JIRA_", "SPLUNK_", "GITLAB_")
    shell_env = {k: v for k, v in os.environ.items() if k.startswith(platform_prefixes)}
    if shell_env:
        sources.append(("shell", shell_env))

    # 2-3. Env files on disk
    for label, path in discover_env_files():
        env_dict = load_env_file(path)
        if env_dict:
            sources.append((label, env_dict))

    # Build merged view (later sources don't override earlier ones)
    merged_env = {}
    for _label, env_dict in reversed(sources):
        merged_env.update(env_dict)

    # Determine which platforms are fully configured
    configured = {}
    for platform, config in PLATFORM_CONFIGS.items():
        required_vars = config["required_vars"]
        if all(merged_env.get(var) for var in required_vars):
            configured[platform] = {var: merged_env[var] for var in required_vars}

    return configured, merged_env, sources


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


def validate_existing_config(configured: dict) -> dict:
    """
    Validate existing credentials for all configured platforms.

    Args:
        configured: Dictionary of platform -> credentials

    Returns:
        Dictionary of platform -> {"valid": bool, "message": str, "url": str}
    """
    status = {}

    for platform, creds in configured.items():
        success, message = validate_credentials(platform, creds)

        # Extract URL for display
        config = PLATFORM_CONFIGS.get(platform, {})
        url_var = config.get("url_var", "")
        url = creds.get(url_var, "")
        if url:
            url = url.replace("https://", "").replace("http://", "").rstrip("/")

        status[platform] = {
            "valid": success,
            "message": message,
            "url": url,
        }

    return status


def show_validation_results(validation_status: dict, configured: dict) -> bool:
    """
    Display validation results for --validate-only mode.

    Args:
        validation_status: Results from validate_existing_config
        configured: Dictionary of configured platforms

    Returns:
        True if all configured platforms are valid
    """
    console.print("[bold]Validating existing configuration...[/bold]")
    console.print()

    all_platforms = ["confluence", "jira", "splunk", "gitlab"]
    all_valid = True
    any_configured = False

    for platform in all_platforms:
        if platform in validation_status:
            any_configured = True
            status = validation_status[platform]
            url_info = f" ({status['url']})" if status["url"] else ""

            if status["valid"]:
                console.print(f"  [green]✓[/green] {platform.capitalize()}: {status['message']}{url_info}")
            else:
                console.print(f"  [red]✗[/red] {platform.capitalize()}: {status['message']}{url_info}")
                all_valid = False
        else:
            console.print(f"  [dim]○[/dim] {platform.capitalize()}: (not configured)")

    console.print()

    if not any_configured:
        console.print("[yellow]No platforms configured.[/yellow]")
        console.print("Run setup.sh without --validate-only to configure credentials.")
        return False

    if all_valid:
        console.print("[green]All configured platforms are valid.[/green]")
    else:
        console.print("[yellow]Some credentials need to be updated.[/yellow]")
        console.print("Run setup.sh to reconfigure invalid credentials.")

    return all_valid


def select_platforms_with_status(configured: dict, validation_status: dict) -> tuple[list[str], bool]:
    """
    Enhanced platform selection with validation status.

    Shows existing config status and offers options to keep, reconfigure,
    or add new platforms.

    Args:
        configured: Dictionary of configured platforms
        validation_status: Results from validate_existing_config

    Returns:
        Tuple of (list of platforms to configure, skip_credentials flag)
    """
    # If platforms specified via command line, use those
    if PLATFORMS_ARG:
        platforms = [p.strip().lower() for p in PLATFORMS_ARG.split(",")]
        valid = [p for p in platforms if p in PLATFORM_CONFIGS]
        if valid:
            return valid, False

    # Check if we have any valid existing config
    valid_platforms = [p for p, s in validation_status.items() if s["valid"]]
    invalid_platforms = [p for p, s in validation_status.items() if not s["valid"]]
    unconfigured = [p for p in PLATFORM_CONFIGS.keys() if p not in configured]

    # Show current status
    console.print("[bold]Validating existing configuration...[/bold]")

    all_platforms = ["confluence", "jira", "splunk", "gitlab"]
    for platform in all_platforms:
        if platform in validation_status:
            status = validation_status[platform]
            url_info = f" ({status['url']})" if status["url"] else ""
            if status["valid"]:
                console.print(f"  [green]✓[/green] {platform.capitalize()}: Valid{url_info}")
            else:
                console.print(f"  [red]✗[/red] {platform.capitalize()}: {status['message']}{url_info}")
        else:
            console.print(f"  [dim]○[/dim] {platform.capitalize()}: (not configured)")

    console.print()

    # If all existing configs are invalid, go straight to configuration
    if configured and not valid_platforms:
        console.print("[yellow]Credentials need to be updated. Proceeding with configuration...[/yellow]")
        console.print()
        return list(configured.keys()), False

    # Build menu options
    options = []
    option_map = {}

    # Option 1: Keep existing (only if we have valid platforms)
    if valid_platforms:
        options.append("  [1] Keep existing config, install packages/plugins only (Recommended)")
        option_map["1"] = ("keep", valid_platforms)

    # Option 2+: Reconfigure specific invalid platforms
    next_opt = 2
    if invalid_platforms:
        for platform in invalid_platforms:
            options.append(f"  [{next_opt}] Reconfigure {platform.capitalize()}")
            option_map[str(next_opt)] = ("reconfigure", [platform])
            next_opt += 1

    # Option: Add unconfigured platforms
    if unconfigured:
        for platform in unconfigured:
            options.append(f"  [{next_opt}] Add {platform.capitalize()}")
            option_map[str(next_opt)] = ("add", [platform])
            next_opt += 1

    # Option: Reconfigure all
    if configured:
        options.append(f"  [{next_opt}] Reconfigure all platforms")
        option_map[str(next_opt)] = ("reconfigure_all", list(configured.keys()))
        next_opt += 1

    # Option: Configure from scratch
    if not configured:
        options.append("  [1] Configure Confluence + JIRA (Atlassian Cloud)")
        options.append("  [2] Configure all platforms (Confluence + JIRA + Splunk + GitLab)")
        options.append("  [3] Configure Confluence only")
        options.append("  [4] Configure JIRA only")
        options.append("  [5] Configure Splunk only")
        options.append("  [6] Configure GitLab only")
        option_map = {
            "1": ("configure", ["confluence", "jira"]),
            "2": ("configure", ["confluence", "jira", "splunk", "gitlab"]),
            "3": ("configure", ["confluence"]),
            "4": ("configure", ["jira"]),
            "5": ("configure", ["splunk"]),
            "6": ("configure", ["gitlab"]),
        }
        next_opt = 7

    console.print("[bold]What would you like to do?[/bold]")
    for opt in options:
        console.print(opt)
    console.print()

    valid_choices = list(option_map.keys())
    choice = Prompt.ask("Select", choices=valid_choices, default="1")
    action, platforms = option_map[choice]

    if action == "keep":
        # Skip credentials, just install packages/plugins
        return platforms, True
    else:
        return platforms, False


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
    console.print("  [2] All platforms (Confluence + JIRA + Splunk + GitLab)")
    console.print("  [3] Confluence only")
    console.print("  [4] JIRA only")
    console.print("  [5] Splunk only")
    console.print("  [6] GitLab only")
    console.print()

    choices = {
        "1": ["confluence", "jira"],
        "2": ["confluence", "jira", "splunk", "gitlab"],
        "3": ["confluence"],
        "4": ["jira"],
        "5": ["splunk"],
        "6": ["gitlab"],
    }

    choice = Prompt.ask("Select", choices=list(choices.keys()), default="1")
    return choices[choice]


def check_platform_prerequisites(platform: str) -> tuple[bool, str]:
    """
    Check if platform prerequisites are met (e.g., CLI tools installed).

    Args:
        platform: Platform name to check

    Returns:
        Tuple of (success, error_message). If success is True, error_message is empty.
    """
    config = PLATFORM_CONFIGS.get(platform, {})

    # Check CLI-based platforms for required CLI tool
    if config.get("installation_type") == "cli":
        cli_name = config.get("cli_name")
        if cli_name and not check_cli_installed(cli_name):
            os_type = detect_os()
            instructions = get_cli_install_instructions(cli_name)
            install_cmd = instructions.get(os_type) or instructions.get("manual", "")
            return False, f"{cli_name} CLI not found. Install with: {install_cmd}"

    return True, ""


def show_cli_install_instructions(cli_name: str):
    """Display installation instructions for a CLI tool."""
    instructions = get_cli_install_instructions(cli_name)
    os_type = detect_os()

    console.print(f"  [yellow]{cli_name} CLI not found.[/yellow]")
    console.print()
    console.print("  Install with:")

    if os_type == "macos" and "macos" in instructions:
        console.print(f"    macOS:   {instructions['macos']}")
    if os_type.startswith("linux") and "linux_apt" in instructions:
        console.print(f"    Ubuntu:  {instructions['linux_apt']}")
    if os_type == "linux_dnf" and "linux_dnf" in instructions:
        console.print(f"    Fedora:  {instructions['linux_dnf']}")
    if "windows" in instructions:
        console.print(f"    Windows: {instructions['windows']}")
    if "manual" in instructions:
        console.print(f"    Manual:  {instructions['manual']}")

    console.print()


def install_python_packages(platforms: list[str]):
    """Install Python packages for selected platforms."""
    console.print()
    console.print("[bold]Installing Python Libraries[/bold]")

    packages = {
        "confluence": ("confluence-as", "1.1.0"),
        "jira": ("jira-as", "1.0.0"),
        "splunk": ("splunk-as", "1.2.0"),
        # gitlab: no Python package needed (uses glab CLI)
    }

    import subprocess

    pip_path = VENV_DIR / "bin" / "pip"

    for platform in platforms:
        config = PLATFORM_CONFIGS.get(platform, {})

        # Skip CLI-based platforms (they don't need Python packages)
        if config.get("installation_type") == "cli":
            cli_name = config.get("cli_name", "CLI")
            console.print(f"  {platform} [dim](uses {cli_name} CLI)[/dim]")
            continue

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
        "gitlab": "gitlab-assistant-skills",
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
            "gitlab": "gitlab-assistant-skills",
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
    if "gitlab" in platforms:
        console.print('  "List my GitLab projects"')


def main():
    """Main setup wizard entry point."""
    show_welcome()

    # Detect existing config
    configured, existing_env, sources = detect_existing_config()

    # Validate existing credentials upfront
    validation_status = validate_existing_config(configured)

    # Handle --validate-only mode
    if VALIDATE_ONLY:
        all_valid = show_validation_results(validation_status, configured)
        sys.exit(0 if all_valid else 1)

    # Handle --skip-credentials mode
    if SKIP_CREDENTIALS:
        console.print("[dim]Skipping credential configuration (--skip-credentials)[/dim]")
        console.print()

        # Use existing configured platforms
        platforms_to_install = list(configured.keys())
        if not platforms_to_install:
            console.print("[yellow]No existing configuration found.[/yellow]")
            console.print("Run setup.sh without --skip-credentials to configure platforms.")
            sys.exit(1)

        # Install packages and plugins only
        install_python_packages(platforms_to_install)
        install_claude_plugins(platforms_to_install)
        show_summary(platforms_to_install, existing_env)
        return

    # Check for interactive mode
    if not IS_INTERACTIVE:
        console.print("[yellow]Non-interactive mode detected.[/yellow]")
        console.print("For non-interactive setup, set environment variables directly:")
        console.print("  CONFLUENCE_SITE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN")
        console.print("  JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        console.print("  SPLUNK_SITE_URL, SPLUNK_USERNAME, SPLUNK_PASSWORD")
        console.print("  GITLAB_TOKEN (optionally GITLAB_HOST for self-hosted)")
        console.print("")
        console.print("Or run setup.sh in a terminal for interactive prompts.")
        sys.exit(1)

    # Select platforms with enhanced menu if we have existing config
    if configured:
        platforms, skip_creds = select_platforms_with_status(configured, validation_status)
        console.print()

        if skip_creds:
            # User chose to keep existing config
            install_python_packages(platforms)
            install_claude_plugins(platforms)
            show_summary(platforms, existing_env)
            return
    else:
        # Fresh install - use standard menu
        platforms = select_platforms(configured)
        console.print()

    # Track credentials to reconfigure
    credentials = {}
    reuse_atlassian = None

    # Collect credentials for each platform
    for platform in platforms:
        config = PLATFORM_CONFIGS[platform]
        console.print(f"[bold cyan]{config['title']}[/bold cyan]")

        # Check CLI prerequisites for CLI-based platforms
        prereq_ok, prereq_error = check_platform_prerequisites(platform)
        if not prereq_ok:
            show_cli_install_instructions(config.get("cli_name", ""))
            if Confirm.ask(f"  Continue without {platform}?", default=True):
                console.print(f"  [dim]Skipping {platform}[/dim]")
                console.print()
                continue

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

        # Collect credentials interactively (skips vars already set in sources)
        creds = collect_credentials(platform, existing_env, sources=sources)

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
    # Start from ~/.env values (preserves $(security ...) keychain patterns)
    home_env = load_env_file(ENV_FILE)
    new_env_vars = home_env.copy()
    for platform, creds in credentials.items():
        for key, value in creds.items():
            # Don't overwrite existing ~/.env entries with resolved plaintext
            # (e.g. keep $(security find-generic-password ...) patterns)
            if key not in home_env or not home_env[key]:
                new_env_vars[key] = value

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

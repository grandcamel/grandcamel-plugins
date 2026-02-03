#!/usr/bin/env python3
"""
Credential collection for AS-Plugins Setup Wizard.

Provides interactive prompts for collecting platform credentials
with validation and helpful defaults.
"""

import re
from getpass import getpass

from rich.console import Console
from rich.prompt import Prompt

from .env_file import mask_value, resolve_env_var

console = Console()

# Platform configuration
PLATFORM_CONFIGS = {
    "confluence": {
        "title": "Confluence Configuration",
        "required_vars": ["CONFLUENCE_SITE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"],
        "url_var": "CONFLUENCE_SITE_URL",
        "prompts": {
            "CONFLUENCE_SITE_URL": {
                "label": "Site URL",
                "placeholder": "https://your-site.atlassian.net",
                "validator": "atlassian_url",
            },
            "CONFLUENCE_EMAIL": {
                "label": "Email",
                "placeholder": "user@example.com",
                "validator": "email",
            },
            "CONFLUENCE_API_TOKEN": {
                "label": "API Token",
                "hidden": True,
                "help": "Create at: https://id.atlassian.com/manage-profile/security/api-tokens",
            },
        },
    },
    "jira": {
        "title": "JIRA Configuration",
        "required_vars": ["JIRA_SITE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"],
        "url_var": "JIRA_SITE_URL",
        "prompts": {
            "JIRA_SITE_URL": {
                "label": "Site URL",
                "placeholder": "https://your-site.atlassian.net",
                "validator": "atlassian_url",
            },
            "JIRA_EMAIL": {
                "label": "Email",
                "placeholder": "user@example.com",
                "validator": "email",
            },
            "JIRA_API_TOKEN": {
                "label": "API Token",
                "hidden": True,
                "help": "Create at: https://id.atlassian.com/manage-profile/security/api-tokens",
            },
        },
    },
    "splunk": {
        "title": "Splunk Configuration",
        "required_vars": ["SPLUNK_SITE_URL", "SPLUNK_USERNAME", "SPLUNK_PASSWORD"],
        "url_var": "SPLUNK_SITE_URL",
        "prompts": {
            "SPLUNK_SITE_URL": {
                "label": "Splunk URL",
                "placeholder": "https://splunk.example.com:8089",
                "validator": "url",
            },
            "SPLUNK_USERNAME": {
                "label": "Username",
                "placeholder": "admin",
            },
            "SPLUNK_PASSWORD": {
                "label": "Password",
                "hidden": True,
            },
        },
    },
    "gitlab": {
        "title": "GitLab Configuration",
        "installation_type": "cli",  # CLI-based platform (uses glab)
        "cli_name": "glab",
        "required_vars": ["GITLAB_TOKEN"],
        "optional_vars": ["GITLAB_HOST"],  # Optional for gitlab.com users
        "url_var": "GITLAB_HOST",
        "prompts": {
            "GITLAB_HOST": {
                "label": "GitLab Host",
                "placeholder": "https://gitlab.com",
                "default": "https://gitlab.com",
                "validator": "url",
                "help": "Press Enter for gitlab.com, or enter your self-hosted URL",
                "optional": True,
            },
            "GITLAB_TOKEN": {
                "label": "Personal Access Token",
                "hidden": True,
                "help": "Create at: https://gitlab.com/-/user_settings/personal_access_tokens (scopes: api)",
            },
        },
    },
}


def validate_atlassian_url(url: str) -> tuple[bool, str]:
    """Validate Atlassian Cloud URL."""
    if not url:
        return False, "URL is required"

    # Normalize
    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"

    # Check for atlassian.net domain
    if ".atlassian.net" not in url:
        return False, "Must be an Atlassian Cloud URL (*.atlassian.net)"

    # Basic URL format
    pattern = r"^https://[a-zA-Z0-9-]+\.atlassian\.net$"
    if not re.match(pattern, url):
        return False, "Invalid Atlassian URL format"

    return True, url


def validate_url(url: str) -> tuple[bool, str]:
    """Validate generic URL."""
    if not url:
        return False, "URL is required"

    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"

    pattern = r"^https?://[a-zA-Z0-9.-]+(?::\d+)?(?:/.*)?$"
    if not re.match(pattern, url):
        return False, "Invalid URL format"

    return True, url


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if not email:
        return False, "Email is required"

    email = email.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, email


VALIDATORS = {
    "atlassian_url": validate_atlassian_url,
    "url": validate_url,
    "email": validate_email,
}


def collect_credentials(platform: str, existing_env: dict, sources: list = None) -> dict:
    """
    Collect credentials for a platform interactively.

    If sources is provided, variables already set in any source are
    skipped (displayed with source attribution) instead of prompted.

    Args:
        platform: Platform name (confluence, jira, splunk, gitlab)
        existing_env: Existing environment variables for defaults
        sources: Optional ordered list of (label, env_dict) for skip-if-set logic

    Returns:
        Dictionary of collected credential variables
    """
    config = PLATFORM_CONFIGS[platform]
    credentials = {}

    for var_name, prompt_config in config["prompts"].items():
        label = prompt_config["label"]

        # Skip prompting if variable is already set in any source
        if sources:
            value, source_label = resolve_env_var(var_name, sources)
            if value:
                hidden = prompt_config.get("hidden", False)
                if value.startswith("$(") and value.endswith(")"):
                    console.print(f"  {label}: [green]****[/green] [dim](keychain via {source_label})[/dim]")
                elif hidden:
                    console.print(f"  {label}: [green]{mask_value(value)}[/green] [dim](from {source_label})[/dim]")
                else:
                    console.print(f"  {label}: [green]{value}[/green] [dim](from {source_label})[/dim]")
                credentials[var_name] = value
                continue
        placeholder = prompt_config.get("placeholder", "")
        validator_name = prompt_config.get("validator")
        hidden = prompt_config.get("hidden", False)
        help_text = prompt_config.get("help")
        is_optional = prompt_config.get("optional", False)
        config_default = prompt_config.get("default", "")

        # Get default from existing env, falling back to config default
        default = existing_env.get(var_name, "") or config_default

        # Show help text if available
        if help_text:
            console.print(f"  [dim]{help_text}[/dim]")

        # Build prompt text
        if default and not hidden:
            prompt_text = f"  {label} [{default}]"
        elif placeholder:
            prompt_text = f"  {label} [{placeholder}]"
        else:
            prompt_text = f"  {label}"

        # Collect input
        while True:
            if hidden:
                # Use getpass for hidden input
                console.print(f"  {label} (hidden): ", end="")
                value = getpass("")
                if not value and default:
                    value = default
            else:
                value = Prompt.ask(prompt_text, default=default or "")

            # Handle optional fields with defaults
            if not value:
                if is_optional and config_default:
                    value = config_default
                elif not is_optional:
                    console.print("    [red]Value required[/red]")
                    continue

            # Validate if validator specified and we have a value
            if value and validator_name:
                validator = VALIDATORS.get(validator_name)
                if validator:
                    valid, result = validator(value)
                    if not valid:
                        console.print(f"    [red]{result}[/red]")
                        continue
                    value = result  # Use normalized value

            break

        if value:  # Only add non-empty values
            credentials[var_name] = value

    return credentials

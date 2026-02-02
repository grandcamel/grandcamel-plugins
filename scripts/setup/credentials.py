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
        "required_vars": ["SPLUNK_URL", "SPLUNK_USERNAME", "SPLUNK_PASSWORD"],
        "url_var": "SPLUNK_URL",
        "prompts": {
            "SPLUNK_URL": {
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


def collect_credentials(platform: str, existing_env: dict) -> dict:
    """
    Collect credentials for a platform interactively.

    Args:
        platform: Platform name (confluence, jira, splunk)
        existing_env: Existing environment variables for defaults

    Returns:
        Dictionary of collected credential variables
    """
    config = PLATFORM_CONFIGS[platform]
    credentials = {}

    for var_name, prompt_config in config["prompts"].items():
        label = prompt_config["label"]
        placeholder = prompt_config.get("placeholder", "")
        validator_name = prompt_config.get("validator")
        hidden = prompt_config.get("hidden", False)
        help_text = prompt_config.get("help")

        # Get default from existing env
        default = existing_env.get(var_name, "")

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

            if not value:
                console.print("    [red]Value required[/red]")
                continue

            # Validate if validator specified
            if validator_name:
                validator = VALIDATORS.get(validator_name)
                if validator:
                    valid, result = validator(value)
                    if not valid:
                        console.print(f"    [red]{result}[/red]")
                        continue
                    value = result  # Use normalized value

            break

        credentials[var_name] = value

    return credentials

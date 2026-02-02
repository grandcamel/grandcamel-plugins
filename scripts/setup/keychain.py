#!/usr/bin/env python3
"""
OS Keychain integration for AS-Plugins Setup Wizard.

Provides secure credential storage using:
- macOS: security command (Keychain Access)
- Linux: secret-tool (GNOME Keyring / libsecret)

This is optional functionality - credentials can also be stored
in ~/.env file directly.
"""

import subprocess
import sys
from typing import Optional


def get_platform() -> str:
    """Get the current platform."""
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    else:
        return "unsupported"


def is_keychain_available() -> bool:
    """Check if OS keychain is available."""
    platform = get_platform()

    if platform == "macos":
        # Check for security command
        try:
            subprocess.run(
                ["security", "help"],
                capture_output=True,
                check=False,
            )
            return True
        except FileNotFoundError:
            return False

    if platform == "linux":
        # Check for secret-tool
        try:
            subprocess.run(
                ["secret-tool", "--version"],
                capture_output=True,
                check=False,
            )
            return True
        except FileNotFoundError:
            return False

    return False


def store_secret(service: str, account: str, secret: str) -> bool:
    """
    Store a secret in the OS keychain.

    Args:
        service: Service name (e.g., "as-plugins-confluence")
        account: Account identifier (e.g., "api_token")
        secret: The secret value to store

    Returns:
        True if successful, False otherwise
    """
    platform = get_platform()

    if platform == "macos":
        try:
            # Delete existing entry first (ignore errors)
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s", service,
                    "-a", account,
                ],
                capture_output=True,
                check=False,
            )

            # Add new entry
            subprocess.run(
                [
                    "security",
                    "add-generic-password",
                    "-s", service,
                    "-a", account,
                    "-w", secret,
                    "-U",  # Update if exists
                ],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    if platform == "linux":
        try:
            # Store using secret-tool
            process = subprocess.Popen(
                [
                    "secret-tool",
                    "store",
                    "--label", f"{service} - {account}",
                    "service", service,
                    "account", account,
                ],
                stdin=subprocess.PIPE,
                capture_output=True,
            )
            process.communicate(input=secret.encode())
            return process.returncode == 0
        except Exception:
            return False

    return False


def get_secret(service: str, account: str) -> Optional[str]:
    """
    Retrieve a secret from the OS keychain.

    Args:
        service: Service name (e.g., "as-plugins-confluence")
        account: Account identifier (e.g., "api_token")

    Returns:
        The secret value if found, None otherwise
    """
    platform = get_platform()

    if platform == "macos":
        try:
            result = subprocess.run(
                [
                    "security",
                    "find-generic-password",
                    "-s", service,
                    "-a", account,
                    "-w",  # Output password only
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    if platform == "linux":
        try:
            result = subprocess.run(
                [
                    "secret-tool",
                    "lookup",
                    "service", service,
                    "account", account,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    return None


def delete_secret(service: str, account: str) -> bool:
    """
    Delete a secret from the OS keychain.

    Args:
        service: Service name (e.g., "as-plugins-confluence")
        account: Account identifier (e.g., "api_token")

    Returns:
        True if successful or not found, False on error
    """
    platform = get_platform()

    if platform == "macos":
        try:
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s", service,
                    "-a", account,
                ],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            # Not found is OK
            return True

    if platform == "linux":
        try:
            subprocess.run(
                [
                    "secret-tool",
                    "clear",
                    "service", service,
                    "account", account,
                ],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return True

    return False

#!/usr/bin/env python3
"""
API validation for AS-Plugins Setup Wizard.

Tests connectivity to Confluence, JIRA, and Splunk APIs
to verify credentials are correct before saving.
"""

import base64
from urllib.parse import urljoin

import requests


def validate_confluence(url: str, email: str, token: str) -> tuple[bool, str]:
    """
    Validate Confluence credentials by testing API connectivity.

    Args:
        url: Confluence site URL (https://site.atlassian.net)
        email: Atlassian account email
        token: API token

    Returns:
        Tuple of (success, message)
    """
    # Create auth header
    auth_string = f"{email}:{token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Accept": "application/json",
    }

    # Try multiple endpoints (v1 API is more reliable)
    endpoints = [
        ("wiki/rest/api/user/current", "user"),
        ("wiki/api/v2/spaces?limit=1", "spaces"),
        ("wiki/rest/api/space?limit=1", "spaces"),
    ]

    last_status = None
    for path, endpoint_type in endpoints:
        try:
            api_url = urljoin(url + "/", path)
            response = requests.get(api_url, headers=headers, timeout=10)
            last_status = response.status_code

            if response.status_code == 200:
                data = response.json()
                if endpoint_type == "user":
                    name = data.get("displayName", data.get("username", ""))
                    return True, f"Connected as {name}" if name else "Connected"
                return True, "Connected"

            # 401 is definitely invalid credentials
            if response.status_code == 401:
                return False, "Invalid credentials (401 Unauthorized)"

            # 403 might mean credentials work but endpoint is restricted
            # Continue to try other endpoints
            if response.status_code == 403:
                continue

            # 404 means endpoint doesn't exist, try next
            if response.status_code == 404:
                continue

        except requests.exceptions.Timeout:
            return False, "Connection timed out"
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to server"
        except Exception:
            continue

    # If we got here, no endpoint worked
    if last_status == 403:
        return False, "Access denied - check API token permissions"
    if last_status == 404:
        return False, "Confluence not found at this URL"
    if last_status:
        return False, f"API returned status {last_status}"
    return False, "Could not validate credentials"


def validate_jira(url: str, email: str, token: str) -> tuple[bool, str]:
    """
    Validate JIRA credentials by testing API connectivity.

    Args:
        url: JIRA site URL (https://site.atlassian.net)
        email: Atlassian account email
        token: API token

    Returns:
        Tuple of (success, message)
    """
    # Create auth header
    auth_string = f"{email}:{token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Accept": "application/json",
    }

    # Try multiple endpoints
    endpoints = [
        ("rest/api/3/myself", "user"),
        ("rest/api/2/myself", "user"),
    ]

    last_status = None
    for path, endpoint_type in endpoints:
        try:
            api_url = urljoin(url + "/", path)
            response = requests.get(api_url, headers=headers, timeout=10)
            last_status = response.status_code

            if response.status_code == 200:
                data = response.json()
                display_name = data.get("displayName", "Unknown")
                return True, f"Connected as {display_name}"

            if response.status_code == 401:
                return False, "Invalid credentials (401 Unauthorized)"

            if response.status_code == 403:
                return False, "Access denied - check API token permissions"

            # 404 means endpoint doesn't exist, try next
            if response.status_code == 404:
                continue

        except requests.exceptions.Timeout:
            return False, "Connection timed out"
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to server"
        except Exception:
            continue

    if last_status == 404:
        return False, "JIRA not found at this URL"
    if last_status:
        return False, f"API returned status {last_status}"
    return False, "Could not validate credentials"


def validate_splunk(url: str, username: str, password: str) -> tuple[bool, str]:
    """
    Validate Splunk credentials by testing API connectivity.

    Args:
        url: Splunk management URL (https://splunk:8089)
        username: Splunk username
        password: Splunk password

    Returns:
        Tuple of (success, message)
    """
    try:
        # Use /services/auth/login to test authentication
        api_url = urljoin(url + "/", "services/auth/login")

        response = requests.post(
            api_url,
            data={
                "username": username,
                "password": password,
                "output_mode": "json",
            },
            verify=False,  # Splunk often uses self-signed certs
            timeout=10,
        )

        if response.status_code == 200:
            return True, "Connected"

        if response.status_code == 401:
            return False, "Invalid credentials (401 Unauthorized)"

        return False, f"API returned status {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Connection timed out"
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to server"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_credentials(platform: str, credentials: dict) -> tuple[bool, str]:
    """
    Validate credentials for a platform.

    Args:
        platform: Platform name (confluence, jira, splunk)
        credentials: Dictionary of credential variables

    Returns:
        Tuple of (success, message)
    """
    if platform == "confluence":
        return validate_confluence(
            url=credentials.get("CONFLUENCE_SITE_URL", ""),
            email=credentials.get("CONFLUENCE_EMAIL", ""),
            token=credentials.get("CONFLUENCE_API_TOKEN", ""),
        )

    if platform == "jira":
        return validate_jira(
            url=credentials.get("JIRA_SITE_URL", ""),
            email=credentials.get("JIRA_EMAIL", ""),
            token=credentials.get("JIRA_API_TOKEN", ""),
        )

    if platform == "splunk":
        return validate_splunk(
            url=credentials.get("SPLUNK_URL", ""),
            username=credentials.get("SPLUNK_USERNAME", ""),
            password=credentials.get("SPLUNK_PASSWORD", ""),
        )

    return False, f"Unknown platform: {platform}"

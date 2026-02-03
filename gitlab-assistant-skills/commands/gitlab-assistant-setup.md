---
name: gitlab-assistant-setup
description: Set up GitLab Assistant Skills with credentials and glab CLI configuration
---

# GitLab Assistant Setup

You are helping the user set up GitLab Assistant Skills. Guide them through the process conversationally.

## Step 1: Check Prerequisites

First, verify the glab CLI is installed:

```bash
glab --version
```

If glab is not installed, provide installation instructions:

**macOS:**
```bash
brew install glab
```

**Ubuntu/Debian:**
```bash
sudo apt install glab
```

**Windows:**
```bash
winget install glab
```

**Other:** Visit https://gitlab.com/gitlab-org/cli#installation

## Step 2: Check Authentication Status

Check if glab is already authenticated:

```bash
glab auth status
```

If already authenticated, skip to Step 5 (Validate Connection).

## Step 3: Get Personal Access Token

Tell the user they need a Personal Access Token from GitLab:

"To connect to GitLab, you'll need a Personal Access Token. I can open the page where you can create one.

Would you like me to open the token creation page?"

If they agree, use:
```bash
python3 -c "import webbrowser; webbrowser.open('https://gitlab.com/-/user_settings/personal_access_tokens')"
```

Guide them:
1. Click "Add new token"
2. Name it "GitLab Assistant Skills" or similar
3. Select scopes: `api` (required), optionally `read_user`
4. Set an expiration date (or leave blank for no expiry)
5. Click "Create personal access token"
6. Copy the token immediately (it won't be shown again)

For self-hosted GitLab, the URL is: `https://your-gitlab-host/-/user_settings/personal_access_tokens`

## Step 4: Authenticate glab CLI

Option A - Interactive login (recommended):
```bash
glab auth login
```
This will prompt for:
- GitLab instance (gitlab.com or self-hosted URL)
- Authentication method (token or web browser)

Option B - Environment variables:
```bash
export GITLAB_TOKEN="your-token-here"
export GITLAB_HOST="https://gitlab.com"  # Optional, defaults to gitlab.com
```

For bash/zsh, add to `~/.bashrc` or `~/.zshrc`:
```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
# For self-hosted:
# export GITLAB_HOST="https://gitlab.example.com"
```

After setting, reload the shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

## Step 5: Validate Connection

Test the connection:

```bash
glab auth status
```

Or verify by listing your projects:
```bash
glab repo list --mine
```

## Step 6: Confirm Success

If validation succeeds, tell the user:

"Your GitLab Assistant Skills are now set up! Here's what you can do:

**Test with your projects:**
```bash
glab repo list --mine
glab issue list
glab mr list
```

**Or just ask me naturally:**
- 'List my GitLab projects'
- 'Show open merge requests'
- 'Create an issue for the login bug'
- 'What's the status of my CI pipeline?'
- 'Merge MR !42'

I'm ready to help you with GitLab!"

## Troubleshooting

If authentication fails:
- **401 Unauthorized**: Token is incorrect or expired. Create a new one.
- **403 Forbidden**: Token lacks required scopes (needs 'api' scope).
- **Connection error**: Check the GitLab URL is correct and reachable.
- **SSL errors**: For self-signed certs, set `GITLAB_SKIP_TLS_VERIFY=true`

If glab is not found:
- Ensure glab is in your PATH
- Try running with full path: `/opt/homebrew/bin/glab` (macOS) or `/usr/bin/glab` (Linux)
- Reinstall using the package manager

For self-hosted GitLab:
- Ensure you're using the correct host URL
- Some features may require GitLab Premium or Ultimate
- Check with your GitLab admin for any firewall or network restrictions

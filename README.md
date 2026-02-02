# AS-Plugins (Assistant Skills)

A Claude Code marketplace providing Assistant Skills plugins for enterprise integrations and developer productivity.

## Quick Setup

The setup wizard configures everything in one command:

```bash
# Clone the repository
git clone https://github.com/grandcamel/as-plugins.git
cd as-plugins

# Run the setup wizard
./scripts/setup.sh
```

The wizard will:
1. Create a Python virtual environment
2. Walk you through configuring credentials for Confluence, JIRA, and/or Splunk
3. Validate API connectivity
4. Install Python libraries (`confluence-as`, `jira-as`, `splunk-as`)
5. Add the as-plugins marketplace to Claude Code
6. Install the selected Claude Code plugins

### Setup Options

```bash
# Force recreate virtual environment
./scripts/setup.sh --force

# Skip Claude Code plugin installation
./scripts/setup.sh --skip-plugins

# Pre-select platforms (skip interactive menu)
./scripts/setup.sh --platforms confluence,jira
```

### What Gets Configured

| Item | Location | Description |
|------|----------|-------------|
| Python venv | `.venv/` | Virtual environment with AS libraries |
| Credentials | `~/.env` | API tokens and URLs (permissions 600) |
| Marketplace | Claude Code | `grandcamel/as-plugins` |
| Plugins | `~/.claude/plugins/` | Selected assistant skills plugins |

### After Setup

Activate the Python environment when needed:

```bash
source .venv/bin/activate
```

Try these commands in Claude Code:
- "List all Confluence spaces"
- "Show my open JIRA issues"
- "Run a Splunk search for errors in the last hour"

## Manual Installation

### Via Claude Code Marketplace

```bash
# Add the marketplace
/plugin marketplace add grandcamel/as-plugins

# Install a specific plugin
/plugin install jira-assistant-skills@as-plugins
```

### Direct from GitHub

Each plugin can be installed directly:

```bash
claude --plugin github:grandcamel/JIRA-Assistant-Skills
```

### Python Libraries Only

```bash
pip install confluence-as jira-as splunk-as
```

## Plugins

### Enterprise Integrations

| Plugin | Repository | Description |
|--------|------------|-------------|
| **jira-assistant-skills** | [grandcamel/JIRA-Assistant-Skills](https://github.com/grandcamel/JIRA-Assistant-Skills) | 18 specialized skills for JIRA automation |
| **confluence-assistant-skills** | [grandcamel/Confluence-Assistant-Skills](https://github.com/grandcamel/Confluence-Assistant-Skills) | 14 skills for Confluence Cloud automation |
| **splunk-assistant-skills** | [grandcamel/Splunk-Assistant-Skills](https://github.com/grandcamel/Splunk-Assistant-Skills) | 17 skills for Splunk search and administration |
| **gitlab-assistant-skills** | [grandcamel/gitlab-assistant-skills](https://github.com/grandcamel/gitlab-assistant-skills) | Skills for GitLab automation and repository management |

### Developer Productivity

| Plugin | Repository | Description |
|--------|------------|-------------|
| **assistant-skills** | [grandcamel/Assistant-Skills](https://github.com/grandcamel/Assistant-Skills) | Complete toolkit for building Claude Code skills |

## Credentials

The setup wizard stores credentials in `~/.env` with 600 permissions:

```bash
# Confluence
CONFLUENCE_SITE_URL=https://your-site.atlassian.net
CONFLUENCE_EMAIL=user@example.com
CONFLUENCE_API_TOKEN=your-token

# JIRA
JIRA_SITE_URL=https://your-site.atlassian.net
JIRA_EMAIL=user@example.com
JIRA_API_TOKEN=your-token

# Splunk
SPLUNK_URL=https://splunk.example.com:8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-password
```

### Creating API Tokens

- **Atlassian (Confluence/JIRA)**: [Create API Token](https://id.atlassian.com/manage-profile/security/api-tokens)
- **Splunk**: Use your Splunk admin credentials or create a service account

## Troubleshooting

### Setup wizard fails to validate credentials

1. Verify the URL format (Atlassian must be `https://site.atlassian.net`)
2. Check that the API token is valid and not expired
3. Ensure the account has appropriate permissions

### Claude Code plugin not working

1. Check that credentials are in `~/.env`
2. Verify the plugin is installed: `/plugin list`
3. Try reinstalling: `/plugin install confluence-assistant-skills@as-plugins`

### Python import errors

```bash
# Ensure venv is activated
source .venv/bin/activate

# Verify packages are installed
pip list | grep -E "(confluence|jira|splunk)-as"
```

## Contributing

Each plugin is maintained in its own repository. To contribute:

1. Fork the specific plugin repository
2. Make your changes
3. Submit a PR to the plugin repository

## License

MIT - Each plugin may have its own license; check the individual repositories.

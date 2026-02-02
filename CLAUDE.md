# AS-Plugins (Assistant Skills) Marketplace

Claude Code marketplace for Assistant Skills plugins using GitHub sources.

## Project Structure

```
as-plugins/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── scripts/
│   ├── setup.sh              # Setup wizard entry point
│   └── setup/                # Python setup modules
│       ├── __init__.py
│       ├── main.py           # Main orchestrator
│       ├── credentials.py    # Interactive prompts
│       ├── validate.py       # API connectivity tests
│       ├── env_file.py       # ~/.env management
│       ├── keychain.py       # OS keychain (optional)
│       └── plugins.py        # Claude plugin installation
├── requirements.txt          # Python dependencies
├── VERSION
├── README.md
└── CLAUDE.md
```

## Setup Wizard

The setup wizard (`scripts/setup.sh`) provides one-command setup:

```bash
./scripts/setup.sh
```

### What It Does

1. Creates Python virtual environment in `.venv/`
2. Installs base dependencies (pip, wheel, rich)
3. Runs interactive Python setup wizard:
   - Platform selection (Confluence, JIRA, Splunk)
   - Credential collection with validation
   - API connectivity tests
   - Saves credentials to `~/.env` (600 permissions)
4. Installs Python libraries (`confluence-as`, `jira-as`, `splunk-as`)
5. Adds as-plugins marketplace to Claude Code
6. Installs selected Claude Code plugins

### Options

- `--force`: Recreate virtual environment
- `--skip-plugins`: Skip Claude Code plugin installation
- `--no-keychain`: Don't use OS keychain
- `--platforms`: Pre-select platforms (e.g., `confluence,jira`)

## Key Concept: GitHub Sources

Plugins are referenced via GitHub sources in marketplace.json (no local submodules):

```json
{
  "name": "jira-assistant-skills",
  "source": {
    "source": "url",
    "url": "https://github.com/grandcamel/JIRA-Assistant-Skills.git"
  }
}
```

Users install plugins directly from GitHub without needing to clone this repo.

## Plugin Repositories

| Plugin | Repository |
|--------|------------|
| jira-assistant-skills | grandcamel/JIRA-Assistant-Skills |
| confluence-assistant-skills | grandcamel/Confluence-Assistant-Skills |
| splunk-assistant-skills | grandcamel/Splunk-Assistant-Skills |
| gitlab-assistant-skills | grandcamel/gitlab-assistant-skills |
| assistant-skills | grandcamel/Assistant-Skills |

## Development Guidelines

### Adding a Plugin

Add entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "new-plugin",
  "source": {
    "source": "url",
    "url": "https://github.com/grandcamel/New-Plugin.git"
  },
  "description": "Plugin description",
  "version": "1.0.0",
  "category": "productivity",
  "keywords": ["keyword1", "keyword2"]
}
```

### Updating Versions

When a plugin has a new release, update its version in marketplace.json.

### Commit Messages

Use conventional commits:
- `chore(<plugin>): bump version to X.Y.Z`
- `feat: add <plugin> plugin`
- `feat(setup): improve credential validation`
- `docs:` - Documentation changes

## Testing

```bash
# Test marketplace locally
claude --plugin-dir ./

# Add marketplace
/plugin marketplace add grandcamel/as-plugins

# Test setup wizard
./scripts/setup.sh --force
```

## Credentials Location

The setup wizard saves credentials to `~/.env` with 600 permissions:

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

## Python Libraries

The setup wizard installs these libraries into `.venv/`:

| Package | PyPI | Purpose |
|---------|------|---------|
| confluence-as | [Link](https://pypi.org/project/confluence-as/) | Confluence API client |
| jira-as | [Link](https://pypi.org/project/jira-as/) | JIRA API client |
| splunk-as | [Link](https://pypi.org/project/splunk-as/) | Splunk API client |

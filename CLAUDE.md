# AS-Plugins (Assistant Skills) Marketplace

Claude Code marketplace for Assistant Skills plugins using GitHub sources.

## Project Structure

```
as-plugins/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/                  # Git submodules (local development only)
│   └── <plugin-name>/       → GitHub repository
├── .gitmodules              # Submodule URLs
├── VERSION
└── README.md
```

## Key Concept: GitHub Sources

Plugins are referenced via GitHub sources in marketplace.json:

```json
{
  "name": "jira-assistant-skills",
  "source": {
    "source": "github",
    "repo": "grandcamel/JIRA-Assistant-Skills"
  }
}
```

This allows users to install plugins without cloning submodules.

## Plugin Repositories

| Plugin | Repository |
|--------|------------|
| jira-assistant-skills | grandcamel/JIRA-Assistant-Skills |
| confluence-assistant-skills | grandcamel/Confluence-Assistant-Skills |
| splunk-assistant-skills | grandcamel/Splunk-Assistant-Skills |
| assistant-skills | grandcamel/Assistant-Skills |

## Development Guidelines

### Updating marketplace.json

When a plugin has a new release, update its version in marketplace.json.

### Commit Messages

Use conventional commits:
- `chore(<plugin>): bump version to X.Y.Z`
- `feat: add <plugin> plugin`
- `docs:` - Documentation changes

## Testing

```bash
# Test marketplace
claude --plugin-dir ./

# Add marketplace
/plugin marketplace add grandcamel/as-plugins
```

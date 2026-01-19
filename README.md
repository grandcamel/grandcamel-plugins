# AS-Plugins (Assistant Skills)

A Claude Code marketplace providing Assistant Skills plugins for enterprise integrations and developer productivity.

## Installation

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

## Plugins

### Enterprise Integrations

| Plugin | Repository | Description |
|--------|------------|-------------|
| **jira-assistant-skills** | [grandcamel/JIRA-Assistant-Skills](https://github.com/grandcamel/JIRA-Assistant-Skills) | 18 specialized skills for JIRA automation |
| **confluence-assistant-skills** | [grandcamel/Confluence-Assistant-Skills](https://github.com/grandcamel/Confluence-Assistant-Skills) | 14 skills for Confluence Cloud automation |
| **splunk-assistant-skills** | [grandcamel/Splunk-Assistant-Skills](https://github.com/grandcamel/Splunk-Assistant-Skills) | 17 skills for Splunk search and administration |

### Developer Productivity

| Plugin | Repository | Description |
|--------|------------|-------------|
| **assistant-skills** | [grandcamel/Assistant-Skills](https://github.com/grandcamel/Assistant-Skills) | Complete toolkit for building Claude Code skills |

## Python Dependencies

Some plugins require Python libraries:

- **jira-assistant-skills**: `pip install jira-assistant-skills-lib`
- **confluence-assistant-skills**: `pip install confluence-assistant-skills-lib`
- **splunk-assistant-skills**: `pip install splunk-assistant-skills-lib`

## Contributing

Each plugin is maintained in its own repository. To contribute:

1. Fork the specific plugin repository
2. Make your changes
3. Submit a PR to the plugin repository

## License

MIT - Each plugin may have its own license; check the individual repositories.

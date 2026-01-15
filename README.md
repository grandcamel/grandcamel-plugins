# Grandcamel Plugins

A Claude Code marketplace providing plugins for P2P development, enterprise integrations, and developer productivity.

Each plugin is maintained as an independent GitHub repository and included here as a git submodule.

## Installation

### Full Marketplace (all plugins)

```bash
# Clone with all plugins
git clone --recurse-submodules https://github.com/grandcamel/grandcamel-plugins.git

# Use with Claude Code
claude --plugin-dir ./grandcamel-plugins
```

### Individual Plugins

Each plugin can be installed directly from its own repository:

```bash
# Example: Install just the holepunch plugin
claude --plugin github:grandcamel/holepunch-plugin
```

## Plugins

### P2P Development

| Plugin | Repository | Description |
|--------|------------|-------------|
| **holepunch** | [grandcamel/holepunch-plugin](https://github.com/grandcamel/holepunch-plugin) | Build zero-infrastructure P2P apps with Holepunch ecosystem |
| **apds-dev** | [grandcamel/apds-plugin](https://github.com/grandcamel/apds-plugin) | APDS Personal Data Server development |
| **anproto** | [grandcamel/anproto-plugin](https://github.com/grandcamel/anproto-plugin) | ANProto ed25519 keypair management |
| **pearpass** | [grandcamel/pearpass-plugin](https://github.com/grandcamel/pearpass-plugin) | PearPass password manager development |
| **wiredove** | [grandcamel/wiredove-plugin](https://github.com/grandcamel/wiredove-plugin) | Wiredove decentralized social networking |

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
| **best-practices** | [grandcamel/best-practices-plugin](https://github.com/grandcamel/best-practices-plugin) | Development best practices for git, Docker, Claude Code |

## Working with Submodules

### Update all plugins to latest

```bash
git submodule update --remote --merge
git add .
git commit -m "chore: update all plugins to latest"
```

### Update a specific plugin

```bash
cd plugins/holepunch
git pull origin main
cd ../..
git add plugins/holepunch
git commit -m "chore(holepunch): update to latest"
```

### Initialize submodules after clone

If you cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

## Project Structure

```
grandcamel-plugins/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/                  # Git submodules
│   ├── holepunch/           → grandcamel/holepunch-plugin
│   ├── jira-assistant-skills/
│   ├── confluence-assistant-skills/
│   ├── splunk-assistant-skills/
│   ├── assistant-skills/
│   ├── best-practices/
│   ├── apds-dev/
│   ├── anproto/
│   ├── pearpass/
│   └── wiredove/
├── .gitmodules              # Submodule configuration
├── VERSION
├── README.md
├── CLAUDE.md
└── LICENSE
```

## Python Dependencies

Some plugins require Python libraries (installed via pip):

- **jira-assistant-skills**: `pip install jira-assistant-skills-lib`
- **confluence-assistant-skills**: `pip install confluence-assistant-skills-lib`
- **splunk-assistant-skills**: `pip install splunk-assistant-skills-lib`

## Contributing

Each plugin is maintained in its own repository. To contribute:

1. Fork the specific plugin repository
2. Make your changes
3. Submit a PR to the plugin repository

To add a new plugin to this marketplace, submit a PR adding the submodule.

## License

MIT - Each plugin may have its own license; check the individual repositories.

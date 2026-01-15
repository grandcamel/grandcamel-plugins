# Grandcamel Plugins Marketplace

Claude Code marketplace using git submodules to reference independent plugin repositories.

## Project Structure

```
grandcamel-plugins/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest
├── plugins/                  # Git submodules (not embedded code)
│   └── <plugin-name>/       → GitHub repository
├── .gitmodules              # Submodule URLs
├── VERSION
└── README.md
```

## Key Concept: Submodule Architecture

Each plugin in `plugins/` is a **git submodule** pointing to an external repository:

- Plugins are independently versioned and maintained
- This repo is an aggregator/index, not the source of truth
- Plugin updates are pulled from upstream repos

## Development Guidelines

### Adding a New Plugin

1. Create the plugin in its own GitHub repository
2. Add as submodule:
   ```bash
   git submodule add https://github.com/owner/repo.git plugins/plugin-name
   ```
3. Register in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "plugin-name",
     "source": "./plugins/plugin-name",
     "version": "1.0.0"
   }
   ```
4. Commit changes

### Updating Plugins

```bash
# Update all plugins
git submodule update --remote --merge

# Update specific plugin
cd plugins/plugin-name
git pull origin main
cd ../..
git add plugins/plugin-name
git commit -m "chore(plugin-name): update submodule"
```

### Versioning

- **Marketplace version**: In `VERSION` file - increment when adding/removing plugins
- **Plugin versions**: Managed in individual plugin repos, reflected in marketplace.json

### Commit Messages

Use conventional commits:
- `chore(<plugin>): update submodule` - Plugin updates
- `feat: add <plugin> plugin` - New plugins
- `docs:` - Documentation changes

## Plugin Repositories

| Plugin | Repository |
|--------|------------|
| holepunch | grandcamel/holepunch-plugin |
| jira-assistant-skills | grandcamel/JIRA-Assistant-Skills |
| confluence-assistant-skills | grandcamel/Confluence-Assistant-Skills |
| splunk-assistant-skills | grandcamel/Splunk-Assistant-Skills |
| assistant-skills | grandcamel/Assistant-Skills |
| best-practices | grandcamel/best-practices-plugin |
| apds-dev | grandcamel/apds-plugin |
| anproto | grandcamel/anproto-plugin |
| pearpass | grandcamel/pearpass-plugin |
| wiredove | grandcamel/wiredove-plugin |

## Testing

```bash
# Ensure submodules are initialized
git submodule update --init --recursive

# Test marketplace
claude --plugin-dir ./

# Test individual plugin
claude --plugin-dir ./plugins/holepunch
```

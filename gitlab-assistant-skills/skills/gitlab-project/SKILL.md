---
name: "gitlab-project-management"
description: "GitLab project and repository operations: list, view, create, clone, fork, search. ALWAYS use this skill when user wants to: (1) list their projects/repositories, (2) view project details, (3) create new projects, (4) clone or fork repositories, (5) search for projects. Triggers on phrases like 'list my projects', 'show repos', 'create a project', 'fork this repo', 'clone the repository'."
version: "1.0.0"
author: "gitlab-assistant-skills"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# gitlab-project

Core operations for GitLab projects and repositories using the `glab` CLI.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List projects | `-` | Read-only |
| View project | `-` | Read-only |
| Clone project | `-` | Local operation only |
| Search projects | `-` | Read-only |
| Fork project | `!` | Creates a new project |
| Create project | `!` | Creates a new project |
| Delete project | `!!!` | **IRREVERSIBLE** |

**Risk Legend**: `-` Safe, read-only | `!` Caution, modifiable | `!!` Warning, destructive but recoverable | `!!!` Danger, irreversible

## When to Use This Skill

Triggers: User asks to...
- List their GitLab projects or repositories
- View details of a specific project
- Create a new GitLab project/repository
- Clone a repository
- Fork a project
- Search for projects

## Prerequisites

Requires the `glab` CLI to be installed and authenticated:
```bash
glab auth status
```

## Available Commands

### List Projects

```bash
# List your own projects
glab repo list --mine

# List all accessible projects
glab repo list

# List with specific visibility
glab repo list --visibility public
glab repo list --visibility private
glab repo list --visibility internal

# List archived projects
glab repo list --archived

# Pagination
glab repo list --per-page 50 --page 2
```

### View Project Details

```bash
# View current project (from git directory)
glab repo view

# View specific project
glab repo view owner/project-name

# View in web browser
glab repo view --web

# Output as JSON
glab repo view --output json
```

### Create Projects

```bash
# Create interactively
glab repo create

# Create with name
glab repo create my-new-project

# Create with options
glab repo create my-project --description "Project description" --visibility private

# Create in a group/namespace
glab repo create my-group/my-project

# Initialize with README
glab repo create my-project --readme

# Create from template
glab repo create my-project --template group/template-project
```

### Clone Repositories

```bash
# Clone a project
glab repo clone owner/project-name

# Clone to specific directory
glab repo clone owner/project-name my-local-dir

# Clone with submodules
glab repo clone owner/project-name -- --recurse-submodules

# Clone all projects in a group
glab repo clone -g my-group
```

### Fork Projects

```bash
# Fork current project
glab repo fork

# Fork specific project
glab repo fork owner/project-name

# Fork and clone locally
glab repo fork --clone

# Fork to specific namespace
glab repo fork owner/project-name --namespace my-namespace
```

### Search Projects

```bash
# Search by name
glab repo search --search "project-name"

# Search within a group
glab repo search --search "query" --group my-group
```

### Other Operations

```bash
# List project contributors
glab repo contributors

# Archive a project
glab repo archive

# Transfer a project
glab repo transfer new-owner

# View/manage project members
glab repo members list
glab repo members add username --access-level developer
```

## Example Workflows

### Create and Clone a New Project

```bash
# 1. Create the project
glab repo create my-new-project --description "My awesome project" --visibility private

# 2. Clone it locally
glab repo clone my-username/my-new-project

# 3. Navigate to directory
cd my-new-project
```

### Fork and Contribute

```bash
# 1. Fork the upstream project
glab repo fork upstream-owner/project-name --clone

# 2. Navigate to the cloned fork
cd project-name

# 3. Create a feature branch
git checkout -b my-feature

# 4. Make changes and push
git push -u origin my-feature

# 5. Create MR to upstream (use gitlab-mr skill)
glab mr create --target-branch main --repo upstream-owner/project-name
```

## Common Options

| Option | Description |
|--------|-------------|
| `--mine` | Show only your own projects |
| `--visibility` | Filter by visibility (public/private/internal) |
| `--archived` | Include/filter archived projects |
| `--per-page` | Number of results per page |
| `--output` | Output format (text/json) |
| `-R, --repo` | Specify repository (OWNER/REPO format) |

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid or expired token | Run `glab auth login` |
| 403 Forbidden | Insufficient permissions | Check project access level |
| 404 Not Found | Project doesn't exist | Verify project path |
| "not a git repository" | Not in a git directory | Specify project with `-R owner/repo` |

## Related Skills

- **gitlab-issue**: Issue management
- **gitlab-mr**: Merge request workflows
- **gitlab-ci**: CI/CD pipelines

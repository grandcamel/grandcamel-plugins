---
name: "gitlab-issue-management"
description: "GitLab issue operations: list, view, create, update, close, comment. ALWAYS use this skill when user wants to: (1) list/show issues, (2) view issue details, (3) create new issues/bugs/tasks, (4) update or edit issues, (5) close/reopen issues, (6) add comments to issues. Triggers on 'show issues', 'create an issue', 'open a bug', 'close issue #X', 'comment on issue'."
version: "1.0.0"
author: "gitlab-assistant-skills"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# gitlab-issue

Issue tracking and management for GitLab using the `glab` CLI.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List issues | `-` | Read-only |
| View issue | `-` | Read-only |
| Create issue | `-` | Easily reversible |
| Add comment | `!` | Cannot be deleted by CLI |
| Update issue | `!` | Can be undone via edit |
| Close issue | `!` | Can reopen |
| Delete issue | `!!!` | **IRREVERSIBLE** |

**Risk Legend**: `-` Safe, read-only | `!` Caution, modifiable | `!!` Warning, destructive but recoverable | `!!!` Danger, irreversible

## When to Use This Skill

Triggers: User asks to...
- List or show issues (open, closed, all)
- View details of a specific issue
- Create a new issue, bug report, or task
- Update issue title, description, labels, assignees
- Close or reopen an issue
- Add a comment/note to an issue
- Subscribe to issue notifications

## Prerequisites

Requires the `glab` CLI to be installed and authenticated:
```bash
glab auth status
```

## Available Commands

### List Issues

```bash
# List open issues in current project
glab issue list

# List all issues (including closed)
glab issue list --all

# List only closed issues
glab issue list --closed

# Filter by label
glab issue list --label "bug"
glab issue list --label "bug,urgent"

# Filter by assignee
glab issue list --assignee @me
glab issue list --assignee username

# Filter by author
glab issue list --author @me

# Filter by milestone
glab issue list --milestone "v1.0"

# Search in title/description
glab issue list --search "login"

# Specify project
glab issue list -R owner/project

# Output format
glab issue list --output json
```

### View Issue Details

```bash
# View specific issue
glab issue view 42

# View in web browser
glab issue view 42 --web

# Include comments
glab issue view 42 --comments

# Output as JSON
glab issue view 42 --output json

# View from another project
glab issue view 42 -R owner/project
```

### Create Issues

```bash
# Create interactively
glab issue create

# Create with title
glab issue create --title "Bug: Login fails on mobile"

# Create with title and description
glab issue create --title "Feature request" --description "Add dark mode support"

# Create with labels
glab issue create --title "Fix crash" --label "bug,critical"

# Create and assign
glab issue create --title "Task" --assignee username
glab issue create --title "Task" --assignee @me

# Create with milestone
glab issue create --title "Release task" --milestone "v2.0"

# Create confidential issue
glab issue create --title "Security issue" --confidential

# Create with due date
glab issue create --title "Deadline task" --due-date "2024-12-31"

# Create with weight (if using issue weights)
glab issue create --title "Weighted task" --weight 5

# Open editor for description
glab issue create --title "Complex issue" --editor
```

### Update Issues

```bash
# Update title
glab issue update 42 --title "New title"

# Update description
glab issue update 42 --description "Updated description"

# Add labels
glab issue update 42 --label "bug,verified"

# Remove all labels
glab issue update 42 --unlabel "*"

# Change assignee
glab issue update 42 --assignee username
glab issue update 42 --unassign  # Remove assignee

# Update milestone
glab issue update 42 --milestone "v2.0"

# Mark as confidential
glab issue update 42 --confidential

# Lock discussion
glab issue update 42 --lock-discussion
```

### Close and Reopen Issues

```bash
# Close an issue
glab issue close 42

# Reopen an issue
glab issue reopen 42
```

### Add Comments/Notes

```bash
# Add a comment
glab issue note 42 --message "This is my comment"

# Add multiline comment
glab issue note 42 --message "Line 1
Line 2
Line 3"

# Open editor for comment
glab issue note 42 --editor
```

### Subscribe/Unsubscribe

```bash
# Subscribe to notifications
glab issue subscribe 42

# Unsubscribe
glab issue unsubscribe 42
```

### Delete Issues

```bash
# Delete an issue (IRREVERSIBLE)
glab issue delete 42
```

## Example Workflows

### Bug Report Workflow

```bash
# 1. Create a bug report
glab issue create \
  --title "Bug: App crashes on startup" \
  --description "## Steps to Reproduce
1. Open the app
2. Click login
3. App crashes

## Expected Behavior
Should show login screen

## Environment
- OS: macOS 14.0
- App Version: 2.1.0" \
  --label "bug,needs-triage"

# Output: Created issue #42

# 2. View the created issue
glab issue view 42

# 3. Add more context via comment
glab issue note 42 --message "Attaching crash logs in next comment"
```

### Triage Workflow

```bash
# 1. List unassigned bugs
glab issue list --label "bug" --assignee ""

# 2. Assign and label
glab issue update 42 --assignee developer-username --label "bug,in-progress"

# 3. Add to milestone
glab issue update 42 --milestone "Sprint 5"
```

### Close with Reference

```bash
# Add closing comment with MR reference
glab issue note 42 --message "Fixed in !123"

# Close the issue
glab issue close 42
```

## Common Options

| Option | Description |
|--------|-------------|
| `--label, -l` | Filter or set labels |
| `--assignee, -a` | Filter or set assignee |
| `--milestone, -m` | Filter or set milestone |
| `--author` | Filter by author |
| `--search` | Search in title/description |
| `--confidential` | Mark as confidential |
| `--output` | Output format (text/json) |
| `-R, --repo` | Specify repository |

## Issue Board Operations

```bash
# List boards
glab issue board list

# View board
glab issue board view 1
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Run `glab auth login` |
| 403 Forbidden | No access to project | Check project permissions |
| 404 Not Found | Issue doesn't exist | Verify issue number |
| "not a git repository" | Not in git directory | Use `-R owner/repo` |
| Invalid label | Label doesn't exist | Create label first or check spelling |

## Related Skills

- **gitlab-project**: Project management
- **gitlab-mr**: Merge requests (create MR to fix issues)
- **gitlab-ci**: CI/CD pipelines

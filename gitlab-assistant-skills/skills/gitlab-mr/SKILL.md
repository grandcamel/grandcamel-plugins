---
name: "gitlab-merge-request-management"
description: "GitLab merge request (MR) operations: list, view, create, merge, approve, review. ALWAYS use this skill when user wants to: (1) list merge requests, (2) view MR details or diff, (3) create new merge requests, (4) merge or approve MRs, (5) checkout MR branches locally, (6) add comments to MRs. Triggers on 'show MRs', 'create merge request', 'merge !X', 'approve MR', 'review the diff'."
version: "1.0.0"
author: "gitlab-assistant-skills"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# gitlab-mr

Merge request workflows for GitLab using the `glab` CLI.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List MRs | `-` | Read-only |
| View MR/diff | `-` | Read-only |
| Checkout MR | `-` | Local operation |
| Create MR | `!` | Can be closed |
| Add comment | `!` | Cannot be deleted via CLI |
| Update MR | `!` | Can be undone |
| Approve MR | `!` | Can revoke |
| Merge MR | `!!` | Merges code to target branch |
| Delete MR | `!!!` | **IRREVERSIBLE** |

**Risk Legend**: `-` Safe, read-only | `!` Caution, modifiable | `!!` Warning, destructive but recoverable | `!!!` Danger, irreversible

## When to Use This Skill

Triggers: User asks to...
- List merge requests (open, merged, closed)
- View MR details, diff, or changes
- Create a new merge request
- Merge or approve a merge request
- Checkout an MR branch locally
- Add review comments
- Rebase or update an MR

## Prerequisites

Requires the `glab` CLI to be installed and authenticated:
```bash
glab auth status
```

## Available Commands

### List Merge Requests

```bash
# List open MRs in current project
glab mr list

# List all MRs (including merged/closed)
glab mr list --all

# List merged MRs
glab mr list --merged

# List closed MRs
glab mr list --closed

# Filter by author
glab mr list --author @me
glab mr list --author username

# Filter by assignee
glab mr list --assignee @me

# Filter by reviewer
glab mr list --reviewer @me

# Filter by label
glab mr list --label "needs-review"

# Filter by target branch
glab mr list --target-branch main

# Filter by source branch
glab mr list --source-branch feature-x

# Search in title
glab mr list --search "fix login"

# From specific project
glab mr list -R owner/project

# Output format
glab mr list --output json
```

### View Merge Request Details

```bash
# View specific MR
glab mr view 123

# View by branch name
glab mr view feature-branch

# View in web browser
glab mr view 123 --web

# Include comments
glab mr view 123 --comments

# Output as JSON
glab mr view 123 --output json
```

### View MR Diff

```bash
# View diff for MR
glab mr diff 123

# View diff with color
glab mr diff 123 --color always

# View diff for current branch's MR
glab mr diff
```

### Create Merge Requests

```bash
# Create interactively
glab mr create

# Create with auto-fill from commits
glab mr create --fill

# Create with specific title
glab mr create --title "Add user authentication"

# Create with title and description
glab mr create --title "Feature: Dark mode" --description "Implements dark mode toggle"

# Specify source and target branches
glab mr create --source-branch feature-x --target-branch develop

# Create draft/WIP MR
glab mr create --draft --title "WIP: New feature"

# Create with labels
glab mr create --fill --label "feature,needs-review"

# Assign reviewers
glab mr create --fill --reviewer username1,username2

# Assign to yourself
glab mr create --fill --assignee @me

# Create for an issue (auto-closes issue on merge)
glab mr for 42  # Creates MR that closes issue #42

# Allow collaboration (maintainers can push)
glab mr create --fill --allow-collaboration

# Create and push current branch
glab mr create --fill --push

# Delete source branch on merge
glab mr create --fill --remove-source-branch

# Squash commits on merge
glab mr create --fill --squash
```

### Approve Merge Requests

```bash
# Approve an MR
glab mr approve 123

# Approve with optional message (via note)
glab mr approve 123
glab mr note 123 --message "LGTM! Approved."
```

### Revoke Approval

```bash
# Revoke your approval
glab mr revoke 123
```

### Merge Merge Requests

```bash
# Merge an MR
glab mr merge 123

# Merge with squash
glab mr merge 123 --squash

# Merge and delete source branch
glab mr merge 123 --remove-source-branch

# Merge when pipeline succeeds
glab mr merge 123 --when-pipeline-succeeds

# Merge with custom commit message
glab mr merge 123 --message "Merge feature X into main"

# Rebase before merge
glab mr merge 123 --rebase
```

### Checkout MR Locally

```bash
# Checkout MR branch
glab mr checkout 123

# Checkout by branch name
glab mr checkout feature-branch

# Checkout and create local branch with custom name
glab mr checkout 123 --branch my-review-branch
```

### Rebase MR

```bash
# Rebase MR against target
glab mr rebase 123

# Skip CI on rebase
glab mr rebase 123 --skip-ci
```

### Add Comments/Notes

```bash
# Add a comment
glab mr note 123 --message "Please add tests for this change"

# Open editor for comment
glab mr note 123 --editor
```

### Update Merge Request

```bash
# Update title
glab mr update 123 --title "New title"

# Update description
glab mr update 123 --description "Updated description"

# Add labels
glab mr update 123 --label "reviewed,approved"

# Remove draft status
glab mr update 123 --ready

# Mark as draft
glab mr update 123 --draft

# Change target branch
glab mr update 123 --target-branch develop

# Lock discussion
glab mr update 123 --lock-discussion
```

### Close and Reopen MRs

```bash
# Close an MR
glab mr close 123

# Reopen an MR
glab mr reopen 123
```

### List Approvers

```bash
# List eligible approvers
glab mr approvers 123
```

### Related Issues

```bash
# List issues related to MR
glab mr issues 123
```

## Example Workflows

### Feature Development Flow

```bash
# 1. Create feature branch and make changes
git checkout -b feature/user-auth
# ... make changes ...
git commit -am "Add user authentication"

# 2. Push and create MR
git push -u origin feature/user-auth
glab mr create --fill --label "feature" --reviewer tech-lead

# Output: Created MR !42

# 3. View the MR
glab mr view 42
```

### Code Review Flow

```bash
# 1. List MRs assigned for review
glab mr list --reviewer @me

# 2. Checkout MR to test locally
glab mr checkout 42

# 3. View the diff
glab mr diff 42

# 4. Add review comment
glab mr note 42 --message "Please add error handling for the API call"

# 5. After fixes, approve
glab mr approve 42
```

### Quick Merge Flow

```bash
# 1. View MR status
glab mr view 42

# 2. Check CI status
glab ci status

# 3. Merge with squash and delete branch
glab mr merge 42 --squash --remove-source-branch
```

### Create MR for Issue Fix

```bash
# Create MR that will close issue #15 on merge
glab mr for 15 --fill

# This adds "Closes #15" to the MR description
```

## Common Options

| Option | Description |
|--------|-------------|
| `--draft` | Create as draft MR |
| `--fill` | Auto-fill from commit messages |
| `--squash` | Squash commits on merge |
| `--remove-source-branch` | Delete source branch on merge |
| `--label, -l` | Set labels |
| `--assignee, -a` | Set assignee |
| `--reviewer` | Set reviewers |
| `--target-branch` | Target branch for MR |
| `--source-branch` | Source branch for MR |
| `-R, --repo` | Specify repository |

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Run `glab auth login` |
| 403 Forbidden | No merge permission | Check project permissions |
| 404 Not Found | MR doesn't exist | Verify MR ID |
| "has conflicts" | Merge conflicts | Rebase or resolve manually |
| "pipeline must succeed" | CI required | Wait for CI or fix failures |
| "requires approval" | Approvals needed | Get required approvals first |

## Related Skills

- **gitlab-project**: Project management
- **gitlab-issue**: Issue tracking
- **gitlab-ci**: CI/CD pipelines (check before merge)

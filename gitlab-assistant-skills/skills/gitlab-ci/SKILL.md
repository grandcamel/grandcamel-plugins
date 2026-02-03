---
name: "gitlab-ci-cd-management"
description: "GitLab CI/CD pipeline operations: list, view, run, cancel, trace jobs. ALWAYS use this skill when user wants to: (1) check pipeline status, (2) view CI/CD pipelines, (3) run/trigger pipelines, (4) cancel running pipelines, (5) view job logs, (6) retry failed jobs, (7) lint CI config. Triggers on 'CI status', 'pipeline status', 'run pipeline', 'show job logs', 'cancel build', 'retry job'."
version: "1.0.0"
author: "gitlab-assistant-skills"
license: "MIT"
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
---

# gitlab-ci

CI/CD pipeline management for GitLab using the `glab` CLI.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List pipelines | `-` | Read-only |
| View status | `-` | Read-only |
| View job logs | `-` | Read-only |
| Lint CI config | `-` | Read-only |
| Download artifacts | `-` | Downloads to local |
| Retry job | `!` | Re-runs a job |
| Trigger job | `!` | Starts manual job |
| Run pipeline | `!` | Creates new pipeline |
| Cancel pipeline | `!!` | Stops running jobs |
| Delete pipeline | `!!!` | **IRREVERSIBLE** |

**Risk Legend**: `-` Safe, read-only | `!` Caution, modifiable | `!!` Warning, destructive but recoverable | `!!!` Danger, irreversible

## When to Use This Skill

Triggers: User asks to...
- Check CI/CD or pipeline status
- List pipelines for a project/branch
- Run or trigger a pipeline
- Cancel a running pipeline
- View job logs or trace output
- Retry a failed job
- Trigger a manual job
- Lint `.gitlab-ci.yml` configuration
- Download job artifacts

## Prerequisites

Requires the `glab` CLI to be installed and authenticated:
```bash
glab auth status
```

## Available Commands

### Pipeline Status

```bash
# View current pipeline status (current branch)
glab ci status

# View status for specific branch
glab ci status --branch main

# Watch status in real-time
glab ci status --live

# Compact view
glab ci status --compact
```

### List Pipelines

```bash
# List recent pipelines
glab ci list

# List with specific status
glab ci list --status running
glab ci list --status failed
glab ci list --status success
glab ci list --status pending

# List for specific branch
glab ci list --branch feature-x

# Pagination
glab ci list --per-page 20

# From specific project
glab ci list -R owner/project

# Output format
glab ci list --output json
```

### View Pipeline

```bash
# View pipeline interactively (select jobs, view logs)
glab ci view

# View specific branch pipeline
glab ci view main

# View specific ref (branch/tag)
glab ci view v1.0.0

# Open in web browser
glab ci view --web
```

### Get Pipeline Details

```bash
# Get pipeline JSON (current branch)
glab ci get

# Get for specific branch
glab ci get --branch main

# Get specific pipeline by ID
glab ci get --pipeline-id 12345

# Output format
glab ci get --output json
```

### Run Pipelines

```bash
# Run pipeline for current branch
glab ci run

# Run for specific branch
glab ci run --branch main

# Run with variables
glab ci run --variables "DEPLOY_ENV:production"
glab ci run --variables "KEY1:value1,KEY2:value2"

# Run with variable from file
glab ci run --variables-file vars.env
```

### Cancel Pipelines

```bash
# Cancel current branch pipeline
glab ci cancel

# Cancel specific branch pipeline
glab ci cancel --branch feature-x

# Cancel specific pipeline
glab ci cancel pipeline 12345

# Cancel specific job
glab ci cancel job 67890
```

### View Job Logs (Trace)

```bash
# Trace job output in real-time
glab ci trace

# Trace specific job by ID
glab ci trace 12345

# Trace job by name
glab ci trace --job-name "build"

# Trace for specific branch
glab ci trace --branch main
```

### Retry Failed Jobs

```bash
# Retry a specific job
glab ci retry 12345

# Retry with debug logging
glab ci retry 12345 --debug
```

### Trigger Manual Jobs

```bash
# Trigger a manual job
glab ci trigger 12345

# Trigger with variables
glab ci trigger 12345 --variables "DEPLOY_TARGET:staging"
```

### Download Artifacts

```bash
# Download artifacts from latest pipeline
glab ci artifact main build

# Download to specific path
glab ci artifact main build --path ./artifacts

# Download specific artifact
glab ci artifact main test --artifact-name coverage.xml
```

### Lint CI Configuration

```bash
# Lint .gitlab-ci.yml
glab ci lint

# Lint specific file
glab ci lint path/to/gitlab-ci.yml

# Lint with merged YAML output
glab ci lint --include-jobs

# Validate specific ref
glab ci lint --ref main
```

### Delete Pipelines

```bash
# Delete specific pipeline (IRREVERSIBLE)
glab ci delete 12345

# Delete without confirmation
glab ci delete 12345 --yes

# Delete with dry-run
glab ci delete 12345 --dry-run
```

### CI Configuration

```bash
# Generate CI config interactively
glab ci config generate

# Validate CI config
glab ci config validate
```

## Example Workflows

### Check and Fix Failing Pipeline

```bash
# 1. Check current pipeline status
glab ci status

# 2. If failed, view detailed status
glab ci view

# 3. Trace the failing job's logs
glab ci trace --job-name "test"

# 4. After fixing code and pushing
git push

# 5. Watch new pipeline
glab ci status --live
```

### Deploy to Production

```bash
# 1. Check that tests pass
glab ci status --branch main

# 2. Trigger deployment pipeline with variables
glab ci run --branch main --variables "DEPLOY_ENV:production"

# 3. Watch deployment
glab ci status --live

# 4. View deployment job logs
glab ci trace --job-name "deploy"
```

### Debug CI Configuration

```bash
# 1. Lint the CI file
glab ci lint

# 2. View merged configuration (includes templates)
glab ci lint --include-jobs

# 3. Validate syntax is correct
glab ci config validate
```

### Retry After Transient Failure

```bash
# 1. Check status
glab ci status
# Shows: test job failed

# 2. View the failure
glab ci trace --job-name "test"
# Shows: network timeout (transient error)

# 3. Get the job ID and retry
glab ci retry 12345

# 4. Watch the retry
glab ci status --live
```

### Monitor Pipeline in Real-Time

```bash
# Interactive view with job selection
glab ci view

# Or watch status continuously
glab ci status --live
```

## Pipeline Variables

```bash
# Pass single variable
glab ci run --variables "KEY:value"

# Pass multiple variables
glab ci run --variables "KEY1:value1,KEY2:value2"

# Pass from file (KEY=value format per line)
glab ci run --variables-file my-vars.env
```

## Common Options

| Option | Description |
|--------|-------------|
| `--branch, -b` | Specify branch |
| `--pipeline-id` | Specific pipeline ID |
| `--job-name` | Specific job name |
| `--live` | Watch in real-time |
| `--compact` | Compact output |
| `--variables` | Pipeline variables |
| `--output` | Output format (text/json) |
| `-R, --repo` | Specify repository |

## Job States

| State | Description |
|-------|-------------|
| `pending` | Waiting for runner |
| `running` | Currently executing |
| `success` | Completed successfully |
| `failed` | Completed with errors |
| `canceled` | Manually canceled |
| `skipped` | Skipped due to rules |
| `manual` | Awaiting manual trigger |
| `scheduled` | Scheduled for later |

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Run `glab auth login` |
| 403 Forbidden | No CI access | Check project permissions |
| "no pipelines found" | No CI configured | Check `.gitlab-ci.yml` exists |
| "no runners available" | No runners assigned | Check runner configuration |
| Lint errors | Invalid YAML syntax | Fix `.gitlab-ci.yml` syntax |
| Job stuck pending | Runner unavailable | Check runner status |

## Related Skills

- **gitlab-project**: Project management
- **gitlab-issue**: Issue tracking (create issue for CI failures)
- **gitlab-mr**: Merge requests (check CI before merge)

---
name: browse-skills
description: Browse all available GitLab skills with descriptions and examples
---

# Browse GitLab Skills

Display the available GitLab Assistant Skills to the user in a helpful format.

## Available Skills

### gitlab-project
**Project and repository management**

Operations:
- List projects (`glab repo list`)
- View project details (`glab repo view`)
- Create projects (`glab repo create`)
- Clone repositories (`glab repo clone`)
- Fork projects (`glab repo fork`)
- Search projects (`glab repo search`)

Example triggers:
- "List my GitLab projects"
- "Show details of project X"
- "Create a new GitLab repo"
- "Fork this repository"

---

### gitlab-issue
**Issue tracking and management**

Operations:
- List issues (`glab issue list`)
- View issue details (`glab issue view`)
- Create issues (`glab issue create`)
- Update issues (`glab issue update`)
- Close/reopen issues (`glab issue close/reopen`)
- Comment on issues (`glab issue note`)

Example triggers:
- "Show open issues in this project"
- "Create a bug report for the login page"
- "Close issue #42"
- "Add a comment to issue #15"

---

### gitlab-mr
**Merge request workflows**

Operations:
- List merge requests (`glab mr list`)
- View MR details (`glab mr view`)
- Create merge requests (`glab mr create`)
- Merge/approve MRs (`glab mr merge/approve`)
- Review diffs (`glab mr diff`)
- Checkout MRs locally (`glab mr checkout`)

Example triggers:
- "Show open merge requests"
- "Create a merge request for this branch"
- "Approve MR !123"
- "Merge the feature branch MR"
- "Show the diff for MR !45"

---

### gitlab-ci
**CI/CD pipeline management**

Operations:
- List pipelines (`glab ci list`)
- View pipeline status (`glab ci status`)
- Run pipelines (`glab ci run`)
- Cancel pipelines (`glab ci cancel`)
- View job logs (`glab ci trace`)
- Trigger manual jobs (`glab ci trigger`)

Example triggers:
- "What's the CI status?"
- "Run the pipeline for this branch"
- "Show the logs for the failing job"
- "Cancel the current pipeline"
- "Retry the failed job"

---

## Quick Reference

| Task | Command |
|------|---------|
| List my projects | `glab repo list --mine` |
| Open issues | `glab issue list --opened` |
| My MRs | `glab mr list --author=@me` |
| Pipeline status | `glab ci status` |
| View issue | `glab issue view <id>` |
| View MR | `glab mr view <id>` |
| Create issue | `glab issue create` |
| Create MR | `glab mr create` |

## Getting Started

If you haven't set up GitLab yet, run:
```
/gitlab-assistant-setup
```

Or ask me to help you set up GitLab authentication.

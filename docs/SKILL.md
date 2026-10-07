---
name: zos-ipl-automation
description: Sets up a GitHub Projects v2 board and creates migration issues from the supported sheets in the repository workbook. Post-IPL validation and dashboard stages are not implemented.
---

<!-- D100726T0227 | HA-0001 | correct migration script paths | JC | ha-ops repo -->
<!-- D20261007T0600 | HA-0011 | align docs with implemented automation | JC | ha-ops repo -->

# z/OS 3.2 Migration Issue Automation

## Overview

The repository implements GitHub Project board setup and issue creation from
the migration workbook. Post-IPL validation, Jira synchronization, CAB
sign-off, and the IPL dashboard are not implemented here; they must not be
treated as available workflow stages.

## Prerequisites

- A GitHub repository and token with permissions to create issues, labels,
  milestones, and Project items.
- Python dependencies installed with `pip install -r docs/requirements.txt`.
- Optional `.env` file with `GH_TOKEN`, `GH_REPO`, and exactly one project
  owner (`GH_ORG` or `GH_USER`).

Run commands from the repository root. The default workbook is
`docs/zos-migration-risk-comparison.xlsx`. `GH_WORKBOOK` may override the
default with a path relative to the repository root; the `--workbook` option
takes precedence over `GH_WORKBOOK`.

## Steps

### 1. Set up the GitHub Project board

Run `python docs/setup_project_board.py --token "$GH_TOKEN" --repo "$GH_REPO" --org "$GH_ORG"`.
For a user-owned Project, set `GH_USER` and use `--user "$GH_USER"` instead.

### 2. Create migration issues

Preview before making changes:

```bash
python docs/create_migration_issues.py --token "$GH_TOKEN" --repo "$GH_REPO" --dry-run
```

Create issues and optionally add them to a Project:

```bash
python docs/create_migration_issues.py --token "$GH_TOKEN" --repo "$GH_REPO" --project-id "$GH_PROJECT_ID"
```

The script creates issues from the supported sheets only:

- `PARMLIB Changes`
- `Deprecated & Removed`
- `Function Matrix`

The workbook also contains `Overview` and `Security Requirements`, which are
not supported for issue creation. Requesting an unsupported sheet with
`--sheets` fails before any GitHub changes are made.

### Future stages (not implemented)

The repository does not contain a post-IPL validation workflow or
`dashboard/ipl-migration-dashboard.html`. Validation, blocker transitions,
Jira/CAB actions, and dashboard monitoring are specified requirements only.
Do not trigger a nonexistent workflow or treat these outcomes as operational.

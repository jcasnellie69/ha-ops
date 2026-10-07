---
name: zos-ipl-automation
description: Automates the complete z/OS 3.2 post-IPL validation and migration management pipeline. Sets up GitHub Project board, creates migration issues from Excel, runs post-IPL validation checks (PARMLIB, RACF/ICSF, JES2, OMVS), auto-closes resolved IPL blockers, syncs to Jira, and generates a signed-off CAB migration completion report with a real-time dashboard. Use when teams need end-to-end z/OS 3.2 migration automation from GitHub board setup through production IPL sign-off.
---

<!-- D100726T0227 | HA-0001 | correct migration script paths | JC | ha-ops repo -->

# z/OS 3.2 Post-IPL Validation & Migration Automation

## Overview
This workflow automates the complete z/OS 3.2 migration lifecycle:
1. GitHub Project board setup with sprint fields and views
2. Migration issue creation from Excel workbook (~78 issues)
3. Post-IPL validation suite (PARMLIB, RACF/ICSF, JES2, OMVS)
4. Real-time dashboard for blocker escalation and sync monitoring

## Parameters
- **ipl_lpar** (required): Target LPAR name (e.g. SYSA)
- **ipl_timestamp** (required): IPL completion timestamp ISO 8601
- **environment** (required, default: non-production): Environment type
- **cab_change_id** (optional): CAB Change Record ID for sign-off
- **jira_epic_key** (optional): Jira epic to update with results

## Prerequisites
Before running this workflow, ensure:
- GitHub repo exists with secrets: ZOSMF_HOST, ZOSMF_USER, ZOSMF_PASS, SLACK_WEBHOOK_MIGRATION, JIRA_URL, JIRA_TOKEN, GH_TOKEN
- Excel workbook at: excel_report/zos-migration-risk/zos-migration-risk-comparison.xlsx
- Python virtual environment with openpyxl and requests installed
- .env file configured with GH_TOKEN, GH_REPO, GH_ORG

## Steps

Run Steps 1–2 from the repository root.

### Step 1: Setup GitHub Project Board

**Starting Step 1/4: Setup GitHub Project Board**

python docs/setup_project_board.py --token $GH_TOKEN --repo $GH_REPO --org $GH_ORG --start-date 2026-10-01

This creates the GitHub Projects v2 board with:
- 8 custom fields: Sprint (iteration), Priority, Component, Risk Level, IPL Blocker, Effort, Source Sheet, Notes
- 6 sprint iterations (2-week cadence)
- 6 views: Sprint Board, Sprint Backlog, IPL Blockers, By Component, Security Track, All Issues
- Saves project_board_config.json with project ID and field IDs

After completion, copy GH_PROJECT_ID from project_board_config.json to .env

**Completed Step 1/4: Setup GitHub Project Board ✓**

---

### Step 2: Create Migration Issues from Excel

**Starting Step 2/4: Create Migration Issues from Excel**

python docs/create_migration_issues.py --token $GH_TOKEN --repo $GH_REPO --project-id $GH_PROJECT_ID

This parses all 3 sheets from the Excel workbook and creates ~78 GitHub Issues:
- PARMLIB Changes: ~21 issues (Sprint 1-3 by risk level)
- Deprecated & Removed: ~16 issues (Sprint 1-2, IPL blockers first)
- Function Matrix: ~41 issues (Sprint 2-5 by focus area)

Each issue includes full detail table, required action, acceptance criteria, sprint label, and milestone.

(Note: In the original conversation, the user selected professional theme and blue color scheme for the PPT presentation. The Excel workbook was generated with 5 sheets covering Overview, PARMLIB Changes, Deprecated & Removed, Security Requirements, and Function Matrix.)

**Completed Step 2/4: Create Migration Issues from Excel ✓**

---

### Step 3: Run Post-IPL Validation Suite

**Starting Step 3/4: Run Post-IPL Validation Suite**

Trigger the post-IPL validation GitHub Actions workflow for LPAR {ipl_lpar} at timestamp {ipl_timestamp} in {environment} environment.

If cab_change_id is provided ({cab_change_id}), include it in the validation report for CAB sign-off.
If jira_epic_key is provided ({jira_epic_key}), update the Jira epic with validation results and transition to Done if all checks pass.

The workflow runs 4 parallel validation jobs:
1. PARMLIB Parameter Verification — checks 10 critical parameters via z/OSMF REST API
2. RACF & ICSF Health Probes — 11 probes for RACF subsystem and ICSF PQC algorithms
3. JES2 Spool Status Check — 5 checks for JES2 health and spool utilization
4. OMVS Filesystem Mount Validation — 8 checks including HFS-free verification

On success: auto-closes all open ipl-blocker issues, updates Projects v2 status to Done, creates signed-off report issue, notifies Slack.
On failure: creates failure report issue, sends escalation alerts, keeps blockers open.

To trigger manually via GitHub CLI:
gh workflow run post_ipl_validate.yml \
  -f ipl_lpar={ipl_lpar} \
  -f ipl_timestamp={ipl_timestamp} \
  -f environment={environment} \
  -f cab_change_id={cab_change_id} \
  -f jira_epic_key={jira_epic_key}

Or via repository_dispatch for automated triggering from z/OSMF:
curl -X POST https://api.github.com/repos/$GH_REPO/dispatches \
  -H "Authorization: Bearer $GH_TOKEN" \
  -d '{"event_type":"ipl-complete","client_payload":{"lpar":"{ipl_lpar}","timestamp":"{ipl_timestamp}","environment":"{environment}"}}'

**Completed Step 3/4: Run Post-IPL Validation Suite ✓**

---

### Step 4: Generate Real-Time Dashboard

**Starting Step 4/4: Generate Real-Time Dashboard**

Open the interactive IPL validation and blocker escalation dashboard:
dashboard/ipl-migration-dashboard.html

The dashboard shows:
- KPI tiles: Open IPL Blockers, SLA Breached, Closed Today, Jira Sync Lag
- Post-IPL Validation Checks panel with pass/fail/warn status for all 14 checks on {ipl_lpar}
- IPL Blockers by Sprint bar chart
- SLA Breach Timeline showing all open blockers with age bars and breach status
- Blockers by Component horizontal bar chart
- Team x Sprint Heat Map showing unresolved critical issues per team per sprint
- GitHub-to-Jira Sync Metrics panel
- Validation Progress rings (PARMLIB, RACF/ICSF, JES2, OMVS)
- 7-Day Blocker Trend line chart
- Recent Activity table with all events

To serve locally:
python -m http.server 8080 --directory dashboard/
# Then open: http://localhost:8080/ipl-migration-dashboard.html

To connect to live GitHub data, replace the DATA object in the dashboard with GitHub API calls using your GH_TOKEN.

**Completed Step 4/4: Generate Real-Time Dashboard ✓**
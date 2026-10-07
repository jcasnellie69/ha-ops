# D100726T0227 | HA-0001 | correct migration script paths | JC | ha-ops repo
# z/OS 3.2 Migration — GitHub Automation Scripts

Two scripts to fully automate your GitHub Project board and issue creation
from the z/OS 3.2 Migration Risk Comparison Excel workbook.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `setup_project_board.py` | Create GitHub Projects v2 board with fields, views, sprints |
| `create_migration_issues.py` | Parse Excel workbook → create GitHub Issues with labels & milestones |

---

## Quick Start

Run all commands from the repository root.

### 1. Install dependencies
```bash
pip install -r docs/requirements.txt
```

### 2. Configure environment
```bash
cp docs/.env.template .env
# Edit .env with your GitHub token and repo, then run:
set -a
. ./.env
set +a
```

### 3. Set up the Project board FIRST
```bash
python docs/setup_project_board.py \
  --token $GH_TOKEN \
  --repo yourorg/zos-32-migration \
  --org yourorg \
  --start-date 2026-10-01

# Output: project_board_config.json  ← contains your project ID
```

### 4. Create all migration issues
```bash
python docs/create_migration_issues.py \
  --token $GH_TOKEN \
  --repo yourorg/zos-32-migration \
  --project-id PVT_kgDOBxxxxxx    # from project_board_config.json
```

### 5. Dry run first (always recommended)
```bash
python docs/create_migration_issues.py \
  --token $GH_TOKEN \
  --repo yourorg/zos-32-migration \
  --dry-run
```

---

## Project Board Structure

### Status Columns (Kanban)
```
📥 Backlog → 🏃 In Sprint → 🔨 In Progress → 👀 In Review → ✅ Done
```

### Custom Fields
| Field | Type | Values |
|-------|------|--------|
| Sprint | Iteration | Sprint 1–6 (2-week cadence) |
| Priority | Single Select | 🔴 Critical / 🟠 Important / 🟢 Beneficial |
| Component | Single Select | BCP, RACF, ICSF, OMVS, DFSMS, Comm Server, etc. |
| Risk Level | Single Select | 💥 IPL Failure / 🔴 High / 🟡 Medium / 🟢 Low |
| IPL Blocker | Single Select | YES — Must fix before IPL / NO |
| Effort | Single Select | 1 day → 6+ months |
| Source Sheet | Single Select | PARMLIB Changes / Deprecated & Removed / Function Matrix |
| Notes | Text | Free-form notes |

### Views
| View | Layout | Purpose |
|------|--------|---------|
| Sprint Board | Board | Kanban by Status — primary working view |
| Sprint Backlog | Table | Current sprint items — planning view |
| IPL Blockers | Table | Filtered to ipl-blocker label — pre-IPL checklist |
| By Component | Table | Grouped by Component — system programmer view |
| Security Track | Table | Filtered to security/qsc — security team view |
| All Issues | Table | Full table — management reporting |

### Sprint Plan
| Sprint | Theme | Focus |
|--------|-------|-------|
| Sprint 1 | IPL Blockers & Foundation | HFS params, VRREGN/VREALSZ, JES3, first IPL test |
| Sprint 2 | Security Architecture | ICSF PQC, System SSL, RACF enhancements |
| Sprint 3 | PARMLIB Hardening | CPENABLE=SYSTEM, IARPRMxx, DIAGxx, SMFLIMxx |
| Sprint 4 | AI Workload Enablement | AI System Services, WLM Policy Advisor, zDNN |
| Sprint 5 | Cloud & Observability | OpenTelemetry, OAM REST, Docker, z/OSMF |
| Sprint 6 | Validation & Cutover | Full IPL test, SMF validation, production cutover |

---

## GitHub Token Permissions

Create a **Fine-grained PAT** at `github.com/settings/tokens` with:

| Permission | Access | Why |
|------------|--------|-----|
| Issues | Read & Write | Create/update issues |
| Projects | Read & Write | Create board, add items, set fields |
| Repository | Read & Write | Create labels, milestones |

Scope the token to **only your migration repository** for security.

---

## VS Code Integration

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Setup Project Board",
      "type": "shell",
      "command": "python docs/setup_project_board.py --token ${env:GH_TOKEN} --repo ${env:GH_REPO} --org ${env:GH_ORG}",
      "group": "build",
      "presentation": { "reveal": "always", "panel": "new" }
    },
    {
      "label": "Create Issues — Dry Run",
      "type": "shell",
      "command": "python docs/create_migration_issues.py --token ${env:GH_TOKEN} --repo ${env:GH_REPO} --dry-run",
      "group": "build",
      "presentation": { "reveal": "always", "panel": "new" }
    },
    {
      "label": "Create Issues — PARMLIB Only",
      "type": "shell",
      "command": "python docs/create_migration_issues.py --token ${env:GH_TOKEN} --repo ${env:GH_REPO} --sheets \"PARMLIB Changes\"",
      "group": "build"
    },
    {
      "label": "Create All Issues",
      "type": "shell",
      "command": "python docs/create_migration_issues.py --token ${env:GH_TOKEN} --repo ${env:GH_REPO} --project-id ${env:GH_PROJECT_ID}",
      "group": "build",
      "presentation": { "reveal": "always", "panel": "new" }
    }
  ]
}
```

---

## Expected Output

Running against the z/OS 3.2 Migration workbook creates:

| Sheet | Issues | Sprint Assignment |
|-------|--------|-------------------|
| PARMLIB Changes | ~21 | Sprint 1–3 (by risk level) |
| Deprecated & Removed | ~16 | Sprint 1–2 (IPL blockers first) |
| Function Matrix | ~41 | Sprint 2–5 (by focus area) |
| **Total** | **~78** | **Across 6 sprints** |

Each issue includes:
- Full detail table (component, release, priority, risk, impacts)
- Required action in a code block
- Acceptance criteria checklist
- Sprint label + milestone assignment
- Component, priority, and focus area labels

---

## Files Generated

| File | Description |
|------|-------------|
| `project_board_config.json` | Project ID, field IDs, view IDs — needed for issue creation |
| `migration_issues_created.json` | Summary of all created issues with URLs |
| `docs/sprint-plan.md` | Full sprint plan with key tasks per sprint |
| `docs/migration-log.md` | Migration log template for sign-offs |
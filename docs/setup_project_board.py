#!/usr/bin/env python3
"""
z/OS 3.2 Migration — GitHub Projects v2 Board Setup
=====================================================
Creates and configures a complete GitHub Projects v2 board with:
  - Sprint iteration fields (6 sprints × 2 weeks)
  - Status columns (Backlog → In Sprint → In Progress → In Review → Done)
  - Priority, Component, Risk Level, and Sheet custom fields
  - Views: Sprint Board, Backlog, IPL Blockers, By Component
  - Automated field configuration via GraphQL API

Usage:
  # Interactive setup (prompts for org/user)
  python setup_project_board.py --token $GH_TOKEN --repo owner/repo

  # Org-level project
  python setup_project_board.py --token $GH_TOKEN --repo owner/repo --org myorg

  # User-level project
  python setup_project_board.py --token $GH_TOKEN --repo owner/repo --user myusername

  # Dry run
  python setup_project_board.py --token $GH_TOKEN --repo owner/repo --dry-run

Requirements:
  pip install requests python-dotenv
"""

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Missing dependency. Run: pip install requests")
    sys.exit(1)

GITHUB_GRAPHQL = "https://api.github.com/graphql"
GITHUB_API     = "https://api.github.com"

# ── Sprint definitions ────────────────────────────────────────────────────────

SPRINTS = [
    {
        "number":      1,
        "name":        "Sprint 1 — IPL Blockers & Foundation",
        "theme":       "Remove all IPL-blocking deprecated params; establish migration baseline",
        "duration":    14,
        "key_tasks": [
            "Remove HFS params from BPXPRMxx (BUFFERMONITOR, FIXED, RNODEWAIT, SYNCDEFAULT, WAITABEND, VIRTUAL)",
            "Replace VRREGN= and VREALSZ= with REAL=nnnM in IEASYSxx",
            "Verify JES3 subsystem entries removed from IEFSSNxx",
            "Complete HFS → ZFS migration for all remaining mounts",
            "Update LNKLSTxx / PROGxx with new z/OS 3.2 library HLQs",
            "Reinstall all user-written SVCs (IEASVCxx)",
            "Reinstall Program Properties Table entries (SCHEDxx)",
            "First non-production LPAR IPL test",
        ],
    },
    {
        "number":      2,
        "name":        "Sprint 2 — Security Architecture",
        "theme":       "ICSF PQC enablement; System SSL audit; RACF enhancements",
        "duration":    14,
        "key_tasks": [
            "Enable PKCS11SUPPORT in ICSF options dataset (CSFPRMxx)",
            "Set FIPSMODE(COMPAT,FAIL(NONE)) for PQC transition",
            "Activate ML-KEM-768, ML-DSA-65, SLH-DSA algorithms",
            "Audit all AT-TLS policies for System SSL default changes",
            "Test all TLS connections after SSL default updates",
            "Enable RACF User ID Containment (APAR OA67286)",
            "Add REUSASID=YES to RACF START command in COMMNDxx",
            "Add DSNRAUTH class to SETROPTS RACLIST",
            "Define RACF Secrets Management policy",
            "Conduct cryptographic inventory using IBM Crypto Discovery Tool",
        ],
    },
    {
        "number":      3,
        "name":        "Sprint 3 — PARMLIB Hardening",
        "theme":       "CPENABLE=SYSTEM testing; IARPRMxx; DIAGxx; SMFLIMxx; IRRPRMxx",
        "duration":    14,
        "key_tasks": [
            "Test CPENABLE=SYSTEM in isolated non-production LPAR",
            "Review all capacity management automation for CPENABLE conflicts",
            "Set RESTRICTPFTCADS in IARPRMxx",
            "Set ARR2V_REQAUTH in IARPRMxx",
            "Set ASCBV31 explicitly in DIAGxx; test in isolated LPAR",
            "Configure CHECKREGIONABOVE and CHECKREGIONBELOW in SMFLIMxx",
            "Set REXXPARSE in BPXPRMxx; test all REXX automation scripts",
            "Update CEEPRMxx; retest all Language Environment applications",
            "Update COMMNDxx with new START commands",
            "Review and update GRS resource name lists (GRSRNLxx)",
        ],
    },
    {
        "number":      4,
        "name":        "Sprint 4 — AI Workload Enablement",
        "theme":       "AI System Services 1.2; WLM Policy Advisor; zDNN; BUFSIZE tuning",
        "duration":    14,
        "key_tasks": [
            "Install AI System Services 1.2 (AISS 1.2)",
            "Install Machine Learning for z/OS 3.2 Core Edition (FMID HAQN320)",
            "Configure AI Framework via z/OSMF workflow",
            "Define WLM service classes for AI inference workloads",
            "Enable WLM Policy Advisor; collect 30 days SMF 99.2 data",
            "Train AI-powered WLM batch initiator model",
            "Increase BUFSIZE to 2047 MB in CTnBPXxx for AI workloads",
            "Configure CHECKREGIONABOVE limits for AI address spaces",
            "Enable AI-assisted outbound packet batching (PH67239)",
            "Validate zDNN library for Telum II AI accelerator",
        ],
    },
    {
        "number":      5,
        "name":        "Sprint 5 — Cloud & Observability",
        "theme":       "OpenTelemetry; OAM REST API; Docker networking; z/OSMF automation",
        "duration":    14,
        "key_tasks": [
            "Configure z/OS OpenTelemetry Emitter (OA66345)",
            "Update SMFPRMxx for new SMF record types 1157-1161",
            "Enable OAM REST API; configure START/STOP/DISPLAY/MODIFY",
            "Configure Docker container networking via Sysplex Distributor",
            "Enable IPv6 R1 Compliance in Communications Server",
            "Configure RMF OpenMetrics endpoint for Prometheus/Grafana",
            "Enable z/OSMF AUTOCONFIG for automated workflows",
            "Configure GTZPRMxx for Generic Tracker / OTel integration",
            "Update IZUPRMxx for new z/OSMF automation capabilities",
            "Test hybrid cloud connectivity and observability pipeline",
        ],
    },
    {
        "number":      6,
        "name":        "Sprint 6 — Validation & Cutover",
        "theme":       "Full IPL test; SMF record validation; RMF OpenMetrics; production cutover",
        "duration":    14,
        "key_tasks": [
            "Full production-equivalent IPL test in staging LPAR",
            "Validate all SMF record types (30, 70 ST3, 72, 74, 88, 119, 1154, 1157-1161)",
            "Run z/OS Upgrade Workflow final checklist in z/OSMF",
            "Performance baseline comparison: z/OS 3.1 vs 3.2 MSU",
            "Validate RMF OpenMetrics endpoint with Prometheus",
            "Security penetration test with new RACF/ICSF configuration",
            "Validate all ISV products at z/OS 3.2-compatible levels",
            "Final sign-off from system programmer, security, and operations",
            "Production cutover — IPL z/OS 3.2",
            "Post-cutover monitoring: 72-hour hypercare period",
        ],
    },
]

# ── GraphQL client ────────────────────────────────────────────────────────────

class GraphQLClient:
    def __init__(self, token: str, dry_run: bool = False):
        self.token   = token
        self.dry_run = dry_run
        self.headers = {
            "Authorization":        f"Bearer {token}",
            "Accept":               "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type":         "application/json",
        }

    def query(self, gql: str, variables: dict = None) -> dict:
        payload = {"query": gql}
        if variables:
            payload["variables"] = variables
        resp = requests.post(GITHUB_GRAPHQL, headers=self.headers,
                             json=payload, timeout=30)
        data = resp.json()
        if "errors" in data:
            for err in data["errors"]:
                print(f"  ⚠️  GraphQL error: {err.get('message','')}")
        return data

    def rest_post(self, path: str, payload: dict) -> dict:
        resp = requests.post(f"{GITHUB_API}{path}", headers=self.headers,
                             json=payload, timeout=30)
        return resp.json()

    def rest_get(self, path: str) -> dict | list:
        resp = requests.get(f"{GITHUB_API}{path}", headers=self.headers, timeout=30)
        return resp.json()


# ── Lookup helpers ────────────────────────────────────────────────────────────

def get_owner_node_id(client: GraphQLClient, owner: str, is_org: bool) -> str | None:
    if is_org:
        q = """query($login: String!) { organization(login: $login) { id } }"""
        r = client.query(q, {"login": owner})
        try:
            return r["data"]["organization"]["id"]
        except (KeyError, TypeError):
            return None
    else:
        q = """query($login: String!) { user(login: $login) { id } }"""
        r = client.query(q, {"login": owner})
        try:
            return r["data"]["user"]["id"]
        except (KeyError, TypeError):
            return None


def get_repo_node_id(client: GraphQLClient, owner: str, repo: str) -> str | None:
    q = """query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) { id }
    }"""
    r = client.query(q, {"owner": owner, "name": repo})
    try:
        return r["data"]["repository"]["id"]
    except (KeyError, TypeError):
        return None


# ── Project creation ──────────────────────────────────────────────────────────

def create_project(client: GraphQLClient, owner_id: str,
                   title: str, dry_run: bool) -> str | None:
    if dry_run:
        print(f"  [DRY RUN] Would create project: {title}")
        return "DRY_RUN_PROJECT_ID"

    mutation = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id url }
      }
    }"""
    r = client.query(mutation, {"ownerId": owner_id, "title": title})
    try:
        proj = r["data"]["createProjectV2"]["projectV2"]
        print(f"  ✅ Project created: {proj['url']}")
        return proj["id"]
    except (KeyError, TypeError):
        print(f"  ❌ Failed to create project: {r}")
        return None


def link_repo_to_project(client: GraphQLClient, project_id: str,
                          repo_id: str, dry_run: bool):
    if dry_run:
        print("  [DRY RUN] Would link repository to project")
        return
    mutation = """
    mutation($projectId: ID!, $repositoryId: ID!) {
      linkProjectV2ToRepository(input: {projectId: $projectId, repositoryId: $repositoryId}) {
        repository { name }
      }
    }"""
    r = client.query(mutation, {"projectId": project_id, "repositoryId": repo_id})
    try:
        name = r["data"]["linkProjectV2ToRepository"]["repository"]["name"]
        print(f"  ✅ Linked repository: {name}")
    except (KeyError, TypeError):
        print(f"  ⚠️  Could not link repository (may require org-level project)")


# ── Field creation ────────────────────────────────────────────────────────────

def create_single_select_field(client: GraphQLClient, project_id: str,
                                name: str, options: list[dict],
                                dry_run: bool) -> str | None:
    if dry_run:
        print(f"  [DRY RUN] Would create single-select field: {name}")
        return f"DRY_RUN_FIELD_{name}"

    mutation = """
    mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
      createProjectV2Field(input: {
        projectId: $projectId,
        dataType: SINGLE_SELECT,
        name: $name,
        singleSelectOptions: $options
      }) {
        projectV2Field {
          ... on ProjectV2SingleSelectField { id name }
        }
      }
    }"""
    r = client.query(mutation, {
        "projectId": project_id,
        "name":      name,
        "options":   options,
    })
    try:
        fid = r["data"]["createProjectV2Field"]["projectV2Field"]["id"]
        print(f"  ✅ Created field: {name} (id: {fid})")
        return fid
    except (KeyError, TypeError):
        print(f"  ⚠️  Field '{name}' may already exist or failed: {r.get('errors','')}")
        return None


def create_text_field(client: GraphQLClient, project_id: str,
                      name: str, dry_run: bool) -> str | None:
    if dry_run:
        print(f"  [DRY RUN] Would create text field: {name}")
        return f"DRY_RUN_FIELD_{name}"

    mutation = """
    mutation($projectId: ID!, $name: String!) {
      createProjectV2Field(input: {
        projectId: $projectId,
        dataType: TEXT,
        name: $name
      }) {
        projectV2Field { id name }
      }
    }"""
    r = client.query(mutation, {"projectId": project_id, "name": name})
    try:
        fid = r["data"]["createProjectV2Field"]["projectV2Field"]["id"]
        print(f"  ✅ Created text field: {name} (id: {fid})")
        return fid
    except (KeyError, TypeError):
        print(f"  ⚠️  Text field '{name}' may already exist or failed")
        return None


def create_iteration_field(client: GraphQLClient, project_id: str,
                            start_date: str, dry_run: bool) -> str | None:
    """Create Sprint iteration field with 6 × 2-week sprints."""
    if dry_run:
        print("  [DRY RUN] Would create Sprint iteration field")
        return "DRY_RUN_ITERATION_FIELD"

    iterations = []
    d = date.fromisoformat(start_date)
    for sprint in SPRINTS:
        iterations.append({
            "title":     sprint["name"],
            "startDate": d.isoformat(),
            "duration":  sprint["duration"],
        })
        d += timedelta(days=sprint["duration"])

    mutation = """
    mutation($projectId: ID!, $name: String!, $startDate: Date!, $iterations: [ProjectV2Iteration!]!) {
      createProjectV2Field(input: {
        projectId: $projectId,
        dataType: ITERATION,
        name: $name,
        iterationConfiguration: {
          startDate: $startDate,
          duration: 14,
          iterations: $iterations
        }
      }) {
        projectV2Field {
          ... on ProjectV2IterationField { id name }
        }
      }
    }"""
    r = client.query(mutation, {
        "projectId":  project_id,
        "name":       "Sprint",
        "startDate":  start_date,
        "iterations": iterations,
    })
    try:
        fid = r["data"]["createProjectV2Field"]["projectV2Field"]["id"]
        print(f"  ✅ Created Sprint iteration field (id: {fid})")
        return fid
    except (KeyError, TypeError):
        print(f"  ⚠️  Sprint field may already exist or failed: {r.get('errors','')}")
        return None


# ── View creation ─────────────────────────────────────────────────────────────

def create_board_view(client: GraphQLClient, project_id: str,
                      name: str, layout: str, dry_run: bool) -> str | None:
    if dry_run:
        print(f"  [DRY RUN] Would create view: {name} ({layout})")
        return f"DRY_RUN_VIEW_{name}"

    mutation = """
    mutation($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
      createProjectV2View(input: {
        projectId: $projectId,
        name: $name,
        layout: $layout
      }) {
        projectV2View { id name }
      }
    }"""
    r = client.query(mutation, {
        "projectId": project_id,
        "name":      name,
        "layout":    layout,
    })
    try:
        vid = r["data"]["createProjectV2View"]["projectV2View"]["id"]
        print(f"  ✅ Created view: {name} ({layout}) id: {vid}")
        return vid
    except (KeyError, TypeError):
        print(f"  ⚠️  View '{name}' failed: {r.get('errors','')}")
        return None


# ── Sprint wiki / README ──────────────────────────────────────────────────────

def generate_sprint_readme() -> str:
    lines = [
        "# z/OS 3.2 Migration — Sprint Plan\n",
        "## Overview\n",
        "This project tracks the complete z/OS 3.2 migration across 6 sprints (12 weeks).\n",
        "Each issue represents a single migration action with acceptance criteria.\n",
        "Issues are auto-generated from the z/OS 3.2 Migration Risk Comparison workbook.\n",
        "\n## Sprint Structure\n",
        "| Sprint | Theme | Duration | Key Focus |\n",
        "|--------|-------|----------|-----------|\n",
    ]
    for s in SPRINTS:
        lines.append(f"| {s['number']} | {s['name'].split('—')[1].strip()} | 2 weeks | {s['theme'][:60]}... |\n")

    lines.append("\n## Labels\n")
    lines.append("| Label | Meaning |\n|-------|--------|\n")
    label_docs = [
        ("ipl-blocker",  "Must be resolved before any IPL attempt"),
        ("critical",     "Critical priority — Sprint 1 or 2"),
        ("important",    "Important — complete before production cutover"),
        ("beneficial",   "Enhancement — complete when capacity allows"),
        ("parmlib",      "Requires SYS1.PARMLIB member change"),
        ("security",     "Security / RACF / ICSF change"),
        ("qsc",          "Quantum-safe cryptography"),
        ("ai-workload",  "AI workload enablement"),
        ("hybrid-cloud", "Hybrid cloud integration"),
        ("deprecated",   "Deprecated or removed function to address"),
        ("monitoring",   "Monitoring / RMF / SMF / CDP"),
        ("needs-review", "Requires system programmer review"),
        ("migration-log","Must be documented in migration log"),
    ]
    for name, desc in label_docs:
        lines.append(f"| `{name}` | {desc} |\n")

    lines.append("\n## Sprint Details\n")
    for s in SPRINTS:
        lines.append(f"\n### {s['name']}\n")
        lines.append(f"**Theme:** {s['theme']}\n\n")
        lines.append("**Key Tasks:**\n")
        for task in s["key_tasks"]:
            lines.append(f"- [ ] {task}\n")

    lines.append("\n## Board Views\n")
    views = [
        ("Sprint Board",    "BOARD",  "Kanban board grouped by Status — primary working view"),
        ("Sprint Backlog",  "TABLE",  "Table view filtered to current sprint — planning view"),
        ("IPL Blockers",    "TABLE",  "Filtered to ipl-blocker label — pre-IPL checklist"),
        ("By Component",    "TABLE",  "Grouped by Component field — system programmer view"),
        ("Security Track",  "TABLE",  "Filtered to security/qsc labels — security team view"),
        ("All Issues",      "TABLE",  "Full table view — management reporting"),
    ]
    lines.append("| View | Layout | Purpose |\n|------|--------|---------|\n")
    for name, layout, purpose in views:
        lines.append(f"| {name} | {layout} | {purpose} |\n")

    lines.append("\n## Automation\n")
    lines.append("Issues are created automatically from the Excel workbook using:\n")
    lines.append("```bash\npython scripts/github-migration/create_migration_issues.py \\\n")
    lines.append("  --token $GH_TOKEN --repo owner/repo\n```\n")
    lines.append("\nProject board is configured using:\n")
    lines.append("```bash\npython scripts/github-migration/setup_project_board.py \\\n")
    lines.append("  --token $GH_TOKEN --repo owner/repo --org myorg\n```\n")

    return "".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="z/OS 3.2 Migration — GitHub Projects v2 Board Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Org-level project (recommended for teams)
  python setup_project_board.py --token $GH_TOKEN --repo myorg/zos-migration --org myorg

  # User-level project
  python setup_project_board.py --token $GH_TOKEN --repo myuser/zos-migration --user myuser

  # Dry run
  python setup_project_board.py --token $GH_TOKEN --repo myorg/zos-migration --org myorg --dry-run

  # Custom sprint start date
  python setup_project_board.py --token $GH_TOKEN --repo myorg/zos-migration \\
    --org myorg --start-date 2026-10-01
        """
    )
    parser.add_argument("--token",      help="GitHub PAT (or set GH_TOKEN env var)")
    parser.add_argument("--repo",       help="GitHub repo: owner/repo-name")
    parser.add_argument("--org",        help="GitHub org login (for org-level project)")
    parser.add_argument("--user",       help="GitHub user login (for user-level project)")
    parser.add_argument("--project-title", default="z/OS 3.2 Migration Sprints",
                        help="Project board title")
    parser.add_argument("--start-date", default=None,
                        help="Sprint 1 start date YYYY-MM-DD (default: next Monday)")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Preview without making API calls")
    parser.add_argument("--env-file",   default=".env",
                        help="Path to .env file")
    parser.add_argument("--output",     default="project_board_config.json",
                        help="Output JSON with project/field IDs")
    args = parser.parse_args()

    # Load .env
    env_path = Path(args.env_file)
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    token = args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo  = args.repo  or os.environ.get("GH_REPO")  or os.environ.get("GITHUB_REPO")

    if not token:
        print("❌ GitHub token required. Use --token or set GH_TOKEN")
        sys.exit(1)
    if not repo:
        print("❌ GitHub repo required. Use --repo owner/repo")
        sys.exit(1)

    owner_login = args.org or args.user or os.environ.get("GH_ORG") or os.environ.get("GH_USER")
    is_org      = bool(args.org or (not args.user and os.environ.get("GH_ORG")))

    if not owner_login:
        owner_login = repo.split("/")[0]
        is_org      = False
        print(f"ℹ️  No --org or --user specified; using repo owner '{owner_login}' as user")

    # Sprint start date — default to next Monday
    if args.start_date:
        start_date = args.start_date
    else:
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7 or 7
        start_date = (today + timedelta(days=days_until_monday)).isoformat()

    repo_name = repo.split("/")[1] if "/" in repo else repo

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║   z/OS 3.2 Migration — GitHub Project Board Setup           ║
╚══════════════════════════════════════════════════════════════╝
  Repo:         {repo}
  Owner:        {owner_login} ({'org' if is_org else 'user'})
  Project:      {args.project_title}
  Sprint Start: {start_date}
  Dry Run:      {args.dry_run}
""")

    client = GraphQLClient(token, args.dry_run)

    # ── Step 1: Resolve owner node ID ─────────────────────────────────────────
    print("🔍 Resolving owner node ID...")
    if args.dry_run:
        owner_id = "DRY_RUN_OWNER_ID"
        repo_id  = "DRY_RUN_REPO_ID"
        print(f"  [DRY RUN] owner_id={owner_id}")
    else:
        owner_id = get_owner_node_id(client, owner_login, is_org)
        if not owner_id:
            print(f"❌ Could not resolve owner '{owner_login}'. Check --org/--user and token permissions.")
            sys.exit(1)
        print(f"  ✅ owner_id: {owner_id}")

        repo_id = get_repo_node_id(client, repo.split("/")[0], repo_name)
        if not repo_id:
            print(f"❌ Could not resolve repo '{repo}'")
            sys.exit(1)
        print(f"  ✅ repo_id:  {repo_id}")

    # ── Step 2: Create project ─────────────────────────────────────────────────
    print(f"\n📋 Creating project: {args.project_title}")
    project_id = create_project(client, owner_id, args.project_title, args.dry_run)
    if not project_id:
        print("❌ Failed to create project")
        sys.exit(1)

    if not args.dry_run:
        time.sleep(1)

    # ── Step 3: Link repository ────────────────────────────────────────────────
    print("\n🔗 Linking repository to project...")
    link_repo_to_project(client, project_id, repo_id, args.dry_run)

    if not args.dry_run:
        time.sleep(1)

    # ── Step 4: Create custom fields ──────────────────────────────────────────
    print("\n🏷️  Creating custom fields...")
    field_ids = {}

    # Priority field
    field_ids["Priority"] = create_single_select_field(
        client, project_id, "Priority",
        [
            {"name": "🔴 Critical",    "color": "RED",    "description": "IPL failure risk or major security"},
            {"name": "🟠 Important",   "color": "ORANGE", "description": "Functional impact before production"},
            {"name": "🟢 Beneficial",  "color": "GREEN",  "description": "Enhancement or new capability"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # Component field
    field_ids["Component"] = create_single_select_field(
        client, project_id, "Component",
        [
            {"name": "BCP / MVS",        "color": "BLUE",   "description": "Base Control Program"},
            {"name": "RACF / Security",   "color": "RED",    "description": "Security Server"},
            {"name": "ICSF / Crypto",     "color": "PURPLE", "description": "Cryptographic Services"},
            {"name": "OMVS / UNIX",       "color": "GREEN",  "description": "z/OS UNIX System Services"},
            {"name": "DFSMS / Storage",   "color": "YELLOW", "description": "Storage Management"},
            {"name": "Comm Server",       "color": "BLUE",   "description": "Communications Server"},
            {"name": "JES2",              "color": "GRAY",   "description": "Job Entry Subsystem"},
            {"name": "RMF / CDP / SMF",   "color": "BLUE",   "description": "Monitoring & Performance"},
            {"name": "z/OSMF",            "color": "GREEN",  "description": "Management Facility"},
            {"name": "SMP/E",             "color": "GRAY",   "description": "System Modification Program"},
            {"name": "Lang Env / Runtime","color": "YELLOW", "description": "Language Environment"},
            {"name": "Multiple",          "color": "GRAY",   "description": "Affects multiple components"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # Risk Level field
    field_ids["Risk Level"] = create_single_select_field(
        client, project_id, "Risk Level",
        [
            {"name": "💥 IPL Failure",  "color": "RED",    "description": "Causes IPL failure if not addressed"},
            {"name": "🔴 High",         "color": "RED",    "description": "High risk — significant functional impact"},
            {"name": "🟡 Medium",       "color": "YELLOW", "description": "Medium risk — requires testing"},
            {"name": "🟢 Low",          "color": "GREEN",  "description": "Low risk — beneficial change"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # Sheet / Source field
    field_ids["Source Sheet"] = create_single_select_field(
        client, project_id, "Source Sheet",
        [
            {"name": "PARMLIB Changes",    "color": "BLUE",   "description": "From PARMLIB Changes sheet"},
            {"name": "Deprecated & Removed","color": "RED",   "description": "From Deprecated & Removed sheet"},
            {"name": "Function Matrix",    "color": "GREEN",  "description": "From Function Matrix sheet"},
            {"name": "Security",           "color": "YELLOW", "description": "From Security Requirements sheet"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # IPL Blocker field
    field_ids["IPL Blocker"] = create_single_select_field(
        client, project_id, "IPL Blocker",
        [
            {"name": "YES — Must fix before IPL", "color": "RED",   "description": "Hard IPL blocker"},
            {"name": "NO",                         "color": "GREEN", "description": "Not an IPL blocker"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # Effort Estimate field
    field_ids["Effort"] = create_single_select_field(
        client, project_id, "Effort",
        [
            {"name": "1 day",      "color": "GREEN",  "description": "Less than 1 day"},
            {"name": "2-3 days",   "color": "GREEN",  "description": "2 to 3 days"},
            {"name": "1 week",     "color": "YELLOW", "description": "About 1 week"},
            {"name": "2-4 weeks",  "color": "YELLOW", "description": "2 to 4 weeks"},
            {"name": "1-3 months", "color": "ORANGE", "description": "1 to 3 months"},
            {"name": "3-6 months", "color": "RED",    "description": "3 to 6 months"},
            {"name": "6+ months",  "color": "RED",    "description": "More than 6 months"},
        ],
        args.dry_run,
    )
    time.sleep(0.5)

    # Notes text field
    field_ids["Notes"] = create_text_field(client, project_id, "Notes", args.dry_run)
    time.sleep(0.5)

    # ── Step 5: Create Sprint iteration field ──────────────────────────────────
    print("\n🏃 Creating Sprint iteration field...")
    field_ids["Sprint"] = create_iteration_field(client, project_id, start_date, args.dry_run)
    time.sleep(1)

    # ── Step 6: Create views ───────────────────────────────────────────────────
    print("\n👁️  Creating board views...")
    view_ids = {}

    views_to_create = [
        ("Sprint Board",     "BOARD_LAYOUT"),
        ("Sprint Backlog",   "TABLE_LAYOUT"),
        ("IPL Blockers",     "TABLE_LAYOUT"),
        ("By Component",     "TABLE_LAYOUT"),
        ("Security Track",   "TABLE_LAYOUT"),
        ("All Issues",       "TABLE_LAYOUT"),
    ]
    for view_name, layout in views_to_create:
        vid = create_board_view(client, project_id, view_name, layout, args.dry_run)
        view_ids[view_name] = vid
        time.sleep(0.5)

    # ── Step 7: Generate README ────────────────────────────────────────────────
    print("\n📝 Generating sprint README...")
    readme_content = generate_sprint_readme()
    readme_path = Path("docs/sprint-plan.md")
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    with open(readme_path, "w") as f:
        f.write(readme_content)
    print(f"  ✅ Sprint plan written to: {readme_path}")

    # ── Step 8: Generate migration log template ────────────────────────────────
    migration_log = """# z/OS 3.2 Migration Log

## Migration Details
- **Source Release:** z/OS 3.1 (or 2.5)
- **Target Release:** z/OS 3.2
- **Migration Start:**
- **Target IPL Date:**
- **System Programmer Lead:**
- **Security Lead:**

## Pre-IPL Checklist
- [ ] All Sprint 1 issues closed
- [ ] All ipl-blocker issues resolved
- [ ] Non-production LPAR IPL successful
- [ ] Security sign-off obtained
- [ ] Operations team briefed

## IPL Log
| Date | LPAR | Result | Notes |
|------|------|--------|-------|
|      |      |        |       |

## Issues Encountered
| Date | Issue | Resolution | Owner |
|------|-------|------------|-------|
|      |       |            |       |

## Sign-offs
| Role | Name | Date | Signature |
|------|------|------|-----------|
| System Programmer Lead | | | |
| Security Lead | | | |
| Operations Manager | | | |
| Change Manager | | | |
"""
    log_path = Path("docs/migration-log.md")
    try:
        with open(log_path, "x") as f:
            f.write(migration_log)
    except FileExistsError:
        print(f"  ℹ️  Existing migration log preserved: {log_path}")
    else:
        print(f"  ✅ Migration log template written to: {log_path}")

    # ── Step 9: Save config ────────────────────────────────────────────────────
    config = {
        "project_id":    project_id,
        "project_title": args.project_title,
        "repo":          repo,
        "owner":         owner_login,
        "is_org":        is_org,
        "sprint_start":  start_date,
        "dry_run":       args.dry_run,
        "field_ids":     field_ids,
        "view_ids":      view_ids,
        "sprints":       [{"number": s["number"], "name": s["name"],
                           "theme": s["theme"]} for s in SPRINTS],
    }
    with open(args.output, "w") as f:
        json.dump(config, f, indent=2)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    SETUP COMPLETE                           ║
╚══════════════════════════════════════════════════════════════╝
  Project ID:   {project_id}
  Sprint Start: {start_date}
  Fields:       {len([v for v in field_ids.values() if v])} created
  Views:        {len([v for v in view_ids.values() if v])} created
  Config saved: {args.output}

  📄 Docs generated:
     docs/sprint-plan.md
     docs/migration-log.md

  🚀 Next steps:
  1. Run create_migration_issues.py to populate issues:
     python scripts/github-migration/create_migration_issues.py \\
       --token $GH_TOKEN --repo {repo} \\
       --project-id {project_id}

  2. Open the project board in GitHub:
     https://github.com/orgs/{owner_login}/projects  (org)
     https://github.com/users/{owner_login}/projects (user)

  3. In VS Code: install GitHub Pull Requests extension
     and GitHub Projects extension for inline board access.
""")


if __name__ == "__main__":
    main()
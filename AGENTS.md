# AGENTS.md — ha-ops Parent Governance Contract (HA-0001)
# D082226T2000 | HA-0001 | initial governance contract | JC | ha-ops repo
# D082326T0100 | HA-0007 | SCM-canonical closure rule | JC | ha-ops repo

## 1. Purpose
Single contract governing all agent activity in this repository. Streams
deliver changes; the orchestrator sequences them; the human operator
promotes them. No agent converges to production directly.

## 2. Roles
| Role  | Charter                                              | Owned paths            |
|-------|------------------------------------------------------|------------------------|
| ORCH  | Registry, sequencing, gates, this contract           | AGENTS.md, docs/       |
| CONFIG| Control-plane platform configuration                 | config/                |
| DASH  | Operator and analytics dashboards                    | dashboards/            |
| SVC   | External services, storage, plugins, backup jobs     | analytics/, ansible/   |

## 3. Serialization (GRS rule)
Cross-session, cross-model coordination protocol: LANES.md (HA-0005).
LANES.md is operator-write-only and binding on all agents and models.
An agent writes ONLY within its owned paths. Cross-boundary needs are
raised to ORCH, which opens a change-ID under the owning stream.
Exclusive ENQ per path; no shared writes, ever.

## 4. Change control
- Every change carries an ID: HA-#### (registry in §8), assigned by ORCH.
- Every touched file carries a compact change header:
  `# <Dtimestamp> | <change-ID> | <reason> | <initials> | <target>`
- Backups precede overwrites (`cp` with D-timestamp suffix).
- Logs are never deleted; archive/compress/relocate only.

## 5. Pipeline
Draft -> Validate -> Review -> Converge -> Verify
- Validate: ./validate.sh (lint + platform config check). Blocking.
- Review:  human operator. Blocking. Agents propose; operator promotes.
- Converge: ansible only, tagged by stream, from the designated admin host.
- Verify:  post-converge smoke checks logged to docs/converge-log.md.

## 6. Prohibitions
- No agent invokes deployment tooling without an approved change-ID.
- No agent edits production state directly (UI, SSH, API) outside a
  Converge executed through the pipeline.
- No agent modifies this contract; amendments are operator-only.

## 7. Guard clause
This contract names roles, gates, paths, and identifiers only. Product
and technology names are prohibited in this file; they belong in
stream-level documentation, which may change without amending this
contract.

## 8. Change registry
A registry row moves to CLOSED only on SCM-visible evidence (merged
commit referencing the ID). Telemetry and summaries never close a row.
| ID      | Stream | Description                            | Status |
|---------|--------|----------------------------------------|--------|
| HA-0001 | ORCH   | Governance contract, repo scaffold     | OPEN   |
| HA-0002 | CONFIG | Recorder scoping + package baseline    | OPEN   |
| HA-0003 | SVC    | Analytics storage + collection wiring  | OPEN   |
| HA-0004 | DASH   | Control-plane dashboard baseline       | OPEN   |
| HA-0005 | ORCH   | Cross-model lane notice (LANES.md)     | OPEN   |
| HA-0006 | ORCH   | Worktree convention, prefixes, orphans | OPEN   |
| HA-0007 | ORCH   | SCM turnover authority, status vocab   | OPEN   |
| HA-0008 | ORCH   | Tool-channel governance (MCP scope)    | OPEN   |

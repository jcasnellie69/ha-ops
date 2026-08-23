# D082326T0200 | HA-0008 | interactive tool channel scope of record | JC | haos-vm
# Channel: HA MCP server (in-process custom component via HACS)
# Status: Specified

## Posture
Server-side enforcement: Read Only Mode as baseline, per-tool
enable/disable for the write allowlist, security policies (approval)
on destructive categories. Local access only for now (direct port /
local webhook); remote access decision deferred to network cutover.

## ALLOWED writes (config-flow plane — repo cannot own this state)
- entity registry (rename, enable/disable), device registry
- areas, floors, labels, categories
- helpers (config-flow created)
- integration setup/options, HACS management
- backup trigger

## OPEN (read/diagnostic plane — all agents)
- search/overview/state, history, statistics, logs
- automation traces, config GET tools, dashboard screenshot
- camera snapshot, system health, template eval (server-side eval:
  treat as read)

## PROHIBITED (YAML plane — repo-owned, Converge only)
- config_set_* for automations, scenes, scripts, dashboards, groups
- file tools (read allowed if needed; write/delete prohibited)
- ha_config_set_yaml (beta) — never enable
- restart/reload via channel (reloads ride the Converge pipeline)

## Notes
- Bundled agent skills (skill:// resources / ha_get_skill_guide) are
  reference input for CONFIG and DASH agents.
- Any scope change to this document is an operator-approved change-ID.

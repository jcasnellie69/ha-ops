# ha-ops
# D082226T2000 | HA-0001 | repo scaffold | JC | ha-ops repo

Config-as-code for the Home Assistant estate. Governance: AGENTS.md.

## Streams
- config/      CONFIG agent — HA control-plane YAML (packages model)
- dashboards/  DASH agent — Lovelace YAML mode + Grafana JSON exports
- analytics/   SVC agent — recorder/LTSS/TSDB design notes
- ansible/     SVC agent — the ONLY door to production (converge layer)
- scripts/     bootstrap & exception tooling (config-flow plane only)

## Pipeline
Draft -> Validate (./validate.sh) -> Review (human) -> Converge (ansible) -> Verify

## Quick start
1. Fill ansible/group_vars/ha.yml (host, token via vault, entity maps)
2. ./validate.sh
3. ansible-playbook ansible/site.yml --tags config

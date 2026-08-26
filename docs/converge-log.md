# D082226T2000 | HA-0001 | converge log opened | JC | ha-ops repo

# D082326T2102 | HA-0001 | scaffold landed to SCM; LANES.md installed to infra repo | JC | ha-ops + infra repos
D082326T2102 HA-0001..HA-0008 — ha-ops scaffold v4 extracted to ~/ha-ops, validated (./validate.sh exit 0), git init on main, committed 02257b6, pushed to private jcasnellie69/ha-ops; LANES.md (HA-0005) installed verbatim at infra repo root, commit 6950615 pushed to jcasnellie69/homelab-config main. All eight registry rows HA-0001..HA-0008 remain OPEN pending their streams (AGENTS.md §8: rows close only on SCM-visible evidence referencing the ID). Status of every capability: Specified, not Operational (LANES §5d). No converge has been executed from either repo.

# D082626T0000 | HA-0009 | p.p. claude-sonnet-5 for JC | ha-ops + infra repos
D082626T0000 HA-0009 — Operator asked for PR review to stop bottlenecking on
the operator personally; built PR risk-tiering + CI in both repos, this being
the ha-ops half. Status: Specified, not Operational (no converge executed;
branch protection not yet applied — see below).

Landed on `chore/pr-risk-tiering-and-ci`, commit 2d889db, pushed, PR #1 open
(not merged):
- `.github/workflows/validate.yml` — wires the existing `./validate.sh` into
  GitHub Actions as a real status check. It was named in AGENTS.md §5 as the
  blocking Validate stage but never actually ran anywhere before this.
- `.github/CODEOWNERS` + `.github/workflows/pr-risk-tier.yml` — two tiers,
  not the infra repo's three. AGENTS.md §5 already mandates "Review: human
  operator. Blocking." for the whole Draft->Validate->Review->Converge
  pipeline, so this does NOT introduce a fast-track auto-merge exception for
  config/dashboards/analytics/ansible/scripts without an operator-approved
  amendment to that contract. Tier A (auto-merge) is plain documentation
  only, explicitly excluding AGENTS.md/LANES.md themselves. Everything else
  defaults to Tier C, hard-blocked from merging without operator review —
  once branch protection is actually applied (see below).

Repo-level `allow_auto_merge` enabled directly (not version-controlled).

Flagged for operator disposition (no agent action taken):
- Branch protection (required `validate` status check + "Require review
  from Code Owners") has NOT been applied to `main`. Without it, CODEOWNERS
  has no enforcement teeth — an agent or anyone could still merge a Tier C
  PR by hand. This is a hard GitHub-side setting, not a file, and the same
  class of action was blocked by the session's own auto-mode classifier as
  high-blast-radius when attempted in the infra repo. Needs explicit
  operator action or explicit operator instruction to the agent.
- The AGENTS.md §8 Change registry table does not yet have an HA-0009 row.
  AGENTS.md is operator-write-only per its own §6 ("No agent modifies this
  contract; amendments are operator-only") — not added here for that
  reason. This converge-log entry is the SCM-visible record until that row
  exists.
- Companion PR in the infra repo (jcasnellie69/homelab-config): same
  pattern, three tiers (that repo has no equivalent blocking-review
  contract, so a Tier B fast-track was defined there), PR chore/pr-risk-tiering
  branch, also awaiting branch protection.

Flagged for operator disposition (no agent action taken):
- §6a ORPHANS: infra checkout /mnt/repos/homelab-config sits on feat/opnsense-staged-deployment (NOT main) with 18 dirty/untracked entries — OPNsense gate2 playbooks, docker-vm-health-check, 7 session logs, artifacts/decommissioned-checkouts/. Verified untouched (18 before, 18 after). Expected NET-RENUM-0001 WIP was NOT found: no such change-ID in any ref, working tree, or share.
- §3/§4 MISSING: infra repo has no converge log and no services-register.md, both presumed by LANES entry protocol. Recovery search per §6b (all refs, .recycle, fileserver share) found no copy. Not created — INFRA-lane artifacts requiring operator direction. This entry is therefore recorded in the ha-ops log per LANES §2 cross-lane escalation, not in the infra log the operator specified.
- §6 CONTRACT NOTE: NFS remediation on host alpha (192.168.4.10) was performed by direct SSH outside a converge run — operator-approved in session, and operator instruction outranks documentation per §6, but recorded here as required. Fileserver 192.168.4.60 exports /srv/artifacts and /srv/homelab-config; alpha had never mounted either, so bind-mounts mp0/mp1 into CT 409 were serving empty local dirs. Mounts are runtime-only, absent from /etc/fstab and /etc/pve/storage.cfg — they will NOT survive an alpha reboot. Local pre-mount artifacts backed up to alpha:/root/fileserver-local-artifacts-D082326T1652.bak.

# D082426T0000 | CHG-NFS-PERSIST-001 | fileserver NFS mounts made persistent on alpha | JC | infra repo -> alpha
D082426T0000 CHG-NFS-PERSIST-001 — Converged deploy/ansible/playbooks/nfs-fileserver-mounts.yml to alpha via the INFRA pipeline (ansible-lint production profile 0 failures; --check preview; converge ok=6 changed=3; idempotence re-run ok=5 changed=0). Playbook committed BEFORE execution per node standing orders: infra commit c0aad7f on branch wip/CHG-NFS-PERSIST-001, pushed. Closes item 3.1 of part1-summary.md.

Applied to alpha (192.168.4.10):
- /etc/fstab: 192.168.4.60:/srv/artifacts -> /mnt/fileserver/artifacts and 192.168.4.60:/srv/homelab-config -> /mnt/fileserver/homelab-config, both nfs4 with _netdev,nofail,x-systemd.mount-timeout=30. Validated with mount -a --fake.
- /etc/systemd/system/pve-guests.service.d/10-fileserver-mounts.conf: orders guest start After= both .mount units and remote-fs.target. Verified registered via systemctl show.

Why the drop-in was necessary: pve-guests.service ships with NO ordering against remote-fs.target — its stock After= list contains only pve services, basic.target and sysinit.target. An fstab entry alone would race container start, so guests bind-mounting /mnt/fileserver/* could still come up bound to empty directories. That race is the intermittent form of the original fault; fstab alone would have looked correct and failed unpredictably.

Residual risk (accepted, documented): nofail means that if fileserver 192.168.4.60 is unreachable at boot, alpha still boots and guests start with EMPTY bind sources rather than hanging. This is deliberate — a hung Proxmox host is worse — but the empty-dir failure mode is not self-announcing. A mount-state check belongs in the health-check pipeline; not implemented here.

NEW — flagged for operator disposition:
- §2/§3 CONVERGE TREE NOT ON MAIN: deploy/ansible/ (31 files: ansible.cfg, inventory, playbooks, roles) exists ONLY on feature branches — feat/opnsense-staged-deployment, feat/repo-health-curator, chore/workspace-governance-monitor. origin/main carries only deploy/docker-compose.yml. LANES §2 designates the INFRA converge pipeline as the only door to production, yet that pipeline has never been merged to main. CHG-NFS-PERSIST-001 was therefore branched from feat/opnsense-staged-deployment, not main; landing it on main would have produced a playbook with no inventory or ansible.cfg. Merge target for the converge tree itself needs operator direction.
- Runbook artifacts/hc/2026-05-28-opnsense-readiness.md still names the wrong NFS server (192.168.4.10; actual export host is 192.168.4.60). Not corrected here — separate change, INFRA lane.

Next action in-session: reboot CT 409 so its mp0/mp1 binds pick up the now-populated NFS sources. Operator-directed. This terminates the working session; any verification after the reboot belongs to the next session.

# D082226T2000 | HA-0001 | converge log opened | JC | ha-ops repo

# D082326T2102 | HA-0001 | scaffold landed to SCM; LANES.md installed to infra repo | JC | ha-ops + infra repos
D082326T2102 HA-0001..HA-0008 — ha-ops scaffold v4 extracted to ~/ha-ops, validated (./validate.sh exit 0), git init on main, committed 02257b6, pushed to private jcasnellie69/ha-ops; LANES.md (HA-0005) installed verbatim at infra repo root, commit 6950615 pushed to jcasnellie69/homelab-config main. All eight registry rows HA-0001..HA-0008 remain OPEN pending their streams (AGENTS.md §8: rows close only on SCM-visible evidence referencing the ID). Status of every capability: Specified, not Operational (LANES §5d). No converge has been executed from either repo.

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

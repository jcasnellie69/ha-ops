# D100626T2302 | HA-0010 | IPL validation evidence and blocker closure traceability requirements | p.p. Copilot for JC | ha-ops repo

# IPL Validation Traceability Requirements

**Status: Specified**

These requirements govern automation that reports post-IPL validation results,
updates blocker issues or project status, transitions Jira items, or produces
a CAB completion/sign-off report. They apply to workflow behavior and every
skill, schema, and runbook that describes that behavior.

## Evidence requirements

- Give every validation run a stable run ID and retain its workflow URL, source
  revision, target LPAR, IPL timestamp, environment, trigger, and completion
  time.
- Record each check separately with a stable check ID, result (`pass`, `fail`,
  `warn`, or `skipped`), execution time, and evidence identifying the observed
  and expected result. Link stored artifacts where the evidence is too large
  for the run summary.
- Map each blocker issue by immutable issue ID to its acceptance criteria and
  the specific checks that verify those criteria. Keep the evidence links and
  verification decision on the issue or in an auditable report referenced by
  that issue.
- Preserve failed, warning, skipped, missing, and ambiguous results as
  non-passing. Do not infer success from a green aggregate, successful
  validation on another environment, or a passing subset of checks.

## Closure and sign-off requirements

- Evaluate closure independently for each blocker. A blocker is eligible only
  when every mapped acceptance criterion and required check has explicit
  passing evidence for the matching LPAR, IPL, and environment. Never close
  all blockers based solely on an overall run result.
- Keep a blocker open if evidence is missing, inconclusive, mismatched, or
  non-passing. A later passing run does not silently substitute for evidence
  from a different IPL or environment.
- Publish the run evidence and per-blocker eligibility decision before
  requesting operator approval. Record the approving operator, approval time,
  run ID, and exact issue/project/Jira/CAB actions approved.
- Without that explicit approval, do not close GitHub issues, mark project
  items Done, transition Jira items to Done, or claim CAB/production sign-off.
  Validation success alone is not approval.
- Report only transitions that actually succeeded. On partial failure, preserve
  unresolved items and identify the exact failed action; do not emit a
  blanket-success or signed-off report.

## Audit and documentation requirements

- Retain an append-only record of run evidence, per-blocker decisions,
  approvals, and completed transitions. Do not replace prior run history.
- Do not include credentials or other secrets in reports, issue comments,
  dashboards, or artifacts.
- Keep workflow implementation, skill descriptions, schemas, and operator
  instructions consistent. Mark a stage unavailable when its implementation
  or evidence source does not exist; do not describe an unimplemented stage as
  operational.
- Test both eligible and ineligible blockers, including mixed check outcomes,
  missing or mismatched evidence, absent approval, and partial downstream
  failures. Verify that no closure, Done transition, or sign-off occurs in
  those cases.

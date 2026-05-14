# Phase 3 Execution Plan: README Handoff And Final Validation

## Metadata

- Status: complete
- Roadmap stage: `v0`
- Feature focus: README governance handoff and final validation
- PR title: `Stage 0 Repository Skeleton And Governance - Phase 3: README Handoff And Final Validation`
- Branch: `agent/stage-0-p3-readme-final-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p3-readme-final-validation`
- Phase execution plan path: `docs/roadmap/stage-0/phases/readme-final-validation.md`
- Full plan: `docs/roadmap/stage-0/implementation-plan.md`
- Planning document: `docs/roadmap/stage-0/planning.md`
- Source phase: Phase 3, `readme-final-validation`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Plan quality gate: passed in implementation plan
- Draft pass: manager-local, no subagent requested
- Refine pass: not needed
- Setup limitations: phase was executed in the control checkout after Phase 2 merged
- Blockers: none

## Objective

Align the README with the implemented Stage 0 skeleton and record final focused
validation evidence without duplicating the canonical roadmap.

## Full-Plan Context

Phases 1 and 2 completed the package skeleton, base errors, and executable
governance guardrails. This phase updates the user-facing repository handoff
and verifies the complete Stage 0 result.

## In-Scope Work

- Update `README.md` with compact Milestone 0 status and roadmap pointer.
- State the public API stability rule and lightweight import policy.
- State the current all-rights-reserved/no-public-use-license status.
- State that generic workflow, artifact, and stage runtimes belong downstream or in `loom`.
- Run final focused validation and the local PR gate.

## Out-of-Scope Work

- Long architecture guide or roadmap duplication.
- Final public license selection.
- Optional dependency matrix or extras.
- Domain behavior or Milestone 1 contracts.

## Scope Contract

This phase changes README guidance and workflow artifacts only. It does not
change package metadata, public imports, runtime dependencies, package behavior,
or scientific contracts.

## Scientific Contract Notes

No scientific operation, sampling behavior, alignment rule, masking/filtering
order, normalization behavior, aggregation, subject identity handling, split
handling, or leakage behavior is introduced.

## Test Plan

- Package suite: required final guardrail check.
- Unit suite: required final error behavior check.
- Lockfile: required final dependency-resolution check.
- Whitespace: required final diff check.
- PR gate: run to produce suite summary and package build evidence.
- Contract, integration, e2e, and acceptance suites: reported as not present by `make test-summary`.

## Validation Commands

```sh
make test-package
make test-unit
uv lock --check
git diff --check
make test-summary
make validate-pr
```

## Completion Notes

- Draft plan: manager-local fast-path plan recorded in this artifact.
- Final phase execution plan: complete.
- Implementation summary: README now states Milestone 0 status, canonical roadmap policy, public API stability rule, lightweight import rule, orchestration boundary, and rights status.
- Implementation validation: `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check`, `make test-summary`, and `make validate-pr` passed.
- Refinement summary: not needed.
- Pre-submit blocker gate: passed; no scope, validation, or scientific-contract blockers found.
- PR preparation: PR body draft recorded in `docs/roadmap/stage-0/phases/readme-final-validation-pr-body.md`.
- Automated review: manager-local review passed before PR submission.
- Merge result: squash-merged through PR #4 into `develop` at `eaf9c62`.
- Cleanup: remote branch deleted by GitHub merge; no separate worktree was created.
- Remaining blockers: none.

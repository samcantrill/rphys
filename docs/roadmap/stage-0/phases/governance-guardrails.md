# Phase 2 Execution Plan: Governance Guardrail Tests

## Metadata

- Status: complete
- Roadmap stage: `v0`
- Feature focus: package governance guardrails
- PR title: `Stage 0 Phase 2: governance guardrail tests`
- Branch: `agent/stage-0-p2-governance-guardrails`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p2-governance-guardrails`
- Phase execution plan path: `docs/roadmap/stage-0/phases/governance-guardrails.md`
- Full plan: `docs/roadmap/stage-0/implementation-plan.md`
- Planning document: `docs/roadmap/stage-0/planning.md`
- Source phase: Phase 2, `governance-guardrails`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Plan quality gate: passed in implementation plan
- Draft pass: manager-local, no subagent requested
- Refine pass: not needed
- Setup limitations: phase was executed in the control checkout after Phase 1 merged
- Blockers: none

## Objective

Make Stage 0 governance executable with focused package tests for lightweight
imports, package metadata, rights status, public API boundaries, and absence of
generic workflow/artifact runtime packages.

## Full-Plan Context

Phase 1 established the importable skeleton and base errors. This phase adds
guardrail tests around that surface without changing package metadata or adding
runtime behavior. Phase 3 remains responsible for README handoff and final
cross-phase validation.

## In-Scope Work

- Add a fresh-interpreter import side-effect check for `rphys`, `rphys.errors`, and planned package homes.
- Assert obvious optional heavy stacks are not imported by core imports.
- Assert runtime dependencies remain empty and private/no-license metadata remains in place.
- Assert `LICENSE` still describes all-rights-reserved status.
- Assert generic workflow/artifact runtime package names are absent.

## Out-of-Scope Work

- Runtime dependency or optional-extra changes.
- License selection.
- README prose changes.
- Broadening the forbidden package list beyond the approved short list.
- Domain behavior or scientific contracts.

## Scope Contract

This phase adds tests only. It does not change the public runtime surface,
package imports, metadata, dependency resolution, or license text. Future
intentional license or dependency changes should update these tests alongside
the relevant roadmap decision.

## Scientific Contract Notes

No scientific operation, data-shape contract, sample-rate behavior, provenance
rule, leakage rule, or analysis semantics are introduced.

## Test Plan

- Package suite: required; `tests/package/test_import_boundaries.py` and `tests/package/test_metadata.py`.
- Unit suite: not required for this test-only governance phase.
- Contract, integration, e2e, and acceptance suites: deferred because no domain contract is introduced.

## Validation Commands

```sh
make test-package
uv lock --check
git diff --check
```

## Completion Notes

- Draft plan: manager-local fast-path plan recorded in this artifact.
- Final phase execution plan: complete.
- Implementation summary: added import-boundary, metadata/private-rights, and no-runtime guardrail tests.
- Implementation validation: `make test-package` passed; `uv lock --check` passed; `git diff --check` passed.
- Refinement summary: not needed.
- Pre-submit blocker gate: passed; no scope, validation, or scientific-contract blockers found.
- PR preparation: PR body draft recorded in `docs/roadmap/stage-0/phases/governance-guardrails-pr-body.md`.
- Automated review: manager-local review passed before PR submission.
- Merge result: squash-merged through PR #3 into `develop` at `c504d56`.
- Cleanup: remote branch deleted by GitHub merge; no separate worktree was created.
- Remaining blockers: none.

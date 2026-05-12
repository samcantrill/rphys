# Phase 1 Execution Plan: Core Skeleton And Base Errors

## Metadata

- Status: complete
- Roadmap stage: `v0`
- Feature focus: package homes and broad base errors
- PR title: `Stage 0 Phase 1: core skeleton and base errors`
- Branch: `agent/stage-0-p1-core-skeleton-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-0-p1-core-skeleton-errors`
- Phase execution plan path: `docs/roadmap/stage-0/phases/core-skeleton-errors.md`
- Full plan: `docs/roadmap/stage-0/implementation-plan.md`
- Planning document: `docs/roadmap/stage-0/planning.md`
- Source phase: Phase 1, `core-skeleton-errors`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Plan quality gate: passed in implementation plan
- Draft pass: manager-local, no subagent requested
- Refine pass: not needed
- Setup limitations: phase was executed in the control checkout because matching local phase files already existed there before a separate worktree was created
- Blockers: none

## Objective

Create the Stage 0 importable package skeleton and broad `RemotePhysError`
hierarchy without introducing domain behavior, optional dependencies, or root
package re-exports.

## Full-Plan Context

This phase establishes public import homes and base exception categories that
later milestones can build on. Phase 2 hardens package governance tests, and
Phase 3 aligns the README and final validation evidence. Metadata guardrails,
README prose, workflow/artifact runtime exclusions, and domain behavior remain
out of this phase.

## In-Scope Work

- Add planned package homes under `src/rphys` with concise docstrings and empty `__all__`.
- Add `src/rphys/errors.py` with `RemotePhysError` and the broad roadmap category subclasses.
- Preserve lightweight root import behavior and empty root `__all__`.
- Add package and unit tests for namespace imports, root API behavior, error exports, subclass relationships, and structured context behavior.

## Out-of-Scope Work

- Specific semantic error subclasses.
- Domain data, IO, operation, model, loss, metric, training, evaluation, or analysis behavior.
- README governance handoff.
- Optional dependencies, extras, registries, and generic workflow/artifact runtime packages.

## Scope Contract

`RemotePhysError(message: str, **context: object)` stores the message in
`.message`, preserves normal exception `args`, and copies keyword context into
`.context`. Broad subclasses inherit this behavior without adding semantics.
The root `rphys` package keeps an empty public surface and does not re-export
error classes.

## Scientific Contract Notes

No scientific operation, sampling behavior, temporal alignment, masking,
filtering, normalization, aggregation, subject identity, split handling, or
failure behavior for physiological data is introduced in this phase.

## Test Plan

- Package suite: `tests/package/test_import.py` checks root import behavior, planned namespace imports, empty namespace public surfaces, `rphys.errors.__all__`, and absence of root error re-exports.
- Unit suite: `tests/unit/rphys/test_errors.py` checks message, args, context copying, empty context, and broad subclass inheritance.
- Contract, integration, e2e, and acceptance suites: deferred because Stage 0 introduces no domain contracts.

## Validation Commands

```sh
make test-package
make test-unit
git diff --check
```

## Completion Notes

- Draft plan: manager-local fast-path plan recorded in this artifact.
- Final phase execution plan: complete.
- Implementation summary: planned package homes, broad error hierarchy, and focused import/error tests are implemented.
- Implementation validation: `make test-package` passed; `make test-unit` passed; `git diff --check` passed.
- Refinement summary: not needed.
- Pre-submit blocker gate: passed; no scope, validation, or scientific-contract blockers found.
- PR preparation: PR body draft recorded in `docs/roadmap/stage-0/phases/core-skeleton-errors-pr-body.md`.
- Automated review: manager-local review passed before PR submission.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.

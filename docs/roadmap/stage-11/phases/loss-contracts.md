# Phase 3 Execution Plan: Loss Contracts And Patch Results

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: backend-neutral loss contracts, terms, results, and field patches
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Loss Contracts And Patch Results
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 3: Loss Contracts And Patch Results`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p3-loss-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p3-loss-contracts`
- Phase execution plan path: `docs/roadmap/stage-11/phases/loss-contracts.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 3
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement the first executable semantic contract for losses over declared field
containers without introducing concrete numerical loss algorithms or backend
adapters.

## Scope Contract

- Add package-local loss modules for specs, context, results, and protocol
  behavior.
- Normalize `FieldLocator | str` inputs and validate duplicate inputs, duplicate
  writes, reductions, missing-field policy, expected metadata, missing fields,
  and empty mask payloads where contract-level validation can detect them.
- Preserve raw backend-native scalar handles on `LossTerm` with backend,
  differentiability, gradient-path, reduction, unit, diagnostics, metadata, and
  provenance.
- Expose `LossResult.fields` as immutable patch-only
  `FieldLocator -> FieldValue` mappings validated against declared writes.
- Do not mutate input containers and do not add concrete loss math,
  objectives, metrics, trainers, backend imports, or Stage 10 imports.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/losses/test_loss_contracts.py tests/contracts/test_loss_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added loss input specs/contracts, runtime context,
  structured terms/results, immutable patch validation, package exports, and
  central typed loss validation errors.
- Implementation validation: focused tests passed; `make test-unit`,
  `make test-contract`, `make test-package`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no concrete algorithms,
  backend imports, trainer/objective/metric coupling, root re-exports, or
  cross-package private helper imports were introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/loss-contracts-pr-body.md`.
- Automated review: passed manager-local; PR target/title verified and no
  remote checks were reported.
- Merge result: PR [#73](https://github.com/samcantrill/rphys/pull/73)
  squash merged to `develop` as `2dcca5c` on 2026-05-16.
- Cleanup: phase worktree pruned and local/remote phase branches deleted.
- Remaining blockers: none.

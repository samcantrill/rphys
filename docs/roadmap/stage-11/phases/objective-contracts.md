# Phase 4 Execution Plan: Objective Contracts And Optimizer Scalar Results

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v11`
- Feature focus: backend-neutral objective aggregation and required `.total`
- Stage descriptor: Loss, Objective, And Metric Contracts
- Phase descriptor: Objective Contracts And Optimizer Scalar Results
- PR title: `Stage 11 Loss, Objective, And Metric Contracts - Phase 4: Objective Contracts And Optimizer Scalar Results`
- Branch: `agent/stage-11-loss-objective-metric-contracts-p4-objective-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-11-loss-objective-metric-contracts-p4-objective-contracts`
- Phase execution plan path: `docs/roadmap/stage-11/phases/objective-contracts.md`
- Full plan: `docs/roadmap/stage-11/implementation-plan.md`
- Planning document: `docs/roadmap/stage-11/planning.md`
- Source phase: Phase 4
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path; manager-local refinement folded into this artifact
- Phase isolation: dedicated branch and worktree created from current `origin/develop`
- Plan quality gate: passed and current in the implementation plan
- Blockers: none

## Objective

Implement optimizer-facing objective contracts and result records with a
required `ObjectiveResult.total` handle, without adding backward calls,
optimizer/scheduler objects, trainer behavior, or backend adapters.

## Scope Contract

- Add package-local objective specs, contexts, results, validation helpers, and
  structural protocol.
- Expose aggregation descriptors with weights, reductions, and data-only
  schedules.
- Require `ObjectiveResult.total` as an `ObjectiveTerm` and preserve raw
  backend-native scalar handles.
- Validate invalid weights/reductions, duplicate terms/writes, malformed loss
  result context inputs, malformed totals, duplicate result term names, and
  undeclared patch fields.
- Consume only public `rphys.losses` records when referencing loss terms.

## Validation Commands

```sh
uv --cache-dir /tmp/uv-cache run pytest tests/unit/rphys/objectives/test_objective_contracts.py tests/contracts/test_objective_contract.py tests/unit/rphys/test_errors.py tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-package
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed.
- Implementation summary: added objective specs/contracts, context, terms,
  required-total result, immutable patch validation, package exports, and typed
  objective validation errors.
- Implementation validation: focused tests passed; `make test-unit`,
  `make test-contract`, `make test-package`, and `git diff --check` passed.
- Pre-submit blocker gate: passed manager-local; no backward calls,
  optimizer/scheduler objects, trainer behavior, backend imports, loss private
  helper imports, or root re-exports were introduced.
- PR preparation: PR body drafted in
  `docs/roadmap/stage-11/phases/objective-contracts-pr-body.md`.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.

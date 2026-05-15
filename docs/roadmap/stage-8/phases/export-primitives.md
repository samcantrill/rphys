# Phase 1 Execution Plan: Export Primitives, Layout, Policy, And Result Records

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v8`
- Feature focus: save/export operations and derived datasource foundations
- Stage descriptor: Save/Export Ops And Derived DataSources
- Phase descriptor: Export Primitives, Layout, Policy, And Result Records
- PR title: `Stage 8 Save/Export Ops And Derived DataSources - Phase 1: Export Primitives, Layout, Policy, And Result Records`
- Branch: `agent/stage-8-p1-export-primitives`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-8-p1-export-primitives`
- Phase execution plan path: `docs/roadmap/stage-8/phases/export-primitives.md`
- Full plan: `docs/roadmap/stage-8/implementation-plan.md`
- Planning document: `docs/roadmap/stage-8/planning.md`
- Source phase: Phase 1
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: dedicated branch/worktree/PR to `develop`
- Plan quality gate: passed in implementation plan review
- Draft pass: manager-local fast path
- Refine pass: not needed unless targeted validation exposes a blocker
- Setup limitations: existing unrelated control-checkout `docs/roadmap.md` changes were not copied
- Blockers: none

## Objective

Add the data-only export surface under `rphys.ops.export`: immutable request,
target, layout, policy, outcome, result, and report records with deterministic
target derivation and stable spec fingerprints. This phase must not write files,
select codecs, execute save operations, link/copy resources, serialize durable
reports, or assemble derived datasources.

## Full-Plan Context

This phase establishes records used by later selection, save, link/copy, and
derived datasource phases. Later phases own `CodecSelectionOperation`,
`SaveOperation`, private local helpers, and descriptor-only derived assembly.

## Scope Contract

Public records live only in `rphys.ops.export` and are not root or parent-package
exports. Fingerprints include requested fields, codec/schema requests,
metadata-save policy, layout version, resource suffix, and output options; they
exclude target root, export target identity, timestamps, file existence, codec
registry identity, Python object identity, and workflow runtime state.

## Implementation Steps

1. Add `rphys.ops.export` data-only records, enums, validation, and target layout.
2. Add unit tests for target derivation, fingerprint sensitivity/exclusions, and policy outcomes.
3. Add unit/contract tests for typed in-memory result and report aggregation.
4. Add package/import tests for scoped exports, no root exports, and no shorthand aliases.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_export_layout.py tests/unit/rphys/ops/test_export_policy.py tests/unit/rphys/ops/test_export_results.py
uv run pytest tests/contracts/test_export_result_contract.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Completion Notes

- Draft plan: completed manager-local fast path.
- Final phase execution plan: scope-complete for Phase 1.
- Implementation summary: added `rphys.ops.export` records for specs, targets,
  layouts, policies, outcomes, field/record/export results, and in-memory
  reports; added deterministic target derivation and stable spec fingerprints.
- Implementation validation: targeted unit tests, export result contract,
  `make test-package`, `make validate-pr`, `make test-summary`, and
  `git diff --check` passed locally.
- Pre-submit blocker gate: passed; no save execution, selection operation,
  durable report serialization, root exports, shorthand aliases, link/copy
  helpers, or derived datasource assembly are present.
- PR preparation: pending.
- Automated review: pending.
- Merge result: pending.
- Cleanup: pending.
- Remaining blockers: none.

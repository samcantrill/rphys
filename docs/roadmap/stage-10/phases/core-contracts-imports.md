# Phase 1 Execution Plan: Core Public Contracts And Import Boundaries

## Metadata

- Status: scope-complete phase execution plan
- Roadmap stage: `v10`
- Feature focus: method/model prediction contract records and import boundaries
- Stage descriptor: Models, Methods, And NN Base Contracts
- Phase descriptor: Core Public Contracts And Import Boundaries
- PR title: `Stage 10 Models, Methods, And NN Base Contracts - Phase 1: Core Public Contracts And Import Boundaries`
- Branch: `agent/stage-10-method-model-contracts-p1-core-contracts-imports`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p1-core-contracts-imports`
- Phase execution plan path: `docs/roadmap/stage-10/phases/core-contracts-imports.md`
- Full plan: `docs/roadmap/stage-10/implementation-plan.md`
- Planning document: `docs/roadmap/stage-10/planning.md`
- Source phase: `Phase 1: Core Public Contracts And Import Boundaries`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phase 0 merged and recorded
- Draft pass: manager-local, because no subagent delegation was requested in this session
- Refine pass: not needed unless validation exposes public API drift
- Setup limitations: unrelated control-checkout roadmap/stage-11 docs are preserved outside this worktree
- Blockers: none

## Objective

Establish code-backed, dependency-light public contracts for batch-level methods, lower-level models, prediction context, and patch-like method outputs without adding adapters, state/trainable records, torch helpers, trainers, losses, metrics, or export behavior.

## Full-Plan Context

Phase 1 follows the Phase 0 LIST uncollation repair and creates the minimal contracts that Phase 2 adapters and Phase 3 capability records will extend. Later phases own output application, state/trainable records, and synthetic integration.

## Source Phase Summary

- Goal: add `Method`, `Model`, `PredictionContext`, and `MethodOutput` with scoped package exports.
- Required scope: `src/rphys/methods/core.py`, `context.py`, `output.py`, `src/rphys/models/core.py`, package exports, package/unit/contract tests.
- Required checkpoints: lightweight imports, no root exports, no torch import, no `Batch` import from models, immutable/copy-protected records, primitive metadata/provenance only, and no hidden mutation/training/export/loss/metric behavior.
- Acceptance criteria: fake method/model contract probes pass and context/output records preserve patch semantics.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `rphys.methods`, `rphys.models`, and `rphys.nn` package homes currently have empty `__all__`; `RemotePhysMethodError` already exists for method failures.
- Existing tests or harness behavior: package import tests expect deferred package homes to be empty and import-boundary tests assert heavy optional modules are not imported.
- Import-boundary or dependency constraints: `rphys.methods` may import `Batch` and field records as needed; `rphys.models` must not import `Batch`, datasources, loaders, torch, losses, metrics, trainers, or export helpers.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` and `docs/roadmap/stage-11/planning.md` changes remain outside the phase worktree.
- Dedicated branch/worktree status: created from current `origin/develop`.
- Current `develop` base: `ecab928`
- Earlier phase dependency status: Phase 0 merged and metadata pushed.
- Push/PR infrastructure status: GitHub auth, fetch, push, PR creation, and merge were verified during Phase 0.
- Stop condition if isolation cannot be maintained: mark Phase 1 blocked and stop rather than implement in the control checkout.

## In-Scope Work

- Add immutable `PredictionContext` with string-keyed primitive metadata/provenance mappings.
- Add immutable patch-like `MethodOutput` with `FieldLocator` to `FieldValue` fields and primitive diagnostics/metadata/provenance mappings.
- Add structural runtime-checkable `Method` and `Model` protocols.
- Add scoped package exports and package/import-boundary tests.
- Add focused unit and contract tests for record behavior and fake method/model conformance.

## Out-of-Scope Work

- Adapters, output apply/merge helpers, state/trainable records, `rphys.nn` helpers, concrete algorithms, losses, metrics, learners, trainers, device movement, checkpoints, torch helpers, and public model input/output records.

## Assumptions

- Primitive context/output metadata values are limited to `str`, `int`, `float`, `bool`, and `None`.
- `MethodOutput` copies mapping containers but preserves `FieldValue` objects to avoid copying tensor-like payloads.
- Exact field names can grow additively in later phases if the locked semantics remain intact.

## Scope Contract

`Method.predict(batch, *, context=None) -> MethodOutput` is a structural protocol and does not require inheritance. `Model[InputT, OutputT]` is a structural callable protocol below `Batch` and does not import runtime containers. `PredictionContext` and `MethodOutput` are frozen top-level records that defensively copy and expose read-only mappings. Neither record defines first-class sample IDs, batch IDs, split labels, dtype/device fields, trainer modes, export paths, optimizer handles, or checkpoint policy.

## Scientific Contract Notes

- Sampling and temporal alignment: no sampling, alignment, filtering, masking, or normalization behavior is introduced.
- Field roles, locators, schemas, and provenance: output patches retain explicit `FieldLocator` keys and `FieldValue` objects; provenance is caller-supplied primitive metadata.
- Masking, filtering, normalization, and aggregation order: not affected.
- Subject identity, splits, leakage, and grouping: no identity/split/leakage policy is encoded; downstream code may pass caller-owned primitive metadata.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not interpreted by Phase 1 records or protocols.

## Design Impact

- Maintainability: public contracts are small modules with private shared primitive validation.
- Extensibility: Phase 2 adapters and Phase 3 capability records can import these names without changing their semantics.
- Lightweight import policy: no new runtime dependencies or optional backend imports.
- Source-tree boundaries: methods can see `Batch`; models stay below runtime containers.

## Future Compatibility

Stage 11-13 can consume patch fields from `MethodOutput`; Stage 12 can compose any structural method/model without inheriting trainer or backend lifecycle hooks.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Public method/model base classes | Structural protocols avoid inheritance lock-in before concrete algorithms exist. |
| Returning `Batch` from `predict` | DQ-2 locked patch-only output and explicit later application. |
| Model input/output public records | No current concrete model evidence justifies freezing those shapes in Stage 10 Phase 1. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Primitive mapping helper remains private under `rphys.methods` | Only context/output need it now | Stage 11/12 duplicate identical primitive-record validation |

## Reviewability

- Expected PR size and shape: small public contracts, package exports, and focused tests.
- Files and areas to inspect: `src/rphys/methods/`, `src/rphys/models/`, package/unit/contract tests, and import-boundary tests.
- Scope-control checks: no root exports, no torch import, no `Batch` import from models, no adapters/state/trainers/export behavior.

## Implementation Steps

1. Add private primitive mapping validation and immutable `PredictionContext`.
2. Add `MethodOutput` field patch record and structural `Method` protocol.
3. Add generic structural `Model` protocol without runtime-container imports.
4. Update methods/models package exports and package/import-boundary tests.
5. Add focused unit and contract tests, then run required validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `make test-package`
- Required assertions or deferral reason: scoped public exports and heavy-import boundaries.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/methods/test_context.py`, `tests/unit/rphys/methods/test_output.py`
- Required assertions or deferral reason: mapping copies, read-only mappings, primitive validation, no domain identifier attributes, and patch fields.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_method_contract.py`, `tests/contracts/test_model_contract.py`
- Required assertions or deferral reason: fake structural method/model conformance and boundaries.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: adapter-backed synthetic prediction flow belongs to Phase 2/4.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no workflow runtime behavior.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no user-facing acceptance workflow is introduced.

## Risks

- Public record fields may need additive later fields; tests should avoid overfitting to future adapters.
- Runtime-checkable protocols only prove attribute presence, so contract tests must exercise fake behavior.
- Primitive mapping validation must not become a domain identity taxonomy.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/methods/test_context.py tests/unit/rphys/methods/test_output.py
uv run pytest tests/contracts/test_method_contract.py tests/contracts/test_model_contract.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: primitive records, method output, method protocol, model protocol, exports/tests.
- Tests to run with each slice: focused unit tests first, then method/model contract tests and package tests.
- Decisions the executor must not revisit: patch-only output, structural protocols, model below `Batch`, primitive context only, no torch helper.
- Conditions that require stopping for the manager: any need for `Batch` return, model import of runtime containers, hard torch import, or trainer/export/loss/metric behavior.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed by manager in phase worktree.
- Final phase execution plan: this document.
- Implementation summary: added `PredictionContext`, `MethodOutput`, structural `Method`, structural generic `Model`, scoped methods/models package exports, private primitive mapping validation, and focused package/unit/contract tests.
- Implementation validation: `uv run pytest tests/unit/rphys/methods/test_context.py tests/unit/rphys/methods/test_output.py`, `uv run pytest tests/contracts/test_method_contract.py tests/contracts/test_model_contract.py`, `make test-package`, `make validate-pr`, `make test-summary`, and `git diff --check` passed. `make test-summary` reported package 47 passed, unit 637 passed, contract 123 passed, integration 18 passed, and no e2e/acceptance suites present.
- Refinement summary: fixed a brittle floating-point assertion in the new model contract probe.
- Pre-submit blocker gate: passed; no root export, model `Batch` import, heavy optional import, hidden mutation, or trainer/export/loss/metric scope blocker found.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

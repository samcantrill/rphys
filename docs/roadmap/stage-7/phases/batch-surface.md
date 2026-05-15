# Phase 6 Execution Plan: Provisional Batch Operation Surface

## Metadata

- Status: draft phase execution plan
- Roadmap stage: `v7`
- Feature focus: provisional batch operations, batch augmentations, equivalence, and pipeline surface
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines
- Phase descriptor: Provisional Batch Operation Surface
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 6: Provisional Batch Operation Surface`
- Branch: `agent/stage-7-p6-batch-surface`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p6-batch-surface`
- Phase execution plan path: `docs/roadmap/stage-7/phases/batch-surface.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: Phase 6, `batch-surface`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path because this adds a provisional public surface
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation-plan quality gate already passed
- Draft pass: completed in this artifact
- Refine pass: pending only if equivalence fields imply backend, loader, or model policy
- Setup limitations: none; branch and worktree created from `develop`
- Blockers: none

## Objective

Add a dependency-light provisional batch operation family that can describe,
execute, and compare batch-level operation behavior against sample-side
correctness without introducing backend arrays, DataLoader/model policy, device
movement, cache/export identity, or broad batch planning semantics.

## Full-Plan Context

Phases 1 through 5 established the generic operation-step contract, sample
operations, replayable augmentations, mutation enforcement, checks, and
specialized sample pipelines. Phase 6 mirrors only the approved provisional
batch surface on top of existing `Batch`, `FieldLocator`, and `OperationResult`
contracts. Phase 7 will finalize docs and broad validation evidence. Stage 9
batch planning, loader adapters, cache/materialization, and fused backend
kernels remain deferred.

## Source Phase Summary

- Goal: add dependency-light provisional batch operation, augmentation,
  equivalence, and pipeline APIs referenced to sample-side correctness.
- Required scope: `BatchOperation`, `BatchTransform`, `BatchAugmentation`,
  `BatchOperationContext`, `BatchOperationContract`,
  `BatchEquivalenceReport`, batch/per-sample parameter scope declarations,
  descriptive dtype/device metadata, and `BatchOperationPipeline` sequence and
  mapping diagnostics.
- Required checkpoints: no Torch/DataLoader/model imports, no device movement,
  no broad `BatchProgram`, no selector-hot-loop policy, no collation policy
  changes, and no backend-native arrays in public records.
- Acceptance criteria: public batch contracts are inspectable, params scope is
  explicit, equivalence reports reject unsupported claims, synthetic
  LIST-collated integration examples pass, and package import boundaries stay
  lightweight.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/data` exposes
  `Batch`, `Sample`, `FieldValue`, and LIST-only `collate_samples`; sample
  operation code in `src/rphys/ops/sample.py` is the correctness reference;
  `src/rphys/ops/pipelines.py` already has private specialized pipeline
  diagnostics for sample operations.
- Existing tests or harness behavior: data collation tests cover LIST-collated
  `Batch`; operation runtime boundary tests cover generic `Operation` treating
  `Batch` as an ordinary payload; package tests enforce public exports and
  import boundaries.
- Import-boundary or dependency constraints: the batch surface must not import
  NumPy, Torch, pandas, cv2, av, scipy, matplotlib, DataLoader, model,
  trainer, export, cache, or workflow modules.

## Phase Isolation State

- Control checkout dirty-state review: control checkout had unrelated untracked
  `docs/roadmap/stage-8/`; it is outside Phase 6 scope and must be left alone.
- Dedicated branch/worktree status: branch `agent/stage-7-p6-batch-surface`
  and worktree `/home/samcantrill/work/rphys-worktrees/stage-7-p6-batch-surface`
  were created from `develop`.
- Current `develop` base: `bd5282d docs: record stage 7 phase 5 merge`
- Earlier phase dependency status: Phases 1 through 5 are merged to `develop`.
- Push/PR infrastructure status: GitHub CLI and push/merge path were available
  for prior phases.
- Stop condition if isolation cannot be maintained: stop and mark the phase
  blocked rather than implementing in the control checkout or combining phases.

## In-Scope Work

- Add `src/rphys/ops/batch.py` with provisional public batch operation records
  and wrappers.
- Reuse `SampleFieldPermissions` or an equivalent field-permission declaration
  shape without changing sample semantics.
- Add `BatchOperationContext` with lightweight metadata/provenance, batch shape,
  dtype/device descriptors, and replay seed material as descriptive evidence.
- Add `BatchOperationContract` with field permissions, required context,
  failure modes, mutation policy, side effects, copy mode, and descriptive
  batch equivalence metadata.
- Add `BatchOperation`, `BatchTransform`, and `BatchAugmentation` callable-first
  wrappers over `Batch`.
- Add `BatchAugmentationParams` with explicit scope values such as batch-level
  and per-sample params.
- Add `BatchEquivalenceReport` with allowed claim labels and required
  diagnostics for approximate or unsupported claims.
- Add `BatchOperationPipeline` with the same specialized sequence and mapping
  diagnostic contract as `SampleOperationPipeline`.
- Add package, unit, contract, and integration tests over synthetic
  LIST-collated fixtures.

## Out-of-Scope Work

- Torch, DataLoader, model layout, trainer, optimizer, or device movement
  policy.
- Concrete fused kernels or backend array execution.
- Changing LIST collation or adding collation policies.
- Hot-loop selector parsing or a broad batch planner/program.
- Export/save/cache/materialization identity.
- DAGs, retry/resume, workflow runtime behavior, or loader orchestration.
- Root `rphys` exports or top-level `rphys.transforms`.

## Assumptions

- `Batch` has the same field-container mutation API as `Sample`, so snapshot
  enforcement can be dependency-light.
- LIST-collated fields are enough to validate provisional equivalence examples.
- Dtype/device metadata can remain strings or immutable primitive mappings,
  not actual backend objects.
- Existing pipeline diagnostics can be generalized privately without changing
  `OperationPipeline` or sample pipeline public behavior.

## Scope Contract

The batch surface is provisional but code-backed. Public batch operations accept
and return `Batch` objects through `OperationResult`. Field effects are
detected through before/after `field_items()` snapshots and must obey declared
permissions. Batch params must declare whether they apply to the whole batch or
per sample. Equivalence reports must describe whether a batch operation is an
identical, approximate, diagnostic-only, or unsupported replacement for the
sample-side behavior, and must include human-readable diagnostics for
approximate or unsupported claims.

Batch APIs may carry descriptive dtype/device metadata, but that metadata must
not move data, allocate arrays, import backend libraries, or imply model
layout. Batch pipelines preserve sequence or insertion-ordered mapping order,
use mapping keys only as diagnostics, and wrap failures with step index,
operation name, and effective diagnostic name. Unsupported public inputs must
fail with typed operation errors.

## Scientific Contract Notes

- Sampling and temporal alignment: batch APIs do not resample or align data;
  equivalence reports must document whether sample-side masking/alignment and
  replay obligations are satisfied, approximate, diagnostic-only, or
  unsupported.
- Field roles, locators, schemas, and provenance: field permissions remain
  exact locator declarations; batch wrappers do not broaden locator matching or
  mutate provenance policy.
- Masking, filtering, normalization, and aggregation order: no new scientific
  transforms are introduced. Any operation-specific scientific meaning remains
  caller-provided and must be represented in diagnostics or operation docs.
- Subject identity, splits, leakage, and grouping: no subject, split, loader,
  or grouping policy is introduced. Batch contexts may carry descriptive
  metadata only.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: the base batch wrappers do not inspect payload contents;
  such behavior remains operation-specific.

## Design Impact

- Maintainability: keep batch helpers small and private, mirroring sample
  behavior only where the contracts are already proven.
- Extensibility: retain enough descriptive metadata for Stage 9 batch planning
  without introducing backend or loader policy now.
- Lightweight import policy: base batch imports stay within standard library,
  `rphys.data`, `rphys.errors`, and existing `rphys.ops` modules.
- Source-tree boundaries: batch operation code belongs in `src/rphys/ops`; no
  data collation, datasource, IO, model, trainer, export, cache, or workflow
  modules are edited except focused tests if needed.

## Future Compatibility

- Stage 9 may build loader/cache/batch planning on top of the provisional
  public records after real backend requirements are known.
- Future fused kernels can provide stronger `BatchEquivalenceReport`
  diagnostics without changing sample operation correctness contracts.
- Dtype/device descriptors can later inform backend adapters but are not
  device movement instructions in this phase.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Require NumPy/Torch arrays in batch params or contexts | Violates lightweight base imports and prematurely commits backend policy. |
| Encode DataLoader/model layout policy | Loader, trainer, and model integration are future-stage responsibilities. |
| Change collation policy to support batch tests | Phase 6 must validate against existing LIST collation without expanding data behavior. |
| General batch planner/program API | The approved scope is provisional operations and equivalence evidence, not a batch execution language. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Equivalence diagnostics are descriptive rather than mathematically exhaustive | Keeps the base library backend-light while requiring explicit claims | A concrete fused kernel needs stronger numeric-equivalence evidence |
| Dtype/device metadata is string/primitive evidence only | Avoids backend imports and movement policy | Stage 9 or model integration needs structured backend adapters |

## Reviewability

- Expected PR size and shape: expanded but bounded public surface in batch ops,
  pipeline exports, package/unit/contract/integration tests, and phase docs.
- Files and areas to inspect: `src/rphys/ops/batch.py`,
  `src/rphys/ops/pipelines.py`, `src/rphys/ops/__init__.py`, batch-focused
  tests, package import tests, and synthetic integration fixtures.
- Scope-control checks: no backend imports, no DataLoader/model/trainer/cache/
  export/workflow modules, no collation changes, no root exports, no broad
  planner.

## Implementation Steps

1. Implement batch public records and validation helpers in a new batch module:
   context, contract, params, and equivalence report.
2. Implement `BatchOperation`, `BatchTransform`, and `BatchAugmentation` with
   field snapshot enforcement and deterministic split between parameter
   sampling and application.
3. Add `BatchOperationPipeline` and private shared pipeline normalization only
   where it does not change generic or sample pipeline public behavior.
4. Wire lazy exports from `rphys.ops` and package import tests.
5. Add unit, contract, and integration coverage for public behavior,
   diagnostics, import boundaries, and synthetic LIST-collated equivalence.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`.
- Required assertions or deferral reason: batch names are exported only from
  `rphys.ops`, package imports stay lightweight, and forbidden backend/workflow
  imports do not appear.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_batch.py` and pipeline tests.
- Required assertions or deferral reason: context/contract validation, params
  scope validation, equivalence claims, batch operation execution, declared
  field effects, augmentation sampling/application, pipeline sequence/mapping
  diagnostics, invalid inputs, and copy modes.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_batch_operations.py` or equivalent.
- Required assertions or deferral reason: provisional public API semantics,
  equivalence report requirements, batch params scope, pipeline diagnostics,
  and explicit generic/sample behavior preservation.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_batch_operations.py` or equivalent.
- Required assertions or deferral reason: synthetic LIST-collated sample-to-
  batch fixtures demonstrate identical and approximate equivalence claims and
  per-sample diagnostic recovery without backend imports.

### E2E Suite

- Status: deferred
- Expected paths: none.
- Required assertions or deferral reason: no real dataset, model, trainer,
  DataLoader, GPU, or workflow behavior is in scope.

### Acceptance Suite

- Status: deferred
- Markers affected: none.
- Required assertions or deferral reason: no benchmark, hardware, opt-in, or
  long-running fused-kernel validation is required.

## Risks

- Public provisional names may appear more stable than intended if docs omit
  the provisional label.
- Equivalence reports can overclaim replacement behavior if unsupported or
  approximate claims do not require diagnostics.
- Batch wrappers could accidentally import backend libraries through convenience
  checks.
- Pipeline helper reuse could regress generic or sample pipeline behavior.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_batch.py
uv run pytest tests/contracts/test_batch_operations.py
uv run pytest tests/integration/test_batch_operations.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-integration
make test-package
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: public records first, batch execution second,
  augmentation/equivalence third, pipeline/export fourth, integration/package
  coverage fifth.
- Tests to run with each slice: focused unit tests after records/execution;
  contract tests after public semantics; integration after LIST fixtures;
  package tests after exports; `git diff --check` before PR prep.
- Decisions the executor must not revisit: no backend arrays or imports, no
  DataLoader/model/trainer/device movement, no collation changes, no broad
  batch planner, no export/cache/workflow behavior, no root exports.
- Conditions that require stopping for the manager: batch records need backend
  objects, equivalence claims require numeric backend policy, LIST collation is
  insufficient for synthetic examples, or implementation requires changing
  generic/sample pipeline behavior.

## Refinement And Review Budget Status

- Phase execution plan refinement: unused / not needed unless backend policy is implicated
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: pending
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending
- Pre-submit blocker gate: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

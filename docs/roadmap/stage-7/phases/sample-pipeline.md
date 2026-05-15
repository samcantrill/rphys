# Phase 5 Execution Plan: Specialized Sample Pipeline Composition

## Metadata

- Status: implementation complete; PR preparation pending
- Roadmap stage: `v7`
- Feature focus: sample operation pipeline composition
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines
- Phase descriptor: Specialized Sample Pipeline Composition
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 5: Specialized Sample Pipeline Composition`
- Branch: `agent/stage-7-p5-sample-pipeline`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p5-sample-pipeline`
- Phase execution plan path: `docs/roadmap/stage-7/phases/sample-pipeline.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: Phase 5, `sample-pipeline`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path with explicit Stage 6 regression checks
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: implementation-plan quality gate already passed
- Draft pass: completed in this artifact
- Refine pass: not needed; implementation preserved generic pipeline behavior
- Setup limitations: none; branch and worktree created from `develop`
- Blockers: none

## Objective

Implement the public `SampleOperationPipeline` specialized pipeline for
sequential and insertion-ordered mapping composition of sample operation steps,
with sample context propagation and step-aware diagnostics, while preserving the
generic `OperationPipeline` sequence-only Stage 6 contract.

## Full-Plan Context

Phases 1 through 4 established the generic operation-step interface, sample
operation contracts, field-effect enforcement, checks, transforms, and
replayable augmentations. This phase adds only sample-specialized pipeline
composition over those completed primitives. Phase 6 owns the provisional batch
pipeline and batch operation surface, and Phase 7 owns final docs and validation
readback. This phase must not introduce DAGs, routing graphs, retry/resume,
loader orchestration, workflow runtime behavior, cache/export identity, or
batch APIs.

## Source Phase Summary

- Goal: implement `SampleOperationPipeline` ordering, context propagation, and
  step-aware diagnostics without changing generic `OperationPipeline`.
- Required scope: sequence and insertion-ordered mapping construction, private
  immutable step normalization, mapping keys as diagnostic names, context
  propagation, `OperationResult.output` forwarding, invalid step rejection, and
  failures with step index and effective name.
- Required checkpoints: generic `OperationPipeline` still rejects mappings and
  tuple named entries; sample pipeline accepts mappings only in the specialized
  class; missing fields and undeclared mutations surface through pipeline
  execution diagnostics.
- Acceptance criteria: order is deterministic; mapping keys are diagnostic
  labels only; public helpers are not added; no workflow, graph, loader, or
  batch semantics are introduced.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/ops/pipelines.py`
  currently exports only sequence-only `OperationPipeline`; `src/rphys/ops/sample.py`
  provides `SampleOperation`, `SampleOperationContext`, `SampleTransform`,
  `SampleCheck`, and `SampleAugmentation`; `src/rphys/ops/__init__.py` uses lazy
  sample exports to keep package imports lightweight.
- Existing tests or harness behavior: `tests/unit/rphys/ops/test_pipelines.py`
  and `tests/contracts/test_operation_pipeline_contract.py` lock generic
  sequence-only behavior and mapping rejection. Sample operation tests already
  cover field-effect and lazy-boundary enforcement for individual steps.
- Import-boundary or dependency constraints: no NumPy, Torch, plotting,
  video/array stacks, dataset SDKs, loader/cache/export modules, or workflow
  runtime imports are allowed in base operation imports.

## Phase Isolation State

- Control checkout dirty-state review: control checkout had unrelated untracked
  `docs/roadmap/stage-8/`; it is outside Phase 5 scope and must be left alone.
- Dedicated branch/worktree status: branch `agent/stage-7-p5-sample-pipeline`
  and worktree `/home/samcantrill/work/rphys-worktrees/stage-7-p5-sample-pipeline`
  were created from `develop`.
- Current `develop` base: `fa84992 docs: record stage 7 phase 4 merge`
- Earlier phase dependency status: Phases 1 through 4 are merged to `develop`.
- Push/PR infrastructure status: GitHub CLI and push/merge path were available
  for prior phases.
- Stop condition if isolation cannot be maintained: stop and mark the phase
  blocked rather than implementing in the control checkout or combining phases.

## In-Scope Work

- Add public `SampleOperationPipeline` in the operation pipeline surface.
- Accept non-empty sequences of sample operation steps.
- Accept insertion-ordered mappings of diagnostic names to sample operation
  steps.
- Preserve the ordered tuple of underlying operations as immutable public
  inspection state.
- Use mapping keys only as pipeline diagnostics, not as operation identity,
  registry names, routing labels, or durable artifact identifiers.
- Propagate one `SampleOperationContext` to every step, adapting a generic
  `OperationContext` when provided.
- Forward each step's `OperationResult.output` into the next step.
- Wrap execution failures with step index, operation name, and effective
  diagnostic name.
- Add focused package, unit, and contract tests plus generic pipeline
  regression checks.

## Out-of-Scope Work

- Changing generic `OperationPipeline` mapping rejection or constructor
  signature.
- Batch operation or `BatchOperationPipeline` behavior.
- Tuple named entries in either generic or sample pipelines.
- DAGs, branches, routers, route-policy execution, retries, resume semantics,
  workflow runtime behavior, loader orchestration, cache/export identity, or
  artifact writing.
- Public step-record helper classes or registries.
- Concrete rPPG transforms or model/trainer consumption.

## Assumptions

- Python mapping insertion order is sufficient for the approved specialized
  ordered mapping API.
- Existing `SampleOperationContext` can carry the phase's runtime context
  requirements without adding fields.
- Existing `OperationPipelineExecutionError` can carry sample pipeline step
  diagnostics through context fields without adding a new error class.
- Existing sample operation enforcement remains the authoritative field-effect
  and lazy-boundary behavior inside pipeline steps.

## Scope Contract

`SampleOperationPipeline` is a public specialized composition wrapper for
sample operation steps. It must require each step to be a `SampleOperation`
instance or another object that satisfies the sample operation contract already
exposed by Phase 2 through Phase 4. It must not accept raw callables, text,
empty collections, tuple named entries, or non-sample generic operations. A
sequence preserves sequence order. A mapping preserves insertion order and
stores keys as effective diagnostic names. The pipeline returns the final
`OperationResult` from the last step after forwarding intermediate
`OperationResult.output` values.

Errors must be typed and inspectable. Construction errors use
`InvalidOperationPipelineError` with `step_index` and, for mapping inputs,
`step_name` or equivalent diagnostic context. Execution errors use
`OperationPipelineExecutionError` and include the failing step index, underlying
operation name, effective diagnostic name, phase, and cause type. Missing-field,
context, result-shape, and undeclared mutation failures remain the underlying
sample operation causes and are not converted into policy decisions.

## Scientific Contract Notes

- Sampling and temporal alignment: the pipeline must not resample, window,
  align, normalize, or otherwise interpret payloads. It only preserves step
  order and context propagation.
- Field roles, locators, schemas, and provenance: locator permissions,
  replacements, deletes, and replay metadata remain owned by individual
  `SampleOperation` steps; pipeline diagnostics must not broaden field
  permissions.
- Masking, filtering, normalization, and aggregation order: no new filtering,
  masking, normalization, or aggregation behavior is introduced. Pipeline order
  is explicit and deterministic.
- Subject identity, splits, leakage, and grouping: no split, subject, loader,
  or grouping policy is introduced. Context metadata passes through unchanged.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: the pipeline does not inspect payload contents; such
  conditions must be handled by the individual operations that understand them.

## Design Impact

- Maintainability: keep shared step validation private and local to pipeline
  internals, with tests proving generic behavior is unchanged.
- Extensibility: batch pipelines in Phase 6 can reuse private normalization
  ideas, but this phase must not add public helper records or generic mapping
  support.
- Lightweight import policy: keep sample pipeline imports within `rphys.ops`,
  `rphys.data`, and existing error/context/contract modules only.
- Source-tree boundaries: implementation belongs in `src/rphys/ops/pipelines.py`
  and public lazy exports in `src/rphys/ops/__init__.py`; tests stay under the
  existing package/unit/contract hierarchy.

## Future Compatibility

- Phase 6 may add `BatchOperationPipeline` with similar diagnostics after the
  sample contract is proven here.
- Stage 9 loader adapters may call sample pipelines, but no loader adapter,
  materialization manifest, or worker orchestration is introduced now.
- Mapping keys remain diagnostic only so future export/cache systems do not
  inherit accidental durable identity semantics.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add mapping support to generic `OperationPipeline` | DD-6 requires specialized-only mapping support and Stage 6 regression tests preserve generic sequence-only behavior. |
| Accept tuple named entries | The implementation plan explicitly keeps tuple named entries out of both generic and sample pipeline construction. |
| Public step descriptor records | Private normalization is enough for diagnostics; public records would reserve future API names without behavior. |
| Route-aware or DAG pipeline semantics | Routing, graph execution, retry/resume, and workflow behavior are outside Stage 7 Phase 5. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Mapping keys are diagnostics rather than durable identifiers | Keeps Phase 5 narrow and avoids export/cache identity commitments | Stage 8/9 export, cache, or loader planning requires stable pipeline identity |
| Specialized pipeline helper shape remains private | Avoids public helper leakage before batch reuse is known | Phase 6 duplicates enough private logic to justify a shared internal helper |

## Reviewability

- Expected PR size and shape: small-to-medium focused change in pipeline code,
  lazy exports, and tests.
- Files and areas to inspect: `src/rphys/ops/pipelines.py`,
  `src/rphys/ops/__init__.py`, `tests/unit/rphys/ops/test_pipelines.py`,
  `tests/contracts/test_operation_pipeline_contract.py`, package import tests,
  and any new sample-pipeline-specific tests.
- Scope-control checks: generic `OperationPipeline` still rejects mappings;
  no batch surface appears; no public private-helper exports appear; no heavy
  imports or workflow/cache/loader modules appear.

## Implementation Steps

1. Add private sample-pipeline step normalization and diagnostic-name handling
   while leaving the generic pipeline constructor unchanged.
2. Implement `SampleOperationPipeline` execution with sample context coercion,
   step order preservation, output forwarding, and execution diagnostics.
3. Add public lazy export coverage for `SampleOperationPipeline`.
4. Add unit tests for sequence construction, ordered mapping construction,
   invalid entries, context propagation, output forwarding, missing-field and
   undeclared-mutation wrapping, and generic pipeline mapping regression.
5. Add contract/package tests for the public specialized-only API and import
   boundary expectations.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and import-boundary tests as
  needed.
- Required assertions or deferral reason: `SampleOperationPipeline` is
  importable from `rphys.ops` without importing heavy optional stacks or adding
  root `rphys` exports.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_pipelines.py` and/or a focused
  `tests/unit/rphys/ops/test_sample_pipeline.py`.
- Required assertions or deferral reason: sequence and ordered mapping order,
  immutable operations tuple, mapping diagnostic names, output forwarding,
  context identity/adaptation, invalid step rejection, raw callable rejection,
  tuple named-entry rejection, missing-field wrapping, undeclared mutation
  wrapping, and generic `OperationPipeline` mapping rejection.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_pipeline_contract.py` and/or
  a focused sample pipeline contract test.
- Required assertions or deferral reason: `SampleOperationPipeline` public
  construction forms are stable, generic pipeline remains sequence-only, and
  diagnostic names do not become operation identity or route policy.

### Integration Suite

- Status: deferred
- Expected paths: none required for this phase.
- Required assertions or deferral reason: individual sample-operation lazy
  boundaries are already covered by Phase 3/4 integration tests. Phase 5 only
  composes public steps without new IO, loader, or payload behavior.

### E2E Suite

- Status: deferred
- Expected paths: none.
- Required assertions or deferral reason: no end-to-end dataset, loader, model,
  trainer, or workflow behavior is in scope.

### Acceptance Suite

- Status: deferred
- Markers affected: none.
- Required assertions or deferral reason: no real datasets, hardware, GPU,
  network, benchmark, or opt-in workflow validation is required.

## Risks

- Reusing generic helpers could accidentally permit mappings in
  `OperationPipeline`.
- Mapping diagnostic names could be mistaken for operation identities, route
  labels, or durable artifact names.
- Context coercion could drop sample-specific replay fields if it converts a
  `SampleOperationContext` to generic context too early.
- Wrapping errors could hide important sample operation causes if the original
  exception is not preserved as `__cause__`.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_pipelines.py
uv run pytest tests/contracts/test_operation_pipeline_contract.py
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-package
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: pipeline internals first, public export second,
  unit tests third, contract/package tests fourth, docs/metadata last.
- Tests to run with each slice: focused unit tests after pipeline internals;
  package tests after exports; contract tests after public API behavior is
  wired; `git diff --check` before PR prep.
- Decisions the executor must not revisit: generic pipeline remains
  sequence-only; mapping keys are diagnostic only; no tuple named entries; no
  public helper records; no batch, loader, DAG, retry/resume, workflow, export,
  cache, trainer, or model behavior.
- Conditions that require stopping for the manager: implementation requires
  changing generic `OperationPipeline` mapping rejection, exposing public step
  descriptor helpers, adding workflow/router/graph semantics, accepting raw
  callables as pipeline steps, or importing heavy/backend modules.

## Refinement And Review Budget Status

- Phase execution plan refinement: unused / not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: completed in this artifact
- Implementation summary: implemented on 2026-05-15 in
  `agent/stage-7-p5-sample-pipeline`; added public
  `SampleOperationPipeline` with sequence and insertion-ordered mapping
  construction, private diagnostic step normalization, sample context
  propagation, output forwarding, step-aware execution diagnostics, and
  package exports while leaving generic `OperationPipeline` mapping rejection
  unchanged.
- Implementation validation: targeted
  `uv run pytest tests/unit/rphys/ops/test_pipelines.py tests/contracts/test_operation_pipeline_contract.py tests/package/test_import.py`,
  `make test-unit`, `make test-contract`, `make test-package`, `make
  validate-pr`, `make test-summary`, and `git diff --check` passed on
  2026-05-15. `make test-summary` reported 619 passing
  package/unit/contract/integration tests; e2e and acceptance suites are not
  present.
- Refinement summary: not needed
- Pre-submit blocker gate: completed; no generic mapping support, tuple named
  entries, public step helper leakage, batch behavior, workflow semantics, or
  heavy imports remain known.
- PR preparation: durable PR body drafted in
  `docs/roadmap/stage-7/phases/sample-pipeline-pr-body.md`
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

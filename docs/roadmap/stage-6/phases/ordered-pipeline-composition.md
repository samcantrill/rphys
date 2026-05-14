# Phase 3 Execution Plan: Ordered Pipeline Composition

## Metadata

- Status: draft phase execution plan; expanded-path refinement required before
  implementation
- Roadmap stage: `v6`
- Feature focus: Sequence-only generic operation pipeline composition
- Stage descriptor: Operation Foundations And Functional Kernels
- Phase descriptor: Ordered Pipeline Composition
- PR title: `Stage 6 Operation Foundations And Functional Kernels - Phase 3: Ordered Pipeline Composition`
- Branch: `agent/stage-6-p3-ordered-pipeline-composition`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p3-ordered-pipeline-composition`
- Phase execution plan path: `docs/roadmap/stage-6/phases/ordered-pipeline-composition.md`
- Full plan: `docs/roadmap/stage-6/implementation-plan.md`
- Planning document: `docs/roadmap/stage-6/planning.md`
- Source phase: Phase 3, `ordered-pipeline-composition`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after expanded-path refinement, automated review,
  local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: existing dedicated branch and worktree verified; do not
  create a new worktree
- Plan quality gate: Stage 6 implementation plan approved; draft pass completed
  with expanded-path refinement required because Phase 3 adds public pipeline
  construction, `OperationResult.output` forwarding semantics, step diagnostics,
  and Stage 7 step-naming pressure.
- Draft pass: completed 2026-05-14
- Refine pass: pending / required
- Setup limitations: no product code, tests, PR body, PR, broad checks, or new
  worktree created during this draft planning pass
- Blockers: expanded-path refinement must complete before implementation starts

## Objective

Add the generic `OperationPipeline` composition layer for Stage 6 as a narrow,
sequence-only wrapper over existing `Operation` execution: store an ordered tuple
of operations, validate adjacent declared output/input compatibility, propagate a
single `OperationContext` unchanged to every step, forward each step's
`OperationResult.output`, return the final `OperationResult`, and surface
pipeline failures with step index, operation name, and preserved cause.

## Full-Plan Context

Phase 1 established the public operation schema, context/result records, kernel
vocabulary, private validators, and initial operation errors. Phase 2 added the
concrete `Operation` wrapper, result-return execution, explicit `.output`
access, input/context/result validation, and cause-preserving operation errors.
Phase 3 is the first composition phase and must stay entirely generic. Phase 4
owns runtime-container/lazy-field examples and public docs expansion, and Phase
5 owns final stage-wide validation. Phase 3 must not introduce Stage 7
`SampleOp`/`BatchOp` semantics, export/save pipelines, workflow orchestration, or
named step APIs.

## Source Phase Summary

- Goal: add generic ordered `OperationPipeline` composition over approved
  operation/result behavior.
- Required scope: sequence-only construction; non-empty ordered tuple storage of
  concrete `Operation` instances; rejection of mappings, ordered mappings, named
  entries, and non-operation entries; adjacent declared output/input
  compatibility validation; unchanged context propagation; `result.output`
  forwarding; final `OperationResult` return; step-aware typed pipeline errors
  with zero-based step index, operation name, and cause where applicable.
- Required checkpoints: unit coverage for construction, ordering,
  compatibility, context propagation, result forwarding, and step diagnostics;
  contract coverage for public pipeline semantics and future-roadmap guardrails;
  package/import regression coverage for exports and lightweight boundaries;
  `git diff --check`.
- Acceptance criteria: pipelines reject unsupported construction forms, preserve
  order, propagate one context, validate declared compatibility, report
  step-aware validation/execution failures, return the last step's
  `OperationResult`, and leave mapping/named-entry construction, DAG/routing,
  retry/resume/workflow state, `SampleOpPipeline`, `BatchProgram`, export
  pipelines, and private helper APIs absent.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: current `develop` already
  includes `src/rphys/ops/contracts.py`, `context.py`, `kernels.py`, `core.py`,
  and private `_validation.py`. There is no `src/rphys/ops/pipelines.py` and no
  `OperationPipeline` export yet.
- Existing files or modules that constrain this phase: `Operation` is the only
  executable wrapper and exposes `name`, `contract`, `.run(input_value,
  context=None)`, and `__call__(input_value, context=None)`, both returning
  `OperationResult`.
- Existing files or modules that constrain this phase: `OperationContract`
  stores optional `input_type` and `output_type` as `type`,
  `tuple[type, ...]`, or `None`; Phase 3 compatibility must use these declared
  runtime type expectations without adding schema conversion, field locators, or
  richer type systems.
- Existing files or modules that constrain this phase: `OperationContext`
  contains only `metadata` and `provenance`; `OperationResult` contains `output`,
  `operation_name`, `role`, `metadata`, `provenance`, and
  `side_effect_evidence`. Pipeline execution must not add pipeline identity,
  step-result aggregation, cache keys, workflow state, or durable serialization.
- Existing files or modules that constrain this phase: `src/rphys/errors.py`
  currently has broad `RemotePhysPipelineError` but no concrete pipeline errors.
  Any concrete pipeline error must be exercised by Phase 3 public behavior and
  remain under `RemotePhysPipelineError`.
- Existing tests or harness behavior: `tests/package/test_import.py` asserts
  exact `rphys.ops.__all__`, focused submodule `__all__`, no root operation
  exports, and exact operation error exports. Phase 3 must update these only for
  implemented pipeline names and exercised concrete pipeline errors.
- Existing tests or harness behavior: `tests/package/test_import_boundaries.py`
  imports `rphys.ops`, `rphys.ops.contracts`, `rphys.ops.context`,
  `rphys.ops.core`, and `rphys.ops.kernels` in a subprocess and forbids heavy
  optional modules, `rphys.data`, `rphys.datasources`, `rphys.io`, codec modules,
  and `tests.support`. Phase 3 must extend this boundary to
  `rphys.ops.pipelines`.
- Existing tests or harness behavior: current unit and contract coverage exists
  for operation contracts, context/result records, kernels, and `Operation`
  execution. Phase 3 should add `tests/unit/rphys/ops/test_pipelines.py` and
  `tests/contracts/test_operation_pipeline_contract.py`.
- Import-boundary or dependency constraints: `rphys.ops.pipelines` and any
  private validators may use stdlib collection/typing utilities, existing
  `rphys.ops` public records, private local helpers, and `rphys.errors` only.
  They must not import data/runtime containers, datasource/index, IO/codec,
  optional numerical/video/deep-learning stacks, test support, workflow/artifact
  packages, or future Stage 7/8 modules.

## Phase Isolation State

- Control checkout dirty-state review: `git status --short --branch` showed a
  clean existing worktree on
  `agent/stage-6-p3-ordered-pipeline-composition` before this plan edit.
- Dedicated branch/worktree status: assigned branch and worktree verified at
  `/home/samcantrill/work/rphys-worktrees/stage-6-p3-ordered-pipeline-composition`;
  no new worktree was created.
- Current `develop` base: local `HEAD`, local `develop`, `origin/develop`, and
  merge-base with `develop` resolved to
  `87e4efaa49a102dab0f51ce51ee7ef79b8afa1b0` during the draft pass.
- Earlier phase dependency status: Phase 1 and Phase 2 are merged into the
  current base, including docs merge records and the code/test surfaces Phase 3
  depends on.
- Push/PR infrastructure status: not exercised in this planning pass.
- Stop condition if isolation cannot be maintained: stop before implementation
  if the worktree is not on the assigned branch, if unrelated dirty files appear
  in touched paths, if `develop` advances in a way that invalidates Phase 1/2
  assumptions, or if implementation pressure requires a new branch/worktree.

## In-Scope Work

- Add `OperationPipeline` as the only new public composition name, likely in
  `src/rphys/ops/pipelines.py`, and export it from `rphys.ops` only after it is
  implemented and tested.
- Accept only a single ordered sequence of concrete `Operation` objects; reject
  empty sequences, mappings, ordered mappings, named entries such as
  `(name, operation)` pairs, strings/bytes, and non-`Operation` entries.
- Store operations as an ordered tuple and expose only read-only inspection that
  does not create stable step names or mutable step state.
- Validate adjacent declared output/input compatibility using
  `OperationContract.output_type` from step `i` and `input_type` from step
  `i + 1` without coercion, schema adapters, or implicit conversion.
- Execute steps sequentially in stored order, using one resolved
  `OperationContext` object for every operation invocation.
- Forward each completed step's `OperationResult.output` as the next step's
  input; do not forward the whole result object unless it is itself the payload.
- Return the final step's `OperationResult` exactly as validated by that
  operation; do not synthesize a pipeline-level result, aggregate metadata, or
  collect per-step results in public state.
- Wrap construction, validation, and execution failures in exercised typed
  pipeline errors that subclass `RemotePhysPipelineError`, preserve the original
  exception as `__cause__` where applicable, and include zero-based step index,
  operation name, and cause type/context useful for diagnosis.
- Update package/import-boundary tests for `rphys.ops.pipelines`,
  `OperationPipeline`, and any exercised concrete pipeline errors.
- Add unit and contract tests for ordering, construction rejection, static
  compatibility checks, runtime mismatch wrapping, context object identity,
  `result.output` forwarding, final-result return, and absence of workflow/DAG
  and Stage 7/8 behavior.
- Add only concise docstrings/examples needed for public pipeline behavior and
  test readability; broader docs expansion belongs to Phase 4.

## Out-of-Scope Work

- Ordered mapping construction, named entries, stable step names, per-step name
  overrides, public step descriptor records, pipeline identity records, or
  provenance step traces.
- DAGs, routing, branching, fan-in/fan-out, dynamic dispatch, automatic retries,
  resume, checkpointing, workflow/artifact runtime integration, scheduling, or
  distributed execution.
- Per-step context overrides, context mutation/merging policy, hidden global
  context, workflow context, or automatic context synthesis beyond the single
  resolved `OperationContext` object.
- SampleOp, BatchOp, Transform, augmentation/check APIs, field-locator
  read/write/delete permissions, BatchProgram, `SampleOpPipeline`,
  `BatchOpPipeline`, export/save pipelines, datasource-derived pipelines, or
  runtime-container imports.
- Raw-output pipeline APIs, collection of all intermediate results, callback or
  hook systems, private helper public APIs, registries, symbolic lookup,
  `_target_` resolution, or public Protocol/base changes.
- Hidden schema conversion, output coercion, lazy field materialization policy,
  device movement, RNG/replay policy, cache/materialization identity, real
  datasets, concrete rPPG kernels, optional heavy dependencies, or broad docs.
- Root `rphys` re-exports, placeholder Stage 7/8 package names, unexercised
  concrete pipeline errors, private-helper tests/imports, PR body generation, or
  opening a PR in this planning phase.

## Assumptions

- `OperationPipeline` is a lightweight wrapper over existing `Operation`
  instances, not a base class, protocol, registry entry, or workflow object.
- The public constructor should stay narrow, e.g.
  `OperationPipeline(operations: Sequence[Operation])`, with no `name`, `steps`,
  `metadata`, `provenance`, `context`, retry, routing, cache, export, or
  workflow parameters.
- The pipeline must contain at least one operation because public execution
  returns the final step's `OperationResult`.
- Public inspection may expose an `operations` tuple. It must not expose mutable
  step state or stable named-step APIs.
- Static adjacent compatibility is checked only when both adjacent declarations
  are present. If either side omits a declared type, runtime validation by the
  next `Operation` remains the enforcement point.
- Static type compatibility follows normal Python runtime type semantics:
  every declared output type from the upstream step must be acceptable to the
  downstream step's declared input type using `issubclass`-style checks aligned
  with `isinstance` runtime validation.
- A single `OperationContext` object is resolved before execution. If callers
  omit context, the pipeline may create one empty `OperationContext()` once and
  pass that same object to every step; if callers provide context, object
  identity is preserved for every step.
- Runtime operation failures are wrapped by pipeline errors without discarding
  the original operation error or callable cause chain.
- Exact concrete pipeline error names are public API and must be confirmed in
  the required refinement pass before implementation. The draft expectation is a
  minimal exercised subset for invalid pipeline construction/compatibility and
  pipeline step execution failures only.

## Scope Contract

Phase 3 changes public behavior only by adding generic ordered pipeline
composition over existing Stage 6 operations. The only new `rphys.ops` public
name should be `OperationPipeline`, plus any exercised concrete pipeline error
names exposed from `rphys.errors`. No `SampleOp`, `BatchOp`, transform,
pipeline-name, export, workflow, registry, protocol/base, or root `rphys` export
is allowed.

`OperationPipeline` construction must accept ordered sequences only. Accepted
inputs are list/tuple-like sequences whose items are concrete `Operation`
instances. The constructor must copy the sequence into an immutable tuple in the
same order. It must fail loudly for mappings and ordered mappings even though
they preserve order, because Stage 7 owns named-entry pressure. It must also
fail for named pairs such as `("scale", operation)`, non-operation entries,
strings/bytes, and empty sequences. Rejections must raise a typed pipeline error
with structured context describing the field, expected shape, actual shape, and
step index when a specific entry is invalid.

Adjacent compatibility validation must inspect only declared runtime type
expectations. For every adjacent pair, if the upstream operation declares
`output_type` and the downstream operation declares `input_type`, the upstream
declared output set must be accepted by the downstream declared input set. A
declared `output_type=int` feeding `input_type=(int, float)` is compatible; a
declared `output_type=(int, str)` feeding `input_type=int` is incompatible
because one possible declared output is not accepted. If either adjacent type is
`None`, construction should not fail on that pair; the downstream operation's
normal runtime input validation still applies during execution. Compatibility
must not coerce values, inspect schemas, materialize lazy fields, move devices,
or infer container field semantics.

Pipeline execution must be sequential and transparent. `run(input_value,
context=None)` and `__call__(input_value, context=None)` should have matching
semantics and return the final `OperationResult`. The pipeline resolves one
`OperationContext` object before the first step, validates that provided context
is an `OperationContext`, and passes that exact object to each operation. Step
`0` receives the original `input_value`; each later step receives only the
previous step's `OperationResult.output`. The final result is the final step's
validated result, not a pipeline wrapper result or a collected result list.

Step diagnostics use zero-based tuple position plus `Operation.name`. Any
pipeline validation or execution error tied to a step must include
`step_index`, `operation_name`, and relevant `expected`/`actual` information.
When wrapping an operation error or callable failure, use exception chaining so
the original error remains available through `__cause__`; do not stringify and
drop causes. Static adjacent compatibility errors should identify both
operations where useful, including upstream step index/name and downstream step
index/name.

Pipeline public behavior must not imply workflow semantics. There is no
per-step context policy, retry, resume, routing, scheduling, artifact store,
cache key, export target, run identity, or persistent provenance trace. If the
implementation needs any of those to satisfy tests, stop for manager review.

## Required Refinement Topics

- Confirm the exact public constructor and execution signatures, including
  whether `OperationPipeline.run`/`__call__` allow omitted context by resolving a
  single empty `OperationContext()`.
- Confirm the exact static compatibility rule for tuple type expectations and
  subclass relationships, especially whether the rule requires every upstream
  possible output type to satisfy the downstream input expectation.
- Confirm the exact exercised concrete pipeline error names before editing
  `src/rphys/errors.py`; avoid adding unexercised placeholders.
- Confirm the public inspection surface, likely an `operations` tuple only, and
  explicitly reject pipeline names or step-name APIs until Stage 7 pressure.
- Pressure-test diagnostics wording and context keys so every step error carries
  step index, operation name, and cause without freezing Stage 7 named-entry
  semantics.

## Scientific Contract Notes

- Sampling and temporal alignment: Phase 3 may use synthetic primitive
  payloads, such as arithmetic or tiny signal-like tuples, but it introduces no
  sampling-rate, alignment, resampling, filtering, windowing, or temporal-slice
  scientific behavior.
- Field roles, locators, schemas, and provenance: pipeline compatibility uses
  generic declared Python runtime types only. It adds no field locator
  permissions, datasource identity, manifest fingerprints, schema conversion,
  cache keys, or provenance aggregation.
- Masking, filtering, normalization, and aggregation order: the only processing
  order defined by Phase 3 is operation sequence order. No numerical algorithm,
  filter ordering, normalization policy, or aggregation semantics are added.
- Subject identity, splits, leakage, and grouping: no subject, split, leakage,
  grouping, record, or dataset identity policy is introduced. Context metadata
  used in tests is synthetic runtime metadata, not a durable identity contract.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: Phase 3 handles pipeline construction errors, declared
  type incompatibility, invalid context objects, operation failures, and runtime
  input/result mismatches through typed pipeline diagnostics. It does not add
  signal quality, field-missing, temporal slicing, or numerical edge-case
  policy.

## Design Impact

- Maintainability: `OperationPipeline` belongs in a focused `pipelines.py`
  implementation-home module so composition logic stays separate from contracts,
  context/result records, kernels, and single-operation execution.
- Extensibility: sequence-only composition gives Stage 7 and Stage 8 a small
  reusable core while leaving named entries, specialized SampleOp/BatchOp
  classes, export pipelines, and workflow semantics additive.
- Lightweight import policy: `rphys.ops.pipelines` must stay stdlib plus
  existing `rphys.ops` public modules and `rphys.errors`; import-boundary tests
  must prove it does not load data, datasource, IO, codec, test-support,
  workflow/artifact, or heavy optional stacks.
- Source-tree boundaries: Phase 3 may touch `src/rphys/ops/pipelines.py`,
  `src/rphys/ops/__init__.py`, private `src/rphys/ops` validators if needed,
  `src/rphys/errors.py` only for exercised pipeline errors, package tests, unit
  ops/error tests, and operation pipeline contract tests.

## Future Compatibility

- Keep ordered mappings and named-entry construction absent so Stage 7 can add
  step naming only after SampleOp/BatchOp pressure proves the semantics.
- Keep diagnostics based on step index plus operation name so errors are useful
  without creating stable public step names.
- Keep pipeline execution as `OperationResult.output` forwarding so Stage 7/8
  pipelines inherit uniform result-return behavior without a raw-output API.
- Keep context propagation as one unchanged `OperationContext` object so later
  specialized contexts can wrap or extend behavior instead of reverse-engineering
  per-step merge policy.
- Keep compatibility validation based on declared generic runtime types so later
  locator/schema/RNG/export/cache contracts can layer on top without private
  helper dependencies.
- Keep concrete pipeline errors minimal and exercised so later operation
  families can add catchable failures without carrying unused Phase 3 taxonomy.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Accept ordered mappings or `(name, operation)` entries now | Stage 7 owns naming pressure; accepting them now would freeze step-name semantics too early. |
| Return a pipeline-level `OperationResult` with collected step metadata | Stage 6 locks result forwarding through step outputs and final result return; aggregation would imply workflow/provenance policy. |
| Forward whole `OperationResult` objects between steps | The approved execution contract says pipelines feed `result.output`; forwarding results would change operation input semantics. |
| Add retry, resume, DAG, or routing behavior | These are workflow/runtime concerns explicitly outside Stage 6 generic composition. |
| Import `Sample`, `Batch`, datasource, IO, or export modules for realistic examples | Phase 3 is generic and primitive; runtime-container examples belong to Phase 4 and specialized operation families belong to later stages. |
| Expose private compatibility helpers for downstream reuse | DD-10 requires helper behavior to remain private and tested through public APIs only. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Pipeline steps have no stable user-supplied names | Sequence-only Stage 6 avoids premature naming semantics before Stage 7. | Stage 7 `SampleOpPipeline`, export pipelines, or downstream users need explicit step names beyond index plus operation name. |
| Compatibility validation is limited to declared Python runtime types | Existing `OperationContract` intentionally avoids field locators, schemas, and domain contracts. | A later specialized operation family needs richer compatibility checks that cannot compose with generic type declarations. |
| Pipeline returns only the final step result | This preserves the approved `OperationResult` execution model and avoids hidden workflow trace policy. | Downstream users repeatedly need inspected intermediate results and an approved later API adds explicit trace/result collection semantics. |

## Reviewability

- Expected PR size and shape: small composition-focused PR adding one pipeline
  module, exact export updates, minimal exercised pipeline errors, and focused
  package/unit/contract tests.
- Files and areas to inspect: `src/rphys/ops/pipelines.py`,
  `src/rphys/ops/__init__.py`, private `src/rphys/ops/_validation.py` only if
  reused or extended, `src/rphys/errors.py`, `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`,
  `tests/unit/rphys/ops/test_pipelines.py`, `tests/unit/rphys/test_errors.py`,
  and `tests/contracts/test_operation_pipeline_contract.py`.
- Scope-control checks: `OperationPipeline` is the only new `rphys.ops`
  composition name; no mapping/named-entry construction; no step-name API; no
  DAG/routing/retry/resume/workflow behavior; no SampleOp/BatchOp/export
  pipelines; no raw-output API; no runtime-container, IO, datasource, codec,
  test-support, workflow, or heavy imports; no private helper exports/docs/tests;
  no unexercised public errors.

## Implementation Steps

1. Add `src/rphys/ops/pipelines.py` with a narrow `OperationPipeline` class,
   constructor validation for non-empty ordered sequences of concrete
   `Operation` instances, immutable tuple storage, read-only tuple inspection,
   and no pipeline/step naming fields.
2. Add private adjacent-compatibility validation using
   `OperationContract.output_type` and `input_type`, raising typed pipeline
   validation errors with zero-based upstream/downstream step context and no
   coercion, schema inspection, runtime-container imports, or public helper
   exposure.
3. Implement `.run(input_value, context=None)` and `__call__` parity with one
   resolved `OperationContext`, unchanged context object identity for every
   step, sequential execution, `OperationResult.output` forwarding, final
   `OperationResult` return, and step-aware wrapping of operation/context/result
   failures with preserved causes.
4. Add only exercised concrete pipeline errors under `RemotePhysPipelineError`
   after refinement confirms names, and update `rphys.errors.__all__`,
   inheritance tests, package export tests, and structured context assertions.
5. Update `rphys.ops` exports and import-boundary tests for
   `OperationPipeline` and `rphys.ops.pipelines`, keeping root `rphys` free of
   operation exports and forbidding data, datasource, IO, codec, test-support,
   workflow, and heavy optional imports.
6. Add unit and contract coverage for sequence-only construction, rejection of
   mappings/named entries/non-operations/empty sequences, order preservation,
   static and runtime compatibility failures, context propagation, output
   forwarding, final result return, step diagnostics, cause preservation, and
   explicit absence of Stage 7/8/workflow semantics.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`;
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` includes
  `OperationPipeline` plus the existing implemented Stage 6 names and no
  `SampleOp`, `BatchOp`, `Transform`, named-step, registry, workflow, export, or
  raw-output names; `rphys.ops.pipelines.__all__` exposes exactly
  `["OperationPipeline"]`; root `rphys` still does not re-export operation
  names; `rphys.errors.__all__` includes only exercised concrete pipeline errors
  after refinement confirms names; importing `rphys.ops.pipelines` does not load
  heavy optional modules, `rphys.data`, `rphys.datasources`, `rphys.io`, codec
  modules, `tests.support`, workflow/artifact packages, or Stage 7/8 modules.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_pipelines.py`;
  `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: constructor accepts lists/tuples of
  concrete `Operation` instances and stores an ordered tuple; constructor rejects
  empty sequences, mappings, ordered mappings, named pairs, strings/bytes,
  non-operation entries, and private helper exposure; adjacent declared
  `output_type`/`input_type` compatibility passes and fails according to refined
  type rules; `.run()` and `__call__` return the same final-result semantics;
  one `OperationContext` object identity reaches every step; each next step sees
  the previous step's `result.output`; step errors include zero-based step index,
  operation name, expected/actual details where useful, and preserved
  `__cause__`; concrete pipeline errors subclass `RemotePhysPipelineError` and
  keep `RemotePhysError.context`.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_pipeline_contract.py`
- Required assertions or deferral reason: public pipeline behavior is
  sequence-only and generic; operation order is preserved; unsupported mapping
  and named-entry construction is rejected; static adjacent compatibility and
  runtime mismatches fail loudly; explicit context is propagated unchanged; final
  return is the last `OperationResult`; users can rely on `result.output`
  forwarding; diagnostics identify step index and operation name while avoiding
  stable named-step semantics; no DAG/routing/retry/resume/workflow,
  SampleOp/BatchOp, export pipeline, raw-output, registry, public Protocol/base,
  or runtime-container behavior is present.

### Integration Suite

- Status: deferred for Phase 3
- Expected paths: none in this phase
- Required assertions or deferral reason: runtime-container and lazy-field
  boundary coverage belongs to Phase 4 after generic pipeline behavior is
  present. Phase 3 must stay primitive/generic and must not import `Sample`,
  `Batch`, `SampleField`, datasource/index, IO, or codec modules.

### E2E Suite

- Status: deferred for Phase 3
- Expected paths: none in this phase
- Required assertions or deferral reason: end-to-end workflows would imply
  runtime, datasource, export, or workflow orchestration. Phase 3 validates the
  public generic composition contract through package, unit, and contract tests.

### Acceptance Suite

- Status: deferred for Phase 3
- Markers affected: none
- Required assertions or deferral reason: no real datasets, hardware, GPU,
  network, optional dependency, long-running acceptance behavior, or user-facing
  workflow is involved in generic ordered pipeline composition.

## Risks

- Sequence-only construction may need additive named-step support soon in Stage
  7; accepting names now would lock semantics too early.
- Static type compatibility over `type | tuple[type, ...] | None` is useful but
  underpowered for later schema, locator, and export compatibility decisions.
- Step diagnostics must be helpful without smuggling in named entries,
  workflow IDs, or persistent trace semantics.
- Wrapping operation errors can obscure original causes unless exception
  chaining and structured context are tested carefully.
- Import-boundary regressions can slip in if compatibility helpers reuse data,
  IO, datasource, codec, or test-support utilities.
- Public concrete pipeline error names are hard to remove and must remain
  limited to exercised behavior.

## Validation Commands

Targeted development commands:

```sh
make test-package
make test-unit
make test-contract
git diff --check
```

Final PR-preparation commands:

```sh
make test-package
make test-unit
make test-contract
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: add the pipeline module and constructor/storage
  validation first; add compatibility validation second; add run/call execution
  and result forwarding third; add exercised pipeline errors fourth; update
  exports/import-boundary and public tests last.
- Tests to run with each slice: package tests after export/import-boundary edits;
  focused unit pipeline tests after constructor, compatibility, and execution
  behavior; unit error tests after any `errors.py` change; contract tests after
  public pipeline semantics settle.
- Decisions the executor must not revisit: sequence-only construction; reject
  mappings/named entries; store an ordered tuple of concrete `Operation`
  instances; no stable step names; validate adjacent declared compatibility only
  from `output_type` to `input_type`; propagate one `OperationContext` unchanged;
  forward `OperationResult.output`; return final `OperationResult`; step errors
  include zero-based index, operation name, and preserved cause; no DAG/routing,
  retry/resume/workflow, SampleOp/BatchOp/export, raw-output, registry,
  Protocol/base, runtime-container import, hidden schema conversion, or private
  helper public API.
- Conditions that require stopping for the manager: implementation needs
  ordered mappings, named entries, per-step context policy, pipeline-level
  metadata/provenance aggregation, intermediate result collection, DAG/routing,
  retry/resume/workflow state, runtime-container/import coupling, export/save
  behavior, schema/device/lazy-field conversion, public Protocol/base, raw-output
  API, unexercised public errors, or direct private-helper tests/docs.

## Refinement And Review Budget Status

- Phase execution plan refinement: required / pending
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed 2026-05-14 in the assigned worktree
- Final phase execution plan: pending; expanded-path refinement required before
  implementation
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending; must lock constructor/execution signatures,
  compatibility type rules, concrete pipeline error names, inspection surface,
  and step diagnostics before code edits
- Pre-submit blocker gate: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: expanded-path refinement is required before implementation

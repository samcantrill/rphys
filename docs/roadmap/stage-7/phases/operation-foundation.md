# Phase 1 Execution Plan: Operation Foundation Refactor

## Metadata

- Status: draft phase execution plan
- Roadmap stage: `v7`
- Feature focus: shared operation execution foundation for Stage 7 sample and
  batch operation families
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And
  Pipelines
- Phase descriptor: Operation Foundation Refactor
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 1: Operation Foundation Refactor`
- Branch: `agent/stage-7-p1-operation-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p1-operation-foundation`
- Phase execution plan path: `docs/roadmap/stage-7/phases/operation-foundation.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: `## Phase 1: Operation Foundation Refactor`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI
  pass
- Workflow path: expanded path because this intentionally refactors shared
  operation foundation code
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: refreshed gate passed and final maintainer approval
  recorded on 2026-05-15 in `docs/roadmap/stage-7/planning.md` and
  `docs/roadmap/stage-7/implementation-plan.md`
- Draft pass: expanded-path draft created in the existing manager-created
  worktree after inspecting Stage 7 planning, implementation plan, roadmap,
  glossary, operation source, package tests, unit tests, contract tests, and
  test suite layout
- Refine pass: not run; not needed unless reviewer finds a missing public API,
  scientific contract, import-boundary, dependency, serialization, provenance,
  compatibility, or cross-module risk in this artifact
- Setup limitations: GitHub auth/network and phase branch/worktree creation
  were manager-verified before this pass; this planner did not recreate or
  refetch the worktree
- Blockers: none

## Objective

Refactor the generic Stage 6 operation foundation around a public
`OperationStep` execution interface so generic and later specialized pipelines
can compose step objects without depending on concrete `Operation` instances,
while preserving Stage 6 user-visible semantics except for accepting broader
ordered sequence entries that satisfy `OperationStep`.

## Full-Plan Context

This is the first Stage 7 phase and is the prerequisite for all sample and
batch operation phases. It may clean up Stage 6 operation internals for a
cohesive execution path, but it must not implement sample contracts,
field-permission enforcement, stochastic augmentation, specialized ordered
mapping pipelines, batch equivalence, docs examples, or final broad validation.
Those remain in Phases 2 through 7.

Future phases depend on this phase for a stable step contract that can be used
by `SampleOperation`, `BatchOperation`, transforms, checks, augmentations, and
specialized pipelines. This phase must keep that foundation narrow enough that
later phases can add locator permissions, replay metadata, and batch
equivalence without inheriting registry, workflow, loader, cache, export, or
trainer policy.

## Source Phase Summary

- Goal: introduce `OperationStep`, make `Operation` satisfy it, and let
  generic `OperationPipeline` compose ordered step objects instead of concrete
  `Operation` instances only.
- Required scope: likely `src/rphys/ops/core.py`,
  `src/rphys/ops/pipelines.py`, `src/rphys/ops/__init__.py`, possibly focused
  operation errors in `src/rphys/errors.py`, public operation docstrings, and
  focused package, unit, and contract tests.
- Required checkpoints: `Operation` is an operation step; a minimal custom step
  composes in `OperationPipeline`; mappings, tuple named entries, text, raw
  callables, empty sequences, invalid context, compatibility failures, and step
  execution failures retain typed errors and useful diagnostics.
- Acceptance criteria: preserve `OperationResult`, `OperationContext`,
  `OperationContract`, wrapper-first callable behavior, result forwarding,
  adjacent contract compatibility checks, raw callable rejection, mapping
  rejection, tuple named-entry rejection, lightweight imports, and no registry
  or workflow behavior.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/ops/core.py` defines concrete `Operation` as a callable wrapper
  around `FunctionalKernel`, with `name`, `contract`, `run()`, `__call__()`,
  input/context validation, result normalization, side-effect evidence checks,
  and `OperationExecutionError` wrapping.
- `src/rphys/ops/pipelines.py` currently constrains
  `OperationPipeline(operations)` to `Sequence[Operation]`, rejects text,
  mappings, tuple named entries, raw callables, non-`Operation` objects, and
  empty sequences, stores an immutable `operations` tuple, validates adjacent
  `OperationContract` type compatibility, forwards each
  `OperationResult.output`, and wraps context or step failures as
  `OperationPipelineExecutionError`.
- `src/rphys/ops/contracts.py` and `src/rphys/ops/context.py` define the
  Stage 6 records that must remain stable: `OperationContract`,
  `OperationRole`, `OperationMutationPolicy`, `OperationContext`, and
  `OperationResult`.
- `src/rphys/ops/__init__.py` is the package export boundary for operation
  names; root `rphys` must not re-export operation names.
- Existing tests or harness behavior:
  `tests/unit/rphys/ops/test_core.py` and
  `tests/contracts/test_operation_execution_contract.py` lock wrapper-first
  operation construction, call signatures, context checks, input checks,
  output/result validation, side-effect evidence, and error wrapping.
- `tests/unit/rphys/ops/test_pipelines.py` and
  `tests/contracts/test_operation_pipeline_contract.py` lock pipeline
  constructor shape, sequence-only construction, immutable operations tuple,
  result forwarding, context identity reuse, mapping rejection, tuple
  named-entry rejection, non-operation rejection, compatibility errors, and
  step failure wrapping.
- `tests/contracts/test_operation_runtime_boundary_contract.py` proves generic
  operations treat `Sample` and `Batch` as ordinary payloads and do not
  materialize lazy `SampleField` values except when kernel code demands
  payload access.
- `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py` lock `rphys.ops` public exports,
  submodule `__all__` values, no root re-exports, and lightweight imports that
  avoid heavy optional modules such as NumPy, pandas, SciPy, OpenCV,
  matplotlib, AV, and torch.
- Import-boundary or dependency constraints: this phase must not add heavy
  optional dependencies, datasource scanning, test-support imports in package
  code, `loom` coupling, registries, symbolic operation names, graph execution,
  retry/resume behavior, cache/export identifiers, loader policy, or trainer
  policy.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is on
  `develop...origin/develop` with unrelated untracked `docs/roadmap/stage-8/`;
  it was inspected only for status and left untouched.
- Dedicated branch/worktree status: worktree is
  `/home/samcantrill/work/rphys-worktrees/stage-7-p1-operation-foundation` on
  `agent/stage-7-p1-operation-foundation`; it was clean before this plan file
  was created.
- Current `develop` base: `33de900 docs: updated approval for implementation`.
- Earlier phase dependency status: none; this is the first Stage 7 phase.
- Push/PR infrastructure status: manager verified GitHub auth/network, remote
  `develop`, branch, and worktree before assignment.
- Stop condition if isolation cannot be maintained: stop and ask the manager
  before editing the control checkout, rebasing onto an unverified base,
  combining phases, or committing files beyond this phase execution plan in the
  planning pass.

## In-Scope Work

- Add a public, dependency-light `OperationStep` execution interface, likely in
  the smallest coherent operation module location, and export it through
  `rphys.ops` without adding root `rphys` exports.
- Define the step interface around the existing public generic execution
  contract: inspectable `name`, inspectable `contract`, and
  `run(input_value, context=None) -> OperationResult`.
- Make `Operation` satisfy `OperationStep` while preserving its constructor,
  callable-first wrapper model, `run()` behavior, `__call__()` behavior,
  result normalization, context handling, and typed failures.
- Update generic `OperationPipeline` to accept ordered sequences of
  `OperationStep` objects while preserving all sequence-only construction and
  execution semantics except the approved broader step item type.
- Preserve or improve invalid-step diagnostics for text, mappings, tuple named
  entries, raw callables, non-step objects, empty sequences, invalid context,
  adjacent compatibility failures, and step execution failures.
- Add package, unit, and contract coverage that proves `OperationStep`
  behavior, `Operation` compatibility, minimal custom step composition, raw
  callable rejection, mapping rejection, tuple named-entry rejection, Stage 6
  semantic regression preservation, and lightweight imports.
- Update public module docstrings and focused operation docstrings so ordinary
  user extensions remain callable-first through `Operation` or later
  specialized wrappers, while direct `OperationStep` implementation is the
  advanced adapter path.

## Out-of-Scope Work

- `SampleOperation`, `SampleTransform`, `SampleAugmentation`, `SampleCheck`,
  `SampleOperationContext`, sample locator permissions, sample mutation
  enforcement, sample route/check records, or sample pipeline mapping support.
- `BatchOperation`, `BatchTransform`, `BatchAugmentation`,
  `BatchOperationContext`, batch equivalence reports, dtype/device behavior,
  batch parameter scopes, or batch pipeline mapping support.
- Raw callable acceptance in `OperationPipeline`.
- Mapping, tuple named-entry, graph, DAG, retry, resume, branch, route, split,
  loader, trainer, workflow, export, cache, artifact, or persistence behavior
  in generic `OperationPipeline`.
- Changes to `OperationResult`, generic `OperationContext`, generic
  `OperationContract`, mutation policy semantics, side-effect semantics,
  failure-mode semantics, or lazy `SampleField` materialization behavior.
- New concrete physiological algorithms, CHROM/POS/POS-like kernels, model
  input formatting, `DataLoader` adapters, backend device movement, broad
  `BatchProgram`, root `rphys` exports, placeholder future modules, or heavy
  optional imports.

## Assumptions

- Stage 6 source and tests are the compatibility baseline for this phase.
- The only accepted user-visible Stage 6 behavior change is that ordered
  `OperationPipeline` sequence entries may be `OperationStep` objects, not only
  concrete `Operation` instances.
- A minimal public step interface is enough for later Stage 7 wrappers; if
  implementation needs durable step IDs, registries, symbolic names, graph
  edges, workflow provenance, cache/export identity, or loader/trainer policy,
  the phase must stop.
- Direct `OperationStep` implementation is an advanced adapter path. Ordinary
  custom behavior remains callable-first through `Operation` in this phase and
  through specialized wrappers in later phases.
- No dependency metadata change is expected. Any dependency addition is a
  stop-and-review condition.

## Scope Contract

The executor must define `OperationStep` as a public operation execution
interface, not a workflow abstraction. A valid step must expose:

- `name`: a non-empty operation name used for diagnostics.
- `contract`: an `OperationContract` used for adjacent compatibility checks.
- `run(input_value, context=None) -> OperationResult`: execution that returns
  the existing `OperationResult` record.

`Operation` must remain the ordinary wrapper-first public implementation. Its
constructor remains `Operation(function, *, name=None, contract=None)`, and
`run()`/`__call__()` continue to accept `input_value` plus optional
`OperationContext`, coerce missing context to an empty `OperationContext`,
validate required metadata keys and input/output types, normalize bare outputs
to `OperationResult`, preserve explicit `OperationResult` metadata/provenance,
validate side-effect evidence, and wrap callable exceptions as
`OperationExecutionError`.

`OperationPipeline` remains generic and sequence-only. It may accept ordered
`Sequence[OperationStep]` and expose `operations` as an immutable tuple of
accepted step objects. It must continue to reject text inputs, mappings and
ordered mappings, tuple named entries, raw callables, arbitrary non-step
objects, and empty sequences with `InvalidOperationPipelineError`. It must
continue to coerce one pipeline context per run, preserve explicit context
identity across steps, validate adjacent type compatibility through each
step's `OperationContract`, forward each step's `OperationResult.output`, and
wrap context and step execution failures in `OperationPipelineExecutionError`
with inspectable step diagnostics.

No public contract change is in scope for `OperationResult`, `OperationContext`,
`OperationContract`, `OperationRole`, `OperationMutationPolicy`, or
`FunctionalKernel`.

## Scientific Contract Notes

- Sampling and temporal alignment: this phase is payload-agnostic and must not
  interpret sampling rates, timestamps, temporal slices, masks, or alignment.
  Such semantics remain owned by later sample/batch operation contracts and
  user kernels.
- Field roles, locators, schemas, and provenance: generic operations must
  continue to treat `Sample`, `Batch`, `FieldLocator`, and lazy fields as
  ordinary payloads. Operation metadata and provenance remain the runtime
  `OperationContext` and `OperationResult` mappings, not durable cache/export
  identities.
- Masking, filtering, normalization, and aggregation order: no filtering,
  normalization, aggregation, or physiological transform order is introduced
  here. Pipeline order remains the explicit ordered sequence supplied by the
  caller.
- Subject identity, splits, leakage, and grouping: this phase must not inspect
  or decide subject IDs, split assignment, grouping, routing, drops, retries,
  or loader policy.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: generic operation foundation code must not special-case
  these scientific data conditions. Failure behavior remains either declared
  Python type validation, context validation, step-raised errors wrapped by the
  operation/pipeline, or later specialized contracts.

## Design Impact

- Maintainability: the shared step interface should remove the concrete
  `Operation` dependency from generic pipeline composition while keeping result
  forwarding and compatibility checks in one foundation path for later
  sample/batch wrappers.
- Extensibility: later `SampleOperation` and `BatchOperation` classes can
  implement the same step interface without generic pipeline changes; direct
  third-party step implementations remain possible for advanced adapters.
- Lightweight import policy: use standard-library typing/collections only.
  Avoid optional numerical, video, plotting, dataset, deep-learning, or test
  support imports from package code.
- Source-tree boundaries: keep generic operation foundation under
  `src/rphys/ops`; do not add `rphys.transforms`, root exports, datasource
  package coupling, trainer/model coupling, or placeholder Stage 7 modules in
  this phase.

## Future Compatibility

- Phase 2 can introduce sample operation foundations as concrete wrappers over
  `OperationStep` without changing generic result/context/contract records.
- Phases 3 and 4 can add locator permissions, mutation checks, deterministic
  checks, augmentation params, replay evidence, and view writes without
  revisiting generic pipeline construction.
- Phase 5 can add specialized sample pipeline sequence/mapping diagnostics
  without changing generic `OperationPipeline` mapping rejection.
- Phase 6 can add provisional batch operation wrappers and equivalence records
  over the same step interface without adding backend dependencies or model
  layout policy.
- Stage 8/9 export, materialization, loader, cache, and batch planning remain
  deferred; `OperationStep` must not become their durable identity or policy
  carrier.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Keep `OperationPipeline` restricted to concrete `Operation` instances. | Blocks the approved Stage 7 foundation refactor and would force later sample/batch adapters to duplicate generic execution logic or inherit from `Operation` for the wrong reason. |
| Accept raw callables as pipeline steps. | Rejected by DD-1 and Stage 6 compatibility guardrails because raw callables do not expose `name`, `contract`, or reliable `OperationResult` behavior. |
| Add a registry or symbolic operation-name system with `OperationStep`. | Out of scope and would introduce global state and workflow policy before any domain contract requires it. |
| Change `OperationResult`, `OperationContext`, or `OperationContract` to fit the new interface. | Explicit DD-1 reopen trigger; later phases rely on those Stage 6 records as stable prerequisite behavior. |
| Add generic mapping/named-entry support to `OperationPipeline`. | Reserved for specialized sample/batch pipelines in later phases; generic mapping rejection is a locked compatibility guardrail. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None expected. | Phase 1 should complete with a code-backed public interface and tests, not placeholders. | Any temporary helper, undocumented private behavior dependency, or skipped test must be recorded in the PR and revisited before Phase 2. |

## Reviewability

- Expected PR size and shape: small to moderate shared foundation PR touching
  generic ops source, focused docs/docstrings, and package/unit/contract tests.
  No sample, batch, augmentation, loader, trainer, export, cache, or algorithm
  implementation should appear.
- Files and areas to inspect:
  `src/rphys/ops/core.py`, `src/rphys/ops/pipelines.py`,
  `src/rphys/ops/__init__.py`, `src/rphys/ops/contracts.py`,
  `src/rphys/ops/context.py`, `src/rphys/errors.py` only if a focused typed
  error addition is unavoidable, `tests/unit/rphys/ops/test_core.py`,
  `tests/unit/rphys/ops/test_pipelines.py`,
  `tests/contracts/test_operation_execution_contract.py`,
  `tests/contracts/test_operation_pipeline_contract.py`,
  `tests/contracts/test_operation_runtime_boundary_contract.py`,
  `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`, and relevant operation docstrings.
- Scope-control checks: no new public sample/batch operation names, no raw
  callable pipeline acceptance, no mapping support in generic pipelines, no
  changes to generic result/context/contract schemas, no root exports, no heavy
  imports, and no registry/workflow/cache/export identifiers.

## Implementation Steps

1. Add and export the `OperationStep` interface.
   Place it in the smallest coherent generic ops module, keep it
   dependency-light, require `name`, `contract`, and `run(...) ->
   OperationResult`, export it from the module and `rphys.ops`, and update
   package export tests. Prefer a runtime-checkable structural interface or a
   private validation helper only where needed for precise pipeline diagnostics.
2. Make `Operation` explicitly satisfy the step contract without changing
   callable-wrapper behavior.
   Update typing/docstrings and add unit/contract assertions that an
   `Operation` satisfies `OperationStep`, while preserving constructor,
   `run()`, `__call__()`, result normalization, metadata/provenance handling,
   side-effect evidence validation, and error wrapping tests.
3. Refactor `OperationPipeline` validation from concrete operation checks to
   step checks.
   Keep the constructor one-argument and sequence-only, update accepted entry
   validation to `OperationStep`, preserve rejection branches and error
   contexts for text, mappings, tuple named entries, raw callables, arbitrary
   non-step objects, and empty sequences, and update signature/export tests.
4. Preserve execution and compatibility semantics through the new step path.
   Keep one context per run, adjacent `OperationContract` type compatibility,
   ordered result-output forwarding, final `OperationResult` return shape, and
   step-aware `OperationPipelineExecutionError` wrapping. Add a minimal custom
   step fixture proving direct advanced adapters compose without being concrete
   `Operation` instances.
5. Tighten documentation and regression coverage.
   Update `rphys.ops` and relevant class docstrings to identify
   `OperationStep` as the composition interface, `Operation` as the ordinary
   callable-first extension path, and direct step implementation as advanced.
   Extend package, unit, and contract tests for import boundaries, public API,
   custom step composition, raw callable rejection, mapping rejection, tuple
   named-entry rejection, lazy runtime-boundary preservation, and no workflow
   surface.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` and relevant
  submodule `__all__` include `OperationStep`; root `rphys` still does not
  re-export operation names; importing `rphys.ops` and lightweight packages does
  not load heavy optional modules; no generic workflow/artifact runtime package
  appears.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_core.py` and
  `tests/unit/rphys/ops/test_pipelines.py`
- Required assertions or deferral reason: `Operation` satisfies
  `OperationStep`; `Operation` constructor/run/call behavior is unchanged;
  `OperationPipeline` signature reflects ordered operation-step sequences;
  `operations` remains immutable; a minimal custom step composes; text,
  mappings, ordered mappings, tuple named entries, raw callables, non-step
  objects, and empty sequences are rejected; adjacent type compatibility and
  step failure diagnostics remain intact.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_operation_execution_contract.py`,
  `tests/contracts/test_operation_pipeline_contract.py`,
  `tests/contracts/test_operation_runtime_boundary_contract.py`, and a focused
  operation-step contract test if that keeps the public interface clearer than
  extending existing files.
- Required assertions or deferral reason: public `OperationStep` exposes only
  execution-interface behavior; `Operation` remains callable-first and returns
  `OperationResult`; generic pipeline remains sequence-only with no stable
  pipeline names, no raw-output API, no mapping support, no route/retry
  behavior, and no workflow policy; custom step composition preserves final
  `OperationResult`; `Sample`/`Batch` payloads and lazy `SampleField`
  materialization behavior remain unchanged.

### Integration Suite

- Status: deferred for this phase
- Expected paths: none expected under `tests/integration`
- Required assertions or deferral reason: Phase 1 changes generic operation
  foundation behavior covered by package, unit, and contract suites. Add or run
  integration coverage only if the implementation reaches across multiple
  non-ops components beyond the existing runtime-boundary contract test.

### E2E Suite

- Status: deferred for this phase
- Expected paths: none expected under `tests/e2e`
- Required assertions or deferral reason: no end-to-end user workflow, dataset
  flow, export/materialization flow, loader/trainer flow, or sample/batch
  operation family is implemented in Phase 1. E2E coverage belongs to later
  phases if public workflows emerge.

### Acceptance Suite

- Status: deferred for this phase
- Markers affected: none
- Required assertions or deferral reason: no real dataset, hardware, GPU,
  network, optional dependency, or long-running validation is required or
  allowed for this foundation refactor.

## Risks

- A broad foundation refactor could accidentally change Stage 6 behavior that
  later phases rely on.
- A structural step check could accept objects that look callable but do not
  provide a valid `OperationContract` or `OperationResult` path unless tests
  cover invalid shapes.
- Documentation could overstate direct `OperationStep` implementation and
  encourage users to bypass callable-first wrappers.
- Adding the interface in the wrong module could create circular imports or
  expand the public surface beyond code-backed behavior.
- Pipeline diagnostics could get weaker when moving from concrete
  `Operation` checks to structural step validation.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py
uv run pytest tests/contracts/test_operation_execution_contract.py tests/contracts/test_operation_pipeline_contract.py tests/contracts/test_operation_runtime_boundary_contract.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-unit
make test-contract
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

`uv lock --check` is not expected to be necessary because this phase should not
change dependencies. If dependency metadata changes despite the stop condition,
run `uv lock --check` and record the reason.

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: add/export `OperationStep`; adapt `Operation`;
  adapt `OperationPipeline` validation; add custom-step and regression tests;
  update focused docstrings and package import tests.
- Tests to run with each slice: run focused unit tests after `Operation` or
  pipeline edits, focused contract tests after public behavior edits, and
  package import tests after export/docstring/import-boundary edits. Finish
  with `make test-unit`, `make test-contract`, `make test-package`, and
  `git diff --check`; prepare the PR with `make validate-pr`,
  `make test-summary`, and `git diff --check`.
- Decisions the executor must not revisit: keep `OperationResult`,
  `OperationContext`, and `OperationContract` semantics stable; keep
  callable-first wrappers as the ordinary user extension path; keep generic
  `OperationPipeline` sequence-only; keep raw callables, mappings, and tuple
  named entries rejected; keep root exports empty; keep heavy optional
  dependencies out.
- Conditions that require stopping for the manager: implementation requires
  changing generic result/context/contract records, accepting raw callables,
  changing mapping rejection, adding generic workflow/registry/cache/export
  policy, adding dependencies, changing lazy `SampleField` behavior, or
  implementing sample/batch operation families before Phase 1 is merged.

## Refinement And Review Budget Status

- Phase execution plan refinement: unused / not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: created in
  `docs/roadmap/stage-7/phases/operation-foundation.md` for Phase 1 only
- Final phase execution plan: pending implementation handoff review
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: not needed for this draft
- Pre-submit blocker gate: pending implementation
- PR preparation: pending implementation
- Automated review: pending implementation PR
- Merge result: pending
- Cleanup: pending after merge
- Remaining blockers: none

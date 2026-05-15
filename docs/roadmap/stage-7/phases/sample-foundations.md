# Phase 2 Execution Plan: Sample Operation Public Foundations

## Metadata

- Status: draft phase execution plan
- Roadmap stage: `v7`
- Feature focus: code-backed public sample operation foundation over `Sample`
  containers, parsed `FieldLocator` declarations, and Stage 6
  `OperationStep` execution
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And
  Pipelines
- Phase descriptor: Sample Operation Public Foundations
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 2: Sample Operation Public Foundations`
- Branch: `agent/stage-7-p2-sample-foundations`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p2-sample-foundations`
- Phase execution plan path:
  `docs/roadmap/stage-7/phases/sample-foundations.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: `## Phase 2: Sample Operation Public Foundations`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI
  pass during the implementation workflow
- Workflow path: fast path unless implementation discovers an operation-step
  adapter conflict
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed for the implementation pass
- Plan quality gate: refreshed gate passed and final maintainer approval
  recorded in `docs/roadmap/stage-7/planning.md` and
  `docs/roadmap/stage-7/implementation-plan.md`
- Draft pass: fast-path plan created in the existing dedicated worktree after
  inspecting Stage 7 planning, the implementation plan, Phase 1 completion,
  roadmap/glossary guidance, current operation/data source, package tests,
  unit tests, contract tests, and test suite layout
- Refine pass: not needed; no operation-step adapter conflict was found during
  planning
- Setup limitations: GitHub auth, remote `develop`, branch, and push/PR
  infrastructure were manager-verified; this pass did not refetch, recreate the
  worktree, open a PR, or modify the control checkout
- Blockers: none

## Objective

Establish the first code-backed public `SampleOperation` foundation: immutable
sample contract records with parsed locator declarations, dependency-light
sample context/replay records, required-field preflight, and callable-first
`OperationStep` adaptation that returns Stage 6 `OperationResult` without
expanding generic operation contracts.

## Full-Plan Context

Phase 1 merged the public `OperationStep` foundation and broadened generic
`OperationPipeline` sequence entries while preserving Stage 6 result, context,
contract, mapping-rejection, raw-callable rejection, and error behavior. This
phase consumes that foundation to create the sample operation base and public
record shapes only.

Later phases depend on these records for mutation enforcement, transforms,
checks, augmentations, specialized sample pipelines, and provisional batch
operations. Those later behaviors must not leak into this phase: no snapshot
field-effect enforcement, no `SampleTransform`, no `SampleCheck`, no
augmentation parameter sampling/application, no `SampleOperationPipeline`, no
batch APIs, and no export/cache/loader/trainer/workflow policy.

## Source Phase Summary

- Goal: establish the code-backed public sample operation foundation without
  mutation enforcement beyond base declaration and required-read validation.
- Required scope: `src/rphys/ops/sample.py`, `src/rphys/ops/__init__.py`,
  focused public docstrings, package/unit/contract tests, and only exercised
  error additions if existing typed errors are insufficient.
- Required checkpoints: public full names are code-backed only when
  implemented; locator declarations parse through `FieldLocator`; contract,
  context, and replay records are immutable and inspectable; required-field
  preflight uses non-payload `Sample.has()`/`field_items()` style access; and
  `SampleOperation` is accepted anywhere an `OperationStep` is valid.
- Acceptance criteria: preserve `OperationResult`, `.run()`, `__call__`,
  `name`, `contract`, generic pipeline compatibility checks, and typed failure
  behavior; keep specialized contracts separate from generic
  `OperationContract`; add no shorthand aliases, root `rphys` exports,
  placeholder future names, registries, or heavy imports.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/rphys/ops/core.py`
  defines public `OperationStep` with `name`, `contract`, and
  `run(input_value, context=None) -> OperationResult`; `Operation` remains the
  ordinary callable-first wrapper; `src/rphys/ops/pipelines.py` validates
  `OperationStep` entries structurally and still rejects mappings, tuple named
  entries, raw callables, text, and empty sequences.
- `src/rphys/ops/contracts.py` and `src/rphys/ops/context.py` define the
  generic Stage 6 records that must not be expanded for sample permissions:
  `OperationContract`, `OperationContext`, `OperationResult`,
  `OperationRole`, and `OperationMutationPolicy`.
- `src/rphys/data/containers.py` exposes `Sample.has()`, `field()`, `get()`,
  `require()`, `set_field()`, `delete_field()`, `rename_field()`,
  `field_items()`, `shallow_copy()`, and `deep_copy()`. `has()`, `field()`, and
  `field_items()` preserve lazy handles; `get()` and `require()` may materialize
  payloads.
- `src/rphys/data/locators.py` parses `<role>/<data-key>[#<metadata-key>]` and
  keeps locators as addresses only. Sample operation policy must live in
  `rphys.ops.sample`, not in `FieldLocator`.
- Existing tests or harness behavior: package tests lock `rphys.ops.__all__`,
  submodule `__all__`, no root re-exports, and no heavy optional imports from
  operation modules. Unit and contract tests lock Stage 6 execution/result
  semantics, `OperationStep` compatibility, generic pipeline mapping
  rejection, and lazy-field non-materialization boundaries.
- Import-boundary or dependency constraints: `rphys.ops.sample` may import
  Stage 6 operation primitives plus `Sample` and `FieldLocator`; it must not
  import NumPy, torch, OpenCV, PyAV, scipy, pandas, plotting stacks,
  datasource builders, loader/cache/export modules, model/trainer modules, or
  `tests.support`.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is on
  `develop...origin/develop` with unrelated untracked `docs/roadmap/stage-8/`;
  it was inspected only for status and left untouched.
- Dedicated branch/worktree status:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p2-sample-foundations` is on
  `agent/stage-7-p2-sample-foundations...origin/develop` and was clean before
  this plan file was created.
- Current `develop` base: `d59dc6627a25`; local `develop`, `origin/develop`,
  and this worktree `HEAD` all resolve to that merge-metadata commit.
- Earlier phase dependency status: Phase 1 merged to `develop` at
  `4c693336ad12eb8db381795963ef7bcb58a0a4a7`; merge metadata was pushed in
  `d59dc66`.
- Push/PR infrastructure status: manager verified GitHub auth and remote
  `develop`; this planning pass did not push or open a PR.
- Stop condition if isolation cannot be maintained: stop before editing the
  control checkout, committing product code during the planning pass, rebasing
  onto an unverified base, broadening into later phases, or committing files
  beyond this phase execution plan.

## In-Scope Work

- Add `rphys.ops.sample` with public, code-backed `SampleOperation`,
  `SampleOperationContract`, `SampleFieldPermissions`,
  `SampleOperationContext`, and a minimal immutable `SampleReplayRecord` or
  equivalent replay/context runtime-evidence record needed by the base.
- Make `SampleOperation` the ordinary callable-first sample adapter over
  `Sample -> Sample` callables while satisfying public `OperationStep`.
- Expose an adapted generic `OperationContract` through
  `SampleOperation.contract` with `input_type=Sample` and `output_type=Sample`;
  keep the richer sample contract separately inspectable, for example through
  `SampleOperation.sample_contract`.
- Normalize all field declarations from `FieldLocator | str` into immutable
  tuples of parsed `FieldLocator` objects during contract construction.
- Validate malformed locators, duplicate declarations, and contradictory
  read/write/delete declarations that would make later enforcement ambiguous.
- Implement required-read preflight before callable invocation using
  non-payload access (`Sample.has()` or equivalent), raising typed failures for
  missing declared reads without materializing `SampleField` payloads.
- Coerce `None`, `OperationContext`, and `SampleOperationContext` execution
  contexts into a dependency-light `SampleOperationContext`, and adapt it back
  to generic `OperationContext` metadata/provenance for `OperationResult`.
- Normalize callable return values so bare `Sample` outputs become
  `OperationResult` and explicit `OperationResult` outputs are validated for
  operation name, generic role, output type, and sample output identity/type.
- Re-export implemented sample public names from `rphys.ops` only; update
  package tests for code-backed names and root-export absence.
- Reuse existing typed errors where they describe the failure accurately, and
  add concrete sample-specific error classes only if tests exercise distinct
  catchable semantics.

## Out-of-Scope Work

- `SampleTransform`, `SampleCheck`, `SampleDecision`, `SampleRoute`,
  `SampleAugmentation`, augmentation params, `sample_params()`,
  `apply_params()`, linked fields, self-supervised view writes, and
  deterministic check/report behavior.
- Snapshot mutation enforcement, before/after `field_items()` comparisons,
  same-locator `FieldValue` replacement detection, declared write/delete
  enforcement, dynamic-write enforcement, explicit shallow/deep copy execution
  modes, and payload-internal mutation examples.
- `SampleOperationPipeline`, ordered mapping support, step normalization
  records, mapping-key diagnostics, route/drop behavior, DAGs, retries, resume,
  workflow stages, DataLoader orchestration, and generic
  `OperationPipeline` constructor changes.
- `BatchOperation`, `BatchTransform`, `BatchAugmentation`,
  `BatchOperationContext`, `BatchOperationPipeline`, batch equivalence reports,
  dtype/device declarations, collation policy changes, and model tuple layouts.
- Durable replay serialization, export/cache identity, file writing,
  datasource scanning/filtering/splitting, loader policy, trainer policy,
  backend device movement, concrete physiological algorithms, root `rphys`
  exports, shorthand `SampleOp` aliases, public registries, and placeholder
  future APIs.

## Assumptions

- Phase 1's `OperationStep` behavior is the compatibility baseline; this phase
  does not need to change `OperationStep`, `Operation`, generic
  `OperationPipeline`, `OperationResult`, generic `OperationContext`, or
  generic `OperationContract`.
- `OperationRole.GENERIC` remains the adapted generic role for
  `SampleOperation` results in this phase; specialized sample semantics live in
  sample contract/context records rather than expanding the generic enum.
- Missing required field preflight can use `Sample.has()` with parsed
  `FieldLocator`s and does not require payload access or `Sample.require()`.
- Dynamic field permissions can be declared in an inspectable, immutable shape
  now, but enforcement and view-family behavior are deferred to later phases.
- No dependency metadata change is expected. Any dependency addition is a
  stop-and-review condition.

## Scope Contract

The executor must treat `SampleOperation` as a public sample-specialized
`OperationStep` adapter, not as a registry, pipeline, transform catalog, or
workflow runtime. A valid `SampleOperation` exposes:

- `name`: non-empty local diagnostic name inferred from the wrapped callable or
  set explicitly.
- `sample_contract`: immutable `SampleOperationContract` containing
  `SampleFieldPermissions`, required context keys, failure modes, and
  runtime-only metadata/provenance declarations needed by the base.
- `contract`: an adapted generic `OperationContract` for compatibility checks,
  with `input_type=Sample`, `output_type=Sample`, Stage 6 mutation/result
  semantics, and no sample-specific fields added to the generic record.
- `run(input_value, context=None) -> OperationResult`: validates `input_value`
  is a `Sample`, coerces context, preflights declared reads without loading
  payloads, calls the wrapped callable with a `SampleOperationContext`,
  normalizes bare `Sample` output to `OperationResult`, and validates explicit
  `OperationResult` output.
- `__call__`: same semantics as `run()`.

`SampleFieldPermissions` must normalize declaration inputs to immutable parsed
locators and keep declaration categories inspectable. The initial required
categories are reads, writes, deletes, and dynamic-write allowances. Reads
drive Phase 2 preflight. Writes/deletes/dynamic declarations are public
contract data for later phases but must not be enforced yet beyond
construction-time validation for malformed or contradictory declarations.

`SampleOperationContext` must remain dependency-light and adaptable to generic
`OperationContext`. It should preserve user metadata/provenance mappings and
carry typed reproducibility fields approved by DD-4: run seed, epoch, worker
id, item id, sample id, operation index, operation name, view name, and an
optional caller-provided RNG stream object. It must not require NumPy, torch,
or any backend-specific RNG type. `SampleReplayRecord` or the chosen equivalent
record must be immutable runtime evidence only; it is not a durable
serialization schema, cache key, export manifest, or loader identity.

Errors must stay fail-loud and typed. Malformed locator declarations should
surface through `InvalidFieldLocatorError` or `InvalidOperationContractError`
with operation/field context. Invalid contexts should use
`InvalidOperationContextError`. Non-`Sample` input should use
`InvalidOperationInputError`. Missing declared reads may use `MissingFieldError`
with operation/locator context unless implementation adds and tests a narrower
sample-operation error. Callable failures should remain wrapped as
`OperationExecutionError`. Invalid explicit results should use
`InvalidOperationResultError`.

No public contract change is in scope for `OperationStep`, `Operation`,
`OperationPipeline`, `OperationResult`, `OperationContext`,
`OperationContract`, `OperationRole`, `OperationMutationPolicy`,
`FieldLocator`, `Sample`, `SampleField`, or `FieldValue`.

## Scientific Contract Notes

- Sampling and temporal alignment: this phase does not inspect, resample,
  slice, filter, normalize, mask, pad, or aggregate payloads. Context fields
  such as epoch, worker id, item id, sample id, operation index, operation
  name, and view name are provenance seed material only.
- Field roles, locators, schemas, and provenance: field declarations are parsed
  `FieldLocator`s over existing runtime roles and data keys. Locator parsing is
  address validation only; no lookup, schema validation, routing, datasource
  indexing, or mutation policy moves into `FieldLocator` or `Sample`.
- Masking, filtering, normalization, and aggregation order: not implemented in
  this phase. The contract must leave room for later transforms/checks to
  document order explicitly.
- Subject identity, splits, leakage, and grouping: context metadata may carry
  caller-provided subject/split/group identifiers, but this phase does not
  compute or enforce split/group policy.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: only missing declared fields are validated in Phase 2.
  Numerical edge cases, rates, slices, masks, and payload validity are later
  transform/check responsibilities.

## Design Impact

- Maintainability: keeps sample-specific declarations in `rphys.ops.sample`
  while reusing the Stage 6 execution/result envelope, avoiding changes to
  generic operation records.
- Extensibility: ordinary users extend sample behavior through callable-first
  `SampleOperation` now and later through `SampleTransform`,
  `SampleAugmentation`, and `SampleCheck`. Direct `OperationStep`
  implementation remains an advanced adapter path.
- Lightweight import policy: the sample module may import `Sample` and
  `FieldLocator` but must not import heavy optional runtime stacks or later
  datasource/loader/export/trainer systems.
- Source-tree boundaries: field policy stays in `src/rphys/ops/sample.py`;
  generic operation helpers remain generic; private helpers may be introduced
  only when validated through public behavior tests and not re-exported.

## Future Compatibility

- Stage 8 export/materialization can inspect field declarations and runtime
  metadata later without Phase 2 treating replay/context records as durable
  cache or export schemas.
- Stage 9 loaders can later adapt worker/item seed material into
  `SampleOperationContext` without this phase importing loader abstractions.
- Phase 3 can add mutation snapshots and transform/check subclasses on top of
  the same `SampleOperationContract` and `SampleFieldPermissions` records
  without changing their basic locator normalization contract.
- Phase 4 can add augmentation params and deterministic `apply_params()` using
  the context/replay fields established here, while keeping RNG streams
  caller-provided and dependency-light.
- Phase 5 can compose `SampleOperation` objects in specialized pipelines; this
  phase should not add mapping support to generic `OperationPipeline`.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add sample permission fields directly to generic `OperationContract`. | Reopens Stage 6 contracts and makes generic operations carry sample-only policy. |
| Make `SampleOperation` inherit deeply from `Operation` internals. | Couples sample behavior to wrapper implementation details; Phase 1 created `OperationStep` so concrete adapters can share the execution interface without brittle subclassing. |
| Accept raw callables directly in pipelines as sample operations. | Loses inspectable contracts, result normalization, and typed diagnostics; Stage 6 explicitly rejects raw callables. |
| Start with `SampleTransform`, `SampleCheck`, or `SampleOperationPipeline` in this phase. | Those are separate accepted phases with distinct enforcement and review risks. |
| Use global/random NumPy/torch RNGs or backend-specific context fields. | Violates DD-4 replay policy and lightweight import requirements. |
| Add shorthand `SampleOp` aliases or root `rphys` exports. | Maintainer guidance locked full public names and package tests protect scoped exports. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Write/delete/dynamic declarations are recorded before enforcement exists. | Phase 2 must lock public record shapes before Phase 3 implements mutation snapshots. | Phase 3 implementation finds the declaration shape cannot express approved mutation checks or view-family allowances. |
| Replay records are runtime evidence, not durable schemas. | Stage 8/9 own cache/export/loader identity; locking durable serialization now would overreach. | Later export/cache planning needs stable serialization and promotes an explicit schema through a new approved phase. |
| Missing-read preflight validates presence only, not schema/payload type. | Payload and schema validation can materialize lazy fields or belong to operation-specific logic. | A later contract requires non-materializing schema checks through existing `FieldValue` metadata only. |

## Reviewability

- Expected PR size and shape: one new public sample module, focused export and
  error updates if needed, and targeted package/unit/contract tests. No broad
  shared operation refactor should be necessary.
- Files and areas to inspect: `src/rphys/ops/sample.py`,
  `src/rphys/ops/__init__.py`, `src/rphys/errors.py` only if new exercised
  errors are added, `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`, new
  `tests/unit/rphys/ops/test_sample*.py`, and new
  `tests/contracts/test_sample_operations*.py`.
- Scope-control checks: confirm no transform/check/augmentation/pipeline/batch
  public names, no root exports, no generic contract expansion, no
  `OperationPipeline` constructor changes, no mutation snapshots, no payload
  materialization during preflight, and no heavy imports.

## Implementation Steps

1. Add `src/rphys/ops/sample.py` with immutable `SampleFieldPermissions`,
   `SampleOperationContract`, `SampleOperationContext`, and
   `SampleReplayRecord` or equivalent runtime replay evidence. Include locator
   normalization and context/replay validation helpers as private functions.
2. Implement callable-first `SampleOperation` as an `OperationStep` adapter:
   constructor validation, `name`, `sample_contract`, adapted generic
   `contract`, context coercion, required-read preflight, result normalization,
   and typed error wrapping.
3. Wire public exports from `rphys.ops` and `rphys.ops.sample`, updating
   package tests for code-backed full names, submodule `__all__`, no root
   exports, and lightweight import boundaries.
4. Add unit tests for record immutability, locator parsing/normalization,
   malformed/duplicate/contradictory declarations, context adaptation,
   replay-record immutability, `SampleOperation` construction, bare output
   wrapping, explicit result validation, and callable failure wrapping.
5. Add contract tests for declaration inspection, required-field preflight
   without payload materialization, generic `OperationPipeline` compatibility
   with a `SampleOperation`, and preservation of Stage 6 mapping/raw-callable
   rejection.
6. Run the focused validation commands, then broaden to the required package,
   unit, contract, and diff hygiene checks for the phase handoff.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` includes only
  implemented sample names; `rphys.ops.sample.__all__` matches code-backed
  names; root `rphys` does not re-export sample names or new errors; importing
  `rphys.ops` and `rphys.ops.sample` does not load heavy optional modules,
  datasource builders, loader/cache/export modules, model/trainer modules, or
  test support.

### Unit Suite

- Status: required
- Expected paths: new `tests/unit/rphys/ops/test_sample.py` or similarly
  focused source-mirrored files
- Required assertions or deferral reason: immutable record construction;
  locator string and `FieldLocator` normalization; malformed, duplicate, and
  contradictory declaration failures; context coercion from `None`, generic
  `OperationContext`, and `SampleOperationContext`; replay record shape and
  immutability; `SampleOperation` name/contract/sample_contract behavior;
  required-read preflight; bare `Sample` output wrapping; explicit
  `OperationResult` validation; callable failure wrapping.

### Contract Suite

- Status: required
- Expected paths: new `tests/contracts/test_sample_operation_contract.py` or
  similarly named public contract tests, plus existing operation pipeline
  contracts as regression coverage
- Required assertions or deferral reason: users can inspect declared reads,
  writes, deletes, and dynamic allowances before execution; missing declared
  reads fail before callable invocation; preflight does not materialize lazy
  `SampleField` payloads; `SampleOperation` satisfies `OperationStep` and
  composes in generic `OperationPipeline`; `OperationResult.output` is the
  resulting `Sample`; generic pipeline still rejects mappings and raw
  callables.

### Integration Suite

- Status: deferred
- Expected paths: none required for Phase 2 unless the executor touches lazy IO
  helpers beyond existing contract fixtures
- Required assertions or deferral reason: Phase 2 behavior is covered by unit,
  package, and contract suites; broader lazy-field and mutation-snapshot
  integration belongs to Phase 3.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no full user workflow or public
  pipeline is implemented in this phase.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real dataset, hardware, GPU,
  network, or long-running behavior is required.

## Risks

- A too-broad context or replay record could be mistaken for durable
  cache/export identity.
- Accepting direct `OperationStep` implementations too broadly as sample
  operations could bypass sample contracts; ordinary extension should remain
  callable-first through `SampleOperation`.
- Dynamic permissions could become too permissive if the declaration shape is
  vague; keep it inspectable and defer enforcement details to later phases.
- Accidentally using `Sample.require()` or `get()` in preflight would
  materialize lazy fields and violate the scientific boundary.
- Adding new public error classes without distinct exercised semantics would
  enlarge the API surface unnecessarily.

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
make test-unit
make test-contract
make test-package
git diff --check
```

`make validate-pr` is optional for this phase unless implementation touches
shared operation internals, dependency metadata, or a broader public surface
than planned.

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: records/locator normalization first; then
  `SampleOperation` execution; then exports/package tests; then contract tests
  proving preflight, lazy boundary, and `OperationStep` compatibility.
- Tests to run with each slice: record and execution slices should run focused
  unit tests first; export slices should run `make test-package`; contract
  slices should run `make test-contract`; final handoff requires
  `make test-unit`, `make test-contract`, `make test-package`, and
  `git diff --check`.
- Decisions the executor must not revisit: full public names only; no generic
  `OperationContract` expansion; no changes to generic `OperationPipeline`
  mapping/raw-callable behavior; context/replay records are runtime evidence
  only; no transform/check/augmentation/pipeline/batch APIs; no heavy imports.
- Conditions that require stopping for the manager: implementing this phase
  requires changing `OperationStep`, `OperationResult`, generic
  `OperationContext`, generic `OperationContract`, generic
  `OperationPipeline` constructor behavior, accepting raw callables in
  pipelines, adding durable cache/export identity, adding backend RNG
  dependencies, or adding mutation snapshot enforcement.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: used for narrow public-record/import-boundary
  hardening on 2026-05-15
- PR review: unused
- Blocker resolution: 1/3 used

## Completion Notes

- Draft plan: created in
  `docs/roadmap/stage-7/phases/sample-foundations.md`
- Final phase execution plan: this artifact is ready for Phase 2 execution
- Implementation summary: complete
- Implementation validation: complete
- Refinement summary: narrow public-record/import-boundary hardening complete;
  `SampleOperationContract.field_permissions` now rejects non-permission
  records, direct `SampleReplayRecord` construction validates typed context
  fields consistently with `SampleOperationContext`, and direct
  `rphys.ops.sample` import has package-boundary coverage.
- Pre-submit blocker gate: package/import regressions, placeholder exports,
  generic contract expansion, lazy-field materialization during preflight,
  operation-step adapter conflicts, root exports, heavy imports, or
  export/cache/loader/trainer/workflow behavior block completion
- Validation commands run:
- `uv run pytest tests/unit/rphys/ops/test_sample.py` (pass; 19 tests)
- `uv run pytest tests/package/test_import_boundaries.py -k ops_sample` (pass; 1 selected)
- `make test-unit` (pass)
- `make test-contract` (pass)
- `make test-package` (pass)
- `git diff --check` (pass)
- `make test-unit` had one transient failure while validating locator fixtures; corrected test input and re-ran.
- PR preparation: ready to handoff
- Automated review: not run
- Merge result: not run
- Cleanup: complete
- Remaining blockers: none

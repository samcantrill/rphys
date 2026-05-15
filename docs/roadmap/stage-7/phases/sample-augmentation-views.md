# Phase 4 Execution Plan: Sample Augmentation Replay And Views

## Metadata

- Status: refined phase execution plan
- Roadmap stage: `v7`
- Feature focus: reproducible `SampleAugmentation` behavior, dependency-light
  augmentation params, runtime replay metadata, linked-field synchronization,
  and initial self-supervised view-field writes over `SampleOperation`
- Stage descriptor: SampleOps, BatchOps, Transforms, Augmentations, Checks, And
  Pipelines
- Phase descriptor: Sample Augmentation Replay And Views
- PR title: `Stage 7 SampleOps, BatchOps, Transforms, Augmentations, Checks, And Pipelines - Phase 4: Sample Augmentation Replay And Views`
- Branch: `agent/stage-7-p4-sample-augmentation-views`
- Worktree:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p4-sample-augmentation-views`
- Phase execution plan path:
  `docs/roadmap/stage-7/phases/sample-augmentation-views.md`
- Full plan: `docs/roadmap/stage-7/implementation-plan.md`
- Planning document: `docs/roadmap/stage-7/planning.md`
- Source phase: `## Phase 4: Sample Augmentation Replay And Views`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI
  pass during the implementation workflow
- Workflow path: expanded path. Manager review reclassified Phase 4 because it
  introduces the public `SampleAugmentation`/`SampleAugmentationParams` data
  shape plus stochastic replay and scientific contracts that must be precise
  before implementation. Budget state: this phase execution-plan refinement is
  used; implementation refinement, PR review, and blocker-resolution budgets
  remain unused.
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed for the implementation pass
- Plan quality gate: refreshed gate passed and final maintainer approval
  recorded in `docs/roadmap/stage-7/planning.md` and
  `docs/roadmap/stage-7/implementation-plan.md`
- Draft pass: initial plan created in the existing dedicated worktree after
  inspecting `AGENTS.md`, the phase-plan prompt and template, the Stage 7
  implementation plan, Stage 7 planning decisions, Phase 1 through Phase 3
  completion notes, current sample operation source, package/unit/contract/
  integration tests, and `tests/README.md`
- Refine pass: completed with
  `.codex/prompts/phase-execution-plan-refine.md` to address manager review on
  expanded-path status, public API shape, direct replay semantics, reserved
  metadata, RNG limits, exact view-locator permissions, and package validation
- Setup limitations: manager provided the existing branch, worktree, and
  current `develop` base; this pass did not create another branch or worktree,
  refetch remotes, push, open a PR, or modify the control checkout
- Blockers: none

## Objective

Add the public `SampleAugmentation` path that separates reproducible parameter
sampling from deterministic application, records runtime replay evidence, and
supports synchronized self-supervised view-field writes such as
`inputs/video.rgb.view_a` and `inputs/video.rgb.view_b` without adding concrete
rPPG algorithms, backend RNG integrations, pipeline behavior, batch behavior,
or durable replay/export/cache schemas.

## Full-Plan Context

Phase 1 merged the public `OperationStep` foundation. Phase 2 merged
`SampleOperation`, `SampleOperationContract`, `SampleFieldPermissions`,
`SampleOperationContext`, and `SampleReplayRecord`. Phase 3 merged deterministic
sample field-effect enforcement, copy modes, `SampleTransform`, `SampleCheck`,
`SampleDecision`, `SampleRoute`, and runtime `sample_field_effects` metadata.

This phase builds stochastic sample behavior on top of that deterministic
sample operation skeleton. It must reuse Phase 3 declared-read, copy, snapshot,
and field-permission enforcement rather than inventing a parallel mutation
path. Phase 5 owns specialized sample pipeline composition, and Phase 6 owns
provisional batch operations and batch augmentation scope. Both remain out of
scope here.

## Source Phase Summary

- Goal: add reproducible sample augmentation behavior and the initial
  self-supervised view-writing path.
- Required scope: `SampleAugmentation`, public immutable lightweight
  `SampleAugmentationParams`, `sample_params(sample, context)`, deterministic
  `apply_params(sample, params, context)`, replay metadata, synchronized linked
  fields, declared view locator writes, focused public exports, public
  docstrings, and package/unit/contract/integration tests.
- Required checkpoints: `sample_params()` is the only RNG-sampling path;
  `apply_params()` is deterministic for fixed sample, params, and context;
  `run()` samples params exactly once, applies them exactly once, writes only
  declared locators, and records replay evidence; invalid params fail loudly
  before partial mutation where practical; package base code must not import
  `random` or call module-level `random.*`, NumPy, Torch, or backend RNG state.
- Acceptance criteria: `run()` produces deterministic replay metadata and
  deterministic outputs for fixed sampled params/context; direct
  `apply_params()` produces deterministic field changes for fixed
  params/context without promising replay metadata; linked fields and view
  locators are synchronized through inspectable params and declared field
  permissions; replay remains runtime metadata only; no
  export/cache/loader/trainer/model/pipeline/batch behavior appears.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/ops/sample.py` currently exports `SampleFieldPermissions`,
  `SampleOperationContract`, `SampleOperationContext`, `SampleReplayRecord`,
  `SampleOperation`, `SampleTransform`, `SampleCheck`, `SampleDecision`, and
  `SampleRoute`. There is no augmentation class or params record yet.
- `SampleOperation.run()` already coerces `SampleOperationContext`, validates
  required context keys and declared reads, prepares `in_place`/`shallow`/`deep`
  execution samples, captures before/after `field_items()` snapshots, validates
  declared writes/deletes/exact `dynamic_writes`, and attaches runtime
  `sample_field_effects` metadata.
- `SampleOperationContext` already carries dependency-light reproducibility
  fields: `run_seed`, `epoch`, `worker_id`, `item_id`, `sample_id`,
  `operation_index`, `operation_name`, `view_name`, and `rng_stream`.
  `SampleReplayRecord` mirrors those fields as immutable runtime evidence.
- `SampleFieldPermissions.dynamic_writes` is currently an exact-locator tuple,
  not a prefix, family, glob, schema, role-wide, or callable predicate. Phase 4
  should use explicit declared view locators first. If generated view-family
  permissions require a broader matching shape, stop for manager review instead
  of designing it inside implementation.
- Existing tests or harness behavior: `tests/unit/rphys/ops/test_sample.py`,
  `tests/contracts/test_sample_operations.py`, and
  `tests/integration/test_sample_operations_lazy.py` cover sample operation
  context/replay records, copy modes, mutation enforcement, lazy-field
  non-materialization, transform/check public contracts, and field-effect
  metadata. Package tests lock `rphys.ops` exports, root-export absence, and
  import boundaries.
- Import-boundary or dependency constraints: package code may use standard
  library records and existing `rphys.ops`/`rphys.data` primitives only. It
  must not import `random`, NumPy, torch, OpenCV, PyAV, scipy, pandas, plotting
  stacks, datasource builders, codec/runtime IO, loader/cache/export modules,
  model/trainer modules, or `tests.support`.

## Phase Isolation State

- Control checkout dirty-state review: not modified by this pass; the assigned
  phase worktree is used for all plan work.
- Dedicated branch/worktree status:
  `/home/samcantrill/work/rphys-worktrees/stage-7-p4-sample-augmentation-views`
  is on `agent/stage-7-p4-sample-augmentation-views` and was clean before this
  plan file was created.
- Current `develop` base:
  `9fac17a7bc7ee985f3648e65453c5b90810fcc2f` (`docs: record stage 7 phase 3
  merge`), with this worktree `HEAD`, local `develop`, and `origin/develop`
  resolving to that commit.
- Earlier phase dependency status: Phase 1, Phase 2, and Phase 3 are merged to
  `develop`; Phase 3 completion records `SampleTransform`, `SampleCheck`,
  field-effect enforcement, and lazy integration validation.
- Push/PR infrastructure status: manager provided setup facts; this planning
  pass did not push or open a PR.
- Stop condition if isolation cannot be maintained: stop before editing the
  control checkout, committing product code during this planning pass, rebasing
  away from the verified base, broadening into Phase 5/6, or committing files
  beyond this phase execution plan.

## In-Scope Work

- Add code-backed public names `SampleAugmentation` and
  `SampleAugmentationParams`. `SampleAugmentation` is the sample-specialized
  stochastic wrapper over the Phase 3 `SampleOperation` execution skeleton.
  Its public constructor shape is callable-first and must be implemented as:
  `SampleAugmentation(sample_params, apply_params, *, name=None, contract=None,
  copy_mode=None)`. The `sample_params` callable must accept
  `(sample, context)` and return `SampleAugmentationParams`. The
  `apply_params` callable must accept `(sample, params, context)` and return
  `Sample | OperationResult`. The class must expose
  `sample_params(sample, context)` and `apply_params(sample, params, context)`
  methods that delegate to those callables, and `run()` must call each public
  method exactly once.
- Add immutable, dependency-light public record `SampleAugmentationParams` with
  exactly these fields: `values`, `linked_fields`, and `view_locators`. The
  accepted public shape is `values: Mapping[str, object]`,
  `linked_fields: tuple[tuple[FieldLocator, ...], ...]`, and
  `view_locators: Mapping[str, FieldLocator]`. Mapping keys must be non-empty
  strings. `values` must normalize to a recursively immutable value grammar:
  `None`, bool, int, float, str, tuples of supported values, and string-keyed
  mappings of supported values. Constructor inputs may normalize lists or other
  non-string sequences to tuples only when every element is supported. Locator
  fields accept only `FieldLocator | str` inputs and normalize to exact
  `FieldLocator` instances; locators must not live inside arbitrary backend
  objects.
- Keep params free of backend arrays, payloads, RNG objects, file handles,
  mutable containers, `Sample`, `FieldValue`, `SampleField`, NumPy arrays,
  Torch tensors, or backend-specific scalar wrappers. Reject unsupported params
  with typed operation errors before application.
- Reuse existing `SampleReplayRecord` for context seed/material evidence and
  add runtime augmentation replay metadata under the reserved
  `OperationResult.metadata["sample_augmentation_replay"]` key. The metadata
  shape must be dependency-light and inspectable: operation name, params
  evidence, context replay evidence, linked field groups as locator strings,
  view locators as `view_name -> locator string`, and no payloads or durable
  artifact identifiers. `sample_augmentation_replay` is a reserved key:
  user-provided result metadata that already contains it must fail instead of
  being overwritten. The key must coexist with Phase 3 `sample_field_effects`
  metadata in the final `run()` result. This metadata is runtime evidence only,
  not a stable serialization, manifest, cache key, export identity, or workflow
  artifact.
- Ensure `run()` samples params exactly once by calling `sample_params()` before
  deterministic application, then calls `apply_params()` exactly once with the
  sampled params and the coerced `SampleOperationContext`. `run()` must return
  an `OperationResult` with `output` as the execution `Sample`, existing
  `sample_field_effects` metadata preserved, and `sample_augmentation_replay`
  added without reserved-key collisions.
- Define direct deterministic application behavior through
  `apply_params(sample, params, context)`: fixed params plus compatible context
  must apply the same field changes each time. Direct `apply_params()` calls do
  not guarantee Phase 3 declared mutation enforcement, `sample_field_effects`,
  or `sample_augmentation_replay`; those guarantees are provided by `run()`
  because it owns preflight, snapshots, permission validation, result
  normalization, and metadata attachment. `apply_params()` must not call
  `sample_params()`, consume `context.rng_stream`, derive new seed material, or
  use hidden/global/default RNGs.
- Keep all randomness at the `sample_params()` boundary. Package code must not
  import `random`, call module-level `random.*`, call NumPy default RNGs, call
  Torch default generators, or touch backend RNG state. Synthetic tests may use
  explicitly seeded standard-library `random.Random` objects or simple
  deterministic fake RNGs as caller-provided context streams outside package
  code. The base class is not required to prove arbitrary user callables never
  use hidden RNG; deterministic `sample_params()`/`apply_params()` behavior is
  an extension contract, and tests should enforce it for package-provided
  examples.
- Support linked-field synchronization by making params identify the locator
  groups and sampled values that must be shared across fields. The base wrapper
  should make those groups inspectable in params/replay metadata; synthetic
  tests should prove the same sampled value is used for linked outputs. It
  should not inspect or transform payload internals beyond what the user
  `apply_params()` callable does.
- Add self-supervised view-writing examples using one wide-window `Sample` and
  declared exact writes or exact `dynamic_writes` for locators such as
  `inputs/video.rgb.view_a` and `inputs/video.rgb.view_b`. Broader generated
  view-family permissions remain out of scope and require manager review. The
  examples must write `FieldValue` payloads that are tiny synthetic
  placeholders, not real video data or codec-backed arrays.
- Add or update package exports only for implemented code-backed public names:
  `SampleAugmentation` and `SampleAugmentationParams`. Preserve no root
  `rphys` exports and no shorthand aliases.
- Add focused docstrings for RNG/replay boundaries, params immutability,
  linked fields, view locator writes, lazy-field limits, invalid-param
  failures, and explicit deferrals.

## Out-of-Scope Work

- Concrete rPPG or video augmentation algorithms, CHROM/POS kernels, color
  transforms, physiological signal processing, model-specific view formatting,
  learner/model consumption, and real video/audio/image decoding.
- Backend-specific RNG integrations, NumPy/Torch generator adapters, global or
  default RNG use, backend arrays/tensors in params, device movement, dtype
  policy, and backend-specific scalar coercion.
- Nested view `Sample`s, multi-member `IndexItem`s, new temporal slicing or
  datasource indexing behavior, loader worker adapters, cache/export/save
  manifests, durable replay serialization, operation fingerprints, and
  materialization workflow behavior.
- `SampleOperationPipeline`, ordered mapping support, step diagnostics, route
  graphs, DAGs, retry/resume, workflow branching, and generic
  `OperationPipeline` behavior.
- `BatchOperation`, `BatchTransform`, `BatchAugmentation`,
  `BatchOperationContext`, `BatchOperationPipeline`, batch/per-sample parameter
  scope, batch equivalence reports, collated field behavior, and DataLoader or
  model layout policy.
- Prefix/family/glob/schema-wide/role-wide dynamic write matching unless the
  maintainer explicitly reopens the field-permission design for generated view
  families.
- New dependencies, raw datasets, large fixtures, root `rphys` exports,
  registries, symbolic operation names, or placeholder future APIs.

## Assumptions

- Phase 3 `SampleOperation` field-effect enforcement can be reused for
  augmentation application, including copy modes, exact locator declarations,
  `FieldValue` replacement detection, and runtime `sample_field_effects`
  metadata.
- Existing `SampleOperationContext` and `SampleReplayRecord` fields are enough
  context seed/material evidence for Phase 4. Additive replay metadata should
  reference those records rather than adding durable serialization fields.
- A lightweight params record with recursively immutable primitive values,
  linked field groups, and view locator mappings is sufficient for synthetic
  view-writing examples and future backend adapters.
- The base operation cannot prevent arbitrary user-provided callables from
  using hidden RNGs internally, so the enforceable contract is: package base
  code and package-provided examples do not import or call hidden/default RNGs;
  public docs state that custom `sample_params()`/`apply_params()` callables
  must keep randomness at the explicit sampling boundary and make application
  deterministic for fixed params.
- No dependency metadata change is expected. Any dependency addition is a
  stop-and-review condition.

## Scope Contract

The executor must preserve the public operation shape as
`Sample -> OperationResult`, with `OperationResult.output` holding the resulting
execution `Sample`. `SampleAugmentation` must remain a `SampleOperation`
specialization and use the same field-permission enforcement path:

Public constructor shape:

```python
SampleAugmentation(
    sample_params,
    apply_params,
    *,
    name=None,
    contract=None,
    copy_mode=None,
)
```

- `sample_params` is a callable with the method-compatible signature
  `(sample, context) -> SampleAugmentationParams`.
- `apply_params` is a callable with the method-compatible signature
  `(sample, params, context) -> Sample | OperationResult`.
- `name`, `contract`, and `copy_mode` follow the existing `SampleOperation`
  keyword style and conflict behavior.
- The class exposes public methods `sample_params(sample, context)` and
  `apply_params(sample, params, context)` that delegate to the constructor
  callables after validation/normalization. `run()` must call each method
  exactly once.

1. Coerce `None`, `OperationContext`, or `SampleOperationContext` into a
   `SampleOperationContext` whose `operation_name` matches the augmentation.
2. Validate required context keys and declared reads without materializing lazy
   payloads.
3. Select the execution sample through the inherited `copy_mode`.
4. Call `sample_params(execution_sample, context)` exactly once.
5. Normalize and validate params into the public params record.
6. Call `apply_params(execution_sample, params, context)` exactly once.
7. Normalize and validate the result as an `OperationResult` whose output is
   the same execution sample object.
8. Enforce declared writes/deletes/exact dynamic writes through the Phase 3
   before/after snapshot path.
9. Reject result metadata that already contains the reserved
   `sample_augmentation_replay` key, then return metadata that includes both
   Phase 3 `sample_field_effects` and Phase 4 `sample_augmentation_replay`.

Public params constructor and shape:

```python
SampleAugmentationParams(
    *,
    values=None,
    linked_fields=None,
    view_locators=None,
)
```

- `values`: string-keyed immutable mapping of sampled parameter names to
  dependency-light primitive values. Accepted leaves are `None`, bool, int,
  float, and str. Lists/sequences supplied by users should normalize to tuples
  only when every element is supported. String-keyed nested mappings may be
  accepted only when recursively normalized to immutable mappings. Unsupported
  objects fail loudly.
- `linked_fields`: tuple of locator groups. Each group must contain at least
  two distinct exact parsed `FieldLocator`s when present, and one locator must
  not appear in multiple groups. Groups describe fields that share sampled
  params; they do not grant read or write permission by themselves.
- `view_locators`: string-keyed mapping from non-empty view names, such as
  `view_a` and `view_b`, to exact parsed `FieldLocator`s. View names and
  locators must be unique. These locators do not grant read or write permission
  by themselves.

Replay metadata shape:

- `sample_augmentation_replay.operation_name`: executing augmentation name.
- `sample_augmentation_replay.context`: the `SampleReplayRecord` or its
  runtime-only mapping evidence for run seed, epoch, worker id, item id, sample
  id, operation index, operation name, view name, and caller-provided RNG
  stream reference. Do not introspect, clone, or serialize backend RNG state.
- `sample_augmentation_replay.params`: the normalized params record or its
  dependency-light mapping evidence.
- `sample_augmentation_replay.linked_fields`: tuple of tuple locator strings
  derived from params.
- `sample_augmentation_replay.view_locators`: mapping of view names to locator
  strings derived from params.
- `sample_augmentation_replay` is reserved runtime metadata. If user metadata
  already contains that key, `run()` fails instead of merging or overwriting it.
  The returned metadata must also preserve Phase 3 `sample_field_effects`.

Error behavior:

- Invalid augmentation constructor arguments, non-callable sampler/apply
  functions, conflicting copy modes, or invalid contracts raise
  `InvalidOperationContractError`.
- Missing required context fields or mismatched `operation_name` continue to
  raise `InvalidOperationContextError`.
- Missing declared reads continue to raise `MissingFieldError` before
  parameter sampling or application.
- `sample_params()` callable failures are wrapped in `OperationExecutionError`
  with phase/context indicating parameter sampling.
- `sample_params()` returning anything other than `SampleAugmentationParams`
  raises `InvalidOperationResultError` during `run()`; direct params
  construction with unsupported values or direct `apply_params()` with invalid
  params should raise `InvalidOperationInputError` or the narrowest existing
  operation-input failure available.
- `apply_params()` callable failures during `run()` are wrapped in
  `OperationExecutionError` with phase/context indicating deterministic
  application.
- During `run()`, an `apply_params()` result whose output is not the execution
  sample, or whose metadata collides with reserved
  `sample_augmentation_replay`, raises `InvalidOperationResultError`. Direct
  `apply_params()` calls are deterministic application helpers; they do not
  attach replay metadata or promise full Phase 3 mutation enforcement.
- Undeclared writes to view fields or linked fields continue to raise
  `UndeclaredSampleFieldMutationError` with the Phase 3 field-effect context.
- If the implementation needs a new params-specific public error, add at most
  one focused exercised error under `RemotePhysOperationError`; do not add a
  broad augmentation error taxonomy.

No public contract change is in scope for generic `OperationStep`,
`Operation`, `OperationPipeline`, `OperationResult`, `OperationContext`,
`OperationContract`, `OperationRole`, `OperationMutationPolicy`,
`FieldLocator`, `Sample`, `SampleField`, `FieldValue`, `IndexItem`, or `Batch`.

## Scientific Contract Notes

- Sampling and temporal alignment: this phase does not create new temporal
  slices, resample video/signals, filter, pad, align, or normalize payloads.
  The approved view-writing path assumes one already-built wide-window
  `Sample`; params may record offsets or crop/window identifiers as primitive
  values, but concrete temporal semantics belong to future algorithms.
- Field roles, locators, schemas, and provenance: linked field groups and view
  locators are explicit `FieldLocator` declarations. They are provenance and
  replay evidence, not permissions. Actual writes must still be declared in
  `SampleFieldPermissions`.
- Masking, filtering, normalization, and aggregation order: no concrete
  scientific transform is implemented. The only ordering contract is
  preflight, one params sample, deterministic apply, field-effect enforcement,
  then replay metadata attachment.
- Subject identity, splits, leakage, and grouping: replay context may record
  item/sample ids and worker/epoch seed material, but this phase does not
  assign splits, inspect subject identity, or implement leakage policy. View
  fields are created after sample construction and before later collation.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: missing declared fields fail before sampling. Payload
  validity remains the responsibility of concrete augmentation callables and
  must be documented by those callables when real algorithms are added later.

## Design Impact

- Maintainability: keep augmentation param normalization and replay metadata
  attachment central and private, with public validation only through
  `SampleAugmentation` behavior and the params record.
- Extensibility: backend-specific samplers can later supply params through the
  same record without adding NumPy/Torch imports to base operations. Public
  extension remains callable-first; direct operation-step implementation stays
  the advanced path from Phase 1.
- Lightweight import policy: `rphys.ops.sample` must remain dependency-light,
  and `rphys.ops` must preserve lazy access to sample names. Params and replay
  records must not import or store backend arrays/tensors.
- Source-tree boundaries: augmentation behavior stays in `rphys.ops.sample`.
  Data containers, locators, codecs, datasource views, loaders, models, and
  trainers must not learn augmentation replay or view-writing policy.

## Future Compatibility

- Stage 8/9 export, materialization, cache, and loader planning may inspect
  runtime params/replay metadata, but this phase must not promote it to a
  durable manifest or cache/export identity.
- Stage 9 loader worker contexts can later construct `SampleOperationContext`
  or pass explicit RNG streams; this phase should not define loader worker
  adapters or multiprocessing behavior.
- Phase 5 sample pipelines should be able to execute `SampleAugmentation` as a
  regular sample operation and rely on `OperationResult.output` forwarding, but
  no sample pipeline class or step diagnostics are added here.
- Phase 6 batch augmentations should reference this sample-side split between
  params sampling and deterministic application, but no batch/per-sample scope
  records are added here.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Global or default RNG use in base augmentations | Breaks replay and violates DD-4/FQ-3 reproducibility requirements. |
| NumPy/Torch arrays or generators in params | Adds heavy/backend coupling and makes params non-portable runtime evidence. |
| Durable replay serialization in Phase 4 | Belongs to export/cache/materialization planning in later stages. |
| Nested view `Sample`s or multi-member `IndexItem`s | Explicitly deferred by FQ-7; initial path is view locators on one wide-window sample. |
| Prefix or glob dynamic permissions for views | Too broad for current field-permission contract; explicit locators are inspectable and sufficient for Phase 4 examples. |
| Hiding `sample_params()` inside `apply_params()` | Makes deterministic replay untestable and conflicts with approved DD-5 split sampling/application. |
| Concrete physiological augmentation algorithms | Stage 7 is locking operation contracts first; algorithms can be added after the runtime semantics are stable. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Replay metadata is runtime-only and not durably serializable | Keeps Stage 8/9 cache/export identity intentionally deferred. | Export/materialization planning needs stable manifests and can promote a deliberate schema. |
| Params values are restricted to primitive immutable data | Avoids backend imports and array/tensor coupling in the base library. | A real augmentation needs a richer dependency-light scalar shape and can justify an additive params field. |
| Base code cannot police hidden RNG inside arbitrary user callables | Python callables are extension points; tests and docs can enforce package/examples and public contract. | A future adapter framework can provide audited sampler/apply wrappers without changing Phase 4 semantics. |
| Exact view locator declarations may be verbose | Preserves provenance and avoids premature prefix/family matching. | Multiple generated view families require inspectable dynamic permissions beyond exact locators. |

## Reviewability

- Expected PR size and shape: one focused sample augmentation PR touching
  `src/rphys/ops/sample.py`, `src/rphys/ops/__init__.py`, `src/rphys/errors.py`
  only if a focused params error is justified, package tests, sample unit
  tests, sample contract tests, synthetic integration tests, and public
  docstrings. No broad docs-only pass is expected beyond code-backed API
  docstrings.
- Files and areas to inspect: params record immutability/coercion,
  `SampleAugmentation.run()` call order, separation of `sample_params()` and
  `apply_params()`, replay metadata attachment, reserved metadata collision
  checks, declared view writes, linked-field synchronization tests, public
  exports, import-boundary tests, and lazy-field non-materialization.
- Scope-control checks: verify no package `random` import, no module-level or
  hidden/default RNG use in package-provided examples, no NumPy/Torch imports,
  no backend arrays in params, no concrete algorithms, no nested samples, no
  multi-member index items, no sample pipeline class, no batch class, no
  export/cache/loader/trainer/model behavior, no root exports, and no
  placeholder future names.

## Implementation Steps

1. Add the minimal public params shape and private coercion helpers in
   `rphys.ops.sample`: immutable primitive `values`, parsed linked-field
   groups, parsed view-locator mapping, unsupported-object failures, and
   public docstrings that state no backend arrays or durable serialization.
2. Add `SampleAugmentation` over the existing sample operation execution path
   with separate `sample_params()` and `apply_params()` hooks/callables. Ensure
   `run()` samples once, applies once, preserves copy/read/snapshot behavior,
   and rejects reserved metadata collisions.
3. Attach runtime `sample_augmentation_replay` metadata from the normalized
   params and `SampleOperationContext.to_replay_record()` without serializing
   RNG state, payloads, `FieldValue` objects, or artifact identifiers.
4. Update code-backed public exports and package tests for implemented
   augmentation names while preserving root-export absence and lightweight
   imports.
5. Add focused unit and contract coverage for params immutability, invalid
   params, call counts, deterministic direct application without replay
   metadata guarantees, no package `random` import or hidden RNG in
   package-provided examples, declared/undeclared view writes, and linked-field
   synchronization.
6. Add tiny integration coverage for one wide-window lazy `Sample` that writes
   `inputs/video.rgb.view_a` and `inputs/video.rgb.view_b` from synthetic
   placeholders without materializing unrelated lazy fields or invoking
   datasource/codec/export/loader behavior.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`;
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.ops.__all__` and
  `rphys.ops.sample.__all__` include only implemented Phase 4 public names;
  root `rphys` still does not re-export sample operation names; any new focused
  error is exported only if code-backed and tested; importing `rphys.ops` and
  `rphys.ops.sample` does not import NumPy, torch, video/codec stacks,
  datasource, loader, cache/export, model, trainer, or `tests.support` modules.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/ops/test_sample.py` or a focused
  source-mirrored `tests/unit/rphys/ops/test_sample_augmentation.py` if that
  keeps the file reviewable
- Required assertions or deferral reason: params record normalization,
  recursive immutability, unsupported-object failures, locator parsing,
  invalid linked-field and view-locator shapes, constructor validation,
  `sample_params()` called exactly once by `run()`, `apply_params()` called
  exactly once, direct `apply_params()` does not call the sampler, deterministic
  direct application for fixed params/context without expecting replay
  metadata, reserved metadata collision behavior, context replay evidence, no
  package `random` import or hidden RNG in package-provided examples, declared
  view writes pass, undeclared view writes fail, and invalid params fail before
  application where practical.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_sample_operations.py` or a focused
  `tests/contracts/test_sample_augmentations.py`
- Required assertions or deferral reason: public `SampleAugmentation` and
  params behavior through public imports; `run()` with fixed sampled
  params/context produces deterministic output and replay metadata;
  `sample_params()` is the only sampling boundary; direct `apply_params()` is
  deterministic, does not attach replay metadata, and writes only declared
  locators when executed through `run()`; linked fields share sampled values;
  view locators are explicit fields on one `Sample`; invalid params and
  reserved metadata collisions are typed failures; replay metadata is
  documented as runtime-only and not a durable export/cache schema.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/` with tiny synthetic `SampleField`
  fixtures, reusing existing lazy fixture patterns where practical
- Required assertions or deferral reason: one wide-window sample with
  video-like placeholder fields writes synchronized `inputs/video.rgb.view_a`
  and `inputs/video.rgb.view_b`; declared reads/preflight, params sampling,
  apply, snapshots, and metadata attachment do not materialize unrelated lazy
  fields; payload access inside the synthetic apply callable materializes only
  through existing lazy-field APIs; no datasource scan, codec decode, export,
  loader, trainer, or model behavior is invoked.

### E2E Suite

- Status: deferred
- Expected paths: none for this phase
- Required assertions or deferral reason: Phase 4 does not implement a public
  pipeline, loader, export/cache workflow, batch execution surface, or learner
  consumption path. End-to-end coverage should wait until Phase 5 pipelines and
  later export/loading stages exist.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real datasets, hardware, GPU,
  network, long-running video decoding, or benchmark validation is required.
  Synthetic package/unit/contract/integration coverage is sufficient for this
  runtime augmentation contract phase.

## Risks

- Hidden RNG inside user-provided callables cannot be mechanically prevented by
  the base wrapper. Tests must prove package-provided examples avoid hidden RNG,
  and docs must make deterministic `apply_params()` a public extension
  contract.
- Params could become a back door for backend arrays or payload objects. Keep
  validation strict and reject unsupported values loudly.
- Replay metadata may be mistaken for durable serialization. Keep field names
  runtime-oriented and avoid cache/export/manifest wording.
- Linked-field metadata can look like permission grants. Tests must prove field
  writes still require explicit `writes` or exact `dynamic_writes`.
- View-field examples can drift into pipeline or learner behavior. Keep the
  phase limited to writing fields on one `Sample`.

## Validation Commands

Targeted development commands:

```sh
make test-unit
make test-contract
make test-integration
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

- Safe implementation slices: params/coercion first, augmentation execution
  second, replay metadata third, exports/package tests fourth, linked view
  integration last.
- Tests to run with each slice: unit tests after params and execution changes;
  package tests after export changes; contract tests after public behavior is
  wired; integration tests after linked view fixtures are added; `git diff
  --check` before PR prep.
- Decisions the executor must not revisit: no package `random` import, no
  global/default RNG, no backend array params, no durable replay serialization,
  no nested view samples, no multi-member index items, no Phase 5 pipelines, no
  Phase 6 batch work, no loader/cache/export/trainer/model behavior, and no
  broad dynamic permission matching without manager approval.
- Conditions that require stopping for the manager: params need backend arrays
  or non-primitive public fields; replay needs durable serialization or stable
  artifact identity; `SampleReplayRecord` requires incompatible field changes;
  exact locator declarations cannot express the required view examples;
  implementation requires importing `random`, NumPy/Torch/backend RNGs; or the
  augmentation base cannot reuse Phase 3 sample operation enforcement.

## Refinement And Review Budget Status

- Phase execution plan refinement: used once / completed for expanded path
- Phase implementation refinement: used once / completed for duplicate view
  locator validation and focused public-boundary coverage
- PR review: unused
- Blocker resolution: 1/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: refined expanded-path execution plan completed in
  this artifact
- Implementation summary: implemented on 2026-05-15 in
  `agent/stage-7-p4-sample-augmentation-views`
- Implementation validation: `make test-unit`, `make test-contract`, `make
  test-integration`, `make test-package`, `make validate-pr`, `make
  test-summary`, and `git diff --check` passed on 2026-05-15.
- Implementation refinement: completed on 2026-05-15 for assigned blocker
  cluster covering duplicate view locator rejection, constructor callable
  validation coverage, undeclared view-write enforcement coverage,
  `apply_params` error wrapping coverage, and package-level `random` source
  boundary coverage
- Refinement summary: completed; manager review findings addressed for
  expanded-path status, public constructor and params shape, direct
  `apply_params()` limits, reserved metadata behavior, RNG restrictions, exact
  locator permissions, and targeted `make test-package` validation
- Pre-submit blocker gate: completed; no global/default RNG, backend-heavy
  import, nested sample view, durable replay serialization, or scope-expansion
  blocker remains known.
- PR preparation: completed; durable PR body drafted in
  `docs/roadmap/stage-7/phases/sample-augmentation-views-pr-body.md`
- PR: [#51](https://github.com/samcantrill/rphys/pull/51) opened against
  `develop` from `agent/stage-7-p4-sample-augmentation-views`; target and
  title verified by `gh pr view`
- Automated review: not started
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

## Phase Refinement Report: Sample Augmentation View Coverage

## Assigned Blocker

- Blocker: close the assigned Phase 4 coverage cluster for duplicate view
  locators, constructor callable checks, undeclared view writes,
  `apply_params` failure context, package-level `random` boundary coverage, and
  phase artifact cleanup.
- Source: manager-assigned implementation test refinement.
- Scope: `src/rphys/ops/sample.py`,
  `tests/unit/rphys/ops/test_sample_augmentation.py`,
  `tests/package/test_import_boundaries.py`, and this phase artifact.
- Budget use: implementation refinement completed; blocker resolution 1/3 used.

## Resolution

- Changes made: `SampleAugmentationParams.view_locators` now rejects duplicate
  normalized locator values while preserving exact named locator mappings.
- Tests or docs updated: added focused unit coverage for duplicate view
  locators, non-callable constructor inputs, undeclared view writes through
  Phase 3 mutation enforcement, and `apply_params` execution wrapping; added a
  package source-text random boundary test; cleaned completion notes.
- Validation rerun: `uv run pytest tests/unit/rphys/ops/test_sample_augmentation.py tests/package/test_import_boundaries.py`,
  `make test-unit`, `make test-package`, `make test-contract`, and
  `git diff --check` passed.

## Result

- Blocker resolved: yes.
- Remaining blocker: none known.
- Recommended next gate: focused unit/package validation followed by
  `make test-unit`, `make test-package`, and `git diff --check`.

## Files Changed

- `src/rphys/ops/sample.py`
- `tests/unit/rphys/ops/test_sample_augmentation.py`
- `tests/package/test_import_boundaries.py`
- `docs/roadmap/stage-7/phases/sample-augmentation-views.md`

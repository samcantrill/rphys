# Phase 3 Execution Plan: Lazy `SampleField` Runtime Compatibility

## Metadata

- Status: implemented; ready for PR
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Lazy `SampleField` Runtime Compatibility
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 3: Lazy SampleField Runtime Compatibility`
- Branch: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Phase execution plan path: `docs/roadmap/stage-4/phases/lazy-sample-field-runtime.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-3-lazy-samplefield-runtime-compatibility`
- Assignment: `docs/roadmap/stage-4/phases/lazy-sample-field-runtime-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path; expanded path only if runtime compatibility review finds accessor ambiguity, loaded `Sample` contract regression, or need for a parallel `LazySample` container
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; Preparation Phases 1
  and 2 plus Primary Phases 1 and 2 are merged and recorded
- Draft pass: completed in this artifact
- Refine pass: not needed unless implementation exposes ambiguous payload
  access, public API, compatibility, or import-boundary behavior not resolved
  by this plan
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Add lazy `SampleField` handles that can live inside existing `Sample` field
storage, expose inspectable unloaded/loaded/failed state, load through the
Phase 2 codec result boundary exactly once, and preserve the meaning of loaded
`Sample`, `FieldValue`, `FieldContainer`, contract, and collation behavior.

## Full-Plan Context

Preparation Phase 1 added the public `FieldContainer` protocol and
`field_items()` surface. Preparation Phase 2 froze `FieldSpec` and clarified
`FieldIndex` terminology. Primary Phase 1 added datasource-neutral codec
contracts, and Primary Phase 2 added explicit `CodecRegistry` behavior,
operation results, typed failures, and private synthetic codec coverage.

This Phase 3 is the runtime compatibility step between codecs and builders. It
adds lazy field handles but does not build samples from `IndexItem`s. Phase 4
owns `SampleBuilder`, requested locator handling, eager build orchestration,
builder-side datasource provenance, probe paths, and compound resource bridge
coverage. Phase 5 owns closeout docs, examples, package hardening, and final
validation. Those later behaviors remain out of scope here.

## Source Phase Summary

- Goal: add lazy field handles while preserving loaded `Sample` semantics.
- Required scope: `src/rphys/data/sample_fields.py`; additive compatibility
  updates in `src/rphys/data/containers.py`; conditional `src/rphys/data/__init__.py`
  only if import-boundary tests support package re-export; focused data unit
  tests; runtime and lazy-field contract tests.
- Required checkpoints: `SampleField` is stored as the field object, not as a
  `FieldValue.payload`; `Sample.field()` returns the handle without loading;
  payload-demanding paths load only where documented; successful load is
  retained; failed load state and diagnostics are retained; repeated payload
  access returns the retained payload or re-raises the retained error; eager
  handle load uses the same state machine.
- Acceptance criteria: loaded-sample unit and contract behavior remains green;
  lazy state transitions are executable; provenance and codec load result
  evidence stay inspectable; no `LazySample`, broad cache/retry/reset policy,
  async state, public loader handler interface, builder behavior, or collation
  redesign is introduced.

## Current Source And Harness Findings

- `src/rphys/data/sample_fields.py` does not exist yet. Adding it is the main
  product-code surface for the executor.
- `src/rphys/data/containers.py` stores private `_FieldEntry.value` objects and
  currently treats only `isinstance(value, FieldValue)` inputs as already
  wrapped. Any `SampleField` path must avoid accidentally wrapping the lazy
  handle as a raw payload inside a new `FieldValue`.
- `FieldContainer`, `Sample.field()`, `Sample.role()`, and `field_items()` are
  annotated around `FieldValue`. The executor may widen annotations or local
  aliases only as needed for `SampleField` compatibility, while preserving
  method names and loaded behavior.
- `Sample.field(locator)` with no validation currently returns the stored
  object without touching `.payload`. `Sample.get()`, `Sample.require()`,
  `_validate_field_value(... expected_type=...)`, `map_tensors_()`, and
  `collate_samples()` are payload-demanding paths because they access
  `.payload`.
- `_validate_field_value(... schema=...)` can check `value.schema` without
  materializing payloads. Expected-type validation necessarily loads through
  `.payload`; this should be documented and tested rather than hidden.
- `FieldValue` is identity-equality, copyable, and carries `schema`,
  `metadata`, and `collate_policy`. `SampleField` must be compatible with the
  public attributes loaded-runtime code reads, but it must not replace the
  loaded `FieldValue` contract for normal fields.
- `SampleContract` validates only public container shape and delegates
  required/optional checks to `container.require()`. Lazy required fields may
  load during contract validation because it is payload-demanding.
- `collate_samples()` accepts `FieldContainer`, uses public `field_items()`,
  and then reads each field `.payload` for LIST collation. It must keep using
  public field iteration and may load lazy fields only as a documented
  payload-demanding behavior.
- `src/rphys/io/codecs.py` now provides `LoadContext`, `CodecLoadResult`,
  `CodecRegistry.load()`, and typed codec failures. `LoadContext` is
  datasource-neutral and must not gain `record`, `index_item`, locator,
  manifest, or builder provenance fields in this phase.
- `tests/support/synthetic_codecs.py` is private and already exercises
  dependency-light load behavior. Phase 3 tests can use it or local fixtures,
  but package code must not import `tests.support`.
- Package import-boundary tests already assert lightweight imports and that
  `rphys.io.codecs` does not import `rphys.data.sample_fields` or
  `rphys.data.sample_builders`. If `SampleField` is re-exported from
  `rphys.data`, update package tests deliberately; otherwise keep
  `rphys.data.sample_fields` as the canonical import home.
- `tests/README.md` defines package, unit, contract, integration, e2e, and
  acceptance suite intent. There are no e2e or acceptance tests present, and
  integration currently covers runtime collation only.
- Harness targets run through `tools.test_harness`. `make validate-pr` runs
  lock check, `make test-summary`, build, and `git diff --check`; PR
  preparation must also run `git diff --check origin/develop...HEAD` for the
  review range requested by the manager.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` was
  checked before this plan edit and was clean on `develop` tracking
  `origin/develop`.
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime` and was clean
  before this plan edit.
- Current `develop` base: `7eb39f3 docs: record stage 4 phase 2 cleanup`.
- Branch setup note: the branch already contains
  `c857edf plan: add phase 3 assignment`; preserve it and add only the
  execution-plan commit for this pass.
- Earlier phase dependency status: Preparation Phases 1 and 2 and Primary
  Phases 1 and 2 are merged and recorded in the implementation plan.
- Push/PR infrastructure status: assignment records GitHub push and PR
  infrastructure as previously exercised; this planning pass does not push or
  open a PR.
- Stop condition if isolation cannot be maintained: stop before product code
  edits or PR work and return to the manager if the branch/worktree cannot
  remain dedicated to Phase 3.

## In-Scope Work

- Add `SampleField` in `src/rphys/data/sample_fields.py` with a small explicit
  state model for unloaded, loaded, and failed handles.
- Store the `LoadContext`, loader callable or registry adapter, retained
  `CodecLoadResult`, retained loaded `FieldValue`, retained error, and
  inspectable provenance/evidence needed to explain how the field was loaded.
- Implement payload access so the first demand invokes the loader exactly once,
  stores either the typed `CodecLoadResult` or the failure, and subsequent
  demands return the retained payload or re-raise the retained error.
- Implement eager handle loading as the same path used by payload access, not
  a separate state transition.
- Preserve `FieldValue`-compatible attributes read by runtime code: `payload`,
  `schema`, `metadata`, and `collate_policy`.
- Update `Sample`/`FieldContainer` acceptance and annotations only enough to
  store loaded `FieldValue`, raw payloads, or `SampleField` without changing
  existing loaded-field semantics.
- Add tests for no-load `field()` access, load-on-`payload`, `get()`,
  `require()`, expected-type validation, eager loading, failed-state
  retention, repeated access, public `field_items()`, shallow/deep copy
  behavior, contracts, and LIST collation compatibility.
- Add or update package import tests only if `SampleField` becomes part of
  `rphys.data.__all__`; otherwise assert canonical submodule import remains
  lightweight.

## Out-of-Scope Work

- `SampleBuilder`, `SampleBuildContext`, requested locator normalization,
  `IndexItem` provenance joining, datasource scans, split/view/index manifest
  construction, probe orchestration, and eager build orchestration.
- Cross-sample caches, cache invalidation policy, retry/reset APIs, async
  loading, cancellation, thread safety, device movement, tensor conversion
  beyond existing payload-demanding `map_tensors_()` behavior, and operation
  pipelines.
- Public loader handler interfaces, public fake codecs, real codecs, optional
  video/array dependencies, filesystem discovery, network access, raw dataset
  fixtures, or dataset SDK integrations.
- Changing `LoadContext` into a datasource-aware context or adding record,
  item, manifest, locator, alignment, member, fingerprint, or model-formatting
  semantics to codec contexts.
- Replacing loaded `FieldValue` behavior, introducing a parallel `LazySample`
  container, replacing handles with loaded values inside `Sample`, or erasing
  retained diagnostics after load.
- Redesigning collation policy, adding stack/pad behavior, or adding implicit
  full-load fallbacks for unsupported indexes.

## Constraints

- Keep base imports lightweight. `rphys.data.sample_fields` may import
  `rphys.io.codecs` records if needed, but package import tests must prove this
  does not pull in heavy optional modules, datasource packages, builders, or
  test support.
- Preserve public method names on `FieldContainer`, `Sample`, and `Batch`.
  Annotation changes must be additive and must not force users of loaded
  samples to change code.
- Keep the lazy handle stored as the field object in `_FieldEntry.value`.
  Wrapping a lazy handle as `FieldValue.payload` is a blocker.
- Do not mutate `FieldView`, `FieldRef`, `LoadContext`, or codec result
  records. Keep descriptor provenance recoverable by reference or copied
  primitive metadata.
- Add only error classes that are directly exercised and justified. Prefer
  existing typed codec/data errors when they already describe the failure.
- Keep tests license-safe, deterministic, and dependency-light.

## Assumptions

- `SampleField` can be made compatible with existing `FieldValue` access
  patterns without changing loaded sample meaning.
- Existing `CodecRegistry.load(context)` and `CodecLoadResult.field_value`
  provide enough of the load boundary for this phase.
- Loader callables in unit tests may be simple dependency-light fakes as long
  as they return real `CodecLoadResult` objects and expose call counts.
- Package-level `rphys.data` re-export is optional. Canonical import from
  `rphys.data.sample_fields` is acceptable if it keeps import boundaries
  clearer.
- Contract tests can document payload-demanding access semantics without
  adding a new public runtime container class.

## Scope Contract

`rphys.data.sample_fields` owns lazy field handles for this phase. A
`SampleField` represents one logical runtime field that has enough
datasource-neutral codec context to materialize itself later. It must behave as
a field object from the perspective of `Sample.field()`, `role()`, and
`field_items()`, and as a payload provider from the perspective of `get()`,
`require()`, expected-type validation, LIST collation, and other code that
reads `.payload`.

The state machine is intentionally narrow:

1. `unloaded`: the handle has context and loader evidence but no retained
   codec result or payload.
2. `loaded`: the handle has exactly one retained `CodecLoadResult` and exposes
   that result's `FieldValue.payload`, `schema`, `metadata`, and
   `collate_policy`.
3. `failed`: the handle retains the raised exception and enough context to
   inspect what was attempted; repeated payload access re-raises the retained
   error without retry.

The executor must not add retry, reset, cache policy, async state, public
loader registries, `LazySample`, builder behavior, or datasource-aware codec
contexts. Failure behavior must be typed and inspectable at the operation
boundary. If the existing error hierarchy cannot represent a required lazy
failure without ambiguity, stop for manager review before adding new public
errors.

## Scientific Contract Notes

- Sampling and temporal alignment: `SampleField` must preserve the
  `LoadContext.field_view` and its optional field-native `FieldIndex`; it must
  not reinterpret indexes as seconds, frames, subjects, members, or alignment
  semantics.
- Field roles, locators, schemas, and provenance: role-qualified
  `FieldLocator` ownership remains in `Sample`; intrinsic field key, schema,
  resources, and field metadata remain in `FieldRef`/`FieldView`/loaded
  `FieldValue`. Lazy handles must keep enough context/result evidence to trace
  the source of a payload after load.
- Masking, filtering, normalization, and aggregation order: no such
  operations are introduced. Payload bytes/objects are whatever the codec
  returns inside `CodecLoadResult.field_value`.
- Subject identity, splits, leakage, and grouping: this phase must not invent
  subject, split, sample, record, item ID, or grouping semantics. Builder-side
  datasource provenance is Phase 4.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: missing runtime fields still raise existing
  `MissingFieldError`; payload validation still uses `FieldTypeError` and
  `FieldSchemaError`; unsupported field indexes remain codec/slice failures
  from the codec boundary. This phase does not inspect signal values or sample
  rates.

## Design Impact

- Maintainability: keep lazy state in one module and keep container changes
  small so loaded runtime behavior remains easy to reason about.
- Extensibility: expose state/result/error/context evidence as stable
  read-only observations, but avoid committing to cache, retry, async, or
  builder policies before real use requires them.
- Lightweight import policy: avoid heavy dependencies and avoid imports from
  datasource packages, builder modules, or tests in package code.
- Source-tree boundaries: `rphys.data.sample_fields` owns runtime lazy
  handles; `rphys.io.codecs` owns codec contracts and registry loading;
  `rphys.data.containers` owns field storage and payload-demanding access;
  Phase 4 will own sample construction and provenance joining.

## Future Compatibility

- Phase 4 can create `SampleField` instances from `IndexItem`/`FieldView`
  records and call eager load without changing the state machine introduced
  here.
- Real codecs can later add codec-specific metadata inside
  `CodecLoadResult.metadata` without changing `SampleField` storage.
- If operations later need lazy-aware batching or device movement, they should
  build on documented payload-demanding behavior rather than changing
  `field()` to load.
- A future cache policy, retry API, or async loader must be additive and must
  not erase retained load/failure diagnostics from this phase.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add a parallel `LazySample` container | The approved design requires lazy handles to live inside existing `Sample` and satisfy public `FieldContainer` behavior. |
| Store `SampleField` as `FieldValue.payload` | This would make `Sample.field()` return a wrapper around the handle and violates DD-6/DD-7 plus the assignment stop conditions. |
| Replace the handle with the loaded `FieldValue` after first load | This erases state, context, retained result, and failure diagnostics that must remain inspectable. |
| Add retry/reset/cache policy now | The phase only needs single-attempt retained state; cache and retry semantics are unapproved future behavior. |
| Make `LoadContext` datasource-aware | Codec contexts are intentionally datasource-neutral; builder-side record/item provenance belongs to Phase 4. |
| Redesign collation for lazy values | Existing LIST collation can remain payload-demanding through `.payload`; policy expansion is outside Stage 4 Phase 3. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| No public retry/reset/cache API for failed or loaded handles | Approved scope requires retained one-shot state only. | A later roadmap phase accepts explicit cache or retry semantics. |
| No async or concurrent load coordination | Current runtime is dependency-light and synchronous. | Real codec integrations require concurrency semantics. |
| `SampleField` compatibility may require local annotation widening in container APIs | Runtime compatibility must land before builder construction. | Static typing or downstream extension pressure shows a cleaner shared field-object alias is needed. |

## Loaded Runtime Compatibility Risks

- Existing callers may assume every `Sample.field()` return is a fully loaded
  `FieldValue`. Tests must preserve loaded fields while documenting that lazy
  handles can be returned without loading.
- Existing `set_field()` wraps non-`FieldValue` objects as raw payloads. The
  executor must make `SampleField` acceptance explicit so the handle remains
  the stored field object.
- `expected_type` validation touches `.payload`; this will load lazy fields.
  Tests must distinguish `field(locator)` with no validation from
  payload-demanding access.
- `map_tensors_()` and LIST collation touch payloads today. If lazy field
  loading through those paths causes broad behavior changes or collation
  redesign pressure, stop for manager review.
- Copy behavior can accidentally duplicate loader state or lose retained
  diagnostics. Shallow copy should be explicit about aliasing; deep copy must
  either work predictably or fail through documented behavior without changing
  loaded-field copies.

## Reviewability

- Expected PR size and shape: small-to-medium runtime PR with one new data
  module, minimal container/package edits, and focused unit/contract/package
  tests.
- Files and areas to inspect: `src/rphys/data/sample_fields.py`;
  `src/rphys/data/containers.py`; optional `src/rphys/data/__init__.py`;
  `tests/unit/rphys/data/test_sample_fields.py`; updated container,
  contract, collation, and package import tests; lazy runtime contract tests.
- Scope-control checks: no product code under `src/rphys/io` except if a
  directly required type import adjustment is proven necessary; no
  `sample_builders.py`; no datasource imports; no public fake codec; no heavy
  optional imports; no root `rphys` re-exports.
- Review focus: state transitions, no-load `field()` access, one-shot load
  behavior, failed-state retention, loaded-sample compatibility, import
  boundaries, and clear tests for payload-demanding paths.

## Implementation Steps

1. Add the `SampleField` module and tests for construction, state inspection,
   retained context, unloaded attributes that do not require payload, and
   successful load through a loader returning `CodecLoadResult`.
2. Implement one-shot payload/eager loading and retained failure behavior,
   including repeated access semantics and inspectable retained result/error.
3. Update container acceptance and annotations so `SampleField` is stored as a
   field object, while loaded `FieldValue` and raw payload wrapping keep their
   current behavior.
4. Add compatibility tests for `Sample.field()`, `get()`, `require()`,
   expected-type/schema validation, `field_items()`, `role()`, copy behavior,
   `SampleContract`, and LIST collation.
5. Decide package export shape based on import-boundary evidence: either
   re-export `SampleField` from `rphys.data` with package tests, or keep only
   `rphys.data.sample_fields` as the public home and test that import path.
6. Run targeted checks, then the required suite and PR-preparation gates,
   recording any unavailable command with a reason before PR submission.

## Test Plan

### Package Suite

- Status: required if `SampleField` is re-exported from `rphys.data`; otherwise
  required as a focused import-boundary assertion for canonical submodule
  import.
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`.
- Required assertions or deferral reason: verify exact `__all__` expectations,
  no root re-export, lightweight import, and no heavy optional, datasource,
  builder, or `tests.support` imports. Do not defer if package public surface
  changes.

### Unit Suite

- Status: required.
- Expected paths: new `tests/unit/rphys/data/test_sample_fields.py`; updates
  to `tests/unit/rphys/data/test_containers.py`,
  `tests/unit/rphys/data/test_contracts.py`, and
  `tests/unit/rphys/data/test_collation.py` as needed.
- Required assertions or deferral reason: construction and state; no-load
  `field()` access; payload-triggered load exactly once; eager load uses the
  same path; retained `CodecLoadResult`; retained and re-raised failure;
  schema/metadata/collate policy exposure; container storage without wrapping;
  loaded `FieldValue` regression coverage; payload-demanding access behavior.

### Contract Suite

- Status: required.
- Expected paths: `tests/contracts/test_runtime_core_contract.py` and new or
  existing lazy runtime contract coverage under `tests/contracts`.
- Required assertions or deferral reason: executable EX-1 behavior at the
  handle/sample level; `FieldContainer` remains valid; loaded sample contract
  examples still pass; lazy handles preserve provenance/result/failure
  evidence without adding builder, datasource, or cache semantics.

### Integration Suite

- Status: deferred by default.
- Expected paths: `tests/integration/test_runtime_collation.py` only if
  runtime/container changes cannot be adequately covered by unit and contract
  tests.
- Required assertions or deferral reason: not required unless lazy handle
  behavior crosses into a multi-component runtime flow beyond current
  unit/contract coverage. If added, keep fixtures synthetic and
  dependency-light.

### E2E Suite

- Status: deferred.
- Expected paths: no e2e files are currently present.
- Required assertions or deferral reason: Phase 3 does not include full
  datasource-to-sample construction or user workflow behavior; Phase 4/5 may
  revisit if a vertical slice is approved.

### Acceptance Suite

- Status: deferred.
- Markers affected: none expected.
- Required assertions or deferral reason: no raw datasets, hardware, network,
  GPU, long-running checks, or optional dependencies are in scope.

## Risks

- `SampleField` may be hard to make `FieldValue`-compatible without either
  subclassing or carefully widening container typing. Keep the implementation
  minimal and stop if public loaded behavior would change.
- Failure retention may expose the need for a new public lazy-field error. Add
  no placeholder error; stop if existing typed codec/data errors cannot
  represent the behavior clearly.
- Import-boundary changes can accidentally make `rphys.data` import codec,
  datasource, or test-support modules too eagerly. Package tests must cover
  the chosen export shape.
- Copy/deepcopy and `map_tensors_()` may reveal policy questions not settled
  by the assignment. Preserve existing loaded behavior and stop if lazy policy
  would need a broad redesign.

## Stop Conditions

- Loaded `Sample` contracts must be broken or existing loaded `FieldValue`
  behavior must be replaced.
- `SampleField` must be wrapped as `FieldValue.payload` instead of stored as
  the field object.
- Loading must replace the handle in the sample and erase retained
  diagnostics, context, provenance, or load result.
- Implementation requires a parallel `LazySample` container, `SampleBuilder`,
  datasource scanning, datasource-aware codec contexts, public loader handler
  interfaces, broad cache/retry/reset policy, async state, or collation
  redesign.
- Import-boundary tests show heavy optional modules, datasource packages,
  builders, or test support being imported by lightweight package imports.
- A public API or scientific behavior is needed that is not traced to FR-4,
  FR-6, FR-7, DD-6, DD-7, DD-8, DD-10, DD-12, or EX-1.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/data/test_sample_fields.py
uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py tests/unit/rphys/data/test_contracts.py tests/unit/rphys/data/test_collation.py
uv run pytest tests/contracts/test_runtime_core_contract.py
make test-unit
make test-contract
make test-package
```

Conditional commands:

```sh
make test-integration
make test-e2e
make test-acceptance
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check origin/develop...HEAD
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: add `SampleField` and state tests first; then
  loader/eager/failure retention; then container compatibility; then
  contract/package hardening.
- Tests to run with each slice: targeted `uv run pytest` for the new
  `test_sample_fields.py` while building the handle; add container, contract,
  collation, and package tests as those surfaces are touched; finish with
  `make test-unit`, `make test-contract`, `make test-package`,
  `make validate-pr`, `make test-summary`, and PR-range diff check.
- Decisions the executor must not revisit: no `LazySample`; no wrapping lazy
  handles as payloads; no replacement of handles after load; no retry/reset,
  async, cache, datasource-aware codec context, builder, or collation redesign.
- Conditions that require stopping for the manager: any stop condition above,
  any untraced public API need, or any package import-boundary regression that
  cannot be fixed with local import restructuring.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed on the fast path
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: implemented and locally validated
- Implementation summary:
  - Added `rphys.data.sample_fields` with public `SampleField` and
    `SampleFieldState`. `SampleField` subclasses `FieldValue` so existing
    containers store the lazy handle as the field object rather than wrapping
    it as a payload.
  - Implemented the narrow lazy state machine: unloaded handles retain
    `LoadContext` and a private loader; payload/eager access loads once and
    retains the `CodecLoadResult`; failed loads retain and re-raise the same
    error without retry.
  - Preserved loaded runtime behavior while documenting the container as
    `FieldValue`-compatible storage. `Sample.field()`, `role()`, and
    `field_items()` return handles without loading; payload-demanding paths
    such as `get()`, `require()`, expected-type validation, and LIST collation
    load through `.payload`.
  - Kept `SampleField` canonical in `rphys.data.sample_fields` rather than
    package-level `rphys.data` to avoid import cycles and preserve lightweight
    codec import boundaries.
  - Added unit and contract coverage for initial/loaded/failed states,
    successful load-once behavior, eager loading, retained failures, invalid
    loader results, no-load container field access, payload-demanding sample
    access, sample contracts, LIST collation, copy behavior, and import
    boundaries.
- Implementation validation:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py tests/unit/rphys/data/test_collation.py`: passed, 34 tests after copy/metadata fixes.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_lazy_sample_field_contract.py tests/contracts/test_runtime_core_contract.py`: passed, 9 tests.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py`: passed, 18 tests.
  - `make test-package`: passed, 21 tests.
  - `make test-unit`: passed, 298 tests.
  - `make test-contract`: passed, 33 tests.
  - `make validate-pr`: passed; lock check passed, harness summary wrote
    `build/test-summary.md`, package 21, unit 298, contract 33, integration
    1, e2e/acceptance not present, build succeeded, and `git diff --check`
    was clean.
- Refinement summary: not needed
- Pre-submit blocker gate: passed after local validation and manager review
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known

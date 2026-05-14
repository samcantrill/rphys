# Phase 1 Execution Plan: Codec Public Contract Foundation

## Metadata

- Status: implemented; ready for PR
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Codec Public Contract Foundation
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 1: Codec Public Contract Foundation`
- Branch: `agent/codecs-lazy-samples-p1-codec-contract-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p1-codec-contract-foundation`
- Phase execution plan path: `docs/roadmap/stage-4/phases/codec-contract-foundation.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/phases/codec-contract-foundation-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; maintainer approval is
  supplied by the phase assignment request
- Draft pass: completed in this artifact
- Refine pass: not needed unless implementation exposes a blocker in public
  context/result shapes, import boundaries, or approved error taxonomy
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Establish the Stage 4 dependency-light IO public contract in
`rphys.io.codecs`: structural codec surface, typed datasource-neutral
probe/load/save context and result records, narrow save metadata policy, and
intentional import/error boundaries, without adding registry operation
behavior, runtime lazy samples, builders, real codecs, or datasource/export
workflow behavior.

## Full-Plan Context

Preparation Phase 1 added the public runtime `FieldContainer` protocol.
Preparation Phase 2 froze `FieldSpec` and clarified `FieldIndex` as a narrow
base interface. This Phase 1 is the first primary Stage 4 phase and provides
the IO contract objects that later phases will consume. Phase 2 owns explicit
codec resolution and dependency-light codec behavior. Phase 3 owns lazy
`SampleField` runtime compatibility. Phase 4 owns the `SampleBuilder` bridge
and datasource provenance. Phase 5 owns closeout docs and validation. Those
later behaviors are explicit exclusions from this phase.

## Source Phase Summary

- Goal: establish the Stage 4 IO public contract without implementing runtime
  lazy samples or full registry operation behavior.
- Required scope: `src/rphys/io/codecs.py`, conditional
  `src/rphys/io/__init__.py`, only exercised additions in
  `src/rphys/errors.py`, package import/export tests, focused IO unit tests for
  records/errors/imports, and this phase documentation artifact.
- Required checkpoints: `FieldCodec` is structural/duck-typed;
  `CodecCapabilities`, `IOContext`, `LoadContext`, `SaveContext`,
  `CodecProbeResult`, `CodecLoadResult`, and `CodecSaveResult` are typed,
  minimal, and datasource-neutral; `SaveContext.target` is a `FieldRef`;
  `MetadataSavePolicy` is a narrow enum; package imports remain lightweight.
- Acceptance criteria: typed records instantiate with Stage 2/3 descriptors;
  descriptors are not mutated or given load/save methods; root `rphys` remains
  unchanged; `rphys.io.codecs` does not import datasource modules or heavy
  optional stacks; any new concrete error is exercised and context-rich.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/io/__init__.py` currently exports only Stage 3 descriptor names
  and its docstring explicitly says the package does not provide codecs,
  builders, registries, or runtime payload hooks. `src/rphys/io/codecs.py` does
  not exist yet.
- Existing descriptor behavior:
  `src/rphys/io/resources.py`, `src/rphys/io/fields.py`, and
  `src/rphys/io/indexes.py` define frozen, unhashable descriptor objects.
  `ResourceRef` preserves URI/protocol/options without opening resources.
  `FieldRef` preserves ordered `ResourceRef`s, key, schema, and field metadata
  without member, role, codec, or field-index semantics. `FieldView` binds an
  optional `FieldIndex` without payload, locator, or alignment behavior.
  `TemporalIndexSlice` is field-native, integer, and half-open.
- Existing runtime field behavior:
  `src/rphys/data/fields.py` defines frozen `FieldSpec` and loaded
  `FieldValue`. Phase 1 records may refer to these value objects, but must not
  add runtime `SampleField` behavior or change `Sample` accessors.
- Existing error behavior:
  `src/rphys/errors.py` already exposes broad `RemotePhysCodecError`,
  `RemotePhysDependencyError`, `RemotePhysIOError`, `RemotePhysFieldError`, and
  `RemotePhysSliceError` bases. Existing tests assert exact `errors.__all__`
  ordering and inheritance. This phase must not add placeholder resolution,
  sample-build, or lazy-field errors.
- Existing tests or harness behavior:
  `tests/package/test_import.py` asserts exact `rphys.io` exports and root
  non-exports. `tests/package/test_import_boundaries.py` lists lightweight
  imports and guards heavy optional modules. `tests/unit/rphys/io/` covers
  descriptor immutability, serialization, lack of IO runtime hooks, and no
  registry/factory behavior. `tests/unit/rphys/test_errors.py` covers broad
  and concrete error surfaces. `tests/README.md` requires package, unit,
  contract, integration, e2e, acceptance, and support tests to stay separated
  by intent.
- Import-boundary or dependency constraints:
  `rphys.io.codecs` must stay stdlib-only plus existing dependency-light
  `rphys.data` and `rphys.io` descriptors. It must not import
  `rphys.datasources`, array/video/plotting/deep-learning libraries, dataset
  SDKs, runtime sample-field modules, builder modules, export modules, or test
  support codecs.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is clean
  on `develop` tracking `origin/develop`
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-p1-codec-contract-foundation` and was clean
  before this plan edit
- Current `develop` base: `32aa7d1 docs: record stage 4 prep 2 cleanup`
- Branch setup note: the branch already contains
  `bd8c506 plan: add phase 1 assignment`; preserve it and add only the
  execution-plan commit for this pass
- Earlier phase dependency status: Prep 1 and Prep 2 are merged and recorded
  in the implementation plan
- Push/PR infrastructure status: assignment records GitHub auth, push, PR
  creation, and merge as exercised successfully in earlier phases; this
  planning pass does not push or open a PR
- Stop condition if isolation cannot be maintained: stop before product code
  edits or PR work and return to the manager if the phase branch/worktree
  cannot remain dedicated to Phase 1

## In-Scope Work

- Add `src/rphys/io/codecs.py` as the owning public module for Stage 4 codec
  contract records and structural codec typing.
- Define a structural/duck-typed `FieldCodec` surface for capability metadata
  and `probe`, `load`, and `save` operation methods without requiring
  inheritance from an rphys base class.
- Define `CodecCapabilities` as a minimal typed value object for declared
  operation support needed by later capability checks. This phase does not select,
  rank, match, or execute codecs.
- Define datasource-neutral typed records:
  `IOContext`, `LoadContext`, `SaveContext`, `CodecProbeResult`,
  `CodecLoadResult`, and `CodecSaveResult`.
- Ensure `LoadContext` is centered on a `FieldView`; ensure `SaveContext.target`
  is a `FieldRef`; ensure result records can carry the minimal approved
  `FieldSpec`, `FieldValue`, target/resource, and primitive metadata evidence
  needed by later phases without importing datasource provenance.
- Define `MetadataSavePolicy` as a small save-context enum with only the
  exercised Stage 4 values: default reference-only behavior and explicit
  field-metadata inclusion for codecs that support it.
- Use frozen/slotted dataclasses or equivalent immutable records where
  appropriate; copy or freeze mappings so caller mutation cannot change
  context/result provenance after construction.
- Add only concrete errors in `src/rphys/errors.py` that this phase directly
  exercises. Prefer existing broad bases when no concrete Stage 4 operation is
  implemented. Resolution, sample-build, and sample-field-state errors are
  deferred.
- Update `src/rphys/io/__init__.py` only if package tests show codec contract
  names can be re-exported without increasing import cost. Keep canonical
  imports from `rphys.io.codecs` valid either way.
- Add focused package/unit tests for record construction, immutability or
  mutation-detachment, `SaveContext.target` type, enum values, structural
  codec surface shape, descriptor non-mutation, error inheritance/context when
  concrete errors are added, exact exports, root non-exports, and lightweight
  imports.

## Out-of-Scope Work

- `CodecRegistry`, resolver matching, codec registration, deterministic
  selection, ambiguity handling, priority/order semantics, symbolic codec
  names, plugin discovery, process-global registries, or global default
  registries.
- Dependency-light synthetic codecs, real codecs, test-support codec fixtures,
  probe/load/save execution behavior, call counters, full-load fallback checks,
  optional dependency operation failures, or codec round trips.
- `SampleField`, lazy load state, payload-triggered loading, eager loading,
  retry/reset/cache policy, async behavior, or any change to `Sample`/`Batch`
  runtime accessors.
- `SampleBuilder`, `SampleBuildContext`, requested-locator normalization,
  `IndexItem` build/probe behavior, record provenance joining, or missing
  requested-field validation.
- Datasource scanning, datasource adapters, views, splits, manifests, item IDs,
  descriptor fingerprints, datasource-aware codec contexts, or imports from
  `rphys.datasources`.
- Metadata handler interfaces, manifest writers, load-time metadata
  persistence, export layouts, export target/idempotency policy, derived
  datasource assembly, or export orchestration.
- New index types, seconds/spatial slices, member binding, cross-field
  alignment, resource selector semantics, model formatting, training loaders,
  operation pipelines, or root `rphys` convenience exports.

## Assumptions

- A single `rphys.io.codecs` module is sufficient for the public contract
  foundation; a future package split can preserve this import path as a facade
  if real codec families justify it.
- Phase 1 can expose structural codec typing and typed context/result records
  before any resolver executes them, as long as no matching or operation
  behavior is implemented here.
- `LoadContext` and `SaveContext` stay datasource-neutral. Builder/sample
  layers will join `RecordRef` and item metadata later without reversing the
  `rphys.io` to `rphys.datasources` dependency direction.
- `SaveContext.target: FieldRef` is the accepted Stage 4 save target shape;
  export layouts and derived datasource behavior can wrap it later.
- `MetadataSavePolicy` needs only `REFERENCE_ONLY` and
  `INCLUDE_FIELD_METADATA` now. Additional save/export semantics require later
  roadmap approval.
- Public result records should remain narrow even if this leaves room for
  later additive fields when real codecs expose stronger evidence.

## Scope Contract

`rphys.io.codecs` is a codec contract module, not a codec catalog, resolver,
datasource layer, runtime sample layer, or export framework. The executor must
keep public names code-backed, minimal, and dependency-light.

`FieldCodec` must be structural/duck-typed. A downstream object should be able
to provide the required capability and operation attributes without inheriting
from an rphys base class. This phase may define method signatures for `probe`,
`load`, and `save`, but it must not implement operation dispatch,
registration, matching, or fallback behavior.

`CodecCapabilities` must describe only declared operation support and the
minimum static facts later capability checks will need. It must not parse resources,
inspect files, import optional dependencies, rank codecs, or imply a hidden
registry.

`LoadContext` must reference the `FieldView` being probed or loaded. Through
that view, a codec can inspect the `FieldRef`, ordered `ResourceRef`s, schema,
metadata, and optional field-native index. It must not contain `FieldLocator`,
`RecordRef`, `IndexItem`, datasource schema, split, group, item ID,
fingerprint, alignment, member binding, model, trainer, or transform fields.

`SaveContext` must use `target: FieldRef` and
`metadata_policy: MetadataSavePolicy`. It may carry only primitive/reference
metadata needed for explicit save behavior. It must not define export layouts,
idempotency, manifest writes, derived datasource refs, metadata handlers, or
implicit load-time metadata persistence.

`CodecProbeResult` must be lightweight and must not contain loaded payload
data. It may carry a `FieldSpec` and primitive metadata sufficient to describe
what a codec can materialize. `CodecLoadResult` must carry a loaded
`FieldValue` or an equivalently explicit field-value result object without
requiring a `Sample` or `SampleField`. `CodecSaveResult` must carry enough
target/resource metadata to confirm what was saved to the `FieldRef` target
without creating export manifests or datasource objects.

All records must detach mutable caller inputs where they expose metadata or
options. Equality may be value-based where it follows local dataclass patterns,
but no public hash contract should be introduced for records with mappings or
mutable payload references. Descriptor inputs must not be mutated, wrapped with
load/save methods, or coerced into datasource-aware objects.

## Scientific Contract Notes

- Sampling and temporal alignment: contexts pass through any existing
  `FieldView.field_index` exactly as descriptor data. This phase does not
  define slicing support, sample-rate conversion, seconds conversion,
  resampling, padding, spatial crops, or cross-field alignment.
- Field roles, locators, schemas, and provenance: codec contexts operate on
  intrinsic `FieldRef`/`FieldView` identity, not role-qualified
  `FieldLocator`s. Datasource record provenance and item metadata stay out of
  IO contexts and remain builder/sample responsibilities in later phases.
- Masking, filtering, normalization, and aggregation order: no payload
  transformation, mask handling, filtering, normalization, aggregation, or
  collation behavior is introduced.
- Subject identity, splits, leakage, and grouping: no subject, split, group,
  record, leakage, or dataset partition semantics are added to codec contexts
  or results.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: no payload-level validation exists in Phase 1. Invalid
  record components must fail loudly through existing descriptor errors,
  `TypeError`, `ValueError`, or an exercised codec-contract error. Unsupported
  slice operation behavior belongs to Phase 2 and must not be simulated here.

## Design Impact

- Maintainability: centralizes Stage 4 IO contract names in one module and
  prevents Stage 3 descriptors from accumulating load/save methods.
- Extensibility: structural codec typing allows downstream codec objects to
  compose with rphys without mandatory inheritance; later registries can
  validate behavior at operation boundaries.
- Lightweight import policy: implementation remains stdlib-only plus existing
  data and IO descriptors, with package tests guarding optional dependency and
  datasource imports.
- Source-tree boundaries: `rphys.io.codecs` owns codec contracts, contexts,
  capabilities, results, and save metadata policy; `rphys.errors` owns only
  exercised concrete diagnostics; `rphys.data.sample_fields`,
  `rphys.data.sample_builders`, and `rphys.datasources` remain untouched.

## Future Compatibility

Later registry behavior can consume `FieldCodec`, `CodecCapabilities`, and the
typed contexts/results without changing descriptor classes. Later
`SampleField` and `SampleBuilder` phases can join datasource provenance around
these datasource-neutral records. Later export planning can wrap
`SaveContext.target` rather than replacing the single-logical-field target
contract. Real codecs may motivate additive result fields or a package split,
but those changes must preserve the public `rphys.io.codecs` import path and
the explicit exclusions recorded here.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add codec methods directly to `FieldRef` or `FieldView` | Breaks Stage 3 descriptor purity and couples serializable descriptors to IO execution. |
| Require all codecs to subclass a stateful rphys base class | Over-couples downstream extensions; structural/duck typing is the approved design. |
| Add `CodecRegistry` behavior with the public records | Registry operation semantics are Phase 2 scope and need separate review. |
| Put `RecordRef` or `IndexItem` on codec contexts | Reverses the `rphys.io`/`rphys.datasources` dependency direction and pulls builder provenance into IO. |
| Use `ResourceRef` alone as the save target | Too narrow for logical fields and compound resources; accepted design locks `SaveContext.target: FieldRef`. |
| Add public metadata handlers or export targets now | Stage 8 owns export layouts, manifest writing, idempotency, and derived datasource assembly. |
| Add a public fake or synthetic codec for examples | Validation codecs belong to later test-support behavior, not this contract-foundation phase. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Minimal context/result fields may need additive extension after real codec evidence | The phase intentionally avoids freezing manifest/export/datasource semantics early. | A later real codec or export phase needs provenance that cannot be carried without new fields. |
| `CodecCapabilities` starts as declaration data without executable matching behavior | Phase 1 owns declarations only, and operation behavior remains excluded. | A later approved phase needs additional declaration fields that cannot be added compatibly. |
| Package-level `rphys.io` re-export may be deferred | Canonical `rphys.io.codecs` imports are enough if package import tests show re-export cost or ordering risk. | Package tests and docs settle that re-export is lightweight and useful. |

## Reviewability

- Expected PR size and shape: small public API diff adding one IO module,
  conditional IO package exports, focused error additions only if exercised,
  package tests, unit tests, and docstrings. No runtime or datasource behavior
  should appear.
- Files and areas to inspect:
  `src/rphys/io/codecs.py`,
  `src/rphys/io/__init__.py`,
  `src/rphys/errors.py`,
  `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`,
  `tests/unit/rphys/io/test_codecs.py` or source-mirrored equivalent,
  `tests/unit/rphys/test_errors.py`, and existing descriptor tests under
  `tests/unit/rphys/io/` for no load/save hook regressions.
- Scope-control checks: no files under `src/rphys/data/sample_fields.py`,
  `src/rphys/data/sample_builders.py`, `src/rphys/datasources`, registry
  modules, codec catalog modules, export modules, or `tests/support` synthetic
  codecs; no root exports; no heavy optional dependencies; no descriptor
  mutation; no operation dispatch.

## Implementation Steps

1. Add `src/rphys/io/codecs.py` with module docstring, `__all__`, structural
   `FieldCodec`, `CodecCapabilities`, `IOContext`, `LoadContext`,
   `SaveContext`, `CodecProbeResult`, `CodecLoadResult`, `CodecSaveResult`,
   and `MetadataSavePolicy`. Keep records minimal, frozen/slotted where
   appropriate, and datasource-neutral.
2. Implement context/result coercion and validation narrowly: require
   `LoadContext.field_view` to be a `FieldView`, require
   `SaveContext.target` to be a `FieldRef`, default metadata policy to
   reference-only, detach metadata mappings, preserve ordered resources through
   descriptors, and avoid adding behavior to descriptors.
3. Update public imports intentionally. Keep root `rphys` unchanged. Add
   `rphys.io.codecs` package/import coverage, and update `rphys.io.__all__`
   only if re-exporting code-backed codec contract names remains lightweight.
4. Update `src/rphys/errors.py` and error tests only for concrete codec
   contract errors that this phase actively exercises. Do not add
   `CodecResolutionError`, dependency-operation errors, sample-build errors,
   or sample-field-state errors before their behavior exists.
5. Add focused package and unit tests for record construction, frozen or
   mutation-detached metadata behavior, `SaveContext.target` type, enum values,
   structural codec surface shape through a local no-op test class only,
   descriptor non-mutation, import boundaries, and exact exports.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.io.codecs` imports
  successfully and exposes only code-backed Phase 1 names; root `rphys` does
  not re-export codec names or errors; `rphys.io.__all__` is updated only if
  re-exported names are intentional; importing `rphys.io.codecs` does not load
  heavy optional modules, `rphys.datasources`, sample-field modules, builder
  modules, export modules, or test-support modules.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/io/test_codecs.py` or source-mirrored
  equivalent, `tests/unit/rphys/test_errors.py` when concrete errors are
  added, and existing `tests/unit/rphys/io/test_field_refs.py`,
  `tests/unit/rphys/io/test_resources.py`, and
  `tests/unit/rphys/io/test_indexes.py` as regression anchors if touched.
- Required assertions or deferral reason: context/result records construct
  with valid `FieldView`, `FieldRef`, `FieldSpec`, `FieldValue`, and
  `ResourceRef` inputs; mutable metadata/options are detached; records reject
  invalid descriptor components loudly; `SaveContext.target` must be a
  `FieldRef`; `MetadataSavePolicy` contains only approved values; structural
  `FieldCodec` does not require inheritance; descriptors gain no `load`,
  `save`, `probe`, `codec`, or `payload` hooks; any concrete error inherits
  existing broad bases and preserves message/context.

### Contract Suite

- Status: deferred for this phase
- Expected paths: none required in Phase 1
- Required assertions or deferral reason: this phase defines construction and
  import contracts only. Executable probe/load/save, registry resolution,
  synthetic codec, lazy sample, and builder contracts belong to later phases.
  If the executor adds a public contract file, it must cover only Phase 1
  construction/import behavior and must not simulate future operation behavior.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no cross-component codec execution,
  datasource, runtime sample, builder, or export behavior is in scope.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end lazy sample
  materialization or save/export workflow exists in Phase 1.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real dataset, optional
  dependency, hardware, network, GPU, or long-running behavior is introduced.

## Risks

- Over-wide context or result fields could freeze datasource, manifest,
  alignment, member, or export semantics before evidence exists.
- Too many concrete error names could create placeholder API surface that later
  phases need to unwind.
- Re-exporting codec names from `rphys.io` could accidentally pull in
  datasource or heavy optional imports if the module boundary is not kept
  tight.
- A structural `FieldCodec` test could drift into synthetic codec operation
  behavior. Keep any local test class no-op and limited to protocol shape.
- `MetadataSavePolicy` wording could imply handler or manifest behavior.
  Tests and docstrings must state that metadata persistence is explicit save
  context only.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/io/test_codecs.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
uv run pytest tests/unit/rphys/test_errors.py
make test-package
make test-unit
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: create the codec contract module first; add
  context/result validation and metadata detachment second; update imports and
  package tests third; add only exercised error names fourth; run focused unit
  and package checks after each slice.
- Tests to run with each slice: `uv run pytest tests/unit/rphys/io/test_codecs.py`
  after module changes; package import tests after any `__all__` change; error
  tests after any `errors.py` change; finish with `make test-package`,
  `make test-unit`, and `git diff --check` before PR preparation.
- Decisions the executor must not revisit: `rphys.io.codecs` is the canonical
  import home; `FieldCodec` is structural; codec contexts are
  datasource-neutral; `SaveContext.target` is a `FieldRef`;
  `MetadataSavePolicy` is a narrow enum; root `rphys` remains without
  convenience exports; no registry, synthetic codec, `SampleField`,
  `SampleBuilder`, datasource scanning, metadata handler, or export behavior is
  in scope.
- Conditions that require stopping for the manager: implementation requires
  datasource-aware codec contexts, registry matching behavior, a public fake
  codec, real optional dependencies, metadata handler interfaces, export
  target/layout policy, descriptor mutation, a package tree instead of the
  `rphys.io.codecs` module, new scientific semantics for member/alignment or
  slicing, or public names not traced to FR-1/FR-6/FR-7 and DD-1/DD-2/DD-4/DD-5/DD-8.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: implemented and locally validated
- Implementation summary:
  - Added `rphys.io.codecs` as the canonical codec contract module with
    structural `FieldCodec`, `CodecCapabilities`, `IOContext`, `LoadContext`,
    `SaveContext`, `CodecProbeResult`, `CodecLoadResult`, `CodecSaveResult`,
    and `MetadataSavePolicy`.
  - Kept codec contexts datasource-neutral: load/probe contexts carry
    `FieldView`, save contexts carry `target: FieldRef`, and all primitive
    metadata mappings are detached and frozen.
  - Kept package-level `rphys.io.__all__` limited to Stage 3 descriptor names
    after contract tests confirmed codec names with `load`/`save`/`probe`
    methods must stay in `rphys.io.codecs`.
  - Added focused package/unit coverage for exact exports, import boundaries,
    record construction, invalid typed components, structural duck typing,
    descriptor non-mutation, and metadata detachment.
  - No concrete codec error classes were added; construction validation uses
    the existing broad `RemotePhysCodecError` because no operation-specific
    behavior exists in this phase.
- Implementation validation:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/io/test_codecs.py`: passed, 12 tests.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py`: passed, 16 tests.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/test_errors.py`: passed, 34 tests.
  - `make test-contract`: initially failed when codec names were package-level
    `rphys.io` re-exports; fixed by keeping canonical codec imports in
    `rphys.io.codecs`.
  - `make test-contract`: passed, 25 tests.
  - `make test-package`: passed, 19 tests.
  - `make test-unit`: passed, 271 tests.
  - `make validate-pr`: passed; lock check passed, harness summary wrote
    `build/test-summary.md`, package 19, unit 271, contract 25, integration
    1, e2e/acceptance not present, build succeeded, and `git diff --check`
    was clean.
  - `git diff --check`: clean.
- Refinement summary: not needed; manager resolved the import-boundary issue
  found by contract validation before PR preparation.
- Pre-submit blocker gate: passed after local validation and manager review
- PR preparation: completed; PR #23 opened against `develop`
- Automated review: completed; no blocking findings, local review checks passed
- Merge result: pending
- Cleanup: pending merge
- Remaining blockers: none known

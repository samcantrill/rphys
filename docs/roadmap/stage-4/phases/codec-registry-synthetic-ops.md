# Phase 2 Execution Plan: Explicit Registry And Synthetic Codec Operations

## Metadata

- Status: implemented; ready for PR
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Explicit Registry And Synthetic Codec Operations
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 2: Explicit Registry And Synthetic Codec Operations`
- Branch: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Phase execution plan path: `docs/roadmap/stage-4/phases/codec-registry-synthetic-ops.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-2-explicit-registry-and-synthetic-codec-operations`
- Assignment: `docs/roadmap/stage-4/phases/codec-registry-synthetic-ops-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; Phase 1 dependency is
  merged and recorded
- Draft pass: completed in this artifact
- Refine pass: not needed unless implementation exposes unapproved registry
  matching, public fake-codec, dependency, or provenance behavior
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Implement and validate explicit dependency-light codec registry behavior in
`rphys.io.codecs`, then prove probe, load, save, deterministic resolution,
typed failures, metadata policy handling, and ordered resource propagation
through a private synthetic test codec without adding runtime lazy samples,
builders, real codecs, discovery, export, or datasource behavior.

## Full-Plan Context

Preparation Phase 1 added the public runtime `FieldContainer` protocol.
Preparation Phase 2 froze `FieldSpec` and clarified `FieldIndex` as a base
interface. Primary Phase 1 added the dependency-light codec contract records in
`rphys.io.codecs`: structural `FieldCodec`, `CodecCapabilities`,
datasource-neutral load/save contexts, operation result records, and
`MetadataSavePolicy`.

This Phase 2 is the IO behavior phase. It adds explicit registry instances and
synthetic probe/load/save operation behavior so later phases can use a tested
codec boundary. Phase 3 owns lazy `SampleField` state and runtime container
compatibility. Phase 4 owns `SampleBuilder`, `IndexItem` provenance joining,
requested locator handling, and eager/lazy sample construction. Phase 5 owns
closeout docs, examples, and final validation. Those later runtime, builder,
and docs-closeout behaviors remain out of scope here.

## Source Phase Summary

- Goal: prove deterministic codec resolution and dependency-light
  probe/load/save behavior through explicit registry instances.
- Required scope: `src/rphys/io/codecs.py`; exercised codec diagnostics in
  `src/rphys/errors.py`; private `tests/support` synthetic codec helper or
  fixture; IO unit tests under `tests/unit/rphys/io/**`; codec contract tests
  under `tests/contracts/test_codec_contract.py` or equivalent; package tests
  only if public exports or import-boundary expectations change.
- Required checkpoints: explicit `CodecRegistry`; structural codec acceptance;
  capability/support matching for probe/load/save; no-match, ambiguous,
  unsupported operation/index, and dependency-unavailable failures; synthetic
  probe without load; indexed load without hidden full-resource fallback;
  single-field save to `SaveContext.target`; metadata policy behavior; ordered
  multi-resource propagation.
- Acceptance criteria: one matching codec resolves deterministically; missing
  and ambiguous matches fail with typed, context-rich diagnostics; unsupported
  operations and indexes fail loudly; dependency failures occur at the
  operation boundary; the synthetic codec remains private to tests/support;
  no global discovery, process-global mutable registry, public fake codec,
  descriptor mutation, datasource-aware codec context, manifest write, export
  layout, `SampleField`, or `SampleBuilder` behavior is introduced.

## Current Source And Harness Findings

- Existing `src/rphys/io/codecs.py` defines only Stage 4 contract records:
  `FieldCodec`, `CodecCapabilities`, `IOContext`, `LoadContext`,
  `SaveContext`, `CodecProbeResult`, `CodecLoadResult`, `CodecSaveResult`, and
  `MetadataSavePolicy`. There is no `CodecRegistry`, resolver, operation
  wrapper, support predicate, concrete codec, or operation failure wrapping.
- `FieldCodec` is currently a runtime-checkable structural protocol with
  `capabilities`, `probe`, `load`, and `save`. `CodecCapabilities` has
  operation booleans and metadata policies only; matching against a specific
  field view/context is not implemented yet.
- `LoadContext` and `SaveContext` are datasource-neutral and intentionally lack
  `record`, `index_item`, `locator`, `manifest`, and export-layout fields.
  This phase must preserve that boundary; builder-side datasource provenance is
  Phase 4.
- `CodecProbeResult`, `CodecLoadResult`, and `CodecSaveResult` are frozen,
  explicitly unhashable typed records. Metadata is copied to primitive,
  read-only mappings. `CodecSaveResult` defaults to target resources and
  preserves caller resource order.
- `src/rphys/io/__init__.py` still exports only Stage 3 descriptor names and
  its docstring says codecs live in `rphys.io.codecs`. Package tests assert
  Stage 4 names are not re-exported from `rphys.io`; if this phase changes
  that public surface, it must update and justify package tests.
- `src/rphys/errors.py` exposes broad `RemotePhysCodecError`,
  `RemotePhysDependencyError`, `RemotePhysIOError`, and
  `RemotePhysSliceError`, plus concrete Stage 1 through Stage 3 errors. Error
  tests assert exact `errors.__all__` ordering. Add only concrete Stage 4
  error names that this phase directly exercises.
- `src/rphys/io/fields.py` preserves `FieldRef.resources` order and explicitly
  does not define member, selector, alignment, codec, or payload semantics.
  `FieldView.field_index` is optional and field-native.
- `src/rphys/io/indexes.py` supports only `TemporalIndexSlice`; unknown
  serialized tags raise `UnsupportedFieldIndexError`. Registry or codec
  unsupported-slice behavior must not add a hidden full-load fallback.
- `src/rphys/data/fields.py` provides frozen/unhashable `FieldSpec` and loaded
  `FieldValue`. The synthetic codec may return these values but must not add
  lazy runtime behavior to them.
- Existing IO unit coverage is in `tests/unit/rphys/io/test_codecs.py` and
  currently checks contract-record construction, immutability, structural
  codec typing, datasource-neutral contexts, save target shape, result
  validation, descriptor purity, and no registry hooks.
- Existing contract coverage in `tests/contracts/test_lazy_io_contract.py`
  asserts Stage 3 descriptors remain serialization-only and `rphys.io` has no
  runtime or registry hooks. New codec contract coverage should use
  `rphys.io.codecs`, not mutate Stage 3 descriptor classes or the package root.
- `tests/package/test_import.py` asserts exact public exports and root
  non-exports. `tests/package/test_import_boundaries.py` imports
  `rphys.io.codecs` while checking that heavy optional modules, datasource
  modules, runtime sample-field modules, sample-builder modules, and
  `tests.support` are not imported.
- `tests/README.md` defines suite intent. `tests/support` is the right place
  for trusted private synthetic helpers, but the directory does not exist yet
  in this worktree; creating it is in scope only as test support.
- `pyproject.toml` has no runtime dependencies. Synthetic codec behavior must
  stay stdlib-only and use primitive, license-safe test data.
- Harness targets are split through Make includes. `make validate-pr` runs
  lock check, `make test-summary`, build, and diff check; `make test-summary`
  writes Markdown/JUnit artifacts under `build/test-summary*`.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` was
  clean on `develop` tracking `origin/develop` before this plan edit.
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops` and was clean
  before this plan edit.
- Current `develop` base: `bf93003 docs: record stage 4 phase 1 cleanup`.
- Branch setup note: the branch already contains
  `517f913 plan: add phase 2 assignment`; preserve it and add only the
  execution-plan commit for this pass.
- Earlier phase dependency status: Preparation Phases 1 and 2 and Primary
  Phase 1 are merged and recorded in the implementation plan.
- Push/PR infrastructure status: assignment records GitHub push and PR
  infrastructure as previously exercised; this planning pass does not push or
  open a PR.
- Stop condition if isolation cannot be maintained: stop before product code
  edits or PR work and return to the manager if the branch/worktree cannot
  remain dedicated to Phase 2.

## In-Scope Work

- Add `CodecRegistry` or equivalent explicit registry behavior in
  `src/rphys/io/codecs.py` with deterministic, instance-local codec storage.
- Register and resolve structural codec objects without requiring inheritance
  from an rphys base class.
- Validate the operation-specific structural shape at registration or
  operation boundary and raise typed diagnostics with operation and codec
  context.
- Match codecs by declared operation capability and field/context support.
  If adding an optional support predicate to the structural codec surface, keep
  it narrow, documented in `rphys.io.codecs`, behavior-tested, and free of
  symbolic names, plugin discovery, or public helper registries.
- Provide probe, load, and save operation wrappers that resolve exactly one
  codec, invoke the codec once, return typed result records, and preserve the
  supplied `LoadContext` or `SaveContext` without descriptor mutation.
- Add typed, exercised failure behavior for no match, ambiguous match,
  unsupported operation, unsupported field index, invalid codec shape,
  operation failure, and dependency-unavailable boundaries.
- Add private synthetic codec support under `tests/support` or local test
  fixtures. It should use primitive in-memory resources, record call counts,
  probe without loading, load only supported `FieldView.field_index` requests,
  reject unsupported indexes without full-load fallback, save one logical
  `FieldValue`, and exercise both metadata save policies.
- Add focused IO unit tests and codec contract tests for EX-2, EX-3, EX-4, and
  EX-5.
- Update package/import-boundary tests only if the public export surface
  intentionally changes. Keep root `rphys` unchanged.

## Out-of-Scope Work

- Global codec discovery, process-global mutable default registries, symbolic
  codec keys, plugin systems, config resolution, hidden priority heuristics,
  or registry state outside explicit instances.
- Real codecs, optional video/array dependencies, dataset SDKs, filesystem
  probing, network access, raw datasets, or production format support.
- Public fake codec exports, public examples that imply a supported synthetic
  format, or imports of test support from package code.
- Hidden full-resource fallback when a sliced/indexed view is unsupported.
- Metadata manifest writes, metadata handler interfaces, export targets,
  output layouts, idempotency policy, derived datasource assembly, or save
  orchestration beyond one `SaveContext.target`.
- `SampleField`, lazy field state, eager loading at runtime, payload-triggered
  loading, retry/reset/cache policy, async state, or changes to `Sample` and
  `Batch` accessors.
- `SampleBuilder`, `SampleBuildContext`, requested locator normalization,
  `IndexItem` provenance joining, datasource scanning, split/index manifest
  behavior, item IDs, fingerprints, member binding, alignment semantics, model
  formatting, operation pipelines, or training loaders.
- Public helper functions for matching/coercion or tests that rely on private
  helper names as extension points.

## Assumptions

- Phase 1 result/context records are sufficient for registry operation tests;
  if a real public context/result field is required, it must be additive,
  datasource-neutral, and traced to FR/DD/EX evidence.
- Explicit registry instances are the accepted extension point. Later config
  layers can wrap registries additively without changing the Phase 2 contract.
- Structural codec support can be validated through capability flags plus a
  narrow operation-specific support check; no mandatory base class or symbolic
  codec name is needed.
- Synthetic codec state and call counters belong in tests only and are not a
  public behavior guarantee.
- Existing broad dependency and slice error bases may be used where they give
  better semantics than adding placeholder concrete names.
- Package-level `rphys.io` re-exports can remain unchanged unless implementation
  evidence shows `CodecRegistry` should be exported from the package home.

## Scope Contract

`rphys.io.codecs` owns the public codec registry and operation boundary for
this phase. The registry must be explicit, deterministic, instance-local, and
dependency-light. It must select exactly one codec for a requested operation
and context or raise a typed, inspectable failure. It must not consult import
side effects, global mutable state, environment variables, filesystem paths,
entry points, or test support modules.

Codec extension remains structural and object-based. Registered objects do not
need to inherit from an rphys class, but the operation methods and
capabilities/support shape needed by registry behavior must be validated before
or during operation execution. Invalid shape should fail loudly with enough
context to identify the operation and missing/invalid attributes.

Probe and load operate on `LoadContext` with a `FieldView`. Save operates on a
`FieldValue` plus `SaveContext` whose target is a `FieldRef`. Operation
wrappers must return `CodecProbeResult`, `CodecLoadResult`, or
`CodecSaveResult` and reject or wrap wrong result types with typed codec
diagnostics. They must not mutate `ResourceRef`, `FieldRef`, `FieldView`,
`FieldSpec`, `FieldValue`, or context metadata.

Capability/support matching must be narrow and explicit. Unsupported operation
is distinct from no matching codec. Unsupported `FieldView.field_index` is a
slice/materialization failure, not permission to load the whole resource. An
optional dependency failure must occur at the codec operation boundary and
must not make core imports heavy.

The synthetic codec is a validation fixture. It can define primitive payload
and metadata conventions in tests, but package code must not depend on or
export it. Its metadata behavior is limited to proving that
`MetadataSavePolicy.REFERENCE_ONLY` does not persist field metadata and
`MetadataSavePolicy.INCLUDE_FIELD_METADATA` includes only explicit field
metadata supported by the fixture.

No new scientific semantics are introduced for sampling rates, seconds-based
slices, spatial slices, member binding, cross-field alignment, quality masks,
normalization, or aggregation. `TemporalIndexSlice` values remain field-native
integer offsets. Ordered resources are passed through in order; the codec may
interpret them internally, but rphys must not infer member, selector, or
alignment semantics.

## Scientific Contract Notes

- Sampling and temporal alignment: `TemporalIndexSlice` remains half-open,
  integer, and field-native. Equal numeric slices across fields do not imply
  alignment, resampling, padding, seconds conversion, or shared sampling rate.
- Field roles, locators, schemas, and provenance: codecs receive `FieldView`
  and `FieldRef` descriptors, not role-qualified `FieldLocator`s or
  datasource records. Field schema, field metadata, field index, target, and
  ordered resources must remain inspectable in contexts/results.
- Masking, filtering, normalization, and aggregation order: no masking,
  filtering, normalization, aggregation, signal transforms, or quality-policy
  behavior is in scope. Synthetic payload slicing must not imply a scientific
  preprocessing contract.
- Subject identity, splits, leakage, and grouping: no subject, split, group,
  record, or dataset membership semantics are interpreted by codecs or
  registry behavior. Datasource provenance remains outside codec contexts.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: no signal statistics or sampling-rate validation is
  added. Unsupported index shapes, invalid context/result types, unsupported
  operations, no matching codec, ambiguity, and dependency failures must fail
  loudly with typed context. Missing requested locators and partial sample
  output are Phase 4 concerns.

## Design Impact

- Maintainability: keeps registry behavior in the existing `rphys.io.codecs`
  contract module and validates behavior through public operation methods,
  reducing pressure for broad base classes or placeholder APIs.
- Extensibility: downstream projects can pass importable codec objects to an
  explicit registry. Later symbolic config or plugin layers can wrap the
  registry without changing this public behavior.
- Lightweight import policy: package code must stay stdlib-only plus existing
  dependency-light rphys descriptors and runtime field records. Optional
  dependency failures stay inside concrete codec operations or test fixtures.
- Source-tree boundaries: `rphys.io.codecs` may depend on `rphys.data.fields`,
  `rphys.io.fields`, `rphys.io.resources`, and broad errors. It must not
  import `rphys.datasources`, `rphys.data.sample_fields`,
  `rphys.data.sample_builders`, tests/support, or heavy optional stacks.

## Future Compatibility

- Later real codecs can reuse `CodecRegistry`, contexts, results, and
  operation wrappers without changing Stage 3 descriptors.
- Later datasource/index layers can provide explicit registry instances or
  wrap them with config/symbolic lookup, but Phase 2 does not define symbolic
  keys.
- Later `SampleField` can call the same registry load wrapper while retaining
  lazy state and failure context.
- Later `SampleBuilder` can join `IndexItem.record`, item metadata, and
  locators around datasource-neutral codec contexts/results.
- Later export/save workflows can compose `SaveContext.target` and
  `CodecSaveResult` without replacing the single logical field save contract.
- Later compound resource member schemas can be added only with real codec
  evidence; Phase 2 preserves ordered resources without adding member meaning.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Process-global mutable default registry | Violates deterministic explicit-instance design and would couple tests, imports, and downstream workflows through hidden state. |
| Plugin/entry-point discovery in core imports | Would create hidden dependency/import behavior before a symbolic config contract exists. |
| Public synthetic or toy codec | Would imply a supported production format; DD-11 keeps the synthetic codec private to tests/support. |
| Mandatory codec base class | Conflicts with the accepted structural/duck-typed extension model. |
| Capability-only matching with hidden first-match fallback | Risks silent priority semantics and ambiguous behavior; overlapping matches must be tested and fail loudly unless one match is explicit. |
| Hidden full-resource load for unsupported slices | Violates the fail-loud slicing contract and can change scientific interpretation. |
| Datasource-aware codec contexts | Reverses the intended module dependency direction and belongs to Phase 4 builder/sample provenance joining. |
| Metadata handler or manifest writer API | Belongs to later export/save planning; Phase 2 only proves narrow save metadata policies. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Registry matching is proven with synthetic codecs only. | Real codec catalog and optional dependencies are deliberately out of scope; synthetic coverage is the approved dependency-light proof path. | First real codec family needs richer support predicates, priority metadata, or resource member semantics. |
| Metadata save behavior is narrow and fixture-backed. | Stage 4 only needs `REFERENCE_ONLY` and `INCLUDE_FIELD_METADATA`; manifest/export policy is deferred. | Milestone 8 export work needs layout, idempotency, or manifest persistence semantics. |
| Concrete error taxonomy may remain small. | DD-8 requires only exercised public errors to avoid placeholder names. | Downstream consumers need catchable distinctions not covered by broad codec/dependency/slice bases and tests exercise them. |
| `tests/support` may be introduced for a single helper. | Suite guidance already reserves it for trusted test-only helpers; keeping the codec there avoids public fake APIs. | Multiple independent fixtures suggest a clearer support package layout is needed. |

## Reviewability

- Expected PR size and shape: one IO behavior diff in `src/rphys/io/codecs.py`,
  a small exercised error-surface diff only if concrete errors are needed,
  private synthetic test helper(s), focused IO unit tests, codec contract
  tests, and package import updates only if exports change.
- Files and areas to inspect: `src/rphys/io/codecs.py`,
  `src/rphys/errors.py`, `tests/unit/rphys/io/test_codecs.py` or
  `tests/unit/rphys/io/test_codec_registry.py`, `tests/contracts/test_codec_contract.py`,
  `tests/support/**`, and package import-boundary tests if touched.
- Scope-control checks: no changes to `src/rphys/data/sample_fields.py`,
  `src/rphys/data/sample_builders.py`, runtime `Sample`/`Batch` behavior,
  datasource modules, Stage 3 descriptor load/save methods, root exports,
  dependency metadata, or workflow assets.
- Reviewer focus: explicit registry determinism, no global state, structural
  codec acceptance, typed failure context, no hidden fallback, no datasource
  imports, private synthetic codec boundary, and ordered resource/metadata
  preservation.

## Implementation Steps

1. Extend `rphys.io.codecs` with explicit registry behavior and only the
   public names needed for Phase 2. Keep storage instance-local, deterministic,
   and lightweight; update `__all__` only for code-backed names.
2. Implement operation-specific resolution and wrappers for probe, load, and
   save. Validate structural codec shape, capability/support matching, result
   types, and failure contexts through public behavior.
3. Add only exercised diagnostics in `src/rphys/errors.py` when broad bases are
   insufficient. Cover exact inheritance, `__all__` ordering, and context in
   tests.
4. Add a private dependency-light synthetic codec under `tests/support` or as
   local test fixtures, with primitive resources/payloads and call counters
   proving probe does not load and unsupported indexes do not full-load.
5. Add focused unit coverage for no match, one match, ambiguous match,
   deterministic ordering, invalid shape, unsupported operation/index,
   dependency-unavailable, metadata policies, save result provenance, ordered
   resources, and descriptor/context non-mutation.
6. Add codec contract coverage for executable probe/load/save examples and run
   package/import tests if any public export or import-boundary expectation
   changes.

## Test Plan

### Package Suite

- Status: conditional for full suite; focused package tests required if exports
  or import boundaries change.
- Expected paths: `tests/package/test_import.py`;
  `tests/package/test_import_boundaries.py`.
- Required assertions or deferral reason: root `rphys` remains empty;
  `rphys.io` re-exports only intentionally approved names; `rphys.io.codecs`
  exposes code-backed Phase 2 names; core imports do not load heavy optional
  modules, datasource modules, sample-field/builders, or `tests.support`.
  If implementation leaves package exports unchanged, run targeted package
  import-boundary tests plus `make test-package` before PR only if risk or
  export drift appears.

### Unit Suite

- Status: required.
- Expected paths: `tests/unit/rphys/io/test_codecs.py` and/or
  `tests/unit/rphys/io/test_codec_registry.py`; `tests/unit/rphys/test_errors.py`
  if concrete errors are added; private helpers under `tests/support/**` are
  exercised through unit tests.
- Required assertions or deferral reason: registry registration/resolution;
  structural codec acceptance without inheritance; invalid shape diagnostics;
  no match, one match, ambiguous match, unsupported operation, unsupported
  index, dependency-unavailable, deterministic ordering, operation result type
  validation, context/result metadata immutability, descriptor non-mutation,
  probe call counts without load, indexed load behavior, metadata policy
  behavior, save target/resources metadata, ordered multi-resource propagation,
  and no public fake codec import.

### Contract Suite

- Status: required.
- Expected paths: `tests/contracts/test_codec_contract.py` or equivalent
  focused codec contract file.
- Required assertions or deferral reason: executable EX-2 through EX-5
  behavior with private/local synthetic codecs: probe without load, save
  through `SaveContext.target`, missing/ambiguous/unsupported/dependency
  failure matrix, and compound ordered resource preservation without member or
  alignment semantics. Existing lazy IO descriptor contracts must remain green.

### Integration Suite

- Status: deferred.
- Expected paths: none for this phase.
- Required assertions or deferral reason: Phase 2 is IO behavior only and must
  not cross into runtime `SampleField` or `SampleBuilder` integration. Run
  `make test-integration` only if implementation unexpectedly touches shared
  integration surfaces, then stop for scope review if a vertical sample build
  is needed.

### E2E Suite

- Status: deferred.
- Expected paths: none for this phase.
- Required assertions or deferral reason: no end-to-end workflow, datasource
  scan, export, or training path is in scope.

### Acceptance Suite

- Status: deferred.
- Markers affected: none expected.
- Required assertions or deferral reason: no real datasets, hardware, network,
  GPU, optional dependency stacks, or long-running checks are in scope.

## Risks

- Registry matching may become too broad and produce ambiguity in legitimate
  cases, or too narrow and reject valid structural codecs.
- An operation wrapper could silently pick first registered codec and create
  hidden priority semantics unless ambiguity is tested.
- Unsupported `FieldView.field_index` handling could accidentally load the
  whole resource instead of failing loudly.
- Adding concrete errors without direct test coverage would create placeholder
  public API.
- A synthetic codec in package code or docs would create false production
  codec semantics.
- Optional dependency simulations could leak dependency imports into core
  modules unless import-boundary tests cover them.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/io/test_codecs.py
uv run pytest tests/unit/rphys/io/test_codec_registry.py
uv run pytest tests/contracts/test_codec_contract.py
uv run pytest tests/contracts/test_lazy_io_contract.py
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

If dependency metadata changes unexpectedly, also run:

```sh
uv lock --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: registry public surface and storage first;
  resolution/wrappers second; exercised errors third; private synthetic codec
  fourth; unit/contract/package validation last.
- Tests to run with each slice: registry unit tests after public surface;
  failure matrix tests after resolution; synthetic operation tests after
  fixture implementation; contract tests after probe/load/save examples;
  package tests after any `__all__` or import-boundary change.
- Decisions the executor must not revisit: explicit instance registry,
  structural codec interface, datasource-neutral contexts, `SaveContext.target`
  as `FieldRef`, narrow metadata policy, private synthetic codec, no global
  discovery, no hidden full-load fallback, no datasource/export/runtime sample
  behavior.
- Conditions that require stopping for the manager: registry matching needs
  symbolic names, plugin discovery, global mutable state, unapproved priority
  heuristics, public fake codec support, datasource-aware contexts, real
  optional dependencies, export/manifest policy, member/alignment semantics,
  `SampleField`, `SampleBuilder`, or a public API not traced to the accepted
  FR/DD/EX records.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: implemented and locally validated
- Implementation summary:
  - Added explicit instance-local `CodecRegistry` behavior in
    `rphys.io.codecs`, including deterministic ordered registration,
    operation-specific resolution for probe/load/save, optional structural
    `supports_*` predicates, save metadata-policy matching, typed result
    validation, and no process-global registry or discovery behavior.
  - Added exercised Stage 4 codec diagnostics for invalid codec shape,
    resolution ambiguity/no-match, unsupported operation, unsupported indexed
    materialization, dependency-unavailable operation boundaries, and invalid
    operation results.
  - Added private `tests.support.synthetic_codecs.SyntheticCodec` for
    dependency-light probe/load/save validation. The fixture records call
    counts, probes without loading, loads only supported unit-step temporal
    slices, rejects unsupported indexes without full-load fallback, preserves
    ordered resources on save, and exercises both metadata save policies.
  - Added executable unit and contract coverage for EX-2, EX-3, EX-4, and
    EX-5 while keeping root `rphys` and package-level `rphys.io` exports
    unchanged.
- Implementation validation:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/io/test_codec_registry.py tests/unit/rphys/io/test_codecs.py`: passed, 25 tests.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_codec_contract.py tests/contracts/test_lazy_io_contract.py`: passed, 9 tests.
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py tests/unit/rphys/test_errors.py`: passed, 51 tests.
  - `make test-package`: passed, 19 tests.
  - `make test-unit`: passed, 284 tests before final synthetic-private assertion and 285 tests under `make validate-pr`.
  - `make test-contract`: passed, 30 tests.
  - `make validate-pr`: passed; lock check passed, harness summary wrote
    `build/test-summary.md`, package 19, unit 285, contract 30, integration
    1, e2e/acceptance not present, build succeeded, and `git diff --check`
    was clean.
- Refinement summary: not needed for planning
- Pre-submit blocker gate: passed after local validation and manager review
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known

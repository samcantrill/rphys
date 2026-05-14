# Phase Prep 2 Execution Plan: FieldSpec And FieldIndex Contract Tightening

## Metadata

- Status: ready for implementation
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction preparation
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: FieldSpec And FieldIndex Contract Tightening
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase Prep 2: FieldSpec And FieldIndex Contract Tightening`
- Branch: `agent/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Phase execution plan path: `docs/roadmap/stage-4/phases/field-spec-index-contracts.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/phases/field-spec-index-contracts-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; maintainer approval is
  supplied by the phase assignment request
- Draft pass: completed in this artifact
- Refine pass: not needed unless implementation exposes documented public
  workflow pressure from `FieldSpec` immutability or a real `FieldIndex`
  extension-protocol need
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Remove shallow-mutation ambiguity from datasource schema field declarations and
align `FieldIndex` documentation with the current subclass-based implementation
before Stage 4 codec contracts and sample-builder code depend on those
descriptor objects.

## Full-Plan Context

Preparation Phase 1 established the public runtime `FieldContainer` surface.
This preparation phase tightens the adjacent Stage 2/3 descriptor contracts
that primary Stage 4 phases will consume: `FieldSpec` as a stable datasource
schema declaration value, and `FieldIndex` as an explicit base interface for
implemented index classes. Primary Phase 1 owns codec public contracts, Primary
Phase 2 owns registry and synthetic codec operations, Primary Phase 3 owns lazy
`SampleField`, and Primary Phase 4 owns `SampleBuilder`; all of that behavior
remains out of scope here.

## Source Phase Summary

- Goal: freeze `FieldSpec` and clarify `FieldIndex` as a subclass-based base
  interface before codec and builder APIs depend on these declarations.
- Required scope: `src/rphys/data/fields.py`, `src/rphys/io/indexes.py`,
  focused field/schema/index unit tests, lazy descriptor contract tests,
  package tests, touched module docstrings, and this phase documentation
  artifact.
- Required checkpoints: `FieldSpec` is frozen and slotted; construction still
  coerces Stage 1 vocabulary values; `FieldSpec.__hash__` is explicitly `None`;
  `DataSourceSchema` can keep storing `FieldSpec` declarations directly because
  they cannot be mutated through the schema mapping; `FieldIndex` wording says
  base class or base interface, not protocol.
- Acceptance criteria: mutation of `FieldSpec` fails; value equality and
  copy/deepcopy behavior remain value-preserving; hashing still raises
  `TypeError`; datasource declarations cannot be mutated through
  `schema.fields`; `FieldIndex` behavior remains subclass-based with no
  registry or `FieldIndex.from_dict`.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/data/fields.py` defines `FieldSpec` as `@dataclass(slots=True)`
  with direct attribute assignment in `__post_init__`. It already avoids rich
  payload facts such as `shape`, `dtype`, and `sample_rate`, and equality is
  value-based over `key`, `data_type`, and `schema`.
- Existing datasource schema behavior:
  `src/rphys/datasources/schemas.py` defines frozen `DataSourceSchema` and
  stores `fields` in a `MappingProxyType`, but `_coerce_fields` currently
  stores the caller's `FieldSpec` objects directly. The mapping is immutable;
  the stored declaration object is not. This phase makes that direct storage
  safe by freezing `FieldSpec`, without adding public `FieldSpec.to_dict()`.
- Existing IO index behavior:
  `src/rphys/io/indexes.py` implements `FieldIndex` as a simple base class
  whose direct construction raises `TypeError`. `TemporalIndexSlice` is the
  only concrete Stage 3 index, unknown type tags fail loudly through
  `UnsupportedFieldIndexError`, and tests already assert no registry,
  `register`, or `FieldIndex.from_dict` surface. The module docstring wording
  still calls `FieldIndex` a "Base protocol", which is the terminology this
  phase must correct.
- Existing tests or harness behavior:
  `tests/unit/rphys/data/test_fields.py` covers vocabulary coercion,
  value equality, copy/deepcopy, invalid vocabulary, and absence of rich schema
  fields. `tests/unit/rphys/datasources/test_datasource_schemas.py` covers
  schema declaration consistency, primitive round trips, immutable metadata,
  unhashable schema objects, and no scanning or validation hooks.
  `tests/unit/rphys/io/test_indexes.py` covers `TemporalIndexSlice` semantics,
  immutability, unknown tag failures, and the no-registry base boundary.
  `tests/unit/rphys/io/test_field_refs.py` and contract tests exercise
  `FieldView` reconstruction through the private Stage 3 index dispatcher.
- Import-boundary or dependency constraints:
  implementation must remain stdlib-only plus existing Stage 1/2 vocabulary
  and Stage 3 descriptor imports. It must not import codec, datasource
  discovery, array/video, plotting, deep-learning, dataset SDK, builder, or
  runtime sample-field modules.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is clean
  on `develop` tracking `origin/develop`
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-prep2-field-spec-index-contracts` and clean
  before this plan edit
- Current `develop` base: `3b58ff0 docs: record stage 4 prep 1 cleanup`
- Branch setup note: the branch already contains
  `c947571 plan: add prep 2 phase assignment`; preserve it and add only the
  execution-plan commit for this pass
- Earlier phase dependency status: Prep 1 merged through PR #21 and recorded
  in the implementation plan
- Push/PR infrastructure status: assignment records GitHub auth, fetch, push,
  PR creation, and merge as exercised in Prep 1; this planning pass does not
  push or open a PR
- Stop condition if isolation cannot be maintained: stop before code edits or
  PR work and return to the manager if the phase branch/worktree cannot remain
  dedicated to Prep 2

## In-Scope Work

- Change `FieldSpec` to `@dataclass(frozen=True, slots=True)`.
- Update `FieldSpec.__post_init__` to use `object.__setattr__` for `DataKey`,
  `DataType`, and optional `SchemaName` coercion.
- Set `FieldSpec.__hash__ = None` after the class definition so hashability
  remains explicitly outside the public contract.
- Preserve `FieldSpec` constructor shape, value equality, copy/deepcopy value
  behavior, vocabulary coercion, and absence of `shape`, `dtype`,
  `sample_rate`, or other rich schema fields.
- Add or update focused field tests proving attempted mutation fails,
  copy/deepcopy preserve value, and `hash(FieldSpec(...))` raises `TypeError`.
- Add or update datasource schema tests proving a stored declaration cannot be
  mutated through `DataSourceSchema.fields` and that the schema still stores
  declarations directly rather than adding schema snapshots or a public
  `FieldSpec` serialization API.
- Update `FieldIndex` docstrings and any related test/docs wording to call it a
  base class or base interface, not a protocol.
- Preserve current `FieldIndex` behavior: direct construction fails,
  `TemporalIndexSlice` remains the only supported Stage 3 index,
  unknown serialized tags fail loudly, and no registry or `FieldIndex.from_dict`
  is added.

## Out-of-Scope Work

- Public `FieldSpec.to_dict()`, shared `FieldSpec.from_dict()`, schema
  manifests, schema snapshots, schema validation reports, observed/expected
  schema evidence, schema versions, or descriptor fingerprints.
- Field-index registries, symbolic index names, structural `Protocol`
  dispatch, ABC registration, `FieldIndex.from_dict`, or public third-party
  index serialization extension.
- New index types, including seconds-based slices, spatial slices, alignment
  indexes, member bindings, or nested/compound index semantics.
- Codec contracts, codec registries, synthetic codecs, probe/load/save
  behavior, optional dependency handling, or hidden full-load fallback policy.
- `SampleField`, lazy state, `SampleBuilder`, requested-locator selection,
  datasource scanning, datasource views/splits/manifests, exports, operations,
  model formatting, caches, or training loaders.
- Root `rphys` convenience exports or exports from unrelated packages.

## Assumptions

- Freezing `FieldSpec` is an acceptable compatibility tightening before public
  downstream use expands through Stage 4.
- `DataSourceSchema` should continue storing `FieldSpec` declarations directly;
  freezing the declaration object is sufficient and avoids inventing schema
  snapshots.
- Dataclass frozen instances may become hashable by default, so this phase must
  explicitly assign `FieldSpec.__hash__ = None` and test it.
- `FieldIndex` should stay a nominal subclass base because the Stage 3
  implementation already rejected ABC registration exposure and structural
  registry behavior.
- `TemporalIndexSlice` wording and behavior remain field-native, integer, and
  half-open; this phase only corrects base-interface terminology around it.

## Scope Contract

`FieldSpec(key, data_type, schema=None)` remains the minimal runtime field
descriptor over exactly three fields: `DataKey`, `DataType`, and optional
`SchemaName`. Construction must still coerce compatible strings into those
vocabulary types and reject invalid values through the existing Stage 1 errors.
After construction, assignment to `key`, `data_type`, or `schema` must fail with
normal frozen dataclass behavior. Equality remains value-based over the three
declared fields. Copy and deep copy remain value-preserving. Hashability is not
public and must raise `TypeError`.

`DataSourceSchema(fields, metadata=None)` continues to require a non-empty
`DataKey -> FieldSpec` mapping with key/spec consistency. It may continue to
store the same `FieldSpec` declarations directly because those declarations are
now immutable. The executor must not add public `FieldSpec` serialization or
schema snapshot behavior; private `_field_spec_to_dict` and
`_field_spec_from_dict` remain datasource-schema internals.

`FieldIndex` remains a nominal base class/base interface for implemented
field-native index descriptors. Direct `FieldIndex()` construction fails.
`TemporalIndexSlice` remains the only supported Stage 3 index type.
Serialization reconstruction remains through the existing supported-tag path
used by `FieldView.from_dict`; unknown tags fail loudly. No registry,
registration hook, structural protocol, or public base factory is in scope.

## Scientific Contract Notes

- Sampling and temporal alignment: `TemporalIndexSlice` remains a field-native
  integer `[start, stop)` descriptor; equal numeric slices across fields still
  do not imply temporal alignment, resampling, padding, or seconds conversion.
- Field roles, locators, schemas, and provenance: `FieldSpec` continues to
  represent intrinsic field identity, broad data category, and optional schema
  identity only. Runtime roles stay in `FieldLocator`; datasource provenance
  stays in datasource descriptors and metadata.
- Masking, filtering, normalization, and aggregation order: no mask, filter,
  normalization, aggregation, transform, or collation behavior changes.
- Subject identity, splits, leakage, and grouping: no subject, split, group,
  record, or leakage semantics are added; existing datasource metadata remains
  descriptive.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: no payload-level behavior is introduced. Invalid
  vocabulary values and invalid/unsupported field-index descriptors retain
  current typed failure behavior.

## Design Impact

- Maintainability: freezing `FieldSpec` lets datasource schemas reuse the same
  declaration object without hidden mutation hazards or duplicate snapshot
  logic.
- Extensibility: keeping `FieldIndex` as a narrow nominal base leaves future
  index families to explicit roadmap/design approval instead of accidental
  structural extension.
- Lightweight import policy: changes stay in existing dependency-light data,
  datasource, and IO descriptor modules.
- Source-tree boundaries: `rphys.data.fields` owns `FieldSpec`;
  `rphys.datasources.schemas` owns declaration-only datasource schemas;
  `rphys.io.indexes` owns the Stage 3 index base and `TemporalIndexSlice`.

## Future Compatibility

Primary Stage 4 phases may rely on stable `FieldSpec` declarations when codecs
probe fields or builders preserve schema/provenance, but they must not require
this phase to add public schema manifests or serialization. Later roadmap stages
may design richer schema evidence, manifests, fingerprints, or additional index
types as wrappers or explicit new contracts without changing the immutability
and no-registry boundaries established here.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Copy or deep-copy `FieldSpec` values into `DataSourceSchema` | Freezing the declaration object solves the mutation hazard without adding hidden snapshot semantics or extra allocation policy. |
| Add public `FieldSpec.to_dict()` while touching schema declarations | Stage 2 explicitly has no public `FieldSpec` serialization contract; datasource schema serialization remains private until a manifest/schema stage approves one. |
| Make `FieldSpec` hashable after freezing | Hashability is not public and would imply stable cache-key behavior before manifests/fingerprints are designed. |
| Convert `FieldIndex` into a `typing.Protocol` or ABC | Stage 3 deliberately settled on a simple subclass base after ABC registration exposure; structural extension is not part of the approved contract. |
| Add `FieldIndex.from_dict` or a registry for future index tags | Future index serialization requires explicit scientific semantics and roadmap approval; Stage 3 supports only `TemporalIndexSlice`. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None expected | This phase tightens existing contracts and terminology without adding new extension machinery. | Revisit only if implementation exposes a documented public workflow that depends on post-construction `FieldSpec` mutation. |

## Reviewability

- Expected PR size and shape: small descriptor-contract diff across one data
  module, one IO module, focused unit/contract/package tests, and docstrings.
- Files and areas to inspect:
  `src/rphys/data/fields.py`,
  `src/rphys/datasources/schemas.py` only if docstrings/tests need declaration
  wording,
  `src/rphys/io/indexes.py`,
  `tests/unit/rphys/data/test_fields.py`,
  `tests/unit/rphys/datasources/test_datasource_schemas.py`,
  `tests/unit/rphys/io/test_indexes.py`,
  `tests/unit/rphys/io/test_field_refs.py` if index wording or dispatcher
  expectations need coverage,
  `tests/contracts/test_lazy_io_contract.py`,
  `tests/contracts/test_lazy_datasource_contract.py`,
  `tests/contracts/test_lazy_reference_contract.py`,
  `tests/package/test_import.py`, and
  `tests/package/test_import_boundaries.py`.
- Scope-control checks: no new files under `src/rphys/io/codecs.py`,
  `src/rphys/data/sample_fields.py`, `src/rphys/data/sample_builders.py`, or
  datasource adapter/view/index modules; no new public exports; no new
  dependencies; no codec, builder, manifest, registry, or runtime lazy-field
  behavior.

## Implementation Steps

1. Tighten `FieldSpec` in `src/rphys/data/fields.py`: make the dataclass frozen
   and slotted, update `__post_init__` to use `object.__setattr__`, keep the
   constructor and docstring semantics narrow, and assign
   `FieldSpec.__hash__ = None` after the class.
2. Add focused field tests in `tests/unit/rphys/data/test_fields.py` for frozen
   mutation failure, explicit unhashability, preserved value equality,
   copy/deepcopy behavior, vocabulary coercion, and continued absence of rich
   schema/payload fields.
3. Add datasource schema coverage in
   `tests/unit/rphys/datasources/test_datasource_schemas.py` proving
   `schema.fields[key]` cannot be mutated through the stored declaration and
   that `DataSourceSchema` still does not add validation, manifest, snapshot,
   or public `FieldSpec` serialization behavior.
4. Update `src/rphys/io/indexes.py` docstrings and any related test wording so
   `FieldIndex` is described as a base class/base interface, while preserving
   direct-construction failure, private supported-tag reconstruction, and
   `TemporalIndexSlice` semantics.
5. Run focused unit checks first, then package and contract suites to verify no
   public export, import-boundary, lazy descriptor, or datasource contract
   regression.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact `rphys.data`,
  `rphys.datasources`, and `rphys.io` exports remain unchanged except prior
  Prep 1 `FieldContainer`; root `rphys` remains empty; importing touched
  modules remains lightweight and does not import heavy optional stacks.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/data/test_fields.py`,
  `tests/unit/rphys/datasources/test_datasource_schemas.py`,
  `tests/unit/rphys/io/test_indexes.py`, and targeted
  `tests/unit/rphys/io/test_field_refs.py` if index reconstruction wording or
  behavior needs adjacent coverage
- Required assertions or deferral reason: `FieldSpec` mutation raises frozen
  dataclass failure; `hash(FieldSpec(...))` raises `TypeError`; value equality,
  copy/deepcopy, coercion, and invalid-vocabulary behavior remain unchanged;
  datasource schema declarations cannot be mutated through stored specs;
  `FieldIndex` remains non-instantiable, non-registry, and non-factory; unknown
  index tags and invalid temporal bounds retain existing typed failures.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_lazy_io_contract.py`,
  `tests/contracts/test_lazy_datasource_contract.py`, and
  `tests/contracts/test_lazy_reference_contract.py`
- Required assertions or deferral reason: lazy IO descriptors still round-trip
  through primitive JSON without payloads, manifests, fingerprints, registries,
  or runtime hooks; datasource schema declarations remain stable and
  declaration-only; public package examples continue to use `FieldSpec`,
  `DataSourceSchema`, `FieldIndex`, `TemporalIndexSlice`, `FieldView`, and
  `IndexItem` through the approved Stage 3 surfaces.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: this prep phase changes descriptor
  immutability and wording only. No multi-component codec, builder, datasource
  scanning, runtime materialization, or operation behavior is introduced.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end user workflow or real
  lazy sample construction path is in scope.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real dataset, hardware, network,
  GPU, optional dependency, or long-running acceptance behavior is affected.

## Risks

- Dataclass freezing can accidentally make `FieldSpec` hashable unless
  `__hash__` is explicitly set to `None` and tested.
- Direct mutation of `FieldSpec` may exist in downstream or local scratch code,
  but that conflicts with the approved value-object role and should fail early
  before Stage 4 expands use.
- Overcorrecting `FieldIndex` wording into a structural `Protocol`, ABC, or
  registry would reopen a Stage 3 decision and create implementation-agent
  invention risk.
- Schema tests must distinguish mapping immutability from declaration-object
  immutability so the intended mutation hazard is actually covered.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/data/test_fields.py tests/unit/rphys/datasources/test_datasource_schemas.py tests/unit/rphys/io/test_indexes.py
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

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: `FieldSpec` immutability first, field tests
  second, datasource schema declaration-safety tests third, `FieldIndex`
  wording fourth, package/contract validation last.
- Tests to run with each slice: run `uv run pytest
  tests/unit/rphys/data/test_fields.py` after `FieldSpec` changes; run
  `uv run pytest tests/unit/rphys/datasources/test_datasource_schemas.py` after
  declaration-safety coverage; run `uv run pytest
  tests/unit/rphys/io/test_indexes.py` after `FieldIndex` wording; run
  `make test-package` and `make test-contract` after all public wording and
  descriptor changes.
- Decisions the executor must not revisit: `FieldSpec` gets frozen rather than
  copied into schema snapshots; hashability stays non-public; `FieldIndex`
  stays a nominal subclass base; no registry, structural protocol, new index
  type, public factory, codec, builder, manifest, or sample-field behavior is
  introduced.
- Conditions that require stopping for the manager: freezing `FieldSpec`
  breaks a documented public workflow that cannot be adjusted in this phase;
  implementation needs public `FieldSpec` serialization or schema snapshots;
  index behavior needs a real extension protocol, registry, or new index type;
  package or contract suites show a compatibility regression outside the
  approved descriptor-tightening scope.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in
  `docs/roadmap/stage-4/phases/field-spec-index-contracts.md`
- Final phase execution plan: ready for execution after this planning commit
- Implementation summary:
  - Changed `FieldSpec` to a frozen slotted dataclass while preserving constructor coercion through `object.__setattr__`.
  - Explicitly kept `FieldSpec` unhashable with `FieldSpec.__hash__ = None`.
  - Added focused tests for `FieldSpec` immutability, copy/deepcopy value behavior, unhashability, and unchanged minimal schema vocabulary.
  - Added datasource schema coverage proving stored `FieldSpec` declarations cannot be mutated through `DataSourceSchema.fields` while remaining direct stored declarations.
  - Updated `FieldIndex` wording from protocol to base class and preserved current no-registry/no-factory behavior.
- Implementation validation:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_fields.py tests/unit/rphys/datasources/test_datasource_schemas.py tests/unit/rphys/io/test_indexes.py`: passed, 29 tests.
  - `make test-unit`: passed, 259 tests.
  - `make test-contract`: passed, 25 tests.
  - `make test-package`: passed, 18 tests.
  - `git diff --check`: clean.
  - `make validate-pr`: passed. Suite summary: package 18 passed, unit 259
    passed, contract 25 passed, integration 1 passed, e2e/acceptance not
    present, build succeeded, and `git diff --check` was clean.
- Refinement summary: not needed; targeted and required validation passed.
- Pre-submit blocker gate: manager review found the diff phase-scoped,
  future codec/lazy/builder behavior absent, public imports unchanged, and no
  scientific behavior changes beyond descriptor immutability and terminology.
- PR preparation: pending executor
- Automated review: pending PR
- Merge result: pending PR
- Cleanup: pending merge
- Remaining blockers: none known

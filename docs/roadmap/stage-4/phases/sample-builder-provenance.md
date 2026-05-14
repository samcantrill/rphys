# Phase 4 Execution Plan: `SampleBuilder` Bridge And Provenance Contracts

## Metadata

- Status: implementation complete; PR preparation pending
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: `SampleBuilder` Bridge And Provenance Contracts
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase 4: SampleBuilder Bridge And Provenance Contracts`
- Branch: `agent/codecs-lazy-samples-p4-sample-builder-provenance`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p4-sample-builder-provenance`
- Phase execution plan path: `docs/roadmap/stage-4/phases/sample-builder-provenance.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/implementation-plan.md#phase-4-samplebuilder-bridge-and-provenance-contracts`
- Assignment: `docs/roadmap/stage-4/phases/sample-builder-provenance-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path; this artifact records the additional provenance,
  accessor, and scope constraints, with no separate refinement pass needed
  before implementation unless a stop condition is hit
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; Preparation Phases 1
  and 2 plus Primary Phases 1 through 3 are merged and recorded
- Draft pass: completed in this artifact
- Refine pass: not needed for planning; one refiner pass remains available if
  implementation exposes ambiguous provenance, accessor, public API, import
  boundary, or validation behavior not resolved here
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Implement the one-item `SampleBuilder` bridge from Stage 3 `IndexItem`
descriptors to Stage 2 runtime `Sample`s containing Phase 3 lazy
`SampleField` handles, while preserving requested locator semantics,
datasource provenance, ordered resources, explicit codec resolution, and
probe/eager behavior without adding datasource scanning, hidden loading, cache,
model-formatting, or export responsibilities.

## Full-Plan Context

Preparation Phase 1 added the public `FieldContainer` protocol and
`field_items()` surface. Preparation Phase 2 froze `FieldSpec` and clarified
`FieldIndex` as a base interface. Primary Phase 1 added datasource-neutral
codec contexts and results. Primary Phase 2 added explicit `CodecRegistry`
resolution and private synthetic codec coverage. Primary Phase 3 added lazy
`SampleField` handles that store `LoadContext`, load through retained
`CodecLoadResult`s, and preserve loaded `Sample` compatibility.

This phase is the bridge behavior phase. It owns `SampleBuildContext`,
`SampleBuilder`, all/subset/one requested-locator selection, probe without
load, eager loading through `SampleField`, and builder-side provenance. Phase 5
owns closeout docs, examples, public API hardening, and final broad validation.
Stage 5 and later still own datasource discovery, views, splits, manifests,
operations, export orchestration, training loaders, caches, and model
formatting.

## Source Phase Summary

- Goal: build lazy `Sample`s from one `IndexItem` with all/subset/one/probe/eager
  paths and locked provenance semantics.
- Required scope: `src/rphys/data/sample_builders.py`; conditional
  `src/rphys/data/__init__.py` only if import-boundary tests support package
  re-export; builder/provenance unit tests; lazy sample contract tests;
  optional integration-style vertical slice if fragmented unit/contract tests
  leave meaningful risk.
- Required checkpoints: requested locator normalization; missing requested
  locators fail before any partial sample output; all/subset/one builds create
  lazy handles without loading unless `eager=True`; `probe` does not load;
  eager loading uses the `SampleField` state machine; built samples satisfy
  `FieldContainer`; descriptor and `IndexItem` objects are not mutated.
- Acceptance criteria: EX-1, EX-2, and EX-5 are covered; FR-5, FR-6, and FR-8
  are satisfied; integration portions of FR-2, FR-3, and FR-4 are preserved;
  provenance remains inspectable without adding unapproved identity, alignment,
  member, datasource-aware codec-context, or export semantics.

## Current Source And Harness Findings

- `src/rphys/data/sample_builders.py` does not exist yet. Adding it is the main
  product-code surface for the executor.
- `src/rphys/data/__init__.py` currently re-exports only Stage 2 runtime names.
  `SampleField` remains canonical in `rphys.data.sample_fields`; `SampleBuilder`
  can likewise remain canonical in `rphys.data.sample_builders` unless package
  tests deliberately prove a lightweight `rphys.data` re-export.
- `Sample` stores `FieldValue` objects directly, and `SampleField` subclasses
  `FieldValue`. `Sample.field()`, `role()`, and `field_items()` return stored
  handles without loading; `get()`, `require()`, expected-type validation,
  `SampleContract`, `map_tensors_()`, and LIST collation are payload-demanding.
- `SampleField` accepts a datasource-neutral `LoadContext` plus a loader
  callable. `eager_load()` uses the same retained state machine as payload
  access, so the builder should call `SampleField.eager_load()` for eager paths
  rather than bypassing the handle.
- `rphys.io.codecs.LoadContext` carries only `field_view` and primitive
  metadata. It must not gain `RecordRef`, `IndexItem`, locator, split, member,
  alignment, fingerprint, or datasource fields in this phase.
- `CodecRegistry` instances are explicit, ordered, non-global resolver objects.
  `probe()` and `load()` already enforce unique matching codecs, unsupported
  index errors, dependency wrapping, and operation result typing.
- `IndexItem` is frozen and descriptor-only. It exposes a role-qualified
  `fields` mapping, mandatory `record`, and item `metadata`; it validates that
  each `FieldLocator.key` matches the `FieldView.field_ref.key` and that the
  field key is present in `RecordRef.fields`.
- `FieldRef.resources` preserves caller-provided order without member,
  priority, selector, canonical-resource, or alignment semantics. Tests must
  assert this order survives through build/probe/load paths.
- `tests/support/synthetic_codecs.py` is private test support with probe/load
  call counters and compound-resource metadata. Package code must not import
  it, but Phase 4 tests can use it.
- Package import-boundary tests already prevent `rphys.io.codecs` from loading
  datasources, `rphys.data.sample_fields`, `rphys.data.sample_builders`, or
  `tests.support`; they also prevent `rphys.data.sample_fields` from loading
  datasource builders or test support.
- Suite intent is split by `tests/README.md`. Unit tests mirror `src/rphys`;
  contract tests document public semantics; integration/e2e/acceptance should
  stay absent unless a license-safe public vertical slice materially reduces
  risk.
- Harness targets run through `tools.test_harness`. `make validate-pr` runs
  lock check, `make test-summary`, build, and `git diff --check`; the final
  PR-range whitespace check must also use
  `git diff --check origin/develop...HEAD`.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` was
  checked before this plan edit and was clean on `develop` tracking
  `origin/develop`.
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-p4-sample-builder-provenance` and was clean
  before this plan edit.
- Current `develop` base: `89a6d3f docs: record stage 4 phase 3 cleanup`.
- Branch setup note: the branch already contains
  `d84fda4 plan: add phase 4 assignment`; preserve it and add only the
  execution-plan commit for this pass.
- Earlier phase dependency status: Preparation Phases 1 and 2 and Primary
  Phases 1 through 3 are merged and recorded in the implementation plan.
- Push/PR infrastructure status: assignment records GitHub push and PR
  infrastructure as previously exercised; this planning pass does not push or
  open a PR.
- Stop condition if isolation cannot be maintained: stop before product code
  edits or PR work and return to the manager if the branch/worktree cannot
  remain dedicated to Phase 4.

## In-Scope Work

- Add `SampleBuildContext` as the builder configuration and provenance context
  with explicit `CodecRegistry` input, optional primitive builder metadata, and
  no hidden global registry.
- Add `SampleBuilder` in `rphys.data.sample_builders` with
  `build(index_item, requested=None, eager=False)`, `build_one(...)`, and
  `probe(...)` behavior.
- Normalize requested locators from `FieldLocator` or parseable strings while
  preserving role, intrinsic key, and optional metadata selector components.
- Prevalidate every requested locator against the `IndexItem.fields` mapping
  before constructing a `Sample`, `SampleField`, probe result, or partial
  output.
- Build all, subset, and one-field `Sample` instances from one `IndexItem`,
  storing `SampleField` handles directly under the requested role-qualified
  locators.
- Wire each lazy handle to `CodecRegistry.load(LoadContext(field_view, ...))`
  through the Phase 3 `SampleField` loader path.
- Implement probe paths for all/subset/one requested locators through
  `CodecRegistry.probe(LoadContext(...))`, returning inspectable probe evidence
  without invoking load or reading payloads.
- Preserve builder/sample provenance: requested locator, intrinsic field key,
  `IndexItem.record`, `IndexItem.metadata`, `FieldView.field_index`,
  `FieldRef.schema`, `FieldRef.metadata`, ordered `FieldRef.resources`, and
  codec result metadata where the existing objects make that evidence
  available.
- Add focused unit and contract tests for all/subset/one build, probe without
  load, eager load, missing-request prevalidation, ordered compound resources,
  provenance retention, descriptor/index-item non-mutation, and import
  boundaries.

## Out-of-Scope Work

- Datasource scans, datasource index iteration, split selection, view
  construction, manifest construction, item IDs, fingerprints, or persistent
  sample identity.
- Adding `RecordRef`, `IndexItem`, datasource, split, subject, group, member,
  alignment, or fingerprint fields to `LoadContext`, `SaveContext`, or codec
  registry matching.
- Cache policy, retry/reset beyond existing `SampleField` failed-state
  retention, async loading, cancellation, thread safety, device movement,
  tensor conversion, operation pipelines, or model tuple formatting.
- Export operations, save orchestration, derived datasources, metadata
  persistence policy beyond the existing `SaveContext` contract, or any real
  codec catalog.
- Public fake/synthetic codecs, optional video/array/deep-learning
  dependencies, network access, raw datasets, or test fixtures that are not
  tiny and license-safe.
- Redesigning `Sample`, `SampleField`, `CodecRegistry`, `IndexItem`,
  `FieldRef`, `FieldView`, field indexes, collation policy, or the existing
  error hierarchy unless a stop condition is escalated.

## Constraints

- Keep base imports lightweight. `rphys.data.sample_builders` may import
  datasource descriptor types and codec records needed for the bridge, but it
  must not import test support or optional heavy stacks.
- Keep the registry explicit. The builder receives a `CodecRegistry` through
  `SampleBuildContext` or construction and must not consult process-global
  discovery, entry points, symbolic registries, or hidden defaults.
- Keep codec contexts datasource-neutral. Builder-owned provenance may live on
  builder records, sample metadata, returned build/probe evidence, or retained
  handles, but not as new `LoadContext` fields.
- Treat `IndexItem`, `RecordRef`, `FieldRef`, `FieldView`, `ResourceRef`, and
  `FieldSpec` as immutable descriptor evidence. Tests must prove build/probe
  paths do not mutate or replace descriptor state.
- Do not collapse role-qualified locators into intrinsic keys. Two locators
  with the same `DataKey` but different roles remain distinct runtime fields.
- Missing requested locators are an atomic failure before partial output. This
  includes `build`, `build_one`, and `probe` variants.
- Probe must not construct payload-demanding access, call registry load, call
  `SampleField.payload`, or call `SampleField.eager_load()`.
- Eager build must materialize through each built `SampleField.eager_load()` so
  retained result/error state and later payload behavior remain identical to
  normal lazy access.
- Add new public errors only if existing typed errors cannot represent the
  failure with inspectable context; stop for manager review before broadening
  the error taxonomy.

## Assumptions

- The accepted Phase 1 through Phase 3 APIs are sufficient for builder
  behavior without redesign.
- `SampleBuildContext` can carry primitive builder metadata for traceability
  while `LoadContext.metadata` remains primitive and datasource-neutral.
- Existing `MissingFieldError`, `FieldTypeError`, `CodecResolutionError`,
  `UnsupportedCodecIndexError`, and `CodecOperationError` are likely enough
  for requested-locator, resolver, and load/probe failures.
- Canonical imports from `rphys.data.sample_builders` are acceptable if
  package-level `rphys.data` re-export would blur import boundaries.
- Unit and contract coverage should be enough; integration is conditional on a
  single vertical slice proving a cross-module behavior that is awkward to
  express clearly elsewhere.

## Scope Contract

`rphys.data.sample_builders` owns the conversion of exactly one `IndexItem`
into runtime `Sample` objects whose fields are lazy `SampleField` handles.
The builder is not a datasource, index, operation, cache, export, or training
abstraction. It only selects `FieldView`s already present on the supplied
`IndexItem`, creates datasource-neutral `LoadContext`s for those views, stores
lazy handles under the role-qualified locators, and returns or exposes enough
builder-side evidence to explain where each handle came from.

The public behavior contract is:

1. `build(index_item, requested=None, eager=False)` builds all fields when
   `requested` is `None`; otherwise it builds exactly the requested locators in
   request order after atomic missing-request prevalidation.
2. `build_one(...)` builds exactly one requested locator and shares the same
   validation, provenance, lazy/eager loading, and error behavior as `build`.
3. `probe(...)` resolves probe-capable codecs for the same all/subset/one
   locator set and returns probe evidence without constructing payloads,
   invoking load, or changing lazy field state.
4. Built samples satisfy `FieldContainer`; `sample.field(locator)`,
   `sample.role(role)`, and `sample.field_items()` return lazy handles without
   loading, while existing payload-demanding runtime APIs may load through
   `SampleField`.
5. Locator, field key, field index, field schema, field metadata, record
   provenance, item metadata, ordered resources, and codec metadata remain
   inspectable at documented builder/sample/handle/result boundaries.

The executor must not redesign codec resolution, runtime access semantics,
descriptor serialization, or scientific identity semantics to implement this
contract.

## Scientific Contract Notes

- Sampling and temporal alignment: pass each `FieldView.field_index` through
  unchanged in the `LoadContext`. Do not reinterpret integer slices as seconds,
  frames, synchronized windows, padding, resampling, or cross-field alignment.
- Field roles, locators, schemas, and provenance: preserve the distinction
  between role-qualified `FieldLocator` and intrinsic `DataKey`; retain
  `FieldRef.schema`, `FieldRef.metadata`, `IndexItem.record`, and
  `IndexItem.metadata` as provenance, not payload fields.
- Ordered resources: pass `FieldRef.resources` to codecs through the existing
  `FieldView` object in caller-provided order. Do not add member selectors,
  priorities, alignment labels, or canonical resource IDs.
- Masking, filtering, normalization, and aggregation order: no masking,
  filtering, normalization, aggregation, interpolation, padding, or statistics
  are performed in this phase.
- Subject identity, splits, leakage, and grouping: subject, group, split, and
  source values may exist as descriptor metadata only. The builder must not
  choose splits, group records, infer subject identity, or compute leakage
  boundaries.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: payload-level scientific validation remains codec or
  later-operation responsibility. Missing requested locators fail before
  partial sample construction; unsupported slices propagate the codec registry's
  typed fail-loud behavior without hidden full-load fallback.

## Design Impact

- Maintainability: the builder is a small bridge module with explicit context
  and result shapes, keeping datasource descriptors, codec operation records,
  and runtime containers separable.
- Extensibility: later datasource indexes, manifests, operations, export
  layouts, and real codecs can feed or consume the bridge without changing its
  one-item contract.
- Lightweight import policy: canonical focused-module imports avoid pulling
  builder dependencies into `rphys`, `rphys.io.codecs`, or loaded runtime
  containers.
- Source-tree boundaries: `rphys.data.sample_builders` may depend on
  `rphys.datasources.index_items`, `rphys.io.codecs`,
  `rphys.data.sample_fields`, and `rphys.data.containers`; `rphys.io.codecs`
  must not depend on `rphys.data.sample_builders`.

## Future Compatibility

- Later datasource view/index phases can provide iterable `IndexItem`s to this
  builder without changing builder ownership.
- Later export/save phases can consume built samples and retained provenance
  without making `SampleBuilder` responsible for save layouts.
- Later cache or training-loader work can wrap `SampleField` loading explicitly
  without adding hidden cache policy to this phase.
- Real codecs can add support predicates and result metadata while preserving
  the explicit `CodecRegistry` and datasource-neutral `LoadContext` contract.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Global default codec registry used by `SampleBuilder` | Violates explicit registry instances and makes codec resolution hidden and hard to test. |
| Add `RecordRef` or `IndexItem` to `LoadContext` | Breaks the approved datasource-neutral codec context boundary. |
| Build eager samples by replacing handles with loaded `FieldValue`s | Erases lazy state, retained results, and diagnostics that Phase 3 made inspectable. |
| Normalize requested fields by intrinsic `DataKey` only | Collapses runtime role semantics and can silently mix inputs, targets, metadata, or diagnostics. |
| Add item IDs, fingerprints, members, or alignment tags now | These semantics are unapproved and belong to later datasource/manifest/alignment planning. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Builder provenance will likely be a minimal in-memory record shape, not a persisted manifest | Stage 4 must prove the bridge without absorbing Stage 5 datasource manifests or Stage 8 export artifacts. | When datasource index manifests or export provenance become roadmap scope. |
| Package-level `rphys.data` re-export may remain absent | Focused submodule import preserves lightweight boundaries and matches Phase 3 precedent. | Closeout Phase 5 or downstream API review decides `SampleBuilder` is stable enough for package re-export. |
| Integration suite may remain minimal or absent | Unit and contract tests can directly exercise the public bridge with synthetic codecs. | If review finds cross-module provenance or lazy/eager behavior unclear from unit/contract coverage. |

## Reviewability

- Expected PR size and shape: one new builder module plus focused package,
  unit, and contract tests; optional one integration test only if justified.
- Files and areas to inspect: `src/rphys/data/sample_builders.py`,
  conditional `src/rphys/data/__init__.py`, `tests/unit/rphys/data/`,
  `tests/contracts/`, `tests/package/test_import.py`,
  `tests/package/test_import_boundaries.py`, and optional
  `tests/integration/`.
- Scope-control checks: no product-code edits outside the builder module and
  deliberate import-boundary updates unless a local compatibility issue is
  unavoidable; no changes to `rphys.io.codecs` except manager-approved blocker
  resolution.
- Provenance checks: tests should assert exact object identity or serialized
  equivalence for `IndexItem.record`, `IndexItem.metadata`, `FieldView`,
  `FieldRef.metadata`, `field_index`, resources order, and locator/key
  separation.
- Probe/eager checks: tests should assert probe call counts load zero payloads
  and eager build invokes `SampleField` loading exactly once per requested
  field through the retained state machine.

## Implementation Steps

1. Add the public builder records and minimal constructor validation in
   `src/rphys/data/sample_builders.py`: `SampleBuildContext`, `SampleBuilder`,
   explicit registry/context inputs, primitive builder metadata, and docstrings
   that state one-item scope and non-goals.
2. Implement requested-locator coercion and atomic prevalidation for
   all/subset/one paths, including duplicate/request-order behavior and typed,
   inspectable missing-locator failures.
3. Implement lazy `build` and `build_one` by creating `LoadContext`s from
   selected `FieldView`s, constructing `SampleField` handles with registry
   loaders, storing them directly in `Sample`, and retaining builder-side
   provenance without mutating descriptors.
4. Implement eager behavior by calling `SampleField.eager_load()` after sample
   construction and propagating retained typed failures without replacing
   handles.
5. Implement `probe` for all/subset/one requested locators using
   `CodecRegistry.probe()` and return inspectable evidence that includes the
   requested locator and builder-side provenance while never loading payloads.
6. Add focused tests and package/import-boundary updates, then adjust docstrings
   only where needed to make public behavior and non-goals clear.

## Test Plan

### Package Suite

- Status: required if the public module or package import surface changes;
  otherwise required as a focused import-boundary check for the new canonical
  submodule.
- Expected paths: `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`.
- Required assertions: `rphys.data.sample_builders` imports without heavy
  optional modules or test support; `rphys.io.codecs` still does not import
  datasources, sample fields, or builders; `rphys.data` re-export changes only
  if deliberate and tested.

### Unit Suite

- Status: required.
- Expected paths: `tests/unit/rphys/data/test_sample_builders.py`, plus focused
  edits to existing `test_sample_fields.py` only if builder integration exposes
  a real Phase 3 compatibility gap.
- Required assertions: context validation; request normalization; all/subset/one
  builds; missing-request prevalidation before partial output; lazy no-load
  construction; eager path through `SampleField.eager_load()`; registry loader
  contexts; ordered resources; provenance retention; descriptor/index-item
  non-mutation; typed resolver/load failures.

### Contract Suite

- Status: required.
- Expected paths: `tests/contracts/test_lazy_sample_builder_contract.py` or a
  similarly named Stage 4 bridge contract.
- Required assertions: executable EX-1 lazy sample build/load, EX-2 probe
  without load, and EX-5 compound ordered resources; built samples satisfy
  `FieldContainer`; locator/key and record/item provenance remain inspectable;
  unsupported slices fail loudly without hidden full-load fallback.

### Integration Suite

- Status: deferred by default; conditional.
- Expected paths: optional `tests/integration/test_lazy_sample_builder.py`.
- Required assertions or deferral reason: add one license-safe synthetic
  vertical slice only if unit/contract coverage cannot clearly show interaction
  between `IndexItem`, `CodecRegistry`, `SampleField`, and `Sample`; otherwise
  record that unit/contract tests cover the risk directly.

### E2E Suite

- Status: deferred.
- Expected paths: none expected.
- Required assertions or deferral reason: no real datasource, discovery,
  operation pipeline, export, or training workflow is in scope for Phase 4.

### Acceptance Suite

- Status: deferred.
- Markers affected: none expected.
- Required assertions or deferral reason: no raw datasets, hardware, GPU,
  network, optional dependencies, or long-running real-dataset checks are
  required for this dependency-light bridge.

## Risks

- The phase can grow if implementation tries to fix registry, lazy field, or
  datasource descriptor APIs instead of using their accepted contracts.
- Provenance can be weakened if request normalization drops roles, metadata
  selectors, field indexes, record provenance, item metadata, or resource order.
- Probe behavior can accidentally load if tests only inspect returned data and
  do not assert codec load counters and lazy field state.
- Eager behavior can erase diagnostics if it replaces `SampleField` handles
  with loaded `FieldValue`s.
- Import-boundary changes can make `rphys.data` or `rphys.io.codecs` pull in
  datasource, builder, or test-support modules unexpectedly.

## Stop Conditions

- Builder implementation requires datasource index iteration, scans, split
  semantics, datasource views, manifest generation, item identity, fingerprints,
  member/alignment semantics, export orchestration, model formatting, cache
  policy, device movement, or training-loader behavior.
- Requested locators cannot be prevalidated atomically before any sample,
  handle, probe result, or partial output is created.
- Probe paths need to load payloads, call `SampleField.payload`, call
  `SampleField.eager_load()`, or use registry load.
- Descriptor or `IndexItem` provenance must be mutated, copied into codec
  context fields, or simplified in a way that loses role/key/index/resource
  evidence.
- Implementing the contract requires public API or error taxonomy changes not
  traced to the approved FR/DD/EX records.
- Import boundaries force `rphys.io.codecs` to import builders or test support,
  or force heavy optional dependencies into base imports.

## Validation Commands

Targeted development commands:

```sh
make test-package
make test-unit
make test-contract
make test-integration  # only if an integration vertical slice is adopted
git diff --check
```

Focused pytest commands the executor may use while iterating:

```sh
uv run pytest tests/unit/rphys/data/test_sample_builders.py
uv run pytest tests/contracts/test_lazy_sample_builder_contract.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check origin/develop...HEAD
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: builder records first, request prevalidation
  second, lazy build third, eager/probe fourth, tests/import-boundary updates
  last.
- Tests to run with each slice: unit builder tests after records and request
  prevalidation; unit plus contract tests after lazy/eager/probe behavior;
  package tests after any import-surface change.
- Decisions the executor must not revisit: explicit registry instances,
  structural codecs, datasource-neutral codec contexts, `SampleField` stored as
  the field object, no hidden full-load fallback, no descriptor mutation, no
  global discovery, and no unapproved item/member/alignment/fingerprint
  semantics.
- Conditions that require stopping for the manager: any stop condition above,
  unexpected need to alter `LoadContext`, `CodecRegistry`, `SampleField`
  state semantics, or a new public error family.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed; one expanded-path refiner pass
  remains available if implementation exposes unresolved provenance or accessor
  ambiguity
- Phase implementation refinement: unused
- PR review: unused; expected reviewer focus is scientific provenance and scope
  boundaries
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: this artifact is ready for implementation unless
  manager review requests changes
- Implementation summary: added canonical `rphys.data.sample_builders` with
  `SampleBuildContext`, `SampleBuilder`, `SampleFieldProvenance`, and
  `SampleProbeResult`; implemented all/subset/one requested-locator selection,
  atomic missing-request prevalidation, lazy/eager `SampleField` construction,
  probe without load, copy-safe built lazy handles, and builder-side provenance
  that keeps `LoadContext` datasource-neutral.
- Implementation validation: focused builder/field/contract/package pytest
  passed 51 tests; `make test-package` passed 22; `make test-unit` passed 309;
  `make test-contract` passed 38; `make validate-pr` passed lock check,
  package 22, unit 309, contract 38, integration 1, build, and
  `git diff --check`.
- Refinement summary: pending
- Pre-submit blocker gate: passed locally; tests confirm no partial sample
  creation on missing requested locators, no probe load, no descriptor
  mutation, ordered resource retention, and no datasource provenance pushed into
  codec contexts.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none known

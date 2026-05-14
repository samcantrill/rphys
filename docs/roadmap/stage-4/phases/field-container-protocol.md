# Phase Prep 1 Execution Plan: Field Container Protocol

## Metadata

- Status: ready for implementation
- Roadmap stage: `v4`
- Feature focus: Codecs and lazy sample construction preparation
- Stage descriptor: Codecs And Lazy Sample Construction
- Phase descriptor: Field Container Protocol
- PR title: `Stage 4 Codecs And Lazy Sample Construction - Phase Prep 1: Field Container Protocol`
- Branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep1-field-container-protocol`
- Phase execution plan path: `docs/roadmap/stage-4/phases/field-container-protocol.md`
- Full plan: `docs/roadmap/stage-4/implementation-plan.md`
- Planning document: `docs/roadmap/stage-4/planning.md`
- Source phase: `docs/roadmap/stage-4/phases/field-container-protocol-assignment.md`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: passed in the implementation plan; maintainer approval is
  supplied by the phase assignment request
- Draft pass: completed in this artifact
- Refine pass: not needed unless implementation discovers a loaded-runtime
  compatibility blocker or lazy-field-specific protocol pressure
- Setup limitations: branch and worktree were supplied by the manager and were
  reused; no branch or worktree was recreated
- Blockers: none known

## Objective

Establish the public runtime `FieldContainer` protocol and public
`field_items()` iteration surface shared by `Sample`, `Batch`,
`SampleContract`, LIST collation, and later lazy-field runtime work without
changing loaded `Sample` or `Batch` accessor semantics.

## Full-Plan Context

This preparation phase tightens the Stage 2 runtime container boundary before
Stage 4 adds codec contracts, lazy `SampleField` handles, and `SampleBuilder`.
It supports FR-4 lazy-field runtime compatibility, FR-7 intentional public
imports, and FR-8 scope-control validation. Primary Phase 3 may extend
annotations for lazy fields, but it must preserve the public method names and
loaded-runtime behavior introduced here. Codec behavior, registry behavior,
builder provenance, payload loading, lazy state, datasource behavior, and
collation policy expansion remain future-phase work.

## Source Phase Summary

- Goal: add the public runtime `FieldContainer` protocol and public field
  iteration surface before lazy fields widen runtime semantics.
- Required scope: `src/rphys/data/containers.py`,
  `src/rphys/data/contracts.py`, `src/rphys/data/collation.py`,
  `src/rphys/data/__init__.py`, focused runtime unit tests, runtime contract
  tests, package import/export tests, and this phase documentation artifact.
- Required checkpoints: `Sample` and `Batch` expose `field_items()`;
  `SampleContract` validates through the public protocol shape; LIST collation
  uses `field_items()` instead of `_field_items`; `rphys.data` exports
  `FieldContainer` only after import-boundary tests remain lightweight.
- Acceptance criteria: loaded runtime examples still pass; collation no longer
  depends on a private hook; no lazy IO, codec, datasource, or accessor
  semantic change is introduced.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `src/rphys/data/containers.py` defines private `_FieldContainerBase`,
  public `Sample` and `Batch`, and a private `_field_items()` tuple snapshot
  used for iteration. `__all__` currently exports only `Batch` and `Sample`.
- Existing contract and collation behavior:
  `src/rphys/data/contracts.py` currently shape-checks only `has` and
  `require`, while `src/rphys/data/collation.py` reaches for the private
  `_field_items` hook. LIST collation otherwise preserves the current strict
  field-set, schema, policy, payload list, and sparse metadata behavior.
- Existing tests or harness behavior:
  `tests/unit/rphys/data/test_containers.py`,
  `tests/unit/rphys/data/test_contracts.py`, and
  `tests/unit/rphys/data/test_collation.py` cover loaded accessors, contract
  validation, copy/mutation semantics, role views, and LIST collation.
  `tests/contracts/test_runtime_core_contract.py` covers public runtime
  examples and `rphys.data.__all__` expectations. `tests/package/test_import.py`
  and `tests/package/test_import_boundaries.py` protect exact exports and
  lightweight imports.
- Import-boundary or dependency constraints:
  the protocol must stay stdlib-only and must not import IO, datasource,
  array/video, plotting, deep-learning, dataset SDK, codec, or builder modules.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is clean
  on `develop` tracking `origin/develop`
- Dedicated branch/worktree status: current worktree is on
  `agent/codecs-lazy-samples-prep1-field-container-protocol` and clean before
  this plan edit
- Current `develop` base: `e7d95fc docs: revised roadmap items`
- Branch setup note: the branch already contains
  `9500e36 plan: add prep 1 phase assignment`; preserve it and add only the
  execution-plan commit for this pass
- Earlier phase dependency status: no earlier Stage 4 phase exists
- Push/PR infrastructure status: assignment records GitHub auth, git setup,
  fetch, and open-PR checks as passed; this planning pass does not push or open
  a PR
- Stop condition if isolation cannot be maintained: stop before code edits or
  PR work and return to the manager if the phase branch/worktree cannot remain
  dedicated to Prep 1

## In-Scope Work

- Add a `@runtime_checkable` public `FieldContainer` protocol in
  `rphys.data.containers`.
- Include only the current runtime access and iteration surface in the
  protocol: `has`, `field`, `get`, `require`, `role`, and `field_items`.
- Add public `field_items()` to `_FieldContainerBase` so `Sample` and `Batch`
  expose a stable snapshot of `(FieldLocator, FieldValue)` pairs.
- Keep `_field_items()` as a private compatibility alias only if needed, but
  move internal runtime code to `field_items()`.
- Update `SampleContract` shape validation to use the public protocol surface
  rather than an ad hoc `has`/`require` check.
- Update LIST collation to consume `field_items()` and retain current
  field-set, schema, policy, payload, and metadata behavior.
- Export `FieldContainer` from `rphys.data.containers` and conditionally from
  `rphys.data` with matching package and contract tests.
- Add focused unit, contract, and package coverage for protocol satisfaction,
  public iteration, no private collation hook, existing runtime behavior, and
  lightweight imports.

## Out-of-Scope Work

- `SampleField`, lazy payload loading, lazy state, retry/reset/cache policy, or
  eager-load behavior.
- Codec contracts, codec registries, synthetic codecs, load/save/probe
  contexts, or IO errors.
- `SampleBuilder`, `SampleBuildContext`, builder provenance, requested-locator
  selection, datasource scanning, datasource schemas, or `IndexItem` changes.
- New collation policies, collation dispatch, stacking/padding/truncation,
  payload-level collation hooks, or changes to LIST collation semantics.
- Changes to loaded `Sample` or `Batch` accessor semantics for `field`, `get`,
  `require`, `set_field`, `delete_field`, `rename_field`, `role`, copying, or
  `map_tensors_`.
- Root `rphys` convenience exports or exports from unrelated packages.

## Assumptions

- The public protocol can be provisional and minimal because Stage 4 later
  phases may widen compatible field-object annotations additively without
  renaming methods.
- `field_items()` should return the same tuple snapshot shape currently
  returned by `_field_items()`, preserving insertion order and object identity.
- Runtime protocol checks may validate method presence and callable shape, but
  they do not need to validate signatures beyond behavior tested through
  `Sample`, `Batch`, and public-only collation test doubles.
- `FieldContainer` can be re-exported from `rphys.data` without import cost
  because it depends only on existing lightweight data vocabulary.

## Scope Contract

`FieldContainer` is a runtime field-access protocol, not a datasource, codec,
builder, manifest, operation, or workflow abstraction. It must cover only:

- `has(locator: FieldLocator | str) -> bool`
- `field(locator: FieldLocator | str, *, expected_type: PayloadType | None = None, schema: SchemaName | str | None = None) -> FieldValue`
- `get(locator: FieldLocator | str, default: object = None, *, expected_type: PayloadType | None = None, schema: SchemaName | str | None = None) -> object`
- `require(locator: FieldLocator | str, *, expected_type: PayloadType | None = None, schema: SchemaName | str | None = None) -> object`
- `role(role: FieldRole | str) -> Mapping[FieldLocator, FieldValue]`
- `field_items() -> tuple[tuple[FieldLocator, FieldValue], ...]`

The executor must preserve current loaded behavior: `field()` returns the
stored `FieldValue`; `get()` and `require()` return payloads; validation errors
remain typed; `role()` returns a read-only shallow snapshot; `field_items()`
does not expose `_FieldEntry`; mutation and copy APIs keep existing aliasing
semantics. `field_items()` must not load payloads, reinterpret schemas, change
metadata, sort fields, or mutate the container.

Invalid contract containers should continue to fail loudly with
`FieldTypeError` and context identifying the missing public method. Collation
must reject non-container inputs with `CollatePolicyError` and retain the
current sparse metadata, schema-match, explicit LIST-policy, homogeneous
field-set, empty-input, and empty-field failure behavior.

## Scientific Contract Notes

- Sampling and temporal alignment: no sampling-rate, timestamp, alignment,
  spatial slicing, or temporal slicing behavior is introduced.
- Field roles, locators, schemas, and provenance: locators and roles keep their
  current coercion paths; schemas and metadata remain stored on `FieldValue`;
  `field_items()` exposes locator/value pairs without introducing provenance or
  descriptor interpretation.
- Masking, filtering, normalization, and aggregation order: no mask, filter,
  normalization, aggregation, stacking, padding, or transform behavior changes.
- Subject identity, splits, leakage, and grouping: no subject, split, group,
  record, datasource, or leakage semantics are added.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: existing missing-field, wrong-type, wrong-schema,
  collation-policy, schema-mismatch, empty-input, and field-set mismatch
  failures stay unchanged; invalid rates and unsupported slices remain outside
  this phase.

## Design Impact

- Maintainability: centralizes the runtime field-container shape in one public
  protocol instead of duplicating private hook checks in contracts and
  collation.
- Extensibility: later lazy fields can satisfy the same surface by preserving
  method names and widening compatible field-object behavior additively.
- Lightweight import policy: implementation stays within `rphys.data` and uses
  only stdlib typing plus existing data vocabulary.
- Source-tree boundaries: data containers, contracts, and collation own runtime
  behavior; IO, datasources, builders, and errors outside current exercised
  behavior remain untouched.

## Future Compatibility

Primary Phase 3 may extend `FieldContainer` annotations or implementation
details for `SampleField` compatibility, but it must not redesign the public
method names introduced here. Primary Phase 4 may rely on built samples
satisfying `FieldContainer`, but request selection and provenance remain
builder-owned. Later operations can consume the protocol as a runtime access
surface without depending on `_FieldEntry` or any private collation hook.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Keep `_field_items()` private and document it implicitly through collation | Leaves later lazy/runtime code dependent on a private hook and conflicts with the approved public field-container cleanup. |
| Make `SampleContract` check only `has` and `require` | Under-specifies the public runtime surface this phase is intended to establish. |
| Add a broad abstract base class with inheritance requirements | Current `Sample` and `Batch` already share implementation, and later extension should remain structural rather than inheritance-bound. |
| Add lazy-field-specific methods or types now | Lazy state and payload-loading behavior belong to primary Phase 3 and are a stop condition for this preparation phase. |
| Expand collation while touching field iteration | Collation policy expansion is explicitly out of scope; this phase changes only the iteration hook used by existing LIST behavior. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| `_field_items()` may remain as a private alias temporarily | Avoids needless compatibility churn while internal code moves to the public surface. | Remove or de-emphasize only after later phases and tests no longer need private compatibility. |
| Protocol annotations are loaded-runtime oriented | Prep 1 must not design `SampleField` before primary Phase 3. | Primary Phase 3 needs additive lazy-field compatibility annotations without changing method names. |

## Reviewability

- Expected PR size and shape: small public API/runtime compatibility diff across
  data containers, contracts, collation, package exports, and focused tests.
- Files and areas to inspect:
  `src/rphys/data/containers.py`, `src/rphys/data/contracts.py`,
  `src/rphys/data/collation.py`, `src/rphys/data/__init__.py`,
  `tests/unit/rphys/data/test_containers.py`,
  `tests/unit/rphys/data/test_contracts.py`,
  `tests/unit/rphys/data/test_collation.py`,
  `tests/contracts/test_runtime_core_contract.py`,
  `tests/package/test_import.py`, and
  `tests/package/test_import_boundaries.py` if export/import checks need
  adjustment.
- Scope-control checks: no files under `src/rphys/io`,
  `src/rphys/datasources`, `src/rphys/data/sample_fields.py`, or
  `src/rphys/data/sample_builders.py`; no new dependencies; no root package
  export; no changed LIST collation scientific behavior.

## Implementation Steps

1. Add the public protocol and iteration surface in
   `src/rphys/data/containers.py`: define `FieldContainer`, add
   `field_items()` to `_FieldContainerBase`, keep `_field_items()` only as a
   private alias if needed, and update module exports.
2. Update `src/rphys/data/contracts.py` so `SampleContract` validates the
   public `FieldContainer` method surface while preserving existing typed
   failures for missing required fields, optional fields, wrong payload types,
   and schema mismatches.
3. Update `src/rphys/data/collation.py` so `_field_map` uses `field_items()`
   and reports the same `CollatePolicyError` shape when inputs do not satisfy
   the public runtime container surface.
4. Update `src/rphys/data/__init__.py` and package/import tests to export
   `FieldContainer` only from the owning data package without changing root or
   unrelated package exports.
5. Add focused tests for `Sample`/`Batch` protocol satisfaction, public
   `field_items()` snapshot behavior, no `_FieldEntry` exposure,
   `SampleContract` public-shape validation, LIST collation through a
   public-only field container, existing runtime contract compatibility, and
   lightweight import boundaries.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py` and, if needed,
  `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.data.containers.__all__` and
  `rphys.data.__all__` include `FieldContainer` only as an intentional
  code-backed export; importing `rphys.data` and `rphys.data.containers` remains
  lightweight and does not import heavy optional stacks or unrelated packages.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/data/test_containers.py`,
  `tests/unit/rphys/data/test_contracts.py`, and
  `tests/unit/rphys/data/test_collation.py`
- Required assertions or deferral reason: `Sample` and `Batch` satisfy
  `FieldContainer` at runtime; `field_items()` returns a tuple snapshot of
  `(FieldLocator, FieldValue)` pairs without exposing private entries; the
  private alias is not used by collation; `SampleContract` rejects containers
  missing public methods with `FieldTypeError`; LIST collation behavior and
  existing loaded accessors remain unchanged.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_runtime_core_contract.py`
- Required assertions or deferral reason: public runtime contract examples show
  loaded `Sample` and `Batch` field access through `FieldContainer` and
  `field_items()`; the data package does not export private helpers; existing
  loaded sample access, contract validation, and LIST collation examples still
  pass.

### Integration Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no multi-component lazy IO,
  datasource, codec, or builder integration behavior is in scope. Existing
  integration tests may be run opportunistically if runtime collation changes
  appear risky, but no new integration test is required.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no end-to-end workflow is introduced;
  this prep phase changes only a runtime protocol and internal/public field
  iteration surface.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real dataset, hardware, network,
  GPU, optional dependency, or long-running acceptance behavior is in scope.

## Risks

- The protocol could become too specific for primary Phase 3 lazy
  `SampleField` handles if this phase encodes payload-loading or field-object
  assumptions beyond current loaded runtime behavior.
- The protocol could be too weak if `SampleContract` keeps validating only a
  subset of the approved surface.
- Keeping `_field_items()` as a compatibility alias may obscure whether
  collation has truly moved to the public method unless tests cover a
  public-only container.
- Package export updates can unintentionally loosen import-boundary guarantees
  if `FieldContainer` pulls in anything outside lightweight data vocabulary.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/data/test_containers.py tests/unit/rphys/data/test_contracts.py tests/unit/rphys/data/test_collation.py
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

- Safe implementation slices: protocol/export first, contract validation
  second, collation hook third, tests/package expectations last.
- Tests to run with each slice: run targeted unit tests after container,
  contract, and collation edits; run `make test-package` after export changes;
  run `make test-contract` after runtime contract updates.
- Decisions the executor must not revisit: no lazy-field design, no codec or
  builder behavior, no datasource behavior, no collation policy expansion, no
  accessor semantic change, and no root export.
- Conditions that require stopping for the manager: protocol requires
  lazy-field-specific types before primary Phase 3; implementation needs codec
  imports, payload loading, datasource behavior, or collation redesign;
  `FieldContainer` cannot be exported without import-boundary regressions; or
  existing loaded-runtime contracts cannot stay green within this scope.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in
  `docs/roadmap/stage-4/phases/field-container-protocol.md`
- Final phase execution plan: ready for execution after this planning commit
- Implementation summary: pending executor
- Implementation validation: pending executor
- Refinement summary: not needed for planning
- Pre-submit blocker gate: pending executor
- PR preparation: pending executor
- Automated review: pending PR
- Merge result: pending PR
- Cleanup: pending merge
- Remaining blockers: none known

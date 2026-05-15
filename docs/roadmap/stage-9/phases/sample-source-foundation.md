# Phase 1 Execution Plan: SampleSource Foundation And Deterministic Context

## Metadata

- Status: final phase execution plan; ready for executor implementation
- Roadmap stage: `v9`
- Feature focus: index adapters, framework-neutral sample sources, and deterministic source context
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: SampleSource Foundation And Deterministic Context
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 1: SampleSource Foundation And Deterministic Context`
- Branch: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p1-sample-source-foundation`
- Phase execution plan path: `docs/roadmap/stage-9/phases/sample-source-foundation.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Planning document: `docs/roadmap/stage-9/planning.md`
- Source phase: `docs/roadmap/stage-9/implementation-plan.md` section `Phase 1: SampleSource Foundation And Deterministic Context`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path by manager override; implementation plan originally records fast path, but this phase creates public API, import-path, deterministic-context, and data-shape contracts
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: source implementation plan approved 2026-05-15 with no blockers
- Draft pass: complete in this artifact
- Refine pass: complete; expanded-path review tightened module-scoped exports, request/context fingerprint evidence, position validation, and executor stop conditions before implementation
- Setup limitations: no remote fetch or GitHub auth was run during this draft; the supplied worktree already exists, is on the assigned branch, and local `HEAD`, `develop`, and `origin/develop` all resolve to `76585bb`
- Blockers: none for implementation planning

## Objective

Establish the Stage 9 framework-neutral data-loading foundation by adding code-backed `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and `IndexSampleSource` behavior that composes existing `DataSourceIndex` and `SampleBuilder` contracts. The phase must preserve `FieldLocator`-keyed `Sample` shape, keep source context as deterministic primitive evidence, and avoid torch, cache, prepared-data, export, model-formatting, trainer, device, and workflow-runtime behavior.

## Full-Plan Context

Phase 1 is the dependency root for the Stage 9 phases. Phase 2 wraps this source API with optional torch adapters and a collater boundary. Phase 3 uses the request and context records for deterministic cache keys. Phase 4 uses source request equivalence for prepared-data reads. Phases 5 and 6 add materialization, batch-planning, and data-path evidence records after the source contract exists.

Future work must remain out of this phase: torch datasets and loader plans, cache stores and manifests, prepared manifests and readers, storage/materialization and batch-planning records, data-path profile records, concrete optimized-storage backends, real cache payload writers, active streaming/resume runtime, stable DDP cache coordination, model tuple formatting, trainer loops, device movement, raw datasource scanning, split construction, export execution, and a distinct `DerivedIndexSampleSource` without code-backed derived provenance validation.

## Source Phase Summary

- Goal: establish the common framework-neutral data-loading API before torch, cache, prepared, or batch-planning work depends on it.
- Required scope: `SampleRequest`; `SampleRuntimeContext`; `WorkerContextFactory`; `SampleSource`; `IndexSampleSource`; per-call `sample_at`; default-request `__getitem__`; request coercion; all-fields default; empty-request rejection; invalid-position and missing-field failures; deterministic context evidence.
- Required checkpoints: compose `DataSourceIndex` and `SampleBuilder`; preserve sidecar/index provenance; keep imports lightweight; add code-backed scoped exports only if tests and behavior exist; document source semantics and derived-source deferral.
- Acceptance criteria: FieldLocator-keyed lazy/eager `Sample` returns match `SampleBuilder`; subset requests preserve order; missing fields, invalid positions, empty requests, unsupported modes, and invalid context metadata fail loudly with typed errors; source foundations do not import torch/cache/prepared/export/trainer/model/device/runtime modules.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  - `src/rphys/datasources/indexes.py` exposes `DataSourceIndex` and `CompositeDataSourceIndex` with `__len__`, `__getitem__`, iteration, `entries`, and `entry_at(position)` sidecars. `DataSourceIndexEntry` already carries index, entry, record, datasource, source, split/group, field-window, child, metadata, and fingerprint evidence.
  - `src/rphys/datasources/index_items.py` defines descriptor-only `IndexItem` mappings from `FieldLocator` to `FieldView`, with non-empty field validation and no payload, item identity, cache, or export behavior.
  - `src/rphys/data/sample_builders.py` defines `SampleBuilder.build(index_item, requested=None, eager=False)`, `build_one`, and `probe`. It already implements all-fields default, subset order, duplicate and empty request rejection, missing locator failures, eager materialization through `SampleField`, and builder-side provenance.
  - `src/rphys/data/containers.py`, `src/rphys/data/sample_fields.py`, and `src/rphys/data/locators.py` define the runtime `Sample`, lazy `SampleField`, and `FieldLocator` shape Phase 1 must preserve.
  - `src/rphys/datasources/derived.py` provides descriptor-only derived datasource assembly. It does not justify a public `DerivedIndexSampleSource` in this phase.
  - `src/rphys/errors.py` already provides `RemotePhysDataSourceError`, `InvalidIndexCandidateError`, `FieldTypeError`, and `MissingFieldError`. The executor may add a narrow source-specific error only if typed failures cannot be expressed clearly with existing categories.
- Existing tests or harness behavior:
  - `tests/package/test_import.py` and `tests/package/test_import_boundaries.py` protect scoped exports, root non-exports, no heavy optional imports, and no package-level random use.
  - `tests/unit/rphys/datasources/test_datasource_indexes.py`, `tests/contracts/test_datasource_index_contract.py`, and `tests/integration/test_stage5_synthetic_datasource_flow.py` prove index item/entry separation and synthetic index-to-sample flow.
  - `tests/unit/rphys/data/test_sample_builders.py`, `tests/contracts/test_lazy_sample_builder_contract.py`, and `tests/support/lazy_sample_builder_fixtures.py` prove lazy/eager sample building, provenance, request order, missing fields, unsupported slices, and no descriptor mutation.
  - `tests/README.md` defines required suite placement: package, unit, contract, integration, e2e, acceptance, and support.
- Import-boundary or dependency constraints:
  - `pyproject.toml` has no runtime dependencies.
  - Phase 1 must keep base imports dependency-light and must not import torch, optimized-storage SDKs, plotting/array/video stacks, trainer/model packages, export operations, or test support from package code.
  - `rphys` root exports remain empty. Expanded-path review keeps Phase 1 exports module-scoped to `rphys.datasources.sources.__all__`; parent `rphys.datasources` remains Stage 3-only in this phase.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is on `develop` at `76585bb` with a pre-existing modified `docs/roadmap.md`; this plan does not edit the control checkout.
- Dedicated branch/worktree status: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p1-sample-source-foundation` is on `agent/stage-9-data-loading-cache-p1-sample-source-foundation`; it was clean before this artifact was added.
- Current `develop` base: local `HEAD`, `develop`, and `origin/develop` resolve to `76585bb` (`docs: add stage 9 implementation plan`).
- Earlier phase dependency status: none; this is Phase 1.
- Push/PR infrastructure status: not exercised during draft planning.
- Stop condition if isolation cannot be maintained: stop before code changes or PR work if this worktree diverges from the assigned branch, if unrelated local changes appear in Phase 1-owned files, or if Phase 1 cannot remain a single dedicated PR to `develop`.

## In-Scope Work

- Add `src/rphys/datasources/sources.py` with public, code-backed source foundation names:
  - `SampleRequest`
  - `SampleRuntimeContext`
  - `WorkerContextFactory`
  - `SampleSource`
  - `IndexSampleSource`
- Define `SampleRequest` as an immutable request record for requested locators, eager/lazy mode, and deterministic primitive fingerprint evidence. `requested=None` means all fields; an explicit empty request is invalid; operation/materialization fingerprints are optional primitive labels only and must not execute operations, cache, or prepared-data logic.
- Define `SampleRuntimeContext` as immutable primitive evidence, not executable workflow/RNG state. It should cover index/source/entry identity, position, request fingerprint, epoch, worker id/count, rank/world size, seed material, and primitive metadata as appropriate for Phase 1 without changing the returned `Sample` shape.
- Define `WorkerContextFactory` as a deterministic helper/factory over explicit primitive inputs. It must not call package-level random, use Python's process-local `hash()`, inspect torch worker objects in core, read time/PID/environment state, or own trainer/workflow state.
- Define `SampleSource` as the framework-neutral source contract with `__len__`, `sample_at(position, request=None, context=None)`, and default-request `__getitem__(position)`.
- Implement `IndexSampleSource` by composing `DataSourceIndex` or `CompositeDataSourceIndex` and `SampleBuilder`, retrieving aligned `IndexItem` and `DataSourceIndexEntry`, deriving or accepting context evidence, and calling `SampleBuilder.build`.
- Add failure behavior for invalid source/index/builder inputs, non-integer, negative, and out-of-range positions, empty/duplicate/malformed requests, invalid context metadata, missing requested locators, and unsupported eager behavior surfaced by `SampleBuilder`/codec paths.
- Add tests under package, unit, contract, and integration suites. Add e2e/acceptance deferral notes by test plan, not placeholder files.
- Add concise docstrings or docs in the owned code/docs surface explaining request semantics, context evidence, FieldLocator preservation, provenance, and derived-source deferral.
- Add scoped exports in `rphys.datasources.sources.__all__` only when behavior is implemented and package tests prove they are code-backed and import-light. Do not add root or parent `rphys.datasources` exports in Phase 1.

## Out-of-Scope Work

- Torch modules, torch dataset wrappers, torch loader builders, fake/missing torch behavior, and `BatchCollater`.
- Cache keys, policies, stores, manifests, local atomic commits, cached source wrappers, cache payload strategies, and cache invalidation behavior.
- Prepared-data manifests, public provisional prepared readers, prepared sample sources, prepared equivalence checks, and optimized-storage readers.
- Materialization, layout, cost, batch sampler, batch shape, data-path profile, benchmark, streaming, resume, and distributed coordination records.
- Real payload serialization, pickle-based cache behavior, concrete optimized storage adapters, remote stores, and DDP cache stability claims.
- Datasource scanning, validation, filtering, grouping, split construction, index building, raw data discovery, export/save execution, derived datasource assembly changes, and descriptor mutation.
- Model input tuple formatting, tensor stacking/padding/dropping policy expansion, device movement, model/trainer/learner loops, and generic workflow/artifact runtime.
- A public `DerivedIndexSampleSource` class unless the executor can point to code-backed derived provenance validation in this phase; a name-only subclass is rejected.
- Edits to `docs/roadmap.md` or implementation-plan status/merge metadata.

## File Ownership

- Owned for implementation:
  - `src/rphys/datasources/sources.py`
  - `tests/unit/rphys/datasources/test_sources.py`
  - `tests/contracts/test_sample_source_contract.py`
  - `tests/integration/test_stage9_sample_source_flow.py`
  - package import-boundary assertions in `tests/package/test_import.py` and `tests/package/test_import_boundaries.py`
- Conditional ownership:
  - `src/rphys/errors.py` and `tests/unit/rphys/test_errors.py` only if existing typed errors cannot express source/request/context failures cleanly.
  - `tests/support/` only for small reusable synthetic helpers needed by the new tests; no public package code may import test support.
- Do not edit in this phase:
  - `/home/samcantrill/work/rphys` control checkout
  - `docs/roadmap.md`
  - `docs/roadmap/stage-9/implementation-plan.md`
  - `src/rphys/datasources/__init__.py` unless the manager explicitly reopens the Phase 1 parent-export decision
  - torch, cache, prepared, export, model, trainer, operation, and workflow modules
  - `src/rphys/datasources/indexes.py`, `src/rphys/datasources/index_items.py`, and `src/rphys/data/sample_builders.py` unless a narrow compatibility issue blocks Phase 1 and the manager approves the scope change

## Assumptions

- Current Stage 4 `SampleBuilder` and Stage 5 `DataSourceIndex` behavior is sufficient for Phase 1 source access.
- A derived datasource that has been turned into an ordinary `DataSourceIndex` can be consumed through `IndexSampleSource` without a distinct public class.
- Source-specific request/context validation can reuse existing `RemotePhysDataSourceError` or adjacent typed error categories unless implementation evidence shows a narrow new error class is necessary.
- Deterministic context evidence is additive and primitive; it does not need to execute RNG, coordinate distributed workers, or serialize durable cache/prepared schemas in Phase 1.
- Synthetic fixtures are enough for Phase 1 unit/contract/integration validation.

## Scope Contract

Public behavior for Phase 1:

- `SampleSource.sample_at(position, request=None, context=None)` is the primary public access method. `__getitem__(position)` must call the default request path and return the same `Sample` shape.
- `__len__` reports the backing source length and does not scan or materialize data.
- Valid positions are non-boolean integers satisfying `0 <= position < len(source)`. Negative positions must not wrap through Python sequence behavior, and invalid positions must fail loudly with typed rphys context.
- `SampleRequest` with `requested=None` means every locator from the backing `IndexItem`, preserving descriptor order.
- An explicit `requested` iterable preserves caller order, rejects empty and duplicate locators, parses string locators through `FieldLocator.parse`, and fails loudly when requested locators are absent.
- `SampleRequest` fingerprints must be derived from a stable primitive representation of requested locator strings, eager mode, and optional primitive fingerprint labels. They must not use Python's process-local `hash()` or include executable objects, loaders, codec instances, torch state, cache state, prepared manifests, or raw payloads.
- Lazy requests return `Sample` objects containing lazy `SampleField` handles. Eager requests use the same `SampleBuilder` eager path and keep the lazy handles inspectable after loading.
- `IndexSampleSource` must retrieve `index[position]` and `index.entry_at(position)` for the same position and must not mutate either descriptor or sidecar.
- Context evidence must remain primitive, deterministic, and inspectable on context records/fingerprints. It can include rank/worker fields as evidence but must not claim stable DDP behavior, own torch worker/trainer state, or add a side-channel field/metadata wrapper to the returned `Sample`.
- Returned samples remain `FieldLocator` keyed and model-neutral; no tuple/dict model formatting is allowed.

Module boundaries:

- Own source foundation in `rphys.datasources.sources`.
- Compose, do not modify, `rphys.datasources.indexes`, `rphys.datasources.index_items`, and `rphys.data.sample_builders` unless implementation evidence shows a tiny compatibility bug; any such need is a stop condition for manager review if it broadens scope.
- Keep public imports module-scoped. `rphys.datasources.sources` gets `__all__`; `rphys.datasources` and `rphys` do not gain `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, or `IndexSampleSource` exports in Phase 1.
- Do not import torch, cache, prepared, export, trainer, model, workflow, test support, or heavy optional modules from `sources.py`.
- Do not add public helper modules, registries, or placeholder classes.

Data shapes:

- Requests use `FieldLocator` tuples internally and expose stable primitive fingerprints suitable for later cache/prepared equivalence.
- Runtime context metadata is string/primitive keyed and frozen or otherwise immutable. It may carry IDs/fingerprints copied from `DataSourceIndexEntry`, but not full descriptors, loaders, codec registries, field views, payloads, or mutable mappings.
- Source access returns `rphys.data.containers.Sample`, not a model tuple, raw payload, `IndexItem`, or `DataSourceIndexEntry`.

Error behavior:

- Invalid source construction, invalid requests, invalid context metadata, and invalid positions must raise typed rphys errors with inspectable context, not bare `KeyError`/`IndexError` leaks where public behavior can reasonably wrap them.
- Prefer existing `RemotePhysDataSourceError`, `FieldTypeError`, `MissingFieldError`, and locator errors. Add at most one narrow source-specific datasource error only if implementation evidence shows existing categories make public failures unclear; update package/error tests if that happens.
- Missing requested locators should preserve or wrap `MissingFieldError` semantics with requested, missing, and available locator evidence.
- Codec/materialization failures during eager loading are allowed to surface through existing `SampleBuilder`/`SampleField` error behavior and should not be hidden by source code.

Scientific semantics:

- Phase 1 does not align fields, resample, filter, normalize, mask, aggregate, or apply operations.
- Field windows, record identity, datasource identity, splits, groups, child index identity, and fingerprints remain sidecar/context evidence only.
- Subject/group/split evidence must stay inspectable through `DataSourceIndexEntry` and context metadata, with no new split or leakage policy implementation.

Edge cases the executor must not redesign:

- Empty backing indexes are valid only if existing index constructors allow them; `len(source)` should report zero and item access should fail loudly.
- Negative or out-of-range positions must not silently wrap if a public source error is required for stable behavior.
- Empty explicit requests are invalid even though `requested=None` means all fields.
- Duplicate requested locators are invalid.
- Context rank/world, worker id/count, epoch, seed, and metadata fields must validate primitive/non-negative constraints where represented.

## Scientific Contract Notes

- Sampling and temporal alignment: preserve `FieldView` and `DataSourceIndexEntry.field_windows` evidence; do not infer seconds, alignment, interpolation, or sample-rate semantics.
- Field roles, locators, schemas, and provenance: preserve `FieldLocator` keys and `SampleBuilder` provenance. Builder-side provenance remains on built `SampleField` handles; entry/source context evidence must not be pushed into codec `LoadContext`.
- Masking, filtering, normalization, and aggregation order: no masking, filtering, normalization, aggregation, operation pipeline, or hidden preprocessing is in scope.
- Subject identity, splits, leakage, and grouping: expose existing sidecar evidence where context records need it, but do not construct, rebalance, filter, or validate splits in Phase 1.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: missing fields and unsupported slices are handled by existing builder/codec failures; Phase 1 must not add signal-level validation or fallback logic.

## Design Impact

- Maintainability: keeps Stage 9 source behavior additive and compositional over existing index and sample-builder contracts.
- Extensibility: custom future sources, cache wrappers, prepared sources, and torch adapters all target the same `SampleSource` contract without changing model/trainer code.
- Lightweight import policy: source foundation has no heavy optional imports and no dependency on torch/storage SDKs.
- Source-tree boundaries: `rphys.datasources.sources` owns source/request/context records; `rphys.data.sample_builders` remains the only one-item builder; `rphys.datasources.indexes` remains descriptor/index sidecar ownership.

## Future Compatibility

- Phase 2 can wrap any `SampleSource` in torch-compatible adapters while preserving optional imports.
- Phase 3 can fingerprint `SampleRequest` and `SampleRuntimeContext` for deterministic cache keys without changing the source protocol.
- Phase 4 can prove prepared-data equivalence against `SampleRequest` and context/source identity.
- Stage 8 and Stage 13 derived outputs can use ordinary `IndexSampleSource` once represented as `DataSourceIndex`; a distinct derived source class is reserved for future code-backed provenance validation.
- Stage 15 can add rank-safe DDP/cache/profile semantics using additive context/evidence fields, not by redefining Phase 1 source access.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add `SampleSource` to `SampleBuilder` or broaden `SampleBuilder` into an index/cache loader. | Reopens Stage 4 contracts and mixes one-item building with source iteration, cache, and framework concerns. |
| Modify `DataSourceIndex` to build samples directly. | Reopens Stage 5 descriptor/index contracts and couples indexes to codec registries and runtime samples. |
| Create a name-only `DerivedIndexSampleSource`. | Manager and planning docs reject placeholder public classes; derived provenance validation is not code-backed in Phase 1. |
| Use torch worker objects or trainer state in core context records. | Violates lightweight import policy and leaks framework/runtime ownership into datasource foundations. |
| Return model tuples, raw payloads, or batch-like objects from `__getitem__`. | Breaks the canonical `FieldLocator`-keyed `Sample` contract and belongs to later model/trainer formatting work. |
| Add a registry/global symbolic source factory. | Premature abstraction; extension should use importable Python objects and `_target_` paths until symbolic names become a domain contract. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| `SampleRuntimeContext` rank/world fields are evidence only, not stable distributed coordination. | Stage 9 needs deterministic context fingerprints before DDP cache semantics are safe. | Rank-safe DDP cache tests or Stage 15 distributed/restartability work. |
| Distinct derived source class remains deferred. | Ordinary derived indexes can already use `IndexSampleSource`; public class promotion needs code-backed provenance validation. | Stage 8 derived assembly or Stage 13 prediction-derived refs require source-specific validation. |
| Request/context fingerprint helpers may start private. | Avoids premature public helper surfaces in Phase 1. | A second module/backend needs the exact helper as a public reproducibility interface. |

## Reviewability

- Expected PR size and shape: small to moderate public API PR with one new source module, focused package/unit/contract/integration tests, and concise docstrings or docs.
- Files and areas to inspect:
  - `src/rphys/datasources/sources.py`
  - `src/rphys/errors.py` and `tests/unit/rphys/test_errors.py` only if a new source-specific error is justified
  - `tests/package/test_import.py`
  - `tests/package/test_import_boundaries.py`
  - `tests/unit/rphys/datasources/test_sources.py`
  - `tests/contracts/test_sample_source_contract.py`
  - `tests/integration/test_stage9_sample_source_flow.py`
  - Existing fixture surfaces under `tests/support/`, preferably reused rather than duplicated
- Scope-control checks:
  - No edits to `docs/roadmap.md`.
  - No torch/cache/prepared/export/trainer/model/workflow imports.
  - No raw dataset fixtures.
  - No placeholder `DerivedIndexSampleSource`.
  - No parent/root exports; only `rphys.datasources.sources.__all__` is in scope.
  - No changes to `DataSourceIndex` or `SampleBuilder` unless narrowly necessary and reviewed as scope risk.

## Implementation Steps

1. Add source records and validation helpers in `src/rphys/datasources/sources.py`: immutable `SampleRequest`, deterministic primitive request fingerprinting, immutable `SampleRuntimeContext`, and a deterministic `WorkerContextFactory` over explicit primitive inputs.
2. Add the public `SampleSource` contract with `__len__`, `sample_at(position, request=None, context=None)`, and default-request `__getitem__(position)`, keeping helper implementation private unless public promotion is justified by tests.
3. Implement `IndexSampleSource` over `DataSourceIndex`/`CompositeDataSourceIndex` plus `SampleBuilder`: validate construction, reject non-integer/negative/out-of-range positions before indexing, coerce requests/context, retrieve item and aligned entry, derive context evidence, and call `SampleBuilder.build(..., requested=..., eager=...)`.
4. Add typed failure coverage and source-context provenance checks: invalid positions, empty/duplicate/malformed requested locators, missing locators, invalid context metadata, descriptor immutability, and eager/lazy behavior.
5. Add code-backed `rphys.datasources.sources.__all__` exports and import-boundary tests only after behavior exists. Keep `rphys` root empty and keep `rphys.datasources` parent exports unchanged.
6. Add concise docstrings or docs for request semantics, deterministic context evidence, FieldLocator preservation, unsupported behavior, and deferred `DerivedIndexSampleSource`.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.datasources.sources.__all__` lists only code-backed public names; package/root and parent `rphys.datasources` exports remain intentional and do not expose Phase 1 names; importing `rphys.datasources.sources` and the existing lightweight import set does not load torch or other heavy optional modules; package source still does not import or call package-level random.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/datasources/test_sources.py`; `tests/unit/rphys/test_errors.py` only if a new error class is added
- Required assertions or deferral reason: validate `SampleRequest`, context records, deterministic fingerprint/context derivation without process-local `hash()`, primitive metadata freezing, invalid metadata/rank/worker inputs, default/all-fields and subset request coercion, invalid/duplicate/empty requests, `IndexSampleSource` construction, non-integer/negative/out-of-range positions, missing fields, eager/lazy delegation, descriptor non-mutation, and no placeholder derived class.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_sample_source_contract.py`
- Required assertions or deferral reason: executable public contract for custom `SampleSource` behavior and `IndexSampleSource`: `__len__`, `__getitem__`, `sample_at`, FieldLocator-keyed `Sample` returns, request-order preservation, fail-loud missing locator behavior, context evidence inspectability, and no model tuple/raw payload behavior.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_stage9_sample_source_flow.py`; optionally extend `tests/integration/test_synthetic_datasource_index_sample_builder.py` only if reuse is cleaner than a new Stage 9 file
- Required assertions or deferral reason: synthetic `DataSourceIndex` and `CompositeDataSourceIndex` flow through `IndexSampleSource` to lazy/eager `Sample`; sidecar entry evidence aligns with built field provenance; ordinary derived records/indexes are consumable through `IndexSampleSource` without a distinct derived source class; no export/cache/torch/prepared imports are needed.

### E2E Suite

- Status: deferred
- Expected paths: none for Phase 1
- Required assertions or deferral reason: Phase 1 is a source API foundation over synthetic unit/contract/integration paths. Full source-to-loader/cache/prepared e2e behavior depends on later Stage 9 phases.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no real dataset, hardware, GPU, network, long-running, or optional dependency validation is required for Phase 1. Keep acceptance empty unless a future maintainer explicitly requests real datasource coverage.

## Risks

- Public API lock-in around `SampleRequest`, `SampleSource`, and context field names.
- Context records could drift into workflow, RNG execution, torch-worker, or trainer state if not kept primitive.
- `IndexSampleSource` might accidentally hide `IndexError`/`KeyError` or silently allow negative indexing in a way that becomes public behavior.
- Fingerprints could become process-local or non-reproducible if implemented with `hash()`, object identities, time, environment state, mutable mappings, or non-primitive metadata.
- Parent package exports could broaden the public surface beyond the refined module-scoped import decision.
- Duplicate request validation may diverge from existing `SampleBuilder` semantics if rewritten instead of composed carefully.
- A derived-source placeholder could slip in because the roadmap names derived sources; the approved plan explicitly rejects that until validation is code-backed.

## Stop Conditions

- Stop before implementation if executor implementation appears to require changing the public source protocol, request shape, context record fields, or refined module-scoped export policy.
- Stop if source behavior requires modifying `DataSourceIndex`, `IndexItem`, `SampleBuilder`, `Sample`, or `SampleField` public contracts.
- Stop if a distinct `DerivedIndexSampleSource` appears necessary without code-backed derived provenance validation.
- Stop if Phase 1 cannot remain dependency-light without torch, cache, prepared, export, model, trainer, device, workflow, or optimized-storage imports.
- Stop if typed source failures require a new error taxonomy broader than one narrow source/request/context error.
- Stop if `sample_at` needs to return anything other than `Sample`, or if context/source evidence would need to be injected into sample fields, codec `LoadContext`, or model-formatted structures to be inspectable.
- Stop if deterministic fingerprints require public helper/protocol promotion beyond the approved Phase 1 names.
- Stop if unrelated local changes appear in Phase 1-owned files or if the branch/worktree is no longer isolated from the control checkout.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/datasources/test_sources.py
uv run pytest tests/contracts/test_sample_source_contract.py
uv run pytest tests/integration/test_stage9_sample_source_flow.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Acceptance Evidence

- Behavior evidence: `sample_at` and `__getitem__` return FieldLocator-keyed `Sample` objects for all-fields and subset requests; eager and lazy paths match `SampleBuilder` behavior; subset order is preserved.
- Failure evidence: explicit empty requests, duplicate requests, malformed locators, missing locators, invalid positions, invalid source construction, and invalid context metadata fail loudly with typed rphys errors and inspectable context.
- Design-decision evidence: no root or parent exports, no placeholder classes, no model tuple formatting, no raw payload returns, no descriptor mutation, no torch/cache/prepared/export/trainer/model/device/workflow imports.
- Future-roadmap/reuse evidence: any `DataSourceIndex` or `CompositeDataSourceIndex`, including indexes built from derived records, can be wrapped by `IndexSampleSource`; distinct `DerivedIndexSampleSource` remains deferred.
- Documentation evidence: docstrings or docs explain request semantics, eager/lazy behavior, deterministic context evidence, provenance boundaries, unsupported behavior, and derived-source deferral.
- Scientific contract evidence: source/index/entry identity, stable primitive request fingerprints, record/datasource/split/group sidecar evidence, field windows, and builder provenance remain inspectable without changing sample scientific meaning or returned sample shape.

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: start with request/context records and tests, then source protocol, then `IndexSampleSource`, then exports/import tests, then docs/docstrings.
- Tests to run with each slice: unit tests for records first; contract tests after `SampleSource`; integration after `IndexSampleSource`; package import tests after exports/import changes.
- Decisions the executor must not revisit: `sample_at(position, request=None, context=None)`, `__len__`, default-request `__getitem__`, `rphys.datasources.sources` ownership, module-scoped exports only, non-negative integer position semantics, no root or parent exports, no placeholder `DerivedIndexSampleSource`, no torch/cache/prepared/export/trainer/model/device/workflow behavior, and context as primitive evidence rather than runtime state.
- Conditions that require stopping for the manager:
  - A public helper/protocol beyond the approved names becomes necessary.
  - A distinct derived source class seems necessary without code-backed provenance validation.
  - Implementing source behavior requires changing `DataSourceIndex`, `IndexItem`, or `SampleBuilder` contracts.
  - Cache/prepared/torch/materialization concerns are needed to make the source API work.
  - A heavy optional dependency, package-level random, root export, or generic registry appears necessary.
  - Parent `rphys.datasources` exports, process-local fingerprints, or sample-shape changes appear necessary.
  - The branch/worktree gets unrelated changes in Phase 1-owned files.

## Refinement And Review Budget Status

- Expanded-path reason: Phase 1 establishes public `SampleSource` API, import path, request/context records, deterministic fingerprint semantics, and returned sample shape used by later torch/cache/prepared phases.
- Phase execution plan refinement: complete; expanded-path refinement used for plan-only tightening, not implementation
- Phase implementation refinement: complete; 1 refinement used to reject caller-supplied `SampleRuntimeContext` records whose entry or request evidence does not match the sample being built
- PR review: unused
- Blocker resolution: 1/3 used
- Refinement focus resolved: public API stays minimal; request/context fingerprints are primitive and deterministic; error taxonomy remains existing-first with at most one narrow new source error; parent exports are out of scope; negative/non-integer positions fail loudly; `SampleRuntimeContext` remains evidence-only and does not imply stable DDP/workflow semantics.

## Phase Refinement Report: Context Evidence Coherence

## Assigned Blocker

- Blocker: `IndexSampleSource.sample_at` accepted a valid `SampleRuntimeContext` for a different source position or request fingerprint without failing.
- Source: expanded-path Phase 1 implementation refinement against context evidence and typed failure semantics.
- Scope: `src/rphys/datasources/sources.py`, focused source unit tests, and this phase artifact.
- Budget use: Phase implementation refinement 1 used; blocker resolution 1/3 used.

## Resolution

- Changes made: caller-supplied context records are now validated against the aligned `DataSourceIndexEntry` and coerced `SampleRequest` before sample construction; mismatches raise `RemotePhysDataSourceError` with inspectable mismatch evidence.
- Tests or docs updated: added unit coverage for mismatched context position and request fingerprint; updated refinement notes.
- Validation rerun: focused Phase 1 pytest set, `make test-package`, `make test-contract`, and `git diff --check` passed. Focused `uv run ruff check ...` could not run because `ruff` is not installed in the project environment.

## Result

- Blocker resolved: yes.
- Remaining blocker: none identified in Phase 1 scope.
- Recommended next gate: PR preparation after final commit and normal review.

## Files Changed

- `src/rphys/datasources/sources.py`
- `tests/unit/rphys/datasources/test_sources.py`
- `docs/roadmap/stage-9/phases/sample-source-foundation.md`

## PR Body Readiness Report

- PR body refine: complete 2026-05-15 after comparing `docs/roadmap/stage-9/phases/sample-source-foundation-pr-body.md` against the committed `develop...HEAD` diff, phase scope, implementation-plan constraints, validation evidence, and known blocker notes.
- Title/base/head readiness: prepared for title `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 1: SampleSource Foundation And Deterministic Context`, base `develop`, and head `agent/stage-9-data-loading-cache-p1-sample-source-foundation`. PR not opened in this pass per manager instruction.
- PR body accuracy: body accurately describes the new `rphys.datasources.sources` source foundation, module-scoped exports, FieldLocator-keyed `Sample` returns, deterministic primitive request/context evidence, typed fail-loud behavior, validation evidence, and future-phase exclusions.
- Future-phase exclusions confirmed: no torch adapter, collater, cache store, prepared reader/source, materialization, batch-planning, data-path profile, model formatting, device movement, trainer loop, datasource scanning, split construction, export execution, or distinct `DerivedIndexSampleSource` claim appears in the PR body.
- Pre-submit blocker gate: no unresolved known source API, parent-export, negative-position, fingerprint, context-shape, validation-evidence, PR-body, metadata, or derived-source promotion blocker remains.
- Lightweight readiness checks: `git diff --check develop...HEAD`, `git diff --check`, `git diff --name-only develop...HEAD`, `git diff --name-only`, and `git status --short` passed during PR-body refinement. Full suites were rerun afterward by the manager.
- Manager follow-up: accepted the local `tests/contracts/test_sample_source_contract.py` update as in-scope contract coverage for FieldLocator-keyed `Sample` returns, eager/request ordering, missing-locator failures, and aligned context evidence. `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed afterward with 724 total tests.

## Completion Notes

- Draft plan: complete in `docs/roadmap/stage-9/phases/sample-source-foundation.md`
- Final phase execution plan: complete after expanded-path refinement
- Implementation summary: complete; Phase 1 source foundation APIs are implemented, with refinement tightening accepted context evidence coherence.
- Implementation validation: `uv run pytest tests/unit/rphys/datasources/test_sources.py`; `uv run pytest tests/unit/rphys/datasources/test_sources.py tests/contracts/test_sample_source_contract.py tests/integration/test_stage9_sample_source_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py`; `make test-package`; `make test-contract`; `UV_CACHE_DIR=/tmp/uv-cache make validate-pr`; `UV_CACHE_DIR=/tmp/uv-cache make test-summary`; `git diff --check` all passed.
- Refinement summary: plan refinement tightened public API/import-path/data-shape decisions; implementation refinement now rejects context records whose source-entry or request evidence does not match the requested sample without changing the returned `Sample` shape.
- Pre-submit blocker gate: no unresolved source API, parent-export, negative-position, fingerprint, context-shape, or derived-source promotion decision remains in this plan
- PR body draft: complete in `docs/roadmap/stage-9/phases/sample-source-foundation-pr-body.md`
- PR body refine: complete on expanded path
- PR preparation: PR opened and verified as non-draft PR #60 against base `develop` from head `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- Automated review: complete; no blocking findings, PR-review budget consumed, and merge eligible assuming PR opens against `develop` and CI matches local validation
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none identified; PR body is ready for manager submission after automated review

## Automated Phase PR Review Report

- Review date: 2026-05-15
- Reviewer: `rphys_phase_reviewer`
- Findings: no blocking findings identified.
- Scope and acceptance: phase scope satisfied; future-phase torch, cache, prepared, export, trainer, model-formatting, device, workflow-runtime, and derived-source placeholder work avoided; acceptance criteria satisfied for FieldLocator-keyed samples, ordered subset requests, eager/lazy delegation, invalid position/request/context failures, missing locator failures, context evidence validation, and module-scoped exports.
- PR body: matches the final committed diff, scientific contract, validation, and deferred work.
- Validation reviewed: `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed with package 36, unit 571, contract 103, integration 14, total 724.
- Target branch expectation: PR must open against `develop`; `origin/develop` is an ancestor of branch head `6b63e97`.
- Review decision: blocking findings remain no; PR-review budget consumed yes; merge eligible yes, assuming PR CI matches local validation.
- Residual risks: context rank/world/worker fields are evidence only, not distributed coordination; future cache/prepared phases must preserve request/context equivalence without expanding Phase 1 sample shape.

## PR Submission Metadata

- PR: https://github.com/samcantrill/rphys/pull/60
- Number: 60
- State: open
- Draft: no
- Base: `develop`
- Head: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- Title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 1: SampleSource Foundation And Deterministic Context`
- Initial status checks: no GitHub status checks reported at PR-open verification time.

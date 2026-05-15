# Phase 2 Execution Plan: Torch Adapter And FieldLocator Collater Boundary

## Metadata

- Status: final phase execution plan; ready for executor implementation
- Roadmap stage: `v9`
- Feature focus: optional torch-compatible iteration and FieldLocator-preserving collation
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: Torch Adapter And FieldLocator Collater Boundary
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 2: Torch Adapter And FieldLocator Collater Boundary`
- Branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Phase execution plan path: `docs/roadmap/stage-9/phases/torch-collater-boundary.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Planning document: `docs/roadmap/stage-9/planning.md`
- Source phase: `docs/roadmap/stage-9/implementation-plan.md` section `Phase 2: Torch Adapter And FieldLocator Collater Boundary`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path by manager override; implementation plan records fast path, but this phase creates public optional torch adapter, data-loader builder, and collater/import-policy contracts
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to `develop`; local-only completion is not allowed
- Plan quality gate: source implementation plan approved 2026-05-15 with no blockers; Phase 1 merged and provides `rphys.datasources.sources`
- Draft pass: complete in this artifact
- Refine pass: complete; expanded-path self-refinement tightened optional dependency import policy, public export boundaries, collater scientific contract, suite obligations, and stop conditions before implementation
- Setup limitations: no remote fetch or GitHub auth was run during this draft; the supplied worktree already existed, was clean, and was on the assigned branch at local `develop` base `ae0700d`
- Blockers: none for implementation planning

## Objective

Add the smallest optional torch-compatible data-loading boundary over the Phase 1 `SampleSource` API and add a `BatchCollater` that preserves existing `FieldLocator`-keyed `Batch` semantics by delegating to `collate_samples`. The phase must make torch behavior available only through import-gated adapter paths, keep core imports dependency-light, and avoid trainer loops, device movement, model tuple formatting, custom stack/pad/drop policy, datasource scanning, index construction, export, cache, or prepared-data behavior.

## Full-Plan Context

Phase 1 established `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and `IndexSampleSource` in `rphys.datasources.sources`. Phase 2 wraps that source API for torch-style iteration and adds the collater callable that later trainer code can pass to a framework loader without changing the scientific batch shape.

Phase 3 will add deterministic cache contracts and local store behavior. Phase 4 will add prepared manifest/reader/source equivalence. Phase 5 will add materialization, layout, cost, and batch-planning records. Phase 6 will close Stage 9 with data-path evidence/docs/package closeout. Those later phases must remain out of Phase 2, especially cache/prepared semantics, materialized storage, active streaming/resume state, stable DDP coordination, model/trainer/device behavior, and data-path profiling.

## Source Phase Summary

- Goal: provide framework-compatible iteration over `SampleSource` while preserving core import boundaries and FieldLocator-keyed collation.
- Required scope: `TorchSampleSourceDataset`; optional `TorchIndexSampleDataset` only as a fully code-backed convenience over Phase 1 `IndexSampleSource`; `TorchDataLoaderPlan`; `TorchDataLoaderBuilder`; `BatchCollater`; focused adapter/collater/package tests; docs or docstrings for optional dependency behavior.
- Required checkpoints: torch imports are lazy/import-gated; adapter delegates to `SampleSource`; missing torch raises typed dependency diagnostics only for behavior that truly requires torch; collater delegates to `collate_samples`; public exports remain scoped and code-backed.
- Acceptance criteria: core imports stay lightweight without torch; dataset wrappers return `Sample` objects and do not scan/build/export/format; loader builder is data-only except for lazy `torch.utils.data.DataLoader` construction; collater returns existing `Batch` shape with `FieldLocator` keys and current LIST-only failure behavior.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  - `src/rphys/datasources/sources.py` exports `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and `IndexSampleSource`. `IndexSampleSource.sample_at(position, request=None, context=None)` is the required adapter boundary.
  - `src/rphys/data/collation.py` provides LIST-only `collate_samples(samples, context=None) -> Batch`, `CollateContext`, and `CollatePolicy`. It rejects empty samples, empty field sets, heterogeneous field locators, missing explicit field policies, unsupported policies, and schema mismatches.
  - `src/rphys/data/containers.py` defines `Sample` and `Batch` as `FieldLocator`-keyed runtime containers. Phase 2 must preserve those shapes.
  - `src/rphys/datasources/__init__.py` currently re-exports only Stage 3 descriptor names. Phase 2 should not add optional torch names to the parent datasource package unless the manager explicitly reopens that public surface.
  - `src/rphys/data/__init__.py` already re-exports framework-neutral runtime data names. `BatchCollater` is expected to become a code-backed `rphys.data` package export because it is framework-neutral collation behavior, with package tests updated.
  - `src/rphys/errors.py` already provides `RemotePhysDependencyError`, `RemotePhysDataSourceError`, `CollatePolicyError`, and `FieldTypeError`. A new error class is not expected.
- Existing tests or harness behavior:
  - `tests/package/test_import.py` checks root export emptiness, module `__all__` values, parent package exports, and code-backed public names.
  - `tests/package/test_import_boundaries.py` treats `torch` as a heavy optional module and asserts lightweight imports do not load it.
  - `tests/unit/rphys/data/test_collation.py` covers LIST-only collation behavior and the public field-items protocol.
  - `tests/unit/rphys/datasources/test_sources.py`, `tests/contracts/test_sample_source_contract.py`, and `tests/integration/test_stage9_sample_source_flow.py` cover source delegation targets and synthetic source fixtures available to Phase 2 tests.
  - `tests/README.md` requires suite separation across package, unit, contract, integration, e2e, acceptance, and support.
- Import-boundary or dependency constraints:
  - `pyproject.toml` has no runtime dependencies and no torch extra.
  - Importing `rphys`, `rphys.data`, `rphys.data.collation`, `rphys.datasources`, `rphys.datasources.sources`, and `rphys.datasources.torch` must not import `torch`.
  - `TorchDataLoaderBuilder` is the only Phase 2 behavior expected to require lazy torch import. Missing torch must raise `RemotePhysDependencyError` with inspectable context instead of `ImportError`.

## Phase Isolation State

- Control checkout dirty-state review: `/home/samcantrill/work/rphys` is on `develop` at `ae0700d` with pre-existing modified `docs/roadmap.md` and untracked `docs/roadmap/stage-10/`; this plan does not edit the control checkout.
- Dedicated branch/worktree status: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p2-torch-collater-boundary` is on `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`; it was clean before this artifact was added.
- Current `develop` base: local `develop` resolves to `ae0700d1880ecd0a4955bcd9c4f5b812e6562e5e`, matching the manager-supplied base.
- Earlier phase dependency status: Phase 1 is merged into `develop` and provides `rphys.datasources.sources`.
- Push/PR infrastructure status: not exercised during draft planning.
- Stop condition if isolation cannot be maintained: stop before code changes or PR work if this worktree diverges from the assigned branch, if unrelated local changes appear in Phase 2-owned files, or if Phase 2 cannot remain a single dedicated PR to `develop`.

## In-Scope Work

- Add `src/rphys/datasources/torch.py` as an optional, import-gated adapter module with code-backed public names:
  - `TorchSampleSourceDataset`
  - `TorchIndexSampleDataset`, only as a thin convenience over `IndexSampleSource`
  - `TorchDataLoaderPlan`
  - `TorchDataLoaderBuilder`
- Implement `TorchSampleSourceDataset` as a map-style dataset wrapper over any `SampleSource`: `__len__` delegates to the source and `__getitem__(position)` delegates to `source.sample_at(position, request=<configured request>)` or default source indexing. It returns `Sample`, not tuple/dict/model inputs.
- Implement `TorchIndexSampleDataset` only if it stays a constructor convenience that builds an `IndexSampleSource` from an existing `DataSourceIndex`/`CompositeDataSourceIndex` and `SampleBuilder`. It must not scan raw data, build indexes, export fields, or add distinct derived-source behavior.
- Implement `TorchDataLoaderPlan` as a data-only validated record for explicit loader settings such as `batch_size`, `shuffle`, `drop_last`, `num_workers`, and other primitive torch DataLoader kwargs that do not imply device, trainer, distributed coordination, or model formatting.
- Implement `TorchDataLoaderBuilder` as a small object/function that lazily imports `torch.utils.data.DataLoader` only when constructing an actual torch DataLoader. Missing torch raises `RemotePhysDependencyError` with dependency/module and operation context.
- Add `BatchCollater` in `src/rphys/data/collation.py`. The callable must delegate to `collate_samples(samples, context=<optional CollateContext>)`.
- Update code-backed exports:
  - `rphys.datasources.torch.__all__` lists only implemented adapter names.
  - `rphys.datasources.__all__` remains unchanged unless the manager explicitly reopens datasource parent exports for optional adapter names.
  - `rphys.data.collation.__all__` includes `BatchCollater`.
  - `rphys.data.__all__` includes `BatchCollater` because it is framework-neutral runtime collation behavior.
- Add focused package, unit, contract, and integration tests for adapter delegation, lazy/missing/fake torch behavior, collater delegation, public exports, and import boundaries.
- Add concise docstrings or docs explaining optional dependency behavior, `SampleSource` delegation, FieldLocator preservation, LIST-only collation, and unsupported trainer/device/model-formatting/padding behavior.

## Out-of-Scope Work

- Adding torch to runtime dependencies, dependency groups, lockfile requirements, or mandatory test environment assumptions.
- Importing torch from `rphys`, `rphys.data`, `rphys.data.collation`, `rphys.datasources`, `rphys.datasources.sources`, cache, prepared, sample builders, or package import paths.
- Trainer loops, learner integration, Lightning-specific behavior, device movement, pinned-device transfer semantics, GPU assumptions, distributed sampler/DDP coordination, rank-safe cache behavior, or active streaming/resume state.
- Model tuple/dict formatting, hard-coded `inputs`/`targets` outputs, tensor stacking, padding, truncating, dropping, custom collate policies, callable dispatch, or payload-owned collation.
- Datasource scanning, validation, filtering, grouping, split construction, index building, export/save execution, derived datasource assembly, or prepared/cache/materialized data behavior.
- Root `rphys` exports and placeholder registry/factory modules.
- Cache keys/stores/manifests, prepared manifests/readers/sources, materialization/layout/cost records, batch sampler records, data-path profile/benchmark records, or storage backend adapters.
- Raw datasets, GPU/real torch acceptance tests, network access, or long-running benchmark checks.

## File Ownership

- Owned for implementation:
  - `src/rphys/datasources/torch.py`
  - `src/rphys/data/collation.py`
  - `src/rphys/data/__init__.py`
  - `tests/unit/rphys/datasources/test_torch.py`
  - `tests/unit/rphys/data/test_collation.py`
  - `tests/contracts/test_torch_adapter_contract.py`
  - `tests/contracts/test_batch_collater_contract.py`
  - `tests/integration/test_stage9_torch_collater_flow.py`
  - `tests/package/test_import.py`
  - `tests/package/test_import_boundaries.py`
- Conditional ownership:
  - `src/rphys/datasources/__init__.py` only if the manager explicitly approves parent datasource exports for optional adapter names.
  - `tests/support/` only for tiny synthetic/fake helper reuse; package code must not import test support.
  - `src/rphys/errors.py` and `tests/unit/rphys/test_errors.py` only if existing dependency/collation/datasource error categories cannot express required typed failures.
- Do not edit in this phase:
  - `/home/samcantrill/work/rphys` control checkout
  - `docs/roadmap.md`
  - `docs/roadmap/stage-9/implementation-plan.md`
  - cache, prepared, materialization, export, model, trainer, learning, prediction, analysis, and workflow modules
  - `src/rphys/datasources/sources.py`, `src/rphys/datasources/indexes.py`, or `src/rphys/data/sample_builders.py` unless a narrow compatibility issue blocks Phase 2 and the manager approves the scope change

## Assumptions

- A map-style object with `__len__` and `__getitem__` is sufficient for torch `DataLoader` consumption; subclassing `torch.utils.data.Dataset` is not necessary and would threaten import-gating.
- Missing-torch tests can be performed without adding torch by monkeypatching import behavior or using a fake module path around the lazy import branch.
- Fake torch coverage is sufficient for `TorchDataLoaderBuilder` unless the project later defines a real optional torch test extra.
- `BatchCollater` can reuse existing `CollateContext`, `CollatePolicy`, and `collate_samples` without altering LIST-only behavior.
- Parent datasource exports for optional torch names are unnecessary for Phase 2; direct module imports through `rphys.datasources.torch` are the intended public path. `BatchCollater` is different: it is framework-neutral collation behavior and should be parent-exported from `rphys.data`.
- Synthetic `SampleSource` and `IndexSampleSource` fixtures are enough for package/unit/contract/integration validation.

## Scope Contract

Public behavior for Phase 2:

- `rphys.datasources.torch` must be importable without torch installed and without loading torch into `sys.modules`.
- `TorchSampleSourceDataset` wraps a `SampleSource`, validates constructor inputs, delegates `__len__` to the source, and delegates item access to `source.sample_at(position, request=<configured request>)` or `source[position]` default behavior. It returns `Sample`.
- Dataset item access must preserve `SampleSource` typed failure behavior for invalid positions, invalid requests, missing fields, and eager/lazy failures. It must not catch and reclassify scientific/source errors as torch errors.
- `TorchIndexSampleDataset`, if implemented, is only a convenience wrapper over `IndexSampleSource(index, builder, ...)`. Its public behavior is identical to `TorchSampleSourceDataset(IndexSampleSource(...), ...)`.
- `TorchDataLoaderPlan` is a primitive/data-only plan. It can validate loader kwargs but must not create a torch object, inspect devices, inspect models, own workers, own distributed state, or decide scientific collation policy.
- `TorchDataLoaderBuilder` lazily imports `torch.utils.data.DataLoader` only when building a torch DataLoader. If torch is unavailable or malformed, it raises `RemotePhysDependencyError` with dependency and operation context. It must pass a `BatchCollater` or caller-supplied collate callable explicitly; it must not use torch default collation for `Sample` objects.
- `BatchCollater.__call__(samples)` must call `collate_samples(samples, context=<configured context>)` and return `Batch`. It must not add stack, pad, drop, tuple formatting, tensor conversion, device movement, field renaming, hard-coded input/target grouping, or missing-field filling.
- `BatchCollater` must preserve existing `collate_samples` failure behavior for empty batches, empty field sets, heterogeneous field sets, missing explicit policies, unsupported policies, schema mismatches, and invalid sample-like containers.

Module boundaries:

- `rphys.datasources.torch` may import Phase 1 source contracts, `DataSourceIndex`/`CompositeDataSourceIndex`, `SampleBuilder`, `BatchCollater`, and existing rphys errors. It must not be imported by `rphys.datasources.sources`, cache, prepared, indexes, sample builders, or root package code.
- `rphys.data.collation` must remain independent of datasource indexes, torch, cache, prepared, trainer, model, and storage backends.
- Root `rphys.__all__` remains empty. No root `rphys` attribute is added for torch adapter or collater names.
- No public registries, symbolic framework registries, or placeholder adapter classes are added.

Data shapes:

- Dataset items are `Sample` instances keyed by `FieldLocator`.
- Collated outputs are `Batch` instances keyed by `FieldLocator`.
- Request values may be `SampleRequest`/`SampleRequestLike` as supported by Phase 1 and must be coerced by the source path, not by duplicating source request semantics in torch code.
- Loader plans contain primitive or simple immutable values suitable for equality/inspection; they are not durable cache/prepared manifests.

Error behavior:

- Missing torch is a dependency error only for behavior that requires constructing a torch DataLoader.
- Invalid dataset/source/plan/collater inputs should raise typed rphys errors with inspectable context, using existing categories unless implementation evidence justifies a narrow addition.
- Torch adapter code must not swallow `CollatePolicyError`, `MissingFieldError`, `RemotePhysDataSourceError`, or eager loading failures from the source/collater path.

Scientific semantics:

- Phase 2 does not transform payload values, align fields, resample, normalize, mask, aggregate, augment, or apply sample/batch operations.
- Field roles, schemas, metadata, locator identity, request fingerprints, source context evidence, and builder provenance remain as provided by Phase 1 and existing collation.
- Collation keeps LIST-only semantics. Any future stack/pad/drop/tensor conversion policy belongs to a later explicit phase or downstream model/trainer adapter.

Edge cases the executor must not redesign:

- Empty sample sequences still fail through `collate_samples`.
- Heterogeneous field sets still fail; do not fill missing fields.
- Negative positions still follow Phase 1 source failure behavior; do not implement Python sequence wraparound in the dataset wrapper.
- `batch_size=None`, custom `collate_fn`, `num_workers`, and other torch DataLoader kwargs are loader-plan configuration only; they do not imply device or trainer ownership.
- Fake torch modules used in tests must not become package dependencies or public shims.

## Scientific Contract Notes

- Sampling and temporal alignment: no new sampling, slicing, alignment, resampling, or temporal-window semantics are introduced. The adapter consumes the `SampleSource` result exactly as built.
- Field roles, locators, schemas, and provenance: dataset wrappers and `BatchCollater` preserve `FieldLocator` keys, field schema evidence, field metadata, and source/builder provenance exposed by existing objects.
- Masking, filtering, normalization, and aggregation order: no masking, filtering, normalization, aggregation, sample operations, batch operations, or hidden preprocessing is in scope.
- Subject identity, splits, leakage, and grouping: subject/split/group evidence remains source/index/context metadata. Torch adapters do not shuffle or split semantically beyond forwarding explicit torch loader kwargs; no leakage policy is implemented here.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: Phase 2 does not inspect signal payloads. Missing fields and unsupported slices fail through the existing source/builder/collater paths.

## Design Impact

- Maintainability: isolates framework adapter behavior in `rphys.datasources.torch` and keeps `rphys.data.collation` as the single collation implementation.
- Extensibility: future framework adapters can wrap `SampleSource` the same way without changing cache/prepared/source contracts; future collaters can be additive only after explicit policy design.
- Lightweight import policy: importing core rphys modules and the optional adapter module remains possible without importing torch.
- Source-tree boundaries: `datasources.torch` owns optional framework construction; `data.collation` owns framework-neutral batch construction; trainers/models/devices remain outside Stage 9 Phase 2.

## Future Compatibility

- Stage 10/12 trainers can pass `TorchSampleSourceDataset` and `BatchCollater` to torch later, then format batches at the model/trainer boundary rather than in the loader.
- Phase 3 cache wrappers can wrap `SampleSource` before torch datasets without changing adapter behavior.
- Phase 4 prepared sources can expose the same `SampleSource` shape and use the same torch dataset wrapper.
- Phase 5 batch-planning records can later feed explicit loader kwargs or sampler plans without changing `BatchCollater` LIST-only semantics.
- Stage 15 profiling can observe loader/cache/materialization evidence later without Phase 2 claiming active profiling or benchmark behavior.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Make torch a runtime dependency or add torch to default validation. | Breaks repository dependency-light policy and package import-boundary tests. |
| Subclass `torch.utils.data.Dataset` at module import time. | Forces torch import to define public classes and makes `rphys.datasources.torch` unavailable without torch. |
| Let torch default collation process `Sample` objects. | Loses the explicit `FieldLocator`/`Batch` contract and risks tuple/dict/model formatting. |
| Add stack/pad/drop/tensor conversion policy in `BatchCollater`. | Reopens collation semantics beyond Phase 2 and hides scientifically meaningful shape decisions. |
| Add trainer/device/model tuple formatting to the dataset or builder. | Belongs to later trainer/model adapters and would couple data loading to model-specific contracts. |
| Add a generic framework registry. | Premature abstraction; extension should use importable Python objects until symbolic names become a domain contract. |
| Parent-export optional torch adapter names from `rphys.datasources` by default. | Broadens the base datasource package surface for optional framework behavior; direct `rphys.datasources.torch` imports are enough. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Real torch integration may be covered by fake/missing torch tests rather than an installed torch extra. | The repository currently has no runtime deps or torch extra, and Phase 2 must not make torch mandatory. | Maintainer adds an optional torch extra or requests real torch CI coverage. |
| `TorchDataLoaderPlan` starts as data-only and may not cover every `torch.utils.data.DataLoader` kwarg. | A narrow explicit plan reduces accidental trainer/device/runtime ownership. | First downstream trainer needs a validated additional kwarg or sampler hook. |
| `BatchCollater` remains LIST-only and does not handle tensor stacking or padding. | Existing collation semantics are intentionally narrow and scientifically explicit. | A later batch-shape policy phase or trainer adapter designs explicit stack/pad/drop behavior. |
| Parent datasource exports remain unchanged for optional torch names. | Keeps optional framework behavior out of base datasource import surface. | Maintainer requests package-level convenience exports after code-backed usage pressure. |

## Reviewability

- Expected PR size and shape: moderate public adapter/collater PR with one new optional torch module, a small collater addition, focused package/unit/contract/integration tests, and concise docstrings.
- Files and areas to inspect:
  - `src/rphys/datasources/torch.py`
  - `src/rphys/data/collation.py`
  - `src/rphys/data/__init__.py`
  - `tests/package/test_import.py`
  - `tests/package/test_import_boundaries.py`
  - `tests/unit/rphys/datasources/test_torch.py`
  - `tests/unit/rphys/data/test_collation.py`
  - `tests/contracts/test_torch_adapter_contract.py`
  - `tests/contracts/test_batch_collater_contract.py`
  - `tests/integration/test_stage9_torch_collater_flow.py`
- Scope-control checks:
  - No `pyproject.toml` runtime dependency or lockfile dependency change for torch.
  - No root exports.
  - No parent `rphys.datasources` torch exports unless manager-approved.
  - No torch import during base or optional module import.
  - No tuple/model formatting, tensor conversion, stack/pad/drop behavior, trainer/device/runtime code, datasource scanning, index building, export, cache, or prepared logic.

## Implementation Steps

1. Add `BatchCollater` as a thin callable over `collate_samples`, with unit and contract tests proving delegation, FieldLocator-keyed `Batch` output, metadata preservation, and unchanged LIST-only failures.
2. Add `rphys.datasources.torch` public adapter names and constructor validation without importing torch at module import time; prove module import is light through package tests.
3. Implement `TorchSampleSourceDataset` and the optional `TorchIndexSampleDataset` convenience wrapper by delegating to Phase 1 `SampleSource`/`IndexSampleSource` behavior; add focused unit and contract tests for length, item access, request forwarding, and error propagation.
4. Add `TorchDataLoaderPlan` and `TorchDataLoaderBuilder` with lazy `torch.utils.data.DataLoader` import, typed missing dependency diagnostics, fake torch builder coverage, and explicit collater wiring.
5. Update scoped exports and package tests for `rphys.datasources.torch`, `rphys.data.collation`, and the required `rphys.data` parent `BatchCollater` export while keeping `rphys` root and parent `rphys.datasources` surfaces controlled.
6. Add docstrings or docs for optional dependency behavior, adapter boundaries, unsupported behavior, and future-phase exclusions.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: `rphys.datasources.torch.__all__` lists only implemented adapter names; `rphys.data.collation.__all__` includes `BatchCollater`; `rphys.data.__all__` includes the code-backed `BatchCollater` parent export; `rphys.__all__` remains empty; `rphys.datasources.__all__` remains Stage 3-only unless manager-approved; importing lightweight modules, including `rphys.datasources.torch`, does not load `torch` or other heavy optional modules.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/datasources/test_torch.py`, `tests/unit/rphys/data/test_collation.py`; `tests/unit/rphys/test_errors.py` only if a new error class is added
- Required assertions or deferral reason: dataset wrappers validate inputs, delegate length and item access to `SampleSource`, forward configured request behavior, return `Sample`, preserve source errors, avoid scanning/building/exporting/formatting, validate loader plans, lazily import torch only in builder behavior, raise `RemotePhysDependencyError` when torch is missing, build with a fake torch DataLoader when monkeypatched, and `BatchCollater` delegates to `collate_samples` with unchanged failure behavior.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_torch_adapter_contract.py`, `tests/contracts/test_batch_collater_contract.py`
- Required assertions or deferral reason: executable public contract over any `SampleSource` wrapper: map-style dataset returns FieldLocator-keyed `Sample`, loader builder requires explicit collation, no model tuple/dict formatting appears, `BatchCollater` returns FieldLocator-keyed `Batch`, current LIST-only policy is preserved, missing/unsupported collation remains fail-loud, and optional dependency failures are typed.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/test_stage9_torch_collater_flow.py`
- Required assertions or deferral reason: synthetic `IndexSampleSource` feeds `TorchSampleSourceDataset`; a small sequence of dataset samples feeds `BatchCollater`; the output `Batch` preserves `FieldLocator` keys, schemas, metadata, and LIST payload ordering. If fake torch DataLoader integration is small and stable, include one fake-builder smoke; otherwise keep fake torch coverage in unit tests and document the integration deferral.

### E2E Suite

- Status: deferred
- Expected paths: none for Phase 2
- Required assertions or deferral reason: full end-to-end training or torch DataLoader execution with real torch belongs to later trainer/optional-dependency work. Phase 2 validates the public adapter/collater boundary with package, unit, contract, and synthetic integration coverage.

### Acceptance Suite

- Status: deferred
- Markers affected: none required; optional future real torch checks would use `optional_dependency` and possibly `acceptance`
- Required assertions or deferral reason: no real dataset, GPU, installed torch, network, hardware, or long-running acceptance check is required for this phase. Do not add acceptance tests unless a maintainer adds an optional torch environment requirement.

## Risks

- Import leakage: defining torch adapter classes or builder helpers might import torch during package/module import.
- Scientific shape drift: torch adapter or collater might convert `Sample`/`Batch` to tuples, dicts, tensors, or hard-coded input/target structures.
- Collation semantic drift: adding `BatchCollater` might accidentally expand current LIST-only semantics or mask existing `CollatePolicyError` cases.
- Optional dependency diagnostics could be too broad, catching source/collation scientific errors as dependency errors.
- `TorchDataLoaderPlan` could grow into trainer/device/distributed runtime configuration.
- Fake torch tests could overfit to implementation details and miss the import-boundary contract.
- Parent package export choices could widen the public surface beyond code-backed scoped imports.

## Stop Conditions

- Stop if implementing `rphys.datasources.torch` requires torch to be installed, imported at module import time, or added to runtime dependencies.
- Stop if `TorchSampleSourceDataset` needs to scan directories, build indexes, export fields, own cache/prepared behavior, format model inputs, move devices, or run trainer logic.
- Stop if `TorchIndexSampleDataset` cannot remain a thin convenience over existing `IndexSampleSource`; omit it or ask the manager rather than designing a new source class.
- Stop if `BatchCollater` needs stack, pad, drop, tensor conversion, field renaming, missing-field filling, or model-specific output semantics.
- Stop if the loader plan requires sampler/distributed/device/trainer policy beyond primitive data-loader kwargs.
- Stop if implementation requires changing Phase 1 `SampleSource`, `SampleRequest`, or `IndexSampleSource` contracts.
- Stop if parent `rphys.datasources` exports or root `rphys` exports appear necessary.
- Stop if a new error taxonomy broader than existing dependency, datasource, field/type, and collate errors appears necessary.
- Stop if unrelated local changes appear in Phase 2-owned files or if the branch/worktree is no longer isolated from the control checkout.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/unit/rphys/datasources/test_torch.py
uv run pytest tests/unit/rphys/data/test_collation.py
uv run pytest tests/contracts/test_torch_adapter_contract.py tests/contracts/test_batch_collater_contract.py
uv run pytest tests/integration/test_stage9_torch_collater_flow.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
make test-integration
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

## Acceptance Evidence

- Behavior evidence: `TorchSampleSourceDataset` delegates to `SampleSource` and returns `Sample`; `TorchDataLoaderBuilder` either constructs a torch DataLoader through lazy import/fake torch coverage or fails with typed missing-dependency diagnostics; `BatchCollater` returns `Batch` through `collate_samples`.
- Import-boundary evidence: importing core modules and `rphys.datasources.torch` does not load torch; torch is not a runtime dependency; no core module imports `rphys.datasources.torch`.
- Design-decision evidence: no root exports, no parent datasource optional adapter exports unless manager-approved, no registry, no placeholder class, no model tuple formatting, no device/trainer behavior, no stack/pad/drop expansion, no scanning/index/export/cache/prepared logic.
- Future-roadmap/reuse evidence: adapters wrap any `SampleSource`, so future cache and prepared sources can use the same torch dataset; future trainer/model layers can format batches outside this boundary.
- Documentation evidence: docstrings or docs state optional dependency behavior, direct module import path, FieldLocator preservation, LIST-only collation, typed dependency failures, and explicit unsupported behavior.
- Scientific contract evidence: field locators, schemas, metadata, payload ordering, source request behavior, and collate failure modes remain inspectable and unchanged.

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: start with `BatchCollater`, then optional torch module import shell, then dataset wrappers, then loader plan/builder lazy import behavior, then exports/package tests/docs.
- Tests to run with each slice: collation unit/contract after `BatchCollater`; package import-boundary after adding `rphys.datasources.torch`; datasource torch unit/contract after dataset wrappers; fake/missing torch tests after builder; integration after dataset plus collater work.
- Decisions the executor must not revisit: torch remains optional/import-gated; `SampleSource` remains the adapter boundary; dataset items are `Sample`; collater output is `Batch`; `BatchCollater` delegates to `collate_samples`; LIST-only collation remains unchanged; no root exports; no trainer/device/model formatting; no stack/pad/drop behavior; no cache/prepared/materialization behavior.
- Conditions that require stopping for the manager:
  - A hard torch dependency, real torch test extra, or lockfile dependency appears necessary.
  - A public API beyond the listed adapter/collater names appears necessary.
  - Parent datasource exports seem necessary for optional torch names.
  - `TorchIndexSampleDataset` needs behavior beyond composing `IndexSampleSource`.
  - A real sampler/distributed/device/trainer policy is needed to make `TorchDataLoaderPlan` useful.
  - Collation semantics need to change rather than wrap existing `collate_samples`.
  - Source contracts from Phase 1 need modification.

## Refinement And Review Budget Status

- Expanded-path reason: manager override because Phase 2 introduces public optional torch adapter/collater boundaries and import-policy contracts.
- Phase execution plan refinement: complete; expanded-path self-refinement used for plan-only tightening, not implementation
- Phase implementation refinement: unused
- PR review: complete; managing-agent pre-submit review found no blocking findings and consumed the review budget
- Blocker resolution: 0/3 used
- Refinement focus resolved: optional torch import gating is explicit; missing torch diagnostics are scoped to builder behavior; `BatchCollater` is a thin `collate_samples` wrapper; parent/root export boundaries are explicit; suite obligations include package, unit, contract, integration, e2e, and acceptance; stop conditions prevent trainer/device/model-formatting/cache/prepared scope creep.

## Completion Notes

- Draft plan: complete in `docs/roadmap/stage-9/phases/torch-collater-boundary.md`
- Final phase execution plan: complete after expanded-path self-refinement
- Implementation summary: complete; added module-scoped optional torch adapters in `rphys.datasources.torch`, a framework-neutral `BatchCollater` wrapper over `collate_samples`, code-backed `rphys.data`/`rphys.data.collation` exports for `BatchCollater`, and focused package/unit/contract/integration coverage.
- Implementation validation: `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_collation.py tests/unit/rphys/datasources/test_torch.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_batch_collater_contract.py tests/contracts/test_torch_adapter_contract.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_stage9_torch_collater_flow.py`; `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py`; `UV_CACHE_DIR=/tmp/uv-cache make test-package`; `UV_CACHE_DIR=/tmp/uv-cache make test-unit`; `UV_CACHE_DIR=/tmp/uv-cache make test-contract`; `UV_CACHE_DIR=/tmp/uv-cache make test-integration`; `UV_CACHE_DIR=/tmp/uv-cache make validate-pr`; `UV_CACHE_DIR=/tmp/uv-cache make test-summary`; and `git diff --check` passed. Final summary: package 38, unit 583, contract 108, integration 15, total 744; e2e and acceptance not present.
- Refinement summary: plan refinement complete; no implementation refinement used
- Pre-submit blocker gate: no unresolved implementation, import-boundary, optional-dependency, collater-shape, trainer/device/model-formatting, cache/prepared, or parent/root export blocker identified after implementation
- PR body draft: complete in `docs/roadmap/stage-9/phases/torch-collater-boundary-pr-body.md`
- PR preparation: PR opened and verified as non-draft PR #61 against base `develop` from head `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Automated review: complete; no blocking findings, PR-review budget consumed, and merge eligible assuming PR opens against `develop` and CI matches local validation
- Merge result: merged into `develop` through PR #61 as squash commit `3f26c5eb5b1b0aadd341923c10c9d7d39af41585`
- Cleanup: complete; Phase 2 worktree removed, worktree metadata pruned, and local/remote phase branches deleted
- Remaining blockers: none identified

## Automated Phase PR Review Report

- Review date: 2026-05-15
- Reviewer: managing agent local pre-submit review
- Findings: no blocking findings identified.
- Scope and acceptance: phase scope satisfied; future-phase cache, prepared, materialization, trainer, model-formatting, device, distributed/runtime, stack/pad/drop, and root/parent datasource export work avoided.
- PR body: matches the final committed diff, scientific contract, validation evidence, and deferred work.
- Validation reviewed: `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed with package 38, unit 583, contract 108, integration 15, total 744.
- Import/dependency boundary: `rphys.datasources.torch` uses lazy `importlib.import_module("torch.utils.data")` only in `TorchDataLoaderBuilder.build`; package import-boundary tests prove lightweight imports do not load `torch`.
- Review decision: blocking findings remain no; PR-review budget consumed yes; merge eligible yes, assuming PR opens against `develop` and CI matches local validation.
- Residual risks: real torch execution is covered with fake/missing torch tests until an optional torch extra or CI job exists; `TorchDataLoaderPlan` remains intentionally narrow and data-only.

## PR Submission Metadata

- PR: https://github.com/samcantrill/rphys/pull/61
- Number: 61
- State: open
- Draft: no
- Base: `develop`
- Head: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 2: Torch Adapter And FieldLocator Collater Boundary`
- Initial status checks: no GitHub status checks reported at PR-open verification time.

# Phase Merge Record: Stage 9 Phase 2 Torch Adapter And FieldLocator Collater Boundary

## Merge Facts

- Phase: Phase 2 `torch-collater-boundary`
- Branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- PR: https://github.com/samcantrill/rphys/pull/61
- Base branch: `develop`
- Merge command: `gh pr merge 61 --squash --match-head-commit b0aaec7c60bd6acb557116ee675f1866de401cdb --subject "Stage 9 Phase 2: Torch adapter and batch collater" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `3f26c5eb5b1b0aadd341923c10c9d7d39af41585`
- Branch cleanup: complete; local and remote Phase 2 branches deleted after merge metadata commit
- Worktree cleanup: complete; Phase 2 worktree removed and worktree metadata pruned

## Completion Summary

- Behavior implemented: module-scoped `rphys.datasources.torch` with optional torch dataset/loader adapters and framework-neutral `BatchCollater` in `rphys.data.collation`.
- Tests and validation: `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed with package 38, unit 583, contract 108, integration 15, total 744; no GitHub status checks were configured for PR #61.
- Documentation: phase plan, PR body, implementation-plan PR state, automated review, and merge facts recorded.
- Scientific contract implications: dataset wrappers return FieldLocator-keyed `Sample`; collater returns FieldLocator-keyed `Batch`; torch remains optional/import-gated; no trainer/device/model-formatting/stack/pad/drop behavior was added.
- Follow-up notes for later phases: Phase 3 cache wrappers can wrap `SampleSource` before torch datasets; real torch execution remains fake/missing-tested until an optional torch extra or CI job exists.

## Implementation Plan Update

- Phase status: merged
- Completion summary recorded: yes
- Validation evidence recorded: yes
- Remaining blockers: none
- Metadata commit: `f1976a0` recorded merge metadata; follow-up cleanup metadata recorded after branch/worktree cleanup

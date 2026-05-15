# Roadmap Stage 9 Implementation Plan

Status: approved; Phase 4 merged, ready for Phase 5 execution through implementation workflow
Roadmap version: `v9`
Planning document: `docs/roadmap/stage-9/planning.md`
Workflow: `.codex/workflows/roadmap-version-implementation.md`
Target branch: `develop`
Current phase: none
Blockers: none

## Summary

- Goal: implement the Stage 9 data-loading bridge from `DataSourceIndex` and `SampleBuilder` to framework-neutral `SampleSource`, optional torch iteration, explicit cache/prepared contracts, storage-neutral materialization records, and data-path evidence without taking over datasource discovery, preprocessing, model formatting, trainer/device behavior, or workflow runtime.
- Source functionality-agreement gate: passed 2026-05-15; FQ-1 through FQ-10 repo-resolved and FQ-11 repo-resolved/deferred.
- Approved behavior: `SampleSource.sample_at(position, request=None, context=None)`, `__len__`, and default-request `__getitem__`; FieldLocator-keyed `Sample`/`Batch` preservation; optional/import-gated torch; deterministic local cache semantics; immutable prepared manifest equivalence; data-only batch/materialization/profile records.
- Source behavior confirmation: passed 2026-05-15 with fail-loud request, cache, prepared, optional dependency, metadata, and unsupported streaming/DDP behavior.
- Key design constraints: scoped modules only, no root exports, no placeholders, no hard torch/storage SDK imports, no hidden preprocessing, no pickle or opaque `Sample` cache serialization, no concrete optimized-storage backends, no stable DDP cache coordination.
- Source design-agreement gate: passed 2026-05-15; MP-1 through MP-5 locked.
- Source functionality-agreement queue: FQ-1 through FQ-10 repo-resolved; FQ-11 repo-resolved/deferred.
- Source design-agreement queue: DQ-1/MP-1, DQ-2/MP-2, DQ-5/MP-3, DQ-6/DD-7/MP-4, and DQ-6/DD-8/MP-5 locked by maintainer approval; DQ-3, DQ-4, DQ-7, and DQ-8 recorded recommendations; DQ-9/DD-11 auto-approved with promotion triggers.
- Source future-roadmap/reuse safety review: Stage 8 derived provenance, Stage 10/12 trainer use, Stage 13 prediction-derived fields, Stage 14 synthetic smoke, Stage 15 profiling/backend work, second-backend pressure, and DDP/restartability triggers are recorded and carried into phases.
- Examples covered: synthetic index-to-source flow; derived index through ordinary source path; optional torch dataset; `BatchCollater`; request-specific cache/prepared adversarial source; local cache matrix; prepared manifest equivalence; fake prepared reader; batch cost and sampler records.
- Source phase shaping: six accepted phases: source foundation; torch/collater boundary; cache contracts/local store; prepared manifest/reader/source; materialization/layout/cost and batch-planning records; data-path evidence/docs/package closeout.
- Source plan quality gate: passed 2026-05-15; no blocker, reopened queue, stale specialist evidence, or missing maintainer packet remains.
- Out of scope: concrete LitData/WebDataset/Zarr/Arrow/Parquet/mmap adapters, real cache payload writer/reader contracts, active streaming/resume runtime, stable distributed cache coordination, full read/write backend protocol, distinct `DerivedIndexSampleSource` until code-backed derived provenance validation exists, model formatting, trainer loops, device movement, raw datasource scanning, split/index construction, export/save execution, and generic workflow/artifact runtime.

## Implementation Workflow State

- Implementation-plan quality gate: passed 2026-05-15 / maintainer approved
- Review pass: managing-agent review completed 2026-05-15
- Refinement pass: not needed
- Confirmation review: maintainer approved 2026-05-15
- Automatic merge mode: enabled
- Worktree root: `/home/samcantrill/work/rphys-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `sample-source-foundation` | merged | `agent/stage-9-data-loading-cache-p1-sample-source-foundation` | [#60](https://github.com/samcantrill/rphys/pull/60) | `src/rphys/datasources/sources.py`; source/context tests; scoped docs/docstrings | Add `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and `IndexSampleSource`. | Focused source/context unit, contract, integration, package import, and diff checks. | Synthetic `DataSourceIndex` to lazy/eager `Sample`; derived index via ordinary source path. |
| 2 | `torch-collater-boundary` | merged | `agent/stage-9-data-loading-cache-p2-torch-collater-boundary` | [#61](https://github.com/samcantrill/rphys/pull/61) | `src/rphys/datasources/torch.py`; `src/rphys/data/collation.py`; adapter/collater/package tests | Add optional torch adapters and a FieldLocator-preserving `BatchCollater`. | Package import-boundary, missing/fake torch, collater, adapter, and diff checks. | Optional torch dataset over `SampleSource`; `BatchCollater` over FieldLocator-keyed samples. |
| 3 | `deterministic-cache-store` | merged | `agent/stage-9-data-loading-cache-p3-deterministic-cache-store` | [#62](https://github.com/samcantrill/rphys/pull/62) | `src/rphys/datasources/cache.py`; cache unit/contract/temp-dir tests; cache docs/docstrings | Add deterministic cache records, local atomic store, fake/minimal explicit value strategy, and `CachedSampleSource`. | Cache key/manifest/policy/result, temp-dir atomic store, cached-source, package import, and diff checks. | Local cache hit/miss/stale/corrupt matrix; request-specific cache adversarial source. |
| 4 | `prepared-reader-source` | merged | `agent/stage-9-data-loading-cache-p4-prepared-reader-source` | [#63](https://github.com/samcantrill/rphys/pull/63) | `src/rphys/datasources/prepared.py`; prepared manifest/reader/source tests; provisional docs | Add `PreparedDataManifest`, public provisional `PreparedSampleReader`, `PreparedSampleSource`, and equivalence checks. | Prepared manifest, fake reader, equivalence matrix, package import, and diff checks. | Prepared manifest equivalence success/failure; fake prepared reader/backend boundary. |
| 5 | `materialization-batch-records` | PR open | `agent/stage-9-data-loading-cache-p5-materialization-batch-records` | [#64](https://github.com/samcantrill/rphys/pull/64) | `src/rphys/datasources/prepared.py`; materialization/batch record tests; phase docs | Add storage-neutral materialization, layout, cost, and batch-planning records. | Record validator, package import, contract, docs, and diff checks. | Batch cost metadata and sampler plan; storage-neutral materialization records. |
| 6 | `datapath-evidence-closeout` | pending | `agent/stage-9-data-loading-cache-p6-datapath-evidence-closeout` | pending | data-path evidence records; synthetic integration; public exports/docs/package closeout | Add data-path evidence/profile records and close Stage 9 docs, examples, exports, and focused integration. | Data-path record tests, integration smoke, package/import checks, relevant unit/contract suites, `git diff --check`, and broadened validation as needed. | Synthetic source-to-collater/cache/prepared smoke; data-path profile/benchmark evidence. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| None. Functionality agreement, behavior confirmation, design agreement, validation, phase shaping, plan quality, specialist evidence, maintainer packets, auto-approved decision traceability, and adversarial review evidence are recorded as passed in `planning.md`. | readiness check | Continue with implementation-plan approval, then phase execution through the implementation workflow. | clear |

## Phase 1: SampleSource Foundation And Deterministic Context

Status: merged
Slug: `sample-source-foundation`
Branch: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p1-sample-source-foundation`
PR: [#60](https://github.com/samcantrill/rphys/pull/60)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: establish the common framework-neutral data-loading API before torch, cache, prepared, or batch-planning work depends on it.
- Files/modules owned: `src/rphys/datasources/sources.py`; `src/rphys/datasources/__init__.py` only for code-backed scoped exports if needed; focused source/context tests under unit, contract, integration, and package suites; docstrings or docs that explain public source semantics.
- Behavior implemented: `SampleRequest`; `SampleRuntimeContext`; `WorkerContextFactory`; `SampleSource`; `IndexSampleSource`; per-call `sample_at`; default-request `__getitem__`; request coercion; all-fields default; empty-request rejection; invalid-position and missing-field failures; deterministic context evidence.
- Decisions applied: DD-1, DD-2, DD-3, DD-4, DD-11.
- Future-roadmap/reuse constraints: derived indexes use the ordinary `IndexSampleSource` path; do not add a distinct `DerivedIndexSampleSource` unless code-backed derived provenance validation exists. Keep context as primitive evidence, not workflow state or random execution.
- Examples or demos covered: synthetic `DataSourceIndex` to `IndexSampleSource` to lazy/eager `Sample`; any `DataSourceIndex` can be wrapped without export imports or rescans.
- Out of scope: cache, torch, prepared/materialization records, batch planning, export execution, datasource scanning, split construction, model formatting, device movement, trainer loops, and name-only derived source classes.
- Dependencies: existing `DataSourceIndex`, `DataSourceIndexEntry`, `IndexItem`, `SampleBuilder`, `FieldLocator`, and `Sample` contracts.

### Tasks

- Add source request/context records with primitive metadata and deterministic fingerprint/context derivation.
- Add the public source protocol or small ABC with `__len__`, `sample_at`, and default-request `__getitem__`.
- Implement `IndexSampleSource` by composing `DataSourceIndex` and `SampleBuilder` without mutating descriptors or importing export/cache/torch/prepared modules.
- Add typed failure behavior for empty requests, missing locators, invalid positions, unsupported eager/lazy behavior, and invalid context metadata.
- Add code-backed scoped exports only after behavior and tests exist.
- Document source semantics, FieldLocator preservation, provenance/context evidence, and derived-source deferral.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_sources.py tests/contracts/test_sample_source_contract.py tests/integration/test_stage9_sample_source_flow.py` | Prove source request/context behavior and synthetic index-to-source flow. | yes |
| `make test-package` | Prove scoped exports and base imports stay lightweight. | yes |
| `make test-contract` | Recheck public source contract surface after adding a new shared API. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |

### Acceptance Evidence

- Behavior evidence: source APIs return FieldLocator-keyed `Sample` objects for all-fields and subset requests; eager/lazy behavior follows `SampleBuilder`; failures are typed and fail-loud.
- Design-decision evidence: no root exports, no placeholders, no tuple/model formatting, no export/cache/torch/prepared imports in source foundations.
- Future-roadmap/reuse evidence: ordinary derived indexes remain supported through `IndexSampleSource`; derived public class remains deferred unless provenance validation is code-backed.
- Example/demo evidence: synthetic flow covers lazy/eager source access and default-request indexing.
- Documentation evidence: docstrings or docs explain request semantics, context evidence, unsupported behavior, and derived-source deferral.
- Scientific contract evidence: provenance, request fingerprints, source/index/entry identity, and failure modes are inspectable.

### Phase Workflow State

- Phase execution plan: complete in `docs/roadmap/stage-9/phases/sample-source-foundation.md`
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: standard
- Blocker-resolution budget: standard
- Pre-submit blocker gate: no unresolved source API or derived-source promotion decision
- Merge record: complete; squash merged via PR #60 as `249c128339b268ede6bff2624a46d2aa3c526a14`

### Risks And Stop Conditions

- Risks: public source API lock-in; context records drifting into workflow state; accidental descriptor mutation; placeholder derived class.
- Stop conditions: implementation needs a distinct derived class without code-backed validation; source behavior requires hidden preprocessing/model formatting; root exports or heavy imports become necessary.
- Assumptions: current Stage 4/5 index and sample-builder contracts are available and sufficient.

### Completion Summary

- Implementation: complete; `rphys.datasources.sources` adds `SampleRequest`, `SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and `IndexSampleSource`
- Validation: `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed with package 36, unit 571, contract 103, integration 14, total 724
- PR: https://github.com/samcantrill/rphys/pull/60 merged into `develop`
- Merge: squash merged as `249c128339b268ede6bff2624a46d2aa3c526a14`
- Follow-up: Phase 2 `torch-collater-boundary` may now start from updated `develop`; preserve Phase 1 source/import boundaries

### Phase Merge Record

- Phase: Phase 1 `sample-source-foundation`
- Branch: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- PR: https://github.com/samcantrill/rphys/pull/60
- Base branch: `develop`
- Merge command: `gh pr merge 60 --squash --match-head-commit 2e311597648645eaf1c652a2409ad111f2ec78e6 --subject "Stage 9 Phase 1: SampleSource foundation" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `249c128339b268ede6bff2624a46d2aa3c526a14`
- Branch cleanup: complete; local and remote Phase 1 branches deleted after merge metadata commit
- Worktree cleanup: complete; Phase 1 worktree removed and worktree metadata pruned
- Remaining blockers: none

## Phase 2: Torch Adapter And FieldLocator Collater Boundary

Status: merged
Slug: `torch-collater-boundary`
Branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p2-torch-collater-boundary`
PR: [#61](https://github.com/samcantrill/rphys/pull/61)
Base branch: `develop`
Target branch: `develop`
Workflow path: fast path

### Scope

- Goal: provide framework-compatible iteration over `SampleSource` while preserving core import boundaries and FieldLocator-keyed collation.
- Files/modules owned: `src/rphys/datasources/torch.py`; `src/rphys/data/collation.py` or a tiny approved collater wrapper; focused adapter/collater/package tests; docs/docstrings for optional dependency behavior.
- Behavior implemented: `TorchSampleSourceDataset`; optional `TorchIndexSampleDataset` if fully code-backed by Phase 1; `TorchDataLoaderPlan`; `TorchDataLoaderBuilder`; `BatchCollater` delegating to `collate_samples`; typed missing-dependency diagnostics where torch behavior is required.
- Decisions applied: DD-1, DD-2, DD-5, DD-9, DD-11.
- Future-roadmap/reuse constraints: Stage 10/12 trainers consume this path later, but Stage 9 does not own trainer loops, device movement, model tuple formatting, or padding/stack policies.
- Examples or demos covered: optional torch dataset over `SampleSource`; `BatchCollater` over FieldLocator-keyed samples.
- Out of scope: hard torch dependency, datasource scanning/index building/export, model tuple formatting, device movement, trainer loops, custom tensor stacking/padding/dropping, and generic framework registries.
- Dependencies: Phase 1 source contracts and existing `collate_samples` behavior.

### Tasks

- Add the torch adapter module with lazy/import-gated torch behavior and typed diagnostics.
- Add dataset wrappers that delegate item access to `SampleSource` and never scan/build/export/format.
- Add data-only loader plan/builder records with no trainer/device ownership.
- Add `BatchCollater` as a thin callable over existing collation.
- Extend package import-boundary tests to prove core modules do not import torch.
- Document optional dependency behavior and collation boundaries.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_torch.py tests/unit/rphys/data/test_collation.py` | Validate adapter delegation, missing/fake torch behavior, and collater preservation of existing collation. | yes |
| `make test-package` | Ensure torch remains optional and package exports are code-backed. | yes |
| `make test-unit` | Recheck touched unit surfaces, especially collation. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |

### Acceptance Evidence

- Behavior evidence: adapter delegates to `SampleSource`; collater returns existing `Batch` shape with FieldLocator keys.
- Design-decision evidence: torch imports are lazy/import-gated; no model tuples, device moves, scanner, builder, or export behavior appears in adapters.
- Future-roadmap/reuse evidence: any future framework can wrap `SampleSource` without changing core source contracts.
- Example/demo evidence: fake/missing torch path and FieldLocator collation example are tested.
- Documentation evidence: docs or docstrings state optional dependency and unsupported formatting/padding/device behavior.
- Scientific contract evidence: collation does not hide field policy changes or change scientific meaning.

### Phase Workflow State

- Phase execution plan: complete in `docs/roadmap/stage-9/phases/torch-collater-boundary.md`
- Planning/refinement budget: standard
- Implementation/refinement budget: standard
- PR review budget: consumed by managing-agent pre-submit review; no blocking findings
- Blocker-resolution budget: standard
- Pre-submit blocker gate: no hard torch dependency or collation semantic expansion
- Merge record: complete; squash merged via PR #61 as `3f26c5eb5b1b0aadd341923c10c9d7d39af41585`

### Risks And Stop Conditions

- Risks: dependency leakage; accidental tuple/model formatting; duplicated collation behavior.
- Stop conditions: torch must become a base dependency; adapter needs trainer/device behavior; collater requires stack/pad/drop semantics beyond existing policy.
- Assumptions: fake or monkeypatched torch coverage is enough unless the project adds a real optional torch test extra.

### Completion Summary

- Implementation: complete; `rphys.datasources.torch` adds optional torch dataset/loader adapters and `rphys.data.collation` adds `BatchCollater`
- Validation: `UV_CACHE_DIR=/tmp/uv-cache make validate-pr` and `UV_CACHE_DIR=/tmp/uv-cache make test-summary` passed with package 38, unit 583, contract 108, integration 15, total 744
- PR: https://github.com/samcantrill/rphys/pull/61 merged into `develop`
- Merge: squash merged as `3f26c5eb5b1b0aadd341923c10c9d7d39af41585`
- Follow-up: Phase 3 `deterministic-cache-store` may now start from updated `develop`; preserve Phase 1 source and Phase 2 optional torch/collater boundaries

### Phase Merge Record

- Phase: Phase 2 `torch-collater-boundary`
- Branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- PR: https://github.com/samcantrill/rphys/pull/61
- Base branch: `develop`
- Merge command: `gh pr merge 61 --squash --match-head-commit b0aaec7c60bd6acb557116ee675f1866de401cdb --subject "Stage 9 Phase 2: Torch adapter and batch collater" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `3f26c5eb5b1b0aadd341923c10c9d7d39af41585`
- Branch cleanup: complete; local and remote Phase 2 branches deleted after merge metadata commit
- Worktree cleanup: complete; Phase 2 worktree removed and worktree metadata pruned
- Remaining blockers: none

## Phase 3: Deterministic Cache Contracts And Local Atomic Store

Status: merged
Slug: `deterministic-cache-store`
Branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p3-deterministic-cache-store`
PR: [#62](https://github.com/samcantrill/rphys/pull/62)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: lock deterministic cache equivalence, manifest, policy, result, and local atomic store semantics without unsafe payload serialization.
- Files/modules owned: `src/rphys/datasources/cache.py`; focused cache unit/contract/temp-dir tests; docs/docstrings for cache policy, no-pickle behavior, and real-payload deferral.
- Behavior implemented: `CacheKey`; `CachePolicy`; `CacheContext`; `CacheEntry`; `CacheManifest`; lookup/write result records; `CacheStore`; `LocalCacheStore`; `CachedSampleSource`; fake/minimal explicit value strategy.
- Decisions applied: DD-3, DD-6, DD-10, DD-11.
- Future-roadmap/reuse constraints: local deterministic semantics become the baseline for later Stage 15 profiling, remote stores, and DDP coordination. Stable distributed behavior and real payload writers stay deferred.
- Examples or demos covered: local cache hit/miss/stale/corrupt matrix; request-specific cache adversarial source.
- Out of scope: pickle-by-default, opaque `Sample` serialization, real generic payload persistence, remote stores, eviction sophistication, concrete prepared/optimized backends, and stable DDP coordination.
- Dependencies: Phase 1 source/request/context contracts; Phase 2 only for optional examples, not core behavior.

### Tasks

- Add deterministic key construction sensitive to request, context, index entry, field/resource/codec/software evidence, invalidation inputs, and optional operation fingerprints.
- Add manifest and entry records with schema version, key, states, field locators, invalidation evidence, checksums, and write status.
- Add narrow cache store protocol and local store implementation with temp-write then atomic commit/rename behavior.
- Add cached-source wrapper that treats mismatches as typed misses/failures and returns hits only through explicit compatible value strategy.
- Explicitly reject pickle/default opaque `Sample` serialization in implementation and docs.
- Record revisit trigger for the first real cache payload writer/reader contract.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_cache.py tests/contracts/test_cache_contract.py` | Validate keys, manifests, policies, result records, stale/corrupt rejection, and cached-source behavior. | yes |
| `uv run pytest tests/integration` focused to any Stage 9 cache temp-dir tests | Validate local atomic store behavior with real filesystem paths. | yes |
| `make test-package` | Ensure cache module does not import torch, trainer, or storage SDKs. | yes |
| `make test-contract` | Recheck public cache contracts. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |

### Acceptance Evidence

- Behavior evidence: deterministic key sensitivity matrix; stale/mismatched/corrupt/incomplete entries are rejected; explicit hit/miss/failure evidence is available.
- Design-decision evidence: no pickle, no opaque `Sample` serialization, no hidden fallback on mismatch, and atomic local commit semantics are tested.
- Future-roadmap/reuse evidence: remote/distributed stores can reuse the narrow store protocol later; DDP remains explicitly deferred.
- Example/demo evidence: temp-dir cache matrix and adversarial request mismatch tests.
- Documentation evidence: cache docs state fake/minimal value strategy and real payload writer revisit trigger.
- Scientific contract evidence: invalidation inputs and operation/request/source evidence are inspectable.

### Phase Workflow State

- Phase execution plan: complete in `docs/roadmap/stage-9/phases/deterministic-cache-store.md`
- Planning/refinement budget: expanded
- Implementation/refinement budget: expanded
- PR review budget: consumed by managing-agent pre-submit review; no blocking findings
- Blocker-resolution budget: expanded
- Pre-submit blocker gate: no unsafe payload serialization or stable distributed claims
- Merge record: complete; squash merged via PR #62 as `424fc8a915105b6717ada70769d751d1675bea84`

### Risks And Stop Conditions

- Risks: silent stale reuse; overbroad store protocol; accidental pickle/object serialization; temp-write semantics not truly atomic enough for local guarantees.
- Stop conditions: same-shape cache hits require real payload persistence before an explicit writer/reader contract is designed; remote/DDP behavior becomes necessary; implementation cannot prove invalidation inputs.
- Assumptions: first cache phase can use fake/minimal explicit values while locking key/manifest/store correctness.

### Completion Summary

- Implementation: complete; `rphys.datasources.cache` adds deterministic cache records, local atomic JSON manifest store behavior, and `CachedSampleSource` with explicit hit loader/entry factory strategies
- Validation: `make validate-pr` and `make test-summary` passed with package 39, unit 595, contract 111, integration 16, total 761
- PR: https://github.com/samcantrill/rphys/pull/62 merged into `develop`
- Merge: squash merged as `424fc8a915105b6717ada70769d751d1675bea84`
- Follow-up: Phase 4 `prepared-reader-source` may now start from updated `develop`; preserve Phase 1 source, Phase 2 torch/collater, and Phase 3 no-pickle cache boundaries

### Phase Merge Record

- Phase: Phase 3 `deterministic-cache-store`
- Branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- PR: https://github.com/samcantrill/rphys/pull/62
- Base branch: `develop`
- Merge command: `gh pr merge 62 --squash --match-head-commit cdc7218b1881903a2c68ffa1017ae375fdf92a66 --subject "Stage 9 Phase 3: Deterministic cache store" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `424fc8a915105b6717ada70769d751d1675bea84`
- Branch cleanup: complete; local and remote Phase 3 branches deleted after merge
- Worktree cleanup: complete; Phase 3 worktree removed and worktree metadata pruned
- Remaining blockers: none

## Phase 4: Prepared Manifest, Public Provisional Reader, And Prepared Source

Status: merged
Slug: `prepared-reader-source`
Branch: `agent/stage-9-data-loading-cache-p4-prepared-reader-source`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p4-prepared-reader-source`
PR: [#63](https://github.com/samcantrill/rphys/pull/63)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add immutable prepared-data equivalence and the approved minimal public provisional reader boundary.
- Files/modules owned: `src/rphys/datasources/prepared.py`; focused prepared manifest/reader/source tests; docs/docstrings for provisional reader, immutable products, and equivalence semantics.
- Behavior implemented: `PreparedDataManifest`; public provisional `PreparedSampleReader`; `PreparedSampleSource`; manifest compatibility checks; request/source/operation/invalidation equivalence; fake reader support.
- Decisions applied: DD-7, DD-8, DD-11.
- Future-roadmap/reuse constraints: enable later optimized storage, Stage 13 prediction-derived prepared inputs, and Stage 15 backend evaluation without concrete SDK adapters or full read/write backend protocols.
- Examples or demos covered: prepared manifest equivalence success/failure; fake prepared reader/backend boundary; request-specific prepared adversarial source.
- Out of scope: full read/write backend protocol, materialization worker execution, concrete SDK adapters, backend-owned source identity/splits/operation semantics, generic artifact runtime, and hidden preprocessing in `__getitem__`.
- Dependencies: Phase 1 request/source/context contracts and Phase 3 invalidation/cache concepts; does not require a real cache payload writer.

### Tasks

- Add versioned primitive prepared manifest records for approved source/index identity, request and operation fingerprints, field schemas/dtypes, counts, splits/groups, checksums, offsets/chunks/shards, cost/layout metadata, runtime assumptions, and invalidation inputs.
- Add public provisional `PreparedSampleReader` with manifest compatibility validation, one-position/request reads to FieldLocator-keyed `Sample`, and backend identity evidence.
- Add `PreparedSampleSource` that refuses unproven equivalence and never mutates prepared products.
- Add fake reader tests that prove no backend-defined scientific semantics leak into rphys contracts.
- Document provisional status, same-shape behavior, no hidden preprocessing, and second-backend/full-protocol revisit triggers.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_prepared.py tests/contracts/test_prepared_sample_reader_contract.py` | Validate manifest fields, equivalence matrix, fake reader, and prepared source behavior. | yes |
| `make test-package` | Ensure prepared imports stay lightweight and SDK-free. | yes |
| `make test-contract` | Recheck public prepared/source contracts. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |

### Acceptance Evidence

- Behavior evidence: compatible prepared reads return FieldLocator-keyed samples; mismatched request/source/operation/invalidation evidence fails loudly.
- Design-decision evidence: reader is public provisional and minimal; no concrete SDK, full backend protocol, generic artifact runtime, or hidden preprocessing appears.
- Future-roadmap/reuse evidence: second backend can implement the reader without changing `PreparedSampleSource`; stable promotion waits for backend evidence.
- Example/demo evidence: fake reader and equivalence success/failure tests.
- Documentation evidence: public provisional label and revisit triggers are explicit.
- Scientific contract evidence: source/index identity, operation fingerprints, field schemas, checksums, offsets, runtime assumptions, and invalidation inputs are inspectable.

### Phase Workflow State

- Phase execution plan: complete in `docs/roadmap/stage-9/phases/prepared-reader-source.md`
- Planning/refinement budget: expanded
- Implementation/refinement budget: expanded
- PR review budget: consumed by managing-agent pre-submit review; no blocking findings
- Blocker-resolution budget: expanded
- Pre-submit blocker gate: no backend-defined domain semantics or hidden preprocessing
- Merge record: complete; squash merged via PR #63 as `8469fa5dff5ff21ed5c728d5f8ab0f536c8eac89`

### Risks And Stop Conditions

- Risks: manifest schema breadth; freezing reader behavior too early; equivalence gaps.
- Stop conditions: implementation requires a concrete backend dependency; a full read/write backend protocol is needed; prepared source must execute operations in `__getitem__`.
- Assumptions: fake reader tests are sufficient for the first public provisional reader boundary.

### Completion Summary

- Implementation: complete; `rphys.datasources.prepared` adds prepared field/manifest/read records, public provisional `PreparedSampleReader`, and `PreparedSampleSource`
- Validation: `make validate-pr` and `make test-summary` passed with package 40, unit 604, contract 114, integration 17, total 775
- PR: https://github.com/samcantrill/rphys/pull/63 merged into `develop`
- Merge: squash merged as `8469fa5dff5ff21ed5c728d5f8ab0f536c8eac89`
- Follow-up: Phase 5 `materialization-batch-records` may now start from updated `develop`; preserve the public provisional reader boundary and avoid concrete backend execution

### Phase Merge Record

- Phase: Phase 4 `prepared-reader-source`
- Branch: `agent/stage-9-data-loading-cache-p4-prepared-reader-source`
- PR: https://github.com/samcantrill/rphys/pull/63
- Base branch: `develop`
- Merge command: `gh pr merge 63 --squash --match-head-commit 31e2d08ac2c33a94438b01d8166be466e17f9148 --subject "Stage 9 Phase 4: Prepared reader source" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `8469fa5dff5ff21ed5c728d5f8ab0f536c8eac89`
- Branch cleanup: complete; local and remote Phase 4 branches deleted after merge
- Worktree cleanup: complete; Phase 4 worktree removed and worktree metadata pruned
- Remaining blockers: none

## Phase 5: Storage-Neutral Materialization, Layout, Cost, And Batch-Planning Records

Status: PR open
Slug: `materialization-batch-records`
Branch: `agent/stage-9-data-loading-cache-p5-materialization-batch-records`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p5-materialization-batch-records`
PR: [#64](https://github.com/samcantrill/rphys/pull/64)
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add descriptive records for materialized/prepared storage layout and cost-aware batching without implementing concrete backends, trainers, or samplers.
- Files/modules owned: `src/rphys/datasources/prepared.py` or a code-backed sibling module if implementation evidence shows the record set should be split; focused materialization, layout, cost, and batch-planning tests; docs/docstrings for backend neutrality and descriptive-only batching.
- Behavior implemented: `OptimizedStorageFormat`; `OptimizedDataPlan`; `MaterializationPlan`; `MaterializationManifest`; `ShardManifest`; `ChunkMetadata`; `AccessPatternPlan`; `RecordLayoutMetadata`; `BatchCostMetadata`; `BatchSamplerPlan`; `BatchShapePolicy`.
- Decisions applied: DD-7, DD-8, DD-9, DD-10, DD-11.
- Future-roadmap/reuse constraints: records must serve future Stage 12 batching, Stage 14 synthetic smoke, and Stage 15 backend/profile work while keeping concrete adapters and execution planners deferred.
- Examples or demos covered: storage-neutral materialization records; batch cost metadata and sampler plan.
- Out of scope: concrete LitData/WebDataset/Zarr/Arrow/Parquet/mmap adapters, materialization worker execution, trainer samplers, device movement, benchmark thresholds, active streaming/resume.
- Dependencies: Phase 4 prepared manifest identity and reader boundary; Phase 1 FieldLocator/request concepts.

### Tasks

- Add backend-neutral materialization and layout records with validation for backend identity, shards/chunks, offsets/lengths, checksums, compression metadata, access patterns, counts/splits/groups, runtime assumptions, and invalidation inputs.
- Add data-only batch cost and sampler/shape policy records for fixed, cost-aware, dynamic, packing/padding, drop/remainder, and ordering decisions.
- Keep records descriptive: no trainer/device/profiler/backend execution behavior.
- Add public stability/provisional notes and deferrals for concrete backends, full backend protocols, and active execution.
- Split materialization and batch-planning into separate PRs only if implementation size becomes a reviewability risk; record the split as a phase refinement, not a reopened design queue.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_materialization.py tests/contracts/test_materialization_contract.py` | Validate materialization/layout/access records and backend-neutral metadata. | yes |
| `uv run pytest tests/unit/rphys/datasources/test_batch_planning.py` | Validate batch sampler/shape/cost records and descriptive-only behavior. | yes |
| `make test-package` | Ensure no concrete backend/trainer/device imports. | yes |
| `make test-unit` | Recheck touched unit surfaces. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |

### Acceptance Evidence

- Behavior evidence: invalid metadata fails loudly; valid records preserve backend identity, shard/chunk, cost/layout, access-pattern, and policy evidence.
- Design-decision evidence: no concrete SDKs, no active materialization workers, no trainer samplers, no device movement, no benchmark thresholds.
- Future-roadmap/reuse evidence: records are reusable by future backend evaluation and trainer planning without coupling to internals.
- Example/demo evidence: batch plan and materialization record examples are covered by tests.
- Documentation evidence: docs state backend-neutrality, provisional schema pieces, and deferred adapters/execution.
- Scientific contract evidence: checksums, offsets, field schemas, counts/splits/groups, runtime assumptions, and invalidation inputs remain explicit.

### Phase Workflow State

- Phase execution plan: complete
- Planning/refinement budget: expanded
- Implementation/refinement budget: complete
- PR review budget: complete; managing-agent local pre-submit review found no blocking findings
- Blocker-resolution budget: expanded
- Pre-submit blocker gate: no trainer/backend execution behavior or concrete dependencies
- Merge record: pending

### Risks And Stop Conditions

- Risks: record set becomes too broad; premature stable schema; hidden backend/trainer behavior enters validators.
- Stop conditions: a concrete backend adapter is required; batch planning needs active sampler execution; schema choices require new maintainer judgment beyond approved records.
- Assumptions: descriptive record validation can be implemented without choosing a storage format or trainer runtime.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 6: Data-Path Evidence, Integration, Docs, And Package Closeout

Status: pending
Slug: `datapath-evidence-closeout`
Branch: `agent/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: close Stage 9 with inspectable data-path evidence records, synthetic integration, docs, scoped exports, and package/import validation.
- Files/modules owned: data-path evidence records in the Stage 9 owning module chosen during phases 4-5; synthetic integration tests; package/import tests; docs/docstrings for Stage 9 public surfaces and deferrals.
- Behavior implemented: `StreamingReadPlan`; `DataLoaderState`; `DataPathProfile`; `DataPathBenchmark`; synthetic source-to-collater/cache/prepared integration; final code-backed package exports.
- Decisions applied: DD-1, DD-5, DD-9, DD-10, DD-11 plus all prior locked source/cache/prepared decisions.
- Future-roadmap/reuse constraints: records support Stage 15 profiling/restartability and later trainers without implementing active resume, stable distributed cache coordination, system profilers, or trainer event schemas.
- Examples or demos covered: synthetic source-to-collater/cache/prepared smoke; data-path profile/benchmark evidence.
- Out of scope: active resumable loader runtime, stable distributed cache coordination, system profiler, trainer event schema, model formatting, concrete backend benchmarks, and performance thresholds.
- Dependencies: Phases 1 through 5.

### Tasks

- Add descriptive data-path evidence/profile/benchmark records for skipped/resumed/cached/re-read/materialization/batch summaries.
- Add explicit unstable/deferred labels for DDP and active streaming behavior.
- Add focused integration that demonstrates source-to-batch and cache/prepared equivalence boundaries without raw datasets.
- Finalize docs/docstrings for public surfaces, stability labels, unsupported behavior, and revisit triggers.
- Ensure package exports are code-backed and root `rphys` remains empty.
- Run focused and broadened validation appropriate to the cumulative public surface.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `uv run pytest tests/unit/rphys/datasources/test_data_path_records.py tests/integration/test_stage9_data_path_flow.py` | Validate evidence records and synthetic Stage 9 flow. | yes |
| `make test-package` | Prove final exports and import boundaries. | yes |
| `make test-unit` | Recheck Stage 9 unit surfaces. | yes |
| `make test-contract` | Recheck public contracts introduced across the stage. | yes |
| `git diff --check` | Catch whitespace/markdown issues before PR. | yes |
| `make validate-pr` | Broaden validation before the final Stage 9 PR if cumulative public-surface changes are broad or phase-local checks leave residual risk. | conditional |

### Acceptance Evidence

- Behavior evidence: data-path records are descriptive and primitive; synthetic flow demonstrates source-to-batch plus cache/prepared boundaries.
- Design-decision evidence: no active resume, DDP coordination, trainer profiler, model formatter, or concrete backend benchmark behavior appears.
- Future-roadmap/reuse evidence: Stage 15 and future trainers can consume evidence records without coupling to loader internals.
- Example/demo evidence: synthetic integration covers the accepted Stage 9 examples that are code-backed by this point.
- Documentation evidence: public API docs/docstrings record FieldLocator preservation, request/equivalence semantics, optional dependency behavior, cache/prepared invalidation, and deferrals.
- Scientific contract evidence: provenance, invalidation, prepared equivalence, cache state, materialization layout, and batch-cost evidence remain inspectable.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: expanded
- Implementation/refinement budget: expanded
- PR review budget: expanded
- Blocker-resolution budget: expanded
- Pre-submit blocker gate: no active runtime/profiler/trainer behavior slipped in; public exports are code-backed
- Merge record: pending

### Risks And Stop Conditions

- Risks: overlap with Stage 15; hidden resume semantics; public exports not backed by behavior; integration accidentally depends on raw datasets or optional heavy deps.
- Stop conditions: evidence records need benchmark thresholds, profiler integrations, stable DDP semantics, or trainer event schemas; implementation requires modifying roadmap scope.
- Assumptions: synthetic fixtures remain sufficient for a license-safe integration path.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: run focused phase tests first; before the final Stage 9 closeout, run `make test-package`, `make test-unit`, `make test-contract`, `git diff --check`, and `make validate-pr` if cumulative public-surface or import-boundary risk remains.
- Docs/template checks: each phase that adds public behavior must update docstrings or docs in the same PR; final closeout verifies no docs-only PR is needed between phase PRs.
- Scientific/workflow contract checks: preserve FieldLocator keys, request fingerprints, provenance/context evidence, explicit invalidation inputs, no hidden preprocessing, no trainer/device/workflow runtime behavior, no raw datasets, no unsafe serialization, and fail-loud behavior for unproven equivalence.
- Example/demo checks: keep examples synthetic or fake-backed; do not rely on concrete optimized-storage SDKs, torch as a base dependency, or Stage 8 derived provenance until code-backed.
- Manual review focus: verify ownership boundaries, optional import gating, public/provisional labels, deferral triggers, and no placeholder exports after each phase.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Readiness gates and required specialist evidence are passed in `planning.md`. | note | Implementation plan may define phases. | recorded |
| Six-phase shape is broad but accepted and reviewable. | concern | Keep Phase 5 splittable only for implementation-size reviewability; do not reopen design unless new behavior or schema decisions are required. | recorded |
| Deferrals are implementation stop conditions, not hidden TODOs. | concern | Carry real cache payload writers, concrete backends, active streaming/resume, stable DDP, full read/write backend protocols, and distinct derived-source validation as explicit revisit triggers. | recorded |

Gate result:

- Status: approved for implementation
- Review evidence: this plan follows the passed validation/phase-shaping gate, uses the accepted six phases, and records ownership, behavior, validation, risks, assumptions, and stop conditions per phase.
- Accepted risks: Stage 9 intentionally underdelivers real cache payload persistence and concrete optimized-storage backends to avoid unsafe serialization and premature backend lock-in.
- Revisit triggers: Stage 8 derived assembly lands; Stage 13 prediction-derived prepared inputs need stable interchange; first real cache payload writer is needed; second optimized-storage backend appears; rank-safe DDP cache tests are planned; implementation needs public helper/protocol promotion; `docs/roadmap.md` changes materially before phase execution.

## Final Approval

- Approval status: maintainer approved 2026-05-15
- Approved scope: six-phase Stage 9 implementation plan covering source foundation, torch/collater boundary, deterministic cache store, prepared reader/source, materialization/batch records, and data-path evidence closeout.
- Accepted risks: Stage 9 intentionally defers real cache payload writers, concrete optimized-storage adapters, active streaming/resume runtime, stable DDP cache coordination, full read/write backend protocols, and distinct `DerivedIndexSampleSource` until code-backed provenance validation exists.
- Deferred items: real cache payload writers; concrete optimized-storage adapters; active streaming/resume runtime; stable DDP cache coordination; full read/write backend protocols; distinct `DerivedIndexSampleSource` until code-backed provenance validation exists; model formatting; trainer/device behavior.

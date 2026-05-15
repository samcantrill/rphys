# Phase 3 Execution Plan: Deterministic Cache Contracts And Local Atomic Store

## Metadata

- Status: final phase execution plan; ready for implementation
- Roadmap stage: `v9`
- Feature focus: deterministic cache keys, manifest records, local atomic store, and explicit cached-source value strategy
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: Deterministic Cache Contracts And Local Atomic Store
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 3: Deterministic Cache Contracts And Local Atomic Store`
- Branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Phase execution plan path: `docs/roadmap/stage-9/phases/deterministic-cache-store.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path
- Blockers: none for implementation planning

## Objective

Add deterministic, inspectable cache contracts without unsafe payload
serialization. Phase 3 locks request/context/invalidation key semantics,
manifest validation, local temp-write then atomic replace behavior, and a
`CachedSampleSource` wrapper that only returns cache hits through an explicit
caller-provided value loader.

## Scope

In scope:

- `src/rphys/datasources/cache.py` with code-backed public names:
  - `CacheKey`
  - `CachePolicy`
  - `CacheContext`
  - `CacheEntry`
  - `CacheManifest`
  - `CacheLookupResult`
  - `CacheWriteResult`
  - `CacheStore`
  - `LocalCacheStore`
  - `CachedSampleSource`
- Deterministic SHA-256 fingerprints from primitive JSON payloads only.
- JSON manifest serialization with checksums and corruption/incomplete-state rejection.
- Local filesystem store that writes a temporary file in the cache root and commits with `Path.replace`.
- Cached source wrapper over any Phase 1 `SampleSource`.
- Fake/minimal explicit value strategy: hits are returned only when the caller supplies a compatible `hit_loader(CacheEntry) -> Sample`.

Out of scope:

- Pickle or opaque `Sample` serialization.
- Real generic payload writer/reader contracts.
- Remote stores, eviction, distributed/DDP coordination, prepared-data behavior, storage SDK adapters, trainer/model/device behavior, and workflow runtime.
- Parent/root exports.

## Public Contract

- `CacheKey.for_sample(request, context, cache_context=None)` accepts Phase 1
  `SampleRequest` and `SampleRuntimeContext` records and returns a stable key.
- `CacheContext` holds optional primitive operation, invalidation, and metadata evidence.
- `CacheEntry` records key, status, field locators, value strategy/token, invalidation evidence, metadata, and checksum.
- `CacheManifest` is a versioned JSON envelope for one or more entries.
- `LocalCacheStore.lookup(key)` returns typed hit/miss/corrupt/incomplete result records instead of raising for ordinary stale/corrupt cache state.
- `LocalCacheStore.write(entry)` validates and atomically commits a manifest file.
- `CachedSampleSource.sample_at(...)` builds request/context/key evidence, checks the store when policy allows reads, returns a hit only through the explicit `hit_loader`, otherwise delegates to the wrapped source and optionally writes an entry through an explicit `entry_factory`.

## Tests

- Package: cache module `__all__`, parent/root non-exports, lightweight import boundary.
- Unit: key sensitivity, primitive validation, manifest checksum/corruption, local store hit/miss/incomplete/corrupt, cached-source hit/miss/write behavior.
- Contract: public cache key/manifest/store/cached-source semantics.
- Integration: temp-dir local cache matrix over a synthetic source.
- Deferred: e2e and acceptance real-payload/remote/DDP checks.

## Validation Commands

```sh
uv run pytest tests/unit/rphys/datasources/test_cache.py
uv run pytest tests/contracts/test_cache_contract.py
uv run pytest tests/integration/test_stage9_cache_flow.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
make test-integration
git diff --check
```

Final PR gate:

```sh
make validate-pr
make test-summary
git diff --check
```

## Stop Conditions

- Stop if a same-shape cache hit requires pickle, opaque `Sample` serialization, or real payload persistence before a writer/reader contract exists.
- Stop if remote, DDP, eviction, prepared-data, trainer/device, or model-formatting semantics become necessary.
- Stop if cache behavior requires changing Phase 1 `SampleSource`, `SampleRequest`, or `SampleRuntimeContext`.
- Stop if parent/root exports or heavy optional imports appear necessary.

## Completion Notes

- Draft plan: complete
- Final phase execution plan: complete
- Implementation summary: complete; added module-scoped `rphys.datasources.cache` records and wrappers for deterministic cache contexts, keys, entries, manifests, lookup/write results, a local atomic JSON manifest store, and `CachedSampleSource` with explicit hit loader and entry factory strategies.
- Implementation validation: `uv run pytest tests/unit/rphys/datasources/test_cache.py tests/contracts/test_cache_contract.py tests/integration/test_stage9_cache_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py`; `make test-package`; `make test-contract`; `make test-integration`; `make validate-pr`; and `make test-summary` passed. Final summary: package 39, unit 595, contract 111, integration 16, total 761; e2e and acceptance not present.
- Pre-submit blocker gate: no unresolved plan-level blocker identified
- PR body draft: complete in `docs/roadmap/stage-9/phases/deterministic-cache-store-pr-body.md`
- PR preparation: PR opened and verified as non-draft PR #62 against base `develop` from head `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Automated review: complete; managing-agent local pre-submit review found no blocking findings
- Merge result: merged into `develop` through PR #62 as squash commit `424fc8a915105b6717ada70769d751d1675bea84`
- Cleanup: complete; Phase 3 worktree removed, worktree metadata pruned, and local/remote phase branches deleted
- Remaining blockers: none identified for implementation

## Automated Phase PR Review Report

- Review date: 2026-05-15
- Reviewer: managing agent local pre-submit review
- Findings: no blocking findings identified.
- Scope and acceptance: phase scope satisfied; future-phase prepared data, materialization, remote stores, eviction, DDP coordination, payload persistence, trainer, model-formatting, device, and parent/root export work avoided.
- PR body: matches the staged diff, scientific contract, validation evidence, and deferred work.
- Validation reviewed: `make validate-pr` and `make test-summary` passed with package 39, unit 595, contract 111, integration 16, total 761.
- Cache correctness boundary: cache keys validate request/context fingerprint coherence; context-free cached-source access skips cache writes; hits require an explicit `hit_loader`; local writes use temp-write then `Path.replace`.
- Review decision: blocking findings remain no; merge eligible yes, assuming PR opens against `develop` and CI matches local validation.
- Residual risks: real payload persistence and optimized storage remain deferred until explicit writer/reader and prepared-data contracts exist; distributed cache behavior remains future work.

## PR Submission Metadata

- PR: https://github.com/samcantrill/rphys/pull/62
- Number: 62
- State: open
- Draft: no
- Base: `develop`
- Head: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 3: Deterministic Cache Contracts And Local Atomic Store`
- Initial status checks: no GitHub status checks reported at PR-open verification time.

# Phase Merge Record: Stage 9 Phase 3 Deterministic Cache Contracts And Local Atomic Store

## Merge Facts

- Phase: Phase 3 `deterministic-cache-store`
- Branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- PR: https://github.com/samcantrill/rphys/pull/62
- Base branch: `develop`
- Merge command: `gh pr merge 62 --squash --match-head-commit cdc7218b1881903a2c68ffa1017ae375fdf92a66 --subject "Stage 9 Phase 3: Deterministic cache store" --body "..."`
- Merge result: merged 2026-05-15
- Merge commit: `424fc8a915105b6717ada70769d751d1675bea84`
- Branch cleanup: complete; local and remote Phase 3 branches deleted after merge
- Worktree cleanup: complete; Phase 3 worktree removed and worktree metadata pruned

## Completion Summary

- Behavior implemented: module-scoped `rphys.datasources.cache` with deterministic cache contexts, keys, entries, manifests, lookup/write result records, local atomic JSON manifest store behavior, and `CachedSampleSource`.
- Tests and validation: `make validate-pr` and `make test-summary` passed with package 39, unit 595, contract 111, integration 16, total 761; no GitHub status checks were configured for PR #62.
- Documentation: phase plan, PR body, automated review, implementation-plan PR state, and merge facts recorded.
- Scientific contract implications: cache equivalence is request/context/invalidation fingerprint based; context-free cached-source access skips cache writes; hits require explicit caller value loading; no pickle, opaque `Sample` serialization, remote store, prepared-data, trainer/device/model-formatting, or DDP coordination behavior was added.
- Follow-up notes for later phases: Phase 4 prepared data can reuse the invalidation/cache evidence vocabulary while preserving the no-generic-payload-writer boundary.

## Implementation Plan Update

- Phase status: merged
- Completion summary recorded: yes
- Validation evidence recorded: yes
- Remaining blockers: none
- Metadata commit: this direct `develop` metadata commit records merge and cleanup facts

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
- Implementation summary: pending
- Implementation validation: pending
- Pre-submit blocker gate: no unresolved plan-level blocker identified
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none identified for implementation

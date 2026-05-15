# Summary

Implements Stage 9 Phase 3: deterministic cache contracts and a local
atomic manifest store. This adds `rphys.datasources.cache` with
`CacheContext`, `CacheKey`, `CacheEntry`, `CacheManifest`,
`CacheLookupResult`, `CacheWriteResult`, `CachePolicy`, `CacheStore`,
`LocalCacheStore`, and `CachedSampleSource`.

The cache is metadata-first and intentionally provisional. Keys are built from
primitive request/runtime/cache evidence, manifests are versioned JSON records
with checksums, and the local store writes a temporary manifest in the cache
root before committing with `Path.replace`. `CachedSampleSource` never pickles
or serializes `Sample` objects. Cache hits are returned only when the caller
supplies an explicit `hit_loader(CacheEntry) -> Sample`; otherwise the wrapper
delegates to the wrapped `SampleSource`.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/deterministic-cache-store.md`
- Phase 1 source dependency: `rphys.datasources.sources`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p3-deterministic-cache-store`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: cache keys consume `SampleRequest`, `SampleRuntimeContext`, and optional `CacheContext` evidence; `CachedSampleSource` returns normal FieldLocator-keyed `Sample` objects from either the wrapped source or a caller-provided hit loader.
- Units/shapes/dtypes: this phase does not inspect, transform, resample, normalize, stack, pad, truncate, drop, tensorize, or move field payloads. Field units, schemas, dtypes, and shapes remain owned by existing sample/field contracts and any caller-supplied value strategy.
- Sampling/alignment/provenance: cache keys include request fingerprints, runtime context fingerprints, and invalidation evidence. Context-free wrapper access skips caching instead of writing under a synthetic key.
- Pipeline-order implications: operation and materialization details are represented only as primitive fingerprints/evidence. The cache does not apply operations or claim prepared-data equivalence.
- Leakage or subject/split implications: subject/split/group evidence remains in `SampleRuntimeContext` and participates in the runtime context fingerprint. This phase does not create splits, rebalance samples, or coordinate DDP ranks/workers.
- Legacy parity or intentional behavior changes: this is a new provisional public module. It rejects unsafe opaque `Sample` serialization and requires explicit hit/write strategies.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present for this phase
- [x] Acceptance or opt-in checks not present for this phase
- [x] Scientific/workflow contract review completed

Commands run:

```text
uv run pytest tests/unit/rphys/datasources/test_cache.py tests/contracts/test_cache_contract.py tests/integration/test_stage9_cache_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
make test-integration
make validate-pr
make test-summary
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 39 | 39 |
| unit | passed | 595 | 595 |
| contract | passed | 111 | 111 |
| integration | passed | 16 | 16 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 761 | 761 |

`make validate-pr` also passed, checked the lockfile, wrote the test summary,
built the source distribution and wheel, and ran `git diff --check`.

# Risks And Follow-Up

- Cache names remain scoped to `rphys.datasources.cache`; `rphys.datasources` and root `rphys` exports remain unchanged.
- Real generic payload persistence is intentionally deferred until a writer/reader contract exists. Current cache hits require a caller-supplied value loader.
- Remote stores, eviction, prepared data, optimized storage adapters, streaming/resume behavior, and stable distributed/DDP cache coordination remain future phases.
- `CachedSampleSource` can cache only when explicit runtime context evidence is supplied directly or through a context factory.

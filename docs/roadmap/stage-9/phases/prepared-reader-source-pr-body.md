# Summary

Implements Stage 9 Phase 4: prepared manifest, public provisional reader, and
prepared sample source. This adds `rphys.datasources.prepared` with
`PreparedField`, `PreparedDataManifest`, `PreparedReadRequest`,
`PreparedReadResult`, `PreparedSampleReader`, and `PreparedSampleSource`.

The reader boundary is intentionally public provisional. It lets backend
specific readers return FieldLocator-keyed `Sample` objects through a minimal
one-position read protocol, while `PreparedSampleSource` validates
manifest/request/context equivalence before reading. No concrete storage SDK,
materialization worker, cache payload writer, full read/write backend protocol,
trainer/device behavior, or model formatting is introduced.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/prepared-reader-source.md`
- Phase 1 source dependency: `rphys.datasources.sources`
- Phase 3 cache/evidence dependency: `rphys.datasources.cache`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p4-prepared-reader-source`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p4-prepared-reader-source`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p4-prepared-reader-source`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `PreparedSampleSource` consumes `SampleRequest` and `SampleRuntimeContext` evidence and returns normal FieldLocator-keyed `Sample` objects from a `PreparedSampleReader`.
- Units/shapes/dtypes: `PreparedField` records schema, dtype, shape, unit, checksum, layout, and metadata evidence. This phase records these facts but does not transform, resample, normalize, pad, stack, tensorize, or move payloads.
- Sampling/alignment/provenance: manifests include source/index/datasource identity, request fingerprint, operation/materialization fingerprints, field descriptors, split/group counts, checksums, runtime assumptions, invalidation, and metadata. Source reads validate manifest/request/context compatibility before calling the reader.
- Pipeline-order implications: prepared reads are immutable lookups. They do not execute preprocessing, operations, export, materialization, cache payload writing, or hidden fallback behavior in `__getitem__`.
- Leakage or subject/split implications: split/group counts are evidence only. This phase does not create, rebalance, enforce, or mutate splits.
- Legacy parity or intentional behavior changes: this is a new public provisional module. The reader protocol is intentionally minimal until real backend evidence justifies promotion or a fuller protocol.

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
uv run pytest tests/unit/rphys/datasources/test_prepared.py tests/contracts/test_prepared_sample_reader_contract.py tests/integration/test_stage9_prepared_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
make test-integration
make validate-pr
make test-summary
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 40 | 40 |
| unit | passed | 604 | 604 |
| contract | passed | 114 | 114 |
| integration | passed | 17 | 17 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 775 | 775 |

`make validate-pr` also passed, checked the lockfile, wrote the test summary,
built the source distribution and wheel, and ran `git diff --check`.

# Risks And Follow-Up

- Prepared names remain scoped to `rphys.datasources.prepared`; `rphys.datasources` and root `rphys` exports remain unchanged.
- `PreparedSampleReader` is public provisional and minimal. A second backend or real materialization implementation should trigger review before promotion.
- Concrete backend adapters, full read/write protocols, materialization workers, optimized layout records, cache payload writers, active streaming/resume, and DDP behavior remain deferred.

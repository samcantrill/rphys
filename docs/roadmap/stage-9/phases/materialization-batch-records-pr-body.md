# Summary

Implements Stage 9 Phase 5: storage-neutral materialization, layout, cost, and
batch-planning records. This extends `rphys.datasources.prepared` with public
provisional descriptor records for optimized storage formats, optimized data
plans, materialization plans/manifests, shard/chunk metadata, access patterns,
record layouts, batch costs, batch shape policies, and batch sampler plans.

These records are immutable, primitive/fingerprinted, and round-trip through
`to_dict`/`from_dict` for auditability. They describe prepared-data layout and
batching evidence without importing storage SDKs, writing files, sampling
batches, tensorizing payloads, moving devices, or formatting model inputs.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/materialization-batch-records.md`
- Prepared-data dependency: `rphys.datasources.prepared`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p5-materialization-batch-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p5-materialization-batch-records`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p5-materialization-batch-records`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: records store primitive descriptor evidence for layout,
  materialization, and batch planning. They do not read samples, write
  materialized products, open datasets, or yield batches.
- Units/shapes/dtypes: field identity is preserved through `FieldLocator`
  evidence. Byte offsets/lengths, sample counts, costs, lengths, split/group
  counts, checksums, compression metadata, runtime assumptions, and invalidation
  evidence are recorded but not interpreted as payload transformations.
- Sampling/alignment/provenance: materialization records reference prepared
  manifest fingerprints, request fingerprints, storage format fingerprints,
  shard/chunk IDs, record positions, and field locators. Cross-record checks
  reject undeclared shards/fields, out-of-range records, mismatched storage
  formats, and invalid chunk ranges where deterministic evidence is available.
- Pipeline-order implications: this phase records plans/manifests only. It does
  not execute preprocessing, export, materialization, cache payload writing,
  trainer sampling, streaming/resume state, DDP coordination, model formatting,
  tensor conversion, or device movement.
- Leakage or subject/split implications: split/group counts and cost/group
  metadata are evidence only. This phase does not create, rebalance, enforce, or
  mutate splits or subject grouping.
- Legacy parity or intentional behavior changes: this is new public provisional
  descriptor surface inside `rphys.datasources.prepared`; parent package and root
  exports remain unchanged.

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
uv run pytest tests/unit/rphys/datasources/test_materialization.py tests/unit/rphys/datasources/test_batch_planning.py tests/contracts/test_materialization_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
git diff --check
make validate-pr
make test-summary
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 40 | 40 |
| unit | passed | 615 | 615 |
| contract | passed | 116 | 116 |
| integration | passed | 17 | 17 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 788 | 788 |

`make validate-pr` also passed, checked the lockfile, wrote the test summary,
built the source distribution and wheel, and ran `git diff --check`.

# Risks And Follow-Up

- New names remain scoped to `rphys.datasources.prepared`; `rphys.datasources`
  and root `rphys` exports remain unchanged.
- Records are public provisional descriptors. Concrete LitData/WebDataset/Zarr/
  Arrow/Parquet/mmap adapters, actual materialization workers, file writers,
  cache payload writers, trainer samplers, active streaming/resume, benchmark
  thresholds, and DDP coordination remain deferred.
- Later trainer/data-loader work should consume these batch/materialization
  descriptors explicitly instead of adding hidden runtime behavior to them.

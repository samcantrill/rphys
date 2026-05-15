# Phase 5 Execution Plan: Storage-Neutral Materialization, Layout, Cost, And Batch-Planning Records

## Metadata

- Status: final phase execution plan; ready for implementation
- Roadmap stage: `v9`
- Feature focus: storage-neutral materialization/layout records and descriptive batch-planning records
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: Storage-Neutral Materialization, Layout, Cost, And Batch-Planning Records
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 5: Storage-Neutral Materialization, Layout, Cost, And Batch-Planning Records`
- Branch: `agent/stage-9-data-loading-cache-p5-materialization-batch-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p5-materialization-batch-records`
- Phase execution plan path: `docs/roadmap/stage-9/phases/materialization-batch-records.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path
- Blockers: none for implementation planning

## Objective

Add descriptive records for prepared/materialized storage layout and
cost-aware batching without implementing a storage backend, materialization
worker, sampler runtime, trainer integration, or device/model behavior.

## Scope

In scope:

- Extend `src/rphys/datasources/prepared.py` with code-backed public records:
  - `OptimizedStorageFormat`
  - `OptimizedDataPlan`
  - `MaterializationPlan`
  - `MaterializationManifest`
  - `ShardManifest`
  - `ChunkMetadata`
  - `AccessPatternPlan`
  - `RecordLayoutMetadata`
  - `BatchCostMetadata`
  - `BatchSamplerPlan`
  - `BatchShapePolicy`
- Primitive, immutable, fingerprinted records for backend identity, shard/chunk
  layout, offsets/lengths, checksums, compression metadata, access patterns,
  sample/field counts, split/group counts, runtime assumptions, and
  invalidation inputs.
- Descriptive-only batch cost, sampler, and shape policy records that can be
  consumed later by trainer/data-loader work without executing sampling.

Out of scope:

- Concrete LitData/WebDataset/Zarr/Arrow/Parquet/mmap adapters or SDK imports.
- Materialization worker execution, file writing, cache payload writers,
  trainer samplers, device movement, tensor conversion, benchmark thresholds,
  active streaming/resume, and stable DDP behavior.
- Parent/root exports.

## Public Contract

- Storage and batch-planning records are public provisional descriptor records.
- Records accept only JSON-like primitive evidence plus existing prepared
  manifest identity where applicable.
- Records expose stable fingerprints and `to_dict`/`from_dict` round trips for
  auditability.
- Invalid offsets, sizes, counts, duplicate identifiers, unsupported policies,
  and non-primitive metadata fail loudly with typed errors.
- No record executes IO, opens datasets, samples batches, imports backend SDKs,
  moves tensors/devices, or formats model inputs.

## Tests

- Package: prepared module exports and lightweight import boundary remain
  scoped and SDK-free.
- Unit: storage format/data/materialization plan, shard/chunk/layout records,
  materialization manifest compatibility, batch cost/sampler/shape records, and
  invalid metadata failures.
- Contract: materialization records round trip as backend-neutral descriptors
  and batch plans remain descriptive-only.
- Deferred: concrete backend, active materialization, trainer sampler, e2e, and
  acceptance checks.

## Validation Commands

```sh
uv run pytest tests/unit/rphys/datasources/test_materialization.py
uv run pytest tests/unit/rphys/datasources/test_batch_planning.py
uv run pytest tests/contracts/test_materialization_contract.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
git diff --check
```

Final PR gate:

```sh
make validate-pr
make test-summary
git diff --check
```

## Stop Conditions

- Stop if a concrete storage/backend SDK or materialization worker becomes
  necessary.
- Stop if batch records need to execute sampler/trainer/runtime behavior.
- Stop if schema choices require new domain policy beyond descriptive evidence.
- Stop if parent/root exports or heavy optional imports appear necessary.

## Completion Notes

- Draft plan: complete
- Final phase execution plan: complete
- Implementation summary: pending
- Implementation validation: pending
- Pre-submit blocker gate: no unresolved plan-level blocker identified
- PR body draft: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none identified for implementation

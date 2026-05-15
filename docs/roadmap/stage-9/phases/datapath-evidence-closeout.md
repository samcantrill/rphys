# Phase 6 Execution Plan: Data-Path Evidence, Integration, Docs, And Package Closeout

## Metadata

- Status: final phase execution plan; ready for implementation
- Roadmap stage: `v9`
- Feature focus: data-path evidence/profile records, synthetic integration, and Stage 9 closeout
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: Data-Path Evidence, Integration, Docs, And Package Closeout
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 6: Data-Path Evidence, Integration, Docs, And Package Closeout`
- Branch: `agent/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
- Phase execution plan path: `docs/roadmap/stage-9/phases/datapath-evidence-closeout.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path
- Blockers: none for implementation planning

## Objective

Close Stage 9 by adding descriptor-only data-path evidence records and a
license-safe synthetic integration that exercises the accepted source, cache,
prepared, collater, materialization, and batch-planning boundaries without
implementing active streaming, profiler, trainer, device, model-formatting, or
distributed runtime behavior.

## Scope

In scope:

- Add code-backed public provisional records in the Stage 9 owning module:
  - `StreamingReadPlan`
  - `DataLoaderState`
  - `DataPathProfile`
  - `DataPathBenchmark`
- Primitive, immutable, fingerprinted records for skip/resume evidence, cache
  hit/miss summaries, re-read counts, prepared/materialization references,
  batch-planning references, loader state summaries, timings, throughput,
  invalidation inputs, and environment/runtime assumptions.
- Focused synthetic integration that demonstrates source-to-batch flow plus
  cache/prepared equivalence boundaries with no raw data and no concrete
  backend SDK.
- Final package/import checks for Stage 9 public surfaces and root/parent
  export boundaries.
- Docs and PR evidence for public provisional labels and deferred behavior.

Out of scope:

- Active resumable loader runtime, stable distributed cache coordination,
  system profiler integration, trainer event schema, model formatting, tensor
  conversion, device movement, concrete backend benchmarks, benchmark
  thresholds, or performance claims.
- Raw datasets, optional heavy dependency requirements, or parent/root exports.

## Public Contract

- Data-path records are public provisional descriptor records.
- Records accept only JSON-like primitive evidence plus existing Stage 9
  fingerprints and identifiers.
- Records expose stable fingerprints and `to_dict`/`from_dict` round trips.
- Unsupported counts, durations, throughput values, duplicate identifiers,
  non-primitive metadata, and unstable runtime claims fail loudly.
- Records do not iterate, resume, profile, benchmark, sample, cache, read,
  write, tensorize, format model inputs, move devices, or coordinate workers.

## Tests

- Package: prepared module exports include only code-backed Stage 9 names; root
  and `rphys.datasources` remain intentionally scoped.
- Unit: data-path record round trips, fingerprint sensitivity, invalid evidence,
  and descriptive-only behavior.
- Integration: synthetic Stage 9 flow from sample source through collater,
  cache and prepared boundaries, materialization descriptors, and data-path
  profile/benchmark evidence.
- Contract: public data-path records remain primitive, backend-neutral, and
  runtime-free.
- Deferred: concrete profiler, distributed/resume, real optimized backend, e2e,
  and acceptance checks.

## Validation Commands

```sh
uv run pytest tests/unit/rphys/datasources/test_data_path_records.py
uv run pytest tests/integration/test_stage9_data_path_flow.py
uv run pytest tests/contracts/test_data_path_records_contract.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
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

- Stop if data-path evidence requires benchmark thresholds, profiler adapters,
  trainer callbacks, stable DDP semantics, active resume, or worker
  coordination.
- Stop if implementation needs concrete storage/backend SDKs or raw datasets.
- Stop if package closeout requires parent/root exports or placeholder names.
- Stop if docs require changing the already-approved Stage 9 scope.

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

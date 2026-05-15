# Summary

Implements Stage 9 Phase 6: data-path evidence, synthetic integration, docs,
and package closeout. This adds `rphys.datasources.datapath` with public
provisional descriptor records:

- `StreamingReadPlan`
- `DataLoaderState`
- `DataPathProfile`
- `DataPathBenchmark`

The new records are immutable, primitive/fingerprinted, JSON-compatible through
`to_dict`/`from_dict`, and intentionally descriptive-only. They make source,
cache, prepared, materialization, and batch-planning evidence inspectable
without adding active streaming/resume runtime, profiler integration, trainer
event schemas, model formatting, tensor conversion, device movement, concrete
backend benchmarks, benchmark thresholds, or DDP coordination.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/datapath-evidence-closeout.md`
- Data-path module: `rphys.datasources.datapath`
- Prior Stage 9 dependencies: `rphys.datasources.sources`, `rphys.datasources.cache`, `rphys.datasources.prepared`, `rphys.datasources.torch`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p6-datapath-evidence-closeout`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: data-path records store primitive evidence for read plans,
  loader state snapshots, profile summaries, and benchmark observations. They
  do not read samples, write caches, materialize products, iterate loaders,
  resume workers, profile systems, run benchmarks, yield batches, tensorize
  payloads, or format model inputs.
- Units/shapes/dtypes: counts are explicit non-negative integers; durations are
  non-negative finite milliseconds; throughput values are non-negative finite
  samples-per-second style observations with caller-provided units.
- Sampling/alignment/provenance: records preserve request fingerprints,
  materialization fingerprints, state/profile fingerprints, cache hit/miss
  counts, prepared/materialized read counts, reread counts, batch counts,
  summaries, environment evidence, limitations, and metadata.
- Pipeline-order implications: evidence is recorded after existing source,
  cache, prepared, materialization, and collater behavior. This phase does not
  move preprocessing, export, cache payload writing, materialization, trainer
  sampling, streaming/resume, DDP coordination, or profiling into Stage 9.
- Leakage or subject/split implications: profile and benchmark summaries are
  evidence only. This phase does not create, rebalance, enforce, or mutate
  splits or subject groups.
- Legacy parity or intentional behavior changes: `rphys.datasources.datapath`
  is a new public provisional module. Root `rphys` and parent
  `rphys.datasources` exports remain unchanged.

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
uv run pytest tests/unit/rphys/datasources/test_data_path_records.py tests/integration/test_stage9_data_path_flow.py tests/contracts/test_data_path_records_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
make test-integration
git diff --check
make validate-pr
make test-summary
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 41 | 41 |
| unit | passed | 622 | 622 |
| contract | passed | 118 | 118 |
| integration | passed | 18 | 18 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 799 | 799 |

`make validate-pr` also passed, checked the lockfile, wrote the test summary,
built the source distribution and wheel, and ran `git diff --check`.

# Risks And Follow-Up

- New names remain scoped to `rphys.datasources.datapath`; `rphys.datasources`
  and root `rphys` exports remain unchanged.
- Records are public provisional descriptors. Real profiler integrations,
  active resume, stable distributed coordination, trainer event schemas,
  concrete backend benchmarks, and benchmark thresholds remain deferred.
- Later Stage 15 profiling/performance work should consume these records
  explicitly instead of adding hidden runtime behavior to them.

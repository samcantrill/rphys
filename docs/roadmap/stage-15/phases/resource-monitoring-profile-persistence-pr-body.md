## Summary

Implements Stage 15 Phase 3 resource monitoring and profile persistence
contracts:

- Adds primitive resource metric/unit/status vocabulary, `ResourceSample`, and
  ordered `ResourceTrace` records with strict sequence ordering and timestamp
  validation.
- Adds dependency-free fake resource probes, optional run-scoped
  `ResourceMonitor` lifecycle evidence, bounded queue/drop/backpressure
  records, and explicit failure/unavailable behavior.
- Adds structural async profile writer contracts with disabled/no-op,
  bounded queueing, flush scopes, in-memory backend, failure records, and
  monotonic flush sequence evidence.
- Extends `TrainingProfile` and `TrainingProfileRecorder` additively with
  resource traces, monitor lifecycle records, writer append/drop evidence, and
  writer flush summaries.
- Updates package exports, Stage 15 contracts, import-boundary coverage, and
  focused unit tests.

## Scientific Contract Implications

- Resource measurements are observational traces, not code spans or training
  quality claims.
- Samples carry explicit metric kind, unit, status, timestamp, sequence id,
  optional cadence, attribution, clock metadata, synchronization/overhead
  evidence, metadata, and provenance.
- Unavailable, ambiguous, disabled, dropped, monitor failure, writer failure,
  and backpressure cases are represented as inspectable records instead of
  logs or silent omissions.
- Resource traces reject ambiguous mixed attribution and recorder-created
  traces are keyed by metric, unit, probe, series, run/timeline, clock,
  process, node, rank, device, and resource attribution.
- Writer append/drop results can be persisted in `TrainingProfile`, and flush
  summaries carry queue drops since the previous flush result.
- Cross-process/rank/device timestamp comparison remains descriptive unless
  downstream code supplies clock-origin/alignment evidence.
- No real hardware probes, engine hooks, durable file format, artifact store,
  daemon, scheduler, Native wiring, Lightning wiring, or data-path producer
  behavior is added in this phase.

## Validation

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/training/test_profiling.py tests/contracts/test_stage15_training_profile_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py`
  - 88 passed
- `make test-package`
  - 72 passed
- `make test-unit`
  - 788 passed
- `make test-contract`
  - 187 passed
- `make test-summary`
  - package 72 passed
  - unit 788 passed
  - contract 187 passed
  - integration 30 passed
  - e2e not present
  - acceptance not present
- `make validate-pr`
  - lock check passed
  - package/unit/contract/integration summary passed
  - e2e/acceptance not present
  - `uv build` passed
  - `git diff --check` passed
- `UV_CACHE_DIR=/tmp/uv-cache uv lock --check`
  - passed
- `git diff --check`
  - passed

## Assumptions And Residual Risks

- The metric taxonomy is provisional and broad; downstream integrations may add
  metric kinds later when real probes prove a missing signal family.
- Async profile persistence remains a contract over normalized records, not a
  durable profile file format.
- Real resource probes remain out of scope to keep base imports lightweight and
  validation hardware-independent.
- Monitor execution modes are lifecycle semantics only in this phase; real
  thread/process execution is deferred to engine integrations.

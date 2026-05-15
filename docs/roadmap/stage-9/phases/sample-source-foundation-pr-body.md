# Summary

Implements Stage 9 Phase 1: the framework-neutral sample-source foundation for
data loading. This adds `rphys.datasources.sources` with `SampleRequest`,
`SampleRuntimeContext`, `WorkerContextFactory`, `SampleSource`, and
`IndexSampleSource`, composing the existing `DataSourceIndex` and
`SampleBuilder` contracts without adding torch, cache, prepared-data, export,
model, trainer, device, or workflow-runtime behavior.

The new source path preserves `FieldLocator`-keyed `Sample` returns, supports
default all-field requests and ordered subset requests, keeps eager/lazy loading
delegated to `SampleBuilder`, and records deterministic primitive request and
runtime-context evidence for later cache/prepared phases.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/sample-source-foundation.md`
- Implementation plan: `docs/roadmap/stage-9/implementation-plan.md`
- Scientific review: Phase acceptance evidence in `docs/roadmap/stage-9/phases/sample-source-foundation.md`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p1-sample-source-foundation`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p1-sample-source-foundation`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleSource.sample_at(position, request=None, context=None)` and `__getitem__` return `rphys.data.containers.Sample` objects from existing index items; no raw payloads, model tuples, batches, or loader objects are returned.
- Units/shapes/dtypes: field units, sample rates, shapes, dtypes, and loading behavior remain owned by existing `FieldView`, `SampleField`, codec, and `SampleBuilder` contracts. Phase 1 does not resample, align, filter, normalize, mask, aggregate, pad, stack, or move data.
- Sampling/alignment/provenance: `SampleRuntimeContext` captures primitive source/index/entry, split/group, field-window, worker/rank, seed, and request-fingerprint evidence without changing the returned `Sample` shape or injecting source evidence into codec load contexts.
- Pipeline-order implications: `SampleRequest` fingerprints include requested locators, eager mode, and optional primitive operation/materialization labels only; no operation, cache, prepared-data, or workflow execution is introduced.
- Leakage or subject/split implications: existing `DataSourceIndexEntry` split/group evidence remains inspectable through context records, but this phase does not create, rebalance, filter, validate, or enforce split policy.
- Legacy parity or intentional behavior changes: source access is a new Stage 9 API. Invalid positions, empty or duplicate explicit requests, malformed locators, missing fields, invalid construction inputs, invalid context metadata, and mismatched caller-provided contexts fail loudly through typed rphys errors.

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
UV_CACHE_DIR=/tmp/uv-cache make validate-pr
UV_CACHE_DIR=/tmp/uv-cache make test-summary
uv run pytest tests/unit/rphys/datasources/test_sources.py
uv run pytest tests/unit/rphys/datasources/test_sources.py tests/contracts/test_sample_source_contract.py tests/integration/test_stage9_sample_source_flow.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
git diff --check
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 36 | 36 |
| unit | passed | 571 | 571 |
| contract | passed | 103 | 103 |
| integration | passed | 14 | 14 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 724 | 724 |

`make validate-pr` also passed and built the source distribution and wheel.

# Risks And Follow-Up

- Phase 1 intentionally keeps source APIs module-scoped to `rphys.datasources.sources`; root and parent `rphys.datasources` exports remain unchanged.
- `SampleRuntimeContext` rank/world and worker fields are deterministic evidence only, not stable distributed coordination.
- A distinct `DerivedIndexSampleSource`, torch adapters, cache stores, prepared readers/sources, materialization records, batch-planning records, model formatting, device movement, and trainer behavior remain deferred to later phases.

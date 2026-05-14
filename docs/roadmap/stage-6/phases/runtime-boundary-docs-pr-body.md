# Summary

Implements Stage 6 Phase 4 runtime-boundary proof and public operation wording.

This PR adds a contract test showing generic `Operation` wrappers treat loaded
`Sample` and `Batch` containers as ordinary Python payloads, returning
`OperationResult` and requiring callers to unwrap `.output`. It also proves lazy
`SampleField` materialization remains owned by runtime APIs: `sample.field()` in
a wrapped kernel does not load, while a payload-demanding `sample.require()`
call loads exactly once.

The docs/docstrings for `rphys.ops` now clarify package-level imports, plain
kernels versus wrapped operations, explicit `.output` use, sequence-only
`OperationPipeline`, declaration-only mutation/side-effect semantics, and
Stage 7/8/9 deferrals.

# Links

- Roadmap stage: `docs/roadmap.md`
- Phase plan: `docs/roadmap/stage-6/phases/runtime-boundary-docs.md`
- Implementation plan: `docs/roadmap/stage-6/implementation-plan.md`
- Scientific review: encoded in the phase plan and automated phase review

# Phase Isolation

- Branch: `agent/stage-6-p4-runtime-boundary-docs`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-6-p4-runtime-boundary-docs`
- Base branch: `develop`
- Head branch: `agent/stage-6-p4-runtime-boundary-docs`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: generic operations accept runtime containers as ordinary
  payloads when declared with `OperationContract(input_type=..., output_type=...)`.
- Units/shapes/dtypes: no numerical unit, shape, dtype, device, or sampling
  policy is introduced.
- Sampling/alignment/provenance: no resampling, alignment, padding, windowing,
  datasource identity, manifest, cache key, or workflow provenance behavior is
  added.
- Pipeline-order implications: no pipeline execution semantics change; docs
  restate that `OperationPipeline` is sequence-only and forwards
  `OperationResult.output`.
- Leakage or subject/split implications: none; no subject, split, grouping,
  record, or dataset policy changes.
- Legacy parity or intentional behavior changes: no runtime/data/IO/datasource
  behavior changed; this phase adds tests and public wording only.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present
- [x] Acceptance or opt-in checks not present
- [x] Scientific/workflow contract review completed

Commands run:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_operation_runtime_boundary_contract.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_operation_execution_contract.py tests/contracts/test_operation_pipeline_contract.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/ops/test_contracts.py tests/unit/rphys/ops/test_core.py tests/unit/rphys/ops/test_pipelines.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py
make test-contract
make test-unit
make test-package
make validate-pr
git diff --check
```

Latest `make validate-pr` evidence:

```text
package: passed (29 passed)
unit: passed (416 passed)
contract: passed (73 passed)
integration: passed (3 passed)
e2e: not present
acceptance: not present
uv lock --check: passed
uv build: passed
git diff --check: passed
```

# Risks And Follow-Up

The runtime-boundary test intentionally avoids builders, datasources, real
files, and support fixtures. Phase 5 owns final Stage 6 validation and readiness
evidence. Stage 7/8/9 still own `SampleOp`/`BatchOp`, locator permissions,
export/save/cache/workflow identity, and specialized operation families.

# Summary

Implements Stage 9 Phase 2: the optional torch adapter and FieldLocator
collater boundary. This adds `rphys.datasources.torch` with
`TorchSampleSourceDataset`, `TorchIndexSampleDataset`, `TorchDataLoaderPlan`,
and `TorchDataLoaderBuilder`, plus a framework-neutral `BatchCollater` in
`rphys.data.collation`.

The adapter module is importable without torch installed. Torch is imported
only when `TorchDataLoaderBuilder.build()` constructs a real
`torch.utils.data.DataLoader`; missing or malformed torch raises
`RemotePhysDependencyError`. Dataset wrappers delegate to Phase 1
`SampleSource` behavior and return `FieldLocator`-keyed `Sample` objects. The
collater delegates to `collate_samples` and preserves the existing LIST-only
`Batch` contract.

# Links

- Roadmap stage: `docs/roadmap/stage-9/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-9/phases/torch-collater-boundary.md`
- Phase 1 source dependency: `rphys.datasources.sources`

# Phase Isolation

- Branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Base branch: `develop`
- Head branch: `agent/stage-9-data-loading-cache-p2-torch-collater-boundary`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: torch dataset wrappers return `Sample` objects; `BatchCollater` returns `Batch` objects. No model tuples, raw payload dictionaries, hard-coded input/target structures, tensor conversions, or device movement are introduced.
- Units/shapes/dtypes: field units, sample rates, schemas, dtypes, and payload shapes remain owned by existing field/sample/collation contracts. Phase 2 does not resample, align, filter, normalize, mask, aggregate, stack, pad, truncate, drop, or move data.
- Sampling/alignment/provenance: dataset access delegates to `SampleSource` and preserves source request behavior and source/builder provenance. Collation preserves FieldLocator keys, schemas, metadata, and LIST payload ordering.
- Optional dependency behavior: importing `rphys.datasources.torch` does not import torch. Constructing an actual torch DataLoader is the only torch-requiring path.
- Leakage or subject/split implications: this phase does not build, rebalance, validate, or enforce splits. Loader shuffle/drop settings are explicit data-loader settings only, not leakage policy.

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
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_collation.py tests/unit/rphys/datasources/test_torch.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_batch_collater_contract.py tests/contracts/test_torch_adapter_contract.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/integration/test_stage9_torch_collater_flow.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache make test-package
UV_CACHE_DIR=/tmp/uv-cache make test-unit
UV_CACHE_DIR=/tmp/uv-cache make test-contract
UV_CACHE_DIR=/tmp/uv-cache make test-integration
UV_CACHE_DIR=/tmp/uv-cache make validate-pr
UV_CACHE_DIR=/tmp/uv-cache make test-summary
git diff --check
```

Suite evidence from `make test-summary`:

| Suite | Status | Passed | Total |
| --- | --- | ---: | ---: |
| package | passed | 38 | 38 |
| unit | passed | 583 | 583 |
| contract | passed | 108 | 108 |
| integration | passed | 15 | 15 |
| e2e | not present | 0 | 0 |
| acceptance | not present | 0 | 0 |
| Overall | passed | 744 | 744 |

`make validate-pr` also passed and built the source distribution and wheel.

# Risks And Follow-Up

- `rphys.datasources.torch` names remain scoped to the adapter module; `rphys.datasources` and root `rphys` exports remain unchanged.
- Real torch execution is covered through lazy import/fake DataLoader behavior because the repository has no torch runtime dependency or optional torch extra.
- `TorchDataLoaderPlan` is intentionally narrow and data-only; sampler, distributed, trainer, device, and model-formatting behavior remains future work.
- `BatchCollater` remains LIST-only. Stack/pad/drop/tensor-conversion policies require a later explicit design.

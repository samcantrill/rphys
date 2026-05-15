# Summary

Implements roadmap Stage 7 Phase 6 by adding the provisional, dependency-light batch operation surface.

The PR adds `BatchOperation`, `BatchTransform`, `BatchAugmentation`, `BatchOperationContext`, `BatchOperationContract`, `BatchAugmentationParams`, `BatchEquivalenceReport`, and `BatchOperationPipeline`. The implementation includes exact field-effect enforcement, explicit batch/per-sample augmentation parameter scope, descriptive dtype/device context, runtime batch equivalence metadata, and synthetic LIST-collated integration coverage.

# Links

- Roadmap stage: `docs/roadmap/stage-7/planning.md`
- Phase plan: `docs/roadmap/stage-7/phases/batch-surface.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/planning.md`

# Phase Isolation

- Branch: `agent/stage-7-p6-batch-surface`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p6-batch-surface`
- Base branch: `develop`
- Head branch: `agent/stage-7-p6-batch-surface`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: batch operations accept and return `Batch` objects through `OperationResult`; intermediate pipeline results forward `OperationResult.output`.
- Units/shapes/dtypes: dtype and device are descriptive metadata only. The base library does not allocate arrays, move devices, or interpret backend layouts.
- Sampling/alignment/provenance: batch augmentation sampling and deterministic application are split. Equivalence reports describe identical, approximate, diagnostic, or unsupported sample-side replacement claims.
- Pipeline-order implications: `BatchOperationPipeline` preserves sequence or insertion-ordered mapping order; mapping keys are diagnostic names only.
- Leakage or subject/split implications: no subject, split, loader, DataLoader, cache, trainer, model, export, workflow, or device policy is introduced.
- Legacy parity or intentional behavior changes: this is additive provisional Stage 7 behavior and preserves existing LIST collation, generic pipeline, and sample pipeline contracts.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests not present
- [x] Acceptance or opt-in checks not present
- [x] Scientific/workflow contract review completed through phase-plan readback and pre-submit gate

Commands run:

```text
uv run pytest tests/unit/rphys/ops/test_batch.py tests/contracts/test_batch_operations.py tests/integration/test_batch_operations_integration.py tests/package/test_import.py
make test-unit
make test-contract
make test-integration
make test-package
make validate-pr
make test-summary
git diff --check
```

Suite evidence from `make test-summary`:

| Suite | Result | Evidence |
| --- | --- | --- |
| package | passed | 33 passed |
| unit | passed | 501 passed |
| contract | passed | 91 passed |
| integration | passed | 11 passed |
| e2e | not present | 0 tests |
| acceptance | not present | 0 tests |

# Risks And Follow-Up

- Batch APIs are provisional and intentionally descriptive. Real fused kernels may need stronger numeric-equivalence evidence later.
- Phase 7 owns final documentation and validation readback for the completed Stage 7 surface.

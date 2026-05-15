# Summary

Implements roadmap Stage 7 Phase 5 by adding the public `SampleOperationPipeline` specialized composition surface while preserving the generic `OperationPipeline` sequence-only contract.

The PR adds sequence and insertion-ordered mapping construction for sample operations, private diagnostic step normalization, sample context propagation, output forwarding, and step-aware execution diagnostics. Mapping keys are diagnostics only and do not replace operation identity.

# Links

- Roadmap stage: `docs/roadmap/stage-7/planning.md`
- Phase plan: `docs/roadmap/stage-7/phases/sample-pipeline.md`
- Implementation plan: `docs/roadmap/stage-7/implementation-plan.md`
- Scientific review: `docs/roadmap/stage-7/planning.md`

# Phase Isolation

- Branch: `agent/stage-7-p5-sample-pipeline`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-7-p5-sample-pipeline`
- Base branch: `develop`
- Head branch: `agent/stage-7-p5-sample-pipeline`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleOperationPipeline` composes `SampleOperation` steps and returns the final `OperationResult`; each intermediate `OperationResult.output` is forwarded to the next step.
- Units/shapes/dtypes: the pipeline does not inspect or transform payload units, shapes, dtypes, devices, or backend arrays.
- Sampling/alignment/provenance: pipeline order is deterministic. Sampling, replay, field effects, and provenance remain owned by individual sample operation steps.
- Pipeline-order implications: sequences and insertion-ordered mappings preserve order; mapping keys are diagnostic step names only.
- Leakage or subject/split implications: no split, subject, loader, cache, trainer, model, workflow, retry, resume, or routing policy is introduced.
- Legacy parity or intentional behavior changes: generic `OperationPipeline` still rejects mappings and tuple named entries; specialized mapping support is additive on `SampleOperationPipeline`.

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
uv run pytest tests/unit/rphys/ops/test_pipelines.py tests/contracts/test_operation_pipeline_contract.py tests/package/test_import.py
make test-unit
make test-contract
make test-package
make validate-pr
make test-summary
git diff --check
```

Suite evidence from `make test-summary`:

| Suite | Result | Evidence |
| --- | --- | --- |
| package | passed | 32 passed |
| unit | passed | 491 passed |
| contract | passed | 87 passed |
| integration | passed | 9 passed |
| e2e | not present | 0 tests |
| acceptance | not present | 0 tests |

# Risks And Follow-Up

- Mapping keys are diagnostic labels only, not durable pipeline identity.
- Phase 6 owns `BatchOperationPipeline` and any shared internalization that proves worthwhile after batch implementation.

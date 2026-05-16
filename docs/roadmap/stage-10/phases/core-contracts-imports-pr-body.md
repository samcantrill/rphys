# Summary

Implement Stage 10 Phase 1 by adding the first code-backed method/model public contracts. This introduces immutable primitive `PredictionContext`, patch-like `MethodOutput`, a structural batch-level `Method.predict(...) -> MethodOutput` protocol, and a generic callable `Model[InputT, OutputT]` protocol that stays below `Batch`.

# Links

- Roadmap stage: `docs/roadmap/stage-10/planning.md`
- Phase plan: `docs/roadmap/stage-10/phases/core-contracts-imports.md`
- Implementation plan: `docs/roadmap/stage-10/implementation-plan.md`
- Scientific review: Stage 10 Phase 1 pre-submit blocker gate in the phase plan

# Phase Isolation

- Branch: `agent/stage-10-method-model-contracts-p1-core-contracts-imports`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p1-core-contracts-imports`
- Base branch: `develop`
- Head branch: `agent/stage-10-method-model-contracts-p1-core-contracts-imports`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: methods consume `Batch` and return patch-like `MethodOutput`; models are generic callables and do not import runtime containers.
- Units/shapes/dtypes: no tensor, dtype, unit, shape, sample-rate, or device semantics are introduced.
- Sampling/alignment/provenance: context/output provenance is caller-owned primitive metadata only; no alignment or provenance inference is added.
- Pipeline-order implications: no hidden mutation, merge/apply, export, loss, metric, learner, or trainer behavior.
- Leakage or subject/split implications: no first-class sample, batch, record, split, group, or leakage policy fields are added.
- Legacy parity or intentional behavior changes: methods/models package homes now expose scoped code-backed Stage 10 contract names; root package remains unchanged.

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
uv run pytest tests/unit/rphys/methods/test_context.py tests/unit/rphys/methods/test_output.py
uv run pytest tests/contracts/test_method_contract.py tests/contracts/test_model_contract.py
make test-package
make validate-pr
make test-summary
git diff --check
```

# Risks And Follow-Up

The records are intentionally small and may need additive fields once Stage 12/13 define trainer or prediction-runner needs. Phase 2 owns adapters and explicit output application; Phase 3 owns state/trainable capability records.

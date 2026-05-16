# Summary

Implement Stage 10 Phase 3 by adding backend-neutral state and trainable capability records. This introduces named `StateEntry`/`StateView`, strict-load diagnostics through `StateLoadResult`, descriptive `ParameterView` handles, and structural `StatefulMethod`/`TrainableMethod` protocols.

# Links

- Roadmap stage: `docs/roadmap/stage-10/planning.md`
- Phase plan: `docs/roadmap/stage-10/phases/state-trainable-records.md`
- Implementation plan: `docs/roadmap/stage-10/implementation-plan.md`
- Scientific review: Stage 10 Phase 3 pre-submit blocker gate in the phase plan

# Phase Isolation

- Branch: `agent/stage-10-method-model-contracts-p3-state-trainable-records`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p3-state-trainable-records`
- Base branch: `develop`
- Head branch: `agent/stage-10-method-model-contracts-p3-state-trainable-records`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: methods can expose state views, load diagnostics, and parameter handles; prediction semantics remain unchanged.
- Units/shapes/dtypes: state values and parameter handles are backend-owned objects; no tensor dtype, unit, shape, or device policy is introduced.
- Sampling/alignment/provenance: generic primitive metadata/provenance is preserved on records without sampling or alignment inference.
- Pipeline-order implications: no optimizer, scheduler, checkpoint writer, device mover, trainer loop, export, loss, or metric behavior.
- Leakage or subject/split implications: no identity, split, grouping, or leakage policy is encoded.
- Legacy parity or intentional behavior changes: methods exports now include state/trainable capability records and protocols; `rphys.nn` remains empty because no helper is code-backed in this phase.

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
uv run pytest tests/unit/rphys/methods/test_state.py
uv run pytest tests/contracts/test_trainable_method_contract.py
uv run pytest tests/contracts/test_method_contract.py
make test-package
make validate-pr
make test-summary
git diff --check
```

# Risks And Follow-Up

Optimizer grouping, checkpoint schemas, device movement, distributed state, and optional torch/Lightning helpers remain deferred to later roadmap stages. Parameter views are descriptive handles only.

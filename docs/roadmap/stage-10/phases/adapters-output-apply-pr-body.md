# Summary

Implement Stage 10 Phase 2 by adding explicit adapter specs between `Batch` fields and named method/model values, plus explicit patch-to-`Batch` application. Input specs extract declared payloads from `Batch`; output specs map named model results into `MethodOutput`; `apply_method_output` handles shallow-copy default application and explicit conflict policy.

# Links

- Roadmap stage: `docs/roadmap/stage-10/planning.md`
- Phase plan: `docs/roadmap/stage-10/phases/adapters-output-apply.md`
- Implementation plan: `docs/roadmap/stage-10/implementation-plan.md`
- Scientific review: Stage 10 Phase 2 pre-submit blocker gate in the phase plan

# Phase Isolation

- Branch: `agent/stage-10-method-model-contracts-p2-adapters-output-apply`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p2-adapters-output-apply`
- Base branch: `develop`
- Head branch: `agent/stage-10-method-model-contracts-p2-adapters-output-apply`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adapters extract declared `Batch` payloads and map declared output names into `MethodOutput` fields; patch application is a standalone explicit helper.
- Units/shapes/dtypes: only optional Python type and schema checks are added; no tensor schema, dtype, unit, sample-rate, or device policy is introduced.
- Sampling/alignment/provenance: field locators, schemas, metadata/provenance mappings, and caller-selected output roles stay explicit; no alignment inference is added.
- Pipeline-order implications: `Method.predict` still returns a patch and does not mutate inputs; `apply_method_output` copies by default and requires explicit replacement policy for conflicts.
- Leakage or subject/split implications: no identity, split, grouping, or leakage policy is encoded.
- Legacy parity or intentional behavior changes: methods package exports now include adapter specs/adapters and `apply_method_output`; root package remains unchanged.

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
uv run pytest tests/unit/rphys/methods/test_adapters.py
uv run pytest tests/unit/rphys/methods/test_output.py
uv run pytest tests/contracts/test_method_contract.py
uv run pytest tests/integration/test_synthetic_method_prediction_flow.py
make test-package
make test-unit
make validate-pr
make test-summary
git diff --check
```

# Risks And Follow-Up

Adapter validation remains local/private. Stage 11/13 can factor shared selector semantics only after repeated use proves the need. Future non-LIST or copied-batch uncollation semantics remain outside this phase.

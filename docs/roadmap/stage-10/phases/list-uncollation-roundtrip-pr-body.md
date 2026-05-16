# Summary

Implement Stage 10 Phase 0 by adding a data-layer inverse for default LIST-collated batches. `collate_samples` now attaches private per-batch evidence so `uncollate_batch(batch) -> tuple[Sample, ...]` can reconstruct sample fields, schemas, collate policy, and sparse metadata while preserving the distinction between explicit `None` and absent metadata. Non-reversible or edited batches fail loudly instead of guessing.

# Links

- Roadmap stage: `docs/roadmap/stage-10/planning.md`
- Phase plan: `docs/roadmap/stage-10/phases/list-uncollation-roundtrip.md`
- Implementation plan: `docs/roadmap/stage-10/implementation-plan.md`
- Scientific review: Stage 10 Phase 0 pre-submit blocker gate in the phase plan

# Phase Isolation

- Branch: `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- Base branch: `develop`
- Head branch: `agent/stage-10-method-model-contracts-p0-list-uncollation-roundtrip`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: default LIST-collated `Batch` to immutable `tuple[Sample, ...]`; no model tuple formatting or trainer/export behavior.
- Units/shapes/dtypes: payloads, schemas, and field locators are preserved as stored; no unit, dtype, shape, or tensor interpretation is introduced.
- Sampling/alignment/provenance: sample order and generic metadata presence round-trip only when private LIST evidence proves reversibility; no temporal alignment or provenance inference is added.
- Pipeline-order implications: lazy field payloads are still materialized before metadata evidence is captured, preserving existing LIST collation semantics.
- Leakage or subject/split implications: no first-class domain identifiers are introduced; caller-owned metadata round-trips when reversible.
- Legacy parity or intentional behavior changes: current LIST collation payload/metadata shape is preserved; new behavior is explicit uncollation plus fail-loud validation for ambiguous batches.

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
uv run pytest tests/unit/rphys/data/test_collation.py
uv run pytest tests/contracts/test_batch_collater_contract.py
uv run pytest tests/integration/test_stage9_torch_collater_flow.py
uv run pytest tests/unit/rphys/data/test_sample_fields.py::test_lazy_fields_collate_through_payload_demanding_list_policy tests/unit/rphys/data/test_collation.py
make test-package
make validate-pr
make test-summary
git diff --check
```

# Risks And Follow-Up

Private evidence is intentionally limited to batches produced by the default LIST collater. Future stack, pad, drop, custom, or manually assembled batch policies need their own inverse semantics before they can participate in uncollation.

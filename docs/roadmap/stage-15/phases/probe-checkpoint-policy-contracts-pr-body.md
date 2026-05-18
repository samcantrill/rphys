# Summary

Implements Stage 15 Phase 2 contract-only training observability surfaces:
engine-neutral probe records, checkpoint catalog/restart-selection evidence,
checkpoint save/restore/prune result records, and primitive precision,
compile, and kernel policy descriptors.

The PR stays schema-only. It does not add Native or Lightning wiring, real
checkpoint IO, resource sampling, profile persistence, tensor/batch inspection,
or Stage 9 datasource imports from training core.

# Links

- Roadmap stage: `docs/roadmap.md`, Milestone 15
- Phase plan: `docs/roadmap/stage-15/phases/probe-checkpoint-policy-contracts.md`
- Implementation plan: `docs/roadmap/stage-15/implementation-plan.md`
- Scientific review: implementation-plan quality gate and Phase 2 refinement notes in the phase plan

# Phase Isolation

- Branch: `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- Base branch: `develop`
- Head branch: `agent/stage-15-training-profiling-p2-probe-checkpoint-policy-contracts`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adds frozen dataclass records for probe cadence/selectors,
  model/data diagnostic summaries, checkpoint references/catalog selection,
  save/restore/prune evidence, and optimization policy state.
- Units/shapes/dtypes: shape evidence is primitive tuple data; dtype/device
  evidence is string-based; finite numeric values are validated and ratios are
  bounded to `[0, 1]`.
- Sampling/alignment/provenance: records carry run, timeline, sequence,
  process, rank, device, metadata, and provenance fields where relevant, without
  claiming clock synchronization or resource-trace alignment.
- Pipeline-order implications: locks Stage 9-aligned pipeline stage names by
  string only; training core does not import datasource runtime objects.
- Leakage or subject/split implications: data probe records preserve split,
  source/cache/prepared, field, locator, and primitive provenance evidence, but
  do not compute or aggregate subject-level statistics.
- Legacy parity or intentional behavior changes: Phase 1 event/profile/result
  contracts remain additive and compatible; new public names are provisional
  and code-backed.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_stage15_training_profile_contract.py tests/contracts/test_stage15_probe_checkpoint_policy_contract.py tests/unit/rphys/training/test_checkpoint.py tests/unit/rphys/training/test_probes.py tests/unit/rphys/training/test_policies.py
make test-package
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
git diff --check
make test-summary
make validate-pr
```

Suite summary from `make test-summary` / `make validate-pr`:

| Suite | Result |
| --- | --- |
| package | 72 passed |
| unit | 778 passed |
| contract | 187 passed |
| integration | 30 passed |
| e2e | not present |
| acceptance | not present |

# Risks And Follow-Up

- Phase 2 is intentionally contract-only; Native wiring, checkpoint hook
  execution, resource traces, data-path producer evidence, and Lightning mapping
  remain later Stage 15 phases.
- Public export tests are strict; future additions should update package export
  expectations with the same intentional ordering.

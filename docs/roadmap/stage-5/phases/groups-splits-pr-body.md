# Summary

Implements candidate-level group extraction and explicit group-disjoint split assignment. Required groups and missing explicit split mappings fail loudly, while non-split analysis groups are preserved for downstream metadata.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/groups-splits.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p4-groups-splits`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p4-groups-splits`
- Base branch: `develop`
- Head branch: `agent/stage-5-p4-groups-splits`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: selected candidates become group assignments and explicit split assignments.
- Units/shapes/dtypes: no payload values or runtime arrays are introduced.
- Sampling/alignment/provenance: unchanged; candidate provenance is preserved.
- Pipeline-order implications: split assignment occurs after candidate filtering and before final index construction.
- Leakage or subject/split implications: split-group values cannot be silently split across multiple splits.
- Legacy parity or intentional behavior changes: implicit ratios are intentionally not implemented.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
make test-unit
make test-contract
make test-package
git diff --check
```

# Risks And Follow-Up

Only explicit group-to-split assignment is implemented. Ratio/seed policies remain deferred until real use justifies them.

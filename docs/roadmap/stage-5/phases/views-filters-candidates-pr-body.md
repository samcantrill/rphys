# Summary

Implements non-mutating datasource views, structural filter chains, and provisional index candidates. Candidate construction maps record fields to `FieldView`s and supports candidate filtering before group/split assignment.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/views-filters-candidates.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p3-views-filters-candidates`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p3-views-filters-candidates`
- Base branch: `develop`
- Head branch: `agent/stage-5-p3-views-filters-candidates`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: scan results become descriptor views; views become provisional index candidates.
- Units/shapes/dtypes: candidate windows are field-native `FieldIndex` values only.
- Sampling/alignment/provenance: candidates preserve record/source provenance and do not infer alignment or seconds semantics.
- Pipeline-order implications: record filters happen before candidate construction; candidate filters happen before group/split.
- Leakage or subject/split implications: no group or split assignment is added.
- Legacy parity or intentional behavior changes: `IndexItem` remains pure and identity-free.

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

Candidate IDs are provisional and use record IDs until Phase 5 sidecar entries define durable identity. Group/split assignment remains deferred to Phase 4.

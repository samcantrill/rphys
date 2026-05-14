# Summary

Adds the Stage 5 datasource submodule homes and package-level boundary tests required before functional datasource behavior lands. The modules are importable and dependency-light, but expose no public objects until later phases implement backed behavior.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/public-boundary-errors-fixtures.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p1-public-boundary-errors-fixtures`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p1-public-boundary-errors-fixtures`
- Base branch: `develop`
- Head branch: `agent/stage-5-p1-public-boundary-errors-fixtures`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: no runtime datasource inputs or outputs are introduced.
- Units/shapes/dtypes: unchanged.
- Sampling/alignment/provenance: unchanged; descriptor semantics are not modified.
- Pipeline-order implications: module homes only; scan/filter/split/index behavior remains in later phases.
- Leakage or subject/split implications: unchanged.
- Legacy parity or intentional behavior changes: parent and root public exports stay conservative by design.

# Verification

- [x] Package/API tests
- [ ] Unit tests
- [ ] Contract tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
make test-package
git diff --check
```

# Risks And Follow-Up

Functional adapter, validation, filter, split, index, manifest, and composite APIs remain intentionally deferred to later Stage 5 phases. Concrete Stage 5 errors are also deferred until paired with public behavior that raises them.

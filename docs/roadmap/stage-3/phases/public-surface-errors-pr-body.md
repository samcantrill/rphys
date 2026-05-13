# Summary

Implements Stage 3 Phase 1 by tightening public-surface and diagnostics
guardrails before descriptor behavior lands. `rphys.io` and
`rphys.datasources` remain lightweight package homes with empty public
surfaces, root `rphys` still exports nothing, and Stage 3 descriptor names and
concrete descriptor errors remain deferred until code-backed phases introduce
them.

# Links

- Roadmap stage: `docs/roadmap/stage-3/planning.md`
- Phase plan: `docs/roadmap/stage-3/phases/public-surface-errors.md`
- Implementation plan: `docs/roadmap/stage-3/implementation-plan.md`
- Scientific review: no scientific operation introduced; scope is import and diagnostics guardrails only

# Phase Isolation

- Branch: `agent/stage-3-p1-public-surface-errors`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p1-public-surface-errors`
- Base branch: `develop`
- Head branch: `agent/stage-3-p1-public-surface-errors`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: no domain inputs or outputs added
- Units/shapes/dtypes: not applicable
- Sampling/alignment/provenance: no slice, field-view, datasource, or provenance behavior introduced
- Pipeline-order implications: none
- Leakage or subject/split implications: none
- Legacy parity or intentional behavior changes: package docstrings now explicitly avoid promising deferred codec, builder, registry, datasource scanning, manifest, or runtime hooks

# Verification

- [x] Package/API tests
- [x] Unit tests
- [ ] Contract tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
make test-package
make test-unit
git diff --check
```

# Risks And Follow-Up

Phase 2 through Phase 4 must update the deferred-name guardrails as they add
code-backed descriptor exports and concrete errors. This phase intentionally
adds no descriptor modules, descriptor serialization, root exports, codec
hooks, datasource scanning, builders, manifests, or runtime sample behavior.

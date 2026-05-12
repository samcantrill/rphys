# Summary

Implements Stage 0 Phase 2 by adding executable package governance guardrails.
The new package tests check lightweight import side effects, runtime dependency
emptiness, private/no-license metadata, all-rights-reserved license status, and
absence of generic workflow/artifact runtime packages.

# Links

- Roadmap stage: `docs/roadmap/stage-0/planning.md`
- Phase plan: `docs/roadmap/stage-0/phases/governance-guardrails.md`
- Implementation plan: `docs/roadmap/stage-0/implementation-plan.md`
- Scientific review: no scientific operation introduced

# Scientific Contract

- Inputs/outputs: no domain inputs or outputs added
- Units/shapes/dtypes: not applicable
- Sampling/alignment/provenance: not applicable
- Pipeline-order implications: none
- Leakage or subject/split implications: none
- Legacy parity or intentional behavior changes: governance tests protect the Stage 0 import and metadata baseline

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
uv lock --check
git diff --check
```

# Risks And Follow-Up

Metadata assertions will need deliberate updates if the repository selects a
public license, adds runtime dependencies, or introduces optional dependency
groups in a later roadmap phase.

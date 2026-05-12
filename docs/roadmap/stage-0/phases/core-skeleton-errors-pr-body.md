# Summary

Implements Stage 0 Phase 1 by adding the importable package skeleton and broad
base error hierarchy described in `docs/roadmap/stage-0/implementation-plan.md`.
The root package remains lightweight with an empty public surface; planned
package homes expose empty `__all__`; `rphys.errors` owns the broad public error
classes.

# Links

- Roadmap stage: `docs/roadmap/stage-0/planning.md`
- Phase plan: `docs/roadmap/stage-0/phases/core-skeleton-errors.md`
- Implementation plan: `docs/roadmap/stage-0/implementation-plan.md`
- Scientific review: no scientific operation introduced

# Scientific Contract

- Inputs/outputs: no domain inputs or outputs added
- Units/shapes/dtypes: not applicable
- Sampling/alignment/provenance: not applicable
- Pipeline-order implications: none
- Leakage or subject/split implications: none
- Legacy parity or intentional behavior changes: establishes new Stage 0 skeleton and error base classes

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

Visible empty package homes and broad error class names create mild public
compatibility expectations. This is accepted by the approved implementation
plan and mitigated by empty `__all__`, concise package docstrings, and no domain
behavior.

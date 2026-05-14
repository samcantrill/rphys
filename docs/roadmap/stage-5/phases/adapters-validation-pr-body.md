# Summary

Implements the Stage 5 descriptor-only datasource discovery and validation foundation. The new public names live in `rphys.datasources.adapters` and `rphys.datasources.validation`, while the parent `rphys.datasources` export surface remains unchanged.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/adapters-validation.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p2-adapters-validation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p2-adapters-validation`
- Base branch: `develop`
- Head branch: `agent/stage-5-p2-adapters-validation`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adapters scan `DataSourceSpec` into descriptor-only `DataSourceScanResult`; validation emits `DataSourceValidationReport`.
- Units/shapes/dtypes: no payload arrays or runtime sample values are introduced.
- Sampling/alignment/provenance: datasource and record refs are preserved without mutation; no temporal alignment is inferred.
- Pipeline-order implications: scan and validation precede views, filters, candidates, groups, splits, and indexes.
- Leakage or subject/split implications: validation can require metadata but does not assign groups or splits.
- Legacy parity or intentional behavior changes: new Stage 5 errors are added only for implemented scan/validation behavior.

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

Validation issue codes are intentionally provisional strings. Views, filters, candidates, group/split assignment, index finalization, manifests, and composites remain deferred to later Stage 5 phases.

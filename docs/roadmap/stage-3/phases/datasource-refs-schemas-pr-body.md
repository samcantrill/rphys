# Summary

Implements Stage 3 Phase 3 by adding dependency-free datasource descriptors:
`DataSourceRef`, `RecordRef`, and `DataSourceSchema`. The descriptors preserve
datasource identity, record identity, non-empty field presence, declaration-only
schema information, and primitive metadata while staying free of scans,
filters, builders, validation reports, manifests, fingerprints, and stable
datasource-index identity.

# Links

- Roadmap stage: `docs/roadmap/stage-3/planning.md`
- Phase plan: `docs/roadmap/stage-3/phases/datasource-refs-schemas.md`
- Implementation plan: `docs/roadmap/stage-3/implementation-plan.md`
- Scientific review: provenance/leakage metadata scope and declaration-only schema behavior are covered in unit and contract tests

# Phase Isolation

- Branch: `agent/stage-3-p3-datasource-refs-schemas`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p3-datasource-refs-schemas`
- Base branch: `develop`
- Head branch: `agent/stage-3-p3-datasource-refs-schemas`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adds descriptor objects only; no datasource scans, payload validation, or runtime samples
- Units/shapes/dtypes: `DataSourceSchema` reuses `FieldSpec` declarations without observed payload facts, shapes, units, or dtype validation
- Sampling/alignment/provenance: `RecordRef.fields` preserves intrinsic field presence; leakage-sensitive source/subject/split/group context remains metadata
- Pipeline-order implications: none; no loading, filtering, grouping, split building, validation reports, transforms, or aggregation
- Leakage or subject/split implications: subject, split, group, and source identifiers remain metadata keys rather than first-class constructor fields
- Legacy parity or intentional behavior changes: `rphys.datasources` now exports code-backed refs/schema names while `IndexItem` remains deferred

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

Metadata-only leakage provenance is less discoverable than first-class fields,
but it matches the approved Stage 3 scope. Phase 4 owns `IndexItem`; later
datasource stages own scans, filters, validation reports, manifests,
fingerprints, expected-versus-observed evidence, and stable item identity.

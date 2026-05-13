# Summary

Implements Stage 3 Phase 4 by adding `IndexItem`, the role-qualified lazy IO
item consumed later by sample builders. `IndexItem` stores a non-empty
`FieldLocator -> FieldView` mapping, mandatory `RecordRef` provenance,
primitive metadata, locator/view key consistency checks, and record field
membership checks.

# Links

- Roadmap stage: `docs/roadmap/stage-3/planning.md`
- Phase plan: `docs/roadmap/stage-3/phases/index-item-composition.md`
- Implementation plan: `docs/roadmap/stage-3/implementation-plan.md`
- Scientific review: role/identity separation, record provenance, per-field index independence, and no-runtime-sample behavior are covered in unit and contract tests

# Phase Isolation

- Branch: `agent/stage-3-p4-index-item-composition`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p4-index-item-composition`
- Base branch: `develop`
- Head branch: `agent/stage-3-p4-index-item-composition`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adds descriptor objects only; no payload IO or runtime samples
- Units/shapes/dtypes: no shape, dtype, unit, codec, or backend payload semantics
- Sampling/alignment/provenance: each `FieldView` index remains field-native; equal numeric indexes across roles do not imply alignment; mandatory `RecordRef` preserves provenance
- Pipeline-order implications: none; no loading, filtering, transforms, augmentation, export, training, or aggregation
- Leakage or subject/split implications: leakage context remains in `RecordRef` metadata and survives item composition
- Legacy parity or intentional behavior changes: `rphys.datasources` now exports code-backed `IndexItem`; root `rphys` still exports nothing

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

Manual examples remain verbose because record provenance is mandatory. Later
stages own `SampleBuilder`, runtime samples, transforms, augmentations, export,
training, datasource indexes, manifests, fingerprints, `item_id`, and
multi-member or nested item behavior.

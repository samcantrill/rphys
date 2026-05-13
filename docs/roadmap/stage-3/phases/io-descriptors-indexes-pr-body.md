# Summary

Implements Stage 3 Phase 2 by adding dependency-free lazy IO descriptors:
`ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, and
`FieldView`. The descriptors are immutable value objects, copy primitive
metadata/options, serialize through explicit primitive dictionaries, and fail
loudly for invalid construction or unsupported serialized index tags.

# Links

- Roadmap stage: `docs/roadmap/stage-3/planning.md`
- Phase plan: `docs/roadmap/stage-3/phases/io-descriptors-indexes.md`
- Implementation plan: `docs/roadmap/stage-3/implementation-plan.md`
- Scientific review: field-native temporal semantics and no-alignment posture are covered in unit and contract tests

# Phase Isolation

- Branch: `agent/stage-3-p2-io-descriptors-indexes`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p2-io-descriptors-indexes`
- Base branch: `develop`
- Head branch: `agent/stage-3-p2-io-descriptors-indexes`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: adds descriptor objects only; no payload IO or runtime samples
- Units/shapes/dtypes: no shape, dtype, unit, codec, or backend payload semantics
- Sampling/alignment/provenance: `TemporalIndexSlice` stores half-open field-native integer offsets; equal numeric slices across fields do not imply alignment, resampling, padding, or seconds conversion
- Pipeline-order implications: none; no loading, filtering, normalization, transforms, or aggregation
- Leakage or subject/split implications: metadata is primitive and descriptive only; datasource provenance is deferred to Phase 3
- Legacy parity or intentional behavior changes: `rphys.io` now exports code-backed Stage 3 descriptor names while root `rphys` still exports nothing

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

Primitive serialization key spelling is now a compatibility surface. Stage 3
reconstructs only the supported `temporal_index_slice` tag; later seconds,
spatial, custom index, manifest, fingerprint, or stable identity behavior must
be added by later roadmap stages without mutating these descriptor contracts.
Phase 3 owns datasource refs and schema descriptors.

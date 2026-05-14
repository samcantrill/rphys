# Summary

Closes Stage 5 with documentation and integration hardening. This updates datasource index docstrings to reflect final sidecar/manifest/composite responsibilities and adds a synthetic vertical slice covering scan, validation, view/filter, candidate/filter, group/split, index, manifest, composite, and `SampleBuilder`.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/docs-integration-hardening.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p8-docs-integration-hardening`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p8-docs-integration-hardening`
- Base branch: `develop`
- Head branch: `agent/stage-5-p8-docs-integration-hardening`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: Stage 5 descriptors compose from scan results through loaded composite indexes while still yielding pure `IndexItem`s for `SampleBuilder`.
- Units/shapes/dtypes: field-native `TemporalIndexSlice` windows are preserved; payloads remain lazy until the sample field is required.
- Sampling/alignment/provenance: split/group/source/child/global/local provenance stays inspectable on sidecar entries and manifests.
- Pipeline-order implications: filtering happens before candidate construction and candidate filtering happens before group/split/index finalization.
- Leakage or subject/split implications: group-disjoint split assignment remains explicit and visible in entries.
- Legacy parity or intentional behavior changes: public synthetic helpers, `ConcatDataSourceIndex`, cache/export/training/runtime ownership, and seconds/spatial/alignment semantics remain deferred.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [ ] E2E tests
- [ ] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
make test-unit
make test-contract
make test-integration
make test-package
git diff --check
make validate-pr
```

# Risks And Follow-Up

Stage 5 remains intentionally descriptor-only. Real datasource SDK adapters, cache/export/materialization, Torch loaders, operations, training/evaluation workflow behavior, path normalization, and a possible concat alias/class are future-stage work.

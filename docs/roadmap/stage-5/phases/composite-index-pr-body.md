# Summary

Implements the single public Stage 5 combined-index type, `CompositeDataSourceIndex`. It provides ordered flat access over child `DataSourceIndex` objects while preserving source key, child index ID, child index fingerprint, child entry ID, child local position, global position, and child metadata in sidecar entries and manifests.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/composite-index.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: DQ-8 locked composite-only combined indexes on 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p7-composite-index`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p7-composite-index`
- Base branch: `develop`
- Head branch: `agent/stage-5-p7-composite-index`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `CompositeDataSourceIndex` composes child `DataSourceIndex` objects and still yields pure `IndexItem`s.
- Units/shapes/dtypes: item descriptors are unchanged; no payloads are loaded or materialized.
- Sampling/alignment/provenance: source/child/global/local provenance lives in `DataSourceIndexEntry` sidecars and manifest child descriptors.
- Pipeline-order implications: composition follows index construction and manifest support; samplers, loaders, cache, and batch planning remain later-stage responsibilities.
- Leakage or subject/split implications: split/group/source identity remains inspectable per entry and is not hidden in item metadata.
- Legacy parity or intentional behavior changes: `ConcatDataSourceIndex` remains intentionally absent from the public API.

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

Downstream users may ask for a concat name later. That should remain additive only if real usage shows it is worth the public API surface; Stage 5 keeps the composite-only source-aware contract.

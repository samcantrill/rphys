# Summary

Implements the datasource-index manifest codec with schema `rphys.datasource_index.v1`, canonical JSON serialization, exact item/entry preservation, content fingerprints, full-manifest checksums, and rejection paths for unsupported or corrupted manifests.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/index-manifest-codec.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p6-index-manifest-codec`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p6-index-manifest-codec`
- Base branch: `develop`
- Head branch: `agent/stage-5-p6-index-manifest-codec`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `DataSourceIndex` objects serialize to validated JSON manifests and reload to equivalent lazy indexes.
- Units/shapes/dtypes: descriptor dictionaries are preserved exactly; no payload values are persisted.
- Sampling/alignment/provenance: split/group/window/source provenance stays on sidecar entries.
- Pipeline-order implications: persistence follows final index construction and precedes composite manifests.
- Leakage or subject/split implications: split/group provenance is durable and inspectable.
- Legacy parity or intentional behavior changes: pickle and path normalization are intentionally not implemented.

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

This is the initial durable schema; migrations, cache/export manifests, and path normalization remain deferred.

# Summary

Implements `DataSourceIndex` construction from selected candidates. The index yields pure `IndexItem`s, while `DataSourceIndexEntry` sidecars carry stable position, identity, split/group/window/source provenance, and deterministic fingerprints.

# Links

- Roadmap stage: `docs/roadmap/stage-5/planning.md`
- Phase plan: `docs/roadmap/stage-5/phases/datasource-index-entries.md`
- Implementation plan: `docs/roadmap/stage-5/implementation-plan.md`
- Scientific review: Stage 5 implementation-plan quality gate passed 2026-05-14

# Phase Isolation

- Branch: `agent/stage-5-p5-datasource-index-entries`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-5-p5-datasource-index-entries`
- Base branch: `develop`
- Head branch: `agent/stage-5-p5-datasource-index-entries`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: selected candidates become ordered indexes yielding `IndexItem`s plus sidecar entries.
- Units/shapes/dtypes: field-native windows are recorded from `FieldIndex` descriptors only.
- Sampling/alignment/provenance: no seconds or alignment inference; entry provenance remains inspectable.
- Pipeline-order implications: this finalizes candidates after group/split assignment and before manifests.
- Leakage or subject/split implications: split/group data is copied from Phase 4 assignments into entries.
- Legacy parity or intentional behavior changes: `IndexItem.metadata` remains identity-free.

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
```

# Risks And Follow-Up

Entry fingerprints are deterministic sidecar fingerprints; Phase 6 owns durable manifest schema and manifest checksum behavior.

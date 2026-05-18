# Summary

Implements Stage 14 Phase 3 by composing one deterministic upstream smoke flow
through public Stage 5-12 APIs and documenting that debug, smoke, and signal
tiers differ by validation breadth, not fixture semantics.

# Links

- Roadmap stage: `docs/roadmap/stage-14/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-14/phases/upstream-smoke-validation-tiers.md`
- Implementation plan: `docs/roadmap/stage-14/implementation-plan.md`
- Scientific review: Stage 14 design review in `docs/roadmap/stage-14/implementation-plan.md`

# Phase Isolation

- Branch: `agent/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
- Base branch: `develop`
- Head branch: `agent/stage-14-synthetic-smoke-hardening-p3-upstream-smoke-validation-tiers`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: generated synthetic datasource descriptors, scan validation
  reports, group/split sidecars, datasource index manifests, lazy samples,
  LIST-collated batches, Batch-returning method predictions, and Stage 8
  export/derived datasource reload.
- Units/shapes/dtypes: the smoke slices BVP and timestamp evidence to a tiny
  deterministic temporal window while preserving `signal.bvp.v1` schemas and
  role-qualified field locators.
- Sampling/alignment/provenance: sample-rate, timestamp, subject/group/split,
  record provenance, manifest schema version, and derived reload evidence stay
  inspectable through public objects.
- Pipeline-order implications: scan, validation, grouping, splitting, indexing,
  sample building, sample operations, collation, method prediction, export, and
  reload are exercised in order through the same public loader path.
- Leakage or subject/split implications: subject-level group/split evidence is
  preserved; no global statistics, real data, external IO, network, GPU, or
  heavy optional dependency is introduced.
- Legacy parity or intentional behavior changes: this is test/documentation
  coverage only; no public `rphys` API changes.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests
- [x] Acceptance or opt-in checks, if applicable
- [x] Scientific/workflow contract review completed

Commands run:

```text
uv run pytest tests/integration/test_stage14_upstream_smoke_flow.py
make test-integration
make test
make validate-pr
make test-summary
git diff --check
```

The clean summary reported package 72 passed, unit 752 passed, contract 174
passed, integration 29 passed, e2e not present, and acceptance not present.

# Risks And Follow-Up

This phase deliberately stops before the Stage 13 scan-to-report tail. Phase 4
must complete that tail using the real code-backed Stage 13 APIs and must not
retrofit this upstream smoke with a fake report path or alternate loader.

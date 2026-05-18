# Summary

Implements Stage 14 Phase 2 by adding private contract assertion helpers,
a narrow public datasource-index manifest fingerprint golden, consuming
contract coverage, and package/import guardrails that keep Stage 14 support
private.

# Links

- Roadmap stage: `docs/roadmap/stage-14/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-14/phases/contract-boundaries-goldens.md`
- Implementation plan: `docs/roadmap/stage-14/implementation-plan.md`
- Scientific review: Stage 14 design review in `docs/roadmap/stage-14/implementation-plan.md`

# Phase Isolation

- Branch: `agent/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
- Base branch: `develop`
- Head branch: `agent/stage-14-synthetic-smoke-hardening-p2-contract-boundaries-goldens`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: public `RecordRef`, scan validation reports,
  datasource-index manifests, and lazy `SampleBuilder` materialization from the
  Phase 1 synthetic catalog.
- Units/shapes/dtypes: helper assertions preserve sample-rate, timestamp,
  waveform, alignment, schema, payload-fingerprint, and provenance facts
  without loading arrays into durable manifests.
- Sampling/alignment/provenance: manifest and sample assertions check field
  windows, record identity, subject/group/split sidecars, and lazy field
  materialization.
- Pipeline-order implications: public construction remains visible in the
  contract test; helpers only assert repeated invariants.
- Leakage or subject/split implications: package checks prevent private
  fixture helpers from becoming public import surfaces.
- Legacy parity or intentional behavior changes: no public `rphys` API changes.

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
uv run pytest tests/contracts/test_synthetic_contract_assertions.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
make test-integration
make validate-pr
make test-summary
git diff --check
```

`make test-summary` was rerun alone after an artifact-write collision with the
parallel `validate-pr` run. The clean summary reported package 72 passed, unit
752 passed, contract 174 passed, integration 28 passed, e2e not present, and
acceptance not present.

# Risks And Follow-Up

Phase 3 can use these private assertions and manifest checks for upstream
smoke composition, but should not turn them into a support runner. Phase 4
still owns the Stage 13 scan-to-report tail.

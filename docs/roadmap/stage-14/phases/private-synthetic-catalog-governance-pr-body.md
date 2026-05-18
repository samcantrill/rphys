# Summary

Implements Stage 14 Phase 1 by adding a private deterministic synthetic
fixture catalog, named scientific edge variants, and first consuming tests that
exercise public descriptor, validation, index, and sample-builder paths. The
support remains under `tests/support` and does not add public fixture APIs.

# Links

- Roadmap stage: `docs/roadmap/stage-14/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-14/phases/private-synthetic-catalog-governance.md`
- Implementation plan: `docs/roadmap/stage-14/implementation-plan.md`
- Scientific review: Stage 14 design review in `docs/roadmap/stage-14/implementation-plan.md`

# Phase Isolation

- Branch: `agent/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
- Base branch: `develop`
- Head branch: `agent/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: deterministic descriptor-only datasources, records, fields,
  URI resources, scan results, index items, and sample-builder payloads for
  video, BVP, timestamps, and optional mask/quality/landmark/sidecar fields.
- Units/shapes/dtypes: primitive tuple payloads only; sample rates,
  timestamps, waveform frequency/phase/amplitude, heart-rate evidence, sample
  counts, and payload fingerprints are recorded in fixture evidence.
- Sampling/alignment/provenance: positive fixtures record video/BVP/timestamp
  alignment, split/group/subject/source metadata, and public sample provenance.
  Edge variants preserve missing, short, flat, NaN, inf, invalid-rate, drift,
  irregular-timestamp, and misalignment evidence without support-layer repair.
- Pipeline-order implications: first consumers prove public scan validation,
  grouping/splitting, index construction, and lazy sample materialization from
  the private catalog.
- Leakage or subject/split implications: generated subjects carry stable group
  and split metadata for later leakage-aware consumers.
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
uv run pytest tests/contracts/test_synthetic_catalog_contract.py
uv run pytest tests/integration/test_synthetic_catalog_flow.py
make test-package
make test-contract
make test-integration
make validate-pr
make test-summary
git diff --check
```

`make test-summary` reported package 71 passed, unit 752 passed, contract 173
passed, integration 28 passed, e2e not present, and acceptance not present.

# Risks And Follow-Up

Phase 2 should decide which repeated invariants deserve private assertion
helpers and which durable manifests merit narrow goldens. Phase 3 and Phase 4
must still avoid treating this fixture catalog as a smoke runner or Stage 13
tail substitute.

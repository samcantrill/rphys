# Summary

Implements Stage 4 Phase 1, the codec public contract foundation. This PR adds
`rphys.io.codecs` as the canonical dependency-light home for structural codec
typing, operation capability declarations, datasource-neutral load/save
contexts, codec operation result records, and the narrow save metadata policy.

The implementation intentionally keeps codec contract names out of
package-level `rphys.io.__all__` after contract validation confirmed that names
with `probe`/`load`/`save` behavior should remain in the owning
`rphys.io.codecs` module. Root `rphys` exports are unchanged.

# Links

- Roadmap stage: `docs/roadmap/stage-4/planning.md`
- Phase plan: `docs/roadmap/stage-4/phases/codec-contract-foundation.md`
- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Scientific review: Stage 4 plan quality gate in `docs/roadmap/stage-4/implementation-plan.md`

# Phase Isolation

- Branch: `agent/codecs-lazy-samples-p1-codec-contract-foundation`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p1-codec-contract-foundation`
- Base branch: `develop`
- Head branch: `agent/codecs-lazy-samples-p1-codec-contract-foundation`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: codec contexts and results carry Stage 2/3 descriptors and
  values only: `FieldView`, `FieldRef`, `FieldSpec`, `FieldValue`, and
  `ResourceRef`.
- Units/shapes/dtypes: no payload transformation, dtype conversion, shape
  inference, sampling-rate conversion, or unit reinterpretation is introduced.
- Sampling/alignment/provenance: `LoadContext` preserves any existing
  `FieldView.field_index` descriptor by reference; `SaveContext.target` is a
  logical `FieldRef`; datasource record provenance remains out of IO contexts.
- Pipeline-order implications: no registry dispatch, codec execution,
  fallback loading, cache policy, sample building, or export orchestration is
  implemented.
- Leakage or subject/split implications: no subject, split, grouping, record,
  or dataset partition semantics are added.
- Legacy parity or intentional behavior changes: Stage 3 descriptor behavior is
  preserved; the new contract records are additive and canonical under
  `rphys.io.codecs`.

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
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/io/test_codecs.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/test_errors.py
make test-contract
make test-package
make test-unit
make validate-pr
git diff --check
```

`make validate-pr` passed with package 19, unit 271, contract 25, integration
1, e2e/acceptance not present, build success, lock check success, and clean
`git diff --check`.

# Risks And Follow-Up

Registry resolution, synthetic codec operation behavior, lazy `SampleField`,
and `SampleBuilder` construction are intentionally left to later Stage 4
phases. The main residual risk is that real codecs may motivate additive
context/result fields later; this PR keeps the contract narrow so those
additions remain evidence-driven.

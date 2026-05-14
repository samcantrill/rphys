# Summary

Implements Stage 4 Phase 2, explicit registry and synthetic codec operations.
This PR extends `rphys.io.codecs` with an instance-local `CodecRegistry` that
resolves exactly one structural codec per probe/load/save operation, validates
operation result types, honors declared save metadata policies, and fails
loudly for missing, ambiguous, unsupported, invalid, dependency-unavailable,
and unsupported-index cases.

The operation proof uses a private test-support `SyntheticCodec`; it is not
exported from package code. Root `rphys` and package-level `rphys.io` exports
remain unchanged.

# Links

- Roadmap stage: `docs/roadmap/stage-4/planning.md`
- Phase plan: `docs/roadmap/stage-4/phases/codec-registry-synthetic-ops.md`
- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Scientific review: Stage 4 plan quality gate in `docs/roadmap/stage-4/implementation-plan.md`

# Phase Isolation

- Branch: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Base branch: `develop`
- Head branch: `agent/codecs-lazy-samples-p2-codec-registry-synthetic-ops`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: probe/load use `LoadContext(FieldView)`; save uses
  `FieldValue` plus `SaveContext(target: FieldRef)` and returns typed codec
  results.
- Units/shapes/dtypes: no real payload format, dtype conversion, shape
  inference, unit interpretation, or sampling-rate conversion is introduced.
- Sampling/alignment/provenance: field indexes remain field-native integer
  descriptors. Unsupported indexes fail through typed slice/codec errors
  without hidden full-resource fallback. Ordered resources are preserved
  without member or alignment semantics.
- Pipeline-order implications: no global registry, plugin discovery, cache,
  sample field, sample builder, datasource scan, metadata manifest, or export
  orchestration is added.
- Leakage or subject/split implications: no subject, split, group, record, or
  dataset partition semantics are interpreted by codecs or registries.
- Legacy parity or intentional behavior changes: descriptor purity is
  preserved; new behavior is additive under `rphys.io.codecs`.

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
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/io/test_codec_registry.py tests/unit/rphys/io/test_codecs.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_codec_contract.py tests/contracts/test_lazy_io_contract.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py tests/unit/rphys/test_errors.py
make test-package
make test-unit
make test-contract
make validate-pr
git diff --check
```

`make validate-pr` passed with package 19, unit 285, contract 30, integration
1, e2e/acceptance not present, build success, lock check success, and clean
`git diff --check`.

# Risks And Follow-Up

Registry matching is still proven with private synthetic codecs only. Real
codec families may later motivate additive support predicates or resource
member semantics, but symbolic names, plugin discovery, concrete production
codecs, lazy `SampleField`, and `SampleBuilder` construction remain deferred
to later phases.

# Summary

Implements Stage 4 Phase 3, lazy `SampleField` runtime compatibility. This PR
adds `rphys.data.sample_fields.SampleField` and `SampleFieldState` as the
canonical lazy runtime field surface while preserving loaded `Sample`
semantics.

`SampleField` subclasses `FieldValue`, so existing containers store the lazy
handle as the field object, not as a payload wrapper. `Sample.field()`,
`role()`, and `field_items()` return handles without loading. Payload-demanding
paths such as `.payload`, `Sample.get()`, `Sample.require()`, expected-type
validation, and LIST collation materialize through the retained loader exactly
once.

# Links

- Roadmap stage: `docs/roadmap/stage-4/planning.md`
- Phase plan: `docs/roadmap/stage-4/phases/lazy-sample-field-runtime.md`
- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Scientific review: Stage 4 plan quality gate in `docs/roadmap/stage-4/implementation-plan.md`

# Phase Isolation

- Branch: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Base branch: `develop`
- Head branch: `agent/codecs-lazy-samples-p3-lazy-sample-field-runtime`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `SampleField` retains a datasource-neutral `LoadContext` and
  returns the retained `CodecLoadResult`/`FieldValue` from the loader.
- Units/shapes/dtypes: no payload conversion, dtype inference, shape
  validation, unit interpretation, or sampling-rate conversion is introduced.
- Sampling/alignment/provenance: the original `FieldView` and optional
  field-native index remain inspectable through `load_context`; no alignment,
  seconds slicing, member binding, or datasource record semantics are added.
- Pipeline-order implications: no `SampleBuilder`, eager sample build path,
  cache/retry/reset policy, async loading, datasource scan, or collation
  redesign is implemented.
- Leakage or subject/split implications: no subject, split, group, record, or
  dataset partition semantics are interpreted by lazy fields.
- Legacy parity or intentional behavior changes: loaded `FieldValue` behavior
  remains intact; lazy handles are additive and canonical under
  `rphys.data.sample_fields`, not package-level `rphys.data`.

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
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_sample_fields.py tests/unit/rphys/data/test_containers.py tests/unit/rphys/data/test_collation.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/contracts/test_lazy_sample_field_contract.py tests/contracts/test_runtime_core_contract.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-unit
make test-contract
make validate-pr
git diff --check origin/develop...HEAD
```

`make validate-pr` passed with package 21, unit 298, contract 33, integration
1, e2e/acceptance not present, build success, lock check success, and clean
`git diff --check`. PR-range `git diff --check origin/develop...HEAD` also
passed.

# Risks And Follow-Up

Phase 4 still owns `SampleBuilder`, datasource provenance joining, requested
locator selection, and eager sample construction. `SampleField` intentionally
does not add retry/reset/cache policy, async behavior, public loader handler
interfaces, or a parallel `LazySample` container.

# Summary

Adds the public runtime `FieldContainer` protocol and stable `field_items()`
iteration surface needed before Stage 4 introduces lazy sample fields. `Sample`
and `Batch` now expose public field iteration, `SampleContract` validates the
public container shape, LIST collation consumes the public protocol rather than
the private `_field_items()` hook, and `FieldContainer` is intentionally exported
from `rphys.data`.

The change preserves loaded `Sample` and `Batch` accessor semantics. It does
not introduce codecs, lazy payload loading, `SampleField`, `SampleBuilder`,
datasource behavior, new collation policies, or root-package exports.

# Links

- Roadmap stage: `docs/roadmap/stage-4/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-4/phases/field-container-protocol.md`
- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Scientific review: recorded in the phase plan completion and pre-submit notes

# Phase Isolation

- Branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
- Worktree: `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep1-field-container-protocol`
- Base branch: `develop`
- Head branch: `agent/codecs-lazy-samples-prep1-field-container-protocol`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: runtime field containers continue to expose `FieldLocator` to
  `FieldValue` mappings; `field_items()` returns an insertion-ordered tuple
  snapshot of `(FieldLocator, FieldValue)` pairs.
- Units/shapes/dtypes: unchanged. Payload units, shapes, dtypes, schemas, and
  metadata remain stored on `FieldValue` and are not reinterpreted.
- Sampling/alignment/provenance: unchanged. No sampling-rate, timestamp,
  alignment, slicing, datasource, subject, split, or provenance semantics are
  added.
- Pipeline-order implications: unchanged. LIST collation keeps the existing
  field-set, schema, policy, payload list, and sparse metadata behavior while
  reading fields through the public protocol.
- Leakage or subject/split implications: none. This phase does not touch
  datasource records, splits, identities, grouping, builders, or loaders.
- Legacy parity or intentional behavior changes: loaded `Sample` and `Batch`
  accessors keep existing behavior. The intentional public API addition is
  `FieldContainer` plus `field_items()`; `_field_items()` remains only as a
  private compatibility alias.

# Verification

- [x] Package/API tests
- [x] Unit tests
- [x] Contract tests
- [x] Integration tests
- [x] E2E tests: not present for this repository yet
- [x] Acceptance or opt-in checks, if applicable: not present for this phase
- [x] Scientific/workflow contract review completed

Commands run:

```text
uv run pytest tests/unit/rphys/data/test_containers.py tests/unit/rphys/data/test_contracts.py tests/unit/rphys/data/test_collation.py
uv run pytest tests/contracts/test_runtime_core_contract.py tests/package/test_import.py tests/package/test_import_boundaries.py
make test-contract
make test-package
make test-unit
git diff --check
make validate-pr
```

Latest `make validate-pr` summary:

| Suite | Status | Passed | Failed | Errors | Skipped | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| package | passed | 18 | 0 | 0 | 0 | 18 |
| unit | passed | 256 | 0 | 0 | 0 | 256 |
| contract | passed | 25 | 0 | 0 | 0 | 25 |
| integration | passed | 1 | 0 | 0 | 0 | 1 |
| e2e | not present | 0 | 0 | 0 | 0 | 0 |
| acceptance | not present | 0 | 0 | 0 | 0 | 0 |
| Overall | passed | 300 | 0 | 0 | 0 | 300 |

# Risks And Follow-Up

- Primary Stage 4 lazy-field work may widen compatible annotations
  additively, but should preserve the public method names introduced here.
- `_field_items()` remains as a private compatibility alias and should not be
  treated as public API.
- Future phases remain responsible for codecs, lazy field state, sample
  builders, datasource provenance, and any broader collation behavior.

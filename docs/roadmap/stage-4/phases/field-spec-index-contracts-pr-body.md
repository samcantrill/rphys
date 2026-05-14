# Summary

Tightens the Stage 2/3 descriptor contracts that Stage 4 codec and lazy sample
work will depend on.

- Freezes `FieldSpec` as a slotted value object while preserving constructor
  coercion, value equality, copy/deepcopy behavior, and the narrow
  `key`/`data_type`/`schema` contract.
- Keeps `FieldSpec` explicitly unhashable so freezing does not create an
  unapproved cache-key or fingerprint contract.
- Proves `DataSourceSchema.fields` can safely keep direct `FieldSpec`
  declarations because the stored declaration objects can no longer be mutated
  through the schema mapping.
- Updates `FieldIndex` terminology from protocol to base class while preserving
  the existing nominal, no-registry, no-factory index boundary.

# Links

- Roadmap stage: `docs/roadmap/stage-4/implementation-plan.md`
- Phase plan: `docs/roadmap/stage-4/phases/field-spec-index-contracts.md`
- Implementation plan: `docs/roadmap/stage-4/implementation-plan.md`
- Scientific review: phase pre-submit blocker gate recorded in
  `docs/roadmap/stage-4/phases/field-spec-index-contracts.md`

# Phase Isolation

- Branch: `agent/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Worktree:
  `/home/samcantrill/work/rphys-worktrees/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Base branch: `develop`
- Head branch: `agent/codecs-lazy-samples-prep2-field-spec-index-contracts`
- Scope statement: this PR contains one roadmap implementation phase only.

# Scientific Contract

- Inputs/outputs: `FieldSpec(key, data_type, schema=None)` keeps the same
  constructor shape and vocabulary coercion. `DataSourceSchema` still exposes a
  declaration-only field mapping. `FieldIndex` remains a base class for
  implemented field-native index descriptors.
- Units/shapes/dtypes: no payload units, shapes, dtypes, sample rates, masks,
  schema evidence, or rich field facts are introduced.
- Sampling/alignment/provenance: `TemporalIndexSlice` remains the only
  supported Stage 3 index descriptor and still represents field-native integer
  `[start, stop)` slices. Equal numeric slices across fields still do not imply
  temporal alignment, resampling, padding, or seconds conversion.
- Pipeline-order implications: no codec, load/save, builder, collation,
  filtering, normalization, aggregation, or runtime materialization behavior is
  added.
- Leakage or subject/split implications: no subject, split, group, record, or
  leakage semantics change.
- Legacy parity or intentional behavior changes: intentional tightening is that
  post-construction assignment to `FieldSpec.key`, `FieldSpec.data_type`, or
  `FieldSpec.schema` now fails. Public hashability remains absent, and index
  registry/factory behavior remains absent.

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
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit/rphys/data/test_fields.py tests/unit/rphys/datasources/test_datasource_schemas.py tests/unit/rphys/io/test_indexes.py
make test-unit
make test-contract
make test-package
git diff --check
make validate-pr
```

Latest `make validate-pr` evidence from `build/test-summary.md`:

| Suite | Status | Passed | Failed | Errors | Skipped | Deselected | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| package | passed | 18 | 0 | 0 | 0 | 0 | 18 |
| unit | passed | 259 | 0 | 0 | 0 | 0 | 259 |
| contract | passed | 25 | 0 | 0 | 0 | 0 | 25 |
| integration | passed | 1 | 0 | 0 | 0 | 0 | 1 |
| e2e | not present | 0 | 0 | 0 | 0 | 0 | 0 |
| acceptance | not present | 0 | 0 | 0 | 0 | 0 | 0 |
| Overall | passed | 303 | 0 | 0 | 0 | 0 | 303 |

# Risks And Follow-Up

- Downstream scratch code that mutates `FieldSpec` after construction will now
  fail; this is the intended compatibility tightening before Stage 4 expands
  descriptor use.
- This PR deliberately does not add `FieldSpec.to_dict()`,
  `FieldIndex.from_dict()`, index registries, codec contracts, lazy fields, or
  sample builders. Those remain assigned to later Stage 4 phases.

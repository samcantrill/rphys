# Phase 2 Execution Plan: IO Descriptors And Temporal Indexes

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v3`
- Feature focus: dependency-free lazy IO descriptors
- PR title: `Stage 3 P2: IO descriptors and temporal indexes`
- Branch: `agent/stage-3-p2-io-descriptors-indexes`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p2-io-descriptors-indexes`
- Phase execution plan path: `docs/roadmap/stage-3/phases/io-descriptors-indexes.md`
- Full plan: `docs/roadmap/stage-3/implementation-plan.md`
- Planning document: `docs/roadmap/stage-3/planning.md`
- Source phase: Phase 2, `io-descriptors-indexes`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: dedicated branch, worktree, and PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phase 1 is merged and recorded
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path refinement for serialization keys, temporal semantics, and no-registry posture
- Setup limitations: control checkout has an unrelated local `docs/roadmap.md` edit outside Phase 2 ownership
- Blockers: none

## Objective

Implement the Stage 3 lazy IO descriptor chain below datasource refs:
`ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, and
`FieldView`. The descriptors must remain dependency-free, immutable,
serializable through primitive dictionaries, and free of loading, probing,
codec, registry, or sample-building behavior.

## Full-Plan Context

Phase 1 established package and diagnostics guardrails. Phase 2 adds IO
descriptors only. Phase 3 owns datasource refs and schemas, Phase 4 owns
`IndexItem`, and Phase 5 owns full contract hardening and broad validation.

## Source Phase Summary

- Goal: implement resource, field, index, slice, and view descriptors.
- Required scope: `src/rphys/io/`, concrete IO/index errors, IO unit tests,
  package tests, and focused contract examples.
- Required checkpoints: strict construction, copied immutable mappings and
  sequences, value equality, primitive `to_dict()`/`from_dict()`, exact public
  exports, unknown index tag failure, and no deferred Stage 4/5 behavior.
- Acceptance criteria: valid examples round-trip, invalid inputs fail with
  typed errors, and equal numeric slices do not imply alignment.

## Current Source And Harness Findings

- Existing Stage 1 vocabulary supplies `DataKey`, `SchemaName`, and
  `MetadataKey` coercion.
- Existing broad errors include IO, field, and slice bases; Phase 2 adds only
  concrete errors exercised by descriptor behavior.
- Package tests from Phase 1 currently assert IO descriptor names are deferred;
  this phase must update those assertions to code-backed exports.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` edit remains outside Phase 2 files.
- Dedicated branch/worktree status: created from `develop` after Phase 1 metadata commit `c7ed583`.
- Current `develop` base: `c7ed583` at phase start.
- Earlier phase dependency status: Phase 1 merged and recorded.
- Push/PR infrastructure status: GitHub auth, fetch, PR listing, and Phase 1 merge path verified.
- Stop condition if isolation cannot be maintained: do not copy the unrelated roadmap edit or implement datasource/index-item behavior.

## In-Scope Work

- Add `ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, and `FieldView`.
- Add concrete IO/index errors raised by these descriptors.
- Add private primitive-copy/reconstruction helpers without documenting or exporting them.
- Update package, unit, and contract tests for public IO imports, construction,
  serialization, invalid inputs, immutability, and coupling exclusions.

## Out-of-Scope Work

- Datasource refs/schema/index items, codecs, codec registries, URI parsing,
  resource probing, load/save/build methods, seconds or spatial indexes,
  schema-version envelopes, fingerprints, `FieldRef.member`, runtime samples,
  and root `rphys` exports.

## Assumptions

- Stage 3 serializes only supported Stage 3 index types.
- Later codec and manifest stages can wrap these descriptors without changing
  constructor or serialization semantics.

## Scope Contract

`ResourceRef` stores uninterpreted `uri`, explicit `protocol`, and primitive
`storage_options`. `FieldRef` stores a `DataKey`, ordered non-empty
`ResourceRef` sequence, optional `SchemaName`, and primitive `MetadataKey`
mapping. `TemporalIndexSlice` stores half-open field-native `[start, stop)`
integer bounds with positive step. `FieldView` stores a `FieldRef` plus an
optional `FieldIndex`. All descriptors are immutable, value-equal, and
unhashable by public contract.

## Scientific Contract Notes

- Sampling and temporal alignment: temporal indexes are field-native integer
  offsets; equal numeric slices across fields do not imply alignment,
  resampling, padding, or seconds conversion.
- Field roles, locators, schemas, and provenance: `FieldRef` is role-free and
  member-free; schema is an optional `SchemaName`; metadata remains descriptive.
- Masking, filtering, normalization, and aggregation order: not implemented.
- Subject identity, splits, leakage, and grouping: not implemented in IO descriptors.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: invalid slice bounds fail in construction; unknown index
  tags fail loudly through `UnsupportedFieldIndexError`.

## Design Impact

- Maintainability: private helpers remove duplication without becoming public API.
- Extensibility: unsupported index tags fail now; future index types require
  explicit later design rather than hidden registry extension.
- Lightweight import policy: IO modules use only stdlib and Stage 1 vocabulary.
- Source-tree boundaries: no datasource modules are added or modified except package tests.

## Future Compatibility

Stage 4 codecs can interpret `ResourceRef.uri` and materialize `FieldView`.
Stage 5 manifests can wrap descriptors with schema versions, fingerprints, and
canonicalization externally.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add a public field-index registry | Registry names are not approved Stage 3 domain contracts. |
| Parse URIs into path/member components | URI internals are codec/protocol policy deferred to Stage 4/5. |
| Make descriptors broadly hashable | Hashes would imply cache-key semantics before manifest identity is designed. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Private field-index reconstruction supports only one tag | Stage 3 has one approved index type. | Later roadmap stage approves seconds, spatial, or custom index serialization. |

## Reviewability

- Expected PR size and shape: moderate descriptor modules plus focused tests.
- Files and areas to inspect: `src/rphys/io/`, IO errors, package tests, unit tests, contract examples.
- Scope-control checks: no datasource descriptors, load/probe/build methods, public registries, schema-version fields, fingerprints, root exports, or `FieldRef.member`.

## Implementation Steps

1. Add concrete IO/index errors under existing broad bases.
2. Add private primitive validation and immutable-copy helpers.
3. Implement resource, field, index, slice, and view descriptors with primitive serialization.
4. Update package exports and import-boundary checks.
5. Add unit and contract coverage for construction, invalid inputs, isolation, serialization, and exclusions.
6. Run required validation and pre-submit scope review.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact IO package/submodule exports, no root exports, no heavy optional imports.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/io/test_resources.py`, `tests/unit/rphys/io/test_fields.py`, `tests/unit/rphys/io/test_indexes.py`, `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: construction, invalid input, equality, immutability, mapping/resource isolation, serialization, and error inheritance.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_lazy_io_contract.py`
- Required assertions or deferral reason: EX-1, EX-4, and EX-5 lazy IO examples and exclusions.

### Integration Suite

- Status: deferred
- Required assertions or deferral reason: no runtime materialization or datasource integration exists.

### E2E Suite

- Status: deferred
- Required assertions or deferral reason: no user-facing workflow or dataset behavior.

### Acceptance Suite

- Status: deferred
- Required assertions or deferral reason: no opt-in acceptance behavior is affected.

## Risks

- Serialization key spelling becomes durable.
- Private dispatch could be mistaken for a registry if docs or tests import it.
- Temporal slices could be misread as cross-field alignment if docstrings/tests are vague.

## Validation Commands

Targeted development commands:

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

Final PR-preparation commands:

```sh
make test-unit
make test-contract
make test-package
git diff --check
```

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: errors, private primitives, resource refs,
  indexes, field refs/views, package/tests/docs.
- Tests to run with each slice: focused unit tests, then package and contract suites.
- Decisions the executor must not revisit: no root exports, no registries,
  no schema-version fields, no fingerprints, no `FieldRef.member`, no
  seconds/spatial indexes, and no load/probe/build behavior.
- Conditions that require stopping for the manager: need for codec loading,
  URI parsing, datasource provenance, stable identity, or unsupported index
  extension policy.

## Refinement And Review Budget Status

- Phase execution plan refinement: used manager-local expanded-path refinement
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed with expanded-path guardrails.
- Implementation summary: added `ResourceRef`, `FieldRef`, `FieldIndex`, `TemporalIndexSlice`, and `FieldView`; added exercised IO/index errors; updated IO package exports and package/unit/contract tests.
- Implementation validation: `make test-unit` passed with 226 tests; `make test-contract` passed with 16 tests; `make test-package` passed with 17 tests; `git diff --check` passed.
- Refinement summary: first validation run found test-only issues in expected export order, duplicate unit-test basename, and ABC `register` exposure; fixed by aligning tests to public order, renaming the IO field unit test, and using a simple base class for `FieldIndex`.
- Pre-submit blocker gate: passed manager-local expanded-path scope review; no datasource descriptors, runtime hooks, public registries, schema-version fields, fingerprints, root exports, or `FieldRef.member` were introduced.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

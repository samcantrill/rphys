# Phase 3 Execution Plan: Datasource Refs And Schema Descriptors

## Metadata

- Status: final phase execution plan
- Roadmap stage: `v3`
- Feature focus: datasource provenance and declaration-only schemas
- PR title: `Stage 3 Lazy References And Index Items - Phase 3: Datasource Refs And Schema Descriptors`
- Branch: `agent/stage-3-p3-datasource-refs-schemas`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-3-p3-datasource-refs-schemas`
- Phase execution plan path: `docs/roadmap/stage-3/phases/datasource-refs-schemas.md`
- Full plan: `docs/roadmap/stage-3/implementation-plan.md`
- Planning document: `docs/roadmap/stage-3/planning.md`
- Source phase: Phase 3, `datasource-refs-schemas`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: expanded path
- Phase isolation: dedicated branch, worktree, and PR to `develop`; local-only completion is not allowed
- Plan quality gate: passed; Phases 1 and 2 are merged and recorded
- Draft pass: manager-local draft
- Refine pass: manager-local expanded-path refinement for provenance, schema scope, and Stage 5 deferrals
- Setup limitations: control checkout has an unrelated local `docs/roadmap.md` edit outside Phase 3 ownership
- Blockers: none

## Objective

Implement `DataSourceRef`, `RecordRef`, and `DataSourceSchema` as
dependency-free descriptors that preserve datasource identity, record identity,
field presence, declaration-only schema information, and primitive metadata
without scanning, filtering, validating payloads, building splits, creating
manifests, or defining fingerprints.

## Full-Plan Context

Phase 2 supplies IO descriptors consumed by record fields and optional
datasource sources. Phase 3 adds provenance/schema descriptors only. Phase 4
will compose `IndexItem`, and Phase 5 will finalize public examples and broad
validation.

## Source Phase Summary

- Goal: implement datasource and record descriptors plus minimal schema declarations.
- Required scope: `src/rphys/datasources/refs.py`, `src/rphys/datasources/schemas.py`, datasource exports, concrete datasource/schema errors, unit/package/contract tests.
- Required checkpoints: mandatory IDs, non-empty field maps, key/spec and key/ref consistency, primitive metadata, primitive round trips, and no validation/report/manifest behavior.
- Acceptance criteria: datasource examples carry subject/split/group/source metadata and schema declarations without loading data.

## Current Source And Harness Findings

- Phase 2 provides `ResourceRef` and `FieldRef` serialization.
- Stage 2 provides `FieldSpec`; this phase serializes it privately inside datasource schemas without adding `FieldSpec.to_dict()`.
- Existing package tests expect datasource names to be deferred; this phase must update them to code-backed exports while keeping `IndexItem` deferred.

## Phase Isolation State

- Control checkout dirty-state review: unrelated `docs/roadmap.md` edit remains outside Phase 3 files.
- Dedicated branch/worktree status: created from `develop` after Phase 2 metadata commit `413a143`.
- Current `develop` base: `413a143` at phase start.
- Earlier phase dependency status: Phases 1 and 2 merged and recorded.
- Push/PR infrastructure status: GitHub auth, fetch, PR listing, and prior merge path verified.
- Stop condition if isolation cannot be maintained: do not implement `IndexItem`, datasource builders, validation reports, manifests, or fingerprints.

## In-Scope Work

- Add datasource schema, datasource ref, and record ref descriptors.
- Add concrete datasource/schema/record errors raised by Phase 3 behavior.
- Update datasource package exports and import-boundary checks.
- Add unit and contract coverage for construction, invalid input, mapping isolation, serialization, metadata provenance, and coupling exclusions.

## Out-of-Scope Work

- `IndexItem`, datasource adapters/builders/views/filters/splits, validation reports, manifest codecs, expected-versus-observed schema evidence, schema-version fields, fingerprints, stable datasource-index identity, and first-class subject/split/group fields.

## Assumptions

- Metadata-only leakage context is accepted for Stage 3.
- Stage 5 can wrap these descriptors with manifests, validation evidence, fingerprints, and stable identity externally.

## Scope Contract

`DataSourceSchema(fields, metadata=None)` requires a non-empty `DataKey ->
FieldSpec` mapping with key/spec consistency. `DataSourceRef(datasource_id,
source=None, schema=None, metadata=None)` requires a non-empty datasource ID
and optional `ResourceRef`/`DataSourceSchema`. `RecordRef(datasource,
record_id, fields, metadata=None)` requires a mandatory `DataSourceRef`, a
non-empty record ID, and a non-empty `DataKey -> FieldRef` mapping with key/ref
consistency. Descriptors are immutable, value-equal, unhashable, and
primitive-serializable.

## Scientific Contract Notes

- Sampling and temporal alignment: not introduced; record fields carry `FieldRef` only.
- Field roles, locators, schemas, and provenance: record fields use intrinsic `DataKey`; leakage-sensitive source/subject/split/group values stay in metadata.
- Masking, filtering, normalization, and aggregation order: not implemented.
- Subject identity, splits, leakage, and grouping: metadata preserves context without first-class fields or split-building behavior.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and unsupported slices: not introduced beyond non-empty field and ID validation.

## Design Impact

- Maintainability: datasource declarations reuse `FieldSpec` without extending runtime `rphys.data`.
- Extensibility: Stage 5 can add validation reports and manifests as wrappers.
- Lightweight import policy: datasource modules use stdlib, Stage 1/2 data vocabulary, and Phase 2 IO descriptors only.
- Source-tree boundaries: no IO behavior changes beyond imports/tests.

## Future Compatibility

Stage 4 can validate `IndexItem` field views against `RecordRef.fields`.
Stage 5 can add datasource indexes, manifests, validation evidence, and stable
identity without mutating these descriptor fields.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add first-class subject/split/group fields | Leakage metadata remains flexible and avoids premature split-builder policy. |
| Add schema validation status or observed fields | Validation reports are Stage 5 datasource behavior. |
| Add fingerprints or cache keys | Stable identity and canonicalization are deferred manifest/index policy. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| `FieldSpec` serialization is private to datasource schemas | Avoids adding Stage 2 runtime serialization API in Phase 3. | A later public schema/manifest contract needs shared `FieldSpec` serialization. |

## Reviewability

- Expected PR size and shape: moderate datasource modules plus focused tests.
- Files and areas to inspect: datasource refs/schema modules, datasource exports, error taxonomy, package/unit/contract tests.
- Scope-control checks: no `IndexItem`, scans, filters, builders, validation reports, manifests, schema versions, fingerprints, first-class split/subject/group fields, or mutation APIs.

## Implementation Steps

1. Add concrete datasource/schema/record errors.
2. Implement `DataSourceSchema` with non-empty declarations and private `FieldSpec` primitive serialization.
3. Implement `DataSourceRef` and `RecordRef` with copied immutable metadata and field consistency checks.
4. Update datasource package exports and import-boundary tests.
5. Add unit and contract coverage for construction, serialization, provenance, and exclusions.
6. Run required validation and pre-submit scope review.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/package/test_import.py`, `tests/package/test_import_boundaries.py`
- Required assertions or deferral reason: exact datasource package/submodule exports, no root exports, no heavy optional imports, `IndexItem` still deferred.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/rphys/datasources/test_datasource_refs.py`, `tests/unit/rphys/datasources/test_datasource_schemas.py`, `tests/unit/rphys/test_errors.py`
- Required assertions or deferral reason: construction, invalid input, equality, immutability, metadata isolation, field consistency, serialization, and error inheritance.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_lazy_datasource_contract.py`
- Required assertions or deferral reason: EX-2, EX-4, and EX-5 datasource provenance/schema examples and exclusions.

### Integration Suite

- Status: deferred
- Required assertions or deferral reason: no datasource scanning or runtime materialization exists.

### E2E Suite

- Status: deferred
- Required assertions or deferral reason: no user-facing workflow or dataset behavior.

### Acceptance Suite

- Status: deferred
- Required assertions or deferral reason: no opt-in acceptance behavior is affected.

## Risks

- Metadata-only leakage context is less discoverable than first-class fields.
- Reusing `FieldSpec` can blur declaration versus observed payload facts if docstrings/tests are vague.
- Serialization key spelling becomes durable for later manifests.

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

- Safe implementation slices: errors, datasource schemas, datasource/record refs, package tests, unit/contract tests.
- Tests to run with each slice: focused unit tests, then package and contract suites.
- Decisions the executor must not revisit: no fingerprints, schema-version fields, expected/observed validation reports, scans, filters, builders, first-class subject/split/group fields, or `IndexItem`.
- Conditions that require stopping for the manager: provenance cannot be preserved without fingerprints, first-class leakage fields, validation evidence, or builder behavior.

## Refinement And Review Budget Status

- Phase execution plan refinement: used manager-local expanded-path refinement
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed manager-local.
- Final phase execution plan: completed with expanded-path guardrails.
- Implementation summary: added `DataSourceRef`, `RecordRef`, and `DataSourceSchema`; added exercised datasource/schema/record errors; updated datasource package exports and package/unit/contract coverage.
- Implementation validation: `make test-unit` passed with 244 tests; `make test-contract` passed with 19 tests; `make test-package` passed with 19 tests; `git diff --check` passed.
- Refinement summary: first package run found stale deferred-surface expectations for `rphys.datasources`; fixed package tests to treat datasource refs/schema as code-backed exports while keeping `IndexItem` deferred.
- Pre-submit blocker gate: passed manager-local expanded-path scope review; no `IndexItem`, scans, filters, builders, validation reports, manifests, schema-version fields, fingerprints, or first-class subject/split/group fields were introduced.
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none

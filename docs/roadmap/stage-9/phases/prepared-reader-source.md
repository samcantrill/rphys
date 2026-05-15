# Phase 4 Execution Plan: Prepared Manifest, Public Provisional Reader, And Prepared Source

## Metadata

- Status: final phase execution plan; ready for implementation
- Roadmap stage: `v9`
- Feature focus: immutable prepared-data equivalence, public provisional reader boundary, and prepared sample source
- Stage descriptor: Index Adapters, Torch Data Loading, And Cache
- Phase descriptor: Prepared Manifest, Public Provisional Reader, And Prepared Source
- PR title: `Stage 9 Index Adapters, Torch Data Loading, And Cache - Phase 4: Prepared Manifest, Public Provisional Reader, And Prepared Source`
- Branch: `agent/stage-9-data-loading-cache-p4-prepared-reader-source`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-9-data-loading-cache-p4-prepared-reader-source`
- Phase execution plan path: `docs/roadmap/stage-9/phases/prepared-reader-source.md`
- Full plan: `docs/roadmap/stage-9/implementation-plan.md`
- Base branch: `develop`
- Target branch: `develop`
- Workflow path: expanded path
- Blockers: none for implementation planning

## Objective

Add the first prepared-data boundary without choosing a storage backend. Phase 4
introduces versioned primitive prepared manifest records, a public provisional
`PreparedSampleReader` protocol, and `PreparedSampleSource` behavior that reads
FieldLocator-keyed `Sample` objects only after manifest/request/context
equivalence is proven.

## Scope

In scope:

- `src/rphys/datasources/prepared.py` with code-backed public names:
  - `PreparedField`
  - `PreparedDataManifest`
  - `PreparedReadRequest`
  - `PreparedReadResult`
  - `PreparedSampleReader`
  - `PreparedSampleSource`
- Prepared manifest identity and compatibility records for source/index,
  request, operation, invalidation, fields, counts, splits/groups, checksums,
  layout/cost metadata, and runtime assumptions.
- A public provisional reader protocol that accepts one prepared read request
  and returns a FieldLocator-keyed `Sample` plus backend identity evidence.
- A prepared source wrapper that refuses unproven equivalence, validates reader
  manifest compatibility, preserves Phase 1 `SampleSource` shape, and does not
  mutate prepared products.
- Fake reader tests proving backend storage details do not become domain
  semantics.

Out of scope:

- Concrete storage SDKs or backends.
- Full read/write backend protocol.
- Materialization worker execution, shard/chunk writers, cache payload writers,
  active streaming/resume, DDP coordination, trainer/device/model formatting,
  generic artifacts, or hidden preprocessing in `__getitem__`.
- Parent/root exports.

## Public Contract

- `PreparedDataManifest` is an immutable, versioned primitive record that states
  prepared equivalence evidence and a stable fingerprint.
- `PreparedField` describes one prepared field locator, schema/dtype/shape/unit
  metadata, checksum/layout evidence, and primitive metadata.
- `PreparedReadRequest` carries the prepared position, coerced
  `SampleRequest`, `SampleRuntimeContext`, and required manifest fingerprint.
- `PreparedReadResult` carries the returned `Sample`, manifest fingerprint,
  backend identity, field locators, and primitive metadata.
- `PreparedSampleReader` is public provisional: it is an importable protocol for
  backend-specific readers, not a full backend contract.
- `PreparedSampleSource.sample_at(...)` validates request/context/manifest
  equivalence before reading, calls the reader for one position, validates the
  result, and returns the same `Sample` shape as any `SampleSource`.

## Tests

- Package: prepared module `__all__`, parent/root non-exports, lightweight
  import boundary.
- Unit: manifest and field validation, fingerprint sensitivity, compatibility
  success/failure, read request/result validation, fake reader behavior, and
  prepared-source request/context mismatch failures.
- Contract: public provisional reader semantics and prepared source same-shape
  behavior.
- Integration: fake prepared reader/source flow over synthetic samples with
  success and adversarial mismatch paths.
- Deferred: concrete backend, materialization worker, e2e, acceptance, and DDP
  behavior.

## Validation Commands

```sh
uv run pytest tests/unit/rphys/datasources/test_prepared.py
uv run pytest tests/contracts/test_prepared_sample_reader_contract.py
uv run pytest tests/integration/test_stage9_prepared_flow.py
uv run pytest tests/package/test_import.py tests/package/test_import_boundaries.py
make test-package
make test-contract
make test-integration
git diff --check
```

Final PR gate:

```sh
make validate-pr
make test-summary
git diff --check
```

## Stop Conditions

- Stop if implementation requires a concrete backend dependency or SDK.
- Stop if `PreparedSampleReader` needs a full read/write backend protocol.
- Stop if prepared source must run preprocessing, operations, exports,
  materialization workers, trainer/device/model formatting, or hidden mutation
  in `__getitem__`.
- Stop if parent/root exports or heavy optional imports appear necessary.

## Completion Notes

- Draft plan: complete
- Final phase execution plan: complete
- Implementation summary: pending
- Implementation validation: pending
- Pre-submit blocker gate: no unresolved plan-level blocker identified
- PR body draft: pending
- PR preparation: pending
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none identified for implementation

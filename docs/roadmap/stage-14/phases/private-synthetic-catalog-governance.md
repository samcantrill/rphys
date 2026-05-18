# Phase 1 Execution Plan: Private Synthetic Catalog And Governance

## Metadata

- Status: implemented; ready for PR submission
- Roadmap stage: `v14`
- Feature focus: private deterministic synthetic fixtures and support governance
- Stage descriptor: Synthetic Fixtures, Contract Tests, And Smoke Hardening
- Phase descriptor: Private Synthetic Catalog And Governance
- PR title: `Stage 14 Synthetic Fixtures, Contract Tests, And Smoke Hardening - Phase 1: Private Synthetic Catalog And Governance`
- Branch: `agent/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
- Worktree: `/home/samcantrill/work/rphys-worktrees/stage-14-synthetic-smoke-hardening-p1-private-synthetic-catalog-governance`
- Phase execution plan path: `docs/roadmap/stage-14/phases/private-synthetic-catalog-governance.md`
- Full plan: `docs/roadmap/stage-14/implementation-plan.md`
- Planning document: `docs/roadmap/stage-14/planning.md`
- Source phase: `docs/roadmap/stage-14/implementation-plan.md#phase-1-private-synthetic-catalog-and-governance`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after automated review, local validation, and CI pass
- Workflow path: fast path
- Phase isolation: one dedicated branch, one dedicated worktree, one PR to
  `develop`; local-only completion is not allowed
- Plan quality gate: Stage 14 implementation plan approved with Phase 4
  prerequisite-gated; Phase 1 has no recorded blocker
- Draft pass: complete for fast-path planning
- Refine pass: not needed unless implementation finds a real scope, ownership,
  validation, or public-contract ambiguity
- Setup limitations: dedicated worktree and branch were already present and
  clean; local `HEAD`, `develop`, and `origin/develop` refs all resolved to
  `fc9428c`
- Blockers: none for Phase 1 planning or implementation

## Objective

Establish a private, deterministic, license-safe synthetic fixture catalog and
edge-variant vocabulary under `tests/support`, prove it through first consuming
tests that exercise public `rphys` objects, and document concise support
privacy and determinism governance without adding production APIs or public
testing-helper packages.

## Full-Plan Context

Phase 1 creates the fixture foundation for later Stage 14 phases. Phase 2 will
add private contract assertion helpers and narrow durable goldens on top of this
catalog. Phase 3 will compose upstream Stage 5-12 smoke flows and validation
tiers from the proven support base. Phase 4 remains blocked in this checkout
until revised Stage 13 Sample/Batch-native artifact, collection/metric,
visualization/report, and recipe behavior is code-backed and approved. Phase 1
must not pull any of that later work forward.

## Source Phase Summary

- Goal: establish the reusable private fixture base and edge-variant vocabulary
  without adding public APIs.
- Required scope: `tests/support` catalog and edge helpers, first consuming
  tests under `tests/contracts` or `tests/integration`, and concise updates to
  `tests/README.md` or support docstrings if implementation touches support
  governance.
- Required checkpoints: existing support-helper consumers stay compatible or
  are updated together; helper imports remain concrete and private; edge
  variants carry inspectable failure evidence; package validation confirms no
  public fixture leakage.
- Acceptance criteria: consuming tests construct multiple datasource, record,
  subject, group, split, URI-resource, optional-field, waveform, timestamp, and
  representative edge scenarios through public objects; no `src/rphys` public
  import surface is added.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase:
  `tests/support/synthetic_datasources.py` provides one descriptor-only
  datasource/record helper and `SyntheticScanAdapter`;
  `tests/support/lazy_sample_builder_fixtures.py` builds one lazy sample
  builder fixture with video and BVP fields; `tests/support/synthetic_codecs.py`
  provides a dependency-light `SyntheticCodec`; `tests/support/__init__.py` is
  minimal and should remain so by default.
- Existing tests or harness behavior: current consumers include datasource
  validation/index/group-split contracts, Stage 5 datasource flow, Stage 8
  export/derived datasource flow, Stage 9 sample-source/cache/prepared/torch
  flows, sample-builder unit and contract tests, codec tests, and package
  import-boundary tests that already check `tests.support` is not loaded from
  lightweight production imports.
- Import-boundary or dependency constraints: support helpers may import public
  `rphys` modules; production `src/rphys` must not import `tests.support`;
  helpers must remain CPU-only and avoid heavy optional dependencies such as
  video, array, plotting, deep-learning, or dataset SDK stacks.

## Phase Isolation State

- Control checkout dirty-state review: the control checkout had unrelated
  local edits in Stage 14 planning documents and an untracked Stage 15
  directory; those changes are not copied into this phase worktree.
- Dedicated branch/worktree status: the requested branch and worktree exist and
  the phase worktree is clean before this plan edit.
- Current `develop` base: local phase worktree `HEAD`, local `develop`, and
  local `origin/develop` refs all resolve to `fc9428c`.
- Earlier phase dependency status: none; this is the first Stage 14 phase.
- Push/PR infrastructure status: not needed for the draft-plan pass; executor
  or manager must verify GitHub auth, push, PR creation, and CI access before
  marking implementation complete.
- Stop condition if isolation cannot be maintained: stop before implementation
  and report a blocker if the phase branch carries unrelated work, requires
  copying uncommitted control-checkout changes, or cannot remain a standalone
  PR to `develop`.

## In-Scope Work

- Add or consolidate private support helpers for deterministic synthetic
  scenarios, likely in narrow modules such as
  `tests/support/synthetic_catalog.py` and `tests/support/synthetic_edges.py`,
  while preserving existing helper imports or updating all affected consumers
  together.
- Cover multiple datasources, records, subjects, groups, split metadata,
  stable identity metadata, URI `ResourceRef`s, deterministic video-like
  payload evidence, waveform payload evidence, timestamp metadata, optional
  landmarks/masks/quality/sidecar/compound fields, and tiny manifest-ready
  descriptors.
- Add named edge variants for missing fields, short inputs, flat signals,
  `NaN`, `inf`, invalid sample rates, timestamp drift/irregularity, and
  misalignment, with affected field, rate/timestamp/alignment evidence, and
  expected failure family recorded.
- Add first consuming contract and/or integration tests that construct real
  public `rphys` descriptors, scan/index/sample objects, and provenance from
  the private catalog.
- Keep support governance concise in support docstrings or `tests/README.md`:
  helpers are private, generated, deterministic, license-safe, CPU-only, and
  not public API promises.

## Out-of-Scope Work

- Phase 2 contract assertion helpers, contract helper framework, import-boundary
  expansion beyond what Phase 1 needs, and narrow durable golden files.
- Phase 3 smoke/debug/signal tier semantics, upstream root-smoke composition,
  broad integration smoke helpers, and validation target reshaping.
- Phase 4 Stage 13 scan-to-report tail behavior, Stage 13 placeholder exports,
  returned-`Batch` prediction-field contracts, sample artifact report tail, or
  private stand-ins for unavailable Stage 13 APIs.
- Public `rphys.testing`, `rphys.fixtures`, `rphys.datasets`, root re-exports,
  production fixture modules, broad registries, support-level runners, real raw
  datasets, workflow/runtime code, acceptance datasets, performance profiling,
  or heavy optional dependencies.

## Assumptions

- The current public objects through Stage 12 are sufficient to validate the
  Phase 1 catalog with private support and consuming tests only.
- Existing support helpers can either remain as compatibility wrappers or be
  refactored with all current consumers updated in the same phase.
- Deterministic primitive tuple payloads and descriptor metadata are enough for
  Phase 1; realistic media codecs, loaded arrays, and real dataset formats are
  not required.
- Edge variants may record expected failure evidence even when a specific
  public consumer for every variant lands in a later phase; Phase 1 must still
  include representative public-path consumers.

## Scope Contract

Phase 1 changes no public library behavior. Any new helper, dataclass, factory,
fixture, fake adapter, or edge variant is private test support under
`tests/support` and may be refactored later. Consuming tests must import
concrete support modules rather than relying on a broad `tests.support` facade,
and `tests/support/__init__.py` should stay empty or minimal unless a narrow
reviewed need appears.

Support helpers may construct public `DataSourceRef`, `RecordRef`,
`ResourceRef`, `FieldRef`, `FieldView`, `DataSourceScanResult`,
`DataSourceIndex`, `IndexItem`, `SampleBuilder`, `FieldValue`, and related
objects through public APIs. They must not import production-private modules
unless an existing test already targets a private implementation detail. Source
packages under `src/rphys` must not import support helpers.

Scenario data should be small and deterministic. Payload evidence may be
primitive tuples or metadata, with generated values tied to explicit field,
record, subject, datasource, rate, timestamp, and split/group evidence. URI
resources should be descriptor-only unless a consumer explicitly writes to a
temporary directory. No helper should silently coerce invalid scientific inputs;
edge variants should preserve invalidity for the consuming public contract to
raise, reject, or report.

## Scientific Contract Notes

- Sampling and temporal alignment: positive scenarios must record sample rates,
  timestamp offsets, and alignment intent for video-like, waveform, and
  timestamp fields; drift, irregularity, invalid-rate, short, and misaligned
  cases are explicit edge variants, not hidden defaults.
- Field roles, locators, schemas, and provenance: helpers should remain
  field-role oriented rather than dataset-specific. Metadata should make
  datasource, record, subject, group, split, field schema, URI refs, and sample
  provenance inspectable through public objects.
- Masking, filtering, normalization, and aggregation order: Phase 1 does not
  implement signal processing, filtering, normalization, aggregation, or metric
  semantics. Optional masks and quality fields are fixture data only.
- Subject identity, splits, leakage, and grouping: scenarios must use stable
  subject/group/split metadata so later filters, split builders, and smoke
  tests can reason about leakage boundaries without real datasets.
- NaNs, flat signals, missing fields, short inputs, invalid rates, and
  unsupported slices: edge variants must carry the affected field and expected
  failure family; they must not be padded, repaired, dropped, or converted into
  valid positive fixtures by the support layer.

## Design Impact

- Maintainability: centralize repeated synthetic setup in small private
  factories and evidence records, then prove each helper through at least one
  public-path consumer before accepting it.
- Extensibility: keep scenario specs field-role and descriptor oriented so
  future modalities, real datasource stages, and Stage 15 profiling can reuse
  the shape without inheriting dataset-specific shortcuts.
- Lightweight import policy: support modules stay test-only and
  dependency-light; production imports must not load `tests.support` or heavy
  optional stacks.
- Source-tree boundaries: Phase 1 is expected to touch `tests/support`,
  focused consuming tests, and concise test-support docs only. Production code
  changes are a stop condition unless a real public-contract bug is exposed and
  separately scoped.

## Future Compatibility

- Phase 2 may add assertion helpers and narrow durable goldens using this
  catalog, but Phase 1 must not prebuild that assertion/golden framework.
- Phase 3 may compose upstream smoke flows from these helpers, but Phase 1 must
  not add a smoke runner or tier marker policy.
- Phase 4 must consume real Stage 13 public behavior when it exists; Phase 1
  must not create Stage 13 substitutes, placeholder package exports, or report
  tail fixtures that imply code-backed coverage.
- A future public testing-helper package must redesign from stable behavior and
  downstream need, not promote these private helper module paths wholesale.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Add public `rphys.testing` or `rphys.fixtures` helpers | Public testing helpers are deferred by the roadmap and would create durable API and dependency commitments. |
| Build a support-level scenario runner or global registry | It would hide public construction paths and turn private support into a framework before repeated cross-suite need is proven. |
| Store a broad checked-in golden catalog | Broad snapshots would freeze private helper internals and loaded payload details; Phase 2 owns narrow durable artifact goldens. |
| Mutate one-off fixtures ad hoc in each consuming test | It duplicates setup, obscures provenance, and makes scientific edge semantics less inspectable. |
| Re-export all helpers from `tests/support/__init__.py` | A facade would look like a quasi-public support API; concrete module imports keep ownership clearer. |
| Add Stage 13 stand-ins for the smoke tail | Phase 4 is prerequisite-gated; fake Stage 13 behavior would create false integration evidence. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Private helper module names may churn | The phase deliberately avoids public support API commitments. | A future public helper package is approved or repeated downstream reuse requires stable imports. |
| Some edge variants may initially have only representative consumers | Phase 1 establishes the vocabulary; later phases broaden contract and smoke coverage. | A variant remains unused after Phase 2 contract hardening or exposes ambiguous failure semantics. |
| Generated payloads are not realistic codec/media evidence | Phase 1 validates object-model contracts without raw data or heavy dependencies. | Real datasource or codec acceptance work is approved. |
| Package import hardening may rely mostly on existing tests | Phase 1 scope is support/catalog governance, while Phase 2 owns broader import-boundary hardening. | Existing package tests fail to catch a new public helper leak. |

## Reviewability

- Expected PR size and shape: small to medium test/support-only PR with one
  catalog/edge support addition, targeted consumer tests, and concise
  governance docs or docstrings.
- Files and areas to inspect: `tests/support/synthetic_datasources.py`,
  `tests/support/lazy_sample_builder_fixtures.py`,
  `tests/support/synthetic_codecs.py`, `tests/support/__init__.py`, any new
  `tests/support/synthetic_catalog.py` or `tests/support/synthetic_edges.py`,
  focused contract/integration consumers, `tests/README.md`, and package tests
  only if a missing public-leakage guard is discovered.
- Scope-control checks: no `src/rphys` fixture APIs, no public
  `rphys.testing`/`rphys.fixtures`/`rphys.datasets`, no broad
  `tests/support/__init__.py` facade, no golden snapshots, no smoke-tier
  markers, no Stage 13 tail placeholders, and no unused support helpers.

## Implementation Steps

1. Inventory existing support imports and decide whether to preserve the
   current helper names as wrappers or update all current consumers with the
   catalog refactor in the same PR.
2. Add deterministic catalog primitives and factories for positive scenarios:
   multiple datasources, subjects, records, groups, split metadata, URI refs,
   video-like payload evidence, waveform evidence, timestamp evidence, and
   optional fields.
3. Add named edge-variant helpers that derive from catalog scenarios and record
   affected field, invalid or unusual scientific evidence, and expected failure
   family without enforcing consumer-specific assertions.
4. Add first consuming tests in `tests/contracts` and/or `tests/integration`
   that prove catalog scenarios construct real public descriptors, scan/index
   or sample-builder flows, stable provenance, and representative edge behavior.
5. Update concise support governance docs or support module docstrings only
   where the implementation touches support semantics.
6. Run targeted validation, then stop for the manager if implementation needs a
   public API decision, production fixture module, Stage 13 placeholder, real
   data, or broad contract-helper/golden work.

## Test Plan

### Package Suite

- Status: required
- Expected paths: existing `tests/package/test_import.py` and
  `tests/package/test_import_boundaries.py`; add Phase 1 package assertions
  only if implementation reveals a missing public-leakage guard.
- Required assertions or deferral reason: package tests must confirm no public
  fixture package, no root fixture re-export, no production import of
  `tests.support`, and no heavy optional import introduced by support growth.
  Required command: `make test-package`.

### Unit Suite

- Status: required when existing unit consumers of support helpers are touched;
  otherwise deferred because support modules are validated through consuming
  suites rather than a standalone `tests/support` suite.
- Expected paths: likely touched consumers include
  `tests/unit/rphys/datasources/test_validation.py`,
  `tests/unit/rphys/datasources/test_index_candidates.py`,
  `tests/unit/rphys/datasources/test_datasource_indexes.py`,
  `tests/unit/rphys/data/test_sample_builders.py`,
  `tests/unit/rphys/io/test_codec_registry.py`, and export/cache unit tests
  that import `SyntheticCodec` or `make_builder_fixture`.
- Required assertions or deferral reason: any updated unit consumer must still
  prove existing public object behavior and helper compatibility. Run focused
  `uv run pytest ...` paths for every touched unit file; run `make test-unit`
  if helper refactoring changes many unit consumers.

### Contract Suite

- Status: required
- Expected paths: new or updated focused contract tests such as
  `tests/contracts/test_synthetic_catalog_contract.py`,
  `tests/contracts/test_datasource_scan_validation_contract.py`,
  `tests/contracts/test_datasource_index_contract.py`, or
  `tests/contracts/test_lazy_sample_builder_contract.py`.
- Required assertions or deferral reason: contract consumers must show public
  descriptors and validation/index/sample-builder behavior from catalog
  scenarios; edge variants must expose inspectable failure evidence and at
  least representative public-path failure/report behavior. Run focused
  `uv run pytest ...` for touched contract files, and run `make test-contract`
  before PR preparation if contract coverage is added or refactored.

### Integration Suite

- Status: required
- Expected paths: new or updated focused integration tests such as
  `tests/integration/test_synthetic_catalog_flow.py`,
  `tests/integration/test_synthetic_datasource_index_sample_builder.py`, or
  `tests/integration/test_stage5_synthetic_datasource_flow.py`.
- Required assertions or deferral reason: integration coverage must prove at
  least one multi-datasource or multi-record scenario composes through public
  scan/view/index/sample-builder paths with stable subject/group/split
  provenance and deterministic payload evidence. Run focused
  `uv run pytest ...` for touched integration files; run
  `make test-integration` if existing integration flows are refactored.

### E2E Suite

- Status: deferred
- Expected paths: none for Phase 1.
- Required assertions or deferral reason: e2e smoke placement and validation
  tier semantics belong to Phase 3, not the private catalog/governance phase.

### Acceptance Suite

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: real datasets, hardware, GPU,
  network, long-running, or acceptance-data checks are explicitly out of scope
  for Phase 1 and Stage 14 default validation.

## Risks

- Helper sprawl or an implicit support framework; mitigate by requiring first
  consuming tests and rejecting unused factories.
- Dataset-specific shortcuts hidden inside synthetic helpers; mitigate by
  making fields, locators, identities, sample rates, timestamps, and provenance
  explicit.
- Existing consumers break during support consolidation; mitigate by preserving
  wrappers or updating consumers and focused tests together.
- Edge variants become silently valid fixtures; mitigate by recording expected
  failure evidence and using representative public-path consumers.
- Scope drift into Phase 2 assertions/goldens, Phase 3 smoke tiers, or Phase 4
  Stage 13 behavior; mitigate with the stop conditions below.

## Validation Commands

Targeted development commands:

```sh
uv run pytest tests/contracts/test_synthetic_catalog_contract.py
uv run pytest tests/integration/test_synthetic_catalog_flow.py
uv run pytest <touched existing unit/contract/integration paths>
make test-package
make test-contract
make test-integration
git diff --check
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
git diff --check
```

`uv lock --check` is not expected to change for this phase because dependency
metadata changes are out of scope; run it if implementation unexpectedly
touches dependency or lock files, then stop to explain why that scope became
necessary.

## Handoff Notes For `rphys_phase_executor`

- Safe implementation slices: catalog primitives first, edge variants second,
  first consumers third, governance docs last.
- Tests to run with each slice: run focused consumer tests immediately after
  adding or refactoring each helper; run existing unit consumers when preserving
  compatibility wrappers; finish with `make test-package` and the final
  PR-preparation commands.
- Decisions the executor must not revisit: helpers stay private under
  `tests/support`; no public helper package; no broad support registry/runner;
  no durable goldens; no smoke tier work; no Stage 13 placeholders; production
  changes are not planned.
- Conditions that require stopping for the manager: implementation requires a
  public API decision, real data, heavy dependency, production fixture module,
  fake Stage 13 contract, broad contract assertion helper, golden snapshot
  suite, or public-contract bug fix outside the accepted Phase 1 scope.

## Refinement And Review Budget Status

- Phase execution plan refinement: not needed on the fast path
- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed for Phase 1 fast-path planning on 2026-05-18.
- Final phase execution plan: this artifact is ready for implementation
  handoff once committed.
- Implementation summary: added private `tests/support/synthetic_catalog.py`
  and `tests/support/synthetic_edges.py`, focused contract coverage for
  positive catalog descriptors and edge evidence, an integration consumer for
  scan/index/sample-builder composition, and concise `tests/README.md` support
  governance.
- Implementation validation: focused catalog contract and integration tests
  passed; `make test-package`, `make test-contract`, `make test-integration`,
  `make validate-pr`, `make test-summary`, and `git diff --check` passed on
  2026-05-18. `make test-summary` reported 1024 passed tests across package,
  unit, contract, and integration suites; e2e and acceptance suites were not
  present.
- Refinement summary: not needed; focused and suite-level validation passed.
- Pre-submit blocker gate: passed by manager review; no public helper package,
  production fixture API, support facade, broad golden, smoke-tier work, or
  Stage 13 placeholder was introduced.
- PR preparation: PR body drafted at
  `docs/roadmap/stage-14/phases/private-synthetic-catalog-governance-pr-body.md`.
- Automated review: pending
- Merge result: pending
- Cleanup: pending
- Remaining blockers: none for Phase 1

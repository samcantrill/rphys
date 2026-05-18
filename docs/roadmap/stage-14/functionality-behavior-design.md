# Stage 14 Functionality, Behavior, And Design

Status: approved documentation; revised on 2026-05-18 to align with the
Stage 13 Sample/Batch-native implementation plan.

Roadmap version: `v14`
Planning document: `docs/roadmap/stage-14/planning.md`
Implementation plan: `docs/roadmap/stage-14/implementation-plan.md`
Stage 13 dependency: `docs/roadmap/stage-13/implementation-plan.md`

## Purpose

Stage 14 hardens the public `rphys` object model with private deterministic
synthetic fixtures, public-contract assertions, integration smoke tests,
validation tier conventions, and package/import checks. It is a testing and
confidence milestone, not a new public runtime package.

The practical outcome is that maintainers can exercise realistic public API
composition without raw datasets, network access, GPU requirements, workflow
runtimes, plotting stacks, or downstream project code. Downstream users do not
import Stage 14 helpers; they benefit from stronger guarantees around the
public library behavior.

## Implemented Functionality

### Private Synthetic Fixture Catalog

Stage 14 adds or consolidates private helpers under `tests/support` for small,
deterministic, license-safe fixture scenarios. The catalog covers:

- multiple datasources, records, subjects, and groups
- stable identity, split, and group metadata
- deterministic video-like payload fields
- waveform fields with known rate, frequency, phase, amplitude, and heart-rate
  evidence
- timestamp fields with rates, offsets, drift, irregularity, and alignment
  evidence
- optional landmarks, masks, quality fields, sidecars, compound fields, and URI
  refs
- tiny manifest-ready descriptors for public serialization and export tests

The helpers must construct real public `rphys` objects and descriptors. They
must not bypass loader, ref, field, schema, cache, export, or provenance
contracts.

Illustrative test-only usage:

```python
from tests.support.synthetic_catalog import make_synthetic_scenario

scenario = make_synthetic_scenario(
    datasources=2,
    subjects=("s01", "s02"),
    records_per_subject=2,
    fields=("video", "bvp", "mask", "quality"),
)

datasource = scenario.datasource_ref()
records = datasource.scan()

assert records[0].subject_id == "s01"
assert records[0].fields["bvp"].sample_rate_hz == 30.0
assert records[0].resources["video"].uri.startswith("memory://")
```

The names above are illustrative. The implementation may choose different
private helper names, but the behavior and ownership stay fixed.

### Scientific Edge Variants

The fixture catalog includes named negative variants for scientific and data
contract failures:

- missing fields
- short records
- flat signals
- `NaN` and `inf` values
- invalid sample rates
- timestamp drift and irregularity
- field/sample misalignment

Each variant records expected failure evidence: the affected field, sample-rate
or timestamp evidence, alignment details, and the expected failure family. The
test consumer decides whether the public contract should raise, reject, skip,
or surface diagnostics.

Illustrative usage:

```python
from tests.support.synthetic_edges import make_edge_variant

case = make_edge_variant("invalid_sample_rate")

with pytest.raises(ValueError, match="sample rate"):
    build_sample_through_public_api(case.record_ref)
```

Stage 14 does not silently coerce invalid scientific inputs. If a variant
exposes a real public-contract gap, the implementation routes that as a scoped
bug fix or follow-up with tests and docs.

### Private Contract Assertions

Stage 14 adds small private assertion helpers only where they remove repeated
contract-test setup. They are not a scenario runner, registry, or public helper
framework.

The assertion helpers cover repeated invariants such as:

- selector construction and timing
- ref and manifest serialization without loaded arrays or open handles
- `FieldRef` and `FieldView` access behavior
- `SampleBuilder` probe/build subsets
- deterministic and stochastic operation replay evidence
- save/export/derived datasource round trips
- cache key determinism and invalidation
- package and import boundaries
- Method, loss, objective, metric, learner, trainer, and Stage 13-adjacent
  boundaries when code-backed

Illustrative usage:

```python
from tests.support.contract_assertions import assert_manifest_round_trips
from tests.support.synthetic_catalog import make_synthetic_scenario

scenario = make_synthetic_scenario()
manifest = scenario.to_index_manifest()

assert_manifest_round_trips(
    manifest,
    expected_schema_version="1",
    require_no_loaded_payloads=True,
)
```

Tests should still show the public construction path clearly. Helpers provide
consistent assertions; they do not hide the behavior under a support-level
framework.

### Narrow Durable Goldens

Most Stage 14 data is generated. Checked-in golden files are allowed only for
small durable public artifact formats, such as public index manifests, export
manifests, derived datasource fingerprints, or schema examples.

Goldens must not snapshot private helper internals, loaded arrays, open file
handles, broad object dictionaries, or backend-specific layouts that are not a
public artifact contract.

### Package And Import Hardening

Stage 14 strengthens package tests so the public API stays deliberate:

- no public `rphys.testing`
- no public `rphys.fixtures`
- no placeholder public dataset or workflow package
- no root convenience re-exports
- no production import from `tests.support`
- no heavy optional dependency imported by lightweight package paths
- no public Stage 13 name frozen until it is code-backed

This lets test support grow without accidentally becoming library API.

## Stage 13 Alignment

Stage 14 originally planned the final smoke tail in generic
prediction/evaluation/analysis/report terms. Stage 13 has since been revised to
a Sample/Batch-native design, so Stage 14 consumes that shape.

The Stage 13-aligned smoke path is:

```text
synthetic datasource scan
-> filter/group/split
-> index manifest
-> lazy SampleBuilder
-> SampleOperationPipeline
-> BatchCollater
-> Method or Learner returns Batch fields
-> explicit Batch-to-Sample uncollation policy
-> sample-granular export/save
-> generic sample artifact datasource reload
-> runtime SampleCollection grouping/sorting/stitching
-> metric-as-sample-or-collection operation fields
-> visualization/report records or report fields
-> final validation evidence
```

Stage 14 must not reintroduce rejected Stage 13 surfaces. In particular, the
smoke path must not depend on public `PredictionRecord`,
`PredictionCollection`, `PredictionCollector`, `EvaluationRunner`,
`EvaluationPlan`, `EvaluationResult`, `MetricObservationCollection`,
`MetricObservationView`, `MetricResult`, `AnalysisOp`, `AnalysisContext`, or
`AnalysisResult` surfaces unless a later approved code-backed Stage 13 change
reopens those decisions.

Evaluation-like behavior is demonstrated through generic operations,
collections, metric fields, export/save handoff, and reports. Reporting remains
dependency-light and side-effect free by default; report file writers, plotting
backends, dashboards, and workflow runtimes remain outside Stage 14.

## Phase Behavior

Phase 1 builds the private fixture catalog and edge-variant vocabulary. It owns
`tests/support`, first consuming tests, and concise support-governance docs.

Phase 2 turns those fixtures into reusable executable invariants. It owns
private assertion helpers, contract tests, package/import tests, and any narrow
durable golden examples.

Phase 3 composes the code-backed upstream smoke path through current public
APIs. If Stage 13 code-backed behavior is not present in the active checkout,
this phase stops before the Stage 13 tail and labels the smoke incomplete.

Phase 4 completes the full Stage 13-aligned smoke tail only when the revised
Stage 13 behavior is present, code-backed, tested, and approved in the active
checkout. In a checkout where the Stage 13 public package homes are still
empty, Phase 4 remains prerequisite-gated. In a checkout where Stage 13 has
landed, Phase 4 starts by rechecking the code-backed public contracts and then
extends the smoke through the real Stage 13 APIs.

## Validation Behavior

Default Stage 14 validation stays local, deterministic, CPU-only, and
dependency-light. Debug, smoke, and signal tiers differ by fixture breadth,
variant count, and runtime cost. They must not use different loader or
materialization semantics.

Expected checks include:

- `make test-package` for public import and forbidden-boundary checks
- `make test-contract` for public object-model invariants
- `make test-integration` for synthetic composition and export/reload flows
- `make test-e2e` only if the full smoke belongs in e2e placement
- `make test-summary`, `make validate-pr`, `uv lock --check`, and
  `git diff --check` for final phase validation

Acceptance and real-data checks remain deferred unless separately approved.

## Design Boundaries

Stage 14 does not add:

- public fixture APIs
- production fixture modules
- placeholder Stage 13 exports
- a support-level runner or registry
- real datasource adapters
- raw datasets
- workflow runtime ownership
- artifact stores
- dashboards or plotting backends
- profiling or optimization work
- broad golden snapshots

The implementation should be comprehensive inside the approved testing scope:
more fixture families, more edge variants, stronger contract coverage, and
clearer smoke validation are encouraged. That comprehensiveness must still use
private support helpers, public `rphys` paths, tiny synthetic data, explicit
provenance, and fail-loud scientific behavior.

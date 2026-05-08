# Stage 1 Planning Notes: Public Architecture Contracts

## Metadata

- Roadmap slug: `public-architecture-contracts`
- Plan number: `01`
- Status: accepted
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/00-field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Master plan: `docs/implementation/01-public-architecture-contracts/master-plan.md`
- Implementation plan: `docs/implementation/01-public-architecture-contracts/implementation-plan.md`
- Current focus: ready for sequential Stage 3 implementation
- Blocker: GitHub CLI authentication is invalid for `samcantrill`, blocking PR creation and merge until refreshed.

## Context Readout

`rphys` is the domain-specific remote physiological measurement package. Generic experiment machinery belongs in `loom`; `rphys` may depend on `loom`, but `loom` must not depend on `rphys`.

The first scaffold package should define stable public architecture contracts before deeper runtime, dataset, transform, training, or evaluation APIs harden. The package should lock module ownership and extension policy, not detailed method signatures.

## Accepted Behavior

- The first stable public module wave is `rphys.data`, `rphys.io`, `rphys.datasets`, `rphys.transforms`, and `rphys.errors`.
- `rphys.methods`, `rphys.training`, `rphys.losses`, `rphys.evaluation`, `rphys.analysis`, `rphys.recipes`, and `rphys.stages` remain future/provisional and should not be importable in this package.
- Method signatures and concrete runtime behavior are deferred to the later owning work packages.
- A thin package skeleton is allowed only as executable documentation: package markers, module docstrings, broad error classes, and import tests.
- Stable placeholder domain classes are out of scope. Do not add stable `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, `SampleTransform`, method, loss, metric, model, recipe, stage, or testing objects in this package.
- Generic workflow, config composition, `_target_` instantiation, recipe expansion, DAG execution, run stores, artifact stores, executor behavior, resume, locking, and generic resource mechanics belong to `loom`.

## Design Decisions

| Decision | Status | Rationale | Follow-up |
| --- | --- | --- | --- |
| Use stable, provisional, and private/internal API labels | accepted | Compatibility promises need to be explicit while the public surface is still forming. | Later packages must label public behavior before relying on it downstream. |
| Keep first-wave stable modules narrow | accepted | `data`, `io`, `datasets`, `transforms`, and `errors` unblock later core packages without freezing learning/evaluation too early. | Later packages add their own homes deliberately. |
| Put lazy external field access under future `rphys.io` | accepted | `FieldRef`, `TemporalIndexSlice`, and `FieldView` are IO/lazy access concerns, not in-memory data-container concerns. | Dataset/IO plan owns exact signatures. |
| Use code-backed docs | accepted | Handwritten API references drift once implementation exists. | Contract docs explain policy and link to code/API reference as behavior lands. |
| Use `RemotePhysError` as the root error | accepted | Readable naming is clearer than `RPhysError`. | Broad families land in this package; detailed errors land with behavior packages. |
| Default user extension mechanism is `_target_` import paths | accepted | Experiment-local code should not need global registration. | Generic instantiation remains in `loom`. |
| Limit registries to symbolic names | accepted | Registries are useful for codec keys, built-in datasets, field schema names, and later metric/recipe names, not every extension object. | Later packages justify each registry. |
| Keep base imports lightweight | accepted | Base package imports should not require video, signal, torch, training, or analysis stacks. | Optional extras are refined when real backends exist. |
| Use uv and Python 3.12 | accepted | uv gives one modern dependency and environment workflow; Python 3.12 is the project floor. | Package metadata and lockfile land in Phase 2. |
| Keep rights all reserved until a license is selected | accepted | The maintainer has not selected a public-use license. | Replace placeholder before publication, distribution, or external reuse. |
| Implement in four sequential phases | accepted | Docs/policy, tooling, package skeleton, and validation are different review surfaces. | Each phase must merge and clean up before the next starts. |

## Goals

- Define the `loom`/`rphys` boundary.
- Document public API stability labels and obligations.
- Establish first-wave module ownership without freezing concrete signatures.
- Establish central broad `RemotePhys*Error` families.
- Document `_target_`, registry, optional dependency, and code-backed docs policy.
- Establish uv/Python/repository-governance expectations.
- Add persistent tests/checks that make the architecture contract executable.

## Non-Goals

- Runtime field containers, `Sample`, `Batch`, collation, or metadata behavior.
- Dataset references, codecs, adapters, indexes, and sample builders.
- Transforms, augmentation, checks, pipelines, exporters, and materialization behavior.
- Methods, models, learners, trainers, losses, predictions, metrics, evaluation, analysis, recipes, or stages.
- Generic `loom` infrastructure inside `rphys`.
- Heavy optional dependencies in the base install.
- Selecting a real open-source or public-use license.

## Validation Goals

- Import smoke checks for `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- Error hierarchy tests for broad `RemotePhys*Error` classes.
- Documentation checks for API labels, `loom` boundary, extension policy, registry limits, dependency policy, Python baseline, rights status, and scientific-contract obligations.
- Static/search checks that prevent generic workflow infrastructure and stable placeholder domain exports from appearing in this package.
- `uv lock --check`, targeted pytest, full pytest when available, and `git diff --check`.

## Assumptions And Risks

- Optional extras remain category-level until concrete backend implementations exist.
- Cross-repo enforcement that `loom` never imports `rphys` remains documented until a shared check exists.
- The temporary all-rights-reserved placeholder must be revisited before any publication or external distribution.
- Later behavior packages still need their own detailed API and scientific-contract reviews before marking signatures stable.

## Handoff

Stage 2 and Stage 3 should use:

- `docs/implementation/01-public-architecture-contracts/master-plan.md`
- `docs/implementation/01-public-architecture-contracts/implementation-plan.md`
- `docs/roadmap/index.md`
- `AGENTS.md`

# Contributing

`rphys` is being rebuilt as a small base library for remote physiological
measurement research. Keep contributions scoped to reusable package behavior;
full experiments and heavy project workflows belong in downstream repositories.

## Local Setup

Use Python 3.12 and `uv`.

```bash
uv sync
uv run pytest
```

Useful wrappers:

```bash
make setup-help
make dev-help
make test-help
make sync
make lock-check
make test
make test-summary
make validate-pr
make check
```

## Testing Structure

Tests are grouped by intent. See `tests/README.md` for the full structure.

- `tests/package`: package import, public API, metadata, and import-boundary
  tests.
- `tests/unit/rphys`: source-mirrored tests for isolated code under
  `src/rphys`.
- `tests/contracts`: executable public contracts for extension points and
  scientific semantics.
- `tests/integration`: tests that combine multiple `rphys` components using
  synthetic or tiny license-safe fixtures.
- `tests/e2e`: full behavior tests through public APIs.
- `tests/acceptance`: optional real-dataset, hardware, GPU, network, or
  long-running checks excluded from default validation.
- `tests/support`: trusted test-only helpers, fixtures, and synthetic
  generators; not a runnable suite by itself.

Use `make test-package`, `make test-unit`, `make test-contract`,
`make test-integration`, `make test-e2e`, and `make test-acceptance` for focused
suite runs. `make test` runs the default local suite and excludes tests marked
`slow`, `network`, `optional_dependency`, or `acceptance`.

Test execution and summary reporting are implemented in `tools/test_harness`.
Summary targets write Markdown reports and supporting artifacts under
`build/test-summary/`; use these reports as validation evidence in PR bodies.

Make targets are split by concern under `make/setup`, `make/dev`, and
`make/test`. Keep new targets in the relevant included file rather than growing
the root `Makefile`.

## Public Contracts

Public behavior needs code, docs, and tests before downstream projects rely on
it. Use the stability labels in `docs/roadmap.md`: stable, provisional, and
private/internal.

Do not add placeholder public modules, classes, registries, or re-exports just
to reserve future names. Future areas such as methods, models, training, losses,
evaluation, analysis, recipes, stages, ops, and testing need accepted plans
before becoming importable package homes.

## Scientific Documentation

Scientific components must document inputs, outputs, units, shapes, dtypes,
coordinate conventions, sampling rates, temporal alignment, normalization order,
leakage risks, split assumptions, and failure behavior. Tests should cover edge
cases such as NaNs, flat signals, short inputs, missing fields, empty masks,
invalid sampling rates, dtype mismatches, and device mismatches when applicable.

Use synthetic fixtures or tiny license-safe fixtures only. Do not commit raw
datasets.

## Dependency Boundaries

Keep base imports lightweight. Heavy video, signal-processing, torch, plotting,
analysis, dataset-SDK, and documentation stacks should be optional and grouped
by capability only when concrete code needs them.

`rphys` may depend on `loom`; `loom` must not depend on `rphys`. Generic config,
artifact, execution, recipe expansion, sweep, and stage-running machinery belongs
in `loom`, not this package.

Users should extend `rphys` with importable objects referenced through `_target_`
paths. Registries are reserved for cases where symbolic names are part of the
domain contract.

## Rights Status

No public-use license has been selected. The repository is all rights reserved
until the maintainer replaces the placeholder `LICENSE` with a real license.
Do not publish or distribute package artifacts while this placeholder remains in
effect.

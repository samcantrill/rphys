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
make sync
make lock-check
make test
make check
```

## Public Contracts

Public behavior needs code, docs, and tests before downstream projects rely on
it. Use the stability labels in `docs/architecture/public-contracts.md`:
stable, provisional, and private/internal.

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

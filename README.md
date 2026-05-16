# rphys

`rphys` is a Python package for remote physiological measurement research,
providing reusable domain components for data, preprocessing, signal
processing, models, training, evaluation, and analysis.

This repository is being rebuilt as a clean base library. The canonical
architecture, implementation order, public API policy, and scientific contract
rules live in `docs/roadmap.md`.

Start with:

- `AGENTS.md` for Codex and contributor instructions.
- `docs/roadmap.md` for the current implementation roadmap and public architecture policy.

## Current Status

The rebuild has implemented public contracts for naming vocabulary, runtime
field containers, lazy IO descriptors, datasource/index descriptors and
validation records, codec contracts, explicit codec registries, lazy
`SampleField` handles, one-item `SampleBuilder` construction from `IndexItem`
descriptors, generic operations, Stage 7 sample/batch operation families,
export primitives, prepared/cache/data-path records, method/model contracts,
loss/objective/metric records, and Stage 12 learner/trainer contracts. Later
roadmap stages still own prediction materialization, evaluation/report
generation, real external training-framework adapters, deep profiling, real
codec catalogs, concrete algorithm catalogs, and project-specific workflows.

Public API stability requires code, tests, and roadmap or docstring coverage to
agree on the contract. Focused modules such as `rphys.io.codecs`,
`rphys.data.sample_fields`, `rphys.data.sample_builders`, and `rphys.ops` are
canonical homes for implemented names when package tests cover their public
exports. The package root intentionally stays small.

Core imports are intentionally lightweight. Importing `rphys`, `rphys.errors`,
or the planned package homes must not import optional scientific, video,
plotting, dataframe, or deep-learning stacks.

## Boundaries

`rphys` owns reusable remote-physiology library contracts and primitives. It
does not implement generic project configuration, workflow engines, artifact
stores, schedulers, or stage runtimes; those belong in downstream projects or
generic orchestration libraries such as `loom`.

This repository is currently all rights reserved. No public-use license has
been selected.

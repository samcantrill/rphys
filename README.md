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

Milestone 0 provides the repository skeleton and governance baseline. Planned
package homes are importable, but they intentionally expose empty `__all__`
surfaces until behavior is documented and tested. Public API stability requires
code, tests, and roadmap or docstring coverage to agree on the contract.

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

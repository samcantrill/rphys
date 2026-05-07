# Master Implementation Plan: Public Architecture Contracts

Status: implementing
Roadmap item: [docs/roadmap/index.md](/home/samcantrill/work/rphys/docs/roadmap/index.md)
Roadmap slug: `public-architecture-contracts`
Planning notes: [planning-notes.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/planning-notes.md)
Owner: main Codex agent
Draft pass: complete
Refine pass: complete
Quality gate: passed
Blockers: GitHub CLI authentication is invalid for `samcantrill`, blocking PR creation and merge until re-authenticated
Stage 3 status: Phase 0 playbooks complete; Phase 1 implementation planning is next

## Summary

This work package establishes the first public architecture contract for `rphys`: a narrow, documented, executable scaffold for the package boundary, first-wave public module homes, API stability labels, central error hierarchy, `loom` dependency direction, uv-managed packaging, repository contribution/tooling conventions, optional dependency policy, and future public module map.

Successful completion gives later contributors and implementation agents stable places to put domain behavior without locking premature class/function signatures. The implementation is intentionally thin: it creates package/module homes and broad cross-cutting errors, but it does not implement data containers, lazy IO objects, dataset adapters, transforms, methods, training, losses, or evaluation behavior.

## Behavior Model

- User-visible behavior:
  - Users can import `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
  - Users can import broad error base classes from `rphys.errors`.
  - Users can read architecture documentation that explains stable, provisional, and private/internal API labels, the first-wave module boundary, future module names, `_target_` extension rules, registry use, optional dependency expectations, and the strict `loom`/`rphys` ownership boundary.
  - Contributors can use uv project commands and Makefile wrappers for setup and validation once the tooling phase lands.
  - Users do not receive working `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, `SampleTransform`, or similar runtime objects from this package.
- Agent-visible behavior:
  - Stage 3 agents have four ordered implementation phases with mostly disjoint file ownership: contract docs/policy, repository tooling/governance, package/error skeleton, then persistent validation.
  - Later roadmap packages must treat this master plan and the resulting package skeleton as the boundary contract, then define concrete signatures inside their owning packages.
  - Agents should update docs to point toward implemented code/API reference once concrete behavior exists, rather than maintaining duplicate handwritten API references.
- Supported workflows:
  - Import smoke checks for the package and first-wave module homes.
  - Error hierarchy checks for the broad `RemotePhys*Error` families.
  - Static/search checks that prevent generic `loom` infrastructure from being introduced into `rphys`.
  - Lightweight documentation review for architecture boundaries and public API stability policy.
- Unsupported workflows:
  - Running any dataset scan, field IO, transform pipeline, materialization/export, training, loss, or evaluation workflow.
  - Importing placeholder public domain classes such as `DataKey`, `FieldRef`, `DatasetRef`, or `SampleTransform` before their owning work packages implement accepted behavior.
  - Using `rphys` as a generic workflow engine, config composition engine, `_target_` instantiation engine, DAG runner, run store, artifact store, executor, resume planner, sweep runner, or locking system.
- Failure and stop behavior:
  - Unsupported implemented members, if any are intentionally importable, must be labeled provisional and raise explicit `NotImplementedError`; none are planned for this phase.
  - Stable symbols must not exist unless they are documented, importable, and covered by tests.
  - Stage 3 must stop if implementing this scaffold requires changing accepted module ownership, error naming, dependency direction, or API-label policy.
- Resume behavior after context compaction:
  - Resume from this file, [planning-notes.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/planning-notes.md), [docs/roadmap/index.md](/home/samcantrill/work/rphys/docs/roadmap/index.md), `AGENTS.md`, and `.codex/workflows/stage-3-managed-implementation.md`.
  - Treat Stage 1 decisions as stable unless the maintainer explicitly reopens them.

## Goals

- Establish the first stable importable package spine: `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
- Define broad central error bases under readable `RemotePhys*Error` names.
- Document API stability labels and obligations: stable, provisional, and private/internal.
- Document the strict one-way dependency boundary: `rphys` may depend on `loom`; `loom` must not depend on `rphys`.
- Document first-wave, later-wave, and future/provisional module ownership without freezing method signatures.
- Document extension policy: `_target_` import paths by default; registries only where symbolic names are useful.
- Keep base imports lightweight and avoid optional dependency leakage.
- Establish uv as the package/dependency workflow with `pyproject.toml`, `.python-version`, committed `uv.lock`, and Makefile command wrappers.
- Add contributor/governance files that document repository setup, testing, dependency policy, scientific contract expectations, and the temporary all-rights-reserved status until a license is selected.
- Add an explicit architecture refactor-risk gate before Stage 3 so long-term API and extension decisions are reviewed against `docs/rphys_architecture_plan_v3.md`.
- Add focused tests/checks so the skeleton is executable documentation for later work.

## Non-Goals

- Implementing `DataKey`, `FieldSpec`, `FieldValue`, `Sample`, `Batch`, collation, field metadata, or data object traversal.
- Implementing `FieldRef`, `TemporalIndexSlice`, `FieldView`, `DatasetRef`, `RecordRef`, `IndexItem`, codecs, adapters, indexes, or sample builders.
- Implementing transform, augmentation, check, pipeline, exporter, or materialization behavior.
- Implementing `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing` module homes.
- Recreating generic `loom` machinery in `rphys`.
- Adding broad placeholder classes that look stable before behavior is accepted.
- Freezing exact optional dependency package lists beyond documenting likely extras.
- Creating a duplicate handwritten API reference that must be maintained separately from code.
- Installing heavy optional stacks, dataset-specific dependencies, or training frameworks in the base environment.
- Choosing an open-source or public-use license before explicit maintainer selection.

## Design Decisions

| Decision | Status | Alternatives Considered | Rationale | Maintainability/Extensibility Impact | Validation Obligation | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| Start with a thin contract skeleton, not runtime behavior | accepted | Implement first runtime classes now; create many `NotImplementedError` placeholders | The maintainer prioritized API structure and avoiding lock-in. Concrete behavior belongs in later owner packages. | Reduces premature public commitments and keeps later package reviews meaningful. | Import smoke tests must pass without exposing unimplemented stable domain classes. | Later packages still need careful signature review before stabilization. |
| First stable module wave is `data`, `io`, `datasets`, `transforms`, plus `errors` | accepted | Include learning/evaluation modules now; include all broad v3 modules now | This is the smallest spine needed for later field, dataset, IO, and transform packages. | Keeps public surface narrow while reserving coherent homes for future behavior. | Tests import exactly these first-wave homes and errors. Docs list later-wave modules as future/provisional only. | Users may expect `methods` or `evaluation`; docs must make the deferral explicit. |
| Do not create future module homes in this phase | accepted for this plan | Create empty `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, and `stages` packages | Importable empty modules can be mistaken for usable or stable public APIs. | Prevents accidental lock-in and pushes concrete module creation to owning packages. | Import tests should not require later modules. Docs should document them as reserved future areas. | Later work must add these modules deliberately. |
| Use three API labels: stable, provisional, private/internal | accepted | No labels; semantic versioning only; use `NotImplementedError` as a pseudo-tier | Labels communicate compatibility promises. `NotImplementedError` communicates missing runtime behavior, not stability. | Gives downstream users and agents clear compatibility rules. | Contract docs define obligations and examples for each label. Tests cover stable imports only. | Labels need discipline in later packages; review gates should enforce them. |
| Use code-backed docs, not duplicate API docs | accepted | Handwrite detailed API reference now; rely only on code/docstrings | Planning docs need policy and rationale, but duplicated signatures drift. | Keeps long-term docs maintainable and lets implementation become the contract. | Docs must state that API reference should point to implemented code once available. | Documentation tooling may change later; this plan avoids choosing it now. |
| Root error is `RemotePhysError`, not `RPhysError` | accepted | `RPhysError`; package-specific roots only | The maintainer preferred readable naming and asked to avoid `RPhysError`. | Provides consistent diagnostic inheritance without abbreviation ambiguity. | Unit tests assert hierarchy and import paths. | Future detailed errors must remain under these broad bases. |
| Broad error families only | accepted | Implement detailed domain errors now; no error hierarchy yet | Detailed errors belong to owner packages where behavior is known. Broad families are cross-cutting enough to add now. | Enables consistent later package-specific errors without over-designing. | Unit tests cover `RemotePhysError`, `RemotePhysDataError`, `RemotePhysIOError`, `RemotePhysDatasetError`, `RemotePhysTransformError`, `RemotePhysTrainingError`, and `RemotePhysEvaluationError`. | Later packages may need additional broad families; adding subclasses is acceptable. |
| `rphys.io` owns lazy external field access concepts | accepted | Put `FieldRef`, `TemporalIndexSlice`, and `FieldView` under `rphys.data` | Maintainer confirmed IO ownership for lazy external field access. This package documents the owner but does not implement the classes. | Prevents data containers from absorbing IO concerns. | Docs must record ownership and future package handoff. | Later dataset/IO planning must coordinate exact signatures. |
| Strict one-way `loom`/`rphys` dependency boundary | accepted | Let `loom` import `rphys`; duplicate generic workflow pieces in `rphys` | `rphys` is domain-specific and layered on generic `loom` infrastructure. | Avoids cyclic ownership and duplicate workflow engines. | Static/search checks reject generic infrastructure names and `loom` importing `rphys` is documented as forbidden. | Real import-boundary enforcement across both repos may need later cross-repo checks. |
| `_target_` import paths are the default user-extension mechanism | accepted | Require registry registration for all extensions; implement plugin discovery now | Experiment-local code should work through import paths while generic instantiation remains in `loom`. | Keeps `rphys` extensible without central registration bottlenecks. | Docs explain `_target_` policy and that the instantiation engine belongs to `loom`. | Future plugin discovery may be added later without changing this default. |
| Registries are limited to symbolic names | accepted | Global registries for every transform, method, model, loss, metric, adapter | Registries are useful for symbolic names, not every extension object. | Prevents global state from constraining extension code. | Docs list registry-appropriate uses: codec keys, built-in dataset names, standard field schema names, later metric/recipe names. | Later packages must resist convenience registries that become mandatory. |
| Keep optional dependencies out of base imports | accepted | Put video/signal/torch/training/analysis dependencies in base package | The core scaffold should remain lightweight. | Makes import smoke tests reliable and reduces install friction. | Import tests run without optional stacks. Docs list likely extras without freezing exact packages. | Packaging extras will need refinement once actual backends exist. |
| Use uv-managed project metadata | accepted | Plain pip-only editable install; setup.cfg/setup.py; defer package metadata | Maintainer wants uv. uv requires `pyproject.toml` to identify the project root and manages project environments from that metadata. | Gives the repo one modern dependency/package source of truth and avoids parallel requirements files. | Phase 2 must add `pyproject.toml`, `.python-version`, `uv.lock`, and Makefile wrappers; validation should use `uv run`/`uv lock --check`; build backend must be `uv_build` with `requires = ["uv_build>=0.11.6,<0.12"]` and `build-backend = "uv_build"`. | If future extension modules are introduced, the build backend must be revisited before implementation. |
| Commit `uv.lock` for reproducible development | accepted | Ignore lockfile for a library; generate lockfile only in CI | uv lockfiles are cross-platform and intended to be checked into version control for consistent developer environments. | Keeps agent, maintainer, and CI environments aligned while published metadata remains broad in `pyproject.toml`. | Phase 2 must run `uv lock` and Phase 4 must check `uv lock --check`. | Lockfile diffs may be noisy when optional groups change. |
| Keep base install light and use feature extras plus dependency groups | accepted | Put all scientific dependencies in base; use one `dev` extra for everything; split into many namespace packages | Base `rphys` should import without video, signal, torch, or training stacks. Published extras serve users; uv dependency groups serve local development. | Preserves lightweight core imports and lets dataset/IO/training modules declare only the dependencies they need. | Contract docs and tests must distinguish `[project.optional-dependencies]` from `[dependency-groups]` and check base imports do not import heavy stacks. | Exact package pins are deferred to the owning behavior packages. |
| Python version policy starts at 3.12 | accepted | Support Python 3.10 or 3.11; require only latest Python; support every current Python indefinitely | Maintainer indicated Python 3.12 is the right baseline. Python 3.12 is modern enough for current typing/tooling while avoiding the newest-interpreter lag that can affect scientific/training packages. | Gives implementation agents a clear floor and keeps support narrower than a broad legacy matrix. | Phase 2 records `requires-python = ">=3.12"` in `pyproject.toml` and `.python-version` as `3.12`; later CI should test the supported matrix. | Optional training/analysis extras may still need dependency markers if upstream packages lag newer Python releases. |
| Add repository governance and command interface | accepted | Keep only AGENTS.md; rely on raw uv commands; add full docs site now | Human contributors need concise setup and contribution instructions, agents need stable command names, and the repo needs an explicit temporary rights status. | `CONTRIBUTING.md` and `Makefile` make tests/checks discoverable without duplicating policy-heavy docs; a temporary `LICENSE` placeholder prevents accidental permission grants. | Phase 2 must add command wrappers, contributor guidance, and a temporary all-rights-reserved `LICENSE` placeholder. | The real project license remains deferred and must replace the placeholder later. |
| Split implementation into four phases | accepted | Keep one combined phase; keep three phases and fold tooling into package skeleton; split every file type into separate micro-phases | The accepted behavior is thin, but docs, uv/repo tooling, package code, and validation are operationally different enough that one phase would be too large to review cleanly. | Keeps policy review, tooling decisions, code skeleton, and persistent checks independently reviewable. | Each phase needs its own playbook, acceptance evidence, and pathway decision. | Phase 4 may expose a defect in Phase 2 or Phase 3, requiring a small blocker fix before merge. |
| Add an architecture refactor-risk gate | accepted | Rely on normal master-plan review only; defer future-proofing checks to later work packages | Maintainer explicitly requested long-term extensibility and future-proofing against `docs/rphys_architecture_plan_v3.md`. | Makes high-cost refactor risks visible before Stage 3 and prevents implementation agents from hardening weak ownership or extension decisions. | Quality gate must include `docs/implementation/public-architecture-contracts/architecture-refactor-risk-review.md`, covering module ownership, dependency direction, extension points, data contracts, optional dependencies, and deferred decisions. | The gate can identify risks but later work packages still need their own detailed API reviews. |

## Structure And Extensibility

- Directory/module structure:
  - `pyproject.toml`: uv/project metadata, build backend, Python requirement, lightweight base dependencies, optional feature extras, and tool configuration.
  - `.python-version`: default local uv-managed interpreter version.
  - `uv.lock`: committed universal lockfile for reproducible development.
  - `Makefile`: thin command wrapper around uv commands; uv/pyproject remain the source of truth.
  - `CONTRIBUTING.md`: contributor setup, uv workflow, test commands, API-label obligations, scientific-contract expectations, and dependency policy.
  - `LICENSE`: temporary all-rights-reserved placeholder; replaced later only after explicit maintainer license selection.
  - `src/rphys/__init__.py`: package marker and high-level docstring. It should avoid broad re-exports until concrete public behavior exists.
  - `src/rphys/errors.py`: broad `RemotePhys*Error` hierarchy.
  - `src/rphys/data/__init__.py`: first-wave stable module home with docstring only.
  - `src/rphys/io/__init__.py`: first-wave stable module home with docstring only.
  - `src/rphys/datasets/__init__.py`: first-wave stable module home with docstring only.
  - `src/rphys/transforms/__init__.py`: first-wave stable module home with docstring only.
  - `docs/architecture/public-contracts.md`: public architecture and stability policy, linked to planning artifacts and future code-backed docs.
  - `tests/`: focused import, error hierarchy, docs policy, and boundary checks.
- Ownership boundaries:
  - This package owns module homes, broad errors, contract policy docs, and persistent checks for those boundaries.
  - Later field-runtime work owns `DataKey`, `FieldSpec`, `FieldValue`, `Sample`, `Batch`, collation, and data object behavior.
  - Later dataset/IO work owns `DatasetRef`, `RecordRef`, `FieldRef`, `TemporalIndexSlice`, `FieldView`, codecs, adapters, indexes, and sample building.
  - Later transform/materialization work owns transform base classes, pipelines, checks, exporters, and materialization behavior.
  - Later learning/evaluation work owns methods, training, losses, prediction samples, metrics, and evaluation protocols.
- Dependency direction:
  - `rphys` may depend on `loom` where generic infrastructure is needed.
  - `loom` must not depend on `rphys`.
  - First-wave package imports must avoid heavy optional stacks.
  - Domain modules must not import future optional stacks at base import time.
  - `[project.dependencies]` should stay empty or minimal until concrete code requires a runtime dependency.
  - `[project.optional-dependencies]` should hold published user feature extras such as video, signal, torch, training, and analysis.
  - `[dependency-groups]` should hold local-only dev/test/lint/docs dependencies used by uv and contributors.
- Extension points:
  - `_target_` import paths for user-defined extension objects.
  - Registries only for symbolic names such as codec keys, built-in dataset names, standard field schema names, and later metric/recipe names.
  - Public module homes for future owner packages, but no stable signatures before implementation.
- Coupling intentionally avoided:
  - No generic workflow engine in `rphys`.
  - No dataset formatting inside `rphys.datasets`.
  - No IO semantics inside `rphys.data`.
  - No global registration requirement for every extension type.
  - No placeholder stable domain classes.
- Expected future changes this structure should absorb:
  - Adding concrete field/runtime classes under `rphys.data`.
  - Adding lazy IO and codec behavior under `rphys.io`.
  - Adding dataset references/adapters/indexing under `rphys.datasets`.
  - Adding transform and materialization behavior under `rphys.transforms`.
  - Adding learning and evaluation module homes once their prerequisite contracts are accepted.

## Public Interfaces And Documents

- Files or docs allowed to change:
  - [docs/roadmap/index.md](/home/samcantrill/work/rphys/docs/roadmap/index.md)
  - [docs/implementation/public-architecture-contracts/master-plan.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/master-plan.md)
  - `docs/architecture/public-contracts.md`
  - `README.md` links if needed
  - `pyproject.toml`
  - `.python-version`
  - `uv.lock`
  - `Makefile`
  - `CONTRIBUTING.md`
  - `LICENSE` as a temporary all-rights-reserved placeholder
  - `src/rphys/__init__.py`
  - `src/rphys/errors.py`
  - `src/rphys/data/__init__.py`
  - `src/rphys/io/__init__.py`
  - `src/rphys/datasets/__init__.py`
  - `src/rphys/transforms/__init__.py`
  - `tests/test_public_imports.py`
  - `tests/test_error_hierarchy.py`
  - `tests/test_public_contract_docs.py`
  - `tests/test_dependency_boundaries.py`
- Public behavior or conventions introduced:
  - Importable first-wave modules listed above.
  - Broad error classes:
    - `RemotePhysError`
    - `RemotePhysDataError`
    - `RemotePhysIOError`
    - `RemotePhysDatasetError`
    - `RemotePhysTransformError`
    - `RemotePhysTrainingError`
    - `RemotePhysEvaluationError`
  - API labels: stable, provisional, private/internal.
  - `_target_` default extension rule and limited registry policy.
  - uv-managed development with `pyproject.toml`, `.python-version`, committed `uv.lock`, and Makefile wrappers.
  - Python baseline: `requires-python = ">=3.12"` and local `.python-version` `3.12`.
  - Temporary rights status: no open-source or public-use license is granted; all rights are reserved until the maintainer selects a real license.
  - Optional extras names as likely user-facing categories, not frozen package lists: `rphys[video]`, `rphys[signal]`, `rphys[torch]`, `rphys[training]`, and `rphys[analysis]`.
  - Local-only uv dependency groups for development tools, such as `dev`, `test`, `lint`, and `docs`; these are not published user extras.
- Compatibility constraints:
  - Stable names must not be removed or behaviorally narrowed without an explicit compatibility decision.
  - Provisional names may change before stabilization but must be labeled.
  - Private/internal modules have no compatibility promise.
  - A skeleton member that raises `NotImplementedError` must be provisional, never stable.

## Validation Strategy

- Behavior that must be tested:
  - First-wave module importability.
  - Error class importability and inheritance.
  - uv lockfile and project metadata consistency.
  - Temporary all-rights-reserved metadata consistency: no real license metadata, no public-use license file, and no uploadable public package classifier.
  - Absence of heavy optional dependency imports from base package and first-wave module homes.
  - Absence of generic workflow infrastructure introduced in `rphys`.
  - No stable placeholder classes are exported before behavior exists.
- Behavior that must be documented:
  - `loom`/`rphys` ownership boundary.
  - API-label obligations.
  - First-wave, later-wave, and future/provisional module map.
  - Error hierarchy policy.
  - `_target_`, registry, and optional dependency policies.
  - uv workflow, Python 3.12 baseline, Makefile command surface, and contributor setup.
  - Temporary all-rights-reserved status and replacement trigger for a future real license.
  - Code-backed docs policy.
- Behavior guarded by templates or workflow checks:
  - Stage 3 phase playbook must reference this master plan and planning notes.
  - PR body must list public interfaces added and explicitly confirm no runtime domain behavior was implemented.
  - Review checklist must confirm no out-of-scope placeholder classes were added.
- Synthetic fixtures or safe test data:
  - None required for this package. Later behavior packages should use synthetic fixtures.
- CI/static/check commands:
  - `uv lock --check`
  - `uv run pytest tests/test_public_imports.py tests/test_error_hierarchy.py tests/test_public_contract_docs.py tests/test_dependency_boundaries.py`
  - `uv run pytest` once a full test command exists.
  - `git diff --check`
  - `uv sync`
  - Documentation link checks if a docs checker exists; otherwise manual link review in the phase notes.
- Acceptance evidence required before merge:
  - Test output for focused tests.
  - `uv lock --check` output.
  - `git diff --check` output or a note isolating pre-existing unrelated failures.
  - Search evidence showing no generic workflow implementation was added to `rphys`.
  - Review evidence that stable/provisional/private labels are documented.
  - Review evidence that the architecture refactor-risk gate was completed and did not leave blocking findings.

## Implementation Phases

| Phase | Slug | Status | Branch | Worktree | Ownership | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `contract-docs-and-policy` | pending | `agent/public-architecture-contracts-p1-contract-docs-and-policy` | `../rphys-worktrees/public-architecture-contracts-p1-contract-docs-and-policy` | `docs/architecture/public-contracts.md`, README links if needed, roadmap implementation note | Public contract policy and ownership docs are reviewable before code exists |
| 2 | `repository-tooling-scaffold` | pending | `agent/public-architecture-contracts-p2-repository-tooling-scaffold` | `../rphys-worktrees/public-architecture-contracts-p2-repository-tooling-scaffold` | `pyproject.toml`, `.python-version`, `uv.lock`, `Makefile`, `CONTRIBUTING.md`, temporary `LICENSE` placeholder | uv-managed project metadata, Python 3.12 baseline, command wrappers, contributor guidance, and all-rights-reserved notice |
| 3 | `package-and-error-skeleton` | pending | `agent/public-architecture-contracts-p3-package-and-error-skeleton` | `../rphys-worktrees/public-architecture-contracts-p3-package-and-error-skeleton` | `src/rphys/__init__.py`, `src/rphys/errors.py`, first-wave `src/rphys/*/__init__.py` module homes | Minimal importable package and broad `RemotePhys*Error` hierarchy |
| 4 | `contract-validation` | pending | `agent/public-architecture-contracts-p4-contract-validation` | `../rphys-worktrees/public-architecture-contracts-p4-contract-validation` | `tests/test_public_imports.py`, `tests/test_error_hierarchy.py`, `tests/test_public_contract_docs.py`, `tests/test_dependency_boundaries.py` | Persistent tests/checks enforce the public contract skeleton |

### Phase 1: Contract Docs And Policy

- Goal:
  - Land the public architecture contract as a reviewable policy artifact before code skeleton decisions harden.
- Scope:
  - Add `docs/architecture/public-contracts.md`.
  - Document first-wave stable module homes, later-wave/future module map, API stability labels, `loom`/`rphys` dependency direction, code-backed docs policy, `_target_` extension rule, limited registry policy, optional dependency categories, and scientific-contract obligations for later packages.
  - Link the policy doc from `README.md` only if useful.
  - Update roadmap implementation text to point at this master plan and note the four-phase shape.
- Out of scope:
  - Any package code, `pyproject.toml`, tests, generated API docs, CLI entrypoints, recipes, stages, registries, or runtime domain behavior.
- Acceptance criteria:
  - The docs explain what is stable now, what is future/provisional, and what remains private/internal.
  - The docs clearly state that code becomes the contract once implementation exists and docs should reference code/API reference rather than duplicate signatures.
  - The docs preserve the strict `loom`/`rphys` boundary and do not assign generic workflow infrastructure to `rphys`.
  - Link targets added by this phase resolve.
- Test expectations by package, unit, contract, integration, e2e, and opt-in suites:
  - Package/unit/integration/e2e/opt-in: not required because this phase is docs-only.
  - Contract: manual review against Stage 1 planning notes and this master plan.
  - Static: `git diff --check`.
- Design impact:
  - Separates policy acceptance from packaging/code implementation.
  - Gives Phase 2 a concrete document to implement against.
- Future compatibility:
  - Later packages can append references to implemented code/API docs without rewriting the policy.
- Alternatives rejected:
  - Waiting to write contract docs until after code exists.
  - Embedding all architecture policy in module docstrings only.
- Debt introduced:
  - Docs will initially reference planned module homes before they are importable.
- Reviewability:
  - Docs-only PR with no code behavior.
- Completion summary:
  - To be filled during Stage 3 after implementation and validation.

### Phase 2: Repository Tooling Scaffold

- Goal:
  - Establish uv, Python 3.12, contribution guidance, and command wrappers before package code and tests depend on them.
- Scope:
  - Add `pyproject.toml` as the uv/project metadata source of truth.
  - Set `requires-python = ">=3.12"` and `.python-version` to `3.12`.
  - Use the uv native pure-Python build backend exactly as:
    - `requires = ["uv_build>=0.11.6,<0.12"]`
    - `build-backend = "uv_build"`
  - Keep `[project.dependencies]` empty or minimal because the first package skeleton should import without `loom`, torch, video, signal, or training stacks.
  - Document planned user extras in project comments or contract docs rather than publishing empty extras: `video`, `signal`, `torch`, `training`, and `analysis`.
  - Add uv dependency groups for local-only tooling, with at least test support for Phase 4; add lint/docs groups only if they are actually wired to commands.
  - Omit `license` and `license-files` metadata from `pyproject.toml` until the maintainer selects a real license.
  - Add the exact classifier `Private :: Do Not Upload` to `pyproject.toml` to prevent accidental PyPI publication while no real license is selected.
  - Generate and commit `uv.lock`.
  - Add a `Makefile` as a thin wrapper around uv commands such as `sync`, `lock`, `lock-check`, `test`, `check`, and `diff-check`.
  - Add `CONTRIBUTING.md` covering uv setup, dependency policy, testing, public API labels, scientific-contract expectations, temporary all-rights-reserved status, and the no-raw-datasets rule.
  - Add `LICENSE` as a temporary placeholder that states no license has been selected, all rights are reserved, and no permission is granted to use, copy, modify, distribute, sublicense, or sell the work except by explicit maintainer permission.
- Out of scope:
  - Package module code under `src/rphys/`.
  - Persistent tests except lock/tooling checks.
  - Heavy optional dependencies or real user extras with backend packages.
  - Selecting an open-source or public-use license.
  - CI workflows, release automation, docs site tooling, pre-commit hooks, or publishing configuration.
- Acceptance criteria:
  - `uv sync` succeeds for the base/dev environment.
  - `uv lock --check` passes.
  - `.python-version` and `pyproject.toml` agree on the Python 3.12 baseline.
  - `Makefile` targets are thin wrappers and do not become a second source of dependency truth.
  - `CONTRIBUTING.md` explains how to add dependencies without bloating base imports.
  - `LICENSE` is present as a temporary all-rights-reserved placeholder, not as an open-source license.
  - `pyproject.toml` omits real license and license-file metadata and includes the exact `Private :: Do Not Upload` classifier.
- Test expectations by package, unit, contract, integration, e2e, and opt-in suites:
  - Package/unit/integration/e2e/opt-in: not required because package code has not landed.
  - Contract: manual review of dependency groups versus optional extras.
  - Contract: manual review that rights metadata is all-rights-reserved and cannot be mistaken for a public license.
  - Tooling: `uv sync`, `uv lock --check`, and `make lock-check`.
- Design impact:
  - Makes uv the durable interface for agent and contributor commands.
  - Separates packaging/tooling decisions from public module code.
- Future compatibility:
  - Later packages can add exact extras and dependency markers when real backends exist.
  - Later CI can reuse Makefile/uv commands without inventing new entrypoints.
- Alternatives rejected:
  - Using raw pip/requirements files as the primary workflow.
  - Publishing an empty `dev` extra for contributor tooling.
  - Installing all optional scientific stacks in base.
  - Leaving rights status implicit until a real license is chosen.
- Debt introduced:
  - Exact optional dependency lists remain deferred.
  - The temporary `LICENSE` placeholder must be replaced once the maintainer selects a real license.
- Reviewability:
  - Tooling PR is limited to root project files and contributor guidance.
  - Review should reject heavy runtime dependencies in base.
- Completion summary:
  - To be filled during Stage 3 after implementation and validation.

### Phase 3: Package And Error Skeleton

- Goal:
  - Create the minimal importable package skeleton that matches the Phase 1 public contract policy and Phase 2 uv metadata.
- Scope:
  - Add `src/rphys/__init__.py` with a concise package docstring and no broad domain re-exports.
  - Add `src/rphys/errors.py` with `RemotePhysError`, `RemotePhysDataError`, `RemotePhysIOError`, `RemotePhysDatasetError`, `RemotePhysTransformError`, `RemotePhysTrainingError`, and `RemotePhysEvaluationError`.
  - Add first-wave module homes: `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
  - Use module docstrings and optional small `__all__` inventories only where they do not imply unavailable domain behavior.
- Out of scope:
  - Persistent tests, except ad hoc commands recorded as validation evidence.
  - Concrete domain class/function signatures beyond broad errors.
  - Placeholder domain classes that raise `NotImplementedError`.
  - Future module homes for `methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, or `testing`.
  - Runtime logic, IO, datasets, transforms, materialization, learning, evaluation, CLI entrypoints, stage execution, or recipe expansion.
- Acceptance criteria:
  - `uv sync` succeeds after the package skeleton is added.
  - Users can import `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
  - Broad error classes import and inherit from `RemotePhysError` as specified.
  - No broad domain placeholders are exported as stable API.
  - Base imports do not require optional video, signal, torch, training, or analysis stacks.
- Test expectations by package, unit, contract, integration, e2e, and opt-in suites:
  - Package smoke: ad hoc `uv run python -c ...` import command for first-wave modules and `rphys.errors`.
  - Unit: ad hoc `uv run python -c ...` assertion command for error inheritance.
  - Contract: manual check that no stable placeholder domain classes are exported.
  - Integration/e2e/opt-in: not required.
- Design impact:
  - Establishes executable public homes without freezing concrete signatures.
  - Makes broad diagnostic inheritance available for all later packages.
- Future compatibility:
  - Later packages can add concrete classes under the existing homes.
  - Later optional extras can be refined without changing base import behavior.
- Alternatives rejected:
  - Creating all modules from the v3 package tree now.
  - Adding `NotImplementedError` placeholders for expected future classes.
  - Putting lazy IO references under `rphys.data`.
  - Naming the root error `RPhysError`.
- Debt introduced:
  - The scaffold will have importable module homes with little functionality.
  - Optional extras remain categories, not exact dependency sets.
- Reviewability:
  - Code PR is limited to packaging, module homes, and broad errors.
  - Review should reject any concrete runtime/domain behavior beyond broad errors.
- Completion summary:
  - To be filled during Stage 3 after implementation and validation.

### Phase 4: Contract Validation

- Goal:
  - Add persistent checks that turn the accepted public architecture contract into enforceable repository behavior.
- Scope:
  - Add import smoke tests for `rphys`, `rphys.errors`, `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms`.
  - Add error hierarchy tests for broad `RemotePhys*Error` classes.
  - Add docs-policy tests or checks that verify the public contract doc contains the accepted API labels, `loom` boundary, extension policy, registry policy, uv/dependency policy, Python 3.12 baseline, and no stable placeholder promises.
  - Add dependency-boundary/search checks that fail if generic workflow infrastructure is introduced in `rphys` by this package.
- Out of scope:
  - Changing package code except for narrowly scoped blocker fixes if validation exposes a defect.
  - Adding runtime behavior or future module homes.
  - Adding synthetic data fixtures or optional dependency tests.
- Acceptance criteria:
  - Focused tests pass through `uv run pytest`.
  - `uv lock --check` passes.
  - Boundary checks confirm no generic `loom` infrastructure was implemented in `rphys`.
  - Validation records that no stable `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, transform, method, loss, or metric placeholder exists.
  - `git diff --check` passes for files touched by this phase or documents unrelated pre-existing failures.
- Test expectations by package, unit, contract, integration, e2e, and opt-in suites:
  - Package smoke: import first-wave modules and `rphys.errors`.
  - Unit: assert error class inheritance and string behavior inherited from `Exception`.
  - Contract: assert documented stable module inventory and absence of forbidden stable placeholder exports.
  - Integration: not required beyond editable install/import.
  - E2E: not required.
  - Opt-in optional dependency suites: not required.
- Design impact:
  - Makes the skeleton executable documentation for later packages.
  - Gives future packages a documented policy they must satisfy before marking symbols stable.
- Future compatibility:
  - Later packages can extend the tests when they add concrete stable behavior.
  - Later docs can reference generated API docs or code once behavior exists.
- Alternatives rejected:
  - Relying on manual review only.
  - Adding broad synthetic fixtures before runtime packages exist.
- Debt introduced:
  - Cross-repo enforcement that `loom` never imports `rphys` remains a documented boundary until a cross-repo check exists.
- Reviewability:
  - Validation PR should be mostly tests/checks. Any code or tooling fix required by the tests must be small, explained, and treated as a blocker fix.
- Completion summary:
  - To be filled during Stage 3 after implementation and validation.

## Pathway Guidance

- Standard pathway phases:
  - Phase 2 should use the standard pathway by default because it introduces uv package metadata, lockfile behavior, Makefile commands, and contributor/governance files.
  - Phase 3 should use the standard pathway by default because it introduces importable public module homes and broad public error classes.
- Fast-path eligible phases:
  - Phase 1 may be fast-path eligible if it remains docs-only and does not reopen accepted design decisions.
  - Phase 4 may be fast-path eligible if it remains limited to tests/checks and small validation text, with no runtime/domain code changes.
- Criteria that force standard pathway:
  - Adding any concrete `DataKey`, `Sample`, `DatasetRef`, `FieldRef`, transform, method, loss, or metric class.
  - Adding future module homes beyond the first wave.
  - Introducing a CLI, recipe, stage, registry implementation, config loader, plugin discovery, or `_target_` instantiation code.
  - Adding dependencies beyond minimal test/build tooling.
  - Changing accepted Stage 1 decisions.

## Validation And Tests

- Phase-specific commands:
  - Phase 1: `git diff --check -- docs/architecture/public-contracts.md docs/roadmap/index.md README.md`
  - Phase 2: `uv sync`
  - Phase 2: `uv lock --check`
  - Phase 2: `make lock-check`
  - Phase 3: ad hoc `uv run python -c ...` import/error assertions recorded in phase notes.
  - Phase 4: `uv run pytest tests/test_public_imports.py tests/test_error_hierarchy.py tests/test_public_contract_docs.py tests/test_dependency_boundaries.py`
  - Phase 4: `uv lock --check`
  - Each phase: `git diff --check`
- Full-suite command:
  - `uv run pytest`
- Documentation/link checks:
  - Run any docs link checker introduced by the repo.
  - If no checker exists, manually inspect links touched by this phase and record evidence in phase notes.
- TOML/config checks:
  - Verify `pyproject.toml` and `.python-version` agree on Python 3.12.
  - Verify `uv lock --check` after dependency metadata changes.
  - Do not add `loom` config files in this phase.

## Review Requirements

- Standard pathway code review focus:
  - Import behavior is stable and minimal.
  - Error hierarchy is broad, readable, and not over-specific.
  - Package metadata does not introduce heavy dependencies.
  - Tests are focused and do not require real data.
  - No unrelated refactors or generated churn.
- Standard pathway scientific/workflow review focus:
  - Docs preserve scientific-contract obligations for later packages: units, shapes, dtypes, coordinate frames, sampling rates, alignment, leakage risks, failure behavior, and validation tests.
  - Docs preserve the separation among dataset structure, lazy IO selection, runtime transforms, offline materialization, and learning/evaluation.
  - Docs keep generic workflow machinery in `loom`.
- Architecture refactor-risk review focus:
  - Verify first-wave stable modules are sufficient and do not force future runtime, dataset, transform, learning, or evaluation APIs into the wrong owner.
  - Verify `rphys.data`, `rphys.io`, `rphys.datasets`, and `rphys.transforms` boundaries match the v3 architecture separation among field containers, lazy IO, dataset references/indexing, and runtime/offline transforms.
  - Verify deferred module homes (`methods`, `training`, `losses`, `evaluation`, `analysis`, `recipes`, `stages`, `ops`, `models`, `testing`) are not accidentally hardened.
  - Verify `_target_` extension paths and limited registries leave room for user code, plugin discovery, and future standard registries without requiring global registration.
  - Verify optional dependency structure can absorb dataset-specific IO backends, torch/training stacks, analysis stacks, and future CI matrices without bloating base imports.
  - Verify all accepted deferrals from `docs/rphys_architecture_plan_v3.md` remain possible without changing the first package skeleton: collate policies, codec/export lists, mesh support, nested/multi-view samples, spatial/time slices, multi-member index items, entry-point plugins, self-supervised learners, signal-processing methods, materialization exporters, and reports.
  - Record any decision that could require major refactoring later as blocking, accepted risk, or explicit revisit trigger before Stage 3 starts.
- Fast-path manager checklist:
  - Scope limited to the owning phase's docs, repository tooling, module homes, broad errors, or tests.
  - No runtime scientific behavior added.
  - No heavy dependencies added.
  - No out-of-scope modules made importable.
  - Focused tests and diff checks pass or unrelated pre-existing failures are documented.
- Required review or checklist documents:
  - Phase 0 playbooks for `contract-docs-and-policy`, `repository-tooling-scaffold`, `package-and-error-skeleton`, and `contract-validation`.
  - [architecture-refactor-risk-review.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/architecture-refactor-risk-review.md) before Stage 3.
  - Phase notes with commands, results, risks, and scope confirmation.
  - Public PR body linking this master plan and planning notes.

## Discussion History

- Major question rounds:
  - Stage 1 split review accepted the six-package map and selected this package first because stable public API is the highest priority.
  - API scope review cut first-wave stable modules down to `data`, `io`, `datasets`, and `transforms`, plus central `errors`.
  - Design review confirmed strict `loom`/`rphys` ownership, future/provisional module map, code-backed docs, thin skeleton depth, `RemotePhysError` naming, registry policy, `_target_` extension policy, optional dependency policy, and API-label obligations.
  - Stage 1 phase shaping initially confirmed one small implementation phase.
  - Stage 2 maintainer review reopened phase shape because the combined docs, packaging, code skeleton, and validation work was too large operationally; the plan first moved to three phases.
  - Maintainer then confirmed uv, repository setup, Makefile, dependency-policy concerns, and Python 3.12 as the baseline; the plan now uses four phases.
  - Maintainer then deferred license selection, requested all rights reserved until selection, and requested explicit review of long-term refactor-risk and extensibility decisions against the v3 architecture.
- Decisions changed during discussion:
  - `FieldRef`, `TemporalIndexSlice`, and `FieldView` moved under `rphys.io` ownership instead of `rphys.data`.
  - The root error name changed from the architecture-note suggestion `RPhysError` to accepted `RemotePhysError`.
  - Broad placeholder skeleton classes were rejected in favor of module homes and broad errors only.
  - The Stage 2 phase plan changed from one combined phase to four ordered phases: docs/policy, repository tooling, package/errors, then validation.
  - The Phase 2 `LICENSE` file changed from selected-license output to a temporary all-rights-reserved placeholder, with real license metadata omitted from `pyproject.toml`.
  - A formal architecture refactor-risk gate was added before Stage 3.
- Open questions intentionally deferred:
  - Exact runtime signatures for all domain classes.
  - Exact optional dependency package lists.
  - Plugin discovery through Python entry points.
  - Detailed package-specific errors.
  - Generated API documentation tooling.
- Maintainer concerns addressed:
  - Avoids API lock-in by locking module homes before signatures.
  - Avoids restrictive global registries by defaulting to import paths for extensions.
  - Avoids duplicate docs by treating code as contract after implementation.
  - Avoids reimplementing `loom` infrastructure.
  - Makes temporary rights status explicit without choosing a real license.
  - Adds a targeted review for extension points and refactor risk before implementation hardens structure.

## Master Plan Quality Gate

- Initial review:
  - Completed in [master-plan-review-initial.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/master-plan-review-initial.md). Findings required one refinement pass.
- Architecture refactor-risk review:
  - Completed in [architecture-refactor-risk-review.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/architecture-refactor-risk-review.md). No blocking findings remain.
- Refinement pass:
  - Draft refined once in this artifact for behavioral model, structure, ownership, validation, pathway policy, review focus, and stop conditions.
  - Refined again after maintainer review to split the implementation from one broad phase into three smaller phases.
  - Refined again after maintainer uv/tooling/Python feedback to split repository tooling into its own phase and set Python 3.12 as the baseline.
  - Refined again after maintainer rights/future-proofing feedback to require a temporary all-rights-reserved placeholder and an architecture refactor-risk gate.
  - Quality refinement pass used to lock exact uv build backend metadata, exact PyPI no-upload classifier, omitted license metadata, and the architecture refactor-risk review artifact path.
  - Summary recorded in [master-plan-quality-refinement-summary.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/master-plan-quality-refinement-summary.md). Refinement budget is used.
- Confirmation review:
  - Completed in [master-plan-review-confirmation.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/master-plan-review-confirmation.md). No blocking findings remain.
- Gate result:
  - Passed. Maintainer explicitly accepted the master plan; Stage 3 may begin with Phase 0 playbooks.
- Blocking findings:
  - None.
- Maintainer acceptance:
  - Accepted.
- Accepted risks and revisit triggers:
  - uv-managed package metadata and Python 3.12 baseline are accepted. Revisit build backend only if future native extension modules or non-standard packaging needs appear.
  - Temporary all-rights-reserved placeholder is accepted until a real license is selected. Revisit before publication, distribution, or external reuse.
  - Optional extras remain category-level. Revisit when backend implementations need real dependencies.
  - Cross-repo `loom` import enforcement is documented but not fully automated. Revisit when `loom` and `rphys` CI are coordinated.
  - Later behavior packages still require their own detailed API/refactor-risk reviews before concrete signatures are marked stable.

## Blocker Policy

The manager may attempt two automated blocker-fix and re-review cycles for the same blocker. PRs should be auto-merged after pathway gates pass. Stop for maintainer intervention only if the blocker remains, GitHub auth is invalid, branch protection blocks merge, repository-required review is enforced by repository policy, or the implementation would require changing accepted design decisions.

Additional stop conditions for this package:

- Stop if Stage 3 needs to add concrete domain behavior to make tests pass.
- Stop if package metadata requires choosing heavy runtime dependencies.
- Stop if a later-wave module must be made importable for unrelated tooling.
- Stop if docs cannot state the public contract without reopening Stage 1 decisions.
- Stop if the architecture refactor-risk review finds a blocking module-boundary, dependency-boundary, or extension-point issue.

## Open Questions Or Accepted Assumptions

- Accepted assumption: Stage 3 should introduce uv-managed `pyproject.toml`, `.python-version`, committed `uv.lock`, and Makefile wrappers because the repository currently has no package scaffold.
- Accepted assumption: Python 3.12 is the project baseline; Phase 2 should set `requires-python = ">=3.12"` and `.python-version` to `3.12`.
- Accepted assumption: Phase 2 should use `uv_build` as the uv-native pure-Python build backend with `requires = ["uv_build>=0.11.6,<0.12"]` and `build-backend = "uv_build"`.
- Accepted assumption: Phase 2 should add a temporary all-rights-reserved `LICENSE` placeholder and omit real license metadata until the maintainer selects a license.
- Accepted assumption: `pyproject.toml` should include the exact `Private :: Do Not Upload` classifier while the temporary rights placeholder is in effect.
- Accepted assumption: the master-plan quality gate must include [architecture-refactor-risk-review.md](/home/samcantrill/work/rphys/docs/implementation/public-architecture-contracts/architecture-refactor-risk-review.md) before Stage 3.
- Accepted assumption: no implementation phase should create future module homes, even as provisional imports.
- Accepted assumption: no CLI, `loom` config file, recipe, stage, registry implementation, plugin discovery mechanism, or generated API docs tooling is required for this package.

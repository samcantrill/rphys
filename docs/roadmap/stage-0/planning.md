# Roadmap Stage 0 Planning

Status: draft
Roadmap version: `v0`
Stage directory: `docs/roadmap/stage-0/`
Implementation plan: `docs/roadmap/stage-0/implementation-plan.md`

## Source Evidence

| Source | Relevant content | Used for | Notes |
| --- | --- | --- | --- |
| `AGENTS.md` | Repository scope, coding rules, validation expectations, roadmap workflow usage, worktree guidance. | Planning constraints and workflow rules. | Current request is a roadmap-stage planning workflow. |
| `.codex/workflows/roadmap-version-planning.md` | Gate sequence, planning artifact requirements, subagent pass definitions, approval checkpoints, no-code rule. | Workflow structure. | This session is executing the planning flow locally because the user did not explicitly request subagents. |
| `.codex/templates/roadmap-stage-planning.md` | Required sections for source evidence, readbacks, triage, requirements, design, validation, phase shaping, quality gate, and checkpoints. | Artifact structure. | Used as the base shape for this document. |
| `.codex/templates/roadmap-stage-implementation-plan.md` | Later implementation-plan output contract. | Later Stage 11 planning. | Not yet used because phase shaping and plan quality gate are pending. |
| `docs/roadmap.md` | Canonical roadmap, public governance, package boundaries, error contract, Milestone 0 deliverables and definition of done. | Roadmap extraction and stage scope. | Canonical documentation source of truth. |
| `README.md` | Current public-facing repository summary and roadmap pointer. | Current documentation baseline. | Minimal, references `AGENTS.md` and `docs/roadmap.md`. |
| `pyproject.toml` | Package metadata, Python requirement, no runtime dependencies, dev dependency group, pytest markers. | Tooling, dependency, and rights-status baseline. | Classifier uses `Private :: Do Not Upload`; no license metadata advertised. |
| `LICENSE` | All rights reserved placeholder and no public-use license statement. | Rights-status policy baseline. | Matches roadmap policy that no open-source license is selected. |
| `src/rphys/__init__.py` | Minimal package docstring and empty public `__all__`. | Current package/API baseline. | Imports are currently lightweight. |
| `tests/package/test_import.py` | Basic package import smoke test. | Current validation baseline. | Does not yet enforce optional dependency boundaries or public API governance. |
| `tests/README.md` | Suite layout and purpose, including package import-boundary tests and contract tests. | Validation planning constraints. | Test suite taxonomy already exists. |
| `Makefile`, `make/setup/targets.mk`, `make/dev/targets.mk`, `make/test/targets.mk` | `uv`-based setup, lock, build, diff, test, summary, and validation targets. | Tooling baseline and validation commands. | Test harness is already wired through Make targets. |

## Exploration Coverage

| Area | Files or patterns checked | Findings | Gaps |
| --- | --- | --- | --- |
| Roadmap and architecture docs | `docs/roadmap.md` sections 1-9 and Milestone 0. | Milestone 0 is a skeleton/governance stage that precedes broad implementation. It depends on existing package boundary, API governance, scientific contract, and rights-status policy sections. | Later milestones only reviewed enough to understand adjacency with Milestone 1. |
| Feature docs | `find docs -maxdepth 3 -type f` | No separate feature docs are present; `docs/roadmap.md` is the only docs source. | None for Stage 0 unless new feature docs are added later. |
| Code and tests | `src/rphys/__init__.py`, `tests/package/test_import.py`, `tests/README.md`, `pyproject.toml`, Make target files. | Package currently imports, has no runtime dependencies, has minimal package test, and has test taxonomy/tooling. Planned homes and error module do not exist yet. | Need detailed implementation planning for package homes, `errors.py`, stronger package/import tests, and optional dependency metadata. |
| Existing discussions or archive | `.codex/workflows/**`, `.codex/prompts/**`, `.codex/templates/**` listing. | Workflow assets exist and define the stage planning/implementation process. | Archived discussions were not present under `docs/`; prompts were not fully expanded because Stage 1 only needs workflow shape. |
| Version control state | `git status --short` | No tracked local modifications before this planning scaffold. | Generated ignored caches exist under `__pycache__`, but they are not part of tracked planning. |

## Roadmap Extraction

- Baseline roadmap outcome: create the package skeleton and enforce public API, dependency, tooling, and rights-status policy before broad implementation spreads.
- Prerequisites: canonical roadmap policy in `docs/roadmap.md`; Python 3.12 and `uv`; package metadata and lockfile; all-rights-reserved license placeholder; existing Make/test harness structure.
- Prior or adjacent roadmap links: Milestone 0 depends on sections 1-7 for scope, canonical naming, API governance, scientific contract rules, package boundaries, and error contract. Milestone 1 follows with naming, locators, schemas, metadata, and the full error vocabulary.
- Primary feature docs: none separate from `docs/roadmap.md`.
- Deferred or out-of-scope roadmap work: no datasource implementation, codec system, lazy IO, transforms, models, losses, metrics, training loops, evaluation, analysis, workflow runtime, generic artifacts, or project orchestration.
- Compatibility obligations: keep base imports lightweight; avoid advertising an open-source license; do not expose deep helpers as public contracts without docs and tests; do not introduce generic workflow or artifact runtime APIs.
- Public surfaces or durable artifacts likely affected: `pyproject.toml`, `README.md`, `LICENSE`, `src/rphys/__init__.py`, `src/rphys/errors.py`, planned package `__init__.py` files, package/import-boundary tests, and roadmap/governance documentation.

## Overview

- What this stage covers: repository skeleton, initial public import boundary, error module placeholder or base hierarchy, package-home directories, dependency grouping policy, rights-status metadata, and tests that enforce import and governance constraints.
- Why it exists: later domain milestones will spread across many packages; Stage 0 prevents accidental public API, dependency, licensing, or workflow-runtime decisions from becoming hard to unwind.
- Primary outcomes:
  - Importable `rphys` package with lightweight top-level import behavior.
  - Planned package homes exist without pretending unimplemented domain contracts are ready.
  - Public governance is documented and backed by tests.
  - Runtime dependencies remain empty unless explicitly justified.
  - Package metadata reflects private/all-rights-reserved status.
  - No generic workflow engine, artifact store, project config system, or stage runtime is introduced.
- Non-goals:
  - Implementing Milestone 1 naming contracts.
  - Implementing datasource, IO, ops, model, loss, metric, learning, training, prediction, evaluation, or analysis behavior.
  - Creating broad registries, placeholder public classes, or reserved re-export surfaces.
  - Selecting a final public license.
- Related feature docs: none.
- Impacted repo areas: `pyproject.toml`, `README.md`, `LICENSE`, `src/rphys`, `tests/package`, potentially `tests/unit/rphys`, `tests/contracts`, and Make/validation docs only if existing targets prove insufficient.
- Current state:
  - `pyproject.toml` already uses Python 3.12, `uv_build`, empty runtime dependencies, dev dependency group, private classifier, and pytest suite markers.
  - `LICENSE` already states all rights reserved.
  - `src/rphys/__init__.py` is lightweight and exposes an empty `__all__`.
  - Package import smoke coverage exists, but dependency-boundary and governance tests are still thin.
  - Planned package directories and `src/rphys/errors.py` are not present.
- Key uncertainty: how visible Stage 0 should make planned package homes. Empty package `__init__.py` files satisfy skeleton goals but may be mistaken for supported API unless documented and tested as provisional/internal skeleton only.
- User clarification questions and resolved answers:
  - Resolved: Optimize Stage 0 to unlock Milestone 1, adding only guardrails that are immediately beneficial and obvious.
  - Resolved: Include `RemotePhysError` base classes in Milestone 0.
  - Resolved: Use a balanced README update: enough governance context for users and agents without duplicating the canonical roadmap.
- Planning priority or optimization target: smallest useful skeleton that unlocks Milestone 1 while enforcing obvious early guardrails for lightweight imports, rights-status metadata, and exclusion of generic workflow/artifact runtime.

## Approvals

| Gate | Status | Date/round | Notes |
| --- | --- | --- | --- |
| Roadmap briefing and clarification window completed | approved | 2026-05-12 / R1 | Context scaffold briefed; maintainer answered clarification questions. |
| Intent and optimization target confirmed | approved | 2026-05-12 / R2 | Unlock Milestone 1 first; add only obvious immediate guardrails; include base errors; balance README depth. |
| Capability triage approved for functionality discussion | approved | 2026-05-12 / R3 | Maintainer approved proposed include/maybe/defer/out-of-scope triage. |
| Functionality and behavior baseline approved | approved | 2026-05-12 / R4 | Maintainer approved FR-1 through FR-7 as the Stage 0 behavior baseline. |
| Design decisions approved | approved | 2026-05-12 / R5 | Maintainer agreed to design decisions, including `RemotePhysError(message: str, **context: object)` with copied context and normal exception chaining. |
| Planning document and examples approved for validation planning | approved | 2026-05-12 / R6 | Maintainer approved audit and example set for validation planning. |
| Validation strategy approved | approved | 2026-05-12 / R7 | Maintainer approved focused package/unit validation, metadata checks, README review, and no scientific-contract tests for M0. |
| Phase shaping approved | approved | 2026-05-12 / R8 | Maintainer approved three reviewable phases: core skeleton/errors, governance guardrails/tests, README/final validation. |
| Plan quality gate passed | approved | 2026-05-12 / R9 | Maintainer approved passed quality gate; implementation-plan drafting unblocked. |
| Implementation plan approved | approved | 2026-05-12 / R11 | Maintainer approved `docs/roadmap/stage-0/implementation-plan.md`. |

## Stage Readbacks

| Stage | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- |
| Roadmap briefing and clarification | Stage 0 is a skeleton/governance milestone, not a domain implementation milestone. | Treat Stage 0 as planning-only until maintainer approves gates. Keep `rphys` free of generic workflow/artifact runtime. | None for initial briefing. | Capability triage. |
| Intent and optimization target | Unlock Milestone 1 with the smallest useful skeleton; include base `RemotePhysError` classes; balance README governance. | Add immediate, obvious guardrails only. Defer refinements that are better informed by later milestones. | Exact line between broad error category classes and specific subclasses remains for functional requirement discussion. | Approve capability triage for functionality discussion. |
| Capability triage | Include: planned package homes, base errors, lightweight import guardrails, minimal public API governance, rights-status metadata, small no-runtime exclusion, balanced README. Defer: optional dependency matrix, full scientific contract tests, all domain behavior. | Unlock M1 first; include only obvious guardrails with low future refactor risk. | Whether broad error base classes should include all broad roadmap categories in M0 or only `RemotePhysError` plus a smaller category subset. | Functional requirement discussion. |
| Functionality and behavior | FR-1 through FR-7 approved: skeleton namespaces, base errors, lightweight imports, public API governance, rights metadata, no workflow/artifact runtime, balanced README. | Base errors include broad roadmap categories; specific semantic subclasses wait for M1. Runtime dependencies remain empty. | Exact error constructor/context mechanics and root re-export policy are design decisions. | Design proposal and implication review. |
| Design decision review | Approved: public empty namespace homes, broad-only error hierarchy, simple error context API, empty root `__all__`, fresh-interpreter import-boundary tests, metadata guardrails, compact README governance. | Do not re-export errors at package root in M0. Specific semantic errors remain deferred. | None. | Audit and examples. |
| Audit and examples | Audit found no blockers. Example candidates cover namespace imports, base error context, lightweight imports, metadata/rights status, no-runtime boundary, and README handoff. | Treat examples as validation-planning inputs, not extra product scope. | None. | Approve planning document and examples for validation planning. |
| Validation strategy | Approved coverage for namespace imports, error hierarchy/context, lightweight imports, public API surface, metadata/rights status, no-runtime boundary, and README governance. | Keep checks focused and package/unit scoped; no scientific-contract tests in M0. | None. | Phase shaping. |
| Phase shaping | Approved phases: core skeleton/errors, governance guardrails/tests, README/final validation. | Keep public API implementation, test hardening, and docs/final evidence as separate review units. | None. | Plan quality gate. |
| Plan quality gate | Quality review passed with no blockers. | Accepted risks are limited to visible empty package names, broad error class compatibility, metadata test maintenance, and README drift; all have mitigation. | None. | Approve quality gate and create implementation plan. |
| Implementation-plan handoff | Implementation plan approved at `docs/roadmap/stage-0/implementation-plan.md` with three phases and no readiness blockers. | Use approved three-phase shape for the implementation workflow. | None. | Ready for implementation workflow. |

## Capability Triage

| Capability | Decision | Rationale | Requirements produced | Notes |
| --- | --- | --- | --- | --- |
| Package skeleton and planned homes | include | Milestone 0 deliverable and required to unlock Milestone 1 module work. Visibility should be explicit but minimal: namespace packages with docstrings and empty `__all__`, not fake APIs. | FR-1, FR-4 | Do not add `rphys.transforms` or `rphys.stages`. |
| Lightweight import boundary | include | Milestone 0 definition of done requires optional scientific/ML stacks not load through core imports. This is an obvious early guardrail. | FR-3 | Focus on import side effects, not detailed performance budgets. |
| Public API governance tests | include | Stable API means documented and tested extension contracts. Early tests should prevent accidental top-level exports and broad public surface. | FR-4 | Keep governance small; refine with later public contracts. |
| Rights-status and package metadata policy | include | Roadmap says current rights status is all rights reserved and package metadata must not advertise open-source licensing. This is already mostly true and easy to lock down. | FR-5 | Final public license selection remains out of scope. |
| Optional dependency grouping policy | maybe | The policy matters now, but no optional capability groups exist yet. Stage 0 should document the rule and assert runtime dependencies remain empty, then defer concrete extras until capabilities need them. | FR-3, FR-7 | Avoid empty placeholder extras that imply support. |
| Error module baseline | include | Maintainer confirmed base `RemotePhysError` classes belong in Milestone 0. Specific naming/data exceptions can wait for Milestone 1 behavior. | FR-2 | Functional discussion should decide broad category class extent. |
| Generic workflow/artifact runtime exclusion | include | Roadmap explicitly excludes workflow runtimes and generic artifact/store abstractions from `rphys`. A small negative import test is an obvious useful guardrail. | FR-6 | Do not encode a brittle exhaustive forbidden-name list. |
| Full optional dependency matrix and extras | defer | Optional stacks are not implemented in Stage 0. | none | Revisit when codecs, datasources, torch adapters, plotting, or model integrations arrive. |
| Full scientific contract test suite | defer | Stage 0 has no scientific operations yet. | none | Revisit from Milestone 1 onward as public semantics appear. |
| Domain implementations | out of scope | Milestone 0 is skeleton/governance only. | none | Includes datasources, IO, ops, models, losses, metrics, training, evaluation, and analysis behavior. |

## Module Behavior Map

| Module or area | Intended behavior | Why it matters | Codebase capability enabled | Requirements produced | Status |
| --- | --- | --- | --- | --- | --- |
| `rphys` package root | Import cheaply, keep `__all__` intentional, and avoid loading optional scientific/ML stacks. | Protects downstream imports and prevents accidental dependency/load-cost regressions. | Safe baseline for all later milestones. | FR-1, FR-3, FR-4 | draft |
| `rphys.errors` | Provide `RemotePhysError` and Stage-appropriate broad category base classes with structured context support. | Later naming/data modules need consistent diagnostics without each area inventing error mechanics. | Shared error contract path for Milestone 1. | FR-2 | draft |
| Planned package homes | Exist as importable namespaces for future milestones while avoiding fake public contracts. | Keeps implementation order aligned with roadmap package boundaries. | Reviewable module layout for later work. | FR-1, FR-4 | draft |
| Package metadata and dependency groups | Keep runtime dependencies empty, avoid license metadata while rights remain private, and defer optional extras until capabilities require them. | Enforces lightweight import and rights-status policy. | Dependency hygiene for research-library growth. | FR-3, FR-5 | draft |
| Tests and validation | Assert import, public API, dependency, metadata, rights-status, and no-runtime exclusions. | Converts governance into executable checks. | Safe CI/local validation baseline. | FR-3, FR-4, FR-5, FR-6 | draft |
| Documentation | Keep roadmap canonical while README gives balanced public orientation. | Users and agents need clear public/private/stability expectations. | Reduces accidental downstream reliance on internals. | FR-7 | draft |

## Functional Requirements

| ID | Requirement | What | Why | Scope | User-visible behavior | Agent/system behavior | Codebase capability enabled | Impact | Out of scope | Validation | Recommendation | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-1 | Package skeleton | Create planned package homes from the roadmap with minimal `__init__.py` files. | Unlock Milestone 1 and keep later work aligned with package boundaries. | `src/rphys/{data,io,datasources,ops,methods,models,nn,losses,objectives,metrics,learning,training,prediction,evaluation,analysis}/__init__.py`; keep `src/rphys/__init__.py` lightweight. | Users can import planned namespaces, but no domain behavior is promised yet. | Agents have clear homes for later milestone work. | Future implementations have stable module locations. | Moderate import-path impact because namespace homes become visible. | No `rphys.transforms`, `rphys.stages`, domain classes, registries, or re-exports. | Package tests import `rphys` and each planned namespace. | Include, with empty `__all__` and docstrings that avoid claiming stable APIs. | approved |
| FR-2 | Base error module | Implement `src/rphys/errors.py` with `RemotePhysError` and broad category base classes plus optional structured context. | Maintainer confirmed base errors belong in M0; Milestone 1 needs typed diagnostics. | Broad roadmap error categories only; defer specific semantic subclasses unless needed for base mechanics. | Users can import shared error bases and inspect message/context. | Later modules raise common error types rather than ad hoc exceptions. | Consistent diagnostics path for naming and data contracts. | Public API impact because error class names become documented. | Specific subclasses such as `MissingFieldError` or `InvalidDataKeyError`; validation tied to naming/locator behavior. | Unit or package tests cover construction, string behavior, context preservation, and lightweight import. | Include broad base hierarchy now; defer specific domain errors to Milestone 1. | approved |
| FR-3 | Lightweight dependency boundary | Keep runtime dependencies empty and ensure core imports do not load optional stacks. | Stage 0 definition of done requires core imports stay lightweight. | `pyproject.toml` runtime dependencies, `rphys` import, planned namespace imports, and `rphys.errors` import. | Installing/importing base `rphys` does not require scientific, video, ML, plotting, or dataset SDK stacks. | Tests catch accidental heavy imports during skeleton work. | Reliable low-cost import baseline. | Low implementation impact, high regression-prevention value. | Defining all future optional extras or performance budgets. | Package tests inspect `sys.modules` after imports and parse `pyproject.toml` dependencies. | Include as an obvious early guardrail. | approved |
| FR-4 | Public API governance | Make public exposure explicit through minimal `__all__` values and tests for top-level surface. | Stable API requires documented and tested extension contracts, not incidental helpers. | Top-level package and planned namespace `__all__`; README/roadmap policy references. | Users see a deliberately small public surface. | Agents avoid broad re-exports and placeholder public classes. | Prevents accidental API stabilization. | Low now, but important for future compatibility. | Full API review tooling or stability annotations for all future objects. | Package tests assert expected `__all__` and absence of accidental top-level names. | Include minimal governance tests now, refine later. | approved |
| FR-5 | Rights-status metadata | Preserve all-rights-reserved status in `LICENSE`, avoid open-source license metadata, and keep private package classifier. | Roadmap requires package metadata not advertise an open-source license until a real public-use license is selected. | `LICENSE`, `pyproject.toml`, README summary. | Users see private rights status consistently. | Agents do not add license metadata casually. | Publication safety before external release. | Low code impact; documentation/metadata impact. | Selecting final license or distribution policy. | Package test parses `pyproject.toml`; documentation review checks README and LICENSE alignment. | Include. | approved |
| FR-6 | No workflow/artifact runtime | Assert `rphys` does not expose generic workflow/stage/artifact runtime packages. | Roadmap explicitly assigns generic orchestration and artifact stores to downstream projects or `loom`. | Negative checks for obvious forbidden top-level packages such as `rphys.stages`, `rphys.workflow`, and `rphys.artifacts`. | Users do not find misleading orchestration APIs in base `rphys`. | Agents avoid adding generic runtime structure while building skeleton. | Maintains `rphys` as a domain library. | Low, but guardrail must avoid being overly broad. | Domain-specific stage-friendly callable functions in future training APIs; `loom` integration. | Package tests use import spec checks for a short forbidden list. | Include a small non-brittle guardrail. | approved |
| FR-7 | Balanced repository docs | Update README only enough to orient users to status, API stability, dependency policy, rights status, and canonical roadmap. | Maintainer asked for balance; roadmap remains the source of truth. | README plus existing roadmap references. | Users can understand the skeleton without reading every roadmap section first. | Agents have a concise pointer to the governance rules. | Better handoff into M1 without duplicating policy. | Documentation-only impact. | Long architecture guide or duplicated roadmap content. | Documentation review; optional text assertions only if useful. | Include compact README governance section. | approved |

## Behavior Baseline

- Included behavior: proposed package namespace skeleton, base error module, lightweight dependency/import guardrails, minimal public API governance, rights-status metadata checks, no generic workflow/artifact runtime guardrail, and balanced README orientation.
- Default behavior: imports are cheap; namespace `__all__` values are explicit and small; runtime dependencies remain empty; optional extras are not created until a real capability needs them; roadmap remains canonical.
- Failure behavior: `RemotePhysError` preserves a readable message and structured context; tests fail on accidental heavy imports, open-source license metadata, broad top-level exports, or obvious forbidden runtime packages.
- Unsupported behavior: domain data structures, naming validators, datasources, lazy IO, codecs, ops, transforms, models, losses, metrics, training loops, evaluation, analysis, generic workflow runtime, generic artifact store, and final license selection.
- Resume/interruption behavior: continue from this planning artifact and record gate readbacks before moving forward.
- Downstream implications: downstream code may rely on base package import, planned namespace homes, and base error classes only after implementation/docs/tests land; domain behavior waits for later milestones.
- Explicit deferrals: full optional dependency matrix; specific naming/data error subclasses; public stability annotations beyond basic `__all__`; scientific contract tests; all domain implementations.

## Proposed Implementation Shape

- Likely modules or packages:
  - `src/rphys/__init__.py`: lightweight root package, no broad re-exports, intentional empty or near-empty `__all__`.
  - `src/rphys/errors.py`: public base error hierarchy and structured context mechanics.
  - `src/rphys/{data,io,datasources,ops,methods,models,nn,losses,objectives,metrics,learning,training,prediction,evaluation,analysis}/__init__.py`: planned namespace homes with docstrings and empty `__all__`.
  - `tests/package/test_import.py`: package imports, namespace imports, top-level surface, metadata, dependency boundary, and forbidden generic-runtime checks.
  - `tests/unit/rphys/test_errors.py` or package-level equivalent: construction and context behavior for base errors.
  - `README.md`: compact status/governance orientation.
- Likely public classes/functions/protocols:
  - `RemotePhysError`.
  - Broad category subclasses: `RemotePhysDataError`, `RemotePhysFieldError`, `RemotePhysDataSourceError`, `RemotePhysIOError`, `RemotePhysCodecError`, `RemotePhysSliceError`, `RemotePhysCollateError`, `RemotePhysOperationError`, `RemotePhysPipelineError`, `RemotePhysMethodError`, `RemotePhysLearningError`, `RemotePhysTrainingError`, `RemotePhysEvaluationError`, `RemotePhysAnalysisError`, `RemotePhysDependencyError`, `RemotePhysNameError`, `RemotePhysMetadataError`.
  - No public protocols, registries, domain classes, or package-root re-exports in Stage 0.
- Likely internal helpers:
  - Optional private helper in `rphys.errors` only if needed to format or copy context; otherwise no helpers.
  - Test-only helper constants for planned namespaces and forbidden generic-runtime packages may live in tests.
- Data flow:
  - `import rphys` should execute only root-package code and not import optional stacks or domain subpackages.
  - `import rphys.errors` loads stdlib-only error definitions.
  - Importing planned namespace homes imports no other `rphys` submodules except normal package parent resolution.
  - Tests validate metadata through `tomllib`, imports through `importlib`, and heavy-module absence through a fresh interpreter or isolated import check.
- Dependency direction:
  - Root package does not depend on planned homes.
  - Planned homes do not depend on each other.
  - `rphys.errors` depends only on the standard library.
  - Tests may depend on pytest and stdlib only.
- Extension points:
  - Broad error classes are extension bases for later typed errors.
  - Planned namespace homes are locations for later milestone APIs, not extension contracts by themselves.
  - No registry or plugin extension point is introduced.
- Compatibility constraints:
  - Broad error class names and import path `rphys.errors` become public once implemented and tested.
  - Planned namespace import paths become visible but remain behavior-empty until later documented/test-backed APIs land.
  - `README.md`, `pyproject.toml`, and tests must keep private/no-open-source-license status aligned with `LICENSE` and roadmap.

## Design Decisions

| ID | Decision | Classification | What | Why | Proposed implementation shape | Impact | Options | Recommendation | Pros/cons | Limitation or trade-off | Validation/documentation obligation | Residual risk | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DD-1 | Skeleton namespace visibility | recorded recommendation | Use importable planned namespace packages with docstrings and empty `__all__`; expose no domain objects or re-exports. | Unlocks M1 package work while avoiding fake public behavior. | Add minimal `__init__.py` files under all roadmap package homes; no `rphys.transforms`, `rphys.stages`, or registries. | Import paths become visible before behavior exists. | Delay packages until implemented; create private `_` packages; create public empty namespaces. | Create public empty namespaces because the roadmap already names package homes and M1 needs them. | Pro: clear homes and low implementation cost. Con: visible imports may be mistaken for usable APIs. | Empty namespaces still create some compatibility expectation around package names. | README and tests must state/import only namespace homes, not behavior. | Later package reshuffling would be harder after M0. | recorded |
| DD-2 | Error hierarchy scope | recorded recommendation | Include all broad `RemotePhys*Error` categories from the roadmap in M0; defer specific semantic subclasses to M1 and later. | Maintainer approved base errors in M0, and broad categories support M1 diagnostics without implementing naming behavior early. | `rphys.errors` defines `RemotePhysError` plus broad subclasses; `__all__` lists only these classes. | Public API names become stable earlier than other Stage 0 objects. | Only `RemotePhysError`; smaller subset; all broad categories; broad plus specific subclasses. | Include all broad categories only. | Pro: avoids ad hoc later errors. Con: some categories have no behavior yet. | Category names may feel ahead of implementations, but they are roadmap-governed. | Unit/package tests cover imports and subclass relationships; docs explain specific subclasses are deferred. | If broad categories are later renamed, downstream exception handling breaks. | recorded |
| DD-3 | Error context mechanics | recorded recommendation | Define `RemotePhysError(message: str, **context: object)` storing `message` and a copied `context` dict; subclasses add no behavior in M0. | Provides inspectable diagnostics without introducing a complex context schema before M1. | Plain `Exception` subclass; call `super().__init__(message)`; set `self.message`; set `self.context = dict(context)`; rely on normal exception chaining instead of a special `cause` parameter. | Public constructor and attributes become a contract. | Message only; message plus `**context`; message plus explicit context mapping; dataclass/frozen context object. | Use message plus `**context` with copied dict. | Pro: simple, inspectable, easy to test. Con: context keys are not schema-validated. | Later schema-specific errors must validate their own context if needed. | Tests cover string output, args, context copying, empty context, subclass inheritance. | Future desire for immutable or serialized context could require additive helpers, not constructor breakage. | approved |
| DD-4 | Root package public surface | recorded recommendation | Do not re-export errors or planned namespaces from `rphys.__init__` in M0; keep `__all__` empty. | Top-level imports must stay lightweight and public API should not grow by convenience before behavior exists. | Leave root docstring; keep `__all__: list[str] = []`; users import `rphys.errors` directly. | Users cannot do `from rphys import RemotePhysError`. | Re-export error classes; expose version only; empty root surface. | Keep empty root surface in M0. | Pro: minimal and explicit. Con: less convenient for common errors. | A future top-level convenience API would need explicit approval and tests. | Package tests assert root `__all__` and absence of broad re-exports. | Some downstream code may expect common errors at root if other libraries do that. | recorded |
| DD-5 | Import-boundary test shape | auto-approved candidate | Validate lightweight imports and planned namespace imports with package tests, preferably using a fresh interpreter for heavy-module checks. | Avoids false positives from pytest already importing modules and gives an obvious early guardrail. | Tests import `rphys`, `rphys.errors`, and planned namespaces; assert optional stack names are absent from `sys.modules` in isolated import context. | Test-only design; no public API or dependency impact. | In-process checks; subprocess/fresh interpreter; no import-boundary check. | Use fresh-interpreter check for heavy modules and normal imports for namespace smoke. | Pro: robust and clear. Con: slightly more test code. | Requires careful `PYTHONPATH` handling under `uv run`. | Package tests document checked heavy-module list. | The list can become stale as optional groups appear. | proposed |
| DD-6 | Metadata and optional dependency policy | recorded recommendation | Keep runtime dependencies empty and avoid empty optional extras; parse `pyproject.toml` in tests to enforce private/no-license metadata. | M0 unlocks M1 and should not advertise unsupported optional stacks or public license status. | No `[project.optional-dependencies]` until a capability needs one; test `dependencies == []`, no license field, private classifier present. | Configuration policy impact. | Add empty extras now; document only; test metadata now. | Test current metadata and defer extras. | Pro: prevents accidental publication drift. Con: no extras skeleton for future capabilities. | Future optional groups require roadmap-backed change. | Package tests parse with stdlib `tomllib`. | Overly strict metadata tests could need updates when licensing changes. | recorded |
| DD-7 | README governance scope | recorded recommendation | Add concise status/governance sections without duplicating the roadmap. | Maintainer requested balance. | README covers project status, canonical roadmap pointer, public API/stability, dependency policy, rights status, and no workflow-runtime boundary in a compact form. | Documentation impact only. | Keep README minimal; add full architecture guide; add compact governance. | Add compact governance. | Pro: useful orientation. Con: another doc surface to keep aligned. | Roadmap remains canonical; README should not restate detailed contracts. | Documentation review; optional test only for critical rights-status wording if desired. | README can drift if roadmap policy changes. | recorded |

## Design Decision Triage

| Decision ID | Final classification | Auto-approval rationale | Adversarial examples considered | Reviewer objections | Traceability | Manager action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DD-1 | recorded recommendation | Not auto-approved because visible import paths affect compatibility. Recommended because roadmap already commits package homes and FR-1 is approved. | Second downstream project may import empty namespaces; later reshuffle would be breaking; empty `__all__` limits behavior expectation but not package-name expectation. | Keep docstrings explicit that namespaces are homes, not stable domain APIs. | FR-1, FR-4 | summarize | recorded |
| DD-2 | recorded recommendation | Not auto-approved because public exception class names affect API compatibility. Recommended because the roadmap explicitly names broad public errors and FR-2 is approved. | Later model/training/evaluation packages may need category errors before implementations exist; broad names can still be valid extension bases. | Avoid specific subclasses until semantic behavior exists. | FR-2 | summarize | recorded |
| DD-3 | recorded recommendation | Not auto-approved because constructor and context attributes are public API; now approved by maintainer. | A second data module may need structured keys, paths, expected/actual values, and exception chaining; simple `**context` supports this without schema commitment. | Use normal Python exception chaining; do not add first-class `cause` in M0. | FR-2 | summarize | approved |
| DD-4 | recorded recommendation | Not auto-approved because public top-level API shape affects users. Recommended because FR-3 and FR-4 prefer lightweight, intentional imports. | Users may expect `RemotePhysError` from root; delaying re-export avoids convenience API before import policy is mature. | Revisit root convenience imports only after stable public contracts emerge. | FR-3, FR-4 | summarize | recorded |
| DD-5 | auto-approved | Test-only choice, localized, straightforward to validate, no public API/dependency impact, supports approved lightweight-import behavior. | Fresh interpreter might need path setup; that is implementation detail and easy to adjust. | None material. | FR-3 | summarize | approved |
| DD-6 | recorded recommendation | Not auto-approved because package metadata/config policy affects distribution behavior. Recommended by approved FR-3 and FR-5. | Future public license or optional stack work will require deliberate test updates. | Keep tests focused on current rights status and empty runtime deps. | FR-3, FR-5 | summarize | recorded |
| DD-7 | recorded recommendation | Documentation scope is user-facing but follows approved FR-7. | README could drift from roadmap; keep it concise and route detail to roadmap. | Avoid duplicating detailed architecture sections. | FR-7 | summarize | recorded |

Auto-approval criteria:

- No public API, import-path, schema, config, scientific/workflow, dependency, serialization, persistence, or compatibility impact.
- Localized implementation choice with straightforward validation.
- Consistent with approved behavior and rphys design principles.
- Low future refactor risk and no meaningful downstream extension consequence.
- Traceable to an approved functional requirement.
- Challenged by design implication review with no blocker or major concern.

## Design Implication Review

| Finding | Affected decision or requirement | Maintainability/extensibility impact | Recommended revision | Status |
| --- | --- | --- | --- | --- |
| Empty namespace packages create visible import paths before behavior exists. | DD-1 | Moderate compatibility risk if package homes change later; low behavior risk because `__all__` remains empty. | Accept because package homes are roadmap-canonical and needed for M1; mitigate with docs/tests that avoid behavior promises. | resolved |
| Broad error classes become public before many corresponding modules exist. | DD-2 | Public names may outpace implementation, but they are cross-cutting base categories rather than behavior contracts. | Accept broad classes only; defer specific subclasses and semantic validation to later milestones. | resolved |
| Error context API could overfit too early. | DD-3 | A rigid schema or custom context object would be premature; message-only would under-serve M1 diagnostics. | Use approved simple `message: str, **context: object` constructor with copied dict and normal exception chaining. | resolved |
| Root re-exports improve convenience but risk top-level import growth. | DD-4 | Convenience now could encourage broad API stabilization. | Keep root `__all__` empty in M0; revisit convenience imports after stable contracts emerge. | resolved |
| Fresh-interpreter import-boundary tests can be brittle if path setup is ad hoc. | DD-5 | Low maintainability risk if implemented through the current `uv run`/pytest context and stdlib subprocess carefully. | Keep heavy-module list short and focused on obvious optional stacks. | resolved |
| Metadata tests may become intentionally stale when licensing or dependencies change. | DD-6 | Low risk; future changes should explicitly update tests. | Keep assertions tied to current roadmap status. | resolved |
| README governance can duplicate canonical roadmap. | DD-7 | Documentation drift risk. | Use concise orientation and link to roadmap for details. | resolved |

## Functionality And Decision Audit

| Audit item | Impact | Resolution | Status |
| --- | --- | --- | --- |
| Approved capabilities are covered by functional requirements. | Missing requirement coverage would leave implementation ambiguous. | FR-1 through FR-7 cover all included capabilities; optional dependency matrix, scientific contract tests, and domain implementations are explicitly deferred or out of scope. | pass |
| Design decisions trace to approved requirements. | Unsupported design decisions would expand scope beyond the approved behavior baseline. | DD-1 maps to FR-1/FR-4; DD-2/DD-3 map to FR-2; DD-4/DD-5 map to FR-3/FR-4; DD-6 maps to FR-3/FR-5; DD-7 maps to FR-7. | pass |
| Auto-approved decision remains low risk. | Auto-approval would be unsafe if it hid public-contract or refactor risk. | DD-5 is test-only, traceable to FR-3, and has adversarial review evidence; it remains auto-approved. | pass |
| Public-contract risks are recorded instead of auto-approved. | Empty namespaces, broad errors, metadata policy, root API shape, and README content affect users or distribution behavior. | DD-1, DD-2, DD-3, DD-4, DD-6, and DD-7 remain recorded recommendations with residual risks documented. | pass |
| Error scope avoids Milestone 1 leakage. | Specific subclasses would start naming/data behavior before M1. | M0 includes broad categories only; specific semantic subclasses remain deferred to M1 and later milestones. | pass |
| No generic workflow or artifact runtime remains in scope. | Adding generic runtime APIs would violate the roadmap boundary with downstream projects and `loom`. | FR-6 and DD-1 exclude `rphys.stages`, workflow, and artifact packages; examples and validation must include a small negative check. | pass |
| Example coverage is sufficient for validation planning. | Validation planning needs concrete scenarios to turn into tests. | Examples cover namespace skeleton, error context, lightweight imports, metadata/rights status, no-runtime exclusion, and README governance. | pass |

## Examples And Demonstrations

| Example | Behavior demonstrated | Project context | Required docs/tests | Status |
| --- | --- | --- | --- | --- |
| M1 package-home smoke path | Planned namespaces import successfully with empty `__all__` and no domain behavior. | A Milestone 1 implementer can add naming modules under `rphys.data` and errors under `rphys.errors` without first reshaping the package tree. | Package import tests for `rphys` and every planned namespace; README text that these are package homes, not stable domain APIs. | approved |
| Structured base error diagnostics | `RemotePhysNameError("invalid data key", key="inputs/video.rgb", expected="data-key grammar")` preserves message, args, and context. | Milestone 1 validators can raise typed diagnostics before specific subclasses such as `InvalidDataKeyError` are introduced or promoted. | Unit tests for `RemotePhysError` and broad subclasses; docs/readme note context is inspectable and subclass-specific semantics come later. | approved |
| Lightweight import guardrail | Importing `rphys`, `rphys.errors`, and planned namespaces does not import optional stacks such as `torch`, `numpy`, `cv2`, `av`, `scipy`, `pandas`, or `matplotlib`. | Downstream research projects and tooling can inspect package metadata or errors without paying optional scientific/ML import costs. | Package test using a fresh interpreter or isolated import check; short documented heavy-module list. | approved |
| Private package metadata guardrail | `pyproject.toml` keeps runtime dependencies empty, has no open-source license metadata, and retains the private classifier while `LICENSE` says all rights reserved. | Prevents accidental publication or license signaling before a real public-use license is selected. | Package metadata test with `tomllib`; README and LICENSE consistency check or review note. | approved |
| No workflow/artifact runtime boundary | `rphys.stages`, `rphys.workflow`, and `rphys.artifacts` are absent while README/roadmap point orchestration to downstream projects or `loom`. | Keeps `rphys` as reusable remote-physiology domain library, not an experiment runtime. | Negative import-spec package tests; README boundary wording. | approved |
| Balanced README handoff | README tells a new contributor the current status, canonical roadmap, API stability rule, dependency policy, rights status, and orchestration boundary in compact form. | Agents and maintainers can start M1 work with correct expectations without duplicating `docs/roadmap.md`. | Documentation review; optional package/docs text assertion only for critical rights-status wording. | approved |

## Validation Strategy

| Area | Behavior validated | Required coverage | Test/check type | Command or location | Status |
| --- | --- | --- | --- | --- | --- |
| Package namespace skeleton | `rphys` and all planned namespace homes import successfully; namespace `__all__` values are empty; no domain objects are exposed. | Package tests over `src/rphys/__init__.py` and planned package `__init__.py` files. | Required package test. | `tests/package/test_import.py`; run `make test-package`. | approved |
| Base error hierarchy | `RemotePhysError` and broad `RemotePhys*Error` categories import from `rphys.errors`, subclass relationships are correct, root package does not re-export them. | Broad class list from roadmap; `__all__`; subclass checks. | Required package/unit test. | `tests/package/test_import.py` and/or `tests/unit/rphys/test_errors.py`; run `make test-package` and `make test-unit`. | approved |
| Error context behavior | `RemotePhysError(message, **context)` preserves `str(error)`, `args`, `.message`, and copied `.context`; subclasses inherit behavior. | Empty context, multiple context keys, context dict copy behavior, normal exception chaining left to Python. | Required unit test. | `tests/unit/rphys/test_errors.py`; run `make test-unit`. | approved |
| Lightweight imports | Importing `rphys`, `rphys.errors`, and planned namespaces does not import obvious optional scientific/ML/video/plotting/dataframe stacks. | Fresh-interpreter or isolated import check for a short list: `torch`, `numpy`, `cv2`, `av`, `scipy`, `pandas`, `matplotlib`. | Required package test. | `tests/package/test_import.py`; run `make test-package`. | approved |
| Dependency and package metadata | Runtime dependencies remain empty; no open-source license field/classifier is advertised; private classifier remains while `LICENSE` is all rights reserved. | Parse `pyproject.toml` with `tomllib`; inspect `LICENSE` text. | Required package test. | `tests/package/test_import.py` or `tests/package/test_metadata.py`; run `make test-package`. | approved |
| Public API governance | Root `rphys.__all__` stays empty; planned namespace `__all__` values stay empty; no broad root convenience imports are added in M0. | `__all__` assertions and absence of root error attributes. | Required package test. | `tests/package/test_import.py`; run `make test-package`. | approved |
| No generic workflow/artifact runtime | Obvious forbidden runtime packages are absent: `rphys.stages`, `rphys.workflow`, `rphys.workflows`, `rphys.artifacts`. | Negative `importlib.util.find_spec` checks for a short forbidden list. | Required package test. | `tests/package/test_import.py` or `tests/package/test_boundaries.py`; run `make test-package`. | approved |
| README governance orientation | README states current rebuild status, canonical roadmap pointer, public API/stability rule, lightweight dependency policy, private rights status, and orchestration boundary without duplicating roadmap details. | Documentation review; optional text checks for critical rights-status and roadmap-pointer wording. | Required review; optional package/docs text test if implementation wants executable protection. | README review; optionally `tests/package/test_metadata.py`; run `make test-package` if text test added. | approved |
| Full local validation | Stage 0 implementation passes focused package/unit checks and repository whitespace/lock checks. | `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check`; broaden to `make validate-pr` if implementation touches shared tooling. | Required before PR/merge; broader command conditional on implementation footprint. | Make targets and `uv lock --check`, `git diff --check`. | approved |
| Scientific/workflow contracts | No scientific operations or workflow runtime are introduced in Stage 0. | Confirm absence rather than add scientific contract tests. | Explicit non-coverage. | Covered by package boundary tests and review. | approved |

## Phase Shaping

| Phase | Goal | Scope | Out of scope | Dependencies | Acceptance criteria | Test expectations | Design impact | Future compatibility | Reviewability | Risks | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Core skeleton and base errors | Create planned package homes, keep root package lightweight with empty `__all__`, add `rphys.errors` broad hierarchy and simple context behavior. | README governance expansion, metadata guardrail tests, no-runtime negative tests, optional dependency extras, specific semantic error subclasses, domain behavior. | Approved FR-1, FR-2, FR-4, DD-1 through DD-4. | `rphys`, `rphys.errors`, and planned namespaces import; `RemotePhysError` and broad categories behave as approved; no root re-exports. | `make test-package`, `make test-unit` focused on imports and errors. | Establishes public import paths and broad error API. | Package homes and broad error names become compatibility-sensitive. | Coherent code/API review unit with focused tests. | Empty packages may imply more behavior than exists; mitigate with docstrings and empty `__all__`. | approved |
| 2 | Governance guardrail tests | Add or harden package tests for lightweight imports, runtime dependency emptiness, package metadata/rights status, public API surface, and absence of generic workflow/artifact runtime packages. | Changing runtime dependencies, selecting a license, adding optional extras, README prose beyond assertions needed for checks. | Phase 1 import paths and error module exist. | Tests fail on obvious optional-stack imports, open-source license metadata, broad top-level exports, or forbidden runtime packages. | `make test-package`; `uv lock --check`; targeted package metadata/import-boundary tests. | Makes Stage 0 governance executable. | Future intentional license/dependency changes must update tests with roadmap approval. | Reviewable as test/policy hardening separate from code API. | Metadata assertions can become stale when rights/dependency policy changes; keep assertions tied to current roadmap. | approved |
| 3 | README handoff and final validation | Update README with compact status, roadmap, API stability, dependency, rights-status, and orchestration-boundary guidance; run focused validation and record evidence. | New architecture guide, duplicated roadmap detail, implementation of M1 domain contracts. | Phases 1 and 2 complete. | README provides balanced governance orientation; final checks pass or residual risks are recorded. | `make test-package`, `make test-unit`, `uv lock --check`, `git diff --check`; consider `make validate-pr` if implementation touches shared tooling. | Aligns user-facing docs with implemented skeleton and guardrails. | README remains a concise pointer to the roadmap rather than a competing source of truth. | Documentation/final-validation review unit. | README drift risk; mitigate with concise wording and roadmap links. | approved |

## Plan Quality Gate

| Check | Evidence | Result | Required action |
| --- | --- | --- | --- |
| Roadmap-to-requirement traceability | Milestone 0 goal and deliverables map to FR-1 package skeleton, FR-2 base errors, FR-3 lightweight imports, FR-4 API governance, FR-5 rights metadata, FR-6 no workflow/artifact runtime, and FR-7 README orientation. | pass | none |
| Requirement-to-design traceability | FR-1/FR-4 map to DD-1/DD-4; FR-2 maps to DD-2/DD-3; FR-3 maps to DD-5/DD-6; FR-5 maps to DD-6; FR-6 maps through DD-1 and validation guardrails; FR-7 maps to DD-7. | pass | none |
| Design-to-example traceability | Examples cover namespace homes, structured errors, lightweight imports, private metadata, no-runtime boundary, and README handoff. | pass | none |
| Example-to-validation traceability | Validation strategy has required package/unit/docs coverage for each approved example. | pass | none |
| Phase-shaping readiness | Three phases separate public API code, test/policy guardrails, and README/final validation with clear dependencies and acceptance criteria. | pass | none |
| Extensibility and maintainability readiness | Broad errors are minimal extension bases; planned packages are empty homes; no registries, protocols, optional extras, or domain behavior are added prematurely. | pass | none |
| Scientific/workflow contract clarity | Stage 0 introduces no scientific operations; workflow/artifact runtime is explicitly excluded and covered by negative checks. | pass | none |
| Reviewability and phase granularity | Phases are small, coherent, and reviewable independently: skeleton/errors, guardrail tests, docs/final validation. | pass | none |
| Unresolved ambiguity or blockers | No unresolved `blocked` or `needs maintainer discussion` decisions remain; assumptions and deferrals are recorded. | pass | none |

Gate result:

- Status: pass
- Blocking findings: none
- Accepted risks: empty namespace package names create mild compatibility expectations; broad error class names become public before full module behavior exists; metadata tests will need deliberate updates if licensing/dependency policy changes; README can drift if roadmap policy changes.
- Revisit triggers: package boundary changes, license selection, optional dependency groups, public root re-export proposal, or implementation pressure to add domain behavior in M0.

## Accepted Assumptions And Deferrals

| Item | Type | Rationale | Revisit trigger |
| --- | --- | --- | --- |
| `docs/roadmap.md` is the only feature/architecture source for Stage 0. | assumption | No separate feature docs exist under `docs/`. | New feature docs are added or maintainer points to another artifact. |
| No code implementation during roadmap-version planning. | assumption | Workflow explicitly says not to implement code in this workflow. | Maintainer switches to implementation workflow or explicitly pauses planning. |
| Subagent passes are represented by local managing-agent work in this session. | assumption | User requested the workflow but did not explicitly request subagents; current system instructions only allow subagents when explicitly requested. | Maintainer explicitly asks to use the workflow subagents. |
| Stage 0 optimizes for Milestone 1 enablement over exhaustive guardrails. | assumption | Maintainer requested unlocking M1 and refining guardrails as the project grows. | A Stage 0 decision would create a hard-to-unwind public or dependency contract. |
| README should be concise but not silent on governance. | assumption | Maintainer requested a balanced README update. | README starts duplicating the roadmap or lacks enough context for new contributors. |

## Resume Checkpoints

### After Functionality And Behavior

- Baseline locked: FR-1 through FR-7 approved for Stage 0.
- Open questions: error constructor/context mechanics in DD-3.
- Next step: design decision approval.

### After Design Decisions

- Decisions locked: DD-1 through DD-7 approved or recorded; DD-5 auto-approved; DD-3 approved with `RemotePhysError(message: str, **context: object)`.
- Open questions: none.
- Next step: validation strategy.

### After Validation Strategy

- Validation baseline locked: package/unit validation, metadata checks, README review, and no-runtime checks approved; no scientific-contract tests required for M0.
- Open questions: none.
- Next step: phase shaping approval.

### After Phase Shaping

- Phase sketch locked: three implementation phases approved: core skeleton/errors, governance guardrail tests, README/final validation.
- Open questions: none.
- Next step: plan quality gate.

### After Plan Quality Gate

- Gate result: pass; no blockers.
- Open questions: none.
- Next step: implementation-plan drafting.

## Workflow Feedback Routing

| Feedback | Routing | Action | Status |
| --- | --- | --- | --- |
| Execute planning workflow locally when subagents are not explicitly requested. | current-session preference | Record the assumption and continue with managing-agent synthesis only. | accepted for R1 |

## Change Log

| Round | Update |
| --- | --- |
| 2026-05-12 / R1 | Created Stage 0 context scaffold from roadmap, workflow, template, repository baseline, and tooling evidence. |
| 2026-05-12 / R2 | Recorded maintainer clarifications, approved initial intent gates, and drafted capability triage, module behavior, proposed functional requirements, and behavior baseline. |
| 2026-05-12 / R3 | Recorded maintainer approval of capability triage for functionality discussion. |
| 2026-05-12 / R4 | Recorded maintainer approval of functionality baseline and drafted design proposal plus implication review. |
| 2026-05-12 / R5 | Recorded maintainer approval of design decisions and added functionality/decision audit plus example candidates. |
| 2026-05-12 / R6 | Recorded maintainer approval of examples for validation planning and drafted validation strategy. |
| 2026-05-12 / R7 | Recorded maintainer approval of validation strategy and drafted phase shaping. |
| 2026-05-12 / R8 | Recorded maintainer approval of phase shaping and completed plan quality gate with pass result. |
| 2026-05-12 / R9 | Recorded maintainer approval of plan quality gate and began implementation-plan drafting. |
| 2026-05-12 / R10 | Created draft implementation plan from approved planning, phase shaping, validation, and quality-gate evidence. |
| 2026-05-12 / R11 | Recorded maintainer approval of implementation plan. |

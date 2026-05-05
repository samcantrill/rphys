# Legacy Audit And Roadmap Workflow

## Purpose

Use the old codebase as evidence for the new `rphys` design. The goal is not to copy the old structure, but to understand useful behavior, scientific intent, defects, missing tests, and reusable concepts.

## Inputs

- `LEGACY_REPO_PATH`: local path to the old repository.
- Current `rphys` roadmap: `docs/roadmap/index.md`.
- Any user-provided project priorities or known legacy pain points.

## Process

1. Confirm the legacy repository path exists and is readable.
2. Have the main agent identify broad research-component areas: datasets, signal representations, preprocessing, models, losses, training, evaluation, metrics, analysis, visualization, and utilities.
3. Spawn read-only legacy-auditor agents over independent areas when the audit can be parallelized.
4. For each area, map legacy files, classes, functions, scripts, tests, notebooks, and configuration patterns.
5. Record observed behavior, scientific assumptions, hidden coupling, and quality risks.
6. Classify each candidate capability as port, redesign, defer, or drop.
7. Create or update roadmap entries by research component.
8. Open or update GitHub issues for approved roadmap items when `gh` is authenticated.

## Audit Output

Each audited component should record:

- Legacy paths and symbols.
- Purpose inferred from code, tests, docs, and usage.
- Dependencies and coupling.
- Inputs, outputs, units, shapes, sampling-rate assumptions, and pipeline position.
- Known problems: entanglement, implicit global state, leakage risk, unclear normalization, fragile IO, missing validation, or weak tests.
- Porting decision: port, redesign, defer, or drop.
- Required external references or user decisions.
- Recommended RFC scope.

## Roadmap Entry Format

Roadmap entries live in `docs/roadmap/index.md` and should include:

- Component name.
- Status: candidate, RFC, planned, implementing, reviewing, merged, deferred, or dropped.
- Legacy evidence summary.
- Target modern design direction.
- Validation needs.
- GitHub issue link when available.

## Subagent Prompt Shape

Use the `legacy_auditor` custom agent when available. The handoff should specify:

- Legacy path or subsystem to inspect.
- Whether to inspect tests, examples, notebooks, and configs.
- Output sections required from the audit output above.
- No code edits.

## Exit Criteria

- The audited area has a roadmap entry.
- Important legacy evidence is linked or summarized.
- Open scientific or API questions are explicit.
- The next step is either a component RFC, more audit, deferral, or drop.

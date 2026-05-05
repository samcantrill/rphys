# Component RFC Workflow

## Purpose

Turn one roadmap item into an implementation-ready scientific and software design. Implementation should not start until the RFC and phase plan are accepted.

## Inputs

- Roadmap entry from `docs/roadmap/index.md`.
- Legacy audit evidence.
- Relevant papers, dataset documentation, benchmark conventions, or library references.
- User guidance on intended downstream research workflows.

## Process

1. Main agent gathers roadmap context, legacy evidence, and relevant references.
2. Spawn `rfc_planner` only for bounded design support, not final decisions.
3. Discuss high-impact API, scientific, and pipeline tradeoffs with the user.
4. Write the RFC using `docs/templates/component-rfc.md`.
5. Review the RFC for missing scientific contracts, unclear pipeline order, weak validation, and poor extensibility.
6. Mark the RFC as accepted only after the user or maintainer explicitly accepts it.
7. Create or update the linked GitHub issue.

## Required RFC Content

- Component purpose and target users.
- Public API shape, including classes, functions, protocols, or configuration objects.
- Pipeline contract: inputs, outputs, units, shapes, dtypes, sampling rates, and ordering constraints.
- Mathematical operations in LaTeX notation where relevant.
- Legacy evidence and explicit port/redesign/drop decisions.
- Known scientific risks, leakage risks, and failure modes.
- References when algorithms, metrics, datasets, or assumptions come from literature.
- Test and validation plan.
- Phased implementation outline.

## Design Defaults

- Prefer composable Python APIs over monolithic experiment scripts.
- Keep data access, preprocessing, model computation, training orchestration, and analysis separated.
- Make implicit assumptions explicit in types, docstrings, tests, and docs.
- Prefer deterministic behavior and explicit random seeds where randomness is involved.
- Prefer small synthetic fixtures for tests.

## Exit Criteria

- The RFC is decision-complete enough to phase.
- Scientific contracts are explicit.
- Validation requirements are clear.
- User-approved unresolved questions are recorded as assumptions.
- A phase plan can be created without redesigning the component.

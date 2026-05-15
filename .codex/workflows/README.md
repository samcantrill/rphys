# Codex Workflow Entrypoints

This directory is the user-facing "start here" layer for rphys Codex
workflows.

Files here are intentionally short. They route user requests to canonical
prompts in `.codex/prompts/` and durable artifacts in `.codex/templates/`.

Do not put role authority, model, or sandbox policy here; that belongs in
`.codex/agents/`. Do not put full artifact schemas here; that belongs in
`.codex/templates/`. Do not duplicate long prompt bodies here.

## Entrypoints

| Entrypoint | Use when | Canonical prompts |
| --- | --- | --- |
| `roadmap-version-planning.md` | The user wants to convert one roadmap stage into approved planning and an implementation plan | `roadmap-stage-*.md` planning prompts, including the internal functionality-agreement and design-agreement facilitation prompts |
| `roadmap-version-implementation.md` | An approved roadmap-stage implementation plan exists and Codex should execute phases through PRs and automated merges | `phase-loop-management.md` plus phase/PR prompts |

## Typical Path

```text
roadmap-version planning
combined context scaffold, capability triage, and candidate requirements
functionality-agreement review
behavior confirmation
context checkpoint if applicable
design proposal
design implication and future-roadmap safety review
design-agreement review
validation, phase shaping, and plan quality gate
approved stage implementation plan
automatic implementation-plan quality gate
phase execution plan
implementation and phase-scoped validation
phase PR body and suite evidence
automated review
CI-gated phase PR merge to develop
merge metadata update and cleanup
```

## Internal Capabilities

These are workflow internals, not separate user-facing entrypoints:

- Implementation-plan quality gate before phase selection.
- Expanded-path phase execution plan refinement for public API, scientific
  contract, import-boundary, dependency, serialization, provenance, or
  cross-module risk.
- Pre-submit blocker gate before phase PR creation.
- Automated phase PR review and merge after validation and CI pass.
- Direct metadata update or explicit deferral after a phase merge; no
  interstitial docs-only PR between phase PRs.

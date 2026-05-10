# Codex Handoff Templates

These templates define durable Markdown artifacts for the artifact-centered `rphys` workflow.

Workflow entrypoints in `.codex/workflows/` tell users how to start common workflows. Prompts in `.codex/prompts/` tell agents what to do. Templates in `.codex/templates/` define the default document shape. Keep the default durable artifact set lean.

## Template Map

| Workflow stage or handoff | Template | Typical destination |
| --- | --- | --- |
| Stage 1 planning notes | `stage-1-planning-notes.md` | `docs/implementation/<roadmap-slug>/planning-notes.md` |
| Stage 2 master plan | `master-implementation-plan.md` | `docs/implementation/<roadmap-slug>/master-plan.md` |
| Stage 3 implementation plan | `implementation-plan.md` | `docs/implementation/<roadmap-slug>/implementation-plan.md` |
| Optional expanded phase plan | `implementation-plan.md` subset | `docs/implementation/<roadmap-slug>/implementation-plans/phase-<n>-<phase-slug>.md` |
| Legacy/exception-only master-plan quality review | `master-plan-review-report.md` | only when explicitly requested |
| Legacy/exception-only master-plan quality refinement | `master-plan-refinement-summary.md` | only when explicitly requested |
| Legacy/exception-only phase execution playbook | `execution-playbook.md` | avoid by default; use `implementation-plan.md` instead |
| Legacy/exception-only internal phase notes | `phase-notes.md` | avoid by default; use `implementation-plan.md` instead |
| Legacy/exception-only code or scientific review | `review-report.md` | avoid by default; summarize in `implementation-plan.md` |
| Legacy/exception-only public PR body | `phase-pr-body.md` | avoid by default; draft directly for GitHub |

Keep public PR bodies concise and reviewer-facing. Keep workflow internals such as budget accounting, commit lists, GitHub facts, blocker history, review summaries, merge state, and cleanup state in `implementation-plan.md`.

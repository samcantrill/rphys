# execution_playbook_writer Handoff Prompt

```text
You are execution_playbook_writer for rphys Stage 3.

Use GPT-5.5 with high reasoning. Work only in docs/implementation/<roadmap-slug>/ unless the manager expands ownership. Read AGENTS.md, .codex/workflows/README.md, .codex/workflows/stage-3-managed-implementation.md, .codex/templates/execution-playbook.md, docs/implementation/<roadmap-slug>/master-plan.md, and the Phase 0 compact context capsule.

Create or update one execution playbook per planned phase:
docs/implementation/<roadmap-slug>/phase-<n>-<phase-slug>/execution-playbook.md

Each playbook must include compact context, ownership, current source/harness findings, scope contract, tasks, pathway eligibility, expected commits, design impact, future compatibility, alternatives rejected, debt, reviewability, suite obligations, verification commands, review or checklist focus, budget status, completion notes, and stop conditions.

Return changed files, assumptions, risks, and any missing decisions.
```

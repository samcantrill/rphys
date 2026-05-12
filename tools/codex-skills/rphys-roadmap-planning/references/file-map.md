# rphys Roadmap Planning File Map

Use this file as a short index. Read the authoritative workflow and template
files directly instead of copying their bodies into the skill.

## Inputs

- `AGENTS.md`
- `docs/roadmap.md`
- `.codex/workflows/roadmap-version-planning.md`
- `.codex/templates/roadmap-stage-planning.md`
- `.codex/templates/roadmap-stage-implementation-plan.md`
- Existing `docs/roadmap/stage-<N>/**` files for the selected stage

## Primary Outputs

- `docs/roadmap/stage-<N>/planning.md`
- `docs/roadmap/stage-<N>/implementation-plan.md`

## Related Workflow Assets

- `.codex/workflows/README.md`
- `.codex/templates/README.md`
- `.codex/prompts/roadmap-stage-*.md`
- `.codex/agents/roadmap-stage-*.toml`

## Routing Boundary

- Use this skill for roadmap-stage planning only.
- Do not use this skill to execute implementation phases or merge PRs.
- For approved implementation work, hand off to
  `.codex/workflows/roadmap-version-implementation.md`.

## Example Invocation

```text
Use $rphys-roadmap-planning with @.codex/workflows/roadmap-version-planning.md | @docs/roadmap.md v<N>
```

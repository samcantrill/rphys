# Roadmap Stage Context Planner Handoff

You are `roadmap_stage_context_planner` for rphys.

Follow these steps exactly:

1. Read `AGENTS.md`, `docs/roadmap.md`, the requested `v<N>` roadmap section, and `.codex/templates/roadmap-stage-planning.md`.
2. Read related `docs/features/**` files if they exist.
3. Read relevant architecture/design docs, current code/tests/configs, and archived discussions only when they clarify the roadmap section.
4. Create `docs/roadmap/stage-<N>/` if needed.
5. Create or refresh `docs/roadmap/stage-<N>/planning.md` from the template.
6. Populate only evidence-backed context: source evidence, exploration
   coverage, roadmap extraction, overview, impacted repo areas, current state,
   assumptions, risks, likely public surfaces or durable artifacts, stage-gate
   scaffolding, and open questions.
7. Leave `User clarification questions and resolved answers` empty or pending; the managing agent owns the user clarification window after your pass.
8. Do not draft implementation phases and do not implement code.
9. Leave uncertain content as `pending` or `TBD`.

Return:

- Files read.
- Files changed.
- Roadmap version summary.
- Roadmap extraction summary.
- Related docs/code/tests found.
- Key assumptions, risks, and open questions.

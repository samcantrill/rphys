# Stage 2: Roadmap Item To Master Plan

## Purpose

Turn one accepted roadmap work package and confirmed Stage 1 planning notes into a decision-complete live master plan.

Stage 2 should feel direct and explicit. The agent reads context, gives the maintainer a compact readout of what matters, drafts the plan, then first walks the maintainer through the overall intent and functionality of the stage. The maintainer must explicitly approve that intent/functionality baseline before Stage 2 moves into design discussion.

After the functionality baseline is approved, the agent classifies design decisions before discussing them. The agent does not step through every design decision. It records implementation details and strong recommendations directly in the plan, then walks the maintainer through only the decisions that are both impactful and not settled by a strong repository-supported recommendation, plus any decision the maintainer explicitly asks to discuss. Each discussion packet explains what is being decided, why it matters, implementation consequences, alternatives, recommendation, validation impact, and residual risk.

For foundational public-contract packages, high-level packet approval is not enough. Stage 2 must also include a deep design review before full plan acceptance. That review should pressure-test API shape, invariants, edge cases, failure modes, scientific contracts, extension points, alternative designs, compatibility, and downstream consequences. The maintainer should not have to keep the workflow on track or manage a pile of handoff documents.

## Default Artifacts

- Input: `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Output: `docs/implementation/<roadmap-slug>/master-plan.md`.
- Intent/functionality approvals, design-decision classifications, maintainer walkthrough packets, deep design review packets, approvals, revisions, deferrals, quality-gate findings, refinement notes, confirmation results, accepted risks, and blockers are recorded inside `master-plan.md`.
- Do not create separate master-plan review, refinement, context-capsule, or handoff documents by default. Create one only when the maintainer explicitly asks or when a blocker needs evidence that would make `master-plan.md` unreadable.

## Inputs

- Accepted roadmap work package from `docs/roadmap/index.md`.
- Stage 1 planning notes from `docs/implementation/<roadmap-slug>/planning-notes.md`.
- Repository constraints from `AGENTS.md`.
- Existing code and documentation discovered by non-mutating inspection.
- `.codex/templates/master-implementation-plan.md`.

## Process

1. Read the roadmap item, Stage 1 planning notes, `AGENTS.md`, workflow docs, and only the repository files needed to understand the decision surface.
2. Give a concise context readout: current facts, constraints, likely implementation shape, known risks, and the decisions that still need maintainer input.
3. Create or refresh `master-plan.md` with intent/functionality, design decisions, design-decision classification, phases, validation, pathway guidance, and quality-gate metadata.
4. Present the overall intent and functionality baseline first. Cover what the package does, what it refuses to do, user-visible behavior, agent-visible behavior, out-of-scope behavior, failure behavior, validation goals, and likely downstream impact. Ask for explicit approval before moving to design discussion.
5. If the maintainer revises or rejects the intent/functionality baseline, update `master-plan.md` and repeat the intent/functionality round until it is approved or the plan is blocked.
6. After intent/functionality approval, classify material design decisions:
   - `implementation detail`: low impact or locally obvious; record only if useful for implementation.
   - `recorded recommendation`: meaningful impact, but repository evidence and accepted functionality give a strong default; record selected approach, rationale, alternatives, debt, and revisit trigger without individual walkthrough unless the maintainer asks.
   - `needs discussion`: high impact and not fully determined by repository evidence, accepted functionality, or a strong recommendation; discuss with the maintainer before acceptance.
   - `deferred/blocking`: not decidable now; record why Stage 3 can proceed or mark the plan blocked.
7. Present a concise classification summary to the maintainer. Do not walk through every decision. Ask whether any impactful decision is missing or whether any recorded recommendation should be promoted to discussion.
8. Walk through the `needs discussion` design packets with the maintainer. Group related proposals into small packets, usually one to three decisions per round. Each packet must state:
   - What the draft proposes.
   - Why the decision matters.
   - What implementation behavior changes if approved.
   - The main alternatives considered.
   - The recommended default and why repository evidence supports it.
   - Validation/documentation obligations and residual risk.
   - The exact approval requested: approve, revise, or defer.
9. After each meaningful answer, update the live `master-plan.md`. Record the packet, maintainer response, accepted/revised/defaulted decision, rejected alternatives, rationale, validation obligation, residual risk, and revisit trigger.
10. For foundational packages, public-contract packages, or any package where API mistakes would cascade into later work, run a deep design review after the design-decision classification and before full acceptance. Discuss small design-review packets that cover concrete API shapes, object invariants, examples, failure cases, edge cases, extension mechanics, future compatibility, and downstream package consequences. If the maintainer says the earlier discussion was not deep enough, reopen the review and record the concern as a blocker until this review is complete.
11. Refine `master-plan.md` after design discussions are complete. Ensure the behavior model, decisions, phases, validation, review requirements, and stop conditions reflect the accepted design.
12. Run the master-plan quality gate before Stage 3 begins and record the result in `master-plan.md`.
13. If drafting or refining `implementation-plan.md` later exposes unclear implementation details or conflicts, ask focused final questions and record the answers before Stage 3 implementation proceeds.
14. Use `master_plan_planner` agents only for bounded sidecar analysis. Their findings should be summarized into `master-plan.md`; they should not create durable side documents by default.
15. Mark the roadmap item `planning` while drafting.
16. Mark the master plan accepted only after explicit maintainer acceptance of the full plan after intent/functionality approval, design discussion, required deep design review, refinement, and quality-gate review are complete.

## Required Decisions

The Stage 2 discussion must resolve or explicitly defer:

- Behavioral contract: what the completed work does, refuses to do, and reports on failure.
- Public surfaces: import paths, CLI or script entrypoints, docs, templates, workflow files, config files, environment expectations, and stable conventions.
- Internal structure: modules, directories, ownership boundaries, dependency direction, data flow, and extension points.
- Maintainability and extensibility: responsibilities, coupling avoided, future changes the design should absorb, and debt with revisit triggers.
- Validation: tests, static checks, docs checks, TOML/config checks, CI behavior, safe fixtures, and acceptance evidence.
- Agent behavior: what agents may do, what they read/write, where durable state lives, and how resume works after interruption or context loss.
- Implementation phases: phase order, branch/worktree names, ownership boundaries, standard/fast pathway guidance, and stop conditions.
- Merge policy: phases are implemented sequentially and are not gated by human review; automatic or admin merge is used after automated gates pass.

For each material decision, record the decision, alternatives considered, rationale, maintainability/extensibility impact, validation obligation, and residual risk.

## Maintainer Decision Walkthrough

Before accepting the master plan, the Stage 2 discussion must first establish approved intent/functionality, then step through the necessary design decisions with the maintainer.

Use decision packets rather than a monolithic approval request. A packet should be small enough that the maintainer can reasonably approve, revise, or defer it in one response. Combine tightly coupled details only when splitting them would obscure the implementation consequence.

Record the walkthrough inside `master-plan.md`, not in a side document. The record should include:

- Intent/functionality approval status.
- Design-decision classification and status.
- Packet topic and status.
- Proposal summary.
- Implementation consequence.
- Alternatives considered.
- Maintainer response or accepted assumption.
- Resulting plan update.
- Remaining open questions.

If the maintainer approves a packet, update the relevant decision rows from `proposed default` or `needs maintainer approval` to `accepted`. If the maintainer revises a packet, update the plan and record the rejected default. If the maintainer defers a packet, record why Stage 3 can proceed without the answer or mark the plan blocked.

Low-impact implementation details do not need individual approval, but they should be summarized when they materially shape phase ownership, validation, or stop conditions.

## Intent And Functionality Approval

This is the first approval gate. Do not start design discussion until the maintainer explicitly approves the stage intent and functionality baseline.

The baseline must cover:

- Purpose and user-visible outcome.
- Included functionality.
- Unsupported behavior and explicit non-goals.
- Failure behavior and stop behavior.
- Scientific/workflow obligations.
- Validation goals.
- Downstream packages affected.

If approval changes the scope, update the roadmap row and master plan before design discussion begins.

## Design Decision Classification

After intent/functionality approval, identify and classify the design decisions implied by that baseline.

Record material decisions in `master-plan.md` with one of these classifications:

- `implementation detail`: low-impact details that can be chosen by implementation agents within the accepted plan.
- `recorded recommendation`: impactful decision with a strong default from repository evidence, accepted functionality, or local architecture. Record it without a separate walkthrough unless the maintainer asks to discuss it.
- `needs discussion`: impactful decision with meaningful uncertainty or multiple defensible approaches and no strong recommendation. Discuss it with the maintainer before acceptance.
- `deferred/blocking`: not decidable now. Record either why Stage 3 can proceed safely or why the plan is blocked.

For every `needs discussion` decision, explain what is being decided, why it matters, alternatives, recommendation if one exists, maintainability/extensibility impact, validation obligation, and residual risk before asking for approval.

## Deep Design Review

Use this review whenever the package introduces public contracts, foundational runtime behavior, scientific semantics, cross-package extension points, or any API that downstream packages will build on. The review must happen before full master-plan acceptance, even when the maintainer has already approved high-level functionality packets.

Deep design packets should be concrete. Prefer examples, pseudo-signatures, invariants, and failure examples over broad statements. Cover:

- Public class/function shape and import paths.
- Mutability, copying, identity, equality, hashing, and serialization behavior.
- Required invariants and validation timing.
- Metadata semantics, units, shapes, dtype/device expectations, temporal axes, and coordinate conventions where relevant.
- Failure types, diagnostic content, and stop behavior.
- Extension points and what users can add without editing internals.
- Alternatives that were seriously considered and why they were rejected.
- Downstream impacts on dataset IO, transforms, training, evaluation, and docs.
- What must be tested before merge.

Record the review in `master-plan.md`. If the review changes a previously approved packet, update the design decision table and record the change in discussion history. If the review exposes unresolved design questions, keep the plan in draft and blocked status.

## Quality Gate

Before Stage 3 starts, the managing agent runs a bounded quality gate:

1. Review once with `master_plan_reviewer` using `.codex/prompts/master-plan-review.md`.
2. Record findings directly in the `Master Plan Quality Gate` section of `master-plan.md`.
3. If blocking findings exist, run one refinement pass with `master_plan_refiner` using `.codex/prompts/master-plan-quality-refine.md`; the refiner edits `master-plan.md` directly.
4. Run one confirmation review and record the result in `master-plan.md`.
5. Stop before Stage 3 if blockers remain.

The gate checks maintainability, extensibility, reviewability, scientific-contract clarity, phase scope, test strategy, accepted debt, unresolved design conflict, and whether implementation can proceed without redesign.

## Exit Criteria

- `docs/implementation/<roadmap-slug>/master-plan.md` exists, is decision-complete, and is accepted.
- The intent/functionality baseline is explicitly approved and recorded in `master-plan.md`.
- The design-decision classification is recorded in `master-plan.md`.
- The maintainer decision walkthrough is recorded in `master-plan.md`, with every material proposal accepted, revised, or explicitly deferred.
- Any required deep design review is recorded in `master-plan.md`, and every blocker from that review is resolved, revised into the plan, or explicitly deferred with a reason Stage 3 can proceed.
- The plan has been refined after design discussion and any final questions from implementation-plan drafting have been resolved or recorded as safe assumptions.
- The implementation phases are ordered, sequential, and have disjoint ownership.
- Public surfaces, internal structure, validation, agent behavior, pathway policy, merge policy, and stop conditions are documented.
- The master-plan quality gate is recorded as passed in the master plan, or blockers are recorded with exact findings.
- Stage 3 can create or update `docs/implementation/<roadmap-slug>/implementation-plan.md` without asking further design questions.

# Roadmap Stage <N> Planning

Status: draft
Roadmap version: `v<N>`
Stage directory: `docs/roadmap/stage-<N>/`
Implementation plan: `docs/roadmap/stage-<N>/implementation-plan.md`

## Source Evidence

| Source | Relevant content | Used for | Notes |
| --- | --- | --- | --- |
| `docs/roadmap.md` |  | roadmap section |  |

## Exploration Coverage

| Area | Files or patterns checked | Findings | Gaps |
| --- | --- | --- | --- |
| Roadmap and architecture docs |  |  |  |
| Feature docs |  |  |  |
| Code and tests |  |  |  |
| Existing discussions or archive |  |  |  |

## Roadmap Extraction

- Baseline roadmap outcome:
- Prerequisites:
- Prior or adjacent roadmap links:
- Primary feature docs:
- Deferred or out-of-scope roadmap work:
- Compatibility obligations:
- Public surfaces or durable artifacts likely affected:

## Overview

- What this stage covers:
- Why it exists:
- Primary outcomes:
- Non-goals:
- Related feature docs:
- Impacted repo areas:
- Current state:
- Key uncertainty:
- User clarification questions and resolved answers:
- Planning priority or optimization target:

## Stage Gates

| Gate | Required inputs | Current blockers or queue items | Status | Date/round | Notes |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements | roadmap extraction, overview, capability triage, module behavior map, functional requirements, initial functionality queue |  | pending / in_progress / passed / blocked |  |  |
| Functionality-agreement review | functionality-agreement queue |  | pending / in_progress / passed / blocked |  |  |
| Behavior confirmation | resolved functionality-agreement queue |  | pending / in_progress / passed / blocked |  |  |
| Context checkpoint if applicable | resume checkpoint, refreshed context if needed |  | pending / in_progress / passed / blocked / not needed |  |  |
| Design-agreement review | proposed implementation shape, design decisions, design-agreement queue, design implication review, future-roadmap/reuse safety review |  | pending / in_progress / passed / blocked |  |  |
| Validation, phase shaping, and plan quality gate | validation strategy, phase shaping, traceability review, specialist evidence check |  | pending / in_progress / passed / blocked |  |  |
| Implementation plan approved | implementation-plan review and approval |  | pending / in_progress / passed / blocked |  |  |

## Stage Readbacks

| Stage | Gate result | Locked decisions | Defaults and recommendations | Open questions or blockers | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap briefing, capability triage, and candidate requirements |  |  |  |  |  |
| Functionality-agreement review |  |  |  |  |  |
| Behavior confirmation |  |  |  |  |  |
| Context checkpoint if applicable |  |  |  |  |  |
| Design-agreement review |  |  |  |  |  |
| Validation, phase shaping, and plan quality gate |  |  |  |  |  |
| Implementation-plan handoff |  |  |  |  |  |

## Capability Triage

| Capability | Decision | Rationale | Requirements produced | Notes |
| --- | --- | --- | --- | --- |
|  | include / maybe / defer / out of scope |  |  |  |

## Module Behavior Map

| Module or area | Intended behavior | Why it matters | Codebase capability enabled | Requirements produced | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | draft |

## Functionality Agreement Queue

| Queue ID | Related requirement IDs | Depends on | Impact | What is being locked | Why it matters | Recommended answer | Trade-offs or rejected branches | Repo evidence or direct resolution | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FQ-1 | FR-1 |  | high / medium / low |  |  |  |  |  |  | pending triage / repo-resolved / needs maintainer discussion / blocked / locked / deferred |

## Functional Requirements

| ID | Requirement | Depends on | Agreement queue | What | Why | Scope | User-visible behavior | Agent/system behavior | Codebase capability enabled | Impact | Out of scope | Validation | Recommendation | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-1 |  |  | FQ-1 |  |  |  |  |  |  |  |  |  |  | pending |

## Behavior Confirmation

- Included behavior:
- Default behavior:
- Failure behavior:
- Unsupported behavior:
- Resume/interruption behavior:
- Downstream implications:
- Explicit deferrals:
- Why this behavior is locked:

## Proposed Implementation Shape

- Likely modules or packages:
- Likely public classes/functions/protocols:
- Likely internal helpers:
- Data flow:
- Dependency direction:
- Extension points:
- Compatibility constraints:

## Design Agreement Queue

| Queue ID | Related decision IDs | Depends on | Impact | What is being locked | Why it matters | Recommended answer | Trade-offs or rejected branches | Repo evidence or direct resolution | Exact feedback needed | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-1 | DD-1 |  | high / medium / low |  |  |  |  |  |  | pending triage / repo-resolved / needs maintainer discussion / blocked / locked / deferred |

## Design Decisions

| ID | Decision | Depends on | Agreement queue | Classification | What | Why | Proposed implementation shape | Impact | Options | Recommendation | Pros/cons | Limitation or trade-off | Validation/documentation obligation | Residual risk | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DD-1 |  | FR- | DQ-1 | auto-approved candidate / recorded recommendation / needs maintainer discussion / blocked |  |  |  |  |  |  |  |  |  |  | pending |

## Design Decision Triage

| Decision ID | Final classification | Auto-approval rationale | Adversarial examples considered | Reviewer objections | Traceability | Manager action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DD-1 | auto-approved / recorded recommendation / needs maintainer discussion / blocked |  |  |  | FR- | summarize / discuss / block / reopen functionality queue | pending |

Auto-approval criteria:

- No public API, import-path, schema, config, scientific/workflow, dependency,
  serialization, persistence, or compatibility impact.
- Localized implementation choice with straightforward validation.
- Consistent with approved behavior and rphys design principles.
- Low future refactor risk and no meaningful downstream extension consequence.
- No unaddressed conflict with future roadmap items and no avoidable
  dataset-, modality-, backend-, framework-, codec-, or project-specific
  coupling in interfaces/adapters/protocols.
- Traceable to an approved functional requirement.
- Challenged by design implication review with no blocker or major concern.

## Design Implication Review

| Finding | Affected decision or requirement | Maintainability/extensibility impact | Recommended revision | Queue action | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  | record / reopen functionality queue / reopen design queue | pending |

## Future Roadmap And Reuse Safety Review

| Finding | Affected decision or requirement | Future roadmap item or dependency | Interface/adapter/protocol implication | Recommended revision or deferral | Revisit trigger | Queue action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | record / revise design / reopen functionality queue / reopen design queue / defer with trigger | pending |

## Functionality And Decision Audit

| Audit item | Impact | Resolution | Status |
| --- | --- | --- | --- |
|  |  |  | pending |

## Examples And Demonstrations

| Example | Behavior demonstrated | Project context | Required docs/tests | Status |
| --- | --- | --- | --- | --- |
|  |  |  |  | pending |

## Validation Strategy

| Area | Behavior validated | Required coverage | Test/check type | Command or location | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | pending |

## Phase Shaping

| Phase | Goal | Scope | Out of scope | Dependencies | Acceptance criteria | Test expectations | Design impact | Future compatibility | Interface/reuse implications | Reviewability | Risks | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |  |  |  |  |  |  | pending |

## Plan Quality Gate

| Check | Evidence | Result | Required action |
| --- | --- | --- | --- |
| Functionality-agreement queue resolved |  | pass / block |  |
| Behavior confirmation locked |  | pass / block |  |
| Design-agreement queue resolved |  | pass / block |  |
| Roadmap-to-requirement traceability |  | pass / block |  |
| Requirement-to-design traceability |  | pass / block |  |
| Design-to-example traceability |  | pass / block |  |
| Example-to-validation traceability |  | pass / block |  |
| Phase-shaping readiness |  | pass / block |  |
| Future-roadmap compatibility readiness |  | pass / block |  |
| Interface/adapter/protocol reuse readiness |  | pass / block |  |
| Extensibility and maintainability readiness |  | pass / block |  |
| Scientific/workflow contract clarity |  | pass / block |  |
| Reviewability and phase granularity |  | pass / block |  |
| Unresolved ambiguity or blockers |  | pass / block |  |

Gate result:

- Status: pending
- Blocking findings:
- Accepted risks:
- Revisit triggers:

## Accepted Assumptions And Deferrals

| Item | Type | Rationale | Revisit trigger |
| --- | --- | --- | --- |
|  | assumption / deferral |  |  |

## Resume Checkpoints

### After Functionality Agreement

- Queue state:
- Behavior confirmation status:
- Open questions:
- Next step:

### After Design Agreement

- Queue state:
- Implementation shape locked:
- Open questions:
- Next step:

### After Validation, Phase Shaping, And Plan Quality Gate

- Validation baseline locked:
- Phase sketch locked:
- Gate result:
- Open questions:
- Next step:

## Workflow Feedback Routing

| Feedback | Routing | Action | Status |
| --- | --- | --- | --- |
|  | reusable workflow / current-session preference / product requirement |  | pending |

## Change Log

| Round | Update |
| --- | --- |
|  |  |

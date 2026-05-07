# Stage 1 Planning Notes: Learning Evaluation Core

## Metadata

- Roadmap slug: `learning-evaluation-core`
- Source context:
  - `docs/rphys_architecture_plan_v3.md`
  - `docs/implementation/field-centric-architecture-scaffold/planning-notes.md`
  - `docs/roadmap/index.md`
- Planning notes status: draft
- Current discussion stage: roadmap framing
- Related roadmap row: `Learning evaluation core`
- Blockers:
  - Split boundaries have not been confirmed by the maintainer.
  - Dependency on accepted runtime field contracts is unresolved.
  - Design-decision review has not started.

## Stage Gates

| Stage | Status | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- | --- |
| Roadmap framing | draft | Broad architecture is split; this package owns method, learner, loss, prediction, metric, evaluation, and minimal analysis contracts | Runtime Sample/Batch contracts precede this package | Should trainer loops be minimal protocol only? | Confirm scope |
| Intent discovery | draft | None yet | Support supervised, self-supervised, contrastive, classical, signal-processing, and neural methods without hard-coding one style | Which first evaluation flow matters most? | Clarify workflows |
| Capability brainstorming | draft | None yet | Include interfaces and synthetic examples | Full model/trainer/analysis libraries deferred | Mark include/defer |
| Functionality and behavior confirmation | not started | None yet | Predictions are Samples/Batches; metrics consume fields by key | None yet | Confirm behavior |
| Context compaction/reset checkpoint | not started | None yet | Stop with resume instruction if direct compaction is unavailable | None | Record checkpoint |
| Design-decision review | not started | None yet | Review queue below | None yet | Review decisions |
| Phase shaping | not started | None yet | Synthetic method/evaluation first | None yet | Sketch phases |
| Handoff | not started | None yet | Carry accepted contracts into Stage 2 | None yet | Prepare Stage 2 inputs |

## Context Extraction

Baseline outcome:

- Implement the minimal learning and evaluation contract layer while keeping models, methods, learners, trainers, losses, metrics, and aggregation distinct.

Constraints:

- A model is usually a torch module and should not own IO, augmentation, training loops, or evaluation protocols.
- A method predicts fields from Samples/Batches.
- A learner defines training and validation behavior for a learning style.
- A trainer orchestrates loops and device/checkpoint mechanics without knowing the learning style.
- Predictions are Samples/Batches containing prediction fields.
- Metrics consume prediction and reference fields by key.

Deferred or out-of-scope ideas:

- Full neural architecture library.
- Full trainer framework integration.
- Full self-supervised learner catalog.
- Full signal-processing method catalog.
- Full analysis/reporting stack.

Scientific workflow obligations:

- Methods, losses, and metrics must document required fields, units, shapes, sampling assumptions, temporal alignment, aggregation order, and failure behavior.

## User Intent

Target audience:

- Users training or evaluating remote physiological measurement methods.
- Extension authors adding models, methods, learners, losses, and metrics.

User-visible outcome:

- A consistent field-based learning/evaluation scaffold that supports waveform prediction, HR regression, embeddings, quality prediction, and multitask outputs.

Success criteria:

- Synthetic methods can produce prediction fields.
- Losses and metrics can consume fields by key.
- Evaluation supports metric-per-window and aggregate-then-metric workflows.
- Learning style and trainer loop responsibilities are separate.

Non-goals:

- Heavy training framework integration.
- Production model zoo.
- Full paper-ready analysis.

Operational constraints:

- Keep torch-dependent behavior optional or gated if accepted.

## Brainstormed Capabilities

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| `Method` | include, pending confirmation | Standard prediction algorithm interface | Works for neural and signal-processing methods |
| Model boundary | include, pending confirmation | Keeps neural modules focused | Likely torch-optional |
| `Learner` | include, pending confirmation | Encapsulates learning style | Supervised/SSL/contrastive later |
| `Trainer` protocol | maybe | Useful boundary but implementation may be deferred | Avoid full trainer framework early |
| Input/target adapters | include, pending confirmation | Prevent model assumptions leaking into dataset/batch | Field-key based |
| Loss contracts | include, pending confirmation | Supports tensor, field, batch, composite losses | Full loss catalog deferred |
| Predictions as Samples/Batches | include, pending confirmation | Enables arbitrary prediction fields | Required for metrics |
| Metrics and aggregators | include, pending confirmation | Supports multiple evaluation orders | Synthetic metrics first |
| EvaluationProtocol | include, pending confirmation | Captures grouping/order/reports | Report stack minimal |
| Full analysis stack | defer | Heavy optional dependencies and broad scope | Add later |

## Confirmed Functionality And Behavior

Included functionality:

- Pending maintainer confirmation. Proposed scope includes method/model/learner/trainer boundaries, adapters, loss contracts, prediction Samples/Batches, metrics, aggregators, evaluation protocol, and synthetic evaluation tests.

User-visible behavior:

- Pending maintainer confirmation. Users predict fields, train through learners, and evaluate metrics by field key without changing containers for new output types.

Agent-visible behavior:

- Pending maintainer confirmation. Future agents should keep training loops out of models and evaluation logic out of methods.

Default behavior:

- Pending maintainer confirmation. Predictions are normal Samples/Batches; metrics are field-key based; aggregation order is explicit.

Failure behavior and diagnostics:

- Pending maintainer confirmation. Missing prediction/reference fields, unit/schema mismatch, invalid aggregation grouping, and learner output contract failures fail loudly.

Explicit deferrals:

- Pending maintainer confirmation. Full model zoo, production trainer integration, full SSL library, full analysis reports, and heavy plotting/statistics dependencies are deferred.

Out-of-scope behavior:

- Pending maintainer confirmation. Dataset IO, transforms/materialization internals, and generic experiment execution.

## Context Compaction Or Reset Checkpoint

- Checkpoint status: not reached
- Notes path: `docs/implementation/learning-evaluation-core/planning-notes.md`
- Resume instruction: After functionality and behavior are confirmed, compact or reset context, then resume with `.codex/prompts/stage-1-planning-notes-resume.md` and reload this planning notes file before design-decision review.
- Functionality or behavior reopened after checkpoint: none

## Design-Decision Review Queue

| Decision | Why it matters | User feedback needed | Status |
| --- | --- | --- | --- |
| Method/model boundary | Prevents model classes from absorbing experiment logic | Confirm responsibilities | draft |
| Learner/trainer boundary | Supports multiple learning styles | Confirm trainer minimalism | draft |
| Prediction container | Determines evaluation extensibility | Confirm predictions as Samples/Batches | draft |
| Prediction field naming | Prevents collisions | Confirm `prediction.*` conventions | draft |
| Loss abstraction levels | Affects objective extensibility | Confirm tensor/field/batch/composite split | draft |
| Evaluation aggregation order | Affects scientific metric correctness | Confirm sample aggregation before metrics and metric aggregation after | draft |
| Optional torch dependency | Affects package core and CI | Confirm gating strategy | draft |
| Minimal analysis interface | Affects scope | Confirm report/analysis deferral | draft |

## Design Decisions

| Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility and expansion impact | Validation/documentation obligation | Debt and revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None confirmed yet | Pending review | Pending maintainer feedback | Pending review | Stage 1 has not reached design-decision review | Avoids premature training API lock-in | Keeps learning styles extensible | Review required | Revisit after behavior confirmation |

## Practical Design Notes

Public API or documentation surface:

- Proposed contracts: `Method`, `TrainableMethod`, `Learner`, `Trainer`, `InputAdapter`, `TargetAdapter`, `TensorLoss`, `FieldLoss`, `BatchLoss`, `CompositeLoss`, `Metric`, `SampleAggregator`, `MetricAggregator`, and `EvaluationProtocol`.

Workflow and artifact surface:

- Later stages can train, predict, aggregate, compute metrics, and produce reports through these contracts.

Failure modes and diagnostics:

- Missing fields, wrong prediction schema, invalid units, aggregation ambiguity, and learner step output errors.

Extension points and flexibility boundaries:

- Users add methods, models, learners, losses, and metrics through public protocols and `_target_` paths.

Maintainability assessment:

- Separation keeps model code, learning style, trainer mechanics, and metrics independently testable.

Extensibility assessment:

- Prediction fields support waveform, scalar, embedding, mask, landmark, quality, and multitask outputs.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None accepted yet | Design review has not started | Confirm during design-decision review |

## Phase Sketch

### Phase 1 - Synthetic Learning And Evaluation Contracts

Goal:

- Implement minimal field-based method, learner, loss, metric, and evaluation contracts with synthetic tests.

Scope:

- Interfaces, adapters, synthetic method, synthetic loss/metric, aggregators, evaluation protocol smoke.

Out of scope:

- Production trainer, model zoo, full analysis reports.

Acceptance criteria:

- Synthetic prediction fields flow through loss and metric computation with explicit aggregation.

Test expectations:

- Package: import checks.
- Unit: method/loss/metric/adapter tests.
- Contract: prediction fields and aggregation behavior.
- Integration: synthetic predict/evaluate flow.
- E2E: minimal synthetic evaluation protocol.
- Opt-in: torch-gated tests if accepted.

Design impact:

- Locks learning/evaluation boundaries.

Future compatibility:

- Enables neural, classical, signal-processing, and self-supervised methods.

Reviewability:

- Interface-heavy; keep concrete examples synthetic.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Should trainer implementation be deferred to keep this package interface-only? | Scope | Define protocol/minimal loop only | open |
| Should torch be required for losses/models? | Dependencies | Gate torch-dependent tests/features | open |
| Which metric should be the first synthetic example? | Validation | Use simple field-based MAE/correlation fixtures | open |

## Handoff Notes

Master-plan draft inputs:

- `docs/rphys_architecture_plan_v3.md` sections 27-32 and 42-46.
- Accepted runtime field contracts.

Quality-gate risks:

- Scope creep into training framework or model zoo.
- Metrics that accidentally assume one prediction type.
- Optional dependency leakage.

Assumptions to carry forward:

- Runtime Sample/Batch contracts exist before this package.

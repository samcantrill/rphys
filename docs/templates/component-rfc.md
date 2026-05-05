# RFC: <Component Name>

Status: draft
Roadmap item: <link>
GitHub issue: <link or pending>
Legacy evidence: <paths or audit doc>
Owner: <name or agent>

## Summary

Describe the component, why it belongs in `rphys`, and which downstream research workflows it enables.

## Goals

- <Goal 1>
- <Goal 2>

## Non-Goals

- <Explicitly out-of-scope behavior>

## Legacy Evidence

- Legacy paths and symbols:
- Behaviors to retain:
- Behaviors to redesign:
- Behaviors to drop or defer:
- Known legacy defects or ambiguities:

## Scientific Contract

Define:

- Inputs:
- Outputs:
- Units:
- Shapes:
- Dtypes/devices:
- Sampling rates:
- Temporal alignment:
- Normalization/statistic scope:
- Pipeline position:
- Leakage risks:
- Failure behavior:

Use LaTeX notation for important operations, for example:

```text
y_t = f(x_{t-w:t}, theta)
```

## Proposed API

Describe public classes, functions, protocols, configuration objects, and expected import paths.

## Implementation Design

Describe the internal design, separation of concerns, dependencies, and extensibility points.

## Tests And Validation

- Unit tests:
- Behavioral tests:
- Legacy parity fixtures:
- Integration tests:
- Gradient/backward checks:
- Documentation examples:

## References

- <Paper, dataset docs, benchmark docs, or API docs>

## Phased Plan

- Phase 1:
- Phase 2:
- Phase 3:

## Open Questions

- <Question or accepted assumption>

# Scientific Review Workflow

## Purpose

Scientific review checks that an implementation is correct for remote physiological measurement research, not just that the code passes tests.

## Inputs

- PR diff or phase branch.
- Accepted component RFC.
- Phase plan.
- Legacy audit evidence.
- Relevant papers, dataset docs, or benchmark references.
- Test results.

## Review Process

1. Read the RFC before reviewing code.
2. Compare the implementation against the declared pipeline contract.
3. Check legacy evidence and identify intentional behavior changes.
4. Inspect tests as behavioral documentation.
5. Review docstrings and comments for scientific clarity.
6. Report findings by severity with file references and reproduction details when possible.
7. Separate correctness blockers from documentation or follow-up improvements.

## Review Rubric

Check for:

- Input/output shapes, units, dtypes, and device behavior.
- Sampling-rate assumptions and temporal alignment.
- Normalization order and statistic scope.
- Filtering, resampling, interpolation, masking, and windowing semantics.
- Leakage risks across subjects, videos, frames, windows, train/test splits, and labels.
- Handling of NaNs, flat signals, missing data, empty masks, and short inputs.
- Gradient behavior for differentiable losses, transforms, and model components.
- Metric aggregation semantics and confidence interval assumptions.
- Dataset licensing, provenance, and raw-data exclusion.
- Whether docstrings and tests make the behavior clear to future agents and researchers.

## Output Format

Lead with findings:

- Severity.
- File and line when available.
- Problem.
- Why it matters scientifically.
- Suggested fix or required decision.

Then include:

- Tests reviewed.
- Legacy parity status.
- Remaining risks.
- Recommendation: approve, approve with follow-up, or block.

## Exit Criteria

- No unresolved blocker remains.
- Any intentional scientific behavior change is documented in the RFC or PR.
- Tests cover the phase's declared behavioral contract.
- Residual risks are explicit and assigned to follow-up work.

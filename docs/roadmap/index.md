# rphys Roadmap

This roadmap is the canonical planning document for porting and redesigning the legacy rphys codebase. GitHub issues and PRs should link back here and to the relevant RFC.

## Status Values

- `candidate`: identified by audit, not yet accepted for RFC.
- `RFC`: RFC is being drafted or reviewed.
- `planned`: RFC accepted and phase plan pending or accepted.
- `implementing`: phase PRs are active.
- `reviewing`: implementation is waiting for code/scientific review.
- `merged`: accepted into `main`.
- `deferred`: valid but intentionally postponed.
- `dropped`: not planned for the modern library.

## Components

| Component | Status | Legacy Evidence | Target Direction | Validation Needs | Issue |
| --- | --- | --- | --- | --- | --- |
| Datasets and data interfaces | candidate | Pending `LEGACY_REPO_PATH` audit | External raw data, documented dataset interfaces, synthetic fixtures | Loader contract tests, fixture behavior, provenance checks | Pending |
| Signal representations | candidate | Pending `LEGACY_REPO_PATH` audit | Explicit signal containers or typed arrays with units, sampling rate, and shape contracts | Shape/unit tests, NaN/flat/short-signal behavior | Pending |
| Preprocessing | candidate | Pending `LEGACY_REPO_PATH` audit | Composable transforms with explicit ordering and statistic scope | Behavioral tests for filtering, normalization, masking, resampling, leakage | Pending |
| Models | candidate | Pending `LEGACY_REPO_PATH` audit | Modular model components with clear tensor contracts | Shape/device tests, gradient checks, minimal training smoke tests | Pending |
| Training | candidate | Pending `LEGACY_REPO_PATH` audit | Reusable training utilities, not experiment scripts | Determinism, checkpoint, scheduler, loss integration tests | Pending |
| Evaluation and metrics | candidate | Pending `LEGACY_REPO_PATH` audit | Explicit aggregation and benchmark semantics | Metric edge cases, confidence interval assumptions, parity checks | Pending |
| Analysis utilities | candidate | Pending `LEGACY_REPO_PATH` audit | Reusable analysis components with clear statistical assumptions | Statistical behavior tests and reference examples | Pending |

## Next Actions

1. Provide `LEGACY_REPO_PATH`.
2. Run the legacy audit workflow.
3. Replace candidate rows with evidence-backed roadmap items.
4. Draft the first component RFC.

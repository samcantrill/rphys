# Tests

Tests are grouped by intent. The layout follows Loom's suite split, adapted for
`rphys` as a scientific research library rather than an experiment runner.

```text
tests/
  package/      package import, metadata, public API, and import-boundary tests
  unit/         source-mirrored tests for isolated code under src/rphys
  contracts/    executable public contracts for extension points and semantics
  integration/  tests that combine multiple rphys components
  e2e/          full behavior tests through public APIs
  acceptance/   optional real-dataset, hardware, GPU, or long-running checks
  support/      trusted test-only helpers, fixtures, and synthetic generators
```

Unit tests should mirror `src/rphys` below `tests/unit/rphys`. For example,
`src/rphys/data/sample.py` should be tested by
`tests/unit/rphys/data/test_sample.py`.

Package tests protect the public surface and import cost. They should verify
that documented public imports work and that lightweight imports do not pull in
optional video, array, plotting, deep-learning, or dataset-SDK stacks.

Contract tests are reusable compatibility checks for public extension points
and scientific semantics. Use them for datasources, field codecs, operations,
transforms, methods, models, losses, objectives, metrics, learners, trainers,
and analysis components when the behavior is part of the public contract.

Integration and e2e tests must remain license-safe and reproducible. Prefer
synthetic fields, deterministic tiny fixtures, temporary directories, and public
APIs. Do not require raw datasets. If a check needs a real dataset, special
hardware, network access, or a long runtime, put it in `tests/acceptance` and
mark it so it stays out of default validation.

Support modules are not a runnable suite. `tests/support` holds test-only
helpers and synthetic implementations that are validated through the package,
unit, contract, integration, e2e, and acceptance suites that consume them.
Synthetic support should stay generated, deterministic, CPU-only, license-safe,
and private to this repository. Do not treat helper module paths as public API,
and do not add raw data, external services, heavy optional dependencies, or
production imports from `tests.support`.

## Suite Targets

Use the Makefile wrappers for common runs:

```bash
make test
make test-help
make test-package
make test-unit
make test-contract
make test-integration
make test-e2e
make test-acceptance
make test-all
make test-summary
make test-pr-summary
```

`make test` runs the default local suite and excludes tests marked `slow`,
`network`, `optional_dependency`, or `acceptance`. Suite-specific targets print
`not present` while their directories do not yet contain test files.

Summary targets run suites through `tools.test_harness`, write JUnit XML and
optional coverage artifacts, and emit Markdown summaries suitable for PR
validation notes. Use `make test-<suite>-summary` for a focused detailed report
or `make test-summary` for all suites. Use `make test-pr-summary` for a compact
PR-ready validation section under `build/test-pr-summary.md`; pass
`TEST_REPORT_CHECKS=path/to/checks.json` to include explicit manual
Check/Result/Evidence rows. Detailed summaries write artifacts under
`build/test-summary/`; PR summaries write artifacts under
`build/test-pr-summary/`.

## Synthetic Validation Tiers

Debug, smoke, and signal checks should differ by breadth and runtime cost, not
by fixture semantics. Stage 14 synthetic smoke tests use the same generated
datasource descriptors, codecs, manifests, sample builders, operations,
collaters, methods, and export/reload paths as the focused contract and
integration tests. Upstream smoke coverage is explicitly incomplete until the
Stage 13 scan-to-report tail is exercised in its own phase.

Stage 15 exposes `ExperimentTierSpec` as descriptive evidence for debug,
smoke, signal, comparison, and full validation breadths. These specs do not
schedule jobs or define performance thresholds; they record scale knobs and
expected profile, checkpoint, restart, and data-path evidence for the same
execution path.

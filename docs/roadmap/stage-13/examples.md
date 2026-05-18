# Stage 13 Synthetic Composition Examples

Stage 13 uses existing runtime substrates instead of a new prediction,
evaluation, analysis, report, or dataset-formatting engine. The canonical shape
is ordinary Python composition over code-backed records:

```text
Sample fields
-> collate_samples(...)
-> Method.predict(...) or SupervisedLearner.step(...)
-> returned Batch with predictions/* fields
-> explicit uncollate_batch_fields(...)
-> sample artifact export/save
-> derived datasource reload
-> SampleCollection grouping, sorting, metric, visualization, and report ops
-> optional item-to-export mapping for formatted derived datasets
```

The integration tests keep the examples executable:

- `tests/integration/test_stage13_synthetic_composition_flow.py` shows
  Batch-native method prediction, learner returned-`Batch` output, target
  pass-through, and explicit uncollation into per-sample prediction fields.
- `tests/integration/test_stage13_sample_artifact_flow.py` shows prediction and
  target fields exported one sample artifact per source record, reloaded
  through derived datasource/index/sample-builder behavior, then reused by two
  separate recipes: metric/visualization/report construction and
  dataset-formatting-like collection concatenation.
- `tests/integration/test_stage13_synthetic_sample_collection_pipeline.py`
  shows evaluation-like grouping, sorting, collection metric binding, and
  stitching through `OperationPipeline`.

These examples intentionally avoid public `PredictionRunner`,
`EvaluationRunner`, `EvaluationEngine`, `InferenceEngine`, `PipelineJob`,
`JobPlan`, `JobRunner`, `AnalysisOp`, `AnalysisResult`, report writers,
dataframes, plotting backends, output-directory schemas, dashboards, artifact
stores, checkpoint selection, and training-log crawling.

## Contract Notes

- Prediction is field meaning on ordinary `Batch` or `Sample` containers.
- Durable handoff is explicit: uncollate first, export/save through field
  codecs, then reload as a derived datasource.
- Metric and visualization outputs are ordinary fields, so grouping, reporting,
  and formatted-dataset handoff can reuse `SampleCollection` operations.
- `Report` and `ReportTable` are in-memory records. Future save/render adapters
  can consume them additively without changing Stage 13 core behavior.
- Scope remains inspectable through field locators, sample/collection metadata,
  operation metadata, and report row provenance.

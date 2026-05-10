A good way to structure this is to treat the whole package as two related systems:

```text
1. Runtime/batch system
   Batch -> Batch

2. Artifact/stage system
   Artifact(s) -> Artifact(s)
```

Most confusion comes from mixing those two levels. A `Loss`, `Metric`, `Method`, or `Transform` usually operates at the batch level. A `TrainStage`, `PredictStage`, `EvaluateStage`, or `AnalysisStage` operates at the artifact level. This matches the boundary in your `rphys` spec: `loom` owns generic artifact/stage execution, while the domain package owns concrete data, methods, losses, metrics, training logic, evaluation logic, and analysis logic. 

## 1. Core mental model

The cleanest abstraction is:

```text
Batch operators:
  Batch -> Batch

Artifact operators / stages:
  ArtifactRefs -> ArtifactRefs
```

At the batch level, almost everything can be seen as adding, replacing, or checking fields:

```text
input batch
  -> method adds prediction fields
  -> objective/loss adds differentiable loss fields
  -> metric adds metric observations or updates metric state
  -> postprocessor adds derived prediction fields
```

Example:

```text
Batch(
  video.rgb,
  signal.bvp.reference
)

Method:
  adds prediction.signal.bvp

Loss:
  adds loss.waveform_pearson
  adds loss.total

Metric:
  adds metric.window_pearson
  or updates a metric accumulator
```

At the artifact level:

```text
DatasetArtifact
  -> BuildIndexStage
  -> IndexArtifact

IndexArtifact + MethodCheckpoint
  -> PredictStage
  -> PredictionArtifact

PredictionArtifact + ReferenceArtifact
  -> EvaluateStage
  -> MetricReportArtifact

MetricReportArtifact
  -> AnalysisStage
  -> Tables/Figures/Report
```

So yes: many things are “the same thing” in the sense that they are transformations with declared inputs and outputs. But you still want different names because they have different semantics, side effects, and lifecycle rules.

## 2. Recommended top-level concepts

I would define these core concepts:

```text
Field
  A named value inside a Batch.

Batch
  A field container passed through runtime computation.

BatchOperator
  Something that reads fields and writes fields.

Method
  A BatchOperator that produces prediction/representation/action fields.

Model
  A lower-level trainable function, often torch.nn.Module.

Objective / Loss
  A BatchOperator or callable that produces differentiable optimization fields.

Metric
  A measurement object that computes or accumulates non-training measurements.

Learner
  Defines train/validation/test/predict step semantics.

Trainer
  Executes loops, devices, optimization, checkpointing, logging.

Evaluator
  Runs prediction aggregation, metric computation, and metric aggregation.

Analyzer
  Consumes reports/artifacts and produces tables, plots, diagnostics.

Stage
  Artifact-level wrapper around any of the above.
```

The most important separation is:

```text
Model:
  tensor function

Method:
  algorithm that maps Batch fields to prediction fields

Learner:
  defines how a Method is trained or validated

Trainer:
  executes the training loop without knowing domain semantics
```

## 3. Batch and fields

Use a field-based `Batch` rather than hard-coded attributes.

```python
@dataclass
class Field:
    value: Any
    role: str | None = None
    schema: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Batch:
    fields: dict[str, Field]
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        field = self.fields.get(key)
        return default if field is None else field.value

    def require(self, key: str, expected_type: type | None = None) -> Any:
        if key not in self.fields:
            raise KeyError(f"Missing required field: {key}")
        value = self.fields[key].value
        if expected_type is not None and not isinstance(value, expected_type):
            raise TypeError(f"{key} expected {expected_type}, got {type(value)}")
        return value

    def set(self, key: str, value: Any, **metadata) -> "Batch":
        self.fields[key] = Field(value=value, metadata=metadata)
        return self
```

Then everything can use field keys:

```text
input.image
input.video
target.class
target.signal
prediction.logits
prediction.signal
loss.total
loss.ce
metric.accuracy
metric.rmse
embedding.video
```

This gives you one common data path for supervised learning, self-supervised learning, prediction, evaluation, and analysis.

## 4. BatchOperator as the base abstraction

A very useful base abstraction is:

```python
class BatchOperator(Protocol):
    input_contract: "FieldContract"
    output_contract: "FieldContract"

    def __call__(self, batch: Batch, context: "RuntimeContext") -> Batch:
        ...
```

This is the general form.

Then specialize semantically:

```text
Transform:
  Batch -> Batch, usually preprocessing/postprocessing.

Method:
  Batch -> Batch, adds prediction fields.

Objective:
  Batch -> Batch, adds differentiable loss fields.

Metric:
  Batch -> Batch or Batch -> metric state update.

Check:
  Batch -> Batch, raises or annotates.

Adapter:
  Batch -> model inputs, model outputs -> Batch fields.
```

The base is shared, but the semantic names are still valuable.

## 5. Loss versus metric

A loss and a metric can share a similar interface, but they should remain separate concepts.

A loss is:

```text
used for optimization
usually differentiable
usually computed during training
usually reduced to a scalar or small set of scalar terms
part of the backward graph
```

A metric is:

```text
used for measurement
usually detached/no_grad
often aggregated over batches, records, subjects, datasets, or epochs
not necessarily differentiable
not used directly for gradient updates
```

So your idea is good:

```text
Loss takes a Batch and adds differentiable loss fields.
Metric takes a Batch and adds metric fields or updates metric state.
```

But I would refine it:

```python
class Objective(BatchOperator):
    loss_key: str = "loss.total"

    def __call__(self, batch: Batch, context: RuntimeContext) -> Batch:
        ...
```

Example:

```text
Objective input:
  prediction.signal
  target.signal

Objective output:
  loss.pearson
  loss.smoothness
  loss.total
```

Metric can be:

```python
class Metric(Protocol):
    input_contract: FieldContract

    def update(self, batch: Batch, context: RuntimeContext) -> None:
        ...

    def compute(self) -> "MetricResult":
        ...

    def reset(self) -> None:
        ...
```

Some metrics can also write fields:

```python
class BatchMetric(BatchOperator):
    def __call__(self, batch: Batch, context: RuntimeContext) -> Batch:
        batch.set("metric.window_rmse", rmse)
        return batch
```

The distinction I recommend:

```text
Objective/Loss:
  produces differentiable fields, especially loss.total.

Metric:
  produces detached observations and/or accumulated reports.
```

You can share implementation through a common `Measure` base:

```python
class Measure:
    prediction_key: str
    target_key: str
    output_key: str

class Loss(Measure, torch.nn.Module):
    differentiable = True

class Metric(Measure):
    differentiable = False
```

But do not collapse the names. The names communicate intent.

## 6. Method versus model

A `Model` should be narrow.

```text
Model:
  tensor function, usually trainable
  often torch.nn.Module
  does not know experiment stages
  ideally does not know artifact paths
  may not know Batch unless intentionally designed that way
```

A `Method` should be broader.

```text
Method:
  algorithm that consumes Batch fields and produces output fields
  may wrap one model, many models, no model, or a signal-processing algorithm
  owns input/output field semantics
  can be trainable or non-trainable
```

Examples:

```text
PhysNet torch.nn.Module:
  Model

SupervisedPhysNetMethod:
  Method wrapping PhysNet, input adapter, output adapter

CHROM:
  Method with no neural model

EnsembleMethod:
  Method wrapping several methods/models

TeacherStudentMethod:
  Method wrapping teacher and student models

SelfSupervisedEncoderMethod:
  Method producing embeddings or reconstruction predictions
```

So I would not say “Model is a TrainableMethod.” I would say:

```text
A trainable Method may contain one or more Models.

A Model is usually lower-level than a Method.
```

A possible interface:

```python
class Method(Protocol):
    input_contract: FieldContract
    output_contract: FieldContract

    def predict(self, batch: Batch, context: RuntimeContext) -> Batch:
        ...
```

A trainable method can add:

```python
class TrainableMethod(Method, Protocol):
    def parameters(self) -> Iterable[torch.nn.Parameter]:
        ...

    def state_dict(self) -> dict[str, Any]:
        ...

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        ...

    def train(self, mode: bool = True) -> None:
        ...

    def eval(self) -> None:
        ...
```

For a neural model wrapper:

```python
class TorchModelMethod:
    def __init__(
        self,
        model: torch.nn.Module,
        input_adapter: "InputAdapter",
        output_adapter: "OutputAdapter",
    ):
        self.model = model
        self.input_adapter = input_adapter
        self.output_adapter = output_adapter

    def predict(self, batch: Batch, context: RuntimeContext) -> Batch:
        kwargs = self.input_adapter(batch)
        raw_output = self.model(**kwargs)
        return self.output_adapter(batch, raw_output)
```

This keeps `torch.nn.Module` models clean while allowing arbitrary methods.

## 7. Adapters

Adapters are the glue that prevent every component from depending on every other component.

Important adapters:

```text
InputAdapter
  Batch -> model kwargs / tensors

OutputAdapter
  raw model output -> Batch prediction fields

TargetAdapter
  Batch -> target tensors or target fields

LossAdapter
  Batch -> loss inputs

MetricAdapter
  Batch -> metric inputs

BatchAdapter
  arbitrary batch structure -> standard Batch

ArtifactAdapter
  artifact payload -> runtime object
```

For example:

```python
class InputAdapter(Protocol):
    def __call__(self, batch: Batch) -> Mapping[str, Any]:
        ...


class OutputAdapter(Protocol):
    def __call__(self, batch: Batch, raw_output: Any) -> Batch:
        ...
```

For a video model:

```python
class VideoOnlyInputAdapter:
    def __init__(self, video_key="input.video"):
        self.video_key = video_key

    def __call__(self, batch: Batch) -> dict[str, Any]:
        video = batch.require(self.video_key)
        return {"x": video}
```

For output:

```python
class SignalOutputAdapter:
    def __init__(self, output_key="prediction.signal"):
        self.output_key = output_key

    def __call__(self, batch: Batch, raw_output: torch.Tensor) -> Batch:
        batch.set(self.output_key, raw_output, role="prediction")
        return batch
```

Adapters make models reusable across datasets and tasks.

## 8. Learner versus trainer

This is one of the most important separations.

A `Learner` defines the learning semantics.

```text
Learner knows:
  how to run a training step
  how to run a validation step
  how to run a test step
  how to run a prediction step
  which method to call
  which objective/loss to compute
  which metrics to update
  which fields are expected
```

A `Trainer` defines execution mechanics.

```text
Trainer knows:
  epochs
  dataloaders
  devices
  distributed execution
  AMP/autocast
  gradient accumulation
  backward
  optimizer stepping
  scheduler stepping
  checkpointing
  logging hooks
```

The trainer should not know whether you are doing supervised learning, self-supervised learning, contrastive learning, masked modeling, or reinforcement learning.

Recommended interface:

```python
@dataclass
class StepOutput:
    batch: Batch
    loss: torch.Tensor | None = None
    logs: dict[str, Any] = field(default_factory=dict)


class Learner(Protocol):
    def training_step(self, batch: Batch, context: "StepContext") -> StepOutput:
        ...

    def validation_step(self, batch: Batch, context: "StepContext") -> StepOutput:
        ...

    def test_step(self, batch: Batch, context: "StepContext") -> StepOutput:
        ...

    def predict_step(self, batch: Batch, context: "StepContext") -> Batch:
        ...
```

Then trainer:

```python
class Trainer:
    def fit(self, learner: Learner, train_loader, val_loader=None):
        for epoch in range(self.max_epochs):
            for batch in train_loader:
                output = learner.training_step(batch, context)
                output.loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()

            if val_loader is not None:
                with torch.no_grad():
                    for batch in val_loader:
                        learner.validation_step(batch, context)
```

The trainer executes. The learner defines meaning.

## 9. Training, validation, testing, prediction, evaluation, analysis

These terms should not be collapsed, even though their mechanics overlap.

### Training

```text
Purpose:
  update parameters

Batch-level:
  Batch -> Method -> predictions -> Objective -> loss.total

Allowed side effects:
  gradients
  optimizer step
  scheduler step
  training metrics
  checkpoint updates

Artifact output:
  checkpoint
  training report
```

### Validation

```text
Purpose:
  measure during training for model selection or early stopping

Batch-level:
  Batch -> Method -> predictions -> metrics/losses

Allowed side effects:
  metric accumulation
  best-checkpoint selection
  no optimizer update

Artifact output:
  validation report
  selection signal
```

### Testing

```text
Purpose:
  final held-out assessment

Batch-level:
  Batch -> Method -> predictions -> metrics

Allowed side effects:
  metric accumulation
  prediction writing
  no model selection if strict

Artifact output:
  final metric report
  prediction artifact
```

### Prediction / inference

```text
Purpose:
  produce outputs, possibly without targets

Batch-level:
  Batch -> Method -> prediction fields

Allowed side effects:
  writing predictions

Artifact output:
  prediction set
```

### Evaluation

```text
Purpose:
  compare predictions to references under a protocol

Artifact-level:
  prediction artifact + reference artifact -> metric report

May include:
  prediction aggregation
  per-record reconstruction
  metric computation
  metric aggregation
```

### Analysis

```text
Purpose:
  interpret results after evaluation

Artifact-level:
  metric reports / prediction artifacts / logs -> tables, figures, diagnostics

Should not:
  train models
  select checkpoints
  mutate predictions
```

The distinction is less about function signature and more about lifecycle, allowed side effects, and scientific meaning.

## 10. Phase or mode abstraction

You can represent training, validation, testing, and prediction as modes:

```python
class Mode(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    PREDICT = "predict"
```

Use context:

```python
@dataclass
class StepContext:
    mode: Mode
    epoch: int | None = None
    step: int | None = None
    device: str | None = None
    global_step: int | None = None
    split: str | None = None
    grad_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
```

Then the same learner can behave differently by mode:

```python
if context.mode == Mode.TRAIN:
    compute loss with grad
elif context.mode == Mode.PREDICT:
    only add prediction fields
```

But keep separate methods for clarity:

```text
training_step
validation_step
test_step
predict_step
```

This makes subclassing and extension easier.

## 11. Unified BatchProgram idea

A powerful unifying abstraction is:

```python
class BatchProgram:
    steps: list[BatchOperator]

    def __call__(self, batch: Batch, context: RuntimeContext) -> Batch:
        for step in self.steps:
            batch = step(batch, context)
        return batch
```

Then:

```text
PredictionProgram:
  pre transforms
  method
  post transforms

TrainingProgram:
  pre transforms
  method
  objective/loss
  training metrics

EvaluationProgram:
  method or loaded predictions
  postprocessing
  metrics
```

But I would not expose everything as only `BatchProgram`. Use it internally or as a compositional base. Public semantic classes should still exist:

```text
Method
Objective
Metric
Learner
Evaluator
```

Otherwise the code becomes too abstract and loses meaning.

## 12. Artifact-level abstraction

At the artifact level, stages can be treated uniformly:

```python
class Stage(Protocol):
    input_contract: ArtifactContract
    output_contract: ArtifactContract

    def run(self, inputs: Mapping[str, ArtifactRef], context: StageContext) -> Mapping[str, ArtifactRef]:
        ...
```

Examples:

```text
BuildIndexStage:
  DatasetRef -> IndexArtifact

TrainStage:
  IndexArtifact + MethodConfig -> CheckpointArtifact + TrainingReport

PredictStage:
  IndexArtifact + CheckpointArtifact -> PredictionArtifact

EvaluateStage:
  PredictionArtifact + ReferenceArtifact -> MetricReport

AnalysisStage:
  MetricReport -> Tables/Figures/AnalysisReport
```

This is where your line is exactly right:

```text
define input artifact
define output artifact
define transformation process
```

That is the artifact/stage layer. The batch layer is:

```text
define input fields
define output fields
define batch transformation process
```

## 13. Recommended package structure

For a general ML experimentation package:

```text
mlpkg/
  core/
    fields.py
    batch.py
    contracts.py
    context.py
    operators.py
    errors.py

  data/
    datasets.py
    dataloaders.py
    collate.py
    sampling.py

  transforms/
    batch.py
    augmentation.py
    checks.py
    pipelines.py

  methods/
    base.py
    torch_method.py
    ensembles.py
    signal_processing.py

  models/
    base.py
    architectures/
    layers/
    heads/

  objectives/
    base.py
    losses.py
    composite.py
    adapters.py

  metrics/
    base.py
    field_metrics.py
    aggregation.py

  learning/
    learners.py
    supervised.py
    self_supervised.py
    contrastive.py
    masked_modeling.py

  training/
    trainers.py
    optim.py
    checkpointing.py
    callbacks.py

  prediction/
    predictors.py
    writers.py
    prediction_sets.py

  evaluation/
    protocols.py
    evaluators.py
    aggregation.py
    reports.py

  analysis/
    tables.py
    plots.py
    statistics.py
    diagnostics.py

  stages/
    data.py
    training.py
    prediction.py
    evaluation.py
    analysis.py

  recipes/
    data.py
    methods.py
    experiments.py

  testing/
    fixtures.py
    synthetic.py
    contract_tests.py
```

For `rphys`, the domain-specific versions of these belong in `rphys`, while generic config, artifact store, and stage execution stay in `loom`.

## 14. A concrete supervised learner

Example:

```python
class SupervisedLearner:
    def __init__(
        self,
        method: Method,
        objective: Objective,
        train_metrics: Sequence[Metric] = (),
        eval_metrics: Sequence[Metric] = (),
    ):
        self.method = method
        self.objective = objective
        self.train_metrics = list(train_metrics)
        self.eval_metrics = list(eval_metrics)

    def training_step(self, batch: Batch, context: StepContext) -> StepOutput:
        batch = self.method.predict(batch, context)
        batch = self.objective(batch, context)

        for metric in self.train_metrics:
            metric.update(batch, context)

        loss = batch.require("loss.total", torch.Tensor)
        return StepOutput(batch=batch, loss=loss)

    def validation_step(self, batch: Batch, context: StepContext) -> StepOutput:
        batch = self.method.predict(batch, context)

        with torch.no_grad():
            batch = self.objective(batch, context)
            for metric in self.eval_metrics:
                metric.update(batch, context)

        loss = batch.get("loss.total")
        return StepOutput(batch=batch, loss=loss)

    def predict_step(self, batch: Batch, context: StepContext) -> Batch:
        return self.method.predict(batch, context)
```

The trainer does not know what the fields mean.

## 15. A signal-processing method

```python
class CHROMMethod:
    input_contract = FieldContract(required=["input.video"])
    output_contract = FieldContract(produced=["prediction.signal"])

    def __init__(self, video_key="input.video", output_key="prediction.signal"):
        self.video_key = video_key
        self.output_key = output_key

    def predict(self, batch: Batch, context: StepContext) -> Batch:
        video = batch.require(self.video_key)
        signal = chrom_algorithm(video)
        batch.set(self.output_key, signal, role="prediction")
        return batch
```

This method has no neural model and no optimizer, but it can be evaluated with the same evaluation protocol as a neural model.

## 16. A contrastive learner

```python
class ContrastiveLearner:
    def __init__(
        self,
        view_builder: BatchOperator,
        method: Method,
        objective: Objective,
        metrics: Sequence[Metric] = (),
    ):
        self.view_builder = view_builder
        self.method = method
        self.objective = objective
        self.metrics = list(metrics)

    def training_step(self, batch: Batch, context: StepContext) -> StepOutput:
        batch = self.view_builder(batch, context)
        batch = self.method.predict(batch, context)
        batch = self.objective(batch, context)

        for metric in self.metrics:
            metric.update(batch, context)

        return StepOutput(
            batch=batch,
            loss=batch.require("loss.total", torch.Tensor),
        )
```

The trainer is unchanged.

## 17. Recommended base interfaces

At minimum, I would define:

```python
class BatchOperator(Protocol):
    input_contract: FieldContract
    output_contract: FieldContract

    def __call__(self, batch: Batch, context: RuntimeContext) -> Batch:
        ...


class Method(Protocol):
    input_contract: FieldContract
    output_contract: FieldContract

    def predict(self, batch: Batch, context: RuntimeContext) -> Batch:
        ...


class Objective(Protocol):
    input_contract: FieldContract
    output_contract: FieldContract
    loss_key: str

    def __call__(self, batch: Batch, context: RuntimeContext) -> Batch:
        ...


class Metric(Protocol):
    input_contract: FieldContract

    def update(self, batch: Batch, context: RuntimeContext) -> None:
        ...

    def compute(self) -> MetricResult:
        ...

    def reset(self) -> None:
        ...


class Learner(Protocol):
    def training_step(self, batch: Batch, context: StepContext) -> StepOutput:
        ...

    def validation_step(self, batch: Batch, context: StepContext) -> StepOutput:
        ...

    def test_step(self, batch: Batch, context: StepContext) -> StepOutput:
        ...

    def predict_step(self, batch: Batch, context: StepContext) -> Batch:
        ...


class Trainer(Protocol):
    def fit(self, learner: Learner, datamodule: Any) -> TrainingResult:
        ...

    def validate(self, learner: Learner, dataloader: Any) -> MetricReport:
        ...

    def test(self, learner: Learner, dataloader: Any) -> MetricReport:
        ...

    def predict(self, learner: Learner, dataloader: Any) -> PredictionSet:
        ...
```

## 18. Naming recommendation

Use these names:

```text
Objective
  Preferred package-level name for trainable optimization terms.

Loss
  A common Objective implementation.

Metric
  Measurement, not optimization.

Method
  Prediction algorithm over Batches.

Model
  Parameterized tensor module, usually torch.nn.Module.

Learner
  Step semantics for training/validation/test/predict.

Trainer
  Execution engine.

Evaluator
  Prediction/metric protocol runner.

Analyzer
  Post-hoc report/diagnostic generator.

BatchOperator
  General Batch -> Batch primitive.

Stage
  Artifact-level operation.
```

I would use `Objective` in the architecture and `Loss` in concrete implementations:

```text
Objective:
  abstract concept

NegativePearsonLoss:
  concrete objective/loss
```

That leaves room for objectives that are not conventionally called losses.

## 19. Practical rule for where code belongs

Use this decision table:

```text
Does it map tensors to tensors?
  Model or op.

Does it map Batch fields to prediction fields?
  Method.

Does it define how to train/validate/test/predict?
  Learner.

Does it run epochs, devices, optimizers, checkpoints?
  Trainer.

Does it produce differentiable optimization fields?
  Objective/Loss.

Does it measure outputs and aggregate results?
  Metric/Evaluator.

Does it transform one Batch into another Batch?
  BatchOperator / Transform.

Does it transform artifacts into artifacts?
  Stage.

Does it produce tables, plots, diagnostics?
  Analysis.
```

## 20. Core recommendation

The design I would use is:

```text
Batch is the universal runtime data container.

BatchOperator is the universal runtime transformation shape.

Method is a semantic BatchOperator that adds predictions.

Objective/Loss is a semantic BatchOperator that adds differentiable optimization fields.

Metric is a semantic measurement object that consumes prediction/reference fields and aggregates observations.

Learner composes Method + Objective + Metrics into mode-specific steps.

Trainer executes Learner steps without understanding the learning style.

Evaluator computes field-based metrics from predictions and references.

Analyzer consumes evaluation artifacts and produces interpretation artifacts.

Stage wraps any of the above as artifact-level transformations.
```

This gives you a unified abstraction without flattening all concepts into meaningless “functions.” It keeps the software extensible while preserving useful semantic boundaries.

# Roadmap Stage 12 Planning

Status: design implication review recorded; design approval blocked pending
specialist evidence and maintainer decision packets
Roadmap version: `v12`
Stage directory: `docs/roadmap/stage-12/`

## Overview

Stage 12 introduces the first reusable learning and training layer for
`rphys`. The design separates scientific step semantics from loop mechanics:

- A `Learner` defines what one train, validation, test, or prediction step
  means for the scientific method, objective, metrics, diagnostics, and
  provenance.
- A `Trainer` defines how batches are iterated, how step contexts are created,
  how backward and optimizer mechanics happen, how events and profiles are
  emitted, and how a training result is summarized.

This keeps `rphys` useful as a reusable research library without making it a
project workflow runtime. Datasource discovery, dataloader construction, config
parsing, artifact stores, experiment sweeps, export/materialization, and
framework-specific runners remain outside Stage 12 core.

## Why This Stage Exists

The adjacent contracts are already split by responsibility:

- Stage 10 `Method` objects predict from `Sample` or `Batch` containers and
  return patch-like `MethodOutput` records.
- Stage 11 is expected to define objective, loss, and metric contracts.
- Stage 12 composes those contracts into learning steps and training loops.
- Stage 13 can later consume predictions, metric observations, diagnostics,
  and training summaries for prediction and evaluation.
- Stage 15 can later expand training events and profiling.

The main pressure is to avoid mixing these concerns too early. A method should
not own optimizer stepping. A learner should not build dataloaders or write
checkpoints. A trainer should not parse physiological selectors or compute
losses and metrics. Optional framework adapters should map into the same
library-level contracts without pulling framework imports into core.

## Proposed Public Structure

Stage 12 should open only scoped, code-backed module surfaces:

```text
rphys.learning.modes          # LoopMode
rphys.learning.context        # LoopContext and related context records
rphys.learning.output         # StepOutput, BackwardableScalar
rphys.learning.core           # Learner protocol
rphys.learning.supervised     # SupervisedLearner

rphys.training.plan           # TrainingPlan
rphys.training.results        # TrainingResult and summaries
rphys.training.backend        # backend/device/optimizer descriptors
rphys.training.events         # TrainingEvent, sinks, callbacks
rphys.training.profiling      # profile/span records
rphys.training.core           # Trainer facade, TrainingEngine, NativeTrainingEngine
rphys.training.experimental   # run_train
```

Package exports should expose only implemented names. Stage 12 should not add
root-level exports such as `rphys.Trainer`, placeholder modules, registries, or
stable package-level convenience helpers.

## Responsibility Map

| Object or module | Owns | Does not own |
| --- | --- | --- |
| `LoopMode` | The execution mode: train, validate, test, predict. | Dataset split, workflow stage, artifact state. |
| `LoopContext` | Primitive loop metadata such as mode, epoch, step, batch index, split name, metadata, and provenance. | Datasource construction or global runtime state. |
| `Learner` | Structural protocol for one step over a `Batch` plus context, returning `StepOutput`. | Optimizer stepping, scheduler stepping, checkpoint writing, dataloader construction, export. |
| `SupervisedLearner` | Composition of Stage 10 method output with optional Stage 11 objective and metrics. | Framework lifecycle, device movement, optimizer policy, artifact persistence. |
| `StepOutput` | Predictions, objective scalar, detached terms/metrics, diagnostics, metadata, and provenance. | Loop control, device movement, persistence, export materialization. |
| `Trainer` | User-facing RemotePhys facade that dispatches to a selected training engine and normalizes `TrainingResult`. | Scientific loss/metric computation, datasource scanning, config parsing, workflow runtime, hard framework imports. |
| `TrainingEngine` | Actual loop-control boundary for native or delegated execution. | Scientific step semantics or public workflow configuration. |
| `NativeTrainingEngine` | Dependency-light reference loop over already-built `Batch` iterables, step contexts, backward, optimizer mechanics, events, profiles, and results. | Lightning-sized logging, checkpoint, profiler, callback, distributed, or dataloader features. |
| `TrainingPlan` | Assembled objects and primitive loop settings for a trainer run. | Serializable project config, Hydra schema, dataset path schema, artifact manifest. |
| `TrainingResult` | Summary of statuses, counts, failures, metrics, events, profiles, and step summaries. | Durable run storage or report generation. |
| Backend descriptors | Caller-owned hooks for device movement, backward, optimizers, schedulers, and related mechanics. | Backend catalogs, hard torch/JAX/Lightning imports, distributed runtime implementation. |
| Events/profiles/callbacks | Dependency-light observability records and observe-only callbacks. | Logger integrations, callback loop control, hidden synchronization side effects. |
| `run_train` | Experimental delegation to an assembled plan, trainer, and learner. | Config parsing, dataloader construction, artifact writing, stable workflow API. |

## Core Step Contract

The structural learner shape is intentionally small:

```python
class Learner(Protocol):
    def step(self, batch: Batch, context: LoopContext) -> StepOutput:
        ...
```

Custom learners can satisfy this protocol without subclassing a shared base
class or registering symbolic names. This matches the repository preference for
importable Python objects and avoids premature registries.

`LoopMode` is distinct from split identity:

```python
context = LoopContext(
    mode=LoopMode.TRAIN,
    epoch_index=0,
    step_index=12,
    batch_index=12,
    split_name="train",
    metadata={"smoke_test": True},
    provenance={"source": "synthetic"},
)
```

`mode=LoopMode.TRAIN` controls learning mechanics such as backward and
optimizer stepping. `split_name="train"` is provenance about the data. They are
often aligned, but they are not the same contract.

## StepOutput

`StepOutput` is the boundary between learner semantics and trainer mechanics:

```python
step = StepOutput(
    predictions=method_output,
    objective=objective_result.total,
    loss_terms={"waveform_mse": detached_loss_value},
    objective_terms={"total": detached_objective_value},
    metric_values={"heart_rate_mae": detached_metric_value},
    diagnostics={"num_valid_targets": 31},
    metadata={"window_seconds": 10.0},
    provenance={"objective": "SupervisedPulseObjective"},
)
```

The trainer interprets only `StepOutput.objective` for backward. Predictions,
loss terms, objective terms, metrics, diagnostics, metadata, and provenance stay
opaque to the trainer except for summaries and event/result recording.

The approved provisional prediction shape is:

```python
MethodOutput | Sample | Batch | None
```

`SupervisedLearner` should default to returning Stage 10 `MethodOutput`, because
that preserves patch semantics. The broader union keeps room for Stage 13 to
decide whether prediction/evaluation should consume patch-like outputs,
materialized `Sample` objects, materialized `Batch` objects, or no predictions.

Backward compatibility is intentionally minimal. If no backend adapter overrides
backward behavior, train mode expects an objective scalar with a small
`.backward()`-compatible surface:

```python
step.objective.backward()
```

Non-`.backward()` frameworks can be supported later through backend adapters
without changing learner or objective contracts.

## Supervised Learner

`SupervisedLearner` is the only concrete learner in Stage 12. It composes:

- a Stage 10 `Method`;
- an optional Stage 11 `Objective`;
- optional Stage 11 metrics.

Conceptual flow:

```python
prediction = method.predict(batch, context=context)

working_batch = apply_prediction_patch_for_local_use(batch, prediction)

objective_result = objective(working_batch, context=context)
metric_results = [metric(working_batch, context=context) for metric in metrics]

return StepOutput(
    predictions=prediction,
    objective=objective_result.total,
    metric_values=detach_metric_results(metric_results),
)
```

The local working batch is only for objective and metric computation. It should
not become an export path or a persistent materialization contract.

Prediction mode works without objective or targets:

```python
learner = SupervisedLearner(method=method)

step = learner.step(
    batch,
    LoopContext(mode=LoopMode.PREDICT, batch_index=0),
)

assert step.objective is None
assert step.predictions is not None
```

Train mode should fail clearly when backward is required but no objective is
available. Validation, test, and prediction must not accidentally step
optimizers.

## Native Engine Flow

The native engine consumes already-built `Batch` iterables behind the
RemotePhys `Trainer` facade:

```python
trainer = Trainer(engine=NativeTrainingEngine())

result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

The native engine loop is mechanical:

```text
for epoch in epochs:
  for batch_index, batch in enumerate(train_batches):
    context = LoopContext(mode=TRAIN, epoch_index=epoch, batch_index=batch_index)
    batch = device_mover(batch)                         # if configured
    step = learner.step(batch, context)
    backward(step.objective)                            # train mode only
    optimizer.step()                                    # train mode only
    scheduler.step()                                    # if configured
    emit events and profile spans

return TrainingResult(...)
```

Mode-specific entrypoints should be explicit:

```python
trainer.fit(...)
trainer.validate(...)
trainer.test(...)
trainer.predict(...)
```

For the native engine, `Trainer.run(plan)` should be a thin dispatch helper over
the same methods, not a separate workflow runtime. For delegated engines,
`Trainer.run(plan)` dispatches to the selected engine instead of running the
native loop.

## Training Plan And Result

`TrainingPlan` is assembled-object oriented:

```python
plan = TrainingPlan(
    train_batches=train_batches,
    validate_batches=validate_batches,
    max_epochs=5,
    device_mover=device_mover,
    optimizer=optimizer_spec,
    event_sinks=[recording_sink],
    profilers=[profiler],
    metadata={"run_label": "synthetic-smoke"},
)
```

It should not accept raw project configuration, dataset paths, artifact
directories, or serialization promises.

`TrainingResult` summarizes what happened:

```python
result = TrainingResult(
    status="completed",
    epochs_completed=5,
    steps_completed=1200,
    failures=[],
    metric_summaries={"val_heart_rate_mae": 1.8},
    event_summary=event_summary,
    profile_summary=profile_summary,
)
```

Downstream workflow tools can persist or report this result, but Stage 12 core
does not write durable run artifacts.

## Events And Profiling

Stage 12 defines dependency-light event and profile records so native and
future framework-backed execution can produce comparable evidence:

```python
event = TrainingEvent(
    source="native",
    mode=LoopMode.TRAIN,
    phase="optimizer_step",
    position="end",
    epoch_index=0,
    step_index=12,
    batch_index=12,
    status="ok",
    metadata={"optimizer": "fake"},
)
```

The controlled phase/span vocabulary should cover dataloader wait, device
transfer, forward, objective/loss, backward, optimizer step, callbacks/logging,
checkpointing, validation/test/predict, whole-step timing, unavailable probes,
and synchronization overhead.

Callbacks are observe-only in Stage 12. They can receive events and contexts,
but they cannot change learner semantics, request loop control, or become
logger-specific integration points.

## Trainer Engine Architecture And Delegated Control

RemotePhys should keep `Trainer` and `Learner` as the stable library-facing
paradigm, but it should not require the native trainer loop to implement every
feature that mature external engines already provide. The design should treat
loop execution as an engine boundary:

```text
RemotePhys Trainer facade
  -> NativeTrainingEngine for dependency-light reference execution
  -> LightningTrainingEngine adapter for Lightning-controlled execution
  -> Future JaxTrainingEngine or other engines for different backend paradigms
```

This avoids two bad outcomes:

- coupling RemotePhys core to Lightning's object model, callback system,
  checkpoint format, and logging stack;
- rebuilding Lightning-sized functionality in the native trainer before the
  library actually needs it.

The stable contract remains:

```text
Batch-like input + LoopContext -> Learner.step -> StepOutput -> TrainingResult
```

The engine decides how control reaches that learner step and who owns the
mechanics around it.

| Layer | Stable responsibility | Example native owner | Example delegated owner |
| --- | --- | --- | --- |
| `Learner` | Scientific step semantics. | `SupervisedLearner`. | Same `SupervisedLearner` called by adapter hooks. |
| `StepOutput` | Objective, predictions, metrics, diagnostics, metadata, provenance. | Returned to native trainer. | Returned to Lightning/JAX adapter, then logged or summarized. |
| `Trainer` | User-facing RemotePhys training facade and result normalization. | Delegates to native engine by default. | Delegates to an external engine adapter. |
| `TrainingEngine` | Actual loop control. | Native loop over `Iterable[Batch]`. | Lightning `Trainer`, future JAX loop, or downstream runtime. |
| Backend mechanics | Device, backward, optimizer, scheduler, precision, distributed behavior. | Native descriptors/adapters. | External engine configuration. |
| Observability | RemotePhys event/profile vocabulary and `TrainingResult` summaries. | Native event/profile emission. | Adapter maps external hooks/logs/profiles back to RemotePhys records. |

A provisional engine protocol can be kept narrow:

```python
class TrainingEngine(Protocol):
    def fit(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def validate(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def test(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...

    def predict(self, plan: TrainingPlan, learner: Learner) -> TrainingResult:
        ...
```

The public `Trainer` can stay as the RemotePhys entrypoint:

```python
trainer = Trainer(engine=NativeTrainingEngine())
result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

The same facade can delegate control to an external engine:

```python
lightning_engine = LightningTrainingEngine(
    lightning_trainer=lightning_trainer,
    module_factory=RemotePhysLightningModule,
    trainable_module=network,
)

trainer = Trainer(engine=lightning_engine)

result = trainer.run(
    TrainingPlan(
        train_batches=train_loader,
        validate_batches=validate_loader,
        metadata={"engine": "lightning"},
    ),
    learner=learner,
)
```

In that delegated path, `Trainer.run(...)` is not looping over batches itself.
It asks the selected engine to run. The Lightning engine creates the
`RemotePhysLightningModule`, calls Lightning's `Trainer.fit(...)`,
collects logged values, checkpoint metadata, callback state summaries, profiler
summaries, and adapter-emitted RemotePhys events, then normalizes that into a
`TrainingResult`.

`TrainingPlan` should not become the place where Lightning or JAX configuration
lives. Engine-specific objects such as a Lightning trainer, logger list,
callback list, accelerator policy, precision policy, or future JAX compile
policy belong on the engine or adapter object. The plan may carry assembled
batch iterables or loader objects supplied by the caller, loop limits,
callbacks/sinks that are part of RemotePhys, and primitive metadata/provenance.
It should not construct dataloaders or parse framework configuration.

The design can support three execution modes without changing `Learner`:

| Execution mode | Who owns loop control? | Why use it? | What RemotePhys should provide |
| --- | --- | --- | --- |
| Native engine | RemotePhys native trainer loop. | Lightweight tests, examples, simple dependency-free runs, reference semantics. | `NativeTrainingEngine`, backend descriptors, events/profiles, result summaries. |
| External delegated engine | Lightning, future JAX engine, or downstream runtime. | Mature logging, checkpointing, accelerators, distributed training, precision, callbacks, profiling. | Adapter protocol, context/step/output mapping, result normalization. |
| Hybrid native engine with backend adapters | RemotePhys loop plus caller-supplied backend mechanics. | Users want RemotePhys loop semantics but custom backward/optimizer/device behavior. | Narrow backend descriptors without external framework imports. |

For a future JAX path, the same engine boundary helps avoid baking torch or
Lightning assumptions into the learner/trainer contract. A `JaxTrainingEngine`
may need a functional learner implementation, explicit train state, PRNG keys,
and `value_and_grad`-style mechanics. That should be an engine/adapter concern
or a later functional learner extension, not a reason for Stage 12 to make the
native trainer a universal backend framework.

Stage 12 should therefore define the engine boundary and native reference
engine, plus fake external-engine pressure tests. A real Lightning engine can
live behind an optional adapter module or later implementation phase; core
imports must remain Lightning-free.

The main Stage 12 design rule is:

```text
RemotePhys defines the learning contract and result vocabulary.
The selected engine owns loop control and backend mechanics.
Adapters translate engine-specific behavior back into RemotePhys records.
```

## Alignment With Torch Lightning

Lightning has its own `Trainer` and loop machinery. In Lightning, users define
step hooks such as `training_step`, `validation_step`, `test_step`, and
`predict_step` on a `LightningModule`, while Lightning's `Trainer` owns device
placement, gradient mode, backward, optimizer stepping, scheduler stepping,
callbacks, logging, checkpointing, precision, and distributed mechanics.

Under the engine architecture, Lightning integration is not an adapter around
the native RemotePhys trainer loop. It is a delegated-control engine that calls
the same learner contract while Lightning owns the loop:

```text
RemotePhys owns: Method -> Learner.step -> StepOutput
Lightning owns:  loop, device, backward, optimizer, scheduler, callbacks, logs
Adapter owns:    translating Lightning hooks into RemotePhys LoopContext calls
```

This means there are two compatible execution paths over the same learner:

```text
Native path:
Batch iterable -> Trainer with NativeTrainingEngine -> Learner.step
               -> StepOutput -> TrainingResult

Lightning path:
DataLoader -> Lightning Trainer -> LightningModule adapter -> Learner.step
           -> StepOutput -> Lightning mechanics -> RemotePhys-compatible summary/events
```

The native `NativeTrainingEngine` is a dependency-light reference loop and
library baseline. Lightning is an optional stronger loop engine for users who
want Lightning's device, distributed, precision, callback, logging, checkpoint,
and dataloader integration behavior.

| RemotePhys concept | Native rphys execution | Lightning-backed execution |
| --- | --- | --- |
| `SupervisedLearner.step` | Called by `NativeTrainingEngine` through the `Trainer` facade. | Called by an optional `LightningModule` adapter from `training_step`, `validation_step`, `test_step`, or `predict_step`. |
| `StepOutput.objective` | Native trainer uses it for backward unless a backend adapter overrides backward. | Adapter returns it as the Lightning loss for automatic optimization, or passes it to Lightning manual optimization. |
| `StepOutput.predictions` | Native trainer keeps it opaque and records summaries only. | Adapter may return/log selected values, but Lightning should not force a new rphys prediction schema. |
| `TrainingEvent` and profile spans | Emitted directly by native trainer. | Optional adapter maps Lightning hooks into the same event/profile records. |
| Backend descriptors | Caller-owned native loop mechanics. | Usually replaced by Lightning `configure_optimizers`, strategy, precision, callbacks, and trainer settings. |
| `TrainingPlan` / `TrainingResult` | Native assembled-object plan and summary result. | Downstream wrapper can translate assembled objects into Lightning module/trainer calls and then summarize back into `TrainingResult`. |

The important design choice is that `SupervisedLearner` should not subclass
`LightningModule`, and `rphys.training.Trainer` should not import or wrap
Lightning's `Trainer` in core. A future optional adapter can sit at the edge.

### Learner Versus Trainable Module

The `Learner` and the Lightning-visible trainable module are different
concepts:

| Concept | Role | Typical owner |
| --- | --- | --- |
| `SupervisedLearner` | Scientific step orchestration: call the method, apply prediction patches locally when needed, evaluate objective/metrics, and return `StepOutput`. | RemotePhys core. |
| `Method` | Prediction semantics over `Sample` or `Batch`; may hold or reference a backend model. | RemotePhys core or downstream method implementation. |
| trainable module / parameter owner | The torch `nn.Module` or parameter-bearing object Lightning must register for device movement, checkpointing, and optimizer construction. | Optional Lightning adapter or downstream integration. |
| `RemotePhysLightningModule` | Bridge from Lightning hooks to `Learner.step`; registers the trainable module for Lightning. | Optional adapter. |

There should not be two learnable models. In a torch-backed method, the same
module object can be referenced by both the method and the Lightning adapter:

```python
network = PulseNet()
method = TorchPulseMethod(model=network)
learner = SupervisedLearner(method=method, objective=objective, metrics=[metric])

lightning_module = RemotePhysLightningModule(
    learner=learner,
    trainable_module=network,  # same object used by method, not a copy
    optimizer_factory=lambda parameters: torch.optim.Adam(parameters, lr=1e-3),
)
```

The learner stores step semantics and may indirectly hold the trainable state
through `method`. The Lightning adapter stores a direct reference to the same
trainable module so Lightning can discover parameters and apply framework
mechanics. This is a registration/reference concern, not a second model or a
second learning abstraction.

The adapter must avoid registering the same parameter-bearing module twice under
different Lightning attributes. For torch-backed methods, prefer one explicit
Lightning registration point such as `self.trainable_module = network`, while
the learner remains a plain RemotePhys object. If a method object is itself a
torch module, register that method object directly instead of separately
registering both the method and a nested module.

If the method itself is a torch module, the adapter can register the method:

```python
method = TorchPulseMethod(...)
learner = SupervisedLearner(method=method, objective=objective)

lightning_module = RemotePhysLightningModule(
    learner=learner,
    trainable_module=method,
    optimizer_factory=make_optimizer,
)
```

If the method is a pure Python object that owns a nested torch module, the
adapter should register that nested module. If a future backend does not expose
a torch module, Lightning integration is adapter-specific and should not force
new fields onto `SupervisedLearner`.

### Lightning Adapter With Automatic Optimization

With Lightning automatic optimization, `training_step` returns the objective
scalar and Lightning owns backward, optimizer stepping, scheduler stepping,
precision, and distributed mechanics. The adapter records or logs selected
values, but it does not reinterpret the scientific result.

```python
class RemotePhysLightningModule(LightningModule):
    def __init__(self, learner, trainable_module, optimizer_factory, event_sink=None):
        super().__init__()
        self.learner = learner
        # Same parameter-bearing object used by the learner's method.
        # Registering it here lets Lightning own framework mechanics.
        self.trainable_module = trainable_module
        self.optimizer_factory = optimizer_factory
        self.event_sink = event_sink

    def training_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.TRAIN,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="train")
        return step.objective

    def validation_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.VALIDATE,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="val")
        return step.metric_values

    def test_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.TEST,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="test")
        return step.metric_values

    def predict_step(self, batch, batch_idx):
        context = LoopContext(
            mode=LoopMode.PREDICT,
            batch_index=batch_idx,
            metadata={"engine": "lightning"},
        )
        step = self.learner.step(batch, context)
        self._record_step_output(step, prefix="predict")
        return step.predictions

    def configure_optimizers(self):
        return self.optimizer_factory(self.trainable_module.parameters())
```

The `trainable_module` exists so Lightning can discover parameters, move state
to devices, checkpoint state, and own optimizer construction. It should be the
same parameter-bearing object used by the learner's method, not an independent
copy. This is adapter surface, not a Stage 12 core import requirement.

### Lightning Adapter With Manual Optimization

If a downstream integration needs Lightning manual optimization, the adapter
can disable automatic optimization and call Lightning's manual optimization
helpers. The learner still does not step optimizers.

```python
class RemotePhysManualLightningModule(LightningModule):
    def __init__(self, learner, trainable_module, optimizer_factory):
        super().__init__()
        self.automatic_optimization = False
        self.learner = learner
        # Same parameter-bearing object used by the learner's method.
        self.trainable_module = trainable_module
        self.optimizer_factory = optimizer_factory

    def training_step(self, batch, batch_idx):
        optimizer = self.optimizers()

        context = LoopContext(
            mode=LoopMode.TRAIN,
            batch_index=batch_idx,
            metadata={"engine": "lightning", "optimization": "manual"},
        )
        step = self.learner.step(batch, context)

        optimizer.zero_grad()
        self.manual_backward(step.objective)
        optimizer.step()

        self._record_step_output(step, prefix="train")
        return step.objective

    def configure_optimizers(self):
        return self.optimizer_factory(self.trainable_module.parameters())
```

Manual optimization is an optional adapter concern. It must not move optimizer
logic into `SupervisedLearner`.

### Batch And Device Transfer

Lightning may receive `rphys.data.Batch` objects from a `DataLoader` or
`LightningDataModule`. If the batch container is not automatically transferable
by Lightning, the adapter can define transfer behavior:

```python
class RemotePhysLightningModule(LightningModule):
    def transfer_batch_to_device(self, batch, device, dataloader_idx):
        if isinstance(batch, Batch):
            return move_remotephys_batch_to_device(batch, device)
        return super().transfer_batch_to_device(batch, device, dataloader_idx)
```

This keeps device transfer outside `SupervisedLearner`. The learner receives a
batch and context; it does not know whether the native trainer, Lightning, or
another engine moved that batch.

### Event And Profile Mapping

A Lightning adapter can map hook boundaries into the same Stage 12 event and
profile vocabulary used by the native trainer:

```python
def training_step(self, batch, batch_idx):
    context = LoopContext(
        mode=LoopMode.TRAIN,
        batch_index=batch_idx,
        metadata={"engine": "lightning"},
    )

    self.event_sink.emit(TrainingEvent(
        source="lightning",
        mode=LoopMode.TRAIN,
        phase="forward",
        position="start",
        batch_index=batch_idx,
    ))

    step = self.learner.step(batch, context)

    self.event_sink.emit(TrainingEvent(
        source="lightning",
        mode=LoopMode.TRAIN,
        phase="objective_loss",
        position="end",
        batch_index=batch_idx,
        metadata={"has_objective": step.objective is not None},
    ))

    return step.objective
```

The adapter can also translate Lightning callback, validation, test, prediction,
logging, checkpoint, and profiler hooks into `TrainingEvent` or profile span
records. Stage 12 core should only define the shared records and vocabulary; it
should not import Lightning to implement concrete hook mapping.

### Delegating Lightning Features Without Duplicating Them

When Lightning is the selected engine, RemotePhys should not reimplement
Lightning's logging, checkpoint, early stopping, profiler, precision, or
distributed behavior. The adapter should expose RemotePhys values to the
Lightning surfaces that already drive those features.

| Feature | Lightning owner | RemotePhys adapter responsibility |
| --- | --- | --- |
| Logging | Lightning `self.log`, `self.log_dict`, and configured loggers. | Convert selected `StepOutput` objective, metrics, and diagnostics into stable log names. |
| Multiple checkpoints | Lightning `ModelCheckpoint` callbacks. | Ensure monitored metrics such as `val/objective` or `val/heart_rate_mae` are logged. |
| Early stopping | Lightning `EarlyStopping` callback. | Log the monitored validation metric with the expected name and cadence. |
| Profiling | Lightning trainer profiler. | Optionally emit RemotePhys event/profile records at scientific boundaries such as method forward and objective computation. |
| Precision/distribution/device | Lightning `Trainer` configuration, strategies, accelerators, and batch transfer hooks. | Keep learner code device-agnostic and register the same trainable module used by the method. |
| Callback lifecycle | Lightning callbacks. | Avoid duplicating loop-control callbacks in RemotePhys core; map important callback lifecycle evidence into RemotePhys events if needed. |

Example adapter logging:

```python
def _record_step_output(self, step, prefix):
    if step.objective is not None:
        self.log(
            f"{prefix}/objective",
            step.objective,
            on_step=prefix == "train",
            on_epoch=True,
            prog_bar=prefix in {"train", "val"},
            logger=True,
        )

    for name, value in step.metric_values.items():
        self.log(
            f"{prefix}/{name}",
            value,
            on_step=prefix == "train",
            on_epoch=True,
            prog_bar=prefix == "val",
            logger=True,
        )
```

Example Lightning-controlled execution:

```python
checkpoint_best_metric = ModelCheckpoint(
    monitor="val/heart_rate_mae",
    mode="min",
    save_top_k=3,
    filename="best-mae-{epoch}",
)

checkpoint_best_objective = ModelCheckpoint(
    monitor="val/objective",
    mode="min",
    save_top_k=2,
    filename="best-objective-{epoch}",
)

early_stopping = EarlyStopping(
    monitor="val/heart_rate_mae",
    mode="min",
    patience=10,
)

lightning_trainer = LightningTrainer(
    accelerator="gpu",
    devices=1,
    precision="16-mixed",
    logger=[tensorboard_logger, csv_logger],
    callbacks=[checkpoint_best_metric, checkpoint_best_objective, early_stopping],
    profiler="simple",
    max_epochs=100,
)

engine = LightningTrainingEngine(
    lightning_trainer=lightning_trainer,
    module_factory=RemotePhysLightningModule,
    trainable_module=network,
)

result = Trainer(engine=engine).run(plan, learner=learner)
```

In this example, RemotePhys does not decide which checkpoints to save, when to
early stop, how to reduce distributed metrics, how to flush logs, or how to run
the profiler. It supplies the scientific values and maps the resulting
Lightning execution evidence back into `TrainingResult`.

### Design Consequences

The Lightning integration confirms the Stage 12 boundary:

- `SupervisedLearner` remains the reusable scientific unit.
- The trainable module remains the backend parameter owner; when Lightning is
  used, the adapter registers the same object that the method uses.
- `Trainer` remains the RemotePhys user-facing facade and result-normalization
  point.
- `NativeTrainingEngine` remains a lightweight reference loop.
- Lightning integration is an optional delegated engine that calls the same
  learner from Lightning hooks.
- Lightning-specific data modules, dataloaders, strategies, precision,
  checkpointing, logging, and distributed behavior stay outside core.
- `StepOutput.objective` is the one value a loop engine may use for backward.
- `StepOutput.predictions`, metrics, diagnostics, metadata, and provenance
  remain learner outputs that the adapter may summarize or log without changing
  their meaning.

## Design Review: Trainer Engine Boundary

Review date: 2026-05-16

Review result: pass with guardrails. The delegated-engine architecture is a
better fit than treating Lightning as a wrapper around the native trainer loop,
because it lets RemotePhys keep its learner/trainer vocabulary while avoiding a
partial reimplementation of mature framework features.

| Finding | Severity | Impact | Resolution |
| --- | --- | --- | --- |
| Older wording made `Trainer` sound like the native loop owner. | high | Conflicts with the new facade/engine design and would make Lightning delegation look bolted on. | Updated the responsibility map and phase shape so `Trainer` is the facade, `TrainingEngine` owns loop control, and `NativeTrainingEngine` is the reference loop. |
| `TrainingPlan` could become an engine-specific config container. | high | Lightning callbacks, loggers, precision, accelerator, and future JAX compile policy could leak into stable RemotePhys records. | Engine-specific configuration belongs on the engine/adapter object; `TrainingPlan` carries assembled inputs, loop limits, RemotePhys callbacks/sinks, and primitive metadata only. |
| A Lightning adapter can accidentally register duplicate trainable modules. | high | Duplicate parameter registration or checkpoint keys would make optimization/checkpoint behavior confusing. | The adapter must register one parameter-bearing object for Lightning, shared with the method; do not separately register both a method and its nested model. |
| `TrainingResult` normalization from Lightning can overreach. | medium | Parsing full checkpoint files, logger internals, or callback-private state would couple RemotePhys to Lightning implementation details. | Record primitive summaries only: status, counts, monitored metric names/values, checkpoint metadata paths or identifiers when available, profiler summaries, callback names/statuses, and RemotePhys events. |
| JAX-style training may not fit object-mutating learner semantics. | medium | A future JAX engine may need explicit state input/output, PRNG keys, and functional gradient transforms. | Keep `TrainingEngine` provisional and avoid hard-coding torch scalar or module assumptions into the learner protocol; record JAX as a revisit trigger for functional learner extensions. |
| Real Lightning support would add optional dependency pressure. | medium | Core import tests and lightweight package policy could regress. | Stage 12 core should define the engine boundary and fake external-engine pressure tests; real Lightning support should live behind an optional adapter module or later optional phase. |
| Native engine feature scope can creep toward Lightning. | medium | RemotePhys could duplicate logging, checkpointing, early stopping, profiler, and distributed features. | Native engine remains reference-grade; advanced loop features are delegated to external engines or narrow backend descriptors only when required. |

Accepted design guardrails:

- `Trainer` is the public RemotePhys facade; it delegates to a selected
  `TrainingEngine`.
- `NativeTrainingEngine` is dependency-light and reference-grade.
- `LightningTrainingEngine` is a delegated-control adapter, not a wrapper around
  the native engine loop.
- `TrainingPlan` is not a framework config schema.
- `TrainingResult` records normalized summaries, not framework-private state.
- `Learner.step` remains the scientific contract used by all engines.
- External engines may own backward, optimizer, scheduler, logging,
  checkpointing, early stopping, profiling, precision, distributed strategy,
  and framework callback lifecycles.
- Core Stage 12 imports remain Lightning-, torch-, JAX-, logger-, and
  dataset-SDK-free unless a later optional adapter phase explicitly changes
  that boundary.

Validation implications:

- Add package/import tests proving core `rphys.training` does not import
  Lightning, torch, JAX, or logger packages.
- Add fake external-engine tests proving `Trainer(engine=fake_engine)` delegates
  control and does not run the native loop.
- Add native-engine tests proving `NativeTrainingEngine` still executes
  fit/validate/test/predict over already-built `Batch` iterables.
- Add result-normalization tests using fake logged metrics, checkpoint metadata,
  callback summaries, profiler summaries, and RemotePhys events.
- Add adapter-contract tests proving a trainable module is registered once and
  shared with the learner's method in Lightning-like examples.
- Add a future-roadmap test or documentation check that JAX/functional training
  pressure remains an explicit revisit trigger, not an implicit Stage 12
  promise.

## End-To-End Example

```python
method = PulseMethod(...)
objective = PulseObjective(...)
metric = HeartRateMAE(...)

learner = SupervisedLearner(
    method=method,
    objective=objective,
    metrics=[metric],
)

trainer = Trainer(engine=NativeTrainingEngine())

result = trainer.fit(
    learner=learner,
    train_batches=train_batches,
    validate_batches=validate_batches,
)
```

Execution connects as:

```text
Batch iterable
  -> Trainer dispatches to NativeTrainingEngine
  -> NativeTrainingEngine creates LoopContext
  -> SupervisedLearner calls Method.predict
  -> SupervisedLearner evaluates Objective and Metrics when available
  -> SupervisedLearner returns StepOutput
  -> NativeTrainingEngine uses only StepOutput.objective for backward
  -> NativeTrainingEngine emits TrainingEvent/ProfileSpan records
  -> Trainer returns TrainingResult
```

## Explicit Non-Goals

Stage 12 should not implement:

- datasource scanning;
- dataloader construction;
- `SampleBuilder`;
- config parsing or workflow runtime behavior;
- raw artifact stores or checkpoint file writers;
- prediction export/materialization;
- evaluation/report generation;
- concrete Lightning, Fabric, torch, JAX, or logger dependencies in core;
- public Stage 11 objective or metric stand-ins while Stage 11 code is absent;
- additional concrete learner families beyond `SupervisedLearner`.

## Stage 11 Sequencing

Stage 11 objective and metric code is a sequencing dependency. Stage 12 may use
test-local fakes to validate learner and trainer behavior before Stage 11 lands,
but it must not publish objective, loss, metric, observation, or metric table
stand-ins from `rphys.learning` or `rphys.training`.

Once Stage 11 public contracts exist, Stage 12 integration tests should switch
from fakes to those real contracts.

## Implementation Phase Shape

The implementation should remain phaseable and reviewable:

1. Establish learning contract foundation: modes, contexts, learner protocol,
   `StepOutput`, validation helpers, and package exports.
2. Add `SupervisedLearner` composition with Stage 10 method output and Stage 11
   guardrails.
3. Add `TrainingPlan`, `TrainingResult`, the `Trainer` facade, and
   `NativeTrainingEngine` mode methods over already-built `Batch` iterables.
4. Add backend descriptors and train-step mechanics for the native engine.
5. Add event, callback, profiling schema, and fake external-engine mapping
   pressure tests.
6. Add experimental `run_train`, docs, examples, engine-boundary notes, and
   final validation.

No implementation code should be written until an implementation plan is
created and approved.

## Change Log

| Round | Update |
| --- | --- |
| 2026-05-16 / design narrative | Documented Stage 12 purpose, proposed interfaces, responsibility map, native trainer flow, Torch Lightning alignment, examples, non-goals, Stage 11 sequencing, and phase shape. No implementation plan or code created. |
| 2026-05-16 / Lightning trainable module clarification | Clarified that `SupervisedLearner` owns step semantics while the Lightning adapter registers the same trainable module or parameter owner used by the method; this avoids duplicating learnable models or moving optimizer mechanics into the learner. |
| 2026-05-16 / delegated engine architecture | Added the `Trainer` facade and `TrainingEngine` boundary so RemotePhys can keep its learner/trainer paradigm while delegating loop control to native, Lightning, or future backend engines without duplicating mature framework features. |
| 2026-05-16 / delegated engine design review | Reviewed the facade/engine architecture, resolved responsibility-map and plan/config risks, added duplicate-registration and result-normalization guardrails, and recorded validation implications. |

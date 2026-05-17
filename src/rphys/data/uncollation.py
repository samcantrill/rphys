"""Explicit uncollation of returned batch fields into samples.

Stage 13 prediction and analysis handoff uses ordinary ``Batch`` values that
may not have been produced by ``collate_samples``. ``UncollatePlan`` records
how each batch field should be split, broadcast, dropped, or rejected before
durable per-sample export. It never guesses tensor axes, temporal alignment,
sample identity, or physiological meaning.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from rphys.errors import CollatePolicyError

from .containers import Batch, Sample
from .fields import FieldValue
from .locators import FieldLocator
from .metadata import MetadataKey

__all__ = [
    "UncollateFieldSpec",
    "UncollatePlan",
    "UncollatePolicy",
    "uncollate_batch_fields",
]

Splitter = Callable[[object, int], Sequence[object]]


class UncollatePolicy(StrEnum):
    """Explicit policy for one returned ``Batch`` field."""

    LIST = "list"
    BATCH_AXIS = "batch_axis"
    BROADCAST = "broadcast"
    DROP = "drop"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass(frozen=True, init=False, slots=True)
class UncollateFieldSpec:
    """Per-field rule for uncollating a returned ``Batch`` field.

    ``LIST`` requires a list or tuple payload with one entry per sample.
    ``BATCH_AXIS`` accepts sequence-like objects with ``len()`` and integer
    indexing. ``BROADCAST`` copies one payload to every sample. ``DROP`` omits
    the field. ``ERROR`` fails if the field is present. ``CUSTOM`` delegates to
    an adapter-owned splitter that must return one value per sample.
    """

    locator: FieldLocator
    policy: UncollatePolicy
    splitter: Splitter | None

    def __init__(
        self,
        locator: FieldLocator | str,
        *,
        policy: UncollatePolicy | str = UncollatePolicy.LIST,
        splitter: Splitter | None = None,
    ) -> None:
        resolved_policy = _coerce_policy(policy)
        if resolved_policy is UncollatePolicy.CUSTOM and splitter is None:
            raise CollatePolicyError(
                "CUSTOM uncollation requires an explicit splitter.",
                locator=str(locator),
            )
        if resolved_policy is not UncollatePolicy.CUSTOM and splitter is not None:
            raise CollatePolicyError(
                "Uncollation splitters are only allowed with CUSTOM policy.",
                locator=str(locator),
                policy=resolved_policy.value,
            )
        if splitter is not None and not callable(splitter):
            raise CollatePolicyError(
                "Uncollation splitter must be callable.",
                locator=str(locator),
                actual=type(splitter).__name__,
            )
        object.__setattr__(self, "locator", _coerce_locator(locator))
        object.__setattr__(self, "policy", resolved_policy)
        object.__setattr__(self, "splitter", splitter)


@dataclass(frozen=True, init=False, slots=True)
class UncollatePlan:
    """Plan for converting one returned ``Batch`` into per-sample outputs."""

    sample_count: int
    field_specs: tuple[UncollateFieldSpec, ...]
    default_policy: UncollatePolicy

    def __init__(
        self,
        sample_count: int,
        field_specs: Sequence[UncollateFieldSpec | FieldLocator | str] = (),
        *,
        default_policy: UncollatePolicy | str = UncollatePolicy.ERROR,
    ) -> None:
        if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count <= 0:
            raise CollatePolicyError(
                "UncollatePlan sample_count must be a positive integer.",
                actual=type(sample_count).__name__,
                sample_count=sample_count,
            )
        specs = _coerce_field_specs(field_specs)
        _validate_unique_locators(specs)
        object.__setattr__(self, "sample_count", sample_count)
        object.__setattr__(self, "field_specs", specs)
        object.__setattr__(self, "default_policy", _coerce_policy(default_policy))

    def spec_for(self, locator: FieldLocator) -> UncollateFieldSpec:
        """Return the explicit or default spec for ``locator``."""

        for spec in self.field_specs:
            if spec.locator == locator:
                return spec
        return UncollateFieldSpec(locator, policy=self.default_policy)


def uncollate_batch_fields(batch: Batch, plan: UncollatePlan) -> tuple[Sample, ...]:
    """Uncollate returned ``Batch`` fields according to ``plan``.

    The output always contains one ``Sample`` per planned sample. Fields are
    split only through explicit policies and metadata is split only when a list
    or tuple value has exactly ``sample_count`` entries; scalar metadata is
    broadcast to each sample.
    """

    if not isinstance(batch, Batch):
        raise CollatePolicyError(
            "uncollate_batch_fields requires a Batch.",
            actual=type(batch).__name__,
        )
    if not isinstance(plan, UncollatePlan):
        raise CollatePolicyError(
            "uncollate_batch_fields requires an UncollatePlan.",
            actual=type(plan).__name__,
        )
    samples = tuple(Sample() for _ in range(plan.sample_count))
    for locator, field_value in batch.field_items():
        spec = plan.spec_for(locator)
        if spec.policy is UncollatePolicy.DROP:
            continue
        if spec.policy is UncollatePolicy.ERROR:
            raise CollatePolicyError(
                "UncollatePlan does not allow this field.",
                locator=str(locator),
                policy=spec.policy.value,
            )
        payloads = _split_payload(spec, field_value.payload, plan.sample_count)
        metadata_by_sample = _split_metadata(
            locator,
            field_value.metadata,
            sample_count=plan.sample_count,
        )
        for index, sample in enumerate(samples):
            sample.set_field(
                locator,
                FieldValue(
                    payloads[index],
                    schema=field_value.schema,
                    metadata=metadata_by_sample[index],
                ),
            )
    return samples


def _split_payload(
    spec: UncollateFieldSpec,
    value: object,
    sample_count: int,
) -> tuple[object, ...]:
    if spec.policy is UncollatePolicy.LIST:
        if not isinstance(value, (list, tuple)):
            raise CollatePolicyError(
                "LIST uncollation requires a list or tuple payload.",
                locator=str(spec.locator),
                actual=type(value).__name__,
            )
        return _validate_length(tuple(value), spec.locator, sample_count)

    if spec.policy is UncollatePolicy.BATCH_AXIS:
        return _split_batch_axis(value, spec.locator, sample_count)

    if spec.policy is UncollatePolicy.BROADCAST:
        return tuple(value for _ in range(sample_count))

    if spec.policy is UncollatePolicy.CUSTOM:
        assert spec.splitter is not None
        try:
            values = spec.splitter(value, sample_count)
        except Exception as exc:
            raise CollatePolicyError(
                "CUSTOM uncollation splitter failed.",
                locator=str(spec.locator),
                error_type=type(exc).__name__,
            ) from exc
        if _is_blocked_batch_axis_value(values):
            raise CollatePolicyError(
                "CUSTOM uncollation splitter must return a sequence of sample values.",
                locator=str(spec.locator),
                actual=type(values).__name__,
            )
        try:
            split_values = tuple(values)
        except TypeError as exc:
            raise CollatePolicyError(
                "CUSTOM uncollation splitter must return an iterable sequence.",
                locator=str(spec.locator),
                actual=type(values).__name__,
            ) from exc
        return _validate_length(split_values, spec.locator, sample_count)

    raise CollatePolicyError(
        "Unsupported uncollation policy for payload splitting.",
        locator=str(spec.locator),
        policy=spec.policy.value,
    )


def _split_batch_axis(
    value: object,
    locator: FieldLocator,
    sample_count: int,
) -> tuple[object, ...]:
    if _is_blocked_batch_axis_value(value):
        raise CollatePolicyError(
            "BATCH_AXIS uncollation requires a sequence-like payload.",
            locator=str(locator),
            actual=type(value).__name__,
        )
    try:
        length = len(value)  # type: ignore[arg-type]
    except TypeError as exc:
        raise CollatePolicyError(
            "BATCH_AXIS uncollation requires len(payload).",
            locator=str(locator),
            actual=type(value).__name__,
        ) from exc
    if length != sample_count:
        raise CollatePolicyError(
            "BATCH_AXIS payload length does not match sample_count.",
            locator=str(locator),
            expected=sample_count,
            actual=length,
        )
    try:
        return tuple(value[index] for index in range(sample_count))  # type: ignore[index]
    except Exception as exc:
        raise CollatePolicyError(
            "BATCH_AXIS uncollation requires integer indexing.",
            locator=str(locator),
            actual=type(value).__name__,
        ) from exc


def _split_metadata(
    locator: FieldLocator,
    metadata: Mapping[MetadataKey, object],
    *,
    sample_count: int,
) -> tuple[dict[MetadataKey, object], ...]:
    per_sample: list[dict[MetadataKey, object]] = [{} for _ in range(sample_count)]
    for key, value in metadata.items():
        if isinstance(value, (list, tuple)):
            if len(value) != sample_count:
                raise CollatePolicyError(
                    "Uncollated metadata sequence length does not match sample_count.",
                    locator=str(locator),
                    metadata_key=str(key),
                    expected=sample_count,
                    actual=len(value),
                )
            for index, item in enumerate(value):
                per_sample[index][key] = item
            continue
        for index in range(sample_count):
            per_sample[index][key] = value
    return tuple(per_sample)


def _validate_length(
    values: tuple[object, ...],
    locator: FieldLocator,
    sample_count: int,
) -> tuple[object, ...]:
    if len(values) != sample_count:
        raise CollatePolicyError(
            "Uncollated payload length does not match sample_count.",
            locator=str(locator),
            expected=sample_count,
            actual=len(values),
        )
    return values


def _coerce_field_specs(
    values: Sequence[UncollateFieldSpec | FieldLocator | str],
) -> tuple[UncollateFieldSpec, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise CollatePolicyError(
            "UncollatePlan field_specs must be a sequence.",
            actual=type(values).__name__,
        )
    specs: list[UncollateFieldSpec] = []
    for value in values:
        if isinstance(value, UncollateFieldSpec):
            specs.append(value)
        else:
            specs.append(UncollateFieldSpec(value))
    return tuple(specs)


def _validate_unique_locators(specs: tuple[UncollateFieldSpec, ...]) -> None:
    seen: set[FieldLocator] = set()
    duplicates: list[str] = []
    for spec in specs:
        if spec.locator in seen:
            duplicates.append(str(spec.locator))
        seen.add(spec.locator)
    if duplicates:
        raise CollatePolicyError(
            "UncollatePlan field_specs must not contain duplicate locators.",
            locators=sorted(duplicates),
        )


def _coerce_policy(value: UncollatePolicy | str) -> UncollatePolicy:
    try:
        return UncollatePolicy(value)
    except ValueError as exc:
        raise CollatePolicyError(
            "Unsupported uncollation policy.",
            policy=str(value),
            supported=[policy.value for policy in UncollatePolicy],
        ) from exc


def _coerce_locator(value: FieldLocator | str) -> FieldLocator:
    if isinstance(value, FieldLocator):
        return value
    if isinstance(value, str):
        return FieldLocator.parse(value)
    raise CollatePolicyError(
        "Uncollation locators must be FieldLocator objects or strings.",
        actual=type(value).__name__,
    )


def _is_blocked_batch_axis_value(value: object) -> bool:
    return isinstance(value, (str, bytes, Mapping))

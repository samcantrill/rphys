"""LIST-only collation for loaded runtime samples.

Stage 2 collation is deliberately narrow: it requires explicit
``CollatePolicy.LIST`` on every collated field and never stacks, pads,
truncates, drops missing fields, dispatches callables, or asks payload objects
to collate themselves.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Sequence

from rphys.errors import CollatePolicyError

from .containers import Batch, FieldContainer, Sample
from .fields import FieldValue
from .locators import FieldLocator
from .metadata import MetadataKey

__all__ = [
    "BatchCollater",
    "CollateContext",
    "CollatePolicy",
    "collate_samples",
    "uncollate_batch",
]

_MISSING = object()
_COLLATION_EVIDENCE_ATTR = "_rphys_list_collation_evidence"


class CollatePolicy(StrEnum):
    """Supported runtime collation policies."""

    LIST = "list"


@dataclass(frozen=True, slots=True)
class CollateContext:
    """Minimal extension context for future collation policies.

    Stage 2 records optional operation/source labels only. The context does not
    override field policies, register custom behavior, or delegate to payloads.
    """

    operation: str | None = None
    source: str | None = None


@dataclass(frozen=True, slots=True)
class BatchCollater:
    """Callable LIST-only collater over ``FieldLocator``-keyed samples.

    The collater is intentionally a thin wrapper around ``collate_samples`` so
    framework adapters can pass an explicit callable without changing collation
    policy, field identity, payload shape, device placement, or model format.
    """

    context: CollateContext | None = None

    def __post_init__(self) -> None:
        if self.context is not None and not isinstance(self.context, CollateContext):
            raise CollatePolicyError(
                "BatchCollater context must be a CollateContext.",
                actual=type(self.context).__name__,
            )

    def __call__(self, samples: Sequence[Sample]) -> Batch:
        return collate_samples(samples, context=self.context)


def collate_samples(
    samples: Sequence[Sample],
    *,
    context: CollateContext | None = None,
) -> Batch:
    """Collate homogeneous samples into a ``Batch`` using LIST policy only."""

    if context is not None and not isinstance(context, CollateContext):
        raise CollatePolicyError(
            "Collate context must be a CollateContext.",
            actual=type(context).__name__,
        )

    sample_tuple = tuple(samples)
    if not sample_tuple:
        raise CollatePolicyError("Cannot collate an empty sample sequence.")

    field_maps = tuple(_field_map(sample) for sample in sample_tuple)
    expected_locators = set(field_maps[0])
    if not expected_locators:
        raise CollatePolicyError("Cannot collate samples with no fields.")

    for index, field_map in enumerate(field_maps[1:], start=1):
        locators = set(field_map)
        if locators != expected_locators:
            raise CollatePolicyError(
                "Samples must have identical field sets for LIST collation.",
                sample_index=index,
                missing=sorted(str(locator) for locator in expected_locators - locators),
                extra=sorted(str(locator) for locator in locators - expected_locators),
            )

    batch = Batch()
    evidence_by_locator: dict[FieldLocator, _FieldCollationEvidence] = {}
    for locator in sorted(expected_locators, key=str):
        field_values = tuple(field_map[locator] for field_map in field_maps)
        _validate_list_collation(locator, field_values)
        payloads = [field_value.payload for field_value in field_values]
        metadata = _MissingAwareMetadata.collect(field_values)
        batch.set_field(
            locator,
            FieldValue(
                payloads,
                schema=field_values[0].schema,
                metadata=metadata.render(),
                collate_policy=CollatePolicy.LIST,
            ),
        )
        evidence_by_locator[locator] = _FieldCollationEvidence(
            sample_count=len(sample_tuple),
            metadata_presence=metadata.presence(),
        )

    _set_collation_evidence(
        batch,
        _BatchCollationEvidence(
            sample_count=len(sample_tuple),
            fields=evidence_by_locator,
        ),
    )
    return batch


def uncollate_batch(batch: Batch) -> tuple[Sample, ...]:
    """Reconstruct samples from a default LIST-collated ``Batch``.

    Only batches produced by ``collate_samples`` or ``BatchCollater`` carry the
    private evidence needed to distinguish absent metadata from explicit
    ``None`` values. The returned tuple is the stable public shape; callers that
    need mutable collection operations can convert it to a list explicitly.

    Non-LIST fields, edited payload lengths, metadata alignment mismatches,
    unsupported batch-level scalar metadata, and batches without LIST collation
    evidence fail loudly rather than inferring sample structure.
    """

    if not isinstance(batch, Batch):
        raise CollatePolicyError(
            "uncollate_batch requires a Batch produced by LIST collation.",
            actual=type(batch).__name__,
        )

    evidence = _get_collation_evidence(batch)
    if evidence is None:
        raise CollatePolicyError(
            "Batch cannot be uncollated without LIST collation evidence."
        )

    field_items = batch.field_items()
    if not field_items:
        raise CollatePolicyError("Cannot uncollate a batch with no fields.")

    sample_count = evidence.sample_count
    if sample_count <= 0:
        raise CollatePolicyError(
            "LIST collation evidence has an invalid sample count.",
            sample_count=sample_count,
        )

    locators = tuple(locator for locator, _ in field_items)
    evidence_locators = set(evidence.fields)
    if set(locators) != evidence_locators:
        raise CollatePolicyError(
            "Batch fields do not match LIST collation evidence.",
            missing=sorted(str(locator) for locator in evidence_locators - set(locators)),
            extra=sorted(str(locator) for locator in set(locators) - evidence_locators),
        )

    samples = tuple(Sample() for _ in range(sample_count))
    for locator, field_value in field_items:
        field_evidence = evidence.fields[locator]
        _validate_uncollatable_field(
            locator,
            field_value,
            sample_count=sample_count,
            evidence=field_evidence,
        )
        payloads = field_value.payload
        metadata_by_sample = _uncollated_metadata(
            locator,
            field_value,
            sample_count=sample_count,
            evidence=field_evidence,
        )
        for index, sample in enumerate(samples):
            sample.set_field(
                locator,
                FieldValue(
                    payloads[index],
                    schema=field_value.schema,
                    metadata=metadata_by_sample[index],
                    collate_policy=CollatePolicy.LIST,
                ),
            )

    return samples


@dataclass(frozen=True, slots=True)
class _MissingAwareMetadata:
    values_by_key: dict[MetadataKey, list[object]]

    @classmethod
    def collect(cls, field_values: Iterable[FieldValue]) -> "_MissingAwareMetadata":
        values = tuple(field_values)
        keys = sorted(
            {key for field_value in values for key in field_value.metadata},
            key=str,
        )
        values_by_key = {
            key: [
                field_value.metadata.get(key, _MISSING)
                for field_value in values
            ]
            for key in keys
        }
        return cls(values_by_key)

    def render(self) -> dict[MetadataKey, list[object | None]]:
        return {
            key: [None if value is _MISSING else value for value in values]
            for key, values in self.values_by_key.items()
        }

    def presence(self) -> dict[MetadataKey, tuple[bool, ...]]:
        return {
            key: tuple(value is not _MISSING for value in values)
            for key, values in self.values_by_key.items()
        }


@dataclass(frozen=True, slots=True)
class _FieldCollationEvidence:
    sample_count: int
    metadata_presence: Mapping[MetadataKey, tuple[bool, ...]]


@dataclass(frozen=True, slots=True)
class _BatchCollationEvidence:
    sample_count: int
    fields: Mapping[FieldLocator, _FieldCollationEvidence]


def _set_collation_evidence(
    batch: Batch,
    evidence: _BatchCollationEvidence,
) -> None:
    setattr(batch, _COLLATION_EVIDENCE_ATTR, evidence)


def _get_collation_evidence(batch: Batch) -> _BatchCollationEvidence | None:
    evidence = getattr(batch, _COLLATION_EVIDENCE_ATTR, None)
    if isinstance(evidence, _BatchCollationEvidence):
        return evidence
    return None


def _field_map(sample: FieldContainer) -> dict[FieldLocator, FieldValue]:
    if not isinstance(sample, FieldContainer):
        raise CollatePolicyError(
            "collate_samples requires Sample-like field containers.",
            actual=type(sample).__name__,
        )
    field_items = getattr(sample, "field_items", None)
    if field_items is None or not callable(field_items):
        raise CollatePolicyError(
            "collate_samples requires Sample-like field containers.",
            actual=type(sample).__name__,
        )
    items = field_items()
    return dict(items)


def _validate_list_collation(
    locator: FieldLocator,
    field_values: tuple[FieldValue, ...],
) -> None:
    schema = field_values[0].schema
    for index, field_value in enumerate(field_values):
        if field_value.schema != schema:
            raise CollatePolicyError(
                "LIST collation requires matching field schemas.",
                locator=str(locator),
                sample_index=index,
                expected=str(schema) if schema is not None else None,
                actual=str(field_value.schema) if field_value.schema is not None else None,
            )

        try:
            policy = _coerce_policy(field_value.collate_policy)
        except CollatePolicyError as exc:
            raise CollatePolicyError(
                "Unsupported collation policy.",
                locator=str(locator),
                sample_index=index,
                policy=str(field_value.collate_policy),
                supported=[CollatePolicy.LIST.value],
            ) from exc
        if policy is None:
            raise CollatePolicyError(
                "LIST collation requires an explicit field policy.",
                locator=str(locator),
                sample_index=index,
            )
        if policy is not CollatePolicy.LIST:
            raise CollatePolicyError(
                "Unsupported collation policy.",
                locator=str(locator),
                sample_index=index,
                policy=str(field_value.collate_policy),
                supported=[CollatePolicy.LIST.value],
            )


def _validate_uncollatable_field(
    locator: FieldLocator,
    field_value: FieldValue,
    *,
    sample_count: int,
    evidence: _FieldCollationEvidence,
) -> None:
    if evidence.sample_count != sample_count:
        raise CollatePolicyError(
            "Field LIST collation evidence has a mismatched sample count.",
            locator=str(locator),
            expected=sample_count,
            actual=evidence.sample_count,
        )

    try:
        policy = _coerce_policy(field_value.collate_policy)
    except CollatePolicyError as exc:
        raise CollatePolicyError(
            "Cannot uncollate a field with an unsupported collation policy.",
            locator=str(locator),
            policy=str(field_value.collate_policy),
            supported=[CollatePolicy.LIST.value],
        ) from exc
    if policy is not CollatePolicy.LIST:
        raise CollatePolicyError(
            "Cannot uncollate a non-LIST field.",
            locator=str(locator),
            policy=str(field_value.collate_policy),
            supported=[CollatePolicy.LIST.value],
        )

    if not isinstance(field_value.payload, list):
        raise CollatePolicyError(
            "LIST uncollation requires list payloads produced by LIST collation.",
            locator=str(locator),
            actual=type(field_value.payload).__name__,
        )
    if len(field_value.payload) != sample_count:
        raise CollatePolicyError(
            "LIST payload length does not match collation evidence.",
            locator=str(locator),
            expected=sample_count,
            actual=len(field_value.payload),
        )


def _uncollated_metadata(
    locator: FieldLocator,
    field_value: FieldValue,
    *,
    sample_count: int,
    evidence: _FieldCollationEvidence,
) -> tuple[dict[MetadataKey, object], ...]:
    evidence_keys = set(evidence.metadata_presence)
    metadata_keys = set(field_value.metadata)
    if metadata_keys != evidence_keys:
        raise CollatePolicyError(
            "Field metadata keys do not match LIST collation evidence.",
            locator=str(locator),
            missing=sorted(str(key) for key in evidence_keys - metadata_keys),
            extra=sorted(str(key) for key in metadata_keys - evidence_keys),
        )

    metadata_by_sample: list[dict[MetadataKey, object]] = [
        {} for _ in range(sample_count)
    ]
    for key, values in field_value.metadata.items():
        if not isinstance(values, list):
            raise CollatePolicyError(
                "Cannot uncollate batch-level scalar metadata.",
                locator=str(locator),
                metadata_key=str(key),
                actual=type(values).__name__,
            )
        if len(values) != sample_count:
            raise CollatePolicyError(
                "LIST metadata length does not match collation evidence.",
                locator=str(locator),
                metadata_key=str(key),
                expected=sample_count,
                actual=len(values),
            )

        presence = evidence.metadata_presence[key]
        if len(presence) != sample_count:
            raise CollatePolicyError(
                "Metadata presence evidence length does not match sample count.",
                locator=str(locator),
                metadata_key=str(key),
                expected=sample_count,
                actual=len(presence),
            )
        for index, present in enumerate(presence):
            if present:
                metadata_by_sample[index][key] = values[index]

    return tuple(metadata_by_sample)


def _coerce_policy(value: object | None) -> CollatePolicy | None:
    if value is None:
        return None
    if isinstance(value, CollatePolicy):
        return value
    try:
        return CollatePolicy(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise CollatePolicyError(
            "Unsupported collation policy.",
            policy=str(value),
            supported=[CollatePolicy.LIST.value],
        ) from None

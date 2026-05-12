"""LIST-only collation for loaded runtime samples.

Stage 2 collation is deliberately narrow: it requires explicit
``CollatePolicy.LIST`` on every collated field and never stacks, pads,
truncates, drops missing fields, dispatches callables, or asks payload objects
to collate themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Sequence

from rphys.errors import CollatePolicyError

from .containers import Batch, Sample
from .fields import FieldValue
from .locators import FieldLocator
from .metadata import MetadataKey

__all__ = ["CollateContext", "CollatePolicy", "collate_samples"]

_MISSING = object()


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
    for locator in sorted(expected_locators, key=str):
        field_values = tuple(field_map[locator] for field_map in field_maps)
        _validate_list_collation(locator, field_values)
        batch.set_field(
            locator,
            FieldValue(
                [field_value.payload for field_value in field_values],
                schema=field_values[0].schema,
                metadata=_MissingAwareMetadata.collect(field_values).render(),
                collate_policy=CollatePolicy.LIST,
            ),
        )

    return batch


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


def _field_map(sample: Sample) -> dict[FieldLocator, FieldValue]:
    items = getattr(sample, "_field_items", None)
    if items is None or not callable(items):
        raise CollatePolicyError(
            "collate_samples requires Sample-like field containers.",
            actual=type(sample).__name__,
        )
    return dict(items())


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

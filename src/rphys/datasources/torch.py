"""Optional torch data-loading adapters over ``SampleSource``.

The module is importable without torch installed. Torch is imported only when
``TorchDataLoaderBuilder.build`` constructs a real ``torch.utils.data.DataLoader``.
Dataset wrappers return ``FieldLocator``-keyed ``Sample`` objects and never
format model tuples, move devices, scan datasources, build indexes, export
payloads, or perform cache/prepared-data behavior.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from rphys.data.collation import BatchCollater
from rphys.data.containers import Batch, Sample
from rphys.data.locators import FieldLocator
from rphys.data.sample_builders import SampleBuilder
from rphys.datasources.indexes import CompositeDataSourceIndex, DataSourceIndex
from rphys.datasources.sources import (
    IndexSampleSource,
    SampleRequest,
    SampleSource,
    WorkerContextFactory,
)
from rphys.errors import (
    FieldTypeError,
    RemotePhysDataSourceError,
    RemotePhysDependencyError,
)

__all__ = [
    "TorchSampleSourceDataset",
    "TorchIndexSampleDataset",
    "TorchDataLoaderPlan",
    "TorchDataLoaderBuilder",
]

type _SampleRequestLike = (
    SampleRequest | FieldLocator | str | Iterable[FieldLocator | str] | None
)


class TorchSampleSourceDataset:
    """Map-style dataset wrapper that delegates item access to ``SampleSource``."""

    __slots__ = ("_source", "_request")

    def __init__(
        self,
        source: SampleSource,
        *,
        request: _SampleRequestLike = None,
    ) -> None:
        if not isinstance(source, SampleSource):
            raise RemotePhysDataSourceError(
                "TorchSampleSourceDataset source must be a SampleSource.",
                field="source",
                expected="SampleSource",
                actual=type(source).__name__,
            )
        self._source = source
        self._request = request

    @property
    def source(self) -> SampleSource:
        """Wrapped source, exposed for inspection without mutation."""

        return self._source

    @property
    def request(self) -> _SampleRequestLike:
        """Configured sample request forwarded to ``SampleSource`` item access."""

        return self._request

    def __len__(self) -> int:
        return len(self._source)

    def __getitem__(self, position: int) -> Sample:
        if self._request is None:
            return self._source[position]
        return self._source.sample_at(position, request=self._request)


class TorchIndexSampleDataset(TorchSampleSourceDataset):
    """Convenience dataset over an existing datasource index and sample builder."""

    __slots__ = ("_index_source",)

    def __init__(
        self,
        index: DataSourceIndex | CompositeDataSourceIndex,
        builder: SampleBuilder,
        *,
        request: _SampleRequestLike = None,
        context_factory: WorkerContextFactory | None = None,
    ) -> None:
        source = IndexSampleSource(
            index,
            builder,
            context_factory=context_factory,
        )
        self._index_source = source
        super().__init__(source, request=request)

    @property
    def index_source(self) -> IndexSampleSource:
        """Underlying Phase 1 source wrapper."""

        return self._index_source


@dataclass(frozen=True, init=False, slots=True)
class TorchDataLoaderPlan:
    """Data-only torch ``DataLoader`` settings owned by the loader boundary."""

    batch_size: int | None
    shuffle: bool
    drop_last: bool
    num_workers: int

    def __init__(
        self,
        *,
        batch_size: int | None = 1,
        shuffle: bool = False,
        drop_last: bool = False,
        num_workers: int = 0,
    ) -> None:
        object.__setattr__(
            self,
            "batch_size",
            _coerce_optional_positive_int(
                batch_size,
                owner="TorchDataLoaderPlan",
                field="batch_size",
            ),
        )
        object.__setattr__(
            self,
            "shuffle",
            _coerce_bool(shuffle, owner="TorchDataLoaderPlan", field="shuffle"),
        )
        object.__setattr__(
            self,
            "drop_last",
            _coerce_bool(drop_last, owner="TorchDataLoaderPlan", field="drop_last"),
        )
        object.__setattr__(
            self,
            "num_workers",
            _coerce_non_negative_int(
                num_workers,
                owner="TorchDataLoaderPlan",
                field="num_workers",
            ),
        )

    def to_kwargs(self) -> dict[str, object]:
        """Return primitive ``torch.utils.data.DataLoader`` keyword arguments."""

        return {
            "batch_size": self.batch_size,
            "shuffle": self.shuffle,
            "drop_last": self.drop_last,
            "num_workers": self.num_workers,
        }


TorchDataLoaderPlan.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class TorchDataLoaderBuilder:
    """Construct torch ``DataLoader`` instances through a lazy torch import."""

    plan: TorchDataLoaderPlan
    collate_fn: Callable[[object], Batch]

    def __init__(
        self,
        *,
        plan: TorchDataLoaderPlan | None = None,
        collate_fn: Callable[[object], Batch] | None = None,
    ) -> None:
        if plan is None:
            plan = TorchDataLoaderPlan()
        if not isinstance(plan, TorchDataLoaderPlan):
            raise FieldTypeError(
                "TorchDataLoaderBuilder plan must be a TorchDataLoaderPlan.",
                field="plan",
                expected="TorchDataLoaderPlan",
                actual=type(plan).__name__,
            )
        if collate_fn is None:
            collate_fn = BatchCollater()
        if not callable(collate_fn):
            raise FieldTypeError(
                "TorchDataLoaderBuilder collate_fn must be callable.",
                field="collate_fn",
                actual=type(collate_fn).__name__,
            )
        object.__setattr__(self, "plan", plan)
        object.__setattr__(self, "collate_fn", collate_fn)

    def build(self, dataset: object) -> object:
        """Build a torch ``DataLoader`` with explicit rphys collation."""

        dataloader_type = _load_torch_dataloader()
        return dataloader_type(
            dataset,
            collate_fn=self.collate_fn,
            **self.plan.to_kwargs(),
        )


TorchDataLoaderBuilder.__hash__ = None  # type: ignore[assignment]


def _load_torch_dataloader() -> type:
    try:
        torch_data = importlib.import_module("torch.utils.data")
    except ImportError as exc:
        raise RemotePhysDependencyError(
            "torch is required to build a torch DataLoader.",
            dependency="torch",
            module="torch.utils.data",
            operation="TorchDataLoaderBuilder.build",
        ) from exc

    dataloader_type = getattr(torch_data, "DataLoader", None)
    if not isinstance(dataloader_type, type):
        raise RemotePhysDependencyError(
            "torch.utils.data.DataLoader is unavailable or invalid.",
            dependency="torch",
            module="torch.utils.data",
            operation="TorchDataLoaderBuilder.build",
            actual=type(dataloader_type).__name__,
        )
    return dataloader_type


def _coerce_bool(value: object, *, owner: str, field: str) -> bool:
    if type(value) is not bool:
        raise FieldTypeError(
            f"{owner} {field} must be a bool.",
            owner=owner,
            field=field,
            expected="bool",
            actual=type(value).__name__,
        )
    return value


def _coerce_non_negative_int(value: object, *, owner: str, field: str) -> int:
    if type(value) is not int:
        raise FieldTypeError(
            f"{owner} {field} must be a non-boolean integer.",
            owner=owner,
            field=field,
            expected="non-negative int",
            actual=type(value).__name__,
        )
    if value < 0:
        raise FieldTypeError(
            f"{owner} {field} must be non-negative.",
            owner=owner,
            field=field,
            actual=value,
        )
    return value


def _coerce_optional_positive_int(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> int | None:
    if value is None:
        return None
    coerced = _coerce_non_negative_int(value, owner=owner, field=field)
    if coerced == 0:
        raise FieldTypeError(
            f"{owner} {field} must be positive when provided.",
            owner=owner,
            field=field,
            actual=coerced,
        )
    return coerced

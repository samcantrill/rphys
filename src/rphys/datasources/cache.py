"""Deterministic cache records and local store for sample sources.

Stage 9 cache behavior is metadata-first. It records deterministic key,
manifest, lookup, and write evidence without pickling ``Sample`` objects or
claiming generic payload persistence. ``CachedSampleSource`` returns cache hits
only through an explicit caller-provided value loader.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from rphys.data.containers import Sample
from rphys.data.locators import FieldLocator
from rphys.datasources.sources import (
    SampleRequest,
    SampleRequestLike,
    SampleRuntimeContext,
    SampleSource,
)
from rphys.errors import FieldTypeError, RemotePhysDataSourceError
from rphys.io._primitives import FrozenPrimitive, freeze_primitive

__all__ = [
    "CacheKey",
    "CachePolicy",
    "CacheContext",
    "CacheEntry",
    "CacheManifest",
    "CacheLookupResult",
    "CacheWriteResult",
    "CacheStore",
    "LocalCacheStore",
    "CachedSampleSource",
]

_CACHE_MANIFEST_SCHEMA_VERSION = 1


@dataclass(frozen=True, init=False, slots=True)
class CacheContext:
    """Primitive cache invalidation and operation evidence."""

    operation_fingerprint: FrozenPrimitive | None
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    fingerprint: str

    def __init__(
        self,
        *,
        operation_fingerprint: object | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "operation_fingerprint",
            _coerce_optional_primitive(
                operation_fingerprint,
                owner="CacheContext",
                field="operation_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "invalidation",
            MappingProxyType(
                _coerce_primitive_mapping(
                    invalidation,
                    owner="CacheContext",
                    field="invalidation",
                )
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    metadata,
                    owner="CacheContext",
                    field="metadata",
                )
            ),
        )
        object.__setattr__(
            self,
            "fingerprint",
            _sha256(
                {
                    "operation_fingerprint": self.operation_fingerprint,
                    "invalidation": dict(self.invalidation),
                    "metadata": dict(self.metadata),
                }
            ),
        )


CacheContext.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CacheKey:
    """Deterministic cache key for one sample request/context pair."""

    request_fingerprint: str
    runtime_context_fingerprint: str
    cache_context_fingerprint: str | None
    operation_fingerprint: FrozenPrimitive | None
    invalidation: Mapping[str, FrozenPrimitive]
    digest: str

    def __init__(
        self,
        *,
        request_fingerprint: str,
        runtime_context_fingerprint: str,
        cache_context_fingerprint: str | None = None,
        operation_fingerprint: object | None = None,
        invalidation: Mapping[str, object] | None = None,
        digest: str | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "request_fingerprint",
            _coerce_fingerprint(
                request_fingerprint,
                owner="CacheKey",
                field="request_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "runtime_context_fingerprint",
            _coerce_fingerprint(
                runtime_context_fingerprint,
                owner="CacheKey",
                field="runtime_context_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "cache_context_fingerprint",
            (
                None
                if cache_context_fingerprint is None
                else _coerce_fingerprint(
                    cache_context_fingerprint,
                    owner="CacheKey",
                    field="cache_context_fingerprint",
                )
            ),
        )
        object.__setattr__(
            self,
            "operation_fingerprint",
            _coerce_optional_primitive(
                operation_fingerprint,
                owner="CacheKey",
                field="operation_fingerprint",
            ),
        )
        object.__setattr__(
            self,
            "invalidation",
            MappingProxyType(
                _coerce_primitive_mapping(
                    invalidation,
                    owner="CacheKey",
                    field="invalidation",
                )
            ),
        )
        stable = self._stable_payload()
        resolved_digest = digest or _sha256(stable)
        if resolved_digest != _sha256(stable):
            raise RemotePhysDataSourceError(
                "CacheKey digest mismatch.",
                field="digest",
                expected=_sha256(stable),
                actual=resolved_digest,
            )
        object.__setattr__(self, "digest", resolved_digest)

    @classmethod
    def for_sample(
        cls,
        request: SampleRequest,
        context: SampleRuntimeContext,
        *,
        cache_context: CacheContext | None = None,
    ) -> "CacheKey":
        if not isinstance(request, SampleRequest):
            raise FieldTypeError(
                "CacheKey request must be a SampleRequest.",
                field="request",
                actual=type(request).__name__,
            )
        if not isinstance(context, SampleRuntimeContext):
            raise FieldTypeError(
                "CacheKey context must be a SampleRuntimeContext.",
                field="context",
                actual=type(context).__name__,
            )
        if cache_context is not None and not isinstance(cache_context, CacheContext):
            raise FieldTypeError(
                "CacheKey cache_context must be a CacheContext.",
                field="cache_context",
                actual=type(cache_context).__name__,
            )
        if context.request_fingerprint != request.fingerprint:
            raise RemotePhysDataSourceError(
                "CacheKey context request fingerprint does not match the sample request.",
                field="context",
                expected=request.fingerprint,
                actual=context.request_fingerprint,
            )
        return cls(
            request_fingerprint=request.fingerprint,
            runtime_context_fingerprint=context.fingerprint,
            cache_context_fingerprint=(
                None if cache_context is None else cache_context.fingerprint
            ),
            operation_fingerprint=(
                None if cache_context is None else cache_context.operation_fingerprint
            ),
            invalidation={} if cache_context is None else cache_context.invalidation,
        )

    def to_dict(self) -> dict[str, object]:
        return {**self._stable_payload(), "digest": self.digest}

    @classmethod
    def from_dict(cls, value: object) -> "CacheKey":
        data = _require_mapping(value, field="key")
        _require_keys(
            data,
            {
                "request_fingerprint",
                "runtime_context_fingerprint",
                "cache_context_fingerprint",
                "operation_fingerprint",
                "invalidation",
                "digest",
            },
            descriptor="CacheKey",
        )
        return cls(
            request_fingerprint=data["request_fingerprint"],  # type: ignore[arg-type]
            runtime_context_fingerprint=data["runtime_context_fingerprint"],  # type: ignore[arg-type]
            cache_context_fingerprint=data["cache_context_fingerprint"],  # type: ignore[arg-type]
            operation_fingerprint=data["operation_fingerprint"],
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            digest=data["digest"],  # type: ignore[arg-type]
        )

    def _stable_payload(self) -> dict[str, object]:
        return {
            "request_fingerprint": self.request_fingerprint,
            "runtime_context_fingerprint": self.runtime_context_fingerprint,
            "cache_context_fingerprint": self.cache_context_fingerprint,
            "operation_fingerprint": self.operation_fingerprint,
            "invalidation": dict(self.invalidation),
        }


CacheKey.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CachePolicy:
    """Read/write policy for ``CachedSampleSource``."""

    read: bool
    write: bool

    def __init__(self, *, read: bool = True, write: bool = True) -> None:
        object.__setattr__(
            self,
            "read",
            _coerce_bool(read, owner="CachePolicy", field="read"),
        )
        object.__setattr__(
            self,
            "write",
            _coerce_bool(write, owner="CachePolicy", field="write"),
        )


@dataclass(frozen=True, init=False, slots=True)
class CacheEntry:
    """One manifest entry for a deterministic cache key."""

    key: CacheKey
    status: str
    field_locators: tuple[FieldLocator, ...]
    value_strategy: str
    value_token: FrozenPrimitive | None
    invalidation: Mapping[str, FrozenPrimitive]
    metadata: Mapping[str, FrozenPrimitive]
    checksum: str

    def __init__(
        self,
        *,
        key: CacheKey,
        status: str = "complete",
        field_locators: Sequence[FieldLocator | str] = (),
        value_strategy: str = "explicit",
        value_token: object | None = None,
        invalidation: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        checksum: str | None = None,
    ) -> None:
        if not isinstance(key, CacheKey):
            raise FieldTypeError(
                "CacheEntry key must be a CacheKey.",
                field="key",
                actual=type(key).__name__,
            )
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "status", _coerce_status(status))
        object.__setattr__(self, "field_locators", _coerce_locators(field_locators))
        object.__setattr__(
            self,
            "value_strategy",
            _coerce_non_empty_string(
                value_strategy,
                owner="CacheEntry",
                field="value_strategy",
            ),
        )
        object.__setattr__(
            self,
            "value_token",
            _coerce_optional_primitive(
                value_token,
                owner="CacheEntry",
                field="value_token",
            ),
        )
        resolved_invalidation = _coerce_primitive_mapping(
            dict(key.invalidation) if invalidation is None else invalidation,
            owner="CacheEntry",
            field="invalidation",
        )
        if resolved_invalidation != dict(key.invalidation):
            raise RemotePhysDataSourceError(
                "CacheEntry invalidation must match its CacheKey invalidation evidence.",
                field="invalidation",
                expected=dict(key.invalidation),
                actual=resolved_invalidation,
            )
        object.__setattr__(
            self,
            "invalidation",
            MappingProxyType(resolved_invalidation),
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                _coerce_primitive_mapping(
                    metadata,
                    owner="CacheEntry",
                    field="metadata",
                )
            ),
        )
        stable = self._stable_payload()
        resolved_checksum = checksum or _sha256(stable)
        if resolved_checksum != _sha256(stable):
            raise RemotePhysDataSourceError(
                "CacheEntry checksum mismatch.",
                field="checksum",
                expected=_sha256(stable),
                actual=resolved_checksum,
            )
        object.__setattr__(self, "checksum", resolved_checksum)

    @property
    def complete(self) -> bool:
        return self.status == "complete"

    def to_dict(self) -> dict[str, object]:
        return {**self._stable_payload(), "checksum": self.checksum}

    @classmethod
    def from_dict(cls, value: object) -> "CacheEntry":
        data = _require_mapping(value, field="entry")
        _require_keys(
            data,
            {
                "key",
                "status",
                "field_locators",
                "value_strategy",
                "value_token",
                "invalidation",
                "metadata",
                "checksum",
            },
            descriptor="CacheEntry",
        )
        return cls(
            key=CacheKey.from_dict(data["key"]),
            status=data["status"],  # type: ignore[arg-type]
            field_locators=data["field_locators"],  # type: ignore[arg-type]
            value_strategy=data["value_strategy"],  # type: ignore[arg-type]
            value_token=data["value_token"],
            invalidation=data["invalidation"],  # type: ignore[arg-type]
            metadata=data["metadata"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
        )

    def _stable_payload(self) -> dict[str, object]:
        return {
            "key": self.key.to_dict(),
            "status": self.status,
            "field_locators": [str(locator) for locator in self.field_locators],
            "value_strategy": self.value_strategy,
            "value_token": self.value_token,
            "invalidation": dict(self.invalidation),
            "metadata": dict(self.metadata),
        }


CacheEntry.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, init=False, slots=True)
class CacheManifest:
    """Versioned JSON cache manifest envelope."""

    schema_version: int
    entries: tuple[CacheEntry, ...]
    checksum: str

    def __init__(
        self,
        entries: Sequence[CacheEntry],
        *,
        schema_version: int = _CACHE_MANIFEST_SCHEMA_VERSION,
        checksum: str | None = None,
    ) -> None:
        object.__setattr__(
            self,
            "schema_version",
            _coerce_schema_version(schema_version),
        )
        object.__setattr__(self, "entries", _coerce_entries(entries))
        stable = self._stable_payload()
        resolved_checksum = checksum or _sha256(stable)
        if resolved_checksum != _sha256(stable):
            raise RemotePhysDataSourceError(
                "CacheManifest checksum mismatch.",
                field="checksum",
                expected=_sha256(stable),
                actual=resolved_checksum,
            )
        object.__setattr__(self, "checksum", resolved_checksum)

    def to_dict(self) -> dict[str, object]:
        return {**self._stable_payload(), "checksum": self.checksum}

    @classmethod
    def from_dict(cls, value: object) -> "CacheManifest":
        data = _require_mapping(value, field="manifest")
        _require_keys(
            data,
            {"schema_version", "entries", "checksum"},
            descriptor="CacheManifest",
        )
        entries = [
            CacheEntry.from_dict(item)
            for item in _require_sequence(data["entries"], field="entries")
        ]
        return cls(
            entries,
            schema_version=data["schema_version"],  # type: ignore[arg-type]
            checksum=data["checksum"],  # type: ignore[arg-type]
        )

    def dumps(self) -> str:
        return _canonical_json(self.to_dict())

    @classmethod
    def loads(cls, payload: str) -> "CacheManifest":
        return cls.from_dict(json.loads(payload))

    def _stable_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "entries": [entry.to_dict() for entry in self.entries],
        }


CacheManifest.__hash__ = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class CacheLookupResult:
    """Inspectable cache lookup outcome."""

    status: str
    key: CacheKey | None
    entry: CacheEntry | None = None
    reason: str | None = None

    @property
    def hit(self) -> bool:
        return self.status == "hit" and self.entry is not None


@dataclass(frozen=True, slots=True)
class CacheWriteResult:
    """Inspectable cache write outcome."""

    status: str
    key: CacheKey | None
    entry: CacheEntry | None = None
    path: Path | None = None
    reason: str | None = None

    @property
    def written(self) -> bool:
        return self.status == "written"


class CacheStore:
    """Minimal cache store protocol."""

    def lookup(self, key: CacheKey) -> CacheLookupResult:
        raise NotImplementedError

    def write(self, entry: CacheEntry) -> CacheWriteResult:
        raise NotImplementedError


class LocalCacheStore(CacheStore):
    """Local JSON manifest store with temp-write then atomic replace."""

    __slots__ = ("root",)

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: CacheKey) -> Path:
        _require_cache_key(key)
        return self.root / f"{key.digest}.json"

    def lookup(self, key: CacheKey) -> CacheLookupResult:
        _require_cache_key(key)
        path = self.path_for(key)
        if not path.exists():
            return CacheLookupResult("miss", key, reason="missing")
        try:
            manifest = CacheManifest.loads(path.read_text(encoding="utf-8"))
        except (
            FieldTypeError,
            OSError,
            RemotePhysDataSourceError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return CacheLookupResult("corrupt", key, reason=type(exc).__name__)
        if len(manifest.entries) != 1:
            return CacheLookupResult("corrupt", key, reason="entry_count")
        entry = manifest.entries[0]
        if entry.key.digest != key.digest:
            return CacheLookupResult("stale", key, reason="key_mismatch")
        if not entry.complete:
            return CacheLookupResult("incomplete", key, entry=entry, reason=entry.status)
        return CacheLookupResult("hit", key, entry=entry)

    def write(self, entry: CacheEntry) -> CacheWriteResult:
        if not isinstance(entry, CacheEntry):
            raise FieldTypeError(
                "LocalCacheStore entry must be a CacheEntry.",
                field="entry",
                actual=type(entry).__name__,
            )
        path = self.path_for(entry.key)
        manifest = CacheManifest([entry])
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.root,
                prefix=f".{entry.key.digest}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(manifest.dumps())
            temp_path.replace(path)
        except OSError:
            if temp_path is not None:
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass
            raise
        return CacheWriteResult("written", entry.key, entry=entry, path=path)


class CachedSampleSource(SampleSource):
    """SampleSource wrapper with explicit cache hit/load and write strategies."""

    __slots__ = (
        "_source",
        "_store",
        "_policy",
        "_cache_context",
        "_hit_loader",
        "_entry_factory",
        "_context_factory",
        "last_lookup",
        "last_write",
    )

    def __init__(
        self,
        source: SampleSource,
        store: CacheStore,
        *,
        policy: CachePolicy | None = None,
        cache_context: CacheContext | None = None,
        hit_loader: Callable[[CacheEntry], Sample] | None = None,
        entry_factory: Callable[[Sample, CacheKey], CacheEntry] | None = None,
        context_factory: Callable[[int, SampleRequest], SampleRuntimeContext] | None = None,
    ) -> None:
        if not isinstance(source, SampleSource):
            raise RemotePhysDataSourceError(
                "CachedSampleSource source must be a SampleSource.",
                field="source",
                actual=type(source).__name__,
            )
        if not isinstance(store, CacheStore):
            raise RemotePhysDataSourceError(
                "CachedSampleSource store must be a CacheStore.",
                field="store",
                actual=type(store).__name__,
            )
        if policy is None:
            policy = CachePolicy()
        if not isinstance(policy, CachePolicy):
            raise FieldTypeError(
                "CachedSampleSource policy must be a CachePolicy.",
                field="policy",
                actual=type(policy).__name__,
            )
        if cache_context is not None and not isinstance(cache_context, CacheContext):
            raise FieldTypeError(
                "CachedSampleSource cache_context must be a CacheContext.",
                field="cache_context",
                actual=type(cache_context).__name__,
            )
        if hit_loader is not None and not callable(hit_loader):
            raise FieldTypeError(
                "CachedSampleSource hit_loader must be callable.",
                field="hit_loader",
                actual=type(hit_loader).__name__,
            )
        if entry_factory is not None and not callable(entry_factory):
            raise FieldTypeError(
                "CachedSampleSource entry_factory must be callable.",
                field="entry_factory",
                actual=type(entry_factory).__name__,
            )
        if context_factory is not None and not callable(context_factory):
            raise FieldTypeError(
                "CachedSampleSource context_factory must be callable.",
                field="context_factory",
                actual=type(context_factory).__name__,
            )
        self._source = source
        self._store = store
        self._policy = policy
        self._cache_context = cache_context
        self._hit_loader = hit_loader
        self._entry_factory = entry_factory
        self._context_factory = context_factory
        self.last_lookup: CacheLookupResult | None = None
        self.last_write: CacheWriteResult | None = None

    def __len__(self) -> int:
        return len(self._source)

    def sample_at(
        self,
        position: int,
        request: SampleRequestLike = None,
        context: SampleRuntimeContext | None = None,
    ) -> Sample:
        source_position = _coerce_non_negative_int(
            position,
            owner="CachedSampleSource",
            field="position",
        )
        request_object = SampleRequest.coerce(request)
        if context is None:
            context = self._make_context(source_position, request_object)
        else:
            _validate_runtime_context(
                context,
                position=source_position,
                request=request_object,
            )

        if context is None:
            sample = self._source.sample_at(source_position, request=request_object)
            self.last_lookup = CacheLookupResult(
                "miss",
                None,
                reason="missing_context",
            )
            self.last_write = CacheWriteResult(
                "skipped",
                None,
                reason="missing_context",
            )
            return sample

        key = CacheKey.for_sample(
            request_object,
            context,
            cache_context=self._cache_context,
        )
        if self._policy.read:
            lookup = self._store.lookup(key)
            self.last_lookup = lookup
            if lookup.hit and self._hit_loader is not None:
                assert lookup.entry is not None
                loaded = self._hit_loader(lookup.entry)
                if not isinstance(loaded, Sample):
                    raise FieldTypeError(
                        "CachedSampleSource hit_loader must return a Sample.",
                        field="hit_loader",
                        actual=type(loaded).__name__,
                    )
                self.last_write = CacheWriteResult(
                    "skipped",
                    key,
                    entry=lookup.entry,
                    reason="cache_hit",
                )
                return loaded
        else:
            self.last_lookup = CacheLookupResult("disabled", key, reason="read_disabled")

        sample = self._source.sample_at(
            source_position,
            request=request_object,
            context=context,
        )
        return self._write_if_enabled(sample, key)

    def _make_context(
        self,
        position: int,
        request: SampleRequest,
    ) -> SampleRuntimeContext | None:
        if self._context_factory is None:
            return None
        context = self._context_factory(position, request)
        _validate_runtime_context(context, position=position, request=request)
        return context

    def _write_if_enabled(self, sample: Sample, key: CacheKey) -> Sample:
        if self._policy.write and self._entry_factory is not None:
            entry = self._entry_factory(sample, key)
            if not isinstance(entry, CacheEntry):
                raise FieldTypeError(
                    "CachedSampleSource entry_factory must return a CacheEntry.",
                    field="entry_factory",
                    actual=type(entry).__name__,
                )
            if entry.key.digest != key.digest:
                raise RemotePhysDataSourceError(
                    "CachedSampleSource entry_factory returned an entry for a different key.",
                    field="entry_factory",
                    expected=key.digest,
                    actual=entry.key.digest,
                )
            self.last_write = self._store.write(entry)
        else:
            self.last_write = CacheWriteResult("skipped", key, reason="no_entry_factory")
        return sample


def _require_cache_key(key: CacheKey) -> None:
    if not isinstance(key, CacheKey):
        raise FieldTypeError(
            "Cache store key must be a CacheKey.",
            field="key",
            actual=type(key).__name__,
        )


def _validate_runtime_context(
    context: object,
    *,
    position: int,
    request: SampleRequest,
) -> None:
    if not isinstance(context, SampleRuntimeContext):
        raise FieldTypeError(
            "CachedSampleSource context must be a SampleRuntimeContext.",
            field="context",
            actual=type(context).__name__,
        )
    if context.position != position:
        raise RemotePhysDataSourceError(
            "CachedSampleSource context position does not match the requested sample position.",
            field="context",
            expected=position,
            actual=context.position,
        )
    if context.request_fingerprint != request.fingerprint:
        raise RemotePhysDataSourceError(
            "CachedSampleSource context request fingerprint does not match the sample request.",
            field="context",
            expected=request.fingerprint,
            actual=context.request_fingerprint,
        )


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


def _coerce_fingerprint(value: object, *, owner: str, field: str) -> str:
    text = _coerce_non_empty_string(value, owner=owner, field=field)
    if len(text) != 64:
        raise FieldTypeError(
            f"{owner} {field} must be a 64-character fingerprint.",
            owner=owner,
            field=field,
            actual=text,
        )
    return text


def _coerce_non_empty_string(value: object, *, owner: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldTypeError(
            f"{owner} {field} must be a non-empty string.",
            owner=owner,
            field=field,
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


def _coerce_optional_primitive(
    value: object | None,
    *,
    owner: str,
    field: str,
) -> FrozenPrimitive | None:
    if value is None:
        return None
    return freeze_primitive(value, error_type=FieldTypeError, field=f"{owner}.{field}")


def _coerce_primitive_mapping(
    value: Mapping[str, object] | None,
    *,
    owner: str,
    field: str,
) -> dict[str, FrozenPrimitive]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FieldTypeError(
            f"{owner} {field} must be a mapping.",
            owner=owner,
            field=field,
            actual=type(value).__name__,
        )
    output: dict[str, FrozenPrimitive] = {}
    for key, item in value.items():
        output[_coerce_non_empty_string(key, owner=owner, field=f"{field} key")] = (
            freeze_primitive(
                item,
                error_type=FieldTypeError,
                field=f"{owner}.{field}[{key}]",
            )
        )
    return output


def _coerce_locators(values: Sequence[FieldLocator | str]) -> tuple[FieldLocator, ...]:
    if isinstance(values, (str, bytes)):
        raise FieldTypeError(
            "CacheEntry field_locators must be a sequence of locators.",
            field="field_locators",
            actual=type(values).__name__,
        )
    locators = tuple(
        value if isinstance(value, FieldLocator) else FieldLocator.parse(value)
        for value in values
    )
    duplicates = sorted(
        str(locator)
        for index, locator in enumerate(locators)
        if locator in locators[:index]
    )
    if duplicates:
        raise FieldTypeError(
            "CacheEntry field locators must be unique.",
            field="field_locators",
            duplicates=duplicates,
        )
    return locators


def _coerce_status(value: object) -> str:
    status = _coerce_non_empty_string(value, owner="CacheEntry", field="status")
    if status not in {"complete", "incomplete", "failed"}:
        raise FieldTypeError(
            "CacheEntry status is unsupported.",
            field="status",
            expected=["complete", "failed", "incomplete"],
            actual=status,
        )
    return status


def _coerce_schema_version(value: object) -> int:
    if type(value) is not int or value != _CACHE_MANIFEST_SCHEMA_VERSION:
        raise RemotePhysDataSourceError(
            "Unsupported cache manifest schema version.",
            field="schema_version",
            expected=_CACHE_MANIFEST_SCHEMA_VERSION,
            actual=value,
        )
    return value


def _coerce_entries(values: Sequence[CacheEntry]) -> tuple[CacheEntry, ...]:
    try:
        entries = tuple(values)
    except TypeError as exc:
        raise FieldTypeError(
            "CacheManifest entries must be a sequence.",
            field="entries",
            actual=type(values).__name__,
        ) from exc
    if not entries:
        raise FieldTypeError("CacheManifest entries must not be empty.", field="entries")
    for entry in entries:
        if not isinstance(entry, CacheEntry):
            raise FieldTypeError(
                "CacheManifest entries must be CacheEntry records.",
                field="entries",
                actual=type(entry).__name__,
            )
    return entries


def _require_sequence(value: object, *, field: str) -> tuple[object, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise RemotePhysDataSourceError(
            "Serialized cache descriptor values must be sequences.",
            field=field,
            actual=type(value).__name__,
        )
    return tuple(value)


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RemotePhysDataSourceError(
            "Serialized cache descriptors must be mappings.",
            field=field,
            actual=type(value).__name__,
        )
    return value


def _require_keys(value: Mapping[str, object], keys: set[str], *, descriptor: str) -> None:
    actual = set(value)
    if actual != keys:
        raise RemotePhysDataSourceError(
            "Serialized cache descriptor keys do not match the schema.",
            descriptor=descriptor,
            expected=sorted(keys),
            actual=sorted(actual),
        )


def _canonical_json(value: object) -> str:
    return json.dumps(_to_jsonable(value), sort_keys=True, separators=(",", ":"))


def _to_jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _sha256(value: object) -> str:
    import hashlib

    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()

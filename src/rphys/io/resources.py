"""Lazy physical resource descriptors for dependency-free IO planning.

``ResourceRef`` records the precise storage target string, its protocol, and
primitive storage options. It does not parse URIs, open handles, probe files,
resolve codecs, canonicalize paths, or define manifest fingerprints.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Self

from rphys.errors import InvalidResourceRefError

from ._primitives import (
    FrozenPrimitive,
    copy_string_mapping,
    require_exact_keys,
    require_mapping,
    thaw_primitive,
)

__all__ = ["ResourceRef"]


@dataclass(frozen=True, init=False, slots=True)
class ResourceRef:
    """Serializable reference to one addressable storage target.

    ``uri`` and ``protocol`` are uninterpreted non-empty strings. Storage
    options are copied as JSON-like primitives and exposed read-only; nested
    primitive containers are detached so later caller mutation cannot change
    descriptor provenance.
    """

    uri: str
    protocol: str
    storage_options: Mapping[str, FrozenPrimitive]

    def __init__(
        self,
        uri: str,
        protocol: str,
        storage_options: Mapping[str, object] | None = None,
    ) -> None:
        object.__setattr__(self, "uri", _non_empty_string(uri, field="uri"))
        object.__setattr__(
            self,
            "protocol",
            _non_empty_string(protocol, field="protocol"),
        )
        object.__setattr__(
            self,
            "storage_options",
            MappingProxyType(
                copy_string_mapping(
                    storage_options,
                    error_type=InvalidResourceRefError,
                    field="storage_options",
                )
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to primitive values without adding manifest metadata."""

        return {
            "uri": self.uri,
            "protocol": self.protocol,
            "storage_options": {
                key: thaw_primitive(value)
                for key, value in self.storage_options.items()
            },
        }

    @classmethod
    def from_dict(cls, value: object) -> Self:
        """Reconstruct a resource descriptor from ``to_dict`` output."""

        data = require_mapping(
            value,
            error_type=InvalidResourceRefError,
            field="resource_ref",
        )
        require_exact_keys(
            data,
            {"uri", "protocol", "storage_options"},
            error_type=InvalidResourceRefError,
            descriptor="ResourceRef",
        )
        return cls(
            data["uri"],  # type: ignore[arg-type]
            data["protocol"],  # type: ignore[arg-type]
            data["storage_options"],  # type: ignore[arg-type]
        )


ResourceRef.__hash__ = None  # type: ignore[assignment]


def _non_empty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidResourceRefError(
            "ResourceRef fields must be non-empty strings.",
            field=field,
            actual=type(value).__name__,
            value=value,
        )
    return value

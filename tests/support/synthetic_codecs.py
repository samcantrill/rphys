"""Private dependency-light codecs for Stage 4 registry tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rphys.data.fields import FieldSpec, FieldValue
from rphys.errors import RemotePhysDependencyError, UnsupportedCodecIndexError
from rphys.io.codecs import (
    CodecCapabilities,
    CodecLoadResult,
    CodecProbeResult,
    CodecSaveResult,
    LoadContext,
    MetadataSavePolicy,
    SaveContext,
)
from rphys.io.indexes import TemporalIndexSlice


@dataclass
class SyntheticCodec:
    """Small test-only codec with explicit support predicates and call counts."""

    name: str
    key: str = "video.rgb"
    data_type: str = "video"
    schema: str = "video.rgb.v1"
    payload: tuple[Any, ...] = ("f0", "f1", "f2", "f3")
    dependency_available: bool = True
    capabilities: CodecCapabilities = field(
        default_factory=lambda: CodecCapabilities(
            can_probe=True,
            can_load=True,
            can_save=True,
            metadata_policies=(
                MetadataSavePolicy.REFERENCE_ONLY,
                MetadataSavePolicy.INCLUDE_FIELD_METADATA,
            ),
        )
    )
    probe_calls: int = 0
    load_calls: int = 0
    save_calls: int = 0
    saved: list[tuple[FieldValue, SaveContext]] = field(default_factory=list)

    def supports_probe(self, context: LoadContext) -> bool:
        return str(context.field_view.field_ref.key) == self.key

    def supports_load(self, context: LoadContext) -> bool:
        if str(context.field_view.field_ref.key) != self.key:
            return False
        self._validate_index(context)
        return True

    def supports_save(self, value: FieldValue, context: SaveContext) -> bool:
        return str(context.target.key) == self.key

    def probe(self, context: LoadContext) -> CodecProbeResult:
        self._require_dependency()
        self.probe_calls += 1
        return CodecProbeResult(
            FieldSpec(self.key, self.data_type, self.schema),
            metadata={
                "codec": self.name,
                "resource_count": len(context.field_view.field_ref.resources),
            },
        )

    def load(self, context: LoadContext) -> CodecLoadResult:
        self._require_dependency()
        self._validate_index(context)
        self.load_calls += 1
        payload = self._indexed_payload(context)
        return CodecLoadResult(
            FieldValue(
                payload,
                schema=self.schema,
                metadata={"codec": self.name},
            ),
            metadata={
                "codec": self.name,
                "field_key": self.key,
            },
        )

    def save(self, value: FieldValue, context: SaveContext) -> CodecSaveResult:
        self._require_dependency()
        self.save_calls += 1
        self.saved.append((value, context))
        metadata: dict[str, object] = {
            "codec": self.name,
            "metadata_policy": context.metadata_policy.value,
        }
        if context.metadata_policy is MetadataSavePolicy.INCLUDE_FIELD_METADATA:
            metadata["field_metadata"] = {
                str(key): item for key, item in value.metadata.items()
            }
        return CodecSaveResult(
            context.target,
            resources=context.target.resources,
            metadata=metadata,
        )

    def _require_dependency(self) -> None:
        if not self.dependency_available:
            raise RemotePhysDependencyError(
                "Synthetic codec dependency is unavailable.",
                codec=self.name,
            )

    def _validate_index(self, context: LoadContext) -> None:
        field_index = context.field_view.field_index
        if field_index is None:
            return
        if not isinstance(field_index, TemporalIndexSlice) or field_index.step != 1:
            raise UnsupportedCodecIndexError(
                "Synthetic codec supports only full views or unit-step temporal slices.",
                codec=self.name,
                field_key=str(context.field_view.field_ref.key),
                index_type=type(field_index).__name__,
            )

    def _indexed_payload(self, context: LoadContext) -> tuple[Any, ...]:
        field_index = context.field_view.field_index
        if field_index is None:
            return self.payload
        return self.payload[field_index.start : field_index.stop]

from __future__ import annotations

from rphys.data.locators import FieldLocator
import rphys.datasources as datasources


def test_sample_source_exports_are_module_scoped() -> None:
    from rphys.datasources import sources

    assert sources.__all__ == [
        "SampleRequest",
        "SampleRuntimeContext",
        "WorkerContextFactory",
        "SampleSource",
        "IndexSampleSource",
    ]
    for public_name in sources.__all__:
        assert hasattr(sources, public_name)


def test_sample_source_names_are_not_parent_exports() -> None:
    assert not hasattr(datasources, "SampleRequest")
    assert not hasattr(datasources, "SampleRuntimeContext")
    assert not hasattr(datasources, "WorkerContextFactory")
    assert not hasattr(datasources, "SampleSource")
    assert not hasattr(datasources, "IndexSampleSource")


def test_sample_request_string_locator_round_trips() -> None:
    source = __import__("rphys.datasources.sources", fromlist=["SampleRequest"]).SampleRequest
    request = source(requested=("inputs/video.rgb", FieldLocator.parse("targets/signal.bvp.reference")))

    assert str(request.requested[0]) == "inputs/video.rgb"
    assert str(request.requested[1]) == "targets/signal.bvp.reference"

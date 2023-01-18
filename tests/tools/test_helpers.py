import pytest

from tests import is_subset_dict, override_settings
from tools import settings
from tools.helpers import ReservoirSampler, is_step_required


def test_is_subset_dict():
    assert is_subset_dict({}, {"a": 1}) is True
    assert is_subset_dict({"a": 1}, {"a": 1}) is True
    assert is_subset_dict({"a": 1}, {"a": 1, "b": 2}) is True
    assert is_subset_dict({"a": 0}, {"a": 1}) is False
    assert is_subset_dict({"a": 1, "b": 2}, {"a": 1}) is False


def test_reservoir_sampler():
    with pytest.raises(ValueError):
        sampler = ReservoirSampler(-1)

    with pytest.raises(ValueError):
        sampler = ReservoirSampler(0)

    sampler = ReservoirSampler(5)
    for i in range(3):
        sampler.process(i)
    samples = sampler.retrieve_samples()
    assert len(samples) == 3
    assert all([i in samples for i in range(3)])

    sampler = ReservoirSampler(5)
    for i in range(5):
        sampler.process(i)
    samples = sampler.retrieve_samples()
    assert len(samples) == 5
    assert all([i in samples for i in range(5)])

    sampler = ReservoirSampler(5)
    for i in range(10):
        sampler.process(i)
    samples = sampler.retrieve_samples()
    assert len(samples) == 5
    assert all([s in range(10) for s in samples])


@pytest.mark.parametrize(
    "steps,values,expected",
    [
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_COVERAGE,), True),
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_QUALITY,), False),
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_COVERAGE, settings.Steps.FIELD_QUALITY), True),
    ],
)
def test_is_step_required(steps, values, expected):
    with override_settings(STEPS=steps):
        assert is_step_required(*values) is expected

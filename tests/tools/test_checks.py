import pytest

from pelican.exceptions import NonPositiveLimitError
from pelican.util.checks import ReservoirSampler


def test_reservoir_sampler():
    with pytest.raises(NonPositiveLimitError):
        sampler = ReservoirSampler(-1)

    with pytest.raises(NonPositiveLimitError):
        sampler = ReservoirSampler(0)

    sampler = ReservoirSampler(5)
    for i in range(3):
        sampler.process(i)
    assert len(sampler.sample) == 3
    assert all(i in sampler.sample for i in range(3))

    sampler = ReservoirSampler(5)
    for i in range(5):
        sampler.process(i)
    assert len(sampler.sample) == 5
    assert all(i in sampler.sample for i in range(5))

    sampler = ReservoirSampler(5)
    for i in range(10):
        sampler.process(i)
    assert len(sampler.sample) == 5
    assert all(i in range(10) for i in sampler.sample)

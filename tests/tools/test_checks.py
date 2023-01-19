import pytest

from pelican.util.checks import ReservoirSampler


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

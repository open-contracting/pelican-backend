from datetime import datetime, timedelta, timezone

import pytest

from tests import is_subset_dict, override_settings
from tools import settings
from tools.helpers import ReservoirSampler, is_step_required, parse_date, parse_datetime


def test_parse_datetime():
    assert parse_datetime(None) is None
    assert parse_datetime("") is None
    assert parse_datetime("asdfasdf") is None
    assert parse_datetime("2014-10-21T09:30:00Z") == datetime(2014, 10, 21, 9, 30, tzinfo=timezone.utc)
    assert parse_datetime("2014-10-21") is None
    assert parse_datetime("2014-11-18T18:00:00-06:00") == datetime(
        2014, 11, 18, 18, 0, tzinfo=timezone(timedelta(days=-1, seconds=64800))
    )


def test_parse_date():
    assert parse_date(None) is None
    assert parse_date("") is None
    assert parse_date("asdfasdf") is None
    assert parse_date("2014-10-21T09:30:00Z") == datetime(2014, 10, 21).date()
    assert parse_date("2014-10-21") == datetime(2014, 10, 21).date()


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
    "steps,step,expected",
    [
        ([settings.Steps.FIELD_COVERAGE], settings.Steps.FIELD_COVERAGE, True),
        ([settings.Steps.DATASET], settings.Steps.TIME_BASED, False),
    ],
)
def test_is_step_required(steps, step, expected):
    with override_settings(STEPS=steps):
        assert is_step_required(step) is expected

from datetime import datetime, timedelta, timezone

import pytest

from tests import is_subset_dict
from tools.helpers import ReservoirSampler, parse_date, parse_datetime

EMPTY = [None, "", 0, 0.0, False, set(), (), [], {}]
NON_STR = [None, 1, 1.0, True, {1}, (1,), [1], {1}]


@pytest.mark.parametrize("value", EMPTY)
def test_parse_datetime_empty(value):
    assert parse_datetime(value) is None


@pytest.mark.parametrize("value", NON_STR)
def test_parse_datetime_type(value):
    assert parse_datetime(value) is None


@pytest.mark.parametrize("value", ["x", "200101"])
def test_parse_datetime_invalid(value):
    assert parse_datetime(value) is None


@pytest.mark.parametrize(
    "value,components",
    [
        ("2001", (2001, 1, 1, 0, 0)),
        ("2001-02", (2001, 2, 1, 0, 0)),
        ("2001-02-03", (2001, 2, 3, 0, 0)),
        ("20010203", (2001, 2, 3, 0, 0)),
    ],
)
def test_parse_datetime_date(value, components):
    assert parse_datetime(value) == datetime(*components)


# The tests serve to document the formats that are accepted. We don't test week formats.
#
# Dateutil can parse truncated times like "2001-02-03T00:5" and "2001-02-03T00:00:6", but these formats don't support
# time zones. This is undocumented behavior.
#
# https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.isoparse
@pytest.mark.parametrize(
    "suffix,tz",
    [
        ("", None),
        ("Z", timezone.utc),
        # UTC.
        ("+00", timezone.utc),
        ("-00", timezone.utc),
        ("+0000", timezone.utc),
        ("-0000", timezone.utc),
        ("+00:00", timezone.utc),
        ("-00:00", timezone.utc),
        # Non-UTC.
        ("+07", timezone(timedelta(seconds=25200))),
        ("-07", timezone(timedelta(seconds=-25200))),
        ("+0708", timezone(timedelta(seconds=25680))),
        ("-0708", timezone(timedelta(seconds=-25680))),
        ("+07:08", timezone(timedelta(seconds=25680))),
        ("-07:08", timezone(timedelta(seconds=-25680))),
    ],
)
@pytest.mark.parametrize(
    "value,components",
    [
        # With separators.
        ("2001-02-03T04", (2001, 2, 3, 4, 0)),
        ("2001-02-03T04:05", (2001, 2, 3, 4, 5)),
        ("2001-02-03T04:05:06", (2001, 2, 3, 4, 5, 6)),
        ("2001-02-03T04:05:06.0", (2001, 2, 3, 4, 5, 6)),
        ("2001-02-03T04:05:06.123456789", (2001, 2, 3, 4, 5, 6, 123456)),
        # Without separators. (Note: If the "separator" is a number, it is discarded!)
        ("20010203.04", (2001, 2, 3, 4, 0)),
        ("20010203.0405", (2001, 2, 3, 4, 5)),
        ("20010203.040506", (2001, 2, 3, 4, 5, 6)),
        ("20010203.040506,0", (2001, 2, 3, 4, 5, 6)),
        ("20010203.040506,123456789", (2001, 2, 3, 4, 5, 6, 123456)),
        # 24-hour clock.
        ("2001-02-03T00", (2001, 2, 3, 0, 0)),
        ("2001-02-03T24", (2001, 2, 4, 0, 0)),
    ],
)
def test_parse_datetime_dateutil(value, components, suffix, tz):
    assert parse_datetime(value + suffix) == datetime(*components, tzinfo=tz)


# The datetime library can handle short components and long timezones.
@pytest.mark.parametrize(
    "suffix,tz",
    [
        ("Z", timezone.utc),
        # UTC.
        ("+0000", timezone.utc),
        ("-0000", timezone.utc),
        ("+00:00", timezone.utc),
        ("-00:00", timezone.utc),
        ("+00:00:00", timezone.utc),
        ("-00:00:00", timezone.utc),
        # Non-UTC.
        ("+0708", timezone(timedelta(seconds=25680))),
        ("-0708", timezone(timedelta(seconds=-25680))),
        ("+07:08", timezone(timedelta(seconds=25680))),
        ("-07:08", timezone(timedelta(seconds=-25680))),
        ("+07:08:09", timezone(timedelta(seconds=25689))),
        ("-07:08:09", timezone(timedelta(seconds=-25689))),
    ],
)
def test_parse_datetime_library(suffix, tz):
    assert parse_datetime("1000-2-3T4:5:6" + suffix) == datetime(1000, 2, 3, 4, 5, 6, tzinfo=tz)


@pytest.mark.parametrize("value", EMPTY)
def test_parse_date_empty(value):
    assert parse_date(value) is None


@pytest.mark.parametrize("value", NON_STR)
def test_parse_date_type(value):
    assert parse_date(value) is None


@pytest.mark.parametrize("value", ["10000-01-01", "x"])
def test_parse_date_invalid(value):
    assert parse_date(value) is None


@pytest.mark.parametrize(
    "value,components",
    [
        # Date only.
        ("2001", (2001, 1, 1)),
        ("2001-02", (2001, 2, 1)),
        ("2001-02-03", (2001, 2, 3)),
        ("20010203", (2001, 2, 3)),
        # Truncated components.
        ("1000-2-3", (1000, 2, 3)),
        # Extra components.
        ("2001-02-03xxx", (2001, 2, 3)),
        ("2001-02-03T04:05:06Z", (2001, 2, 3)),
    ],
)
def test_parse_date(value, components):
    assert parse_date(value) == datetime(*components).date()


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

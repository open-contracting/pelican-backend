from datetime import datetime, timedelta, timezone

from tools.helpers import parse_datetime


def test_parse_datetime():
    assert parse_datetime(None) is None
    assert parse_datetime("") is None
    assert parse_datetime("asdfasdf") is None
    assert parse_datetime("2014-10-21T09:30:00Z") == datetime(2014, 10, 21, 9, 30)
    assert parse_datetime("2014-10-21") is None
    assert parse_datetime("2014-11-18T18:00:00-06:00") == datetime(2014, 11, 18, 18, 0, tzinfo=timezone(
        timedelta(days=-1, seconds=64800)))

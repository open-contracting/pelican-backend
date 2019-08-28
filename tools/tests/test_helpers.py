from datetime import datetime, timedelta, timezone
from decimal import Decimal
from tools.bootstrap import bootstrap
from tools.helpers import parse_date, parse_datetime


def test_parse_datetime():
    assert parse_datetime(None) is None
    assert parse_datetime("") is None
    assert parse_datetime("asdfasdf") is None
    assert parse_datetime("2014-10-21T09:30:00Z") == datetime(2014, 10, 21, 9, 30)
    assert parse_datetime("2014-10-21") is None
    assert parse_datetime("2014-11-18T18:00:00-06:00") == datetime(2014, 11, 18, 18, 0, tzinfo=timezone(
        timedelta(days=-1, seconds=64800)))


def test_parse_date():
    assert parse_date(None) is None
    assert parse_date("") is None
    assert parse_date("asdfasdf") is None
    assert parse_date("2014-10-21T09:30:00Z") == datetime(2014, 10, 21).date()
    assert parse_date("2014-10-21") == datetime(2014, 10, 21).date()

from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from pelican.util.getter import deep_get, get_values, parse_date, parse_datetime

EMPTY = [None, "", 0, 0.0, False, set(), (), [], {}]
NON_STR = [None, 1, 1.0, True, {1}, (1,), [1], {1}]

item = {
    "id": "123",
    "tender": {
        "id": "0rw29R-005-2011-1",
        "items": [
            {"unit": {"name": "Unidad"}, "quantity": 4.0, "additionalClassifications": [{"id": "bbb"}, {"id": "ccc"}]},
            {"quantity": 5.0, "additionalClassifications": [{"id": "ddd"}, {"id": "eee"}]},
            {"unit": {"name": "Unimom"}, "quantity": 5.0, "additionalClassifications": [{"id": "ddd"}, {"id": "eee"}]},
        ],
        "milestones": [{"status": None}],
    },
    "contracts": [{"documents": [{"id": 0}, {"id": 1}]}, {"documents": [{"id": 2}]}],
}


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
    ("value", "components"),
    [
        ("2001", (2001, 1, 1, 0, 0)),
        ("2001-02", (2001, 2, 1, 0, 0)),
        ("2001-02-03", (2001, 2, 3, 0, 0)),
        ("20010203", (2001, 2, 3, 0, 0)),
    ],
)
def test_parse_datetime_date(value, components):
    assert parse_datetime(value) == datetime(*components, tzinfo=UTC)


# The tests serve to document the formats that are accepted. We don't test week formats.
#
# Dateutil can parse truncated times like "2001-02-03T00:5" and "2001-02-03T00:00:6", but these formats don't support
# time zones. This is undocumented behavior.
#
# https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.isoparse
@pytest.mark.parametrize(
    ("suffix", "tz"),
    [
        ("", None),
        ("Z", UTC),
        # UTC.
        ("+00", UTC),
        ("-00", UTC),
        ("+0000", UTC),
        ("-0000", UTC),
        ("+00:00", UTC),
        ("-00:00", UTC),
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
    ("value", "components"),
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
    ("suffix", "tz"),
    [
        ("Z", UTC),
        # UTC.
        ("+0000", UTC),
        ("-0000", UTC),
        ("+00:00", UTC),
        ("-00:00", UTC),
        ("+00:00:00", UTC),
        ("-00:00:00", UTC),
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
    ("value", "components"),
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
    assert parse_date(value) == datetime(*components, tzinfo=UTC).date()


@pytest.mark.parametrize(
    ("data", "expected", "actual"),
    [
        ({}, "tender.buyer.id", None),
        ({"tender": {"buyer": {"id": "1"}}}, "tender.buyer.id", "1"),
    ],
)
def test_deep_get(data, expected, actual):
    assert deep_get(data, expected) == actual


@pytest.mark.parametrize(
    ("data", "expected", "force", "actual"),
    [
        ({}, "unset", dict, {}),
        ({}, "unset", list, []),
        ({}, "unset", str, ""),
        ({}, "unset", date, None),
        ({}, "unset", datetime, None),
        ({}, "unset", float, None),
        ({}, "unset", int, None),
        # `for part in path.split(".")`
        ({"null": None}, "null.unset", dict, {}),
        ({"null": None}, "null.unset", list, []),
        ({"null": None}, "null.unset", str, ""),
        ({"null": None}, "null.unset", date, None),
        ({"null": None}, "null.unset", datetime, None),
        ({"null": None}, "null.unset", float, None),
        ({"null": None}, "null.unset", int, None),
        # `type(value) is dict`
        ({"emptylist": []}, "emptylist.unset", dict, {}),
        ({"emptylist": []}, "emptylist.unset", list, []),
        ({"emptylist": []}, "emptylist.unset", str, ""),
        ({"emptylist": []}, "emptylist.unset", date, None),
        ({"emptylist": []}, "emptylist.unset", datetime, None),
        ({"emptylist": []}, "emptylist.unset", float, None),
        ({"emptylist": []}, "emptylist.unset", int, None),
        # `part in value`
        ({"emptydict": {}}, "emptydict.unset", dict, {}),
        ({"emptydict": {}}, "emptydict.unset", list, []),
        ({"emptydict": {}}, "emptydict.unset", str, ""),
        ({"emptydict": {}}, "emptydict.unset", date, None),
        ({"emptydict": {}}, "emptydict.unset", datetime, None),
        ({"emptydict": {}}, "emptydict.unset", float, None),
        ({"emptydict": {}}, "emptydict.unset", int, None),
        # date and datetime
        ({"todate": "2001-02-03"}, "todate", date, date(2001, 2, 3)),
        ({"todatetime": "2001-02-03T04:05:06"}, "todatetime", datetime, datetime(2001, 2, 3, 4, 5, 6, tzinfo=UTC)),
        # dict
        ({"todict": None}, "todict", dict, {}),
        ({"todict": ["list"]}, "todict", dict, {}),
        ({"todict": 1}, "todict", dict, {}),
        ({"todict": 1.0}, "todict", dict, {}),
        ({"todict": "string"}, "todict", dict, {}),
        # list
        ({"tolist": None}, "todict", dict, {}),
        ({"tolist": {"key": "value"}}, "tolist", list, []),
        ({"tolist": 1}, "tolist", list, []),
        ({"tolist": 1.0}, "tolist", list, []),
        ({"tolist": "string"}, "tolist", list, []),
        # float
        ({"tofloat": "1"}, "tofloat", float, 1.0),
        ({"tofloat": "1.0"}, "tofloat", float, 1.0),
        ({"tofloat": None}, "tofloat", float, None),
        ({"tofloat": {"key": "value"}}, "tofloat", float, None),
        ({"tofloat": ["list"]}, "tofloat", float, None),
        ({"tofloat": 1}, "tofloat", float, 1.0),
        ({"tofloat": "string"}, "tofloat", float, None),
        # int
        ({"toint": "1"}, "toint", int, 1),
        ({"toint": "1.0"}, "toint", int, None),
        ({"toint": None}, "toint", int, None),
        ({"toint": {"key": "value"}}, "toint", int, None),
        ({"toint": ["list"]}, "toint", int, None),
        ({"toint": 1.0}, "toint", int, 1),
        ({"toint": "string"}, "toint", int, None),
        # str
        # Note: Although returning "None" is surprising, in practice, this should rarely occur. A null value survives
        # Kingfisher Process only if: OCDS Merge was skipped, or the wholeListMerge strategy was used. That said, this
        # behavior can be changed if it causes issues.
        ({"tostring": None}, "tostring", str, "None"),
        ({"tostring": 1}, "tostring", str, "1"),
        ({"tostring": 1.0}, "tostring", str, "1.0"),
        ({"tostring": [1]}, "tostring", str, "[1]"),
        ({"tostring": {"key": "value"}}, "tostring", str, "{'key': 'value'}"),
    ],
)
def test_deep_get_force(data, expected, force, actual):
    assert deep_get(data, expected, force) == actual


def test_get_values_invalid():
    assert get_values({"tender": {"tenderers": "string"}}, "tender.tenderers.contactPoint.name") == []


def test_get_values_simple():
    assert get_values(item, "id") == [{"path": "id", "value": item["id"]}]
    assert get_values(item, "") == [{"path": "", "value": item}]
    assert get_values(item, "tender") == [{"path": "tender", "value": item["tender"]}]
    assert get_values(item, "tender.id") == [{"path": "tender.id", "value": "0rw29R-005-2011-1"}]

    assert get_values(item, "id", value_only=True) == [item["id"]]
    assert get_values(item, "", value_only=True) == [item]
    assert get_values(item, "tender", value_only=True) == [item["tender"]]
    assert get_values(item, "tender.id", value_only=True) == ["0rw29R-005-2011-1"]

    result = get_values(item, "tender.ids")
    assert type(result) is list
    assert (len(result)) == 0

    result = get_values(item, "tender.ids", value_only=True)
    assert type(result) is list
    assert (len(result)) == 0


def test_get_values_lists():
    result = get_values(item, "tender.items.quantity")
    assert result == [
        {"path": "tender.items[0].quantity", "value": 4.0},
        {"path": "tender.items[1].quantity", "value": 5.0},
        {"path": "tender.items[2].quantity", "value": 5.0},
    ]

    assert get_values(item, "tender.items.quantity", value_only=True) == [4.0, 5.0, 5.0]

    assert get_values(item, "tender.items.unit") == [
        {"path": "tender.items[0].unit", "value": {"name": "Unidad"}},
        {"path": "tender.items[2].unit", "value": {"name": "Unimom"}},
    ]

    assert get_values(item, "tender.items.unit", value_only=True) == [{"name": "Unidad"}, {"name": "Unimom"}]

    assert get_values(item, "tender.items.unit.name") == [
        {"path": "tender.items[0].unit.name", "value": "Unidad"},
        {"path": "tender.items[2].unit.name", "value": "Unimom"},
    ]

    assert get_values(item, "tender.items.unit.name", value_only=True) == ["Unidad", "Unimom"]

    result = get_values(item, "tender.items.non_existing")
    assert type(result) is list
    assert len(result) == 0


def test_get_values_join():
    assert get_values(item, "tender.items.additionalClassifications.id") == [
        {"path": "tender.items[0].additionalClassifications[0].id", "value": "bbb"},
        {"path": "tender.items[0].additionalClassifications[1].id", "value": "ccc"},
        {"path": "tender.items[1].additionalClassifications[0].id", "value": "ddd"},
        {"path": "tender.items[1].additionalClassifications[1].id", "value": "eee"},
        {"path": "tender.items[2].additionalClassifications[0].id", "value": "ddd"},
        {"path": "tender.items[2].additionalClassifications[1].id", "value": "eee"},
    ]

    assert get_values(item, "tender.items.additionalClassifications.id", value_only=True) == [
        "bbb",
        "ccc",
        "ddd",
        "eee",
        "ddd",
        "eee",
    ]

    assert get_values(item, "tender.items.additionalClassifications") == [
        {"path": "tender.items[0].additionalClassifications[0]", "value": {"id": "bbb"}},
        {"path": "tender.items[0].additionalClassifications[1]", "value": {"id": "ccc"}},
        {"path": "tender.items[1].additionalClassifications[0]", "value": {"id": "ddd"}},
        {"path": "tender.items[1].additionalClassifications[1]", "value": {"id": "eee"}},
        {"path": "tender.items[2].additionalClassifications[0]", "value": {"id": "ddd"}},
        {"path": "tender.items[2].additionalClassifications[1]", "value": {"id": "eee"}},
    ]

    assert get_values(item, "tender.items.additionalClassifications", value_only=True) == [
        {"id": "bbb"},
        {"id": "ccc"},
        {"id": "ddd"},
        {"id": "eee"},
        {"id": "ddd"},
        {"id": "eee"},
    ]


def test_get_values_end_of_path():
    result = get_values(item, "tender")
    assert type(result) is list
    assert result == [{"path": "tender", "value": item["tender"]}]

    result = get_values(item, "tender", value_only=True)
    assert type(result) is list
    assert result == [item["tender"]]

    result = get_values(item, "tender.items")
    assert type(result) is list
    assert len(result) == 3
    assert result == [
        {"path": "tender.items[0]", "value": item["tender"]["items"][0]},
        {"path": "tender.items[1]", "value": item["tender"]["items"][1]},
        {"path": "tender.items[2]", "value": item["tender"]["items"][2]},
    ]

    result = get_values(item, "tender.items", value_only=True)
    assert type(result) is list
    assert len(result) == 3
    assert result == [item["tender"]["items"][0], item["tender"]["items"][1], item["tender"]["items"][2]]


def test_get_values_indexing():
    result = get_values(item, "tender.items[0]")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "tender.items[0]", "value": item["tender"]["items"][0]}]

    result = get_values(item, "tender.items[0]", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["tender"]["items"][0]]

    result = get_values(item, "contracts.documents[0]")
    assert type(result) is list
    assert len(result) == 2
    assert result == [
        {"path": "contracts[0].documents[0]", "value": item["contracts"][0]["documents"][0]},
        {"path": "contracts[1].documents[0]", "value": item["contracts"][1]["documents"][0]},
    ]

    result = get_values(item, "contracts.documents[0]", value_only=True)
    assert type(result) is list
    assert len(result) == 2
    assert result == [item["contracts"][0]["documents"][0], item["contracts"][1]["documents"][0]]

    result = get_values(item, "contracts.documents[1]")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "contracts[0].documents[1]", "value": item["contracts"][0]["documents"][1]}]

    result = get_values(item, "contracts.documents[1]", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["contracts"][0]["documents"][1]]

    result = get_values(item, "contracts[0].documents")
    assert type(result) is list
    assert len(result) == 2
    assert result == [
        {"path": "contracts[0].documents[0]", "value": item["contracts"][0]["documents"][0]},
        {"path": "contracts[0].documents[1]", "value": item["contracts"][0]["documents"][1]},
    ]

    result = get_values(item, "contracts[0].documents", value_only=True)
    assert type(result) is list
    assert len(result) == 2
    assert result == [item["contracts"][0]["documents"][0], item["contracts"][0]["documents"][1]]


def test_get_values_none_value():
    result = get_values(item, "tender.milestones.status")
    assert type(result) is list
    assert len(result) == 1
    assert result == [{"path": "tender.milestones[0].status", "value": item["tender"]["milestones"][0]["status"]}]

    result = get_values(item, "tender.milestones.status", value_only=True)
    assert type(result) is list
    assert len(result) == 1
    assert result == [item["tender"]["milestones"][0]["status"]]

from datetime import date
from unittest.mock import patch

import pelican.util.currency_converter as cc

#################
# INTERPOLATION #
#################


class InterpolationNone:
    CURRENCY_CONVERTER_INTERPOLATION = None
    CURRENCY_CONVERTER_EXTRAPOLATION = None
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = -1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


class InterpolationClosest:
    CURRENCY_CONVERTER_INTERPOLATION = "closest"
    CURRENCY_CONVERTER_EXTRAPOLATION = None
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = -1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


class InterpolationClosestWithMaxDays:
    CURRENCY_CONVERTER_INTERPOLATION = "closest"
    CURRENCY_CONVERTER_EXTRAPOLATION = None
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = 1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


class InterpolationLinear:
    CURRENCY_CONVERTER_INTERPOLATION = "linear"
    CURRENCY_CONVERTER_EXTRAPOLATION = None
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = -1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


class InterpolationLinearWithMaxDays:
    CURRENCY_CONVERTER_INTERPOLATION = "linear"
    CURRENCY_CONVERTER_EXTRAPOLATION = None
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = 1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


item_test_interpolation1 = [(date(2019, 1, 1), {"CZK": 1, "HNL": 1}), (date(2019, 1, 4), {"CZK": 1, "HNL": 4})]

item_test_interpolation2 = [(date(2019, 1, 1), {"CZK": 1, "HNL": 1}), (date(2019, 1, 6), {"CZK": 1, "HNL": 6})]


def test_interpolation():
    with patch.object(cc, "settings", new=InterpolationNone):
        cc.import_data(item_test_interpolation1)

        assert cc.convert(1, "CZK", "HNL", date(2018, 12, 31)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) is None

    with patch.object(cc, "settings", new=InterpolationClosest):
        cc.import_data(item_test_interpolation1)

        assert cc.convert(1, "CZK", "HNL", date(2018, 12, 31)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) is None

    with patch.object(cc, "settings", new=InterpolationClosestWithMaxDays):
        cc.import_data(item_test_interpolation2)

        assert cc.convert(1, "CZK", "HNL", date(2018, 12, 31)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 6
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) == 6
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 7)) is None

    with patch.object(cc, "settings", new=InterpolationLinear):
        cc.import_data(item_test_interpolation1)

        assert cc.convert(1, "CZK", "HNL", date(2018, 12, 31)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 2
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) is None

    with patch.object(cc, "settings", new=InterpolationLinearWithMaxDays):
        cc.import_data(item_test_interpolation2)

        assert cc.convert(1, "CZK", "HNL", date(2018, 12, 31)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 1
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 2
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 5
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) == 6
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 7)) is None


#################
# EXTRAPOLATION #
#################


class ExtrapolationClosest:
    CURRENCY_CONVERTER_INTERPOLATION = None
    CURRENCY_CONVERTER_EXTRAPOLATION = "closest"
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = -1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = -1


class ExtrapolationClosestWithMaxDays:
    CURRENCY_CONVERTER_INTERPOLATION = None
    CURRENCY_CONVERTER_EXTRAPOLATION = "closest"
    CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK = -1
    CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK = 1


item_test_extrapolation = [
    (date(2019, 1, 3), {"CZK": 1, "HNL": 3}),
    (date(2019, 1, 4), {"CZK": 1, "HNL": 4}),
]


def test_extrapolation():
    with patch.object(cc, "settings", new=ExtrapolationClosest):
        cc.import_data(item_test_extrapolation)

        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) == 4

    with patch.object(cc, "settings", new=ExtrapolationClosestWithMaxDays):
        cc.import_data(item_test_extrapolation)

        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) is None

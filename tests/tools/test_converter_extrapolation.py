from datetime import date
from unittest.mock import patch

from pelican.util import currency_converter


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
    with patch.object(currency_converter, "settings", new=ExtrapolationClosest):
        cc = currency_converter.ExchangeRates(item_test_extrapolation)

        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) == 4

    with patch.object(currency_converter, "settings", new=ExtrapolationClosestWithMaxDays):
        cc = currency_converter.ExchangeRates(item_test_extrapolation)

        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 1)) is None
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 2)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 3)) == 3
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 4)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 5)) == 4
        assert cc.convert(1, "CZK", "HNL", date(2019, 1, 6)) is None

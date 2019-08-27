
import mock
import functools
from datetime import datetime, date

from tools.currency_converter import CurrencyConverter


def mock_update_max_date(self):
    self.max_date = date(2019, 8, 26)


def supply_db_select(db_select):
    def mock_load_from_db(self):
        self._update_db()
        self.rates.clear()
        self.rates_bounds.clear()

        if self.interpolation_type:
            real_data_dates = {currency: [] for currency in self.FIXER_IO_CURRENCIES}

            for query_result in db_select:
                self.rates[query_result[0]] = query_result[1]

                for currency in query_result[1]:
                    if currency not in self.rates_bounds:
                        self.rates_bounds[currency] = (query_result[0], query_result[0])
                    else:
                        self.rates_bounds[currency] = (self.rates_bounds[currency][0], query_result[0])

                    real_data_dates[currency].append(query_result[0])

            for currency, dates in real_data_dates.items():
                if not dates:
                    continue

                previous = dates[0]
                for date in dates:
                    if (date - previous).days > 1:
                        if self.interpolation_type == 'closest':
                            self._interpolation_closest(currency, previous, date)
                        elif self.interpolation_type == 'linear':
                            self._interpolation_linear(currency, previous, date)

                    previous = date
        else:
            for query_result in db_select:
                self.rates[query_result[0]] = query_result[1]

                for currency in query_result[1]:
                    if currency not in self.rates_bounds:
                        self.rates_bounds[currency] = (query_result[0], query_result[0])
                    else:
                        self.rates_bounds[currency] = (self.rates_bounds[currency][0], query_result[0])

    return mock_load_from_db


def mock_update_db(self):
    return


item_test_interpolation1 = [
    (date(2018, 1, 1), {'CZK': 1}),
    (date(2018, 1, 2), {}),
    (date(2018, 1, 3), {}),
    (date(2018, 1, 4), {'CZK': 4})
]

item_test_interpolation2 = [
    (date(2018, 1, 1), {'CZK': 1}),
    (date(2018, 1, 2), {}),
    (date(2018, 1, 3), {}),
    (date(2018, 1, 4), {'CZK': 4})
]

item_test_interpolation3 = [
    (date(2018, 1, 1), {'CZK': 1}),
    (date(2018, 1, 2), {}),
    (date(2018, 1, 3), {}),
    (date(2018, 1, 4), {}),
    (date(2018, 1, 5), {'CZK': 5})
]


def test_interpolation():
    with mock.patch.object(CurrencyConverter, '_update_max_date', new=mock_update_max_date), \
        mock.patch.object(CurrencyConverter, '_update_db', new=mock_update_db), \
        mock.patch.object(
            CurrencyConverter, '_load_from_db', new=supply_db_select(item_test_interpolation1)
            ):

        cc = CurrencyConverter(interpolation_type='closest')
        assert cc.rates[date(2018, 1, 2)]['CZK'] == 1
        assert cc.rates[date(2018, 1, 3)]['CZK'] == 4

    with mock.patch.object(CurrencyConverter, '_update_max_date', new=mock_update_max_date), \
        mock.patch.object(CurrencyConverter, '_update_db', new=mock_update_db), \
        mock.patch.object(
            CurrencyConverter, '_load_from_db', new=supply_db_select(item_test_interpolation2)
            ):

        cc = CurrencyConverter(interpolation_type='linear')
        assert cc.rates[date(2018, 1, 2)]['CZK'] == 2
        assert cc.rates[date(2018, 1, 3)]['CZK'] == 3

    with mock.patch.object(CurrencyConverter, '_update_max_date', new=mock_update_max_date), \
        mock.patch.object(CurrencyConverter, '_update_db', new=mock_update_db), \
        mock.patch.object(
            CurrencyConverter, '_load_from_db', new=supply_db_select(item_test_interpolation3)
            ):

        cc = CurrencyConverter(max_fallback_days=1)
        assert 'CZK' not in cc.rates[date(2018, 1, 3)]

item_test_extrapolation = [
    (date(2018, 1, 10), {'CZK': 1, 'USD': 10}),
    (date(2018, 1, 11), {'CZK': 1, 'USD': 20})
]


def test_extrapolation():
    with mock.patch.object(CurrencyConverter, '_update_max_date', new=mock_update_max_date), \
        mock.patch.object(CurrencyConverter, '_update_db', new=mock_update_db), \
        mock.patch.object(
            CurrencyConverter, '_load_from_db', new=supply_db_select(item_test_extrapolation)
            ):

        cc = CurrencyConverter(max_fallback_days=2)
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 7)) is None
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 8)) == 10
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 9)) == 10
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 12)) == 20
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 13)) == 20
        assert cc.convert(1, 'CZK', 'USD', date(2018, 1, 14)) is None

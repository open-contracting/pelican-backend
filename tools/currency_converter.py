
import json
import requests
import psycopg2.extras
from datetime import datetime, date, timedelta
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import init_logger
from settings.settings import init


class EmptyExchangeRatesTable(Exception):
    pass


class CurrencyConverter():
    BASE = 'EUR'
    DATE_FORMAT = '%Y-%m-%d'
    FIXER_IO_API_KEY = 'c744ed8d097ea8f6d4daeb2fc56a0e44'
    FIXER_IO_LINK = 'http://data.fixer.io/api/{date_historical}?access_key={access_key}&base={base}&symbols={symbols}'
    FIXER_IO_CURRENCIES = {
        'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF',
        'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYR', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP',
        'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD',
        'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR',
        'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW',
        'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK',
        'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR',
        'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG',
        'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY',
        'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VEF', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD',
        'XDR', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMK', 'ZMW', 'ZWL'
    }
    FIXER_IO_CURRENCIES_STR = ','.join(FIXER_IO_CURRENCIES)

    """
    interpolation_type ... 'linear'|'closest'|None
    extrapolation_type ... 'closest'|None
    """
    def __init__(
        self,
        environment='development',
        interpolation_type='closest',
        extrapolation_type='closest',
        max_fallback_days=7
    ):
        # project dependent
        init(environment)
        self.logger = init_logger("CurrencyConverter")
        self.cursor = get_cursor()

        self.interpolation_type = interpolation_type
        self.extrapolation_type = extrapolation_type
        self.max_fallback_days = max_fallback_days
        self.max_date = None
        self._update_max_date()
        self.last_failed_fixer_io_call = {
            'target_date': self.max_date + timedelta(days=1),
            'call_date': self.max_date
        }
        self.rates = {}
        self.rates_bounds = {}
        self._load_from_db()

    def _update_max_date(self):
        self.cursor.execute(
            """
            select max(valid_on)
            from exchange_rates;
            """
        )
        query_result = self.cursor.fetchone()

        if query_result is None:
            raise EmptyExchangeRatesTable()

        self.max_date = query_result[0]

    def _load_from_db(self):
        self._update_db()
        self.rates.clear()
        self.rates_bounds.clear()

        self.cursor.execute(
            """
            select valid_on, rates
            from exchange_rates
            order by valid_on asc;
            """
        )

        if self.interpolation_type:
            real_data_dates = {currency: [] for currency in self.FIXER_IO_CURRENCIES}

            for query_result in self.cursor.fetchall():
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
            for query_result in self.cursor.fetchall():
                self.rates[query_result[0]] = query_result[1]

                for currency in query_result[1]:
                    if currency not in self.rates_bounds:
                        self.rates_bounds[currency] = (query_result[0], query_result[0])
                    else:
                        self.rates_bounds[currency] = (self.rates_bounds[currency][0], query_result[0])

    """
    start_date exclusive, end_date exclusive
    """
    def _interpolation_closest(self, currency, start_date, end_date):
        start_date_rate = self.rates[start_date][currency]
        end_date_rate = self.rates[end_date][currency]

        distance_to_start = None
        distance_to_end = None
        current_date = start_date + timedelta(days=1)
        while current_date < end_date:
            distance_to_start = (current_date - start_date).days
            distance_to_end = (end_date - current_date).days

            if self.max_fallback_days != -1 and distance_to_start > self.max_fallback_days \
                    and distance_to_end > self.max_fallback_days:
                current_date += timedelta(days=distance_to_end - self.max_fallback_days)
                continue
            elif distance_to_start < distance_to_end:
                self.rates[current_date][currency] = start_date_rate
            else:
                self.rates[current_date][currency] = end_date_rate

            current_date += timedelta(days=1)

    """
    start_date exclusive, end_date exclusive
    """
    def _interpolation_linear(self, currency, start_date, end_date):
        start_date_rate = self.rates[start_date][currency]
        end_date_rate = self.rates[end_date][currency]

        distance_to_start = None
        distance_to_end = None
        current_date = start_date + timedelta(days=1)
        while current_date < end_date:
            distance_to_start = (current_date - start_date).days
            distance_to_end = (end_date - current_date).days

            if self.max_fallback_days != -1 and distance_to_start > self.max_fallback_days \
                    and distance_to_end > self.max_fallback_days:
                current_date += timedelta(days=distance_to_end - self.max_fallback_days)
                continue
            else:
                self.rates[current_date][currency] = round(
                    start_date_rate + (current_date - start_date).days *
                    ((end_date_rate - start_date_rate) / (end_date - start_date).days),
                    6
                )

            current_date += timedelta(days=1)

    def _extrapolation_closest_rate(self, currency, rel_date):
        bounds = self.rates_bounds[currency]

        if bounds[0] > rel_date and (bounds[0] - rel_date).days <= self.max_fallback_days:
            return self.rates[bounds[0]][currency]
        elif bounds[1] < rel_date and (rel_date - bounds[1]).days <= self.max_fallback_days:
            return self.rates[bounds[1]][currency]

        return None

    def _update_db(self):
        self._update_max_date()
        date_now = date.today()

        if date_now <= self.last_failed_fixer_io_call['call_date']:
            return

        target_date = self.last_failed_fixer_io_call['target_date']
        while True:
            try:
                date_str = target_date.strftime(self.DATE_FORMAT)

                response = requests.get(
                    self.FIXER_IO_LINK.format(
                        date_historical=date_str,
                        access_key=self.FIXER_IO_API_KEY,
                        base=self.BASE,
                        symbols=self.FIXER_IO_CURRENCIES_STR
                    ),
                    timeout=10
                )
                if response.status_code != 200:
                    break

                data = response.json()
                if not data['success'] or 'rates' not in data:
                    break

                self.cursor.execute(
                    """
                    insert into exchange_rates (valid_on, rates)
                    values ('{}', '{}');
                    """.format(date_str, json.dumps(data['rates']))
                )
                commit()

            except psycopg2.Error:
                rollback()
                break

            except:
                break

            target_date += timedelta(days=1)

        self.last_failed_fixer_io_call['target_date'] = target_date
        self.last_failed_fixer_io_call['call_date'] = date_now

    def convert(self, amount, original_currency, target_currency, rel_date):
        if original_currency not in CurrencyConverter.FIXER_IO_CURRENCIES or \
                target_currency not in CurrencyConverter.FIXER_IO_CURRENCIES:
            return None

        if type(rel_date) != date:
            try:
                rel_date = rel_date.date()
            except AttributeError:
                return None

        # original currency
        original_currency_rate = None
        if rel_date in self.rates and original_currency in self.rates[rel_date]:
            original_currency_rate = self.rates[rel_date][original_currency]
        elif self.extrapolation_type == 'closest':
            original_currency_rate = self._extrapolation_closest_rate(original_currency, rel_date)

        if original_currency_rate is None:
            return None

        # target currency
        target_currency_rate = None
        if rel_date in self.rates and target_currency in self.rates[rel_date]:
            target_currency_rate = self.rates[rel_date][target_currency]
        elif self.extrapolation_type == 'closest':
            target_currency_rate = self._extrapolation_closest_rate(target_currency, rel_date)

        if target_currency_rate is None:
            return None

        return round(amount * (target_currency_rate / original_currency_rate), 6)

import datetime
import os
from operator import itemgetter

import cachetools.func

from pelican.util import settings

# https://docs.pytest.org/en/latest/example/simple.html#pytest-current-test-environment-variable
if "PYTEST_CURRENT_TEST" in os.environ:
    import pelican.util.exchange_rates_file as exchange_rates
else:
    import pelican.util.exchange_rates_db as exchange_rates

# Workers reload exchange rates from the database after this many seconds. A shorter interval gains nothing:
#
# "The Fixer API delivers EOD / End of Day historical exchange rates, which become available at 00:05am GMT for the
# previous day and are time stamped at one second before midnight."
# https://fixer.io/faq
EXCHANGE_RATES_CACHE_TTL = 86400  # 1 day


class ExchangeRates:
    """
    The exchange rates for each date, interpolating rates for missing dates.

    A worker's threads read the same instance. To reload rates, create a new instance (e.g. by expiring the previous
    instance), instead of modifying an existing one.
    """

    def __init__(self, data: list[tuple[datetime.date, dict[str, float]]]):
        self.rates: dict[datetime.date, dict[str, float]] = {}
        self.bounds: dict[str, tuple[datetime.date, datetime.date]] = {}
        self.currencies: set[str] = set()

        for item in data:
            self.currencies.update(item[1].keys())

        data.sort(key=itemgetter(0))

        if settings.CURRENCY_CONVERTER_INTERPOLATION:
            real_data_dates: dict[str, list[datetime.date]] = {currency: [] for currency in self.currencies}

            for item in data:
                self.rates[item[0]] = item[1]

                for currency in item[1]:
                    if currency not in self.bounds:
                        self.bounds[currency] = (item[0], item[0])
                    else:
                        self.bounds[currency] = (self.bounds[currency][0], item[0])

                    real_data_dates[currency].append(item[0])

            for currency, dates in real_data_dates.items():
                if not dates:
                    continue

                previous = dates[0]
                for date in dates:
                    if (date - previous).days > 1:
                        if settings.CURRENCY_CONVERTER_INTERPOLATION == "closest":
                            self.interpolation_closest(currency, previous, date)
                        elif settings.CURRENCY_CONVERTER_INTERPOLATION == "linear":
                            self.interpolation_linear(currency, previous, date)
                        else:
                            raise AttributeError

                    previous = date
        else:
            for item in data:
                self.rates[item[0]] = item[1]

                for currency in item[1]:
                    if currency not in self.bounds:
                        self.bounds[currency] = (item[0], item[0])
                    else:
                        self.bounds[currency] = (self.bounds[currency][0], item[0])

    def interpolation_closest(self, currency, start_date, end_date):
        # start_date and end_date are exclusive.
        start_date_rate = self.rates[start_date][currency]
        end_date_rate = self.rates[end_date][currency]

        distance_to_start = None
        distance_to_end = None
        current_date = start_date + datetime.timedelta(days=1)
        while current_date < end_date:
            distance_to_start = (current_date - start_date).days
            distance_to_end = (end_date - current_date).days

            if (
                settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK != -1
                and distance_to_start > settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
                and distance_to_end > settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
            ):
                current_date += datetime.timedelta(
                    days=distance_to_end - settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
                )
                continue
            if distance_to_start < distance_to_end:
                self.rates.setdefault(current_date, {})
                self.rates[current_date][currency] = start_date_rate
            else:
                self.rates.setdefault(current_date, {})
                self.rates[current_date][currency] = end_date_rate

            current_date += datetime.timedelta(days=1)

    def interpolation_linear(self, currency, start_date, end_date):
        # start_date and end_date are exclusive.
        start_date_rate = self.rates[start_date][currency]
        end_date_rate = self.rates[end_date][currency]

        distance_to_start = None
        distance_to_end = None
        current_date = start_date + datetime.timedelta(days=1)
        while current_date < end_date:
            distance_to_start = (current_date - start_date).days
            distance_to_end = (end_date - current_date).days

            if (
                settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK != -1
                and distance_to_start > settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
                and distance_to_end > settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
            ):
                current_date += datetime.timedelta(
                    days=distance_to_end - settings.CURRENCY_CONVERTER_INTERPOLATION_MAX_DAYS_FALLBACK
                )
                continue

            self.rates.setdefault(current_date, {})
            self.rates[current_date][currency] = round(
                start_date_rate
                + (current_date - start_date).days * (end_date_rate - start_date_rate) / (end_date - start_date).days,
                6,
            )

            current_date += datetime.timedelta(days=1)

    def extrapolation_closest_rate(self, currency, rel_date):
        bound = self.bounds[currency]

        if bound[0] > rel_date and (
            (bound[0] - rel_date).days <= settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK
            or settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK == -1
        ):
            return self.rates[bound[0]][currency]

        if bound[1] < rel_date and (
            (rel_date - bound[1]).days <= settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK
            or settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK == -1
        ):
            return self.rates[bound[1]][currency]

        return None

    def convert(self, amount, original_currency, target_currency, rel_date):
        if original_currency not in self.currencies or target_currency not in self.currencies:
            return None

        if type(rel_date) is not datetime.date:
            try:
                rel_date = rel_date.date()
            except AttributeError:
                return None

        if type(amount) is not float:
            try:
                amount = float(amount)
            except (TypeError, ValueError):
                return None

        original_currency_rate = None
        if rel_date in self.rates and original_currency in self.rates[rel_date]:
            original_currency_rate = self.rates[rel_date][original_currency]
        elif settings.CURRENCY_CONVERTER_EXTRAPOLATION == "closest":
            original_currency_rate = self.extrapolation_closest_rate(original_currency, rel_date)
        if original_currency_rate is None:
            return None

        target_currency_rate = None
        if rel_date in self.rates and target_currency in self.rates[rel_date]:
            target_currency_rate = self.rates[rel_date][target_currency]
        elif settings.CURRENCY_CONVERTER_EXTRAPOLATION == "closest":
            target_currency_rate = self.extrapolation_closest_rate(target_currency, rel_date)
        if target_currency_rate is None:
            return None

        return round(amount * (target_currency_rate / original_currency_rate), 6)


@cachetools.func.ttl_cache(ttl=EXCHANGE_RATES_CACHE_TTL)
def get_exchange_rates() -> ExchangeRates:
    """Return the exchange rates, reloading them from the database once the cache expires."""
    return ExchangeRates(exchange_rates.load())


def convert(amount, original_currency, target_currency, rel_date):
    return get_exchange_rates().convert(amount, original_currency, target_currency, rel_date)

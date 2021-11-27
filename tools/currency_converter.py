import datetime
import os
from typing import Dict, List, Set, Tuple

from tools import settings

# https://docs.pytest.org/en/latest/example/simple.html#pytest-current-test-environment-variable
if "PYTEST_CURRENT_TEST" in os.environ:
    import tools.exchange_rates_db as exchange_rates
else:
    import tools.exchange_rates_file as exchange_rates

rates = dict()  # type: Dict[datetime.datetime, Dict[str, float]]
bounds = dict()  # type: Dict[str, Tuple[datetime.datetime, datetime.datetime]]
currencies = set()  # type: Set[str]


def bootstrap() -> None:
    import_data(exchange_rates.load())


def import_data(data: List[Tuple[datetime.datetime, Dict[str, float]]]) -> None:
    global rates
    global bounds
    global currencies
    rates.clear()
    bounds.clear()
    currencies.clear()

    for item in data:
        currencies.update(item[1].keys())

    data.sort(key=lambda k: k[0])

    if settings.CURRENCY_CONVERTER_INTERPOLATION:
        real_data_dates = {currency: [] for currency in currencies}  # type: Dict[str, List[datetime.datetime]]

        for item in data:
            rates[item[0]] = item[1]

            for currency in item[1]:
                if currency not in bounds:
                    bounds[currency] = (item[0], item[0])
                else:
                    bounds[currency] = (bounds[currency][0], item[0])

                real_data_dates[currency].append(item[0])

        for currency, dates in real_data_dates.items():
            if not dates:
                continue

            previous = dates[0]
            for date in dates:
                if (date - previous).days > 1:
                    if settings.CURRENCY_CONVERTER_INTERPOLATION == "closest":
                        interpolation_closest(currency, previous, date)
                    elif settings.CURRENCY_CONVERTER_INTERPOLATION == "linear":
                        interpolation_linear(currency, previous, date)
                    else:
                        raise AttributeError()

                previous = date
    else:
        for item in data:
            rates[item[0]] = item[1]

            for currency in item[1]:
                if currency not in bounds:
                    bounds[currency] = (item[0], item[0])
                else:
                    bounds[currency] = (bounds[currency][0], item[0])


def interpolation_closest(currency, start_date, end_date):
    """
    start_date exclusive, end_date exclusive
    """
    start_date_rate = rates[start_date][currency]
    end_date_rate = rates[end_date][currency]

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
        elif distance_to_start < distance_to_end:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = start_date_rate
        else:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = end_date_rate

        current_date += datetime.timedelta(days=1)


def interpolation_linear(currency, start_date, end_date):
    """
    start_date exclusive, end_date exclusive
    """
    start_date_rate = rates[start_date][currency]
    end_date_rate = rates[end_date][currency]

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
        else:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = round(
                start_date_rate
                + (current_date - start_date).days
                * ((end_date_rate - start_date_rate) / (end_date - start_date).days),
                6,
            )

        current_date += datetime.timedelta(days=1)


def extrapolation_closest_rate(currency, rel_date):
    bound = bounds[currency]

    if bound[0] > rel_date and (
        (bound[0] - rel_date).days <= settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK
        or settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK == -1
    ):
        return rates[bound[0]][currency]

    elif bound[1] < rel_date and (
        (rel_date - bound[1]).days <= settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK
        or settings.CURRENCY_CONVERTER_EXTRAPOLATION_MAX_DAYS_FALLBACK == -1
    ):

        return rates[bound[1]][currency]


def convert(amount, original_currency, target_currency, rel_date):
    if original_currency not in currencies or target_currency not in currencies:
        return None

    if type(rel_date) != datetime.date:
        try:
            rel_date = rel_date.date()
        except AttributeError:
            return None

    if type(amount) != float:
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return None

    # original currency
    original_currency_rate = None
    if rel_date in rates and original_currency in rates[rel_date]:
        original_currency_rate = rates[rel_date][original_currency]
    elif settings.CURRENCY_CONVERTER_EXTRAPOLATION == "closest":
        original_currency_rate = extrapolation_closest_rate(original_currency, rel_date)

    if original_currency_rate is None:
        return None

    # target currency
    target_currency_rate = None
    if rel_date in rates and target_currency in rates[rel_date]:
        target_currency_rate = rates[rel_date][target_currency]
    elif settings.CURRENCY_CONVERTER_EXTRAPOLATION == "closest":
        target_currency_rate = extrapolation_closest_rate(target_currency, rel_date)

    if target_currency_rate is None:
        return None

    return round(amount * (target_currency_rate / original_currency_rate), 6)


def currency_available(currency):
    return currency in currencies

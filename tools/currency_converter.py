
from datetime import date, timedelta
from settings.settings import get_param

rates = dict()
bounds = dict()
currencies = set()


def import_data(data):
    '''
    data must be in following form [(date, rates)]
    rates must be in following form {'currency': rate}
    '''

    global rates
    global bounds
    global currencies
    rates.clear()
    bounds.clear()
    currencies.clear()

    for item in data:
        currencies.update(item[1].keys())

    data.sort(key=lambda k: k[0])

    if get_param('currency_converter_interpolation'):
        real_data_dates = {currency: [] for currency in currencies}

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
                    if get_param('currency_converter_interpolation') == 'closest':
                        interpolation_closest(currency, previous, date)
                    elif get_param('currency_converter_interpolation') == 'linear':
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
    '''
    start_date exclusive, end_date exclusive
    '''
    start_date_rate = rates[start_date][currency]
    end_date_rate = rates[end_date][currency]

    distance_to_start = None
    distance_to_end = None
    current_date = start_date + timedelta(days=1)
    while current_date < end_date:
        distance_to_start = (current_date - start_date).days
        distance_to_end = (end_date - current_date).days

        if (
            get_param('currency_converter_interpolation_max_days_fallback') != -1 and
            distance_to_start > get_param('currency_converter_interpolation_max_days_fallback') and
            distance_to_end > get_param('currency_converter_interpolation_max_days_fallback')
        ):
            current_date += timedelta(days=distance_to_end - get_param('currency_converter_interpolation_max_days_fallback'))
            continue
        elif distance_to_start < distance_to_end:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = start_date_rate
        else:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = end_date_rate

        current_date += timedelta(days=1)


def interpolation_linear(currency, start_date, end_date):
    '''
    start_date exclusive, end_date exclusive
    '''
    start_date_rate = rates[start_date][currency]
    end_date_rate = rates[end_date][currency]

    distance_to_start = None
    distance_to_end = None
    current_date = start_date + timedelta(days=1)
    while current_date < end_date:
        distance_to_start = (current_date - start_date).days
        distance_to_end = (end_date - current_date).days

        if (
            get_param('currency_converter_interpolation_max_days_fallback') != -1 and
            distance_to_start > get_param('currency_converter_interpolation_max_days_fallback') and
            distance_to_end > get_param('currency_converter_interpolation_max_days_fallback')
        ):
            current_date += timedelta(days=distance_to_end - get_param('currency_converter_interpolation_max_days_fallback'))
            continue
        else:
            if current_date not in rates:
                rates[current_date] = {}

            rates[current_date][currency] = round(
                start_date_rate + (current_date - start_date).days *
                ((end_date_rate - start_date_rate) / (end_date - start_date).days),
                6
            )

        current_date += timedelta(days=1)


def extrapolation_closest_rate(currency, rel_date):
        bound = bounds[currency]

        if (
            bound[0] > rel_date and
            (
                (bound[0] - rel_date).days <= get_param('currency_converter_extrapolation_max_days_fallback') or
                get_param('currency_converter_extrapolation_max_days_fallback') == -1
            )
        ):
            return rates[bound[0]][currency]

        elif (
            bound[1] < rel_date and
            (
                (rel_date - bound[1]).days <= get_param('currency_converter_extrapolation_max_days_fallback') or
                get_param('currency_converter_extrapolation_max_days_fallback') == -1
            )
        ):

            return rates[bound[1]][currency]

        return None


def convert(amount, original_currency, target_currency, rel_date):
    if original_currency not in currencies or \
            target_currency not in currencies:
        return None

    if type(rel_date) != date:
        try:
            rel_date = rel_date.date()
        except:
            return None

    # original currency
    original_currency_rate = None
    if rel_date in rates and original_currency in rates[rel_date]:
        original_currency_rate = rates[rel_date][original_currency]
    elif get_param('currency_converter_extrapolation') == 'closest':
        original_currency_rate = extrapolation_closest_rate(original_currency, rel_date)

    if original_currency_rate is None:
        return None

    # target currency
    target_currency_rate = None
    if rel_date in rates and target_currency in rates[rel_date]:
        target_currency_rate = rates[rel_date][target_currency]
    elif get_param('currency_converter_extrapolation') == 'closest':
        target_currency_rate = extrapolation_closest_rate(target_currency, rel_date)

    if target_currency_rate is None:
        return None

    return round(amount * (target_currency_rate / original_currency_rate), 6)


def currency_available(currency):
    return currency in currencies
